# Database Design & Schema Architecture

## Overview
This document outlines the database architecture, schemas, relationships, indexing strategies, and optimization techniques for the Modular Learning Hub platform.

## Database Strategy: Polyglot Persistence

### Database per Service Pattern
Each microservice owns its database schema, ensuring:
- Data encapsulation
- Independent scaling
- Technology diversity
- Failure isolation

### Database Technologies

| Service | Database | Rationale |
|---------|----------|-----------|
| User Service | PostgreSQL | ACID transactions for authentication |
| Course Service | PostgreSQL + MongoDB | Relational metadata + flexible content |
| Enrollment Service | PostgreSQL | Strong consistency for enrollments |
| Payment Service | PostgreSQL | ACID compliance for financial data |
| Cache Layer | Redis | High-speed caching |

---

## 1. User Service Database (`user_db`)

### Tables

#### `users`
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('ADMIN', 'INSTRUCTOR', 'STUDENT')),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

#### `profiles`
```sql
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    bio TEXT,
    avatar_url VARCHAR(500),
    phone VARCHAR(20),
    country VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_profiles_user_id ON profiles(user_id);
```

#### `refresh_tokens` (Optional)
```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE
);

-- Indexes
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
```

### Redis Storage (User Service)
```
# Session data
session:{user_id} → {session_data} [TTL: 24h]

# JWT blacklist (for logout)
jwt:blacklist:{jti} → 1 [TTL: token expiry]
```

---

## 2. Course Service Database (`course_db`)

### PostgreSQL Tables

#### `categories`
```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    slug VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_categories_slug ON categories(slug);
```

#### `courses`
```sql
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    instructor_id UUID NOT NULL,  -- Foreign key to User Service (logical)
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'USD',
    max_students INTEGER NOT NULL DEFAULT 100,
    current_enrollment INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'PUBLISHED', 'ARCHIVED')),
    thumbnail_url VARCHAR(500),
    level VARCHAR(20) CHECK (level IN ('BEGINNER', 'INTERMEDIATE', 'ADVANCED')),
    duration_hours INTEGER,
    language VARCHAR(50) DEFAULT 'English',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_courses_instructor_id ON courses(instructor_id);
CREATE INDEX idx_courses_category_id ON courses(category_id);
CREATE INDEX idx_courses_status ON courses(status);
CREATE INDEX idx_courses_created_at ON courses(created_at DESC);
CREATE INDEX idx_courses_price ON courses(price);

-- Full-text search index
CREATE INDEX idx_courses_title_description ON courses 
    USING GIN (to_tsvector('english', title || ' ' || description));
```

#### `course_tags` (Optional)
```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE course_tags (
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (course_id, tag_id)
);

-- Indexes
CREATE INDEX idx_course_tags_course_id ON course_tags(course_id);
CREATE INDEX idx_course_tags_tag_id ON course_tags(tag_id);
```

### MongoDB Collections (Course Content)

#### `course_contents`
```javascript
{
    "_id": ObjectId(),
    "course_id": UUID,  // Reference to PostgreSQL courses.id
    "modules": [
        {
            "module_id": UUID,
            "title": String,
            "description": String,
            "order": Integer,
            "lessons": [
                {
                    "lesson_id": UUID,
                    "title": String,
                    "content_type": String,  // "video", "text", "quiz", "assignment"
                    "content_url": String,
                    "duration_minutes": Integer,
                    "order": Integer,
                    "is_preview": Boolean,
                    "metadata": Object
                }
            ]
        }
    ],
    "resources": [
        {
            "resource_id": UUID,
            "title": String,
            "type": String,  // "pdf", "video", "link"
            "url": String
        }
    ],
    "created_at": ISODate,
    "updated_at": ISODate
}

// Indexes
db.course_contents.createIndex({ "course_id": 1 }, { unique: true })
db.course_contents.createIndex({ "modules.lessons.content_type": 1 })
```

