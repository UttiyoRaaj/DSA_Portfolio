---
title: How Do You Debug an Agent Choosing the Wrong Tool?
category: Production Agent Design
difficulty: Hard
description: A production debugging approach for incorrect tool selection using agent traces, tool schemas, prompts, routing logic, evaluation, and observability.
---

## Question

Suppose an agent chooses the **wrong tool** even though the correct tool exists. Where would you debug the problem?

## Short Answer

I would debug the **entire tool-selection pipeline**, not just the LLM.

The main checkpoints are:

```text
User Request
     ↓
Prompt / Instructions
     ↓
Available Tool Definitions
     ↓
Tool Schema / Descriptions
     ↓
LLM Tool Selection
     ↓
Router / Orchestrator
     ↓
Tool Execution
     ↓
Observation / Feedback
```

The first question is:

> **Did the LLM choose the wrong tool, or did the system incorrectly present/route the tools?**

---

# Core Idea

Suppose we have:

```text
Tool 1: get_customer_profile()
Tool 2: get_customer_orders()
```

User asks:

```text
"What orders did customer 123 place?"
```

But the agent chooses:

```text
get_customer_profile(123)
```

There are several possible causes:

```text
                    Wrong Tool
                       |
       +---------------+----------------+
       |               |                |
       v               v                v
 Tool Definition    Prompt/Context    Model Decision
       |               |                |
 Poor description   Confusing rules   Reasoning/tool
 Wrong schema       Too many tools    selection error
 Missing examples   Bad instructions  hallucination
       |
       v
 Router / Framework
       |
 Incorrect filtering
 Incorrect routing
```

So don't immediately conclude:

> "The LLM is bad."

---

# 1. First Check the Agent Trace 🔴

In production, the **first place I would look is the agent trace**.

You want to reconstruct:

```text
Request
   ↓
Prompt sent to model
   ↓
Tools available to model
   ↓
Model response
   ↓
Selected tool
   ↓
Arguments
   ↓
Tool result
   ↓
Next model decision
```

For example:

```text
Trace ID: 8f72a1

User:
"What orders did customer 123 place?"

Available tools:
- get_customer_profile
- get_customer_orders
- cancel_order

LLM decision:
get_customer_profile(customer_id=123)

Result:
Customer profile returned
```

Now we know:

**The model actually selected the wrong tool.**

That's different from a routing bug.

---

# 2. Verify Which Tools Were Actually Available

This is an extremely important debugging step.

The correct tool might exist in the application but **not actually have been provided to the LLM**.

Application:

```text
20 tools registered
```

But model request:

```text
5 tools supplied
```

If:

```text
get_customer_orders()
```

wasn't included in the model's tool list, the LLM couldn't select it.

Check:

```text
Tool registry
      ↓
Tool filtering
      ↓
Permission filtering
      ↓
Agent-specific tools
      ↓
Tools actually sent to LLM
```

This is particularly important in enterprise agents where tools may be dynamically selected based on:

- user role
- project
- tower
- permissions
- agent type
- task
- environment

---

# 3. Check the Tool Description

LLMs primarily understand tools through their **names, descriptions, schemas and instructions**.

Bad:

```python
@tool
def customer_data(id):
    """Get customer information."""
```

The model may not know whether this means:

```text
profile?
orders?
payments?
address?
```

Better:

```python
@tool
def get_customer_orders(customer_id: str):
    """
    Retrieve the customer's historical orders.

    Use this tool when the user asks about:
    - orders
    - purchases
    - order history
    - previously purchased products

    Do not use this tool for customer profile information.
    """
```

The tool description acts almost like an **API contract for the LLM**.

---

# 4. Check Tool Names

Tool names matter too.

Compare:

```text
customer_data()
customer_orders()
```

versus:

```text
get_customer_profile()
get_customer_order_history()
```

The second version provides a much stronger semantic signal.

### Production principle

> **Design tool names and descriptions for both humans and models.**

---

# 5. Check the Tool Schema

Suppose:

```text
get_customer_data(customer_id)
```

returns everything:

```json
{
  "profile": {...},
  "orders": [...],
  "payments": [...]
}
```

This creates ambiguity.

Instead:

```text
get_customer_profile()
get_customer_orders()
get_customer_payments()
```

with focused schemas.

This is called **tool granularity**.

Too broad:

```text
do_customer_operation()
```

Too fragmented:

```text
get_customer_order_id()
get_customer_order_date()
get_customer_order_status()
...
```

You want tools with **clear responsibilities**.

---

# 6. Check System Prompt / Agent Instructions

Suppose the system prompt says:

