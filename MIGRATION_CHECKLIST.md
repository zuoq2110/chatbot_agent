# Migration Checklist: Single Graph → Department Graphs

## Pre-Migration
- [ ] ✅ Backup completed (document_graph_backup, vector_db_backup)
- [ ] ✅ Dependencies checked and installed
- [ ] ✅ Data analysis completed
- [ ] 📊 Department distribution analyzed

## Migration Steps
- [ ] 🔄 Run `python build_department_graphs.py`
- [ ] 📁 Verify department_graphs/ folder created
- [ ] 📊 Check all departments have graph.pkl files
- [ ] 🧪 Run `python test_department_graphs.py`

## Code Updates  
- [ ] 🔄 Update imports to use DepartmentGraphManager
- [ ] 🔄 Update rag_graph.py get_retriever() function
- [ ] 🔄 Update agent code to use department routing
- [ ] 🔄 Update tool descriptions

## Testing
- [ ] 🧪 Test department detection from queries
- [ ] 🧪 Test department-specific retrieval
- [ ] 🧪 Test smart query routing
- [ ] 🧪 Test end-to-end chatbot functionality

## Performance Comparison
- [ ] ⏱️  Compare query response times (old vs new)
- [ ] 📊 Compare retrieval accuracy
- [ ] 🎯 Verify reduced noise in results
- [ ] 📈 Monitor memory usage

## Rollback Plan (if needed)
- [ ] 🔄 Restore from backup: document_graph_backup → document_graph
- [ ] 🔄 Revert code changes
- [ ] 🔄 Update imports back to GraphRoutedRetriever
- [ ] ✅ Verify old system works

## Post-Migration
- [ ] 📚 Update documentation
- [ ] 🎓 Train team on new department system
- [ ] 🗑️  Clean up backup files (after verification)
- [ ] 📊 Monitor production performance

## Test Queries Success Criteria
### phongdaotao queries should return:
- [ ] Đào tạo, sinh viên, chương trình học content
- [ ] NO khảo thí or nghiên cứu content

### phongkhaothi queries should return:
- [ ] Khảo thí, điểm số, quy đổi content  
- [ ] NO đào tạo curriculum content

### Cross-department queries should return:
- [ ] Results from multiple relevant departments
- [ ] Proper department attribution in metadata
