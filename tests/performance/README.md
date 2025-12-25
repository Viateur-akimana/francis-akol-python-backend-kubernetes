# Performance Testing with Locust

This directory contains Locust load tests for the MLH Platform.

## Prerequisites

```bash
pip install locust
```

## Running Tests

### Web UI Mode
```bash
# From project root
locust -f tests/performance/locustfile.py --web-host 0.0.0.0

# Open http://localhost:8089 in browser
```

### Headless Mode
```bash
# 100 users, 10 spawn rate, 60 seconds duration
locust -f tests/performance/locustfile.py \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 60s \
  --host http://localhost:8001
```

### Specific Service Testing
```bash
# Course Service only
locust -f tests/performance/locustfile.py CourseServiceUser \
  --headless --users 50 --spawn-rate 5 --run-time 30s

# Enrollment Service only
locust -f tests/performance/locustfile.py EnrollmentServiceUser \
  --headless --users 30 --spawn-rate 3 --run-time 30s

# Payment Service only
locust -f tests/performance/locustfile.py PaymentServiceUser \
  --headless --users 20 --spawn-rate 2 --run-time 30s
```

## Test Scenarios

### MLHUser (Full Flow)
Simulates complete user journey:
- Sign up and login
- Browse courses
- View course details
- Get AI recommendations
- View profile

### CourseServiceUser
Focused course service testing:
- List courses (weighted 5x)
- Get course detail (weighted 3x)
- List categories (weighted 2x)
- Filtered searches

### EnrollmentServiceUser
Enrollment operations:
- List enrollments
- Get enrollment details
- View statistics

### PaymentServiceUser
Payment operations:
- List payments
- Get payment details
- View statistics

## Benchmarks

Target metrics:
- **p95 latency**: < 200ms
- **Throughput**: 1000 req/sec
- **Concurrent users**: 100+
- **Error rate**: < 1%

## Output

### Console Output
```
Type     Name              # reqs   # fails  Avg     Max     Min   Median   req/s  failures/s
GET      /api/v1/courses/   1000      0     45      203      12      35     85.5      0.00
```

### HTML Report
```bash
locust -f tests/performance/locustfile.py \
  --headless --users 50 --spawn-rate 5 --run-time 60s \
  --html reports/performance_report.html
```

## Docker Mode

```bash
docker run -p 8089:8089 -v $(pwd)/tests/performance:/mnt/locust \
  locustio/locust -f /mnt/locust/locustfile.py
```
