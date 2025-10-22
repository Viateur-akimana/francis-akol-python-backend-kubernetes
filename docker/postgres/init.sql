-- ============================================
-- Modular Learning Hub - Database Initialization
-- ============================================
-- This script creates separate databases for each microservice

-- Create databases
CREATE DATABASE user_db;
CREATE DATABASE course_db;
CREATE DATABASE enrollment_db;
CREATE DATABASE payment_db;

-- Grant privileges (if needed for different users)
GRANT ALL PRIVILEGES ON DATABASE user_db TO mlh_user;
GRANT ALL PRIVILEGES ON DATABASE course_db TO mlh_user;
GRANT ALL PRIVILEGES ON DATABASE enrollment_db TO mlh_user;
GRANT ALL PRIVILEGES ON DATABASE payment_db TO mlh_user;

-- Switch to each database and enable UUID extension
\c user_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For full-text search

\c course_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c enrollment_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c payment_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Success message
\c postgres;
SELECT 'Databases created successfully!' as message;
