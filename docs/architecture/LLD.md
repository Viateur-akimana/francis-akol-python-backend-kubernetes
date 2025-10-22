# Low-Level Design (LLD) - Modular Learning Hub

## Overview
This document provides detailed design specifications, sequence diagrams, class structures, and implementation details for each microservice in the Modular Learning Hub platform.

---

## Table of Contents
1. [Key Workflows & Sequence Diagrams](#key-workflows--sequence-diagrams)
2. [Service-Level Design](#service-level-design)
3. [API Contracts](#api-contracts)
4. [Data Models & Schemas](#data-models--schemas)
5. [Error Handling](#error-handling)
6. [Security Implementation](#security-implementation)

---

## Key Workflows & Sequence Diagrams

### 1. User Registration & JWT Issuance

```
┌────────┐         ┌──────────────┐         ┌──────────┐         ┌───────┐
│ Client │         │ User Service │         │PostgreSQL│         │ Redis │
└───┬────┘         └──────┬───────┘         └────┬─────┘         └───┬───┘
    │                     │                      │                   │
    │ POST /auth/signup   │                      │                   │
    │ {email, password}   │                      │                   │
    ├────────────────────>│                      │                   │
    │                     │                      │                   │
    │                     │ Validate input       │                   │
    │                     │ (Pydantic schema)    │                   │
    │                     │                      │                   │
    │                     │ Check email exists   │                   │
    │                     ├─────────────────────>│                   │
    │                     │ SELECT * FROM users  │                   │
    │                     │ WHERE email = ?      │                   │
    │                     │<─────────────────────┤                   │
    │                     │ (email not found)    │                   │
    │                     │                      │                   │
    │                     │ Hash password        │                   │
    │                     │ (bcrypt)             │                   │
    │                     │                      │                   │
    │                     │ INSERT INTO users    │                   │
    │                     ├─────────────────────>│                   │
    │                     │<─────────────────────┤                   │
    │                     │ (user created)       │                   │
    │                     │                      │                   │
    │                     │ Generate JWT tokens  │                   │
    │                     │ (access + refresh)   │                   │
    │                     │                      │                   │
    │                     │ Store refresh token  │                   │
    │                     ├──────────────────────────────────────────>│
    │                     │ SET refresh:{token_id} = user_id [TTL]   │
    │                     │<──────────────────────────────────────────┤
    │                     │                      │                   │
    │<────────────────────┤                      │                   │
    │ 201 Created         │                      │                   │
    │ {access_token,      │                      │                   │
    │  refresh_token,     │                      │                   │
    │  user: {...}}       │                      │                   │
    │                     │                      │                   │
```

### 2. User Login Flow

```
┌────────┐         ┌──────────────┐         ┌──────────┐         ┌───────┐
│ Client │         │ User Service │         │PostgreSQL│         │ Redis │
└───┬────┘         └──────┬───────┘         └────┬─────┘         └───┬───┘
    │                     │                      │                   │
    │ POST /auth/login    │                      │                   │
    │ {email, password}   │                      │                   │
    ├────────────────────>│                      │                   │
    │                     │                      │                   │
    │                     │ Find user by email   │                   │
    │                     ├─────────────────────>│                   │
    │                     │<─────────────────────┤                   │
    │                     │ (user found)         │                   │
    │                     │                      │                   │
    │                     │ Verify password      │                   │
    │                     │ (bcrypt.verify)      │                   │
    │                     │                      │                   │
    │                     │ Update last_login    │                   │
    │                     ├─────────────────────>│                   │
    │                     │<─────────────────────┤                   │
    │                     │                      │                   │
    │                     │ Generate JWT tokens  │                   │
    │                     │                      │                   │
    │                     │ Cache user session   │                   │
    │                     ├──────────────────────────────────────────>│
    │                     │ SET session:{user_id} = {...} [TTL: 24h] │
    │                     │<──────────────────────────────────────────┤
    │                     │                      │                   │
    │<────────────────────┤                      │                   │
    │ 200 OK              │                      │                   │
    │ {access_token,      │                      │                   │
    │  refresh_token}     │                      │                   │
    │                     │                      │                   │
```

### 3. Course Creation by Instructor

```
┌────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐    ┌───────┐
│Instructor│   │Course Service│    │ User Service │    │PostgreSQL│    │ Redis │
└───┬────┘    └──────┬───────┘    └──────┬───────┘    └────┬─────┘    └───┬───┘
    │                │                    │                 │              │
    │ POST /courses/ │                    │                 │              │
    │ Authorization: │                    │                 │              │
    │ Bearer <token> │                    │                 │              │
    ├───────────────>│                    │                 │              │
    │                │                    │                 │              │
    │                │ Verify JWT token   │                 │              │
    │                │ Extract user_id    │                 │              │
    │                │                    │                 │              │
    │                │ Verify user role   │                 │              │
    │                ├───────────────────>│                 │              │
    │                │ GET /users/{id}    │                 │              │
    │                │<───────────────────┤                 │              │
    │                │ {role: INSTRUCTOR} │                 │              │
    │                │                    │                 │              │
    │                │ Validate course data                 │              │
    │                │ (Pydantic schema)  │                 │              │
    │                │                    │                 │              │
    │                │ INSERT INTO courses│                 │              │
    │                ├────────────────────────────────────>│              │
    │                │<────────────────────────────────────┤              │
    │                │ (course created)   │                 │              │
    │                │                    │                 │              │
    │                │ Invalidate course list cache         │              │
    │                ├─────────────────────────────────────────────────────>│
    │                │ DEL courses:list:* │                 │              │
    │                │<─────────────────────────────────────────────────────┤
    │                │                    │                 │              │
    │<───────────────┤                    │                 │              │
    │ 201 Created    │                    │                 │              │
    │ {course: {...}}│                    │                 │              │
    │                │                    │                 │              │
```

### 4. Student Enrollment with Quota Check

```
┌────────┐  ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐
│Student │  │Enrollment Service│  │Course Service│  │Payment Service│ │PostgreSQL│
└───┬────┘  └─────────┬────────┘  └──────┬───────┘  └──────┬───────┘  └────┬─────┘
    │                 │                   │                 │               │
    │ POST /enrollments/                  │                 │               │
    │ {course_id}     │                   │                 │               │
    ├────────────────>│                   │                 │               │
    │                 │                   │                 │               │
    │                 │ Check existing enrollment           │               │
    │                 ├──────────────────────────────────────────────────>│
    │                 │ SELECT * FROM enrollments                          │
    │                 │ WHERE user_id=? AND course_id=?                    │
    │                 │<──────────────────────────────────────────────────┤
    │                 │ (not enrolled)    │                 │               │
    │                 │                   │                 │               │
    │                 │ Check course availability           │               │
    │                 ├──────────────────>│                 │               │
    │                 │ GET /courses/{id}/availability      │               │
    │                 │<──────────────────┤                 │               │
    │                 │ {available: true, │                 │               │
    │                 │  slots: 5}        │                 │               │
    │                 │                   │                 │               │
    │                 │ Check payment status                │               │
    │                 ├────────────────────────────────────>│               │
    │                 │ GET /payments?user_id=?&course_id=? │               │
    │                 │<────────────────────────────────────┤               │
    │                 │ {status: COMPLETED}                 │               │
    │                 │                   │                 │               │
    │                 │ BEGIN TRANSACTION │                 │               │
    │                 ├──────────────────────────────────────────────────>│
    │                 │                   │                 │               │
    │                 │ INSERT INTO enrollments             │               │
    │                 ├──────────────────────────────────────────────────>│
    │                 │<──────────────────────────────────────────────────┤
    │                 │                   │                 │               │
    │                 │ UPDATE courses    │                 │               │
    │                 │ SET current_enrollment++            │               │
    │                 ├──────────────────>│                 │               │
    │                 │<──────────────────┤                 │               │
    │                 │                   │                 │               │
    │                 │ COMMIT TRANSACTION│                 │               │
    │                 ├──────────────────────────────────────────────────>│
    │                 │<──────────────────────────────────────────────────┤
    │                 │                   │                 │               │
    │                 │ Queue: Send confirmation email (Celery)            │
    │                 │                   │                 │               │
    │<────────────────┤                   │                 │               │
    │ 201 Created     │                   │                 │               │
    │ {enrollment:{...}}                  │                 │               │
    │                 │                   │                 │               │
```

### 5. Payment Processing with Enrollment Confirmation

```
┌────────┐  ┌──────────────┐  ┌──────────────────┐  ┌──────────┐  ┌───────────┐
│Student │  │Payment Service│ │Enrollment Service│  │PostgreSQL│  │  Gateway  │
└───┬────┘  └──────┬───────┘  └─────────┬────────┘  └────┬─────┘  └─────┬─────┘
    │              │                     │                │              │
    │ POST /payments/                    │                │              │
    │ {course_id,  │                     │                │              │
    │  amount}     │                     │                │              │
    ├─────────────>│                     │                │              │
    │              │                     │                │              │
    │              │ Validate amount     │                │              │
    │              │ Generate idempotency_key             │              │
    │              │                     │                │              │
    │              │ INSERT INTO payments│                │              │
    │              │ (status: PENDING)   │                │              │
    │              ├────────────────────────────────────>│              │
    │              │<────────────────────────────────────┤              │
    │              │                     │                │              │
    │              │ Call payment gateway                 │              │
    │              ├─────────────────────────────────────────────────────>│
    │              │ {amount, currency, idempotency_key}               │
    │              │<─────────────────────────────────────────────────────┤
    │              │ {transaction_id, status: SUCCESS}    │              │
    │              │                     │                │              │
    │              │ UPDATE payments     │                │              │
    │              │ SET status=COMPLETED│                │              │
    │              │ SET transaction_id  │                │              │
    │              ├────────────────────────────────────>│              │
    │              │<────────────────────────────────────┤              │
    │              │                     │                │              │
    │              │ Notify Enrollment Service            │              │
    │              ├────────────────────>│                │              │
    │              │ POST /webhooks/payment-confirmed     │              │
    │              │ {payment_id, user_id, course_id}     │              │
    │              │<────────────────────┤                │              │
    │              │ 200 OK              │                │              │
    │              │                     │                │              │
    │              │                     │ Update enrollment│             │
    │              │                     │ status: ACTIVE │              │
    │              │                     ├───────────────>│              │
    │              │                     │<───────────────┤              │
    │              │                     │                │              │
    │<─────────────┤                     │                │              │
    │ 200 OK       │                     │                │              │
    │ {payment:{...}}                    │                │              │
    │              │                     │                │              │
```

---

## Service-Level Design

### 1. User Service Architecture

#### Component Structure
```
user-service/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── auth.py     # Authentication endpoints
│   │           └── users.py    # User management endpoints
│   ├── core/
│   │   ├── config.py           # Settings & configuration
│   │   ├── security.py         # JWT, password hashing
│   │   └── dependencies.py     # Dependency injection
│   ├── models/
│   │   ├── user.py             # SQLAlchemy models
│   │   └── profile.py
│   ├── schemas/
│   │   ├── user.py             # Pydantic schemas
│   │   ├── auth.py
│   │   └── token.py
│   ├── services/
│   │   ├── auth_service.py     # Business logic
│   │   └── user_service.py
│   ├── repositories/
│   │   └── user_repository.py  # Database operations
│   └── db/
│       ├── session.py          # Database session
│       └── base.py             # Base models
├── tests/
├── alembic/                    # Database migrations
├── requirements.txt
└── Dockerfile
```

#### Key Classes

**User Model (SQLAlchemy)**
```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    role: Mapped[str] = mapped_column(default="STUDENT")
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    profile: Mapped["Profile"] = relationship(back_populates="user")
```

**User Schema (Pydantic)**
```python
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    role: Literal["STUDENT", "INSTRUCTOR"] = "STUDENT"

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    role: str
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

**Authentication Service**
```python
class AuthService:
    def __init__(self, user_repo: UserRepository, redis: Redis):
        self.user_repo = user_repo
        self.redis = redis
    
    async def register(self, user_data: UserCreate) -> TokenResponse:
        # Check if user exists
        # Hash password
        # Create user
        # Generate JWT tokens
        # Store refresh token in Redis
        # Return tokens
        pass
    
    async def login(self, credentials: LoginRequest) -> TokenResponse:
        # Verify credentials
        # Generate JWT tokens
        # Cache session in Redis
        # Return tokens
        pass
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        # Validate refresh token
        # Check Redis for validity
        # Generate new access token
        # Return new tokens
        pass
```

---

### 2. Course Service Architecture

#### Component Structure
```
course-service/
├── app/
│   ├── main.py
│   ├── api/v1/endpoints/
│   │   ├── courses.py
│   │   ├── content.py
│   │   └── categories.py
│   ├── core/
│   │   ├── config.py
│   │   ├── cache.py            # Redis caching logic
│   │   └── dependencies.py
│   ├── models/
│   │   ├── course.py           # PostgreSQL models
│   │   └── category.py
│   ├── schemas/
│   │   ├── course.py
│   │   ├── content.py
│   │   └── category.py
│   ├── services/
│   │   ├── course_service.py
│   │   ├── content_service.py  # MongoDB operations
│   │   └── cache_service.py
│   ├── repositories/
│   │   ├── course_repository.py
│   │   └── content_repository.py
│   └── db/
│       ├── postgres.py
│       └── mongodb.py
```

#### Cache Service
```python
class CacheService:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.ttl = 600  # 10 minutes
    
    async def get_course(self, course_id: UUID) -> Optional[dict]:
        key = f"course:{course_id}"
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    async def set_course(self, course_id: UUID, course_data: dict):
        key = f"course:{course_id}"
        await self.redis.setex(key, self.ttl, json.dumps(course_data))
    
    async def invalidate_course(self, course_id: UUID):
        key = f"course:{course_id}"
        await self.redis.delete(key)
        # Also invalidate course list caches
        await self.redis.delete("courses:list:*")
```

---

### 3. Enrollment Service Architecture

#### Celery Tasks
```python
# app/tasks/enrollment_tasks.py

@celery_app.task(bind=True, max_retries=3)
def send_enrollment_confirmation_email(self, enrollment_id: str):
    try:
        enrollment = get_enrollment(enrollment_id)
        user = get_user_from_service(enrollment.user_id)
        course = get_course_from_service(enrollment.course_id)
        
        send_email(
            to=user.email,
            subject=f"Enrollment Confirmed: {course.title}",
            template="enrollment_confirmation.html",
            context={"user": user, "course": course}
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)  # Retry after 1 min

@celery_app.task(bind=True, max_retries=3)
def notify_instructor(self, enrollment_id: str):
    try:
        enrollment = get_enrollment(enrollment_id)
        course = get_course_from_service(enrollment.course_id)
        instructor = get_user_from_service(course.instructor_id)
        student = get_user_from_service(enrollment.user_id)
        
        send_email(
            to=instructor.email,
            subject=f"New Enrollment: {course.title}",
            template="instructor_notification.html",
            context={"instructor": instructor, "student": student, "course": course}
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```

---

### 4. Payment Service Architecture

#### State Machine
```python
class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class PaymentStateMachine:
    transitions = {
        PaymentStatus.PENDING: [PaymentStatus.PROCESSING, PaymentStatus.FAILED],
        PaymentStatus.PROCESSING: [PaymentStatus.COMPLETED, PaymentStatus.FAILED],
        PaymentStatus.COMPLETED: [PaymentStatus.REFUNDED],
        PaymentStatus.FAILED: [PaymentStatus.PENDING],  # Retry
        PaymentStatus.REFUNDED: []  # Terminal state
    }
    
    @staticmethod
    def can_transition(current: PaymentStatus, target: PaymentStatus) -> bool:
        return target in PaymentStateMachine.transitions.get(current, [])
    
    @staticmethod
    def transition(payment: Payment, new_status: PaymentStatus):
        if not PaymentStateMachine.can_transition(payment.status, new_status):
            raise InvalidTransitionError(f"Cannot transition from {payment.status} to {new_status}")
        
        old_status = payment.status
        payment.status = new_status
        payment.updated_at = datetime.utcnow()
        
        # Log transition
        audit_log = PaymentAuditLog(
            payment_id=payment.id,
            action=f"STATUS_CHANGE",
            previous_status=old_status,
            new_status=new_status
        )
        db.add(audit_log)
```

---

## API Contracts

### User Service API

```yaml
# POST /api/v1/auth/signup
Request:
  {
    "email": "student@example.com",
    "username": "student123",
    "password": "SecurePass123!",
    "role": "STUDENT"
  }

Response: 201 Created
  {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
      "id": "uuid",
      "email": "student@example.com",
      "username": "student123",
      "role": "STUDENT"
    }
  }

Errors:
  - 400: Email already exists
  - 422: Validation error (weak password, invalid email)
```

```yaml
# POST /api/v1/auth/login
Request:
  {
    "email": "student@example.com",
    "password": "SecurePass123!"
  }

Response: 200 OK
  {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 900
  }

Errors:
  - 401: Invalid credentials
  - 403: Account disabled
```

### Course Service API

```yaml
# GET /api/v1/courses/
Query Parameters:
  - status: PUBLISHED | DRAFT | ARCHIVED
  - category_id: UUID
  - instructor_id: UUID
  - min_price: decimal
  - max_price: decimal
  - search: string (full-text search)
  - page: int (default: 1)
  - page_size: int (default: 20, max: 100)
  - sort_by: created_at | price | title
  - sort_order: asc | desc

Response: 200 OK
  {
    "items": [...],
    "total": 150,
    "page": 1,
    "page_size": 20,
    "pages": 8
  }
```

### Enrollment Service API

```yaml
# POST /api/v1/enrollments/
Request:
  {
    "course_id": "uuid"
  }

Response: 201 Created
  {
    "id": "uuid",
    "user_id": "uuid",
    "course_id": "uuid",
    "status": "ACTIVE",
    "enrolled_at": "2025-10-21T10:30:00Z",
    "progress_percentage": 0.0
  }

Errors:
  - 400: Already enrolled
  - 400: Course full (quota exceeded)
  - 402: Payment required
  - 404: Course not found
```

### Payment Service API

```yaml
# POST /api/v1/payments/
Request:
  {
    "course_id": "uuid",
    "amount": 99.99,
    "currency": "USD",
    "payment_method": "credit_card",
    "idempotency_key": "unique-key-123"
  }

Response: 201 Created
  {
    "id": "uuid",
    "user_id": "uuid",
    "course_id": "uuid",
    "amount": 99.99,
    "currency": "USD",
    "status": "PENDING",
    "transaction_id": null,
    "created_at": "2025-10-21T10:30:00Z"
  }

Errors:
  - 400: Invalid amount
  - 409: Duplicate payment (idempotency key already used)
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "error": {
    "code": "ENROLLMENT_QUOTA_EXCEEDED",
    "message": "This course has reached its maximum enrollment capacity",
    "details": {
      "course_id": "uuid",
      "max_students": 100,
      "current_enrollment": 100
    },
    "timestamp": "2025-10-21T10:30:00Z",
    "path": "/api/v1/enrollments/",
    "request_id": "correlation-id-123"
  }
}
```

### HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Successful GET/PUT |
| 201 | Successful POST (resource created) |
| 204 | Successful DELETE |
| 400 | Bad request (validation error) |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not found |
| 409 | Conflict (duplicate, race condition) |
| 422 | Unprocessable entity (semantic error) |
| 429 | Too many requests (rate limit) |
| 500 | Internal server error |
| 503 | Service unavailable |

---

## Security Implementation

### JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user-uuid",
    "email": "user@example.com",
    "role": "STUDENT",
    "iat": 1697894400,
    "exp": 1697895300,
    "jti": "token-unique-id"
  },
  "signature": "..."
}
```

### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### Authorization Decorator

```python
from functools import wraps
from fastapi import HTTPException, Depends

def require_role(allowed_roles: List[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Requires one of roles: {', '.join(allowed_roles)}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Usage
@router.post("/courses/")
@require_role(["INSTRUCTOR", "ADMIN"])
async def create_course(course_data: CourseCreate, current_user: User):
    pass
```

---

**Document Version:** 1.0  
**Last Updated:** October 21, 2025  
**Authors:** Francis Akol  
**Status:** Implementation Ready
