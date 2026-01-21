# Quick Reference Guide

## 🚀 Common Commands

### Setup
```bash
# Linux/Mac
./setup.sh

# Windows
setup.bat

# Manual setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Running the Application
```bash
# Process PDF (Phase 2)
python src/ingestion/pdf_processor.py

# Run web app (Phase 4)
streamlit run src/web/app.py

# Run tests
pytest tests/

# Run notebook
jupyter notebook notebooks/experiment.ipynb
```

## 🔑 API Keys

### OpenAI (Recommended)
1. Go to https://platform.openai.com/
2. Create account / Login
3. Go to API Keys section
4. Create new secret key
5. Add to `.env`: `OPENAI_API_KEY=sk-...`

### Anthropic Claude (Alternative)
1. Go to https://console.anthropic.com/
2. Create account / Login
3. Go to API Keys
4. Create new key
5. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

## 📊 Key Configuration Parameters

| Parameter | Location | Description | Default |
|-----------|----------|-------------|---------|
| Chunk Size | `config/config.yaml` | Size of text chunks | 1000 |
| Chunk Overlap | `config/config.yaml` | Overlap between chunks | 200 |
| Top K | `config/config.yaml` | Results to retrieve | 5 |
| LLM Model | `.env` | Which model to use | gpt-4o-mini |
| Temperature | `.env` | Response randomness | 0.3 |

## 🎯 Common Issues & Solutions

### Issue: "OpenAI API key not found"
**Solution**: Copy `.env.example` to `.env` and add your API key

### Issue: "PDF not found"
**Solution**: Ensure PDF is in `data/raw/` directory

### Issue: "Module not found"
**Solution**: Activate virtual environment: `source venv/bin/activate`

### Issue: "ChromaDB error"
**Solution**: Delete `data/chroma_db/` and reprocess PDF

### Issue: "Out of memory"
**Solution**: Reduce chunk size in config or process in batches

## 🔍 Testing Your Setup

```python
# Test 1: Configuration loading
python src/utils.py

# Test 2: Check directories
ls -la data/

# Test 3: Verify environment
python -c "import langchain; print('LangChain OK')"
python -c "import chromadb; print('ChromaDB OK')"
python -c "import streamlit; print('Streamlit OK')"
```

## 📚 Helpful Resources

- [LangChain Docs](https://python.langchain.com/docs/get_started/introduction)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Docling GitHub](https://github.com/DS4SD/docling)
- [OpenAI API Docs](https://platform.openai.com/docs/introduction)

## 🎓 Project Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| Phase 1 | Day 1 | Setup & Configuration ✅ |
| Phase 2 | Day 2-3 | PDF Processing & Chunking |
| Phase 3 | Day 3-4 | RAG Pipeline |
| Phase 4 | Day 4-5 | Web Application |
| Phase 5 | Day 6 | Testing & Refinement |
| Phase 6 | Day 7 | Presentation |

## 💡 Best Practices

1. **Commit often**: Git commit after each working feature
2. **Test early**: Don't wait until the end to test
3. **Start simple**: Get basic version working first
4. **Document**: Comment your code and decisions
5. **Collaborate**: Regular team sync-ups
6. **Backup**: Keep copies of processed data

## 🐛 Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Getting Help

1. Check this guide first
2. Review relevant documentation
3. Check project issues/comments
4. Ask team members
5. Consult course materials

---

**Last Updated**: Phase 1 Complete
**Next Steps**: Begin Phase 2 - PDF Processing
