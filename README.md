# KMA Chatbot Backend

Backend API cho hệ thống Chatbot KMA - sử dụng FastAPI, LangChain và GraphRAG.

## Cấu trúc dự án

```
chatbot_agent/
├── src/
│   ├── agent/          # ReAct Agent với LangGraph
│   ├── backend/        # FastAPI Backend
│   │   ├── api/        # API endpoints
│   │   ├── auth/       # Authentication
│   │   ├── db/         # Database (MongoDB)
│   │   ├── models/     # Pydantic models
│   │   └── services/   # Business logic
│   ├── graph_rag/      # GraphRAG retrieval
│   ├── llm/            # LLM configuration
│   ├── rag/            # RAG components
│   └── score/          # Student score tools
├── data/               # Knowledge base documents
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Yêu cầu

- Python 3.12+
- Docker & Docker Compose
- MongoDB
- Ollama (local LLM)

## Cài đặt

### 1. Clone và setup môi trường

```bash
# Clone repository
git clone <repo-url>
cd chatbot_agent

# Tạo virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### 2. Cấu hình môi trường

Tạo file `.env`:

```env
# MongoDB
MONGO_USER=admin
MONGO_PASSWORD=your_password
MONGO_DB=chatbot
MONGO_URI=mongodb://admin:your_password@localhost:27017

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest

# Google Gemini (optional fallback)
GOOGLE_API_KEY=your_api_key
GEMINI_MODEL=gemini-2.0-flash

# JWT Auth
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
PYTHONPATH=./src
```

### 3. Chạy với Docker

```bash
# Build và start tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f backend

# Stop
docker-compose down
```

### 4. Chạy local (development)

```bash
# Activate venv
.venv\Scripts\activate

# Chạy backend (Windows PowerShell) - từ thư mục chatbot_agent
$env:PYTHONPATH=".\src"; python -m uvicorn backend.main:app --reload --port 3434

# Chạy backend (Linux/Mac) - từ thư mục chatbot_agent
PYTHONPATH=./src python -m uvicorn backend.main:app --reload --port 3434
```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Đăng ký
- `POST /api/auth/login` - Đăng nhập
- `GET /api/auth/me` - Thông tin user

### Chat

- `POST /api/chat/conversations` - Tạo conversation mới
- `GET /api/chat/conversations` - Lấy danh sách conversations
- `POST /api/chat/{conversation_id}/messages` - Gửi tin nhắn

### Admin

- `GET /api/admin/models/current` - Model đang dùng
- `POST /api/admin/models/select` - Chọn model (Ollama/Gemini)

## Tech Stack

- **FastAPI** - Web framework
- **LangChain** - LLM orchestration
- **LangGraph** - Agent workflow
- **MongoDB** - Database
- **Ollama** - Local LLM
- **FAISS** - Vector search
- **NetworkX** - Graph algorithms

## Development

```bash
# Format code
black src/

# Lint
pylint src/
```

## License

MIT
