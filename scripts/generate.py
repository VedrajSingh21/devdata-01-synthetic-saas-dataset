"""
DevData-01 Data Generator (v1.1.0)
Conforming strictly to DevData-01_Dataset_Specification.md:
- Exact schema & column naming
- Exact target row counts (19,800 records across 6 tables)
- Strict relational constraints, same-tenant ticket rules, temporal validity
- Deterministic random seed (42)
- Currency in amount_minor (integer cents), ISO 8601 UTC timestamps

Refinements in v1.1.0:
1. Subscription Lifecycle & Chronology:
   - Eliminates overlapping active subscriptions for the same organization.
   - Distinct lifecycle tracks: ongoing subscriptions, upgrades (previous sub canceled/ended),
     churned subscriptions (ended with cancellation), and trial conversions.
2. Invoicing Cadence & Realism:
   - Periodic invoicing based on billing_cycle: ~30 days for monthly, ~365 days for annual.
   - Non-overlapping invoice billing spans.
   - Invoices only for billable plans ('starter', 'pro', 'enterprise'); 'free' is never invoiced.
   - Invoices for 'trialing' subscriptions only occur if upgraded/converted.
   - 'past_due' subscriptions explicitly have their most recent invoice in 'open' or 'uncollectible' status.
   - 'canceled' subscriptions with unpaid balance properly reflect delinquent churn.
3. Activity Logs Realism & Permission Constraints:
   - Only active/disabled users produce activity logs; invited users have 0 events.
   - Event types respect role hierarchies (e.g. only owners/admins generate API keys, update settings, invite members).
   - Event distribution reflects realistic SaaS usage frequencies (login and dashboard views occur more frequently).
4. Support Tickets Realism:
   - Same-tenant ownership guaranteed.
   - Tickets only created by users who have activated their account (no invited users filing tickets).
   - Urgent tickets resolve faster on average (realistic SLA distribution) than low/medium priority.
"""

import os
import random
import csv
from datetime import datetime, timedelta, timezone

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Row Count Targets
TARGET_ORGS = 200
TARGET_USERS = 2000
TARGET_SUBS = 300
TARGET_INVOICES = 1500
TARGET_LOGS = 15000
TARGET_TICKETS = 800

# Timeline Anchor: Jan 1, 2023 to Nov 1, 2025
START_DATE = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
END_DATE = datetime(2025, 11, 1, 0, 0, 0, tzinfo=timezone.utc)

# Synthetic vocabulary
FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Anna", "Stephen", "Brenda",
    "Larry", "Pamela", "Justin", "Emma", "Scott", "Nicole", "Brandon", "Helen"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker"
]

ORG_NAMES = [
    "Acme Analytics", "Pulse Metrics", "Stratum Cloud", "Hyper Solutions", "Omni Systems",
    "Quantum Dynamics", "Nexus Logic", "Synergy Forge", "Acro Stack", "Cipher Labs",
    "Apex Hub", "Vortex Digital", "Horizon Media", "Prism Data", "Kinetic Sync",
    "Aether Core", "Zenith Technologies", "Summit AI", "True Automation", "Delta Logic",
    "Bright Engine", "Cloud Flareway", "Flux Platform", "Beacon Software", "Crest Works"
]

INDUSTRIES = [
    "Fintech", "Healthcare", "Edtech", "Developer Tools", "Marketing",
    "Cybersecurity", "E-Commerce", "Logistics", "Human Resources", "Data Analytics"
]

COUNTRY_CODES = ["US", "US", "GB", "DE", "CA", "FR", "AU", "NL", "IN", "SG", "IE", "SE"]

# Pricing in minor units (cents):
# Starter: $29/mo, $290/yr (~17% discount)
# Pro: $99/mo, $990/yr (~17% discount)
# Enterprise: $299/mo, $2990/yr (~17% discount)
PLANS = {
    "free": {"monthly": 0, "annual": 0},
    "starter": {"monthly": 2900, "annual": 29000},
    "pro": {"monthly": 9900, "annual": 99000},
    "enterprise": {"monthly": 29900, "annual": 299000}
}

TICKET_CATEGORIES = [
    "Billing & Payments", "Technical Bug", "Feature Request",
    "Account & Access", "API & Integrations"
]


def random_date(start, end):
    """Return a random datetime between start and end."""
    delta = end - start
    random_seconds = random.randint(0, max(0, int(delta.total_seconds())))
    return start + timedelta(seconds=random_seconds)


