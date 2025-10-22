# Modular Learning Hub (MLH)

**Transform a monolithic LMS into a scalable Python microservices architecture**

[![CI Pipeline](https://img.shields.io/badge/CI-GitHub%20Actions-blue)](https://github.com/franakol/francis-akol-python-backend-assessment/actions)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Project Overview

The Modular Learning Hub (MLH) is a modern, scalable Learning Management System (LMS) built using microservices architecture. This project demonstrates the migration from a monolithic application to a distributed system using Python, FastAPI, PostgreSQL, MongoDB, Redis, and Kubernetes.

### Key Features

- 🔐 **JWT-based Authentication** with role-based access control (RBAC)
- 📚 **Course Management** with flexible content storage
- 🎓 **Student Enrollment** with quota management
- 💳 **Payment Processing** with transaction integrity
- ⚡ **Redis Caching** for high-performance reads
- 🔄 **Async Task Processing** with Celery
- 📊 **Observability** with Prometheus & Grafana
- 🐳 **Containerized** with Docker & Kubernetes
- ✅ **Comprehensive Testing** (unit, integration, API, performance)

---

## 🏗️ Architecture

### Microservices

| Service | Port | Description |
|---------|------|-------------|
| **User Service** | 8001 | Authentication, user management, RBAC |
| **Course Service** | 8002 | Course CRUD, content management, caching |
| **Enrollment Service** | 8003 | Student enrollments, quota enforcement |
| **Payment Service** | 8004 | Payment processing, transaction management |

### Tech Stack

- **Backend:** Python 3.11+, FastAPI
- **Databases:** PostgreSQL 15, MongoDB 6, Redis 7
- **Message Queue:** Celery + Redis/RabbitMQ
- **Containerization:** Docker, Docker Compose
- **Orchestration:** Kubernetes
- **Monitoring:** Prometheus, Grafana, Loguru
- **Testing:** Pytest, Locust
- **CI/CD:** GitHub Actions

### Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                   Client Layer                       │
│         (Web App, Mobile App, Admin Panel)          │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              API Gateway (Future)                    │
└────────────────────┬────────────────────────────────┘
                     │
     ┌───────────────┼───────────────┬────────────────┐
     │               │               │                │
┌────▼────┐    ┌─────▼─────┐   ┌────▼────┐    ┌─────▼─────┐
│  User   │    │  Course   │   │Enrollment│    │  Payment  │
│ Service │    │  Service  │   │ Service  │    │  Service  │
│  :8001  │    │   :8002   │   │  :8003   │    │   :8004   │
└────┬────┘    └─────┬─────┘   └────┬─────┘    └─────┬─────┘
     │               │               │                │
     └───────────────┼───────────────┴────────────────┘
                     │
     ┌───────────────┼───────────────┬────────────────┐
     │               │               │                │
┌────▼────┐    ┌─────▼─────┐   ┌────▼────┐    ┌─────▼─────┐
│PostgreSQL│   │  MongoDB  │   │  Redis  │    │  Celery   │
│   :5432  │   │  :27017   │   │  :6379  │    │  Worker   │
└──────────┘   └───────────┘   └─────────┘    └───────────┘
```

**Detailed Architecture:** See [docs/architecture/HLD.md](docs/architecture/HLD.md)

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose**
- **Git**
- **PostgreSQL client** (optional, for debugging)

### Installation

1. **Clone the repository**
   ```bash
   git clone git@github.com:franakol/francis-akol-python-backend-assessment.git
   cd francis-akol-python-backend-assessment
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services**
   ```bash
   # Copy environment file
   cp .env.example .env
   
   # Start all services (migrations run automatically)
   docker-compose up -d
   ```

> **Note:** Database migrations are now run automatically when services start. No manual migration step required!

4. **Access services**
   - User Service API: http://localhost:8001
   - Course Service API: http://localhost:8002
   - Enrollment Service API: http://localhost:8003
   - Payment Service API: http://localhost:8004
   - Swagger Docs: http://localhost:8001/docs (for each service)
   - Grafana: http://localhost:3000 (admin/admin)
   - Prometheus: http://localhost:9090

---

## 📁 Project Structure

```
francis-akol-python-backend-assessment/
├── services/
│   ├── user-service/           # Authentication & user management
│   ├── course-service/         # Course & content management
│   ├── enrollment-service/     # Enrollment & progress tracking
│   └── payment-service/        # Payment processing
├── docs/
│   ├── architecture/           # HLD, LLD, diagrams
│   ├── api-specs/              # OpenAPI specifications
│   └── deployment/             # Deployment guides
├── tests/
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── performance/            # Load tests (Locust)
├── docker/                     # Docker configurations
├── k8s/                        # Kubernetes manifests
├── .github/
│   └── workflows/              # CI/CD pipelines
├── monitoring/
│   └── grafana-dashboards/     # Grafana dashboard exports
├── docker-compose.yml          # Local development setup
├── CHANGELOG.md                # Project roadmap & changelog
└── README.md                   # This file
```

---

## 🔧 Development

### Local Development (Without Docker)

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies (per service)**
   ```bash
   cd services/user-service
   pip install -r requirements.txt
   ```

3. **Start databases**
   ```bash
   docker-compose up postgres mongodb redis -d
   ```

4. **Run service**
   ```bash
   cd services/user-service
   uvicorn app.main:app --reload --port 8001
   ```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=app --cov-report=html

# Performance tests
locust -f tests/performance/locustfile.py
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint
flake8 .
pylint app/

# Type check
mypy app/
```

---

## 📚 API Documentation

### User Service API

**Base URL:** `http://localhost:8001/api/v1`

#### Authentication
```bash
# Register
curl -X POST http://localhost:8001/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "username": "student123",
    "password": "SecurePass123!",
    "role": "STUDENT"
  }'

# Login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123!"
  }'
```

#### User Management
```bash
# Get current user
curl -X GET http://localhost:8001/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"

# Update profile
curl -X PUT http://localhost:8001/api/v1/users/me \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John", "last_name": "Doe"}'
```

### Course Service API

**Base URL:** `http://localhost:8002/api/v1`

```bash
# List courses
curl -X GET "http://localhost:8002/api/v1/courses/?page=1&page_size=20"

# Get course details
curl -X GET http://localhost:8002/api/v1/courses/{course_id}

# Create course (instructor only)
curl -X POST http://localhost:8002/api/v1/courses/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Mastery",
    "description": "Complete Python course",
    "price": 99.99,
    "max_students": 100
  }'
```

### Enrollment Service API

**Base URL:** `http://localhost:8003/api/v1`

```bash
# Enroll in course
curl -X POST http://localhost:8003/api/v1/enrollments/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"course_id": "course-uuid"}'

# List my enrollments
curl -X GET http://localhost:8003/api/v1/enrollments/ \
  -H "Authorization: Bearer <access_token>"
```

### Payment Service API

**Base URL:** `http://localhost:8004/api/v1`

```bash
# Create payment
curl -X POST http://localhost:8004/api/v1/payments/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": "course-uuid",
    "amount": 99.99,
    "currency": "USD",
    "payment_method": "credit_card"
  }'
```

**Interactive API Docs:** Visit `http://localhost:<port>/docs` for each service

---

## 🧪 Testing Strategy

### Test Coverage

| Service | Unit Tests | Integration Tests | API Tests | Coverage |
|---------|-----------|-------------------|-----------|----------|
| User Service | ✅ | ✅ | ✅ | 85%+ |
| Course Service | ✅ | ✅ | ✅ | 82%+ |
| Enrollment Service | ✅ | ✅ | ✅ | 88%+ |
| Payment Service | ✅ | ✅ | ✅ | 90%+ |

### Test Scenarios

**Core Scenarios:**
1. ✅ User signup → JWT token issued
2. ✅ Course creation by instructor
3. ✅ Student enrollment with quota check
4. ✅ Payment validation and recording
5. ✅ Redis cache hit/miss for course details

**Edge Cases:**
1. ✅ Enrollment quota exceeded (concurrent requests)
2. ✅ Unauthorized access to admin endpoints
3. ✅ Payment failure → enrollment rollback
4. ✅ Celery task retry mechanism
5. ✅ Redis cache expiration fallback

---

## 📊 Monitoring & Observability

### Metrics (Prometheus)

Access Prometheus at http://localhost:9090

**Key Metrics:**
- `api_requests_total` - Total API requests
- `api_request_duration_seconds` - Request latency
- `enrollments_created_total` - Business metric
- `cache_hits_total` / `cache_misses_total` - Cache performance

### Dashboards (Grafana)

Access Grafana at http://localhost:3000 (admin/admin)

**Pre-configured Dashboards:**
1. Service Health Dashboard
2. Business Metrics Dashboard
3. Infrastructure Dashboard

### Logs

Structured JSON logs for all services:
```bash
# View logs
docker-compose logs -f user-service

# Filter by level
docker-compose logs user-service | grep ERROR
```

---

## 🚢 Deployment

### Docker Compose (Local/Dev)

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up user-service -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Clean up volumes
docker-compose down -v
```

### Kubernetes (Production)

```bash
# Create namespace
kubectl create namespace mlh-platform

# Apply configurations
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n mlh-platform

# View logs
kubectl logs -f <pod-name> -n mlh-platform

# Scale deployment
kubectl scale deployment user-service --replicas=3 -n mlh-platform
```

**Deployment Guide:** See [docs/deployment/kubernetes-deployment.md](docs/deployment/kubernetes-deployment.md)

---

## 🔐 Security

### Authentication Flow
1. User provides email/password
2. Service validates credentials
3. JWT access token (15 min) + refresh token (7 days) issued
4. Client includes `Authorization: Bearer <token>` in subsequent requests
5. Service validates JWT signature and expiration

### Authorization (RBAC)
- **ADMIN:** Full system access
- **INSTRUCTOR:** Create/manage courses, view enrollments
- **STUDENT:** Enroll in courses, access content

### Security Best Practices
- ✅ Passwords hashed with bcrypt
- ✅ JWT tokens with short expiration
- ✅ HTTPS/TLS in production
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ No secrets in code (environment variables)

---

## 🎯 Design Decisions & Trade-offs

### Why Microservices?
✅ **Pros:**
- Independent scaling (Course Service needs more replicas)
- Technology diversity (PostgreSQL + MongoDB)
- Fault isolation
- Team autonomy

⚠️ **Cons:**
- Increased complexity
- Network latency
- Data consistency challenges
- More operational overhead

**Decision:** Benefits outweigh costs for this use case

### Why Database per Service?
- Data encapsulation
- Independent schema evolution
- Technology flexibility
- Failure isolation

**Trade-off:** Eventual consistency across services

### Why Redis Caching?
- Reduce database load (Course Service is read-heavy)
- Sub-millisecond response times
- Session storage

**Trade-off:** Cache invalidation complexity

### Why Celery for Async Tasks?
- Reliable message delivery
- Retry mechanisms
- Task scheduling
- Mature ecosystem

**Trade-off:** Additional infrastructure (Redis/RabbitMQ)

---

## 📖 Documentation

- **[CHANGELOG.md](CHANGELOG.md)** - Project roadmap and implementation plan
- **[docs/architecture/HLD.md](docs/architecture/HLD.md)** - High-level design
- **[docs/architecture/LLD.md](docs/architecture/LLD.md)** - Low-level design with sequence diagrams
- **[docs/architecture/service-boundaries.md](docs/architecture/service-boundaries.md)** - Service responsibilities
- **[docs/architecture/database-design.md](docs/architecture/database-design.md)** - Database schemas and optimization
- **[docs/architecture/tech-stack.md](docs/architecture/tech-stack.md)** - Technology choices

---

## 🤝 Contributing

This is an assessment project!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Message Convention
```
type(scope): subject

Examples:
feat(user-service): add JWT refresh token endpoint
fix(enrollment): handle concurrent enrollment race condition
docs(architecture): update HLD with caching strategy
test(payment): add idempotency tests
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Francis Akol**
- GitHub: [@franakol](https://github.com/franakol)
- Email: francisakol40@gmail.com

---

## 🙏 Acknowledgments

- FastAPI team for the amazing framework
- The Python community
- Assessment reviewers: @gniyonge3

---

## 📞 Support

For questions or issues:
1. Check the [documentation](docs/)
2. Review [CHANGELOG.md](CHANGELOG.md) for implementation details
3. Open an issue on GitHub
4. Contact the maintainer

---

**Project Status:** 🚧 In Development  
**Assessment Timeline:** Oct 20-22, 2025  
**Review Date:** Oct 23, 2025

---

Built with ❤️ using Python, FastAPI, and modern DevOps practices