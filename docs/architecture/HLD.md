# High-Level Design (HLD) - Modular Learning Hub

## Executive Summary

The Modular Learning Hub (MLH) is a scalable microservices-based Learning Management System (LMS) designed to replace a monolithic architecture. The system enables course creation, student enrollment, and payment processing through independently deployable, fault-tolerant services.

**Project Goal:** Transform a legacy monolithic LMS into a modern, scalable microservices architecture using Python, FastAPI, PostgreSQL, MongoDB, Redis, and Kubernetes.

---

## System Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         External Actors                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────┐    ┌────────────┐    ┌─────────┐    ┌──────────┐ │
│  │ Students │    │Instructors │    │  Admin  │    │  Payment │ │
│  │          │    │            │    │         │    │  Gateway │ │
│  └─────┬────┘    └──────┬─────┘    └────┬────┘    └─────┬────┘ │
│        │                │               │               │       │
└────────┼────────────────┼───────────────┼───────────────┼───────┘
         │                │               │               │
         └────────────────┼───────────────┴───────────────┘
                          │
                ┌─────────▼─────────┐
                │   API Gateway     │
                │   (Future/Opt)    │
                └─────────┬─────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
    ┌────▼────┐     ┌─────▼─────┐    ┌────▼────┐
    │  User   │     │  Course   │    │Enrollment│
    │ Service │     │  Service  │    │ Service │
    └────┬────┘     └─────┬─────┘    └────┬────┘
         │                │                │
         └────────────────┼────────────────┘
                          │
                    ┌─────▼─────┐
                    │  Payment  │
                    │  Service  │
                    └─────┬─────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
    ┌────▼────┐     ┌─────▼─────┐    ┌────▼────┐
    │PostgreSQL│    │  MongoDB  │    │  Redis  │
    └─────────┘     └───────────┘    └─────────┘
