#!/usr/bin/env python3
"""
Rebuild vector database with improved chunking strategy
"""
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.rag.retriever import create_enhanced_vector_database

def rebuild_with_improved_chunking():
    """Rebuild vector database with improved chunking"""
    print("🔧 Rebuilding Vector Database with Improved Chunking")
    print("=" * 60)
    
    # Backup old database
    old_db_path = "./vector_db"
    backup_path = "./vector_db_backup"
    
    if os.path.exists(old_db_path):
        print("📦 Backing up old database...")
        import shutil
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path)
        shutil.copytree(old_db_path, backup_path)
        print("✅ Old database backed up")
        
        # Remove old database
        shutil.rmtree(old_db_path)
        print("🗑️  Old database removed")
    
    # Create new database with improved chunking
    print("🚀 Creating new database with improved chunking...")
    try:
        documents = create_enhanced_vector_database(
            output_path="./vector_db",
            data_dir="./data"
        )
        
        print(f"✅ Successfully created new database with {len(documents)} documents")
        
        # Analyze the new database
        print("\n📊 NEW DATABASE ANALYSIS:")
        print("=" * 40)
        
        # Count structured chunks
        structured_chunks = 0
        table_chunks = 0
        total_chunks = len(documents)
        
        # Count points in chunks
        chunks_with_multiple_points = 0
        all_chunks_with_points = 0
        
        for doc in documents:
            content = doc.page_content.lower()
            
            # Check for structured content
            if any(point in content for point in ['a)', 'b)', 'c)', 'd)', 'đ)', 'e)']):
                all_chunks_with_points += 1
                
                # Count how many points in this chunk
                points_count = sum(1 for point in ['a)', 'b)', 'c)', 'd)', 'đ)', 'e)'] if point in content)
                if points_count > 1:
                    chunks_with_multiple_points += 1
                    
            # Check metadata for structured content
            if doc.metadata.get('contains_table', False):
                table_chunks += 1
            
            # Check for structured preservation indicators
            if 'chunk_type' in doc.metadata and doc.metadata['chunk_type'] == 'structured':
                structured_chunks += 1
        
        print(f"Total Documents: {total_chunks}")
        print(f"Chunks with Points: {all_chunks_with_points}")
        print(f"Chunks with Multiple Points: {chunks_with_multiple_points}")
        print(f"Table Chunks: {table_chunks}")
        print(f"Structured Chunks: {structured_chunks}")
        
        # Calculate improvement metrics
        if all_chunks_with_points > 0:
            consolidation_rate = (chunks_with_multiple_points / all_chunks_with_points) * 100
            print(f"Point Consolidation Rate: {consolidation_rate:.1f}%")
            
            if consolidation_rate > 50:
                print("✅ EXCELLENT: High point consolidation achieved")
            elif consolidation_rate > 30:
                print("✅ GOOD: Moderate point consolidation")
            else:
                print("⚠️  NEEDS WORK: Low point consolidation")
        
        print("\n🎯 Ready to test improved retrieval!")
        print("Run: python test_final_system.py")
        
    except Exception as e:
        print(f"❌ Error creating new database: {e}")
        import traceback
        traceback.print_exc()
        
        # Restore backup if available
        if os.path.exists(backup_path):
            print("🔄 Restoring backup database...")
            shutil.copytree(backup_path, old_db_path)
            print("✅ Backup restored")

if __name__ == "__main__":
    rebuild_with_improved_chunking()