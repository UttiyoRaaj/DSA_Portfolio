---
title: Preventing Unauthorized or Destructive Tool Operations
category: Agent Security / Authorization
difficulty: Intermediate
description: How to ensure an LLM cannot bypass authorization and execute destructive tools even when explicitly instructed by a prompt.
---

## Question

**How would you prevent an LLM from performing an unauthorized or destructive tool operation even if the prompt asks it to?**

## Short Answer

**Never let the LLM itself decide whether an operation is authorized.**

The LLM can **request/propose a tool call**, but an independent authorization/policy layer must validate:

**User → Agent → Tool Request → Authorization/Policy → Tool → Result**

If the operation is unauthorized or high-risk, the policy layer rejects it regardless of what the prompt says. For destructive actions, add **human approval**. This follows least-privilege and independent authorization principles recommended by OWASP. :chatgpt-content-reference{index="0"}

---

## Core Idea

```text
User Prompt
    ↓
LLM / Agent
    ↓
"Delete customer record 123"
    ↓
Tool Authorization Layer
    ├── Is user allowed?
    ├── Is this tool allowed for this agent?
    ├── Is this resource allowed?
    ├── Is this operation destructive?
    └── Is approval required?
          ↓
      ALLOW / DENY
          ↓
      Tool Execution
```

The key principle is:

> **LLM proposes the action; application code decides whether the action is permitted.**

Do **not** rely on a system prompt such as:

```text
"Never delete production data."
```

That is useful as a behavioral instruction, but it is **not an authorization control**. OWASP specifically recommends enforcing authorization in downstream systems rather than relying on the LLM. :chatgpt-content-reference{index="1"}

---

# 1. Apply Least Privilege

Give the agent only the tools and permissions it actually needs.

For example:

```text
Customer Support Agent

Allowed:
  get_customer()
  search_orders()
  create_ticket()

Not allowed:
  delete_customer()
  change_permissions()
  execute_sql()
```

Even if the user says:

> "Delete customer 123."

The model may generate:

```json
{
  "tool": "delete_customer",
  "customerId": "123"
}
```

But the authorization layer returns:

```text
DENIED: Agent does not have delete_customer permission
```

OWASP recommends minimizing both the **number of extensions** and the **functionality/permissions** exposed to agents. :chatgpt-content-reference{index="2"}

---

# 2. Check User Authorization

The agent should operate within the user's actual permissions.

For example:

```text
User → Role → Permissions
                  ↓
            Tool Authorization
```

Suppose:

```text
User Role = Developer

Permissions:
  READ_LOGS
  READ_TEST_DB
```

The user asks:

> "Drop the production database."

Even if the LLM decides to call:

```text
database.execute("DROP DATABASE production")
```

the backend authorization layer rejects it.

```text
User: Developer
        ↓
Authorization Service
        ↓
DROP DATABASE → DENIED
```

**Never treat "the user asked for it" as equivalent to "the user is authorized to do it."**

---

# 3. Classify Tools by Risk

A practical production approach is to classify tools.

| Risk | Example | Control |
|---|---|---|
| 🟢 Low | Search documents | Automatic |
| 🟡 Medium | Create ticket | Permission check |
| 🟠 High | Send email / modify record | Permission + validation |
| 🔴 Critical | Delete data / transfer money | Permission + explicit approval |

For example:

```text
read_customer()
    → LOW

update_customer()
    → MEDIUM

send_email()
    → HIGH

delete_customer()
    → CRITICAL
```

For high-impact or irreversible actions, require explicit human approval. :chatgpt-content-reference{index="3"}

---

# 4. Human-in-the-Loop for Destructive Actions

For something like:

```text
delete_production_data()
```

the flow should be:

```text
LLM proposes deletion
        ↓
Authorization check
        ↓
Risk = CRITICAL
        ↓
Human approval required
        ↓
User sees:
  Tool: delete_customer
  Customer: 123
  Reason: requested deletion
        ↓
Approve / Reject
        ↓
Tool executes only if approved
```

The approval should be tied to the **specific action and parameters**, not just a generic "I approve" flag. OWASP recommends independent validation and approval for high-impact actions. :chatgpt-content-reference{index="4"}

---

# 5. Validate Tool Parameters

Authorization alone isn't enough.

Suppose the user is allowed to delete **test data**, but not production data.

The LLM requests:

```json
{
  "environment": "production",
  "recordId": "123"
}
```

The policy layer checks:

```text
Tool allowed?       YES
User authorized?    YES
Environment?        production
User allowed there? NO

→ DENY
```

So authorization should consider:

```text
User
+ Role
+ Tool
+ Resource
+ Operation
+ Environment
+ Parameters
```

---

# 6. Put the Security Check Outside the LLM

A good architecture is:

```text
                  ┌──────────────┐
User ────────────►│     LLM      │
                  └──────┬───────┘
                         │
                    Tool Request
                         ↓
               ┌──────────────────┐
               │ Policy / AuthZ   │
               │     Service      │
               └────────┬─────────┘
                        │
                 ALLOW / DENY
                        ↓
                 ┌────────────┐
                 │    Tool    │
                 └─────┬──────┘
                       ↓
                 Backend System
```

This is especially important for MCP-based agents: tool access, parameters and permissions should be enforced at the tool/server layer rather than trusting the model. :chatgpt-content-reference{index="5"}

---

# 7. Example: Production Database Agent

Suppose an agent has:

```text
read_database()
write_database()
delete_database_record()
```

User says:

> "Delete all customer records."

The LLM may attempt:

```text
delete_database_record()
```

But the policy engine evaluates:

```text
Agent: CustomerAgent
User: developer123
Tool: delete_database_record
Target: production
Operation: DELETE
Risk: CRITICAL
```

Result:

```text
DENIED
Reason:
User is not authorized for production deletion.
```

The database is **never called**.

That's the important distinction:

**The LLM can make a bad decision, but the bad decision must not automatically become a real-world action.**

---

# 8. Add Audit + Monitoring

Every sensitive tool invocation should be logged:

```text
traceId
userId
agentId
toolName
parameters
resource
authorization result
approval result
timestamp
execution result
```

For example:

```text
User: U123
Agent: DataAgent
Tool: delete_record
Resource: customer/456
Authorization: DENIED
Reason: insufficient privilege
```

This helps with security investigations and detecting abnormal agent behavior. :chatgpt-content-reference{index="6"}

---

# Production Pattern

Remember this:

```text
LLM
 ↓
Propose Action
 ↓
Authentication
 ↓
Authorization
 ↓
Parameter Validation
 ↓
Risk Classification
 ↓
Human Approval (if required)
 ↓
Tool Execution
 ↓
Audit + Monitoring
```

### Interview-ready answer 🔴

> **"I would never rely on the LLM to enforce authorization. The LLM can propose a tool call, but an independent policy and authorization layer validates the user identity, agent permissions, tool, resource and parameters. I would apply least privilege and expose only the tools required for that agent. Read operations can usually run automatically, while destructive or high-impact operations require explicit human approval. The tool itself should also enforce authorization, validate parameters, and log the operation. So even if a prompt injection or malicious user convinces the LLM to request a destructive operation, the backend authorization layer blocks it."**

### One-line mental model

**LLM decides *what it wants to do* → Policy decides *whether it is allowed* → Tool executes only after authorization.**