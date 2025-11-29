"""
Graph-Routed RAG Package

This package implements Graph-Routed RAG with learned routing policy.

Main components:
- DocumentGraph: Build document graph with multiple edge types
- SubgraphPartitioner: Partition graph into subgraphs
- GraphRoutedRetriever: Retrieve using graph structure
- LearnedRouter: Neural routing policy
"""

from .graph_builder import DocumentGraph
from .subgraph_partitioner import SubgraphPartitioner
from .graph_retriever import GraphRoutedRetriever

__all__ = [
    'DocumentGraph',
    'SubgraphPartitioner',
    'GraphRoutedRetriever',
]
