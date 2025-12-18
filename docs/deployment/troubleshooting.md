# Troubleshooting Guide

Common issues and solutions for the MLH platform.

## Docker Issues

### Container Won't Start

**Symptoms:** Container exits immediately or fails health check.

**Solutions:**
1. Check logs: `docker logs <container_name>`
2. Verify environment variables in `.env`
3. Ensure dependencies (DB, Redis) are running first
4. Check port conflicts: `lsof -i :<port>`

### Database Connection Refused

**Symptoms:** `Connection refused` or `could not connect to server`

**Solutions:**
1. Ensure PostgreSQL is running: `docker ps | grep postgres`
2. Check DATABASE_URL format
3. Verify network connectivity: `docker network ls`
4. Wait for PostgreSQL to be ready before starting services

### Redis Connection Failed

**Symptoms:** `Connection refused` to Redis

**Solutions:**
1. Ensure Redis is running: `docker ps | grep redis`
2. Check REDIS_URL in environment
3. Verify Redis is accessible: `redis-cli ping`

## Database Issues

### Migration Errors

**Symptoms:** `alembic upgrade head` fails

**Solutions:**
1. Check database exists and is accessible
2. Review migration files in `alembic/versions/`
3. Drop and recreate database if needed (dev only):
   ```bash
   dropdb <database_name>
   createdb <database_name>
   alembic upgrade head
   ```

### Duplicate Key Error

**Symptoms:** `duplicate key value violates unique constraint`

**Solutions:**
1. Check if record already exists
2. Reset sequence: 
   ```sql
   SELECT setval('table_id_seq', (SELECT MAX(id) FROM table));
   ```

## Authentication Issues

### JWT Token Invalid

**Symptoms:** `401 Unauthorized` on authenticated endpoints

**Solutions:**
1. Check JWT_SECRET_KEY matches across services
2. Verify token hasn't expired
3. Ensure token format: `Authorization: Bearer <token>`
4. Check JWT_ALGORITHM is consistent

### Password Verification Failed

**Symptoms:** Login fails with correct password

**Solutions:**
1. Ensure bcrypt is installed correctly
2. Check password hashing on signup
3. Verify no encoding issues

## API Issues

### CORS Errors

**Symptoms:** `Access-Control-Allow-Origin` missing

**Solutions:**
1. Check CORS_ORIGINS includes your frontend URL
2. Verify CORS middleware is configured
3. Check for trailing slashes in origins

### 500 Internal Server Error

**Symptoms:** Unexpected server error

**Solutions:**
1. Check service logs: `docker logs <service>`
2. Enable DEBUG mode for stack traces
3. Check database connection
4. Verify external service URLs

## Celery Issues

### Tasks Not Executing

**Symptoms:** Tasks remain in queue

**Solutions:**
1. Ensure Celery worker is running
2. Check CELERY_BROKER_URL
3. Verify Redis is accessible
4. Check worker logs: `celery -A app.core.celery_app worker --loglevel=info`

### Task Serialization Error

**Symptoms:** `kombu.exceptions.EncodeError`

**Solutions:**
1. Ensure all task arguments are JSON serializable
2. Use primitive types (strings, numbers, lists, dicts)
3. Convert datetime to ISO format strings

## Kubernetes Issues

### Pods in CrashLoopBackOff

**Solutions:**
1. Check pod logs: `kubectl logs <pod> -n mlh-platform`
2. Describe pod: `kubectl describe pod <pod> -n mlh-platform`
3. Verify secrets and configmaps exist
4. Check resource limits

### Service Unavailable

**Solutions:**
1. Check pod status: `kubectl get pods -n mlh-platform`
2. Verify service endpoints: `kubectl get endpoints -n mlh-platform`
3. Check ingress configuration
4. Test service directly: `kubectl port-forward svc/user-service 8001:80 -n mlh-platform`

## Getting Help

If issues persist:
1. Check GitHub Issues
2. Review service logs
3. Enable DEBUG mode
4. Contact maintainers
