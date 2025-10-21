# Service Boundaries & Domain Design

## Overview
This document defines the microservices architecture, service boundaries, responsibilities, and communication patterns for the Modular Learning Hub (MLH) platform.

## Microservices Architecture Pattern

### Design Principles
1. **Single Responsibility:** Each service owns a specific business domain
2. **Data Ownership:** Each service manages its own database
3. **Loose Coupling:** Services interact via well-defined APIs
4. **High Cohesion:** Related functionality grouped together
5. **Independent Deployment:** Services can be deployed independently
6. **Failure Isolation:** One service failure doesn't cascade

---

## Service Decomposition

### 1. User Service
**Domain:** User Management & Authentication

**Responsibilities:**
- User registration and profile management
- Authentication (JWT token generation/validation)
- Authorization (role-based access control)
- User session management
- Password management (reset, change)
- User role management (Admin, Instructor, Student)

**Data Ownership:**
- `users` table (id, email, username, hashed_password, role, created_at, updated_at)
- `profiles` table (user_id, first_name, last_name, bio, avatar_url)
- `sessions` (in Redis)

**Exposed APIs:**
- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - Authenticate user
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `POST /api/v1/auth/logout` - Invalidate session
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update profile
- `GET /api/v1/users/{user_id}` - Get user by ID (internal/admin)
- `GET /api/v1/users/` - List users (admin)

**Dependencies:**
- None (foundational service)

**Port:** 8001

---

### 2. Course Service
**Domain:** Course Management & Content

**Responsibilities:**
- Course CRUD operations
- Course content management
- Course categorization
- Course search and filtering
- Course availability management
- Instructor-course relationship management
- Course analytics and statistics

**Data Ownership:**
- `courses` table (id, title, description, instructor_id, price, max_students, created_at, updated_at)
- `course_content` collection (MongoDB - course_id, title, content_type, content_url, order, metadata)
- `categories` table (id, name, description)
- `course_categories` table (course_id, category_id)
- Course cache (Redis)

**Exposed APIs:**
- `POST /api/v1/courses/` - Create course (instructor)
- `GET /api/v1/courses/` - List courses (paginated, filtered)
- `GET /api/v1/courses/{course_id}` - Get course details (cached)
- `PUT /api/v1/courses/{course_id}` - Update course
- `DELETE /api/v1/courses/{course_id}` - Delete course
- `POST /api/v1/courses/{course_id}/content` - Add content
- `GET /api/v1/courses/{course_id}/content` - List content
- `GET /api/v1/courses/{course_id}/availability` - Check availability
- `GET /api/v1/categories/` - List categories

**Dependencies:**
- User Service (verify instructor)

**Port:** 8002

---

### 3. Enrollment Service
**Domain:** Student-Course Enrollment Management

**Responsibilities:**
- Enrollment creation and management
- Enrollment status tracking
- Course quota enforcement
- Enrollment confirmation workflow
- Progress tracking
- Certificate generation (future)
- Enrollment analytics

**Data Ownership:**
- `enrollments` table (id, user_id, course_id, status, enrolled_at, completed_at)
- `enrollment_status` enum (PENDING, ACTIVE, COMPLETED, CANCELLED)

**Exposed APIs:**
- `POST /api/v1/enrollments/` - Enroll in course
- `GET /api/v1/enrollments/` - List user enrollments
- `GET /api/v1/enrollments/{enrollment_id}` - Get enrollment details
- `PUT /api/v1/enrollments/{enrollment_id}` - Update enrollment status
- `DELETE /api/v1/enrollments/{enrollment_id}` - Cancel enrollment
- `GET /api/v1/courses/{course_id}/enrollments` - List course enrollments (instructor)
- `GET /api/v1/enrollments/{enrollment_id}/progress` - Get progress

**Dependencies:**
- User Service (verify user exists)
- Course Service (verify course exists, check quota)
- Payment Service (verify payment status)

**Async Tasks:**
- Send enrollment confirmation email
- Notify instructor of new enrollment
- Update course statistics

**Port:** 8003

---

### 4. Payment Service
**Domain:** Payment Processing & Transaction Management

**Responsibilities:**
- Payment intent creation
- Payment processing (mock gateway)
- Payment validation
- Transaction recording
- Refund processing
- Payment status management
- Payment analytics and reporting
- Idempotency handling

**Data Ownership:**
- `payments` table (id, user_id, course_id, amount, currency, status, payment_method, transaction_id, created_at)
- `payment_status` enum (PENDING, COMPLETED, FAILED, REFUNDED)
- `payment_audit_log` table (payment_id, action, timestamp, details)

**Exposed APIs:**
- `POST /api/v1/payments/` - Create payment intent
- `POST /api/v1/payments/{payment_id}/confirm` - Confirm payment
- `GET /api/v1/payments/` - List user payments
- `GET /api/v1/payments/{payment_id}` - Get payment details
- `POST /api/v1/payments/{payment_id}/refund` - Process refund (admin)
- `POST /api/v1/payments/webhook` - Payment gateway webhook
- `GET /api/v1/payments/analytics` - Payment analytics (admin)

**Dependencies:**
- User Service (verify user)
- Course Service (get course price)
- Enrollment Service (notify on payment success)

**Port:** 8004

---

## Communication Patterns

### Synchronous Communication (REST APIs)

#### 1. Enrollment Flow
```
Client → Enrollment Service
  ↓
Enrollment Service → User Service (verify user)
  ↓
Enrollment Service → Course Service (check availability)
  ↓
Enrollment Service → Payment Service (verify payment)
  ↓
Enrollment Service → Client (enrollment confirmation)
```

#### 2. Payment Verification
```
Payment Service → Course Service (get course details)
  ↓
Payment Service → User Service (verify user)
  ↓
Payment Service → Enrollment Service (notify success)
```

### Asynchronous Communication (Celery + Redis)

#### Background Tasks
- **Enrollment Confirmation Email** (Enrollment Service)
  - Triggered: After successful enrollment
  - Queue: `enrollment_queue`
  - Priority: High
  - Retry: 3 attempts

- **Instructor Notification** (Enrollment Service)
  - Triggered: New student enrollment
  - Queue: `notification_queue`
  - Priority: Medium
  - Retry: 3 attempts

- **Course Statistics Update** (Enrollment Service)
  - Triggered: Enrollment status change
  - Queue: `analytics_queue`
  - Priority: Low
  - Retry: 5 attempts

---

## API Gateway Pattern

### Optional: API Gateway (Future)
- Single entry point for clients
- Request routing to microservices
- Authentication middleware
- Rate limiting
- Request/response transformation
- Caching
- Load balancing

**For Phase 1:** Direct service communication without gateway

---

## Data Consistency Patterns

### 1. Strong Consistency
- Within a single service (ACID transactions)
- Example: Payment creation and audit log

### 2. Eventual Consistency
- Across services (async messaging)
- Example: Enrollment → Email notification

### 3. Saga Pattern (Future)
- Distributed transactions
- Example: Payment failure → Enrollment rollback

---

## Service Discovery

### Development Environment
- **Static Configuration:** Services accessed via `localhost:PORT`
- **Docker Compose:** DNS-based discovery (service names)

### Production (Kubernetes)
- **Service Names:** `user-service`, `course-service`, etc.
- **ClusterIP Services:** Internal load balancing
- **Environment Variables:** Service endpoints configuration

---

## Inter-Service Authentication

### Option 1: Service-to-Service JWT
- Each service has a service account
- JWT tokens for internal communication
- Token validation at each service

### Option 2: API Keys (Simpler)
- Shared secret between services
- Header: `X-API-Key: <secret>`
- Validate in middleware

**Implementation:** Option 2 for Phase 1, Option 1 for production

---

## Error Handling & Circuit Breaker

### Circuit Breaker Pattern
- Prevent cascade failures
- Automatic failover
- Health checks before requests

### Retry Logic
- Exponential backoff
- Maximum retry attempts (3-5)
- Timeout configuration

### Fallback Strategies
- Return cached data (Course Service)
- Return partial data
- Graceful degradation

---

## Service Boundaries Decision Rationale

### Why Separate User & Enrollment Services?
- **User Service:** Identity and access management (stable, security-critical)
- **Enrollment Service:** Business logic (enrollment rules, quota management)
- Different scaling requirements
- Different security requirements

### Why Separate Payment Service?
- PCI compliance requirements (future)
- Different availability requirements (99.99% uptime)
- Payment gateway integration isolation
- Audit and compliance separation

### Why Separate Course Service?
- Read-heavy workload (can scale independently)
- Caching strategy differs from other services
- Content management complexity
- Potential for MongoDB integration

---

## Service Sizing Recommendations

### Development
- All services: 1 container each
- Total: 4 service containers + 3 database containers

### Production (Initial)
| Service | Replicas | CPU | Memory |
|---------|----------|-----|--------|
| User Service | 2 | 0.5 | 512Mi |
| Course Service | 3 | 1.0 | 1Gi |
| Enrollment Service | 2 | 0.5 | 512Mi |
| Payment Service | 2 | 0.5 | 512Mi |

**Auto-scaling:** Course Service (most read-heavy)

---

## Future Service Candidates

### Notification Service
- Email, SMS, push notifications
- Centralized notification management
- Currently: Handled by Celery tasks in each service

### Analytics Service
- Business intelligence
- Reporting and dashboards
- Currently: Basic analytics in each service

### File Storage Service
- Course material uploads
- User avatar management
- Currently: Stretch goal with MinIO

---

**Last Updated:** October 21, 2025  
**Authors:** Francis Akol  
**Document Version:** 1.0
