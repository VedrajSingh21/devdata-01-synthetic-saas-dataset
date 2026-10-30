# DevData-01 Data Dictionary

Version: 1.0.0  
Format: CSV (UTF-8, ISO 8601 UTC timestamps, integer minor units for currency)

---

## 1. `organizations.csv`
Contains high-level account information for customer teams and enterprises.

| Field Name | Type | Key | Nullable | Description / Allowed Values | Example |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `organization_id` | string | **PK** | No | Unique organization identifier (`org_0001` to `org_0200`) | `org_0042` |
| `organization_name` | string | | No | Synthetic company name | `Apex Digital 42` |
| `industry` | string | | No | `Fintech`, `Healthcare`, `Edtech`, `Developer Tools`, `Marketing`, `Cybersecurity`, `E-Commerce`, `Logistics`, `Human Resources`, `Data Analytics` | `Developer Tools` |
| `country_code` | string | | No | ISO 2-letter country code | `US`, `GB`, `DE`, `CA` |
| `created_at` | string | | No | ISO 8601 UTC timestamp of account registration | `2023-04-12T14:22:00Z` |

---

## 2. `users.csv`
Represents individual user accounts and team memberships within an organization.

| Field Name | Type | Key | Nullable | Description / Allowed Values | Example |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `user_id` | string | **PK** | No | Unique user ID (`usr_00001` to `usr_02000`) | `usr_00124` |
| `organization_id` | string | **FK** | No | Reference to `organizations.organization_id` | `org_0042` |
| `display_name` | string | | No | Synthetic user full name | `Sarah Jenkins` |
| `email` | string | | No | Reserved example email (`@example.com`) | `sarah.jenkins12@example.com` |
| `role` | string | | No | `owner`, `admin`, `member` | `admin` |
| `signup_at` | string | | No | ISO 8601 UTC timestamp (`>= organizations.created_at`) | `2023-05-01T09:15:30Z` |
| `status` | string | | No | `active`, `invited`, `disabled` | `active` |

---

## 3. `subscriptions.csv`
Records subscription contracts and plan lifecycle states.

| Field Name | Type | Key | Nullable | Description / Allowed Values | Example |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `subscription_id` | string | **PK** | No | Unique subscription ID (`sub_0001` to `sub_0300`) | `sub_0085` |
| `organization_id` | string | **FK** | No | Reference to `organizations.organization_id` | `org_0042` |
| `plan` | string | | No | `free`, `starter`, `pro`, `enterprise` | `pro` |
| `billing_cycle` | string | | No | `monthly`, `annual` | `monthly` |
| `started_at` | string | | No | ISO 8601 UTC timestamp when plan started | `2023-05-02T10:00:00Z` |
| `ended_at` | string | | Yes | ISO 8601 UTC timestamp when subscription ended (null if active) | `2024-02-01T10:00:00Z` |
| `status` | string | | No | `trialing`, `active`, `past_due`, `canceled`, `expired` | `active` |

---

## 4. `invoices.csv`
Synthetic billing records corresponding to paid subscription contracts.

| Field Name | Type | Key | Nullable | Description / Allowed Values | Example |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `invoice_id` | string | **PK** | No | Unique invoice identifier (`inv_00001` to `inv_01500`) | `inv_00320` |
| `subscription_id` | string | **FK** | No | Reference to `subscriptions.subscription_id` | `sub_0085` |
| `issued_at` | string | | No | ISO 8601 UTC timestamp invoice was issued | `2023-06-02T10:00:00Z` |
| `due_at` | string | | No | ISO 8601 UTC payment due date (`issued_at + 14 days`) | `2023-06-16T10:00:00Z` |
| `paid_at` | string | | Yes | ISO 8601 UTC settlement timestamp (non-null for `paid` status) | `2023-06-04T16:40:00Z` |
| `amount_minor` | integer | | No | Billed amount in minor currency units (cents, e.g., 9900 = $99.00) | `9900` |
| `currency_code` | string | | No | ISO 4217 3-letter currency code | `USD` |
| `status` | string | | No | `draft`, `open`, `paid`, `void`, `uncollectible` | `paid` |

---

## 5. `activity_logs.csv`
Product interactions, event stream, and feature usage telemetry.

| Field Name | Type | Key | Nullable | Description / Allowed Values | Example |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `event_id` | string | **PK** | No | Unique event identifier (`evt_000001` to `evt_015000`) | `evt_004521` |
| `user_id` | string | **FK** | No | Reference to `users.user_id` | `usr_00124` |
| `event_type` | string | | No | `login`, `project_created`, `report_viewed`, `export_completed`, `dashboard_viewed`, `api_key_generated`, `integration_enabled`, `settings_updated`, `team_invite_sent` | `dashboard_viewed` |
| `occurred_at` | string | | No | ISO 8601 UTC timestamp (`>= users.signup_at`) | `2023-08-14T11:24:00Z` |
| `session_id` | string | | No | Session tracking ID (`sess_XXXXXX`) | `sess_482910` |

---

## 6. `support_tickets.csv`
Customer inquiries and technical support requests.

| Field Name | Type | Key | Nullable | Description / Allowed Values | Example |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `ticket_id` | string | **PK** | No | Unique support ticket ID (`tkt_0001` to `tkt_0800`) | `tkt_0142` |
| `organization_id` | string | **FK** | No | Reference to `organizations.organization_id` | `org_0042` |
| `created_by_user_id` | string | **FK** | No | Reference to `users.user_id` (guaranteed member of same organization) | `usr_00124` |
| `category` | string | | No | `Billing & Payments`, `Technical Bug`, `Feature Request`, `Account & Access`, `API & Integrations` | `Technical Bug` |
| `priority` | string | | No | `low`, `medium`, `high`, `urgent` | `high` |
| `status` | string | | No | `open`, `in_progress`, `resolved`, `closed` | `resolved` |
| `created_at` | string | | No | ISO 8601 UTC ticket submission timestamp | `2023-09-10T14:00:00Z` |
| `resolved_at` | string | | Yes | ISO 8601 UTC ticket resolution timestamp (`>= created_at`) | `2023-09-11T09:20:00Z` |

