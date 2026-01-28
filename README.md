# AI Product-to-Code Multi-Agent System

A comprehensive FastAPI-based system that uses multiple AI agents to transform product ideas into production-ready code through an intelligent orchestration workflow.

## 🚀 Features

- **Multi-Agent Architecture**: Orchestrated workflow using LangGraph
- **Modern FastAPI**: Async/await with Python 3.11+
- **PostgreSQL Database**: SQLAlchemy 2.0+ with async support
- **JWT Authentication**: Secure role-based access control
- **Real-time Streaming**: Server-Sent Events (SSE) for progress updates
- **Export Capabilities**: PDF and Markdown report generation
- **Observability**: Integrated Langfuse for agent tracing
- **Production Ready**: Proper error handling, validation, and testing

## 📋 Architecture

### Agent Workflow

```
Research → Epic Creation → Story Writing → Spec Generation → Code Generation → Validation
```

### Agents

1. **Research Agent**: Conducts market research and analyzes product ideas
2. **Epic Agent**: Creates high-level product epics
3. **Story Agent**: Generates detailed user stories
4. **Spec Agent**: Produces technical specifications
5. **Code Agent**: Generates production-ready code
6. **Validation Agent**: Validates generated code

## 🛠️ Technology Stack

- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL with asyncpg and pgvector
- **ORM**: SQLAlchemy 2.0+
- **AI/LLM**: LangChain, LangGraph, OpenAI
- **Search**: Tavily Python
- **Observability**: Langfuse
- **Authentication**: JWT (python-jose)
- **Testing**: pytest, pytest-asyncio
- **Code Quality**: ruff

## 📦 Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- OpenAI API Key
- (Optional) Tavily API Key
- (Optional) Langfuse account

### Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd Newassignment
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment**

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Required
SECRET_KEY="your-secret-key-change-this"
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/ai_product_db"
OPENAI_API_KEY="sk-your-openai-api-key"

# Optional
TAVILY_API_KEY="tvly-your-tavily-api-key"
LANGFUSE_PUBLIC_KEY="pk-lf-your-public-key"
LANGFUSE_SECRET_KEY="sk-lf-your-secret-key"
```

5. **Create database**

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ai_product_db;
\q
```

6. **Run migrations**

```bash
alembic upgrade head
```

7. **Start the application**

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token
- `GET /api/v1/auth/me` - Get current user info

### Projects

- `POST /api/v1/projects/` - Create project
- `GET /api/v1/projects/` - List user projects
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Runs

- `POST /api/v1/runs/` - Create new run
- `GET /api/v1/runs/{id}` - Get run details
- `GET /api/v1/runs/project/{id}` - List project runs
- `POST /api/v1/runs/{id}/start` - Start run with SSE streaming

### Exports

- `GET /api/v1/exports/run/{id}/pdf` - Export run as PDF
- `GET /api/v1/exports/run/{id}/markdown` - Export run as Markdown

### Admin

- `GET /api/v1/admin/users` - List all users (admin only)
- `GET /api/v1/admin/stats` - Get system statistics (admin only)

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

## 🔍 Development

### Code Quality

Format and lint code:

```bash
# Run ruff linter
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### Running in Development

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🐳 Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: ai_product_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://user:password@db:5432/ai_product_db
      SECRET_KEY: your-secret-key
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - db

volumes:
  postgres_data:
```

Run with Docker:

```bash
docker-compose up -d
```

## 📊 Project Structure

```
/app
  /api
    /v1
      /endpoints     # API route handlers
  /core            # Core configuration
  /db              # Database setup
  /models          # SQLAlchemy models
  /schemas         # Pydantic schemas
  /agents          # AI agents
  /services        # Business logic
  /utils           # Utility functions
  main.py          # FastAPI application

/tests             # Test files
/alembic           # Database migrations
```

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control (User/Admin)
- SQL injection protection via SQLAlchemy
- Input validation with Pydantic
- CORS configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues, questions, or contributions, please open an issue on GitHub.

## 🎯 Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Redis caching layer
- [ ] Celery for background tasks
- [ ] Enhanced observability with metrics
- [ ] Multi-model support (Claude, Gemini, etc.)
- [ ] Code execution sandbox
- [ ] GitHub integration for code deployment
- [ ] Enhanced test coverage
- [ ] CI/CD pipeline