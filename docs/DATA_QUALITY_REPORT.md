# DevData-01 Data Quality & Integrity Report

**Dataset Version:** 1.1.0  
**Audit Date:** 2026-10-30  
**Generator Seed:** 42 (Fully deterministic)  
**Target Platform:** Kaggle (Public Developer & Educational Dataset)  
**Specification Compliance:** 100% compliant with `DevData-01_Dataset_Specification.md`

---

## 1. Executive Summary

A comprehensive automated audit was performed on the **DevData-01** relational synthetic dataset across all 6 core files. The dataset satisfies all 3NF relational constraints, strict foreign key referential integrity (0 orphan records), same-tenant access boundaries, chronological validity, and financial pricing consistency.

| Metric | Target | Actual | Audit Result |
| :--- | :---: | :---: | :---: |
| Total Tables / CSVs | 6 | 6 | Passed |
| Total Records | 19,800 | 19,800 | Passed |
| Primary Key Duplicates | 0 | 0 | Passed (100% Unique) |
| Orphan Foreign Key Rows | 0 | 0 | Passed (100% Referential Integrity) |
| Cross-Tenant Ticket Leakage | 0 | 0 | Passed (100% Same-Tenant Guaranteed) |
| Overlapping Active Subscriptions per Org | 0 | 0 | Passed |
| Invoices Billed to Free Plan | 0 | 0 | Passed |
| Activity Logs by Invited (Unaccepted) Users | 0 | 0 | Passed |
| Ticket Creation by Invited Users | 0 | 0 | Passed |
| Temporal Sequence Inversions | 0 | 0 | Passed |

---

## 2. Record Counts & File Grain

| File | Entity Grain | Row Count | Primary Key | Foreign Key Dependencies |
| :--- | :--- | :---: | :--- | :--- |
| `data/organizations.csv` | One organization / customer company | 200 | `organization_id` | — |
| `data/users.csv` | One user membership in an organization | 2,000 | `user_id` | `organization_id` |
| `data/subscriptions.csv` | One subscription contract lifecycle | 300 | `subscription_id` | `organization_id` |
| `data/invoices.csv` | One periodic billing record | 1,500 | `invoice_id` | `subscription_id` |
| `data/activity_logs.csv` | One product interaction / audit event | 15,000 | `event_id` | `user_id` |
| `data/support_tickets.csv` | One customer support incident | 800 | `ticket_id` | `organization_id`, `created_by_user_id` |
| **Total** | | **19,800** | | |

---

## 3. Missing Values & Nullability Audit

All fields are non-null with the exception of 3 explicitly nullable business fields defined in the schema specification:

| File | Column | Null Count | Null % | Business Justification |
| :--- | :--- | :---: | :---: | :--- |
| `subscriptions.csv` | `ended_at` | 173 | 57.7% | Ongoing subscriptions (`active`, `trialing`, `past_due`) have no end date. Only churned (`canceled`, `expired`) subscriptions have an explicit `ended_at`. |
| `invoices.csv` | `paid_at` | 103 | 6.9% | Unsettled invoices (`open`, `draft`, `uncollectible`, `void`) have null `paid_at`. 100% of `paid` invoices have a valid `paid_at` timestamp. |
| `support_tickets.csv` | `resolved_at` | 157 | 19.6% | Active tickets (`open`, `in_progress`) are unresolved. 100% of `resolved` and `closed` tickets have a valid `resolved_at` timestamp. |

All other 33 columns across all 6 tables have **0 null values (100% non-null)**.

---

## 4. Referential Integrity & Same-Tenant Boundaries

1. **Foreign Key Integrity:**
   - `users.organization_id` → `organizations.organization_id`: 0 orphans.
   - `subscriptions.organization_id` → `organizations.organization_id`: 0 orphans.
   - `invoices.subscription_id` → `subscriptions.subscription_id`: 0 orphans.
   - `activity_logs.user_id` → `users.user_id`: 0 orphans.
   - `support_tickets.organization_id` → `organizations.organization_id`: 0 orphans.
   - `support_tickets.created_by_user_id` → `users.user_id`: 0 orphans.
2. **Multi-Tenant Boundary Guarantee:**
   - 100% of support tickets (800 / 800) have `created_by_user_id` belonging to the same `organization_id` referenced on the ticket. Zero cross-tenant data leakage.

---

## 5. Date & Chronological Consistency

All timestamps are encoded in ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`). The following temporal assertions were programmatically evaluated and passed with 0 violations:

1. **User Signup vs. Organization Creation:**
   - Assertion: `users.signup_at >= organizations.created_at`
   - Result: 0 violations across 2,000 users.
2. **Activity Event vs. User Signup:**
   - Assertion: `activity_logs.occurred_at >= users.signup_at`
   - Result: 0 violations across 15,000 activity logs.
3. **Subscription Lifecycle Dates:**
   - Assertion: `subscriptions.started_at <= subscriptions.ended_at` (for ended subscriptions)
   - Result: 0 violations across 300 subscriptions.
4. **Subscription Period Overlap:**
   - Assertion: No two subscriptions for the same organization have overlapping active time windows.
   - Result: 0 overlapping subscription periods across all 200 organizations.
5. **Invoice Issuance vs. Due Dates:**
   - Assertion: `invoices.issued_at <= invoices.due_at`
   - Result: 0 violations across 1,500 invoices. Standard grace period is exactly `issued_at + 14 days`.
6. **Paid Settlement Timestamps:**
   - Assertion: `paid_at >= issued_at` and `paid_at <= due_at + 3 days grace`
   - Result: 0 violations across 1,397 paid invoices.
7. **Support Ticket Resolution:**
   - Assertion: `support_tickets.created_at <= support_tickets.resolved_at`
   - Result: 0 violations across 643 resolved/closed tickets.
8. **SLA Resolution Realism:**
   - Urgent tickets resolve in **4.0 hours average** (SLA range 30m–8h).
   - High priority tickets resolve in **12.8 hours average** (SLA range 2h–24h).
   - Medium priority tickets resolve in **26.8 hours average** (SLA range 6h–48h).
   - Low priority tickets resolve in **41.3 hours average** (SLA range 12h–72h).

---

## 6. Financial & Revenue Consistency

All monetary amounts are stored as non-negative integers representing currency minor units (`amount_minor` in USD cents):

| Metric | Cents (`amount_minor`) | USD Equivalent |
| :--- | :---: | :---: |
| Total Invoiced Gross Volume | 24,650,700 | $246,507.00 |
| Total Collected Revenue | 22,489,200 | $224,892.00 |
| Total Open Receivables | 1,349,300 | $13,493.00 |
| Total Uncollectible (Delinquent Bad Debt) | 121,400 | $1,214.00 |
| Total Voided Invoices | 521,200 | $5,212.00 |
| Total Draft Invoices | 169,600 | $1,696.00 |
| **Gross Payment Collection Rate** | — | **91.23%** |

### Pricing Schedule Adherence:
- `starter` plan: $29.00 / mo (`2900`), $290.00 / yr (`29000`)
- `pro` plan: $99.00 / mo (`9900`), $990.00 / yr (`99000`)
- `enterprise` plan: $299.00 / mo (`29900`), $2,990.00 / yr (`299000`)
- `free` plan: $0.00 (`0`) — **strictly 0 invoices generated for free plans**.
- Exact Pricing Fidelity: 1,500 / 1,500 invoices (100%) match the pricing matrix.

---

## 7. Categorical & Enum Distributions

### `users.csv`
- **Role:** `member`: 1,362 (68.1%), `admin`: 438 (21.9%), `owner`: 200 (10.0%, exactly 1 per organization).
- **Status:** `active`: 1,697 (84.85%), `invited`: 205 (10.25%), `disabled`: 98 (4.90%).

### `subscriptions.csv`
- **Plan:** `starter`: 132 (44.0%), `pro`: 92 (30.7%), `enterprise`: 47 (15.7%), `free`: 29 (9.7%).
- **Billing Cycle:** `monthly`: 252 (84.0%), `annual`: 48 (16.0%).
- **Status:** `active`: 150 (50.0%), `canceled`: 99 (33.0%), `expired`: 28 (9.3%), `past_due`: 12 (4.0%), `trialing`: 11 (3.7%).

### `invoices.csv`
- **Status:** `paid`: 1,397 (93.13%), `open`: 54 (3.60%), `void`: 19 (1.27%), `uncollectible`: 16 (1.07%), `draft`: 14 (0.93%).
- **Currency:** `USD`: 1,500 (100%).

### `activity_logs.csv`
- **Event Frequency:**
  - `login`: 5,052 (33.7%)
  - `dashboard_viewed`: 4,215 (28.1%)
  - `report_viewed`: 2,534 (16.9%)
  - `project_created`: 1,527 (10.2%)
  - `export_completed`: 1,080 (7.2%)
  - `settings_updated`: 173 (1.15%)
  - `api_key_generated`: 153 (1.02%)
  - `integration_enabled`: 138 (0.92%)
  - `team_invite_sent`: 128 (0.85%)
- **Access Control:** Privileged actions (`api_key_generated`, `team_invite_sent`, `settings_updated`, `integration_enabled`) are 100% executed by `owner` and `admin` roles only.

### `support_tickets.csv`
- **Category:** `Account & Access`: 187 (23.4%), `Billing & Payments`: 170 (21.2%), `Technical Bug`: 151 (18.9%), `API & Integrations`: 151 (18.9%), `Feature Request`: 141 (17.6%).
- **Priority:** `medium`: 334 (41.8%), `low`: 203 (25.4%), `high`: 194 (24.2%), `urgent`: 69 (8.6%).
- **Status:** `resolved`: 431 (53.9%), `closed`: 212 (26.5%), `in_progress`: 86 (10.8%), `open`: 71 (8.9%).

---

## 8. Known Limitations & Synthetic Boundaries

1. **Synthetic Nature:** Distributions, retention rates, and revenue churn are produced parametrically by the generator. They **do not represent real-world empirical SaaS industry benchmarks**.
2. **Simplified Invoicing Model:** Invoicing models periodic recurring plan payments. It does not model taxes, credit card processing fees, partial refunds, prorations, or line-item usage metering.
3. **Single Tenant Membership:** Each user record belongs to exactly one organization (`organization_id`). Multi-organization user memberships (e.g., cross-tenant collaboration) are not modeled in v1.1.0.
4. **Reserved Contact Data:** All email addresses use the RFC 2606 reserved domain `@example.com` to guarantee zero exposure of personal information.