### Redis Cache (Course Service)
```
# Course details cache
course:{course_id} → {course_json} [TTL: 10 minutes]

# Course list cache
courses:list:{filters_hash} → {courses_json} [TTL: 5 minutes]

# Course availability
course:availability:{course_id} → {available_slots} [TTL: 1 minute]
```

---

## 3. Enrollment Service Database (`enrollment_db`)

### Tables

#### `enrollments`
```sql
CREATE TABLE enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,  -- Foreign key to User Service (logical)
    course_id UUID NOT NULL,  -- Foreign key to Course Service (logical)
    payment_id UUID,  -- Foreign key to Payment Service (logical)
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' 
        CHECK (status IN ('PENDING', 'ACTIVE', 'COMPLETED', 'CANCELLED', 'REFUNDED')),
    enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    progress_percentage DECIMAL(5, 2) DEFAULT 0.00,
    last_accessed TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT unique_user_course UNIQUE (user_id, course_id)
);

-- Indexes
CREATE INDEX idx_enrollments_user_id ON enrollments(user_id);
CREATE INDEX idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX idx_enrollments_status ON enrollments(status);
CREATE INDEX idx_enrollments_enrolled_at ON enrollments(enrolled_at DESC);
CREATE INDEX idx_enrollments_user_course ON enrollments(user_id, course_id);
```

#### `enrollment_progress` (Optional - for future use)
```sql
CREATE TABLE enrollment_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enrollment_id UUID NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
    lesson_id UUID NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    time_spent_seconds INTEGER DEFAULT 0,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_enrollment_lesson UNIQUE (enrollment_id, lesson_id)
);

-- Indexes
CREATE INDEX idx_enrollment_progress_enrollment_id ON enrollment_progress(enrollment_id);
```

---

## 4. Payment Service Database (`payment_db`)

### Tables

#### `payments`
```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,  -- Foreign key to User Service (logical)
    course_id UUID NOT NULL,  -- Foreign key to Course Service (logical)
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'REFUNDED', 'CANCELLED')),
    payment_method VARCHAR(50),  -- "credit_card", "paypal", "bank_transfer"
    transaction_id VARCHAR(255) UNIQUE,  -- External payment gateway transaction ID
    gateway_response JSONB,
    idempotency_key VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    failure_reason TEXT
);

-- Indexes
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_course_id ON payments(course_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_transaction_id ON payments(transaction_id);
CREATE INDEX idx_payments_created_at ON payments(created_at DESC);
CREATE INDEX idx_payments_idempotency_key ON payments(idempotency_key);
```

#### `payment_audit_log`
```sql
CREATE TABLE payment_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id UUID NOT NULL REFERENCES payments(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,  -- "CREATED", "COMPLETED", "FAILED", "REFUNDED"
    previous_status VARCHAR(20),
    new_status VARCHAR(20),
    details JSONB,
    performed_by UUID,  -- User ID who performed the action
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_payment_audit_log_payment_id ON payment_audit_log(payment_id);
CREATE INDEX idx_payment_audit_log_created_at ON payment_audit_log(created_at DESC);
```

---

## Database Relationships & Referential Integrity

### Logical Foreign Keys (Cross-Service)
Since each service has its own database, we maintain logical foreign keys:

```
users.id (User Service)
  ↓ (logical reference)
courses.instructor_id (Course Service)
enrollments.user_id (Enrollment Service)
payments.user_id (Payment Service)

courses.id (Course Service)
  ↓ (logical reference)
enrollments.course_id (Enrollment Service)
payments.course_id (Payment Service)
```

**Consistency:** Maintained via API calls and eventual consistency patterns

### Physical Foreign Keys (Within Service)
Within each service database, we use standard PostgreSQL foreign keys for data integrity.

---

## Indexing Strategy

### Primary Indexes
- **Primary Keys:** UUID (better for distributed systems)
- **Unique Constraints:** Email, username, transaction_id

### Secondary Indexes
1. **Frequent Queries:**
   - User lookup by email
   - Courses by instructor
   - Enrollments by user/course
   
2. **Filtering:**
   - Course status, price range
   - Payment status
   - Enrollment status

3. **Sorting:**
   - Created dates (DESC)
   - Course price

4. **Full-Text Search:**
   - Course title and description (GIN index)

### Composite Indexes
```sql
-- For common query patterns
CREATE INDEX idx_enrollments_user_status ON enrollments(user_id, status);
CREATE INDEX idx_courses_status_price ON courses(status, price);
```

---

## Database Optimization Techniques

### 1. Connection Pooling
```python
# SQLAlchemy configuration
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 40
SQLALCHEMY_POOL_TIMEOUT = 30
SQLALCHEMY_POOL_RECYCLE = 3600
```

### 2. Query Optimization
- Use SELECT with specific columns (avoid SELECT *)
- Use LIMIT for paginated queries
- Use JOIN efficiently (avoid N+1 queries)
- Use EXPLAIN ANALYZE for slow queries

### 3. Caching Strategy
- Cache frequently accessed data (courses, user profiles)
- Cache expensive queries (course listings with filters)
- Cache invalidation on updates

### 4. Partitioning (Future)
```sql
-- Partition enrollments by date
CREATE TABLE enrollments_2025_q4 PARTITION OF enrollments
    FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');
```

### 5. Read Replicas (Production)
- Master for writes
- Read replicas for queries
- Load balancing across replicas

---

## Data Migration Strategy

### Alembic Migrations (Per Service)
```bash
# Generate migration
alembic revision --autogenerate -m "create users table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Migration Naming Convention
```
{timestamp}_{action}_{table_name}.py

Examples:
20251021_create_users_table.py
20251021_add_status_to_enrollments.py
20251022_create_index_courses_instructor.py
```

---

## Backup & Disaster Recovery

### Backup Strategy
1. **Automated Daily Backups**
   - PostgreSQL: pg_dump
   - MongoDB: mongodump
   - Redis: RDB snapshots

2. **Point-in-Time Recovery**
   - PostgreSQL WAL archiving
   - Retention: 30 days

3. **Backup Testing**
   - Monthly restore tests
   - Disaster recovery drills

### High Availability
- **PostgreSQL:** Primary-Replica setup
- **MongoDB:** Replica Set (3 nodes)
- **Redis:** Redis Sentinel or Cluster

---

## Security Considerations

### 1. Sensitive Data
- **Password Hashing:** bcrypt with salt
- **Encryption at Rest:** Database-level encryption
- **Encryption in Transit:** SSL/TLS connections

### 2. Access Control
- **Principle of Least Privilege:** Service-specific database users
- **No Root Access:** Dedicated service accounts
- **Connection Strings:** Environment variables, never committed

### 3. SQL Injection Prevention
- **Parameterized Queries:** Always use SQLAlchemy ORM or prepared statements
- **Input Validation:** Pydantic schemas

---

## Monitoring & Alerts

### Database Metrics
- Connection pool usage
- Query execution time
- Slow query log
- Deadlocks
- Disk usage
- Replication lag

### Alerts
- Connection pool exhaustion (> 90%)
- Slow queries (> 1s)
- Disk usage (> 80%)
- Replication lag (> 10s)

---

## Database Sizing Estimates

### Development
| Database | Size |
|----------|------|
| user_db | 10 MB |
| course_db (PostgreSQL) | 50 MB |
| course_db (MongoDB) | 100 MB |
| enrollment_db | 20 MB |
| payment_db | 30 MB |

### Production (1 year, 10K users, 1K courses)
| Database | Estimated Size |
|----------|----------------|
| user_db | 500 MB |
| course_db (PostgreSQL) | 2 GB |
| course_db (MongoDB) | 10 GB |
| enrollment_db | 3 GB |
| payment_db | 1 GB |

---

**Last Updated:** October 21, 2025  
**Authors:** Francis Akol  
**Document Version:** 1.0
