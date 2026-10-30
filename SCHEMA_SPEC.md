# DevData-01: Relational Schema & Specification

## Architecture Overview
The dataset models a B2B SaaS platform with 6 interconnected entities enforcing strict referential integrity, logical temporal constraints (e.g., invoices occur after subscription start), and realistic business domain logic.

```
       +-----------------------+
       |     organizations     |
       +-----------+-----------+
             |           |
    1:N      |           |  1:N
             v           v
      +------------+  +-----------------+
      |   users    |  |  subscriptions  |
      +-----+------+  +--------+--------+
            |                  |
      1:N   |        1:N       |  1:N
            v        +---------+
    +---------------+|         v
    | activity_logs ||   +------------+
    +---------------+|   |  invoices  |
            |        |   +------------+
      1:N   v        v 1:N
       +------------------+
       |  support_tickets |
       +------------------+
```

## Schema Definitions

### 1. `organizations.csv`
- `org_id` (PK, string, e.g. `org_0001`): Unique identifier for each company.
- `name` (string): Company/team name.
- `domain` (string): Primary domain (e.g. `acme-analytics.io`).
- `industry` (categorical): `Fintech`, `Healthcare`, `Edtech`, `Developer Tools`, `Marketing`, `Cybersecurity`, `E-Commerce`, `Logistics`.
- `company_size` (categorical): `1-10`, `11-50`, `51-200`, `201-500`, `500+`.
- `created_at` (ISO timestamp): Organization registration date (range: 2023-01-01 to 2025-06-30).
- `country` (string, ISO-2): Geographic origin (`US`, `GB`, `CA`, `DE`, `FR`, `IN`, `AU`, `SG`, etc.).

### 2. `users.csv`
- `user_id` (PK, string, e.g. `usr_00001`): Unique user ID.
- `org_id` (FK -> `organizations.org_id`): Organization the user belongs to.
- `first_name` (string): First name.
- `last_name` (string): Last name.
- `email` (string): Business email using organization domain.
- `role` (categorical): `owner`, `admin`, `member`, `guest`. (Every org must have exactly 1 owner).
- `status` (categorical): `active`, `invited`, `suspended`.
- `created_at` (ISO timestamp): User signup date (must be >= `organizations.created_at`).
- `last_login_at` (ISO timestamp / null): Last login time (must be >= `users.created_at` or null if invited).

### 3. `subscriptions.csv`
- `subscription_id` (PK, string, e.g. `sub_0001`): Unique subscription ID.
- `org_id` (FK -> `organizations.org_id`): Organization subscribing.
- `plan_tier` (categorical): `Starter` ($29/mo), `Growth` ($99/mo), `Scale` ($299/mo), `Enterprise` ($999/mo).
- `billing_cycle` (categorical): `monthly`, `annual` (annual receives 15% discount).
- `status` (categorical): `active`, `past_due`, `canceled`, `trialing`.
- `mrr` (float, 2 decimals): Monthly recurring revenue normalized to dollars.
- `current_period_start` (ISO timestamp): Start of current billing cycle (>= org `created_at`).
- `current_period_end` (ISO timestamp): End of period (+1 month or +1 year from period start).
- `canceled_at` (ISO timestamp / null): Non-null only if status is `canceled` (must be >= `current_period_start`).

### 4. `invoices.csv`
- `invoice_id` (PK, string, e.g. `inv_00001`): Unique invoice number.
- `subscription_id` (FK -> `subscriptions.subscription_id`): Associated subscription.
- `org_id` (FK -> `organizations.org_id`): Redundant foreign key for analytical ease.
- `amount_due` (float): Billed amount in USD (matches plan price, taking billing cycle discount into account).
- `amount_paid` (float): Actual amount collected.
- `currency` (string): Always `USD`.
- `status` (categorical): `paid`, `open`, `void`, `uncollectible`.
- `due_date` (ISO timestamp): Typically `invoice_date + 14 days`.
- `invoice_date` (ISO timestamp): Issued timestamp (within subscription active span).
- `paid_at` (ISO timestamp / null): Populated if `status == 'paid'` (between `invoice_date` and `due_date + grace`).

### 5. `activity_logs.csv`
- `log_id` (PK, string, e.g. `act_000001`): Unique log ID.
- `org_id` (FK -> `organizations.org_id`): Organization context.
- `user_id` (FK -> `users.user_id`): User triggering action.
- `action` (categorical): `user.login`, `user.logout`, `report.export`, `dashboard.view`, `api_key.create`, `integration.connected`, `settings.update`, `billing.update`.
- `ip_address` (string): Synthetic IPv4 address.
- `user_agent` (string): Browser user agent (Chrome, Firefox, Safari, Edge).
- `timestamp` (ISO timestamp): When action occurred (must be >= `users.created_at`).

### 6. `support_tickets.csv`
- `ticket_id` (PK, string, e.g. `tkt_0001`): Unique ticket ID.
- `org_id` (FK -> `organizations.org_id`): Company filing ticket.
- `user_id` (FK -> `users.user_id`): Submitter user.
- `subject` (string): Brief summary of issue.
- `category` (categorical): `Billing`, `Technical Bug`, `Feature Request`, `Account Access`, `API & Webhooks`.
- `priority` (categorical): `low`, `medium`, `high`, `urgent`.
- `status` (categorical): `open`, `in_progress`, `resolved`, `closed`.
- `created_at` (ISO timestamp): Ticket submission time (>= user creation).
- `resolved_at` (ISO timestamp / null): Resolution time (populated if resolved/closed, >= created_at).
- `satisfaction_score` (integer / null): CSAT rating from 1 to 5 (populated for 60% of resolved tickets).

## Referential Integrity & Validation Rules
1. Every foreign key matches a valid, existing primary key in the parent table.
2. Temporal hierarchy is strictly respected:
   `org.created_at <= user.created_at <= activity.timestamp`
   `org.created_at <= subscription.current_period_start <= invoice.invoice_date`
   `user.created_at <= ticket.created_at <= ticket.resolved_at`
3. Domain consistency: User email matches their organization's clean domain slug.
4. Business consistency: Invoice amounts match subscription tier and billing cycle calculations.