```

---

## Architecture Overview

### Architecture Style: Microservices

**Key Characteristics:**
1. **Service Independence:** Each service can be developed, deployed, and scaled independently
2. **Database per Service:** Each service owns its database (polyglot persistence)
3. **API-First:** All services expose well-defined REST APIs
4. **Async Communication:** Background tasks via Celery message queue
5. **Event-Driven:** Services react to events (enrollments, payments)

### Core Principles
- **Single Responsibility:** Each service handles one business domain
- **Loose Coupling:** Services interact via APIs, not direct database access
- **High Cohesion:** Related functionality grouped together
- **Failure Isolation:** Service failures don't cascade
- **Scalability:** Services scale independently based on load

---

## Microservices Architecture

### Service Inventory

| Service | Port | Database | Description |
|---------|------|----------|-------------|
| **User Service** | 8001 | PostgreSQL (`user_db`) | Authentication, user management, RBAC |
| **Course Service** | 8002 | PostgreSQL + MongoDB + Redis | Course CRUD, content management, caching |
| **Enrollment Service** | 8003 | PostgreSQL (`enrollment_db`) | Student enrollments, quota management |
| **Payment Service** | 8004 | PostgreSQL (`payment_db`) | Payment processing, transactions |

### Infrastructure Services

| Service | Port | Purpose |
|---------|------|---------|
| **PostgreSQL** | 5432 | Primary relational database |
| **MongoDB** | 27017 | Document storage (course content) |
| **Redis** | 6379 | Cache + Celery message broker |
| **RabbitMQ** | 5672 | Alternative message broker (optional) |
| **Prometheus** | 9090 | Metrics collection |
| **Grafana** | 3000 | Monitoring dashboards |

---

## Service Communication Patterns

### 1. Synchronous Communication (REST APIs)

**Use Cases:**
- Client-to-service requests
- Inter-service queries (user verification, course availability)
- Real-time operations requiring immediate response

**Protocol:** HTTP/HTTPS with JSON payloads

**Example Flow: Student Enrollment**
```
1. Student → POST /api/v1/enrollments/ (Enrollment Service)
2. Enrollment Service → GET /api/v1/users/{user_id} (User Service)
3. Enrollment Service → GET /api/v1/courses/{course_id}/availability (Course Service)
4. Enrollment Service → POST /api/v1/payments/ (Payment Service)
5. Payment Service → Webhook → Enrollment Service (confirm enrollment)
6. Enrollment Service → Response to Student
```

### 2. Asynchronous Communication (Celery + Redis)

**Use Cases:**
- Email notifications
- Long-running tasks
- Non-critical operations
- Event processing

**Message Broker:** Redis or RabbitMQ

**Example Tasks:**
- Send enrollment confirmation email
- Notify instructor of new enrollment
- Update course statistics
- Generate certificates

---

## Data Architecture

### Polyglot Persistence Strategy

```
┌─────────────────────────────────────────────────────────┐
│                     Data Layer                          │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ PostgreSQL   │  │  MongoDB     │  │   Redis      │  │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤  │
│  │ • user_db    │  │ • course     │  │ • Cache      │  │
│  │ • course_db  │  │   content    │  │ • Sessions   │  │
│  │ • enrollment │  │ • resources  │  │ • Queue      │  │
│  │ • payment_db │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
│  Transactional      Flexible           Fast              │
│  ACID Compliance    Document Store     In-Memory         │
└─────────────────────────────────────────────────────────┘
```

### Database Ownership

| Service | PostgreSQL Schema | MongoDB Collection | Redis Keys |
|---------|-------------------|-------------------|------------|
| User | `user_db.users`, `user_db.profiles` | - | `session:*`, `jwt:blacklist:*` |
| Course | `course_db.courses`, `course_db.categories` | `course_contents` | `course:*`, `courses:list:*` |
| Enrollment | `enrollment_db.enrollments` | - | - |
| Payment | `payment_db.payments`, `payment_db.audit_log` | - | - |

---

## Security Architecture

### Authentication Flow (JWT)

```
1. User → POST /api/v1/auth/login (email, password)
2. User Service validates credentials
3. User Service generates JWT (access_token + refresh_token)
4. User → Stores tokens
5. User → Request with Authorization: Bearer <access_token>
6. Service validates JWT signature and expiration
7. Service processes request
```

### Authorization (RBAC)

**Roles:**
- **ADMIN:** Full system access
- **INSTRUCTOR:** Create/manage courses, view enrollments
- **STUDENT:** Enroll in courses, access content

**Permission Model:**
```python
@require_role(["ADMIN", "INSTRUCTOR"])
def create_course():
    pass

@require_role(["STUDENT"])
def enroll_in_course():
    pass
```

### Security Layers
1. **Transport Security:** HTTPS/TLS
2. **Authentication:** JWT tokens
3. **Authorization:** Role-based access control
4. **Input Validation:** Pydantic schemas
5. **SQL Injection Prevention:** ORM (SQLAlchemy)
6. **Password Security:** bcrypt hashing
7. **Rate Limiting:** Redis-based (future)

---

## Scalability & Performance

### Horizontal Scaling

| Service | Scaling Strategy | Reason |
|---------|------------------|--------|
| User Service | 2-3 replicas | Moderate load, authentication-heavy |
| Course Service | 3-5 replicas | High read traffic, caching helps |
| Enrollment Service | 2-3 replicas | Moderate write traffic |
| Payment Service | 2-3 replicas | Critical, needs redundancy |

### Caching Strategy

**Cache Layers:**
1. **Application Cache (Redis):**
   - Course details (TTL: 10 min)
   - Course listings (TTL: 5 min)
   - User sessions (TTL: 24 hours)

2. **Database Query Cache:**
   - Frequent queries cached
   - Invalidate on write operations

### Load Balancing

**Development:** Docker Compose (no load balancing)

**Production (Kubernetes):**
- **Service LoadBalancer:** ClusterIP services
- **Ingress Controller:** nginx-ingress
- **Algorithm:** Round-robin with health checks

---

## Reliability & Fault Tolerance

### High Availability Design

1. **Service Redundancy:**
   - Multiple replicas per service
   - Health checks (liveness + readiness)

2. **Database Redundancy:**
   - PostgreSQL: Primary-Replica
   - MongoDB: Replica Set (3 nodes)
   - Redis: Sentinel or Cluster

3. **Circuit Breaker Pattern:**
   - Prevent cascade failures
   - Automatic retry with exponential backoff
   - Fallback strategies

### Error Handling

```python
# Example: Circuit breaker for inter-service calls
@circuit_breaker(failure_threshold=5, timeout=30)
async def get_user_from_service(user_id: str):
    try:
        response = await http_client.get(f"{USER_SERVICE_URL}/users/{user_id}")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch user {user_id}: {e}")
        # Fallback: return cached user or partial data
        return get_cached_user(user_id)