```text
Use customer_data whenever customer information is required.
```

But your tool list contains:

```text
get_customer_profile()
get_customer_orders()
```

The model has conflicting instructions.

Instead:

```text
Use get_customer_profile for profile information.

Use get_customer_orders for order history.

Never use get_customer_profile to answer questions
about historical orders.
```

For critical routing rules, explicit instructions and examples can significantly improve consistency.

---

# 7. Check Few-Shot Examples

If tool selection is complex, provide examples.

```text
User:
"What is John's email?"

Tool:
get_customer_profile

User:
"What did John order last month?"

Tool:
get_customer_orders

User:
"How much did John spend?"

Tool:
get_customer_orders
```

These examples establish the intended mapping:

```text
Intent → Tool
```

---

# 8. Check Tool Overlap

A very common production problem is **overlapping tools**.

Example:

```text
search_customer()
get_customer_profile()
find_customer()
lookup_customer()
```

The model sees several tools that appear capable of answering:

```text
"Tell me about customer 123."
```

This increases ambiguity.

A better design might be:

```text
get_customer_profile()
search_customer()
```

with clearly defined responsibilities:

```text
search_customer()
→ Find a customer by name/email/phone.

get_customer_profile()
→ Retrieve details for a known customer ID.
```

---

# 9. Check the Router Before the LLM

Sometimes the LLM isn't the problem.

You may have:

```text
User
 ↓
Intent Classifier
 ↓
Tool Router
 ↓
Agent
```

Suppose:

```text
User:
"What orders did customer 123 place?"
```

Classifier incorrectly produces:

```text
intent = CUSTOMER_PROFILE
```

Then the router gives the agent:

```text
get_customer_profile
```

The agent choosing it is now understandable.

Debug:

```text
Input
 ↓
Intent classification
 ↓
Routing decision
 ↓
Tool set
 ↓
LLM
```

---

# 10. Check Permission / Tool Filtering

In enterprise systems, tools may be dynamically filtered.

Example:

```text
User
  ↓
RBAC
  ↓
Available tools
```

User has:

```text
customer.profile.read = true
customer.orders.read = false
```

Then:

```text
get_customer_profile → available
get_customer_orders → unavailable
```

The model chooses profile because that's the only relevant tool it can see.

This is not an LLM reasoning problem.

It is a **tool authorization/configuration problem**.

---

# 11. Check Model Tool-Calling Behavior

If everything above is correct:

```text
Correct tools available
Correct descriptions
Correct schemas
Correct prompt
Correct routing
```

but the model still repeatedly selects the wrong tool, then investigate the model decision itself.

Check:

- model version
- temperature
- tool-calling configuration
- structured output configuration
- context size
- prompt changes
- tool ordering
- model-specific behavior

For deterministic enterprise tool routing, keep randomness low where appropriate.

But don't assume:

> temperature = 0 → perfect tool selection.

It doesn't guarantee correctness.

---

# 12. Check Tool Ordering and Context

If an agent has:

```text
50 tools
```

tool selection becomes harder.

Instead of exposing everything:

```text
Agent
 ├── Tool 1
 ├── Tool 2
 ├── ...
 └── Tool 50
```

use hierarchical routing:

```text
User
 ↓
Domain Router
 ├── Customer Agent
 │     ├── Profile
 │     ├── Orders
 │     └── Payments
 │
 ├── Support Agent
 └── Billing Agent
```

This reduces the candidate tool space.

---

# 13. Add Tool-Selection Evaluation

Don't wait for production users to discover routing problems.

Create an evaluation dataset:

```text
Question                         Expected Tool
------------------------------------------------
"What is John's email?"          profile
"What did John order?"           orders
"Cancel order 123"               cancel_order
"Show John's payment history"    payments
```

Then measure:

```text
Tool Selection Accuracy
= Correct Tool Selections
  -----------------------
    Total Test Cases
```

You can also track:

```text
Top-1 tool accuracy
Wrong-tool rate
Invalid tool-call rate
Argument accuracy
Fallback rate
```

---

# 14. Use Observability / Langfuse

For your stack, I'd instrument the complete trace in **Langfuse** or a similar observability platform.

Example:

```text
Trace
│
├── User Input
│
├── Agent Prompt
│
├── Available Tools
│
├── LLM Generation
│     └── selected_tool = get_customer_profile
│
├── Tool Execution
│
├── Tool Result
│
└── Final Response
```

Add metadata:

```json
{
  "agent": "CustomerAgent",
  "model": "gpt-...",
  "selected_tool": "get_customer_profile",
  "expected_tool": "get_customer_orders",
  "tool_count": 8,
  "iteration": 1,
  "latency_ms": 820
}
```

