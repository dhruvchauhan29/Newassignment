# AI Product-to-Code Multi-Agent System

## Quick Start with Docker

### Prerequisites
- Docker
- Docker Compose

### One-Command Startup

```bash
# Build and start all services
docker compose build
docker compose up
```

The API will be available at `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- API Documentation: `http://localhost:8000/redoc`

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

**Required Variables:**
- `SECRET_KEY`: JWT secret key
- `DATABASE_URL`: Database connection string

**Optional Variables (for full functionality):**
- `OPENAI_API_KEY`: For real LLM-powered agents
- `TAVILY_API_KEY`: For web search in research agent
- `LANGFUSE_PUBLIC_KEY`: For LLM observability
- `LANGFUSE_SECRET_KEY`: For LLM observability

## Features Implemented

### ✅ Real Artifact Generation
- Research artifacts persisted to database
- Epics, stories, and specs stored with proper relationships
- Code and validation reports saved as artifacts
- All artifacts retrievable via API

### ✅ Approval Gates Enforced
- Stories cannot be generated until epics are approved
- Specs cannot be generated until stories are approved
- Code cannot be generated until specs are approved
- Approval endpoints available for each artifact type

### ✅ SSE Progress with Stage Details
SSE streams include:
- `stage`: Current stage name (research, epic, story, spec, code, validation)
- `message`: Human-readable progress message
- `timestamp`: ISO 8601 timestamp
- `progress`: Percentage complete (0-100)

### ✅ Artifact Retrieval APIs
- `GET /api/v1/runs/{run_id}/epics` - Get all epics
- `GET /api/v1/runs/{run_id}/stories` - Get all stories
- `GET /api/v1/runs/{run_id}/specs` - Get all specs
- `GET /api/v1/runs/{run_id}/artifacts` - Get all artifacts

### ✅ Approval Endpoints
- `POST /api/v1/runs/{run_id}/epics/{epic_id}/approve`
- `POST /api/v1/runs/{run_id}/stories/{story_id}/approve`
- `POST /api/v1/runs/{run_id}/specs/{spec_id}/approve`

### ✅ Traceability Matrix
- `GET /api/v1/runs/{run_id}/traceability`
- Maps requirements → epics → stories → specs → code → tests
- Returns complete traceability graph in JSON

### ✅ Langfuse Integration
- LLM calls wrapped with Langfuse tracing when keys provided
- Token usage tracked per agent
- Full observability of all LLM interactions
- Callback handlers available for langchain integration

### ✅ Validation Pipeline
- Pytest execution in validation agent
- Linting and formatting checks
- Validation reports stored as artifacts
- Detailed issue categorization

### ✅ Docker Support
- Dockerfile for containerized deployment
- docker-compose.yml with PostgreSQL and app services
- Health checks and dependency management
- Volume mounts for development

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

### Projects
- `GET /api/v1/projects/` - List user's projects
- `POST /api/v1/projects/` - Create new project
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Runs
- `POST /api/v1/runs/` - Create new run
- `GET /api/v1/runs/{id}` - Get run status
- `POST /api/v1/runs/{id}/start` - Start run execution
- `GET /api/v1/runs/{id}/progress` - Stream progress (SSE)
- `GET /api/v1/runs/project/{id}` - List project runs

### Artifacts
- `GET /api/v1/runs/{id}/epics` - Get run epics
- `GET /api/v1/runs/{id}/stories` - Get run stories
- `GET /api/v1/runs/{id}/specs` - Get run specs
- `GET /api/v1/runs/{id}/artifacts` - Get all artifacts

### Approvals
- `POST /api/v1/runs/{id}/epics/{epic_id}/approve` - Approve epic
- `POST /api/v1/runs/{id}/stories/{story_id}/approve` - Approve story
- `POST /api/v1/runs/{id}/specs/{spec_id}/approve` - Approve spec

### Traceability
- `GET /api/v1/runs/{id}/traceability` - Get traceability matrix

### Admin
- `GET /api/v1/admin/users` - List all users (admin only)
- `GET /api/v1/admin/stats` - Get system statistics

### Export
- `GET /api/v1/exports/run/{id}/markdown` - Export as Markdown
- `GET /api/v1/exports/run/{id}/pdf` - Export as PDF

## Development Setup (Without Docker)

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python init_db.py

# Start the server
uvicorn app.main:app --reload

# Access Swagger UI
open http://localhost:8000/docs
```

## Testing the Complete Flow

### 1. Register and Login

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"pass123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=user@test.com&password=pass123"
# Save the token from response
```

### 2. Create Project and Run

```bash
TOKEN="your-token-here"

# Create project
curl -X POST http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Project","description":"Test project"}'

# Create run
curl -X POST http://localhost:8000/api/v1/runs/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project_id":1,"product_idea":"Build a task management app with real-time collaboration"}'

# Start run
curl -X POST http://localhost:8000/api/v1/runs/1/start \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Stream Progress

```bash
# Stream real-time progress (SSE)
curl -N http://localhost:8000/api/v1/runs/1/progress \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Get Artifacts

```bash
# Get epics
curl http://localhost:8000/api/v1/runs/1/epics \
  -H "Authorization: Bearer $TOKEN"

# Get stories
curl http://localhost:8000/api/v1/runs/1/stories \
  -H "Authorization: Bearer $TOKEN"

# Get specs
curl http://localhost:8000/api/v1/runs/1/specs \
  -H "Authorization: Bearer $TOKEN"

# Get all artifacts
curl http://localhost:8000/api/v1/runs/1/artifacts \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Approve Artifacts

```bash
# Approve epic
curl -X POST http://localhost:8000/api/v1/runs/1/epics/1/approve \
  -H "Authorization: Bearer $TOKEN"

# Approve story
curl -X POST http://localhost:8000/api/v1/runs/1/stories/1/approve \
  -H "Authorization: Bearer $TOKEN"

# Approve spec
curl -X POST http://localhost:8000/api/v1/runs/1/specs/1/approve \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Get Traceability Matrix

```bash
curl http://localhost:8000/api/v1/runs/1/traceability \
  -H "Authorization: Bearer $TOKEN"
```

## Architecture

### Agent Pipeline
```
Product Request
    ↓
Research Agent (market analysis, tech recommendations)
    ↓ (artifact persisted)
Epic Agent (high-level features, priorities)
    ↓ (epics persisted, approval required)
Story Agent (user stories, acceptance criteria)
    ↓ (stories persisted, approval required)
Spec Agent (technical specs, API contracts)
    ↓ (specs persisted, approval required)
Code Agent (code generation)
    ↓ (code persisted)
Validation Agent (testing, linting)
    ↓ (validation report persisted)
Complete Project Output
```

### Database Schema
- `users` - User accounts with roles
- `projects` - User-owned projects
- `runs` - Execution runs with status tracking
- `artifacts` - Generated artifacts (research, code, validation)
- `epics` - High-level epics with approval status
- `stories` - User stories with approval status
- `specs` - Technical specifications with approval status
- `traceability_matrix` - Requirement traceability

## Configuration

### Database
- SQLite (default for development)
- PostgreSQL (recommended for production)

### AI Services
- OpenAI: Optional, system works in mock mode without it
- Tavily: Optional, for web search in research agent
- Langfuse: Optional, for LLM observability

## Security
- JWT authentication with bcrypt password hashing
- Role-based access control (User/Admin)
- Input validation and sanitization
- SQL injection protection via ORM
- CORS middleware configured
- CodeQL security scan passed (0 vulnerabilities)

## Observability
- Langfuse integration for LLM tracing
- Token usage tracking per agent
- Error logging and reporting
- Real-time progress streaming

## Production Deployment

### Using Docker Compose

```bash
# Production deployment
docker compose -f docker-compose.yml up -d

# View logs
docker compose logs -f app

# Stop services
docker compose down
```

### Environment Variables for Production

Update `.env` with:
- Strong `SECRET_KEY`
- PostgreSQL `DATABASE_URL`
- Real API keys for OpenAI, Tavily, Langfuse

## License

This is an assignment project for demonstration purposes.

## Support

For issues or questions:
- Check Swagger UI at `/docs` for API documentation
- Review logs with `docker compose logs`
- See IMPLEMENTATION_SUMMARY.md for technical details
