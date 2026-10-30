# DevData-01: Synthetic SaaS Application Dataset


## 1. Overview

DevData-01 is a reproducible, fully synthetic, relational SaaS dataset for practicing backend development, database queries, analytics, and dashboard prototyping. It models organizations, their users, subscriptions, invoices, product activity, and support tickets. It must not contain real personal or payment information.

The goal of the first release is to learn the end-to-end dataset workflow: schema design, generation, validation, documentation, licensing, and publication. It is **not** a real-world benchmark or a representative sample of SaaS companies.

## Why this dataset exists

Many developers need believable, connected application data before they have a live product or customers. A collection of unrelated dummy rows is easy to generate, but it is less useful for testing joins, permissions, billing states, time-based analytics, and full application flows. DevData-01 aims to provide one documented practice environment spanning those workflows.

**Main goal:** Publish a free, reproducible, developer-ready synthetic SaaS dataset on Kaggle that someone can import and use without having to invent six related tables themselves. For its creator, the goal is hands-on experience with data modeling, generation, QA, packaging, documentation, and public feedback—not initial revenue.

### Who would use it, and why?

| User | Practical use |
|---|---|
| Backend / full-stack developer | Seed a local SaaS prototype, exercise joins, filters, pagination and API endpoints |
| SQL learner | Practice primary/foreign keys, aggregations, CTEs and window functions on connected tables |
| Dashboard developer | Prototype subscription, engagement, billing and support views without real customer data |
| Data analyst / student | Practice cohort analysis and explain assumptions in synthetic business metrics |
| QA engineer | Build fixtures for lifecycle states and test data integrity |
| Educator | Give learners a shared schema for assignments and demonstrations |

### What makes it distinctive (design goals, not proven market uniqueness)

1. **One connected SaaS story:** organizations, memberships, subscription history, invoices, user events and tickets refer to each other coherently.
2. **Lifecycle-aware records:** statuses and timestamps obey explicit business rules rather than being sampled independently.
3. **Developer-first delivery:** six CSVs, a data dictionary, import examples, a reproducible generator, validation tests and a working notebook.
4. **Transparent synthetic assumptions:** generation logic, seed, limits and non-representativeness are disclosed.
5. **Useful edge cases:** where feasible, include trials, cancellation, overdue invoices, inactive users, unresolved tickets and organizations with different activity levels—while preserving consistency.

These features are a proposed quality standard, **not a claim that similar free datasets do not exist**. Compare alternatives and collect user feedback after release.

### Problem statements (PS) the dataset should help developers explore

| ID | Problem statement | Example outcome |
|---|---|---|
| PS-01 | How can a developer seed a multi-tenant SaaS app without real customer records? | Import the six tables and build organization-scoped endpoints |
| PS-02 | How can SQL learners query related business entities rather than isolated flat files? | Join organizations → subscriptions → invoices and users → activity |
| PS-03 | How can a dashboard prototype show subscription and billing trends? | Compute active subscriptions, billed amounts and payment status by month |
| PS-04 | How can a developer inspect user engagement by signup cohort? | Calculate event counts and active users by cohort under stated definitions |
| PS-05 | How can support operations be explored alongside account context? | Analyze open tickets, resolution time and priority by organization |
| PS-06 | How can QA validate that synthetic application data is internally coherent? | Run PK/FK, same-tenant, status and timestamp assertions |

**Example developer questions:** Which organizations have active subscriptions? What share of issued invoices is paid? Which signup cohorts generate repeat activity? Which organizations have unresolved urgent tickets? Can an API reject cross-organization ticket access? Note: the current schema has one organization per user; it does not model multi-organization memberships or prove authorization is secure.

### Scope and honest limitations

This is **not** an industry-representative dataset, a verified SaaS benchmark, a source of real market insights, or proof of demand for a paid product. Any revenue, churn or retention metric reflects the generator's assumptions. The v1 schema is intentionally small; features such as refunds, taxes, plan changes, line items, usage-based billing and detailed permission models are out of scope unless explicitly added later.

## 2. Planned size

| File | Target rows | Grain |
|---|---:|---|
| `organizations.csv` | 200 | One organization |
| `users.csv` | 2,000 | One user membership in an organization |
| `subscriptions.csv` | 300 | One subscription period/record |
| `invoices.csv` | 1,500 | One invoice |
| `activity_logs.csv` | 15,000 | One product event |
| `support_tickets.csv` | 800 | One support ticket |
| **Total** | **19,800** | Planned, not yet generated |

## 3. Proposed schema

These fields are an initial contract and may be revised before generation. IDs should be stable, unique strings; timestamps should use ISO 8601 UTC; money should be stored as integer minor units (e.g., cents), with an explicit currency code.

### `organizations.csv`
- `organization_id` (PK)
- `organization_name` (fictional)
- `industry` (synthetic category)
- `country_code`
- `created_at`

### `users.csv`
- `user_id` (PK)
- `organization_id` (FK → organizations)
- `display_name` (fictional)
- `email` (reserved example domain, e.g., `example.com`)
- `role` (`owner`, `admin`, `member`)
- `signup_at`
- `status` (`active`, `invited`, `disabled`)

### `subscriptions.csv`
- `subscription_id` (PK)
- `organization_id` (FK → organizations)
- `plan` (`free`, `starter`, `pro`, `enterprise`)
- `billing_cycle` (`monthly`, `annual`)
- `started_at`
- `ended_at` (nullable)
- `status` (`trialing`, `active`, `past_due`, `canceled`, `expired`)

### `invoices.csv`
- `invoice_id` (PK)
- `subscription_id` (FK → subscriptions)
- `issued_at`
- `due_at`
- `paid_at` (nullable)
- `amount_minor` (nonnegative integer)
- `currency_code`
- `status` (`draft`, `open`, `paid`, `void`, `uncollectible`)

### `activity_logs.csv`
- `event_id` (PK)
- `user_id` (FK → users)
- `event_type` (e.g., `login`, `project_created`, `report_viewed`, `export_completed`)
- `occurred_at`
- `session_id` (synthetic identifier)

### `support_tickets.csv`
- `ticket_id` (PK)
- `organization_id` (FK → organizations)
- `created_by_user_id` (FK → users; must belong to the same organization)
- `category`
- `priority` (`low`, `medium`, `high`, `urgent`)
- `status` (`open`, `in_progress`, `resolved`, `closed`)
- `created_at`
- `resolved_at` (nullable)

## 4. Relationships and consistency rules

- Each user belongs to an existing organization.
- Each subscription belongs to an existing organization; an organization may have multiple historical subscription records.
- Each invoice references an existing subscription.
- Each activity event references an existing user.
- Each ticket references an existing organization and a user from that same organization.
- `created_at <= resolved_at` when a ticket has a resolution timestamp.
- `issued_at <= due_at`; a paid invoice has `paid_at` populated.
- Subscription end dates cannot precede start dates.
- Event timestamps must not precede the referenced user's signup timestamp.
- Generation rules should model coherent timelines and plausible distributions; document assumptions rather than claiming real-world representativeness.

## 5. Generation approach

1. Define schema, allowed values, and temporal rules.
2. Write a Python generator with a fixed random seed and pinned dependencies.
3. Generate organizations, then users and subscriptions, followed by invoices, events, and tickets.
4. Use fictional names and reserved example domains; never copy real customer data.
5. Export UTF-8 CSV files with consistent null handling and date formats.
6. Record the seed, generator version, generation date, and assumptions in the README.

## 6. Validation checklist

- [x] All six files exist and match documented columns/types.
- [x] Row counts match the release manifest.
- [x] Primary keys are non-null and unique.
- [x] All foreign keys resolve, including same-organization ticket ownership.
- [x] Status and category values match their documented enums.
- [x] No impossible date sequences or negative invoice amounts.
- [x] Paid invoice timestamps and ticket resolution timestamps are consistent with status.
- [x] CSV files load into pandas and a relational database.
- [x] Re-running with the same seed and generator version produces identical outputs.
- [x] Sample queries and notebook run successfully.
- [x] No actual personal, financial, or proprietary information is included.

## 7. Intended use and limitations

**Suitable for:** SQL joins, relational modeling, API fixtures, test environments, SaaS metrics demonstrations, cohort-analysis exercises, and dashboards.

**Not suitable for:** Drawing conclusions about actual SaaS market behavior, fraud detection in production, training systems that require real behavioral distributions, or making financial decisions. Synthetic patterns are determined by the generator.

## 8. Proposed repository layout

```text
DevData-01/
├── data/
│   ├── organizations.csv
│   ├── users.csv
│   ├── subscriptions.csv
│   ├── invoices.csv
│   ├── activity_logs.csv
│   └── support_tickets.csv
├── scripts/
│   ├── generate.py
│   └── validate.py
├── notebooks/
│   └── example_analysis.ipynb
├── docs/
│   └── data_dictionary.md
├── requirements.txt
├── LICENSE
└── README.md
```

## 9. Kaggle publication plan

**Proposed title:** Synthetic SaaS Business Dataset – Users, Billing & Activity  
**Suggested tags:** synthetic data, SaaS, SQL, CSV, analytics, developer tools  
**Proposed version:** 1.0.0

Publication package:
- Six generated CSVs, README, data dictionary, generation methodology, and validation summary.
- A companion notebook showing joins, monthly recurring revenue *under explicitly stated assumptions*, user activity, and support-ticket trends.
- A link to the public generation-code repository.
- A clearly stated synthetic-data disclaimer and limitations.
- A license selected after verifying that every included asset can legally be released under it; CC BY 4.0 is a candidate, not an automatic choice.

## 10. Milestones

1. Finalize the schema and business rules.
2. Generate a small sample and inspect it manually.
3. Generate the target dataset reproducibly.
4. Run automated quality tests and fix failures.
5. Prepare documentation and example notebook.
6. Publish v1.0.0 on Kaggle and gather developer feedback.
7. Consider a later improved or commercial product only after demand is demonstrated; existing open-license grants cannot simply be withdrawn.

## Success criteria

Version 1 succeeds when another developer can download the files, understand the schema without asking questions, import the data, reproduce the generator output, and run the sample notebook without broken references.