Now you can analyze:

```text
Which tools are frequently confused?
Which prompts cause failures?
Which model version has higher wrong-tool rate?
Which agent has the highest routing error?
```

---

# 15. Create a Tool Confusion Matrix

This is particularly useful for production debugging.

Example:

| Expected | Selected | Count |
|---|---|---:|
| `get_customer_orders` | `get_customer_profile` | 42 |
| `get_customer_orders` | `search_customer` | 17 |
| `get_customer_profile` | `search_customer` | 8 |
| `cancel_order` | `get_customer_orders` | 3 |

Now you immediately see:

```text
orders ↔ profile
```

is a major ambiguity.

That suggests improving:

- tool descriptions
- tool names
- examples
- routing
- tool boundaries

rather than blindly changing the model.

---

# 16. Add a Tool-Selection Guard

For critical workflows, introduce a validation layer.

```text
                 Agent
                   |
                   v
            Selected Tool
                   |
                   v
           +---------------+
           | Tool Validator |
           +-------+-------+
                   |
          Is tool appropriate?
             /          \
           YES           NO
            |             |
            v             v
        Execute       Re-plan / Reject
```

Example:

```text
User intent:
ORDER_HISTORY

Selected:
get_customer_profile

Validator:
❌ Tool incompatible with intent

Action:
Ask agent to re-plan
```

This provides a second line of defense.

---

# Production Debugging Flow 🔴

When I encounter a wrong-tool incident, I would debug in this order:

```text
1. Capture trace
       ↓
2. What tool did the model select?
       ↓
3. Was correct tool actually available?
       ↓
4. Was it filtered by RBAC/router?
       ↓
5. Check tool name + description
       ↓
6. Check schema and parameters
       ↓
7. Check system prompt
       ↓
8. Check few-shot examples
       ↓
9. Check overlapping tools
       ↓
10. Check model/configuration
       ↓
11. Reproduce with evaluation case
       ↓
12. Add guardrail if workflow is critical
```

---

# Real-Life Example — TCOE Agentic AI Platform

Suppose your **ADO Agent** needs to retrieve a user story.

You have:

```text
get_ado_story()
search_ado_stories()
get_ado_comments()
get_ado_attachments()
```

User request:

```text
"Get the acceptance criteria for ADO-1234."
```

Expected:

```text
get_ado_story("ADO-1234")
```

But agent chooses:

```text
search_ado_stories("ADO-1234")
```

### Debugging

Trace shows:

```text
User Request
     ↓
ADO Agent
     ↓
Tools Available
     ↓
search_ado_stories
get_ado_story
get_ado_comments
...
     ↓
LLM
     ↓
search_ado_stories
```

Then inspect description:

```text
search_ado_stories:
"Search ADO stories using a query."
```

```text
get_ado_story:
"Get an ADO story."
```

Both are somewhat ambiguous.

Improve them:

```text
search_ado_stories:
"Search for multiple ADO stories when the exact story ID
is unknown."

get_ado_story:
"Retrieve one specific ADO story using its exact ID,
such as ADO-1234. Use this when the user provides a
specific story ID."
```

Add examples:

```text
ADO-1234
→ get_ado_story

"Find stories related to login"
→ search_ado_stories
```

Then evaluate again.

---

# Interview-Ready Answer 🔴

> **"I would start with the agent trace and determine whether the correct tool was actually available to the model. Then I'd inspect the tool descriptions, names, schemas, system prompt, examples and any router or permission-based tool filtering. I'd also look for overlapping tools that create ambiguity. If all of those are correct, I'd investigate the model's tool-calling behavior and configuration. In production I'd instrument tool-selection traces with something like Langfuse and track metrics such as wrong-tool rate and a tool-confusion matrix. For critical workflows, I'd add a tool-selection validator that can reject an incompatible tool and force the agent to re-plan."**

### Strong closing line:

> **"The key is to debug tool selection as a pipeline—availability, routing, tool metadata, prompt, model decision, and execution—not simply blame the LLM."**

---

## Quick Revision

```text
Wrong Tool
    ↓
TRACE
    ↓
Was correct tool available?
    ↓
YES
    ↓
Router / RBAC correct?
    ↓
YES
    ↓
Tool name + description + schema?
    ↓
Prompt + examples?
    ↓
Tool overlap?
    ↓
Model/configuration?
    ↓
Evaluate + reproduce
    ↓
Guardrail if required
```

### Mental Model

> **Observe → Verify availability → Inspect tool metadata → Inspect routing/prompt → Analyze model choice → Evaluate → Add guardrail.**