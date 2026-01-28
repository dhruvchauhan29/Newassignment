"""Spec agent for creating technical specifications."""
import os
from typing import Any, Dict

from app.agents.base import BaseAgent


class SpecAgent(BaseAgent):
    """Agent for creating technical specifications."""

    def __init__(self):
        """Initialize spec agent."""
        super().__init__(name="SpecAgent")
        self.use_mock = not os.getenv("OPENAI_API_KEY")
        self.llm = None
        
        if not self.use_mock:
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(model=self.model, temperature=0.5)
            except Exception as e:
                self.log(f"Failed to initialize LLM, using mock mode: {e}", "warning")
                self.use_mock = True

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute spec creation.

        Args:
            input_data: Contains 'stories'

        Returns:
            Technical specifications
        """
        stories = input_data.get("stories", "")
        self.log("Creating technical specifications")

        if self.use_mock:
            # Mock technical specifications response
            specs_data = """
# Technical Specifications

## Component 1: Authentication Service
**Component Name:** auth-service
**Technology Stack:** Node.js, Express, JWT, bcrypt
**Technical Details:**
- Microservice architecture
- RESTful API
- Token-based authentication
- Password hashing with bcrypt
- Redis for session management

**API Endpoints:**
```
POST /api/auth/register
Request: { email, password, name }
Response: { user_id, message }

POST /api/auth/login
Request: { email, password }
Response: { token, user, expires_in }

POST /api/auth/logout
Headers: { Authorization: Bearer <token> }
Response: { message }

POST /api/auth/refresh
Request: { refresh_token }
Response: { token, expires_in }

POST /api/auth/reset-password
Request: { email }
Response: { message }
```

**Data Models:**
```javascript
User {
  id: UUID (primary key)
  email: String (unique, indexed)
  password_hash: String
  name: String
  created_at: Timestamp
  updated_at: Timestamp
  last_login: Timestamp
  is_active: Boolean
  email_verified: Boolean
}

Session {
  id: UUID
  user_id: UUID (foreign key)
  token: String (indexed)
  refresh_token: String
  expires_at: Timestamp
  created_at: Timestamp
  ip_address: String
  user_agent: String
}
```

**Dependencies:**
- Database: PostgreSQL 14+
- Cache: Redis 6+
- Email service for verification

---

## Component 2: User Management Service
**Component Name:** user-service
**Technology Stack:** Python, FastAPI, SQLAlchemy, Pydantic
**Technical Details:**
- RESTful API
- CRUD operations for users
- Profile management
- Settings management

**API Endpoints:**
```
GET /api/users/{user_id}
Headers: { Authorization: Bearer <token> }
Response: { user object }

PUT /api/users/{user_id}
Headers: { Authorization: Bearer <token> }
Request: { name, profile_data }
Response: { user object }

GET /api/users/{user_id}/settings
Response: { settings object }

PUT /api/users/{user_id}/settings
Request: { notification_prefs, theme, timezone }
Response: { settings object }

DELETE /api/users/{user_id}
Response: { message }
```

**Data Models:**
```python
UserProfile {
  user_id: UUID (foreign key)
  avatar_url: String
  bio: Text
  phone: String
  location: String
  preferences: JSONB
}

UserSettings {
  user_id: UUID (foreign key)
  theme: Enum['light', 'dark', 'auto']
  timezone: String
  language: String
  email_notifications: Boolean
  push_notifications: Boolean
  newsletter: Boolean
}
```

**Dependencies:**
- auth-service for authentication
- storage-service for file uploads

---

## Component 3: Data Management Service
**Component Name:** data-service
**Technology Stack:** Python, FastAPI, Pandas, Celery
**Technical Details:**
- Async task processing
- Data import/export
- Data validation
- Batch processing

**API Endpoints:**
```
POST /api/data/import
Headers: { Authorization: Bearer <token> }
Request: multipart/form-data { file, format }
Response: { job_id, status }

GET /api/data/import/{job_id}
Response: { job_id, status, progress, errors }

POST /api/data/export
Request: { format, filters, fields }
Response: { job_id }

GET /api/data/export/{job_id}
Response: { download_url, expires_at }

GET /api/data/records
Query: { page, limit, filter, sort }
Response: { records[], total, page, pages }
```

**Data Models:**
```python
ImportJob {
  id: UUID
  user_id: UUID
  filename: String
  format: Enum['csv', 'json', 'xml']
  status: Enum['pending', 'processing', 'completed', 'failed']
  total_records: Integer
  processed_records: Integer
  error_records: Integer
  errors: JSONB
  created_at: Timestamp
}

DataRecord {
  id: UUID
  user_id: UUID
  data: JSONB
  source: String
  imported_at: Timestamp
  updated_at: Timestamp
}
```

**Dependencies:**
- RabbitMQ for task queue
- S3/MinIO for file storage

---

## Component 4: Analytics Service
**Component Name:** analytics-service
**Technology Stack:** Go, Gin, ClickHouse, WebSocket
**Technical Details:**
- Real-time data processing
- Time-series analytics
- WebSocket for live updates
- High-performance queries

**API Endpoints:**
```
GET /api/analytics/dashboard
Query: { date_from, date_to, metrics }
Response: { metrics object }

GET /api/analytics/reports
Response: { reports[] }

POST /api/analytics/reports
Request: { name, config, schedule }
Response: { report object }

WS /api/analytics/live
WebSocket connection for real-time updates
```

**Data Models:**
```go
type Metric struct {
    ID        string    `json:"id"`
    UserID    string    `json:"user_id"`
    Name      string    `json:"name"`
    Value     float64   `json:"value"`
    Timestamp time.Time `json:"timestamp"`
    Tags      map[string]string `json:"tags"`
}

type Report struct {
    ID        string `json:"id"`
    UserID    string `json:"user_id"`
    Name      string `json:"name"`
    Config    map[string]interface{} `json:"config"`
    Schedule  string `json:"schedule"`
    CreatedAt time.Time `json:"created_at"`
}
```

**Dependencies:**
- ClickHouse for time-series data
- Redis for caching

---

## Component 5: Notification Service
**Component Name:** notification-service
**Technology Stack:** Node.js, Socket.io, SendGrid
**Technical Details:**
- Real-time notifications via WebSocket
- Email notifications
- Push notifications
- Notification history

**API Endpoints:**
```
GET /api/notifications
Query: { page, limit, unread_only }
Response: { notifications[], total }

PUT /api/notifications/{id}/read
Response: { message }

PUT /api/notifications/read-all
Response: { message }

WS /notifications
WebSocket for real-time notifications
```

**Data Models:**
```javascript
Notification {
  id: UUID
  user_id: UUID (indexed)
  type: String
  title: String
  message: Text
  data: JSONB
  read: Boolean
  created_at: Timestamp
  read_at: Timestamp
}
```

**Dependencies:**
- SendGrid for email
- Firebase for push notifications
- Socket.io for WebSocket

---

## Infrastructure Requirements

### Database
- PostgreSQL 14+ for relational data
- ClickHouse for analytics
- Redis 6+ for caching and sessions

### Message Queue
- RabbitMQ or Apache Kafka

### Storage
- S3-compatible object storage

### Deployment
- Docker containers
- Kubernetes orchestration
- CI/CD pipeline
- Monitoring and logging (Prometheus, Grafana, ELK)

### Security
- HTTPS/TLS everywhere
- API rate limiting
- Input validation
- SQL injection prevention
- XSS protection
- CSRF tokens
- Security headers
"""
            return {
                "success": True,
                "specs": specs_data,
                "component_count": 5,
                "api_endpoints": 25,
                "data_models": 8
            }

        prompt = f"""
        Based on the following user stories, create detailed technical specifications.
        For each component, provide:
        - Component name
        - Technical details
        - API endpoints
        - Data models
        - Dependencies

        User Stories: {stories}

        Format as JSON array.
        """

        try:
            response = await self.llm.ainvoke(prompt)
            specs_data = response.content

            return {
                "success": True,
                "specs": specs_data,
            }
        except Exception as e:
            self.log(f"Spec creation failed: {str(e)}", "error")
            return {"success": False, "error": str(e)}
