"""
Subgraph Partitioner for Document Graph
AUTOMATED community detection & hierarchical clustering
No hardcoded rules, fully data-driven
"""
import logging
from typing import List, Dict, Any, Set, Tuple
import networkx as nx
from langchain_core.documents import Document
import numpy as np

logger = logging.getLogger(__name__)


class SubgraphPartitioner:
    """Automated partition of document graph using community detection"""
    
    def __init__(self, graph: nx.Graph):
        """
        Args:
            graph: Document graph from DocumentGraph
        """
        self.graph = graph
        self.subgraphs = {}  # Dict[subgraph_id, Set[node_ids]]
        self.community_summaries = {}  # Dict[community_id, summary_text]
        self.community_centroids = {}  # Dict[community_id, centroid_embedding]
    
    @property
    def communities(self):
        """Alias for subgraphs for backward compatibility"""
        return self.subgraphs
        
    def partition_by_metadata(self, metadata_key: str = 'category') -> Dict[str, Set[int]]:
        """
        Partition graph by metadata category (hierarchical)
        
        Args:
            metadata_key: Metadata field to partition by (e.g., 'category', 'department')
            
        Returns:
            Dict mapping category -> set of node IDs
        """
        logger.info(f"Partitioning graph by metadata: {metadata_key}")
        
        subgraphs = {}
        
        for node_id in self.graph.nodes():
            metadata = self.graph.nodes[node_id]['metadata']
            category = metadata.get(metadata_key, 'unknown')
            
            if category not in subgraphs:
                subgraphs[category] = set()
            
            subgraphs[category].add(node_id)
        
        self.subgraphs = subgraphs
        
        # Log statistics
        for category, nodes in subgraphs.items():
            logger.info(f"  Subgraph '{category}': {len(nodes)} nodes")
        
        return subgraphs
    
    def partition_by_community_detection(self, algorithm: str = 'louvain') -> Dict[int, Set[int]]:
        """
        HYBRID: Partition graph using metadata-aware community detection
        Combines structural clustering with metadata constraints
        
        Args:
            algorithm: 'louvain' (default) or 'label_propagation'
            
        Returns:
            Dict mapping community_id -> set of node IDs
        """
        logger.info(f"Hybrid partitioning with {algorithm} + metadata...")
        
        # IMPROVEMENT 1: Pre-partition by metadata to preserve hierarchical structure
        metadata_groups = self._pregroup_by_metadata()
        
        # IMPROVEMENT 2: Run community detection within each metadata group
        all_subgraphs = {}
        comm_id_counter = 0
        
        for meta_key, node_ids in metadata_groups.items():
            if len(node_ids) < 2:
                # Single node groups become their own community
                all_subgraphs[comm_id_counter] = node_ids
                comm_id_counter += 1
                continue
            
            # Create subgraph for this metadata group
            subgraph = self.graph.subgraph(node_ids)
            
            if algorithm == 'louvain':
                try:
                    import community as community_louvain
                    communities = community_louvain.best_partition(subgraph)
                except ImportError:
                    logger.warning("python-louvain not installed, falling back to label_propagation")
                    algorithm = 'label_propagation'
            
            if algorithm == 'label_propagation':
                from networkx.algorithms import community
                communities_gen = community.label_propagation_communities(subgraph)
                communities = {}
                for local_comm_id, nodes in enumerate(communities_gen):
                    for node in nodes:
                        communities[node] = local_comm_id
            
            # Map local communities to global IDs
            local_subgraphs = {}
            for node, local_comm_id in communities.items():
                if local_comm_id not in local_subgraphs:
                    local_subgraphs[local_comm_id] = set()
                local_subgraphs[local_comm_id].add(node)
            
            # Assign global community IDs
            for nodes in local_subgraphs.values():
                all_subgraphs[comm_id_counter] = nodes
                comm_id_counter += 1
        
        self.subgraphs = all_subgraphs
        
        # BUGFIX: Assign community attribute to all nodes
        logger.info("Assigning community IDs to nodes...")
        for comm_id, node_ids in all_subgraphs.items():
            for node_id in node_ids:
                self.graph.nodes[node_id]['community'] = comm_id
        
        # Auto-generate community summaries and centroids
        self._generate_community_metadata()
        
        # Log statistics
        logger.info(f"Found {len(all_subgraphs)} communities (metadata-aware)")
        for comm_id, nodes in list(all_subgraphs.items())[:5]:
            summary = self.community_summaries.get(comm_id, '')
            logger.info(f"  Community {comm_id}: {len(nodes)} nodes - {summary[:80]}...")
        
        return all_subgraphs
    
    def _pregroup_by_metadata(self) -> Dict[str, Set[int]]:
        """
        Pre-group nodes by hierarchical metadata path
        E.g., phongdaotao/daihoc, phongdaotao/thacsi, khoa, etc.
        """
        groups = {}
        
        for node_id in self.graph.nodes():
            metadata = self.graph.nodes[node_id]['metadata']
            
            # Build hierarchical key from category
            category = metadata.get('category', 'unknown')
            
            # Normalize category to hierarchical path
            if '/' in category:
                # Already hierarchical (e.g., phongdaotao/daihoc)
                key = category
            else:
                # Flat category (e.g., khoa, phongkhaothi)
                key = category
            
            if key not in groups:
                groups[key] = set()
            groups[key].add(node_id)
        
        logger.info(f"Pre-grouped into {len(groups)} metadata categories")
        return groups
    
    def _generate_community_metadata(self):
        """
        ENHANCED: Create metadata-enriched summaries and centroids
        Includes hierarchical category info for better routing
        """
        logger.info("Generating enhanced community metadata...")
        
        for comm_id, node_ids in self.subgraphs.items():
            # 1. Extract representative texts AND metadata
            texts = []
            embeddings = []
            categories = []
            
            for node_id in list(node_ids)[:10]:  # Sample up to 10 nodes
                content = self.graph.nodes[node_id].get('content', '')
                metadata = self.graph.nodes[node_id].get('metadata', {})
                
                if content:
                    texts.append(content[:200])
                
                # Collect category info
                category = metadata.get('category', '')
                if category and category not in categories:
                    categories.append(category)
                
                # Get embedding if cached
                embedding = self.graph.nodes[node_id].get('embedding')
                if embedding is not None:
                    embeddings.append(embedding)
            
            # 2. Create ENRICHED summary: metadata + content
            summary_parts = []
            
            # Add metadata prefix (hierarchical path)
            if categories:
                # Use most common category or first one
                primary_category = categories[0]
                summary_parts.append(f"[{primary_category}]")
            
            # Add content snippets
            if texts:
                summary_parts.extend(texts[:2])  # Top 2 texts
            
            summary = " | ".join(summary_parts)
            self.community_summaries[comm_id] = summary
            
            # Store metadata for routing
            if not hasattr(self, 'community_metadata'):
                self.community_metadata = {}
            self.community_metadata[comm_id] = {
                'categories': categories,
                'node_count': len(node_ids)
            }
            
            # 3. Create centroid: average of all embeddings
            if embeddings:
                centroid = np.mean(embeddings, axis=0)
                self.community_centroids[comm_id] = centroid
        
        logger.info(f"✅ Generated enhanced metadata for {len(self.subgraphs)} communities")
    
    def get_subgraph(self, subgraph_id: Any) -> Set[int]:
        """Get node IDs in a subgraph"""
        return self.subgraphs.get(subgraph_id, set())
    
    def get_all_subgraphs(self) -> Dict[Any, Set[int]]:
        """Get all subgraphs"""
        return self.subgraphs
    
    def get_subgraph_for_node(self, node_id: int) -> Any:
        """Find which subgraph contains a node"""
        for subgraph_id, nodes in self.subgraphs.items():
            if node_id in nodes:
                return subgraph_id
        return None
    
    def route_query_to_communities(self, query_embedding: np.ndarray, top_k: int = 5, min_similarity: float = 0.35) -> List[Tuple[int, float]]:
        """
        IMPROVED ROUTING: Two-stage with adaptive threshold to avoid centroid averaging problem
        
        FIXES:
        - Increased top_k from 2 to 5 to avoid missing relevant communities
        - Added min_similarity threshold to filter out low-confidence matches
        - Adaptive fallback: returns more communities if confidence is low
        
        Args:
            query_embedding: Query embedding vector
            top_k: Maximum number of communities to route to (default: 5, increased from 2)
            min_similarity: Minimum similarity threshold (default: 0.35)
            
        Returns:
            List of (community_id, similarity_score) tuples
        """
        if not self.community_centroids:
            logger.warning("No community centroids available. Run partition_by_community_detection first.")
            return []
        
        # IMPROVEMENT 3: Multi-factor scoring
        community_scores = []
        
        for comm_id, centroid in self.community_centroids.items():
            # Factor 1: Semantic similarity (embedding)
            semantic_sim = np.dot(query_embedding, centroid) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(centroid)
            )
            
            # Factor 2: Metadata boost (community size/importance)
            metadata_boost = 0.0
            if hasattr(self, 'community_metadata'):
                meta = self.community_metadata.get(comm_id, {})
                # Boost larger communities (more comprehensive information)
                size_boost = min(0.1, meta.get('node_count', 0) / 100)
                metadata_boost += size_boost
            
            # Combined score: 85% semantic + 15% metadata
            final_score = 0.85 * semantic_sim + 0.15 * metadata_boost
            community_scores.append((comm_id, float(final_score)))
        
        # Sort by score desc
        community_scores.sort(key=lambda x: x[1], reverse=True)
        
        # IMPROVEMENT: Adaptive threshold-based selection
        # Take top-k communities that meet minimum similarity threshold
        candidate_communities = [
            (comm_id, score) for comm_id, score in community_scores
            if score >= min_similarity
        ][:top_k]
        
        # FALLBACK: If confidence is low (best score < 0.5), expand search
        if candidate_communities and candidate_communities[0][1] < 0.5:
            logger.warning(f"⚠️  Low routing confidence (best={candidate_communities[0][1]:.3f}). Expanding to top {min(top_k + 3, len(community_scores))} communities.")
            candidate_communities = community_scores[:min(top_k + 3, len(community_scores))]
        
        # FALLBACK 2: If no communities meet threshold, take top-3 anyway
        if not candidate_communities:
            logger.warning(f"⚠️  No communities above threshold {min_similarity}. Taking top-3 by default.")
            candidate_communities = community_scores[:3]
        
        top_communities = candidate_communities
        
        logger.info(f"Query routed to {len(top_communities)} communities (threshold={min_similarity}):")
        for comm_id, score in top_communities:
            summary = self.community_summaries.get(comm_id, '')[:60]
            logger.info(f"  Community {comm_id} (sim={score:.3f}): {summary}...")
        
        return top_communities
