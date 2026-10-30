-- =============================================================================
-- DevData-01 PostgreSQL Database Schema & Import Script (v1.1.0)
-- Conforming to DevData-01_Dataset_Specification.md
-- =============================================================================

-- Drop tables in reverse dependency order if recreating
DROP TABLE IF EXISTS support_tickets CASCADE;
DROP TABLE IF EXISTS activity_logs CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS subscriptions CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;

-- 1. Organizations table
CREATE TABLE organizations (
    organization_id     VARCHAR(32) PRIMARY KEY,
    organization_name   VARCHAR(255) NOT NULL,
    industry            VARCHAR(100) NOT NULL,
    country_code        VARCHAR(2) NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL
);

-- 2. Users table
CREATE TABLE users (
    user_id             VARCHAR(32) PRIMARY KEY,
    organization_id     VARCHAR(32) NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    display_name        VARCHAR(255) NOT NULL,
    email               VARCHAR(255) NOT NULL,
    role                VARCHAR(32) NOT NULL CHECK (role IN ('owner', 'admin', 'member')),
    signup_at           TIMESTAMPTZ NOT NULL,
    status              VARCHAR(32) NOT NULL CHECK (status IN ('active', 'invited', 'disabled'))
);

-- 3. Subscriptions table
CREATE TABLE subscriptions (
    subscription_id     VARCHAR(32) PRIMARY KEY,
    organization_id     VARCHAR(32) NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    plan                VARCHAR(32) NOT NULL CHECK (plan IN ('free', 'starter', 'pro', 'enterprise')),
    billing_cycle       VARCHAR(32) NOT NULL CHECK (billing_cycle IN ('monthly', 'annual')),
    started_at          TIMESTAMPTZ NOT NULL,
    ended_at            TIMESTAMPTZ,
    status              VARCHAR(32) NOT NULL CHECK (status IN ('trialing', 'active', 'past_due', 'canceled', 'expired'))
);

-- 4. Invoices table
CREATE TABLE invoices (
    invoice_id          VARCHAR(32) PRIMARY KEY,
    subscription_id     VARCHAR(32) NOT NULL REFERENCES subscriptions(subscription_id) ON DELETE CASCADE,
    issued_at           TIMESTAMPTZ NOT NULL,
    due_at              TIMESTAMPTZ NOT NULL,
    paid_at             TIMESTAMPTZ,
    amount_minor        BIGINT NOT NULL CHECK (amount_minor >= 0),
    currency_code       VARCHAR(3) NOT NULL DEFAULT 'USD',
    status              VARCHAR(32) NOT NULL CHECK (status IN ('draft', 'open', 'paid', 'void', 'uncollectible'))
);

-- 5. Activity logs table
CREATE TABLE activity_logs (
    event_id            VARCHAR(32) PRIMARY KEY,
    user_id             VARCHAR(32) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    event_type          VARCHAR(64) NOT NULL,
    occurred_at         TIMESTAMPTZ NOT NULL,
    session_id          VARCHAR(64) NOT NULL
);

-- 6. Support tickets table
CREATE TABLE support_tickets (
    ticket_id           VARCHAR(32) PRIMARY KEY,
    organization_id     VARCHAR(32) NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    created_by_user_id  VARCHAR(32) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    category            VARCHAR(64) NOT NULL,
    priority            VARCHAR(16) NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    status              VARCHAR(32) NOT NULL CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    created_at          TIMESTAMPTZ NOT NULL,
    resolved_at         TIMESTAMPTZ
);

-- Performance Indexes on Foreign Keys and Query Filtering Columns
CREATE INDEX idx_users_org_id ON users(organization_id);
CREATE INDEX idx_subscriptions_org_id ON subscriptions(organization_id);
CREATE INDEX idx_invoices_sub_id ON invoices(subscription_id);
CREATE INDEX idx_invoices_issued_at ON invoices(issued_at);
CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_occurred_at ON activity_logs(occurred_at);
CREATE INDEX idx_tickets_org_id ON support_tickets(organization_id);
CREATE INDEX idx_tickets_user_id ON support_tickets(created_by_user_id);

-- =============================================================================
-- CSV IMPORT COMMANDS (PostgreSQL psql \copy syntax)
-- Run these from the project root directory inside psql:
-- psql -d your_database -f scripts/import_postgres.sql
-- =============================================================================

\copy organizations FROM 'data/organizations.csv' WITH (FORMAT csv, HEADER true);
\copy users FROM 'data/users.csv' WITH (FORMAT csv, HEADER true);
\copy subscriptions FROM 'data/subscriptions.csv' WITH (FORMAT csv, HEADER true);
\copy invoices FROM 'data/invoices.csv' WITH (FORMAT csv, HEADER true);
\copy activity_logs FROM 'data/activity_logs.csv' WITH (FORMAT csv, HEADER true);
\copy support_tickets FROM 'data/support_tickets.csv' WITH (FORMAT csv, HEADER true);

-- Quick Row Count Verification
SELECT 'organizations' AS table_name, count(*) AS row_count FROM organizations
UNION ALL
SELECT 'users', count(*) FROM users
UNION ALL
SELECT 'subscriptions', count(*) FROM subscriptions
UNION ALL
SELECT 'invoices', count(*) FROM invoices
UNION ALL
SELECT 'activity_logs', count(*) FROM activity_logs
UNION ALL
SELECT 'support_tickets', count(*) FROM support_tickets;