```

---

## Deployment Architecture

### Development Environment (Docker Compose)

```yaml
version: '3.8'
services:
  user-service:
    build: ./services/user-service
    ports: ["8001:8001"]
    depends_on: [postgres, redis]
  
  course-service:
    build: ./services/course-service
    ports: ["8002:8002"]
    depends_on: [postgres, mongodb, redis]
  
  enrollment-service:
    build: ./services/enrollment-service
    ports: ["8003:8003"]
    depends_on: [postgres, redis, celery-worker]
  
  payment-service:
    build: ./services/payment-service
    ports: ["8004:8004"]
    depends_on: [postgres]
  
  postgres:
    image: postgres:15
    ports: ["5432:5432"]
  
  mongodb:
    image: mongo:6
    ports: ["27017:27017"]
  
  redis:
    image: redis:7
    ports: ["6379:6379"]
  
  celery-worker:
    build: ./services/enrollment-service
    command: celery -A app.celery worker
```

### Production Environment (Kubernetes)

**Cluster Architecture:**
```
┌─────────────────────────────────────────────────┐
│              Kubernetes Cluster                  │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌──────────────────────────────────────────┐   │
│  │         Ingress Controller               │   │
│  │  (nginx-ingress with TLS termination)    │   │
│  └────────────────┬─────────────────────────┘   │
│                   │                              │
│  ┌────────────────┼─────────────────────────┐   │
│  │        Service Mesh (Optional: Istio)    │   │
│  └────────────────┼─────────────────────────┘   │
│                   │                              │
│  ┌────────────────┴─────────────────────────┐   │
│  │         ClusterIP Services               │   │
│  │  • user-service:8001                     │   │
│  │  • course-service:8002                   │   │
│  │  • enrollment-service:8003               │   │
│  │  • payment-service:8004                  │   │
│  └──────────────────────────────────────────┘   │
│                                                   │
│  ┌──────────────────────────────────────────┐   │
│  │         Service Deployments              │   │
│  │  Pods with auto-scaling (HPA)            │   │
│  └──────────────────────────────────────────┘   │
│                                                   │
│  ┌──────────────────────────────────────────┐   │
│  │         StatefulSets                     │   │
│  │  • PostgreSQL (Primary + Replicas)       │   │
│  │  • MongoDB (Replica Set)                 │   │
│  │  • Redis (Sentinel)                      │   │
│  └──────────────────────────────────────────┘   │
│                                                   │
│  ┌──────────────────────────────────────────┐   │
│  │    PersistentVolumes (Storage)           │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## Observability Stack

### Logging (Structured JSON Logs)
```json
{
  "timestamp": "2025-10-21T10:30:00Z",
  "service": "enrollment-service",
  "level": "INFO",
  "correlation_id": "abc-123-def",
  "user_id": "user-uuid",
  "action": "create_enrollment",
  "course_id": "course-uuid",
  "message": "Enrollment created successfully"
}
```

### Metrics (Prometheus)
- **Request Metrics:** Rate, latency, errors (RED method)
- **Business Metrics:** Enrollments/hour, revenue, active users
- **Infrastructure Metrics:** CPU, memory, disk, network

### Monitoring (Grafana Dashboards)
1. **Service Health Dashboard**
2. **Business Metrics Dashboard**
3. **Infrastructure Dashboard**
4. **SLO/SLA Dashboard**

### Tracing (Future: OpenTelemetry)
- Distributed request tracing
- Cross-service flow visualization

---

## CI/CD Pipeline

### Continuous Integration
```yaml
# .github/workflows/ci.yml
on: [push, pull_request]

jobs:
  test:
    - Lint (flake8, pylint)
    - Format check (black, isort)
    - Type check (mypy)
    - Security scan (bandit)
    - Unit tests
    - Integration tests
    - Coverage report (>80%)
  
  build:
    - Build Docker images
    - Tag with commit SHA
    - Push to registry
```

### Continuous Deployment
```yaml
# .github/workflows/cd.yml
on:
  push:
    branches: [main]

jobs:
  deploy:
    - Pull Docker images
    - Deploy to staging
    - Run smoke tests
    - Manual approval
    - Deploy to production
    - Health checks
```

---

## Non-Functional Requirements

### Performance
- **Response Time:** < 200ms (p95)
- **Throughput:** > 1000 requests/sec
- **Concurrent Users:** 100+

### Availability
- **Uptime:** 99.9% (8.76 hours downtime/year)
- **Recovery Time:** < 5 minutes

### Scalability
- **Horizontal Scaling:** Add replicas on demand
- **Database Scaling:** Read replicas, sharding (future)

### Security
- **Authentication:** JWT with 15-min expiry
- **Authorization:** Role-based access control
- **Encryption:** TLS 1.3 for transit, AES-256 for rest

---

## Technology Stack Summary

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.11+, FastAPI |
| **Databases** | PostgreSQL 15, MongoDB 6, Redis 7 |
| **Message Queue** | Celery + Redis/RabbitMQ |
| **Containers** | Docker, Docker Compose |
| **Orchestration** | Kubernetes |
| **CI/CD** | GitHub Actions |
| **Monitoring** | Prometheus, Grafana, Loguru |
| **Testing** | Pytest, Locust |

---

## Migration Strategy (Monolith to Microservices)

### Phase 1: Strangler Fig Pattern
1. Build new microservices alongside monolith
2. Route new requests to microservices
3. Migrate data incrementally

### Phase 2: Service Extraction
1. Extract User Service (authentication critical)
2. Extract Course Service (read-heavy, independent)
3. Extract Payment Service (compliance, security)
4. Extract Enrollment Service (orchestration)

### Phase 3: Monolith Decomissioning
1. Migrate remaining functionality
2. Shut down monolith
3. Cleanup and optimization

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Service Failure** | High | Redundancy, circuit breakers, health checks |
| **Data Inconsistency** | Medium | Eventual consistency, saga pattern, compensation |
| **Network Latency** | Medium | Caching, async processing, service co-location |
| **Complexity** | High | Documentation, monitoring, standardization |
| **Security Breach** | Critical | JWT, RBAC, encryption, security audits |

---

## Future Enhancements

1. **API Gateway:** Centralized routing, auth, rate limiting
2. **Service Mesh (Istio):** Advanced traffic management, security
3. **Event Sourcing:** Audit trail, state reconstruction
4. **CQRS:** Separate read/write models for performance
5. **Machine Learning:** Course recommendations, personalization
6. **Real-time Features:** WebSocket notifications, chat
7. **Multi-tenancy:** Support multiple organizations

---

**Document Version:** 1.0  
**Last Updated:** October 21, 2025  
**Authors:** Francis Akol  
**Status:** Implementation Ready