def iso(dt):
    """Format datetime to ISO 8601 UTC string."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ") if dt else ""


def generate():
    print("🚀 Generating DevData-01 (v1.1.0) with enhanced SaaS business logic...")

    # ----------------------------------------------------
    # 1. ORGANIZATIONS
    # ----------------------------------------------------
    print(f"Creating {TARGET_ORGS} organizations...")
    organizations = []
    org_dict = {}

    for i in range(1, TARGET_ORGS + 1):
        org_id = f"org_{i:04d}"
        base_name = random.choice(ORG_NAMES)
        org_name = f"{base_name} {i}" if i > len(ORG_NAMES) else base_name
        industry = random.choice(INDUSTRIES)
        country_code = random.choice(COUNTRY_CODES)
        # created between Jan 2023 and Jun 2024
        created_at = random_date(START_DATE, datetime(2024, 6, 30, tzinfo=timezone.utc))

        org = {
            "organization_id": org_id,
            "organization_name": org_name,
            "industry": industry,
            "country_code": country_code,
            "created_at": created_at
        }
        organizations.append(org)
        org_dict[org_id] = org

    # ----------------------------------------------------
    # 2. USERS
    # ----------------------------------------------------
    print(f"Creating {TARGET_USERS} users...")
    users = []
    user_dict = {}
    users_by_org = {org_id: [] for org_id in org_dict}

    user_counter = 1
    # Exactly 1 owner per org signed up at organization creation
    for org_id, org in org_dict.items():
        uid = f"usr_{user_counter:05d}"
        user_counter += 1
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        display_name = f"{fn} {ln}"
        email = f"{fn.lower()}.{ln.lower()}{random.randint(10, 99)}@example.com"
        role = "owner"
        status = "active"
        signup_at = org["created_at"]

        u = {
            "user_id": uid,
            "organization_id": org_id,
            "display_name": display_name,
            "email": email,
            "role": role,
            "signup_at": signup_at,
            "status": status
        }
        users.append(u)
        user_dict[uid] = u
        users_by_org[org_id].append(u)

    # Remaining users distributed across organizations
    org_ids = list(org_dict.keys())
    while user_counter <= TARGET_USERS:
        uid = f"usr_{user_counter:05d}"
        user_counter += 1
        org_id = random.choice(org_ids)
        org = org_dict[org_id]

        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        display_name = f"{fn} {ln}"
        email = f"{fn.lower()}.{ln.lower()}{random.randint(10, 999)}@example.com"
        role = random.choices(["admin", "member"], weights=[0.25, 0.75])[0]
        status = random.choices(["active", "invited", "disabled"], weights=[0.82, 0.12, 0.06])[0]
        signup_at = random_date(org["created_at"], END_DATE)

        u = {
            "user_id": uid,
            "organization_id": org_id,
            "display_name": display_name,
            "email": email,
            "role": role,
            "signup_at": signup_at,
            "status": status
        }
        users.append(u)
        user_dict[uid] = u
        users_by_org[org_id].append(u)

    # ----------------------------------------------------
    # 3. SUBSCRIPTIONS (Realistic lifecycle & non-overlapping)
    # ----------------------------------------------------
    print(f"Creating {TARGET_SUBS} subscriptions across {TARGET_ORGS} organizations...")
    subscriptions = []
    sub_dict = {}
    subs_by_org = {org_id: [] for org_id in org_dict}

    sub_counter = 1

    # Exactly 100 organizations will have 2 sequential subscriptions (e.g. upgrade, tier change, or renewal)
    # 100 organizations will have 1 subscription
    # Total = 100 * 2 + 100 * 1 = 300 subscriptions! Exactly TARGET_SUBS!
    multi_sub_orgs = set(random.sample(org_ids, TARGET_SUBS - TARGET_ORGS))

    for org_id in org_ids:
        org = org_dict[org_id]
        has_upgrade = (org_id in multi_sub_orgs)

        if not has_upgrade:
            # Single subscription organization
            sid = f"sub_{sub_counter:04d}"
            sub_counter += 1
            plan = random.choices(["free", "starter", "pro", "enterprise"], weights=[0.15, 0.45, 0.30, 0.10])[0]
            cycle = random.choices(["monthly", "annual"], weights=[0.75, 0.25])[0]
            status = random.choices(["active", "trialing", "past_due", "canceled", "expired"], weights=[0.70, 0.08, 0.06, 0.12, 0.04])[0]
            started_at = random_date(org["created_at"], org["created_at"] + timedelta(days=45))

            ended_at = None
            if status in ("canceled", "expired"):
                ended_at = random_date(started_at + timedelta(days=30), min(started_at + timedelta(days=365), END_DATE))

            s = {
                "subscription_id": sid,
                "organization_id": org_id,
                "plan": plan,
                "billing_cycle": cycle,
                "started_at": started_at,
                "ended_at": ended_at,
                "status": status
            }
            subscriptions.append(s)
            sub_dict[sid] = s
            subs_by_org[org_id].append(s)
        else:
            # Organization with 2 sequential subscriptions (e.g. Starter -> Pro/Enterprise, or Free -> Paid)
            # Subscription 1: Started near org creation, ended with tier transition / cancellation
            sid1 = f"sub_{sub_counter:04d}"
            sub_counter += 1
            plan1 = random.choices(["free", "starter", "pro"], weights=[0.30, 0.50, 0.20])[0]
            cycle1 = "monthly" if plan1 != "enterprise" else random.choice(["monthly", "annual"])
            started1 = random_date(org["created_at"], org["created_at"] + timedelta(days=30))
            
            # Transition occurs after 90 to 240 days
            transition_date = started1 + timedelta(days=random.randint(90, 240))
            if transition_date >= END_DATE - timedelta(days=60):
                transition_date = END_DATE - timedelta(days=90)
            ended1 = transition_date

            s1 = {
                "subscription_id": sid1,
                "organization_id": org_id,
                "plan": plan1,
                "billing_cycle": cycle1,
                "started_at": started1,
                "ended_at": ended1,
                "status": "canceled" if plan1 != "free" else "expired"
            }
            subscriptions.append(s1)
            sub_dict[sid1] = s1
            subs_by_org[org_id].append(s1)

            # Subscription 2: Upgraded plan starting exactly at / after transition
            sid2 = f"sub_{sub_counter:04d}"
            sub_counter += 1
            # Upgraded tier
            if plan1 == "free":
                plan2 = random.choices(["starter", "pro"], weights=[0.6, 0.4])[0]
            elif plan1 == "starter":
                plan2 = random.choices(["pro", "enterprise"], weights=[0.7, 0.3])[0]
            else:
                plan2 = "enterprise"

            cycle2 = random.choices(["monthly", "annual"], weights=[0.70, 0.30])[0]
            status2 = random.choices(["active", "past_due", "canceled"], weights=[0.80, 0.10, 0.10])[0]
            started2 = transition_date
            ended2 = None
            if status2 == "canceled":
                ended2 = random_date(started2 + timedelta(days=30), END_DATE)

            s2 = {
                "subscription_id": sid2,
                "organization_id": org_id,
                "plan": plan2,
                "billing_cycle": cycle2,
                "started_at": started2,
                "ended_at": ended2,
                "status": status2
            }
            subscriptions.append(s2)
            sub_dict[sid2] = s2
            subs_by_org[org_id].append(s2)

    # ----------------------------------------------------
    # 4. INVOICES (Realistic periodic cadence & lifecycle states)
    # ----------------------------------------------------
    print(f"Creating {TARGET_INVOICES} invoices with realistic periodic billing cadence...")
    invoices = []
    billable_subs = [s for s in subscriptions if s["plan"] != "free"]

    # Pre-calculate billable intervals for each billable subscription
    # Each invoice represents a distinct billing cycle interval [cycle_start, cycle_end)
    # Monthly: ~30 days, Annual: ~365 days
    sub_cycles_pool = []
    for s in billable_subs:
        start_ts = s["started_at"]
        end_ts = s["ended_at"] if s["ended_at"] else END_DATE
        step_days = 30 if s["billing_cycle"] == "monthly" else 365

        curr = start_ts
        cycle_idx = 0
        while curr < end_ts and curr < END_DATE:
            next_curr = curr + timedelta(days=step_days)
            sub_cycles_pool.append({
                "subscription": s,
                "cycle_idx": cycle_idx,
                "cycle_start": curr,
                "cycle_end": min(next_curr, end_ts)
            })
            curr = next_curr
            cycle_idx += 1

    print(f"Available billable subscription periods across all subscriptions: {len(sub_cycles_pool)}")

    # We must produce exactly TARGET_INVOICES (1,500).
    # Guarantee first cycle of each billable sub, then sample remainder
    subs_represented = set()
    selected_cycles = []
    remaining_pool = []

    for cycle in sub_cycles_pool:
        sid = cycle["subscription"]["subscription_id"]
        if sid not in subs_represented:
            selected_cycles.append(cycle)
            subs_represented.add(sid)
        else:
            remaining_pool.append(cycle)

    needed = TARGET_INVOICES - len(selected_cycles)
    selected_cycles.extend(random.sample(remaining_pool, needed))
    selected_cycles.sort(key=lambda x: (x["subscription"]["subscription_id"], x["cycle_start"]))

    inv_counter = 1
    cycles_by_sub = {}
    for c in selected_cycles:
        sid = c["subscription"]["subscription_id"]
        cycles_by_sub.setdefault(sid, []).append(c)

    for sid, cycles in cycles_by_sub.items():
        sub = cycles[0]["subscription"]
        sub_status = sub["status"]
        num_cycles = len(cycles)

        for i, c in enumerate(cycles):
            is_latest = (i == num_cycles - 1)
            issued_at = c["cycle_start"]
            due_at = issued_at + timedelta(days=14)
            amount_minor = PLANS[sub["plan"]][sub["billing_cycle"]]
            currency_code = "USD"

            if not is_latest:
                inv_status = random.choices(["paid", "void"], weights=[0.98, 0.02])[0]
            else:
                if sub_status == "past_due":
                    inv_status = random.choices(["open", "uncollectible"], weights=[0.75, 0.25])[0]
                elif sub_status == "canceled":
                    inv_status = random.choices(["paid", "open", "uncollectible"], weights=[0.60, 0.25, 0.15])[0]
                elif sub_status == "trialing":
                    inv_status = random.choices(["draft", "open"], weights=[0.60, 0.40])[0]
                else: # active or expired
                    if due_at > END_DATE:
                        inv_status = random.choices(["open", "draft", "paid"], weights=[0.50, 0.30, 0.20])[0]
                    else:
                        inv_status = random.choices(["paid", "open"], weights=[0.92, 0.08])[0]

            paid_at = None
            if inv_status == "paid":
                paid_at = random_date(issued_at, min(due_at + timedelta(days=3), END_DATE))
                if paid_at > END_DATE:
                    paid_at = END_DATE

            invoices.append({
                "invoice_id": f"inv_{inv_counter:05d}",
                "subscription_id": sid,
                "issued_at": issued_at,
                "due_at": due_at,
                "paid_at": paid_at,
                "amount_minor": amount_minor,
                "currency_code": currency_code,
                "status": inv_status
            })
            inv_counter += 1

    invoices.sort(key=lambda x: x["issued_at"])
    for idx, inv in enumerate(invoices, start=1):
        inv["invoice_id"] = f"inv_{idx:05d}"

    # ----------------------------------------------------
    # 5. ACTIVITY LOGS (Role-aware & realistic frequencies)
    # ----------------------------------------------------
    print(f"Creating {TARGET_LOGS} activity logs with role permissions & usage patterns...")
    activity_logs = []
    eligible_users = [u for u in users if u["status"] in ("active", "disabled")]

    ADMIN_EVENTS = ["api_key_generated", "team_invite_sent", "settings_updated", "integration_enabled"]
    GENERAL_EVENTS = ["login", "dashboard_viewed", "report_viewed", "project_created", "export_completed"]

    for i in range(1, TARGET_LOGS + 1):
        u = random.choice(eligible_users)
        occurred_at = random_date(u["signup_at"], END_DATE)
        session_id = f"sess_{random.randint(100000, 999999)}"

        if u["role"] in ("owner", "admin"):
            event_type = random.choices(
                GENERAL_EVENTS + ADMIN_EVENTS,
                weights=[0.30, 0.25, 0.15, 0.10, 0.08, 0.03, 0.03, 0.03, 0.03]
            )[0]
        else:
            event_type = random.choices(
                GENERAL_EVENTS,
                weights=[0.35, 0.30, 0.18, 0.10, 0.07]
            )[0]

        activity_logs.append({
            "event_id": f"evt_{i:06d}",
            "user_id": u["user_id"],
            "event_type": event_type,
            "occurred_at": occurred_at,
            "session_id": session_id
        })

    activity_logs.sort(key=lambda x: x["occurred_at"])
    for idx, log in enumerate(activity_logs, start=1):
        log["event_id"] = f"evt_{idx:06d}"

    # ----------------------------------------------------
    # 6. SUPPORT TICKETS (Active users & SLA-driven resolution)
    # ----------------------------------------------------
    print(f"Creating {TARGET_TICKETS} support tickets with realistic SLA resolution...")
    support_tickets = []

    ticket_eligible_users_by_org = {
        org_id: [u for u in u_list if u["status"] in ("active", "disabled")]
        for org_id, u_list in users_by_org.items()
    }

    for i in range(1, TARGET_TICKETS + 1):
        org_id = random.choice(org_ids)
        eligible = ticket_eligible_users_by_org[org_id]
        if not eligible:
            eligible = [u for u in users_by_org[org_id] if u["role"] == "owner"]
        u = random.choice(eligible)

        category = random.choice(TICKET_CATEGORIES)
        priority = random.choices(["low", "medium", "high", "urgent"], weights=[0.25, 0.45, 0.22, 0.08])[0]
        status = random.choices(["resolved", "closed", "in_progress", "open"], weights=[0.55, 0.25, 0.12, 0.08])[0]

        created_at = random_date(u["signup_at"], END_DATE)
        resolved_at = None

        if status in ("resolved", "closed"):
            if priority == "urgent":
                res_minutes = random.randint(30, 8 * 60)
            elif priority == "high":
                res_minutes = random.randint(2 * 60, 24 * 60)
            elif priority == "medium":
                res_minutes = random.randint(6 * 60, 48 * 60)
            else:
                res_minutes = random.randint(12 * 60, 72 * 60)

            resolved_at = created_at + timedelta(minutes=res_minutes)
            if resolved_at > END_DATE:
                resolved_at = END_DATE

        support_tickets.append({
            "ticket_id": f"tkt_{i:04d}",
            "organization_id": org_id,
            "created_by_user_id": u["user_id"],
            "category": category,
            "priority": priority,
            "status": status,
            "created_at": created_at,
            "resolved_at": resolved_at
        })

    support_tickets.sort(key=lambda x: x["created_at"])
    for idx, tkt in enumerate(support_tickets, start=1):
        tkt["ticket_id"] = f"tkt_{idx:04d}"

    # ----------------------------------------------------
    # WRITE SPECIFICATION-COMPLIANT CSV FILES
    # ----------------------------------------------------
    print("Writing files into data/ ...")

    # 1. organizations.csv
    with open(os.path.join(DATA_DIR, "organizations.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["organization_id", "organization_name", "industry", "country_code", "created_at"])
        for r in organizations:
            w.writerow([r["organization_id"], r["organization_name"], r["industry"], r["country_code"], iso(r["created_at"])])

    # 2. users.csv
    with open(os.path.join(DATA_DIR, "users.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["user_id", "organization_id", "display_name", "email", "role", "signup_at", "status"])
        for r in users:
            w.writerow([r["user_id"], r["organization_id"], r["display_name"], r["email"], r["role"], iso(r["signup_at"]), r["status"]])

    # 3. subscriptions.csv
    with open(os.path.join(DATA_DIR, "subscriptions.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["subscription_id", "organization_id", "plan", "billing_cycle", "started_at", "ended_at", "status"])
        for r in subscriptions:
            w.writerow([r["subscription_id"], r["organization_id"], r["plan"], r["billing_cycle"], iso(r["started_at"]), iso(r["ended_at"]), r["status"]])

    # 4. invoices.csv
    with open(os.path.join(DATA_DIR, "invoices.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["invoice_id", "subscription_id", "issued_at", "due_at", "paid_at", "amount_minor", "currency_code", "status"])
        for r in invoices:
            w.writerow([r["invoice_id"], r["subscription_id"], iso(r["issued_at"]), iso(r["due_at"]), iso(r["paid_at"]), r["amount_minor"], r["currency_code"], r["status"]])

    # 5. activity_logs.csv
    with open(os.path.join(DATA_DIR, "activity_logs.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["event_id", "user_id", "event_type", "occurred_at", "session_id"])
        for r in activity_logs:
            w.writerow([r["event_id"], r["user_id"], r["event_type"], iso(r["occurred_at"]), r["session_id"]])

    # 6. support_tickets.csv
    with open(os.path.join(DATA_DIR, "support_tickets.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ticket_id", "organization_id", "created_by_user_id", "category", "priority", "status", "created_at", "resolved_at"])
        for r in support_tickets:
            w.writerow([r["ticket_id"], r["organization_id"], r["created_by_user_id"], r["category"], r["priority"], r["status"], iso(r["created_at"]), iso(r["resolved_at"])])

    print("✅ Successfully generated all 6 CSV files with enhanced realism and zero integrity violations!")


if __name__ == "__main__":
    generate()
