"""
Graph-Routed Retriever
Retrieval dựa trên graph traversal với routing strategies
"""
import logging
from typing import List, Dict, Any, Optional, Set
import networkx as nx
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_ollama import OllamaEmbeddings
from pydantic import Field, BaseModel
import numpy as np
import os
from dotenv import load_dotenv

from .graph_builder import DocumentGraph
from .subgraph_partitioner import SubgraphPartitioner

load_dotenv()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text:latest")

logger = logging.getLogger(__name__)


class GraphRoutedRetriever(BaseRetriever, BaseModel):
    """Graph-based retriever with routing strategies"""
    
    graph: Any = Field(description="Document graph")  # nx.Graph
    partitioner: Any = Field(description="Subgraph partitioner")
    k: int = Field(default=4, description="Number of documents to retrieve (final for LLM)")
    internal_k: int = Field(default=None, description="Internal retrieval k (retrieve more, rank to k)")
    hop_depth: int = Field(default=2, description="Max hops for graph traversal")
    expansion_factor: float = Field(default=1.5, description="Graph expansion factor for BFS")
    embeddings: Any = Field(default=None, description="Embeddings model")
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, 
                 graph: nx.Graph,
                 partitioner: SubgraphPartitioner,
                 k: int = 4,
                 internal_k: int = None,
                 hop_depth: int = 2,
                 expansion_factor: float = 1.5,
                 embeddings_model: str = None):
        """Initialize graph-routed retriever with optimization"""
        model = embeddings_model or OLLAMA_EMBEDDING_MODEL
        print(f"📊 Graph Retriever using Ollama embedding model: {model}")
        
        embeddings = OllamaEmbeddings(
            model=model,
            base_url=OLLAMA_BASE_URL
        )
        
        super().__init__(
            graph=graph,
            partitioner=partitioner,
            k=k,
            internal_k=internal_k or (k * 2),  # Default: retrieve 2x docs internally
            hop_depth=hop_depth,
            expansion_factor=expansion_factor,
            embeddings=embeddings
        )
        
        # Optimization: Cache query embeddings
        self._query_embedding_cache = {}
        self._pagerank_cache = None
    
    def _get_relevant_documents(self, query: str, metadata_filter: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        IMPROVED HYBRID: Semantic GraphRAG + Keyword BM25
        - Combines graph-based semantic search with keyword matching
        - Boosts table chunks and exact keyword matches
        - Returns top-k with diversity
        """
        logger.info("=" * 60)
        logger.info("🕸️ HYBRID GraphRAG + BM25 RETRIEVAL")
        logger.info(f"Query: {query[:150]}")
        logger.info(f"Graph: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        logger.info(f"Communities: {len(self.partitioner.communities)}")
        logger.info("=" * 60)
        
        # Step 1: SEMANTIC - Graph-based routing
        target_subgraphs = self._route_query_automated(query)
        logger.info(f"✅ Semantic routing: {len(target_subgraphs)} communities")
        
        semantic_docs = []
        for subgraph_id, node_ids in target_subgraphs.items():
            docs = self._search_in_subgraph(query, node_ids)
            semantic_docs.extend(docs)
        
        logger.info(f"📄 Semantic: {len(semantic_docs)} documents")
        
        # Step 2: KEYWORD - BM25-like search on ALL nodes
        keyword_docs = self._keyword_search_all_nodes(query)
        logger.info(f"🔑 Keyword: {len(keyword_docs)} documents")
        
        # Step 3: MERGE with boosting
        # Boost documents that appear in BOTH semantic and keyword results
        doc_scores = {}
        
        # Semantic scores
        for i, doc in enumerate(semantic_docs):
            doc_id = id(doc)
            # Higher rank = higher score (inverse rank)
            doc_scores[doc_id] = {'doc': doc, 'semantic': len(semantic_docs) - i, 'keyword': 0}
        
        # Keyword scores
        for i, doc in enumerate(keyword_docs):
            doc_id = id(doc)
            if doc_id in doc_scores:
                doc_scores[doc_id]['keyword'] = len(keyword_docs) - i
            else:
                doc_scores[doc_id] = {'doc': doc, 'semantic': 0, 'keyword': len(keyword_docs) - i}
        
        # Combined score with boosting
        for doc_id in doc_scores:
            semantic_score = doc_scores[doc_id]['semantic']
            keyword_score = doc_scores[doc_id]['keyword']
            
            # Boost if in BOTH results (hybrid bonus)
            if semantic_score > 0 and keyword_score > 0:
                doc_scores[doc_id]['final'] = semantic_score * 0.6 + keyword_score * 0.4 + 50  # Hybrid boost
            else:
                doc_scores[doc_id]['final'] = semantic_score * 0.6 + keyword_score * 0.4
            
            # Extra boost for table chunks
            if doc_scores[doc_id]['doc'].metadata.get('contains_table', False):
                doc_scores[doc_id]['final'] *= 1.3
        
        # Rank by final score
        ranked = sorted(doc_scores.items(), key=lambda x: x[1]['final'], reverse=True)
        final_docs = [item[1]['doc'] for item in ranked[:self.k]]
        
        logger.info(f"📊 Hybrid: {len(doc_scores)} unique docs → top {len(final_docs)} returned")
        logger.info("=" * 60)
        return final_docs
    
    def _route_query_automated(self, query: str, top_k_communities: int = 15) -> Dict[Any, Set[int]]:
        """
        AUTOMATED ROUTING: Route query to relevant communities
        Uses embedding similarity - NO HARDCODED RULES
        OPTIMIZED: Cache query embeddings
        ENHANCED: Route to top-5 communities (increased from 3) for better coverage
        IMPROVED: Increased default top_k from 10 to 15 to avoid centroid averaging problem
        
        Returns:
            Dict mapping community_id -> node_ids to search
        """
        # Cache query embedding
        if query not in self._query_embedding_cache:
            self._query_embedding_cache[query] = np.array(self.embeddings.embed_query(query))
        
        query_embedding = self._query_embedding_cache[query]
        
        # Route to top-k most similar communities (increased from 2 to 3)
        top_communities = self.partitioner.route_query_to_communities(
            query_embedding, 
            top_k=top_k_communities
        )
        
        # DEBUG: Log selected communities
        logger.info(f"🎯 Routing selected {len(top_communities)} communities:")
        for comm_id, score in top_communities[:5]:
            size = len(self.partitioner.get_subgraph(comm_id))
            marker = "👉 Bảng 3 HERE" if comm_id == 0 else ""
            logger.info(f"   Community {comm_id}: score={score:.4f}, size={size} nodes {marker}")
        
        if not top_communities:
            # Fallback: search all subgraphs
            logger.warning("No communities found, searching all nodes")
            return self.partitioner.get_all_subgraphs()
        
        # Get node IDs for selected communities
        target_subgraphs = {}
        for comm_id, similarity in top_communities:
            node_ids = self.partitioner.get_subgraph(comm_id)
            if node_ids:
                target_subgraphs[comm_id] = node_ids
        
        return target_subgraphs
    
    def _search_in_subgraph(self, query: str, node_ids: Set[int]) -> List[Document]:
        """
        IMPROVED: Document-level similarity search to avoid centroid averaging problem
        
        FIX: Previously relied on centroid-based routing which could miss relevant documents
        if they were "drowned out" by majority documents in the community.
        
        NEW Strategy:
        1. Compute similarity with EVERY document (not just centroid)
        2. Use cached embeddings from graph nodes (fast!)
        3. Expand from high-scoring seeds with weighted BFS
        4. Return diverse results
        """
        if not node_ids:
            return []
        
        logger.info(f"🔍 Document-level search in subgraph with {len(node_ids)} nodes")
        
        # Get cached query embedding
        if query not in self._query_embedding_cache:
            self._query_embedding_cache[query] = np.array(self.embeddings.embed_query(query))
        query_embedding = self._query_embedding_cache[query]
        
        # IMPROVEMENT: Compute similarities with ALL documents (not just centroid)
        # This avoids the "centroid averaging" problem where relevant docs are hidden
        node_scores = {}
        for node_id in node_ids:
            if node_id not in self.graph.nodes:
                continue
            
            # Use cached embedding from graph builder (NO API CALL!)
            doc_embedding = self.graph.nodes[node_id].get('embedding')
            
            if doc_embedding is None:
                continue  # Skip if no embedding cached
            
            # Fast cosine similarity at DOCUMENT level (no API calls!)
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            node_scores[node_id] = similarity
        
        logger.info(f"✅ Computed {len(node_scores)} document-level similarities (avg={np.mean(list(node_scores.values())):.3f})")
        
        # Sort by similarity
        sorted_nodes = sorted(node_scores.items(), key=lambda x: x[1], reverse=True)
        
        # IMPROVED: Adaptive expansion with aggressive graph traversal for tables
        # Tables/data often have low semantic similarity but high structural relevance
        # Use internal_k (if set) for expansion to cast wider net, then filter to k for LLM
        expansion_base = self.internal_k if hasattr(self, 'internal_k') and self.internal_k else self.k
        target_docs = int(expansion_base * self.expansion_factor)
        seed_count = min(max(3, target_docs // 2), len(sorted_nodes))  # Increased min from 2 to 3
        seeds = [node_id for node_id, _ in sorted_nodes[:seed_count]]
        
        logger.info(f"   Expanding from {seed_count} seed nodes (target: {target_docs} docs, base={expansion_base})")
        
        # Graph expansion from top seeds
        expanded_nodes = self._expand_from_seeds(seeds, node_ids)
        
        # # DEBUG: Check if Node 1016 is in expanded set
        # if 1016 in expanded_nodes:
        #     logger.info("✅ Node 1016 (Bảng 3) IS IN EXPANDED SET")
        # else:
        #     logger.warning("❌ Node 1016 (Bảng 3) NOT in expanded set")
        #     if 1016 in node_ids:
        #         logger.warning(f"   But it IS in subgraph ({len(node_ids)} total nodes)")
        #         if 1016 in node_scores:
        #             logger.warning(f"   Its similarity score: {node_scores[1016]:.4f}")
        #             # Check if any seed connects to 1016
        #             for seed in seeds:
        #                 if self.graph.has_edge(seed, 1016):
        #                     edge_data = self.graph.edges[seed, 1016]
        #                     logger.warning(f"   Seed {seed} connects to 1016: weight={edge_data.get('weight', 0):.3f}, type={edge_data.get('type')}")
        #     else:
        #         logger.warning(f"   NOT in subgraph node_ids ({len(node_ids)} total)")
        #         # Find its community
        #         node_community = self.graph.nodes[1016].get('community', '?')
        #         logger.warning(f"   Node 1016 community: {node_community}")
        
        # Re-rank expanded nodes
        expanded_scores = {nid: node_scores.get(nid, 0) for nid in expanded_nodes}
        sorted_expanded = sorted(expanded_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Convert to documents
        docs = []
        for node_id, score in sorted_expanded[:target_docs]:
            doc = self.graph.nodes[node_id]['document']
            doc.metadata['relevance_score'] = float(score)
            docs.append(doc)
        
        return docs
    
    def _keyword_search_all_nodes(self, query: str, max_results: int = 20) -> List[Document]:
        """
        BM25-style keyword search across ALL nodes in graph
        Returns documents matching query keywords
        """
        query_keywords = set(query.lower().split())
        # Remove stop words
        stop_words = {'là', 'của', 'và', 'có', 'để', 'trong', 'được', 'cho', 'các', 'một', 'này', 'đó'}
        query_keywords = {kw for kw in query_keywords if kw not in stop_words and len(kw) > 2}
        
        doc_scores = []
        for node_id in self.graph.nodes():
            content = self.graph.nodes[node_id].get('content', '').lower()
            
            # Count keyword matches
            match_count = sum(1 for kw in query_keywords if kw in content)
            
            if match_count > 0:
                doc = self.graph.nodes[node_id].get('document')
                if doc:
                    # TF-IDF-like score: match_count / total_keywords
                    score = match_count / len(query_keywords) if query_keywords else 0
                    doc_scores.append((doc, score))
        
        # Sort by score
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in doc_scores[:max_results]]
    
    def _keyword_search_all_nodes(self, query: str, max_results: int = 20) -> List[Document]:
        """
        BM25-style keyword search across ALL nodes in graph
        Returns documents matching query keywords
        """
        query_keywords = set(query.lower().split())
        # Remove stop words
        stop_words = {'là', 'của', 'và', 'có', 'để', 'trong', 'được', 'cho', 'các', 'một', 'này', 'đó'}
        query_keywords = {kw for kw in query_keywords if kw not in stop_words and len(kw) > 2}
        
        doc_scores = []
        for node_id in self.graph.nodes():
            content = self.graph.nodes[node_id].get('content', '').lower()
            
            # Count keyword matches
            match_count = sum(1 for kw in query_keywords if kw in content)
            
            if match_count > 0:
                doc = self.graph.nodes[node_id].get('document')
                if doc:
                    # TF-IDF-like score: match_count / total_keywords
                    score = match_count / len(query_keywords) if query_keywords else 0
                    doc_scores.append((doc, score))
        
        # Sort by score
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in doc_scores[:max_results]]
    
    def _keyword_search_tables(self, query: str, max_results: int = 5) -> List[Document]:
        """
        Keyword-based search specifically for table chunks
        Fallback when semantic routing misses table-containing communities
        """
        # Extract numeric keywords from query
        import re
        numbers = re.findall(r'\d+', query)
        keywords = query.lower().split()
        
        table_candidates = []
        for node_id in self.graph.nodes():
            node = self.graph.nodes[node_id]
            metadata = node.get('metadata', {})
            
            # Only consider table chunks
            if not metadata.get('contains_table', False):
                continue
            
            content = node.get('content', '').lower()
            
            # Score by keyword matches
            score = 0.0
            for num in numbers:
                if num in content:
                    score += 0.5  # Numeric match
            for kw in ['bảng', 'table', 'quy đổi', 'điểm']:
                if kw in content:
                    score += 0.3  # Keyword match
            
            if score > 0:
                doc = node['document']
                doc.metadata['keyword_score'] = score
                table_candidates.append((score, doc))
        
        # Sort by score and return top results
        table_candidates.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in table_candidates[:max_results]]
    
    def _expand_from_seeds(self, seeds: List[int], subgraph_nodes: Set[int]) -> Set[int]:
        """
        Smart expansion from seed nodes using weighted BFS
        Prioritize edges with higher weights (more relevant connections)
        
        Args:
            seeds: Initial seed nodes
            subgraph_nodes: Valid nodes in current subgraph
            
        Returns:
            Set of expanded node IDs
        """
        visited = set(seeds)
        # Priority queue: (priority, node, depth)
        # Priority = -weight (negative for max-heap behavior)
        import heapq
        pq = [(0, seed, 0) for seed in seeds]  # (priority, node, depth)
        heapq.heapify(pq)
        
        while pq:
            _, current, depth = heapq.heappop(pq)
            
            if depth >= self.hop_depth:
                continue
            
            # Explore neighbors, prioritize by edge weight
            for neighbor in self.graph.neighbors(current):
                if neighbor not in visited and neighbor in subgraph_nodes:
                    visited.add(neighbor)
                    
                    # Get edge weight (higher weight = more relevant)
                    edge_data = self.graph.get_edge_data(current, neighbor)
                    weight = edge_data.get('weight', 0.5) if edge_data else 0.5
                    
                    # Negative weight for max-heap (higher weight = higher priority)
                    priority = -weight
                    heapq.heappush(pq, (priority, neighbor, depth + 1))
        
        return visited
    
    def _rank_documents(self, query: str, documents: List[Document]) -> List[Document]:
        """
        ENHANCED MULTI-METRIC RANKING
        Combines multiple signals with metadata awareness + structural bonus
        
        Metrics:
        1. Semantic similarity (cosine) - 35%
        2. BM25 score (keyword matching) - 20%
        3. PageRank (graph centrality) - 10%
        4. Metadata matching (category relevance) - 15%
        5. Structural proximity (bonus for sequential chunks) - 20%
        6. Diversity penalty (MMR-like)
        """
        if not documents:
            return []
        
        # 1. Get cached semantic scores
        semantic_scores = {
            id(doc): doc.metadata.get('relevance_score', 0)
            for doc in documents
        }
        
        # 2. Compute BM25 scores (lexical matching)
        bm25_scores = self._compute_bm25_scores(query, documents)
        
        # 3. Get PageRank scores (node importance in graph)
        pagerank_scores = self._get_pagerank_scores(documents)
        
        # 4. Compute metadata matching scores
        metadata_scores = self._compute_metadata_scores(query, documents)
        
        # 5. NEW: Compute structural proximity bonus (boost sequential chunks)
        structural_scores = self._compute_structural_proximity_scores(documents, semantic_scores)
        
        # 6. Combined scoring with IMPROVED structural bonus for tables/data
        # OPTIMIZATION: Increased BM25 (keyword) and structural weights to better catch
        # tables and data chunks that may have low semantic similarity but high factual relevance
        # NEW: Table boost for numeric queries
        final_scores = {}
        
        # Check if query is about numbers/tables/data
        query_lower = query.lower()
        is_numeric_query = any(keyword in query_lower for keyword in [
            'điểm', 'bao nhiêu', 'quy đổi', 'bảng', 'table', 'số', 'điểm số',
            '650', '700', '500', 'toeic', 'ielts', 'toefl', 'ib', 'cambridge'
        ])
        
        for doc in documents:
            doc_id = id(doc)
            
            # Weighted combination optimized for factual/tabular data
            semantic = semantic_scores.get(doc_id, 0) * 0.20    # 20% semantic (reduced further)
            bm25 = bm25_scores.get(doc_id, 0) * 0.30           # 30% keyword
            pagerank = pagerank_scores.get(doc_id, 0) * 0.10   # 10% graph centrality
            metadata = metadata_scores.get(doc_id, 0) * 0.10   # 10% metadata match
            structural = structural_scores.get(doc_id, 0) * 0.30  # 30% structural (INCREASED AGAIN!)
            
            # TABLE BOOST: Add significant boost for table chunks in numeric queries
            table_boost = 0.0
            if is_numeric_query and doc.metadata.get('contains_table', False):
                table_boost = 0.4  # Strong boost
                chunk_idx = doc.metadata.get('chunk_index', '?')
                logger.info(f"📊 TABLE BOOST: +{table_boost} for chunk {chunk_idx}, node_id={[nid for nid in self.graph.nodes() if self.graph.nodes[nid].get('document') == doc]}")
            
            final_score = semantic + bm25 + pagerank + metadata + structural + table_boost
            final_scores[doc_id] = final_score
            
            # Update metadata
            doc.metadata['combined_score'] = float(final_score)
            doc.metadata['bm25_score'] = float(bm25_scores.get(doc_id, 0))
            doc.metadata['pagerank_score'] = float(pagerank_scores.get(doc_id, 0))
            doc.metadata['metadata_score'] = float(metadata_scores.get(doc_id, 0))
            doc.metadata['structural_score'] = float(structural_scores.get(doc_id, 0))
        
        # 7. Apply diversity (MMR-like) to avoid redundancy
        diverse_docs = self._apply_diversity(documents, final_scores, lambda_param=0.7)
        
        return diverse_docs
    
    def _compute_structural_proximity_scores(self, documents: List[Document], 
                                            semantic_scores: Dict[int, float]) -> Dict[int, float]:
        """
        NEW: Boost scores for documents that have structural connections to high-scoring docs
        This helps retrieve sequential chunks that may contain related information
        """
        scores = {}
        
        # Find top-scoring documents (seeds)
        top_threshold = 0.75  # Top 25% by semantic score
        if semantic_scores:
            sorted_semantic = sorted(semantic_scores.values(), reverse=True)
            if len(sorted_semantic) > 0:
                threshold_value = sorted_semantic[min(len(sorted_semantic) // 4, len(sorted_semantic) - 1)]
            else:
                threshold_value = 0
        else:
            threshold_value = 0
        
        # Build doc_id to node_id mapping
        doc_to_node = {}
        for node_id, node_data in self.graph.nodes(data=True):
            if 'document' in node_data:
                doc_to_node[id(node_data['document'])] = node_id
        
        # Find high-scoring seed nodes
        seed_nodes = set()
        for doc in documents:
            doc_id = id(doc)
            if semantic_scores.get(doc_id, 0) >= threshold_value:
                node_id = doc_to_node.get(doc_id)
                if node_id is not None:
                    seed_nodes.add(node_id)
        
        # Compute structural proximity for all documents
        for doc in documents:
            doc_id = id(doc)
            node_id = doc_to_node.get(doc_id)
            
            if node_id is None:
                scores[doc_id] = 0.0
                continue
            
            # Check if this node has structural connection to any seed
            structural_bonus = 0.0
            
            for neighbor in self.graph.neighbors(node_id):
                if neighbor in seed_nodes:
                    edge_data = self.graph.get_edge_data(node_id, neighbor)
                    edge_type = edge_data.get('edge_type', '') if edge_data else ''
                    
                    # Give strong bonus for structural edges (sequential chunks)
                    if edge_type == 'structural':
                        structural_bonus = max(structural_bonus, 1.0)  # Max boost
                    elif 'metadata' in edge_type:
                        structural_bonus = max(structural_bonus, 0.5)  # Medium boost
                    elif edge_type == 'semantic':
                        structural_bonus = max(structural_bonus, 0.3)  # Small boost
            
            scores[doc_id] = structural_bonus
        
        # Normalize scores to [0, 1]
        max_score = max(scores.values()) if scores else 1.0
        if max_score > 0:
            scores = {k: v / max_score for k, v in scores.items()}
        
        return scores
    
    def _compute_metadata_scores(self, query: str, documents: List[Document]) -> Dict[int, float]:
        """
        IMPROVEMENT: Score documents by metadata relevance
        Helps prioritize documents from relevant departments/categories
        """
        scores = {}
        query_lower = query.lower()
        
        # Common metadata indicators
        dept_indicators = {
            'phongdaotao': ['đào tạo', 'học tập', 'sinh viên', 'giảng viên', 'khóa học', 'chương trình'],
            'phongkhaothi': ['khảo thí', 'thi', 'kiểm tra', 'đánh giá', 'chất lượng'],
            'khoa': ['khoa', 'ngành', 'chuyên ngành', 'attt', 'cntt', 'dtvt'],
            'viennghiencuuvahoptacphattrien': ['nghiên cứu', 'khoa học', 'hợp tác', 'phát triển', 'đề tài'],
            'thongtinhvktmm': ['học viện', 'hvktmm', 'cơ yếu', 'chuyển đổi số', 'sáng kiến']
        }
        
        edu_indicators = {
            'daihoc': ['đại học', 'cử nhân', 'k68', 'k69', 'k70'],
            'thacsi': ['thạc sĩ', 'cao học', 'luận văn'],
            'tiensi': ['tiến sĩ', 'nghiên cứu sinh', 'luận án'],
            'giangvien': ['giảng viên', 'giáo viên', 'cán bộ']
        }
        
        for doc in documents:
            score = 0.0
            category = doc.metadata.get('category', '').lower()
            
            # Match department
            for dept, keywords in dept_indicators.items():
                if dept in category:
                    # Boost if query mentions department keywords
                    keyword_matches = sum(1 for kw in keywords if kw in query_lower)
                    if keyword_matches > 0:
                        score += 0.5 + (keyword_matches * 0.1)
                    else:
                        score += 0.2  # Base score for category match
            
            # Match education level
            for edu_level, keywords in edu_indicators.items():
                if edu_level in category:
                    keyword_matches = sum(1 for kw in keywords if kw in query_lower)
                    if keyword_matches > 0:
                        score += 0.3 + (keyword_matches * 0.1)
                    else:
                        score += 0.1
            
            # Normalize to [0, 1]
            scores[id(doc)] = min(1.0, score)
        
        return scores
    
    def _compute_bm25_scores(self, query: str, documents: List[Document]) -> Dict[int, float]:
        """Compute BM25 scores for keyword matching"""
        from collections import Counter
        import math
        
        # Tokenize query
        query_tokens = set(query.lower().split())
        
        # Compute IDF for query terms
        N = len(documents)
        doc_freqs = Counter()
        for doc in documents:
            doc_tokens = set(doc.page_content.lower().split())
            for token in query_tokens:
                if token in doc_tokens:
                    doc_freqs[token] += 1
        
        idf = {token: math.log((N - freq + 0.5) / (freq + 0.5) + 1) 
               for token, freq in doc_freqs.items()}
        
        # Compute BM25 for each document
        k1, b = 1.5, 0.75  # BM25 parameters
        avg_len = sum(len(doc.page_content.split()) for doc in documents) / N
        
        scores = {}
        for doc in documents:
            doc_tokens = doc.page_content.lower().split()
            doc_len = len(doc_tokens)
            token_freqs = Counter(doc_tokens)
            
            score = 0
            for token in query_tokens:
                if token in token_freqs:
                    tf = token_freqs[token]
                    score += idf.get(token, 0) * (tf * (k1 + 1)) / (
                        tf + k1 * (1 - b + b * doc_len / avg_len)
                    )
            
            # Normalize to [0, 1]
            scores[id(doc)] = score / (len(query_tokens) + 1)
        
        return scores
    
    def _get_pagerank_scores(self, documents: List[Document]) -> Dict[int, float]:
        """Get PageRank scores for document importance"""
        scores = {}
        
        # Get node IDs for documents
        doc_to_node = {}
        for node_id, node_data in self.graph.nodes(data=True):
            if 'document' in node_data:
                doc_to_node[id(node_data['document'])] = node_id
        
        # Compute PageRank once (expensive operation)
        if self._pagerank_cache is None:
            self._pagerank_cache = nx.pagerank(self.graph, alpha=0.85)
        
        # Get scores for documents
        for doc in documents:
            node_id = doc_to_node.get(id(doc))
            if node_id is not None:
                scores[id(doc)] = self._pagerank_cache.get(node_id, 0)
        
        # Normalize to [0, 1]
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                scores = {k: v / max_score for k, v in scores.items()}
        
        return scores
    
    def _apply_diversity(self, documents: List[Document], scores: Dict[int, float], 
                        lambda_param: float = 0.7) -> List[Document]:
        """
        Apply MMR-like diversity to avoid redundant results
        MODIFIED: Reduce penalty for structural neighbors (sequential chunks)
        lambda_param: trade-off between relevance (1.0) and diversity (0.0)
        """
        if len(documents) <= self.k:
            return sorted(documents, key=lambda d: scores[id(d)], reverse=True)
        
        # Build doc_id to node_id mapping
        doc_to_node = {}
        for node_id, node_data in self.graph.nodes(data=True):
            if 'document' in node_data:
                doc_to_node[id(node_data['document'])] = node_id
        
        # Get embeddings
        doc_embeddings = {}
        for doc in documents:
            node_id = doc_to_node.get(id(doc))
            if node_id and 'embedding' in self.graph.nodes[node_id]:
                doc_embeddings[id(doc)] = self.graph.nodes[node_id]['embedding']
        
        # If embeddings not available, skip diversity
        if len(doc_embeddings) < len(documents) // 2:
            return sorted(documents, key=lambda d: scores[id(d)], reverse=True)
        
        # MMR selection
        selected = []
        remaining = list(documents)
        
        while len(selected) < self.k and remaining:
            if not selected:
                # First: pick highest scoring doc
                best = max(remaining, key=lambda d: scores[id(d)])
                selected.append(best)
                remaining.remove(best)
            else:
                # Compute MMR scores
                mmr_scores = {}
                for doc in remaining:
                    doc_id = id(doc)
                    if doc_id not in doc_embeddings:
                        mmr_scores[doc_id] = scores[doc_id]
                        continue
                    
                    relevance = scores[doc_id]
                    
                    # Max similarity to selected docs
                    max_sim = 0
                    has_structural_neighbor = False
                    
                    for sel_doc in selected:
                        sel_id = id(sel_doc)
                        if sel_id in doc_embeddings:
                            sim = np.dot(doc_embeddings[doc_id], doc_embeddings[sel_id]) / (
                                np.linalg.norm(doc_embeddings[doc_id]) * 
                                np.linalg.norm(doc_embeddings[sel_id])
                            )
                            max_sim = max(max_sim, sim)
                            
                            # Check if they are structural neighbors
                            doc_node = doc_to_node.get(doc_id)
                            sel_node = doc_to_node.get(sel_id)
                            if doc_node and sel_node and self.graph.has_edge(doc_node, sel_node):
                                edge_data = self.graph.get_edge_data(doc_node, sel_node)
                                if edge_data and edge_data.get('edge_type') == 'structural':
                                    has_structural_neighbor = True
                    
                    # Modified MMR formula: reduce penalty for structural neighbors
                    if has_structural_neighbor:
                        # Only 10% penalty for sequential chunks
                        mmr_scores[doc_id] = lambda_param * relevance - 0.1 * max_sim
                    else:
                        # Normal 30% penalty for non-sequential chunks
                        mmr_scores[doc_id] = lambda_param * relevance - (1 - lambda_param) * max_sim
                
                # Pick best MMR score
                best = max(remaining, key=lambda d: mmr_scores.get(id(d), 0))
                selected.append(best)
                remaining.remove(best)
        
        return selected
