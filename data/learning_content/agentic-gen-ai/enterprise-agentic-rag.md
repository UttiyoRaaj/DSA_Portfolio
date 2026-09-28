---
title: Design an Enterprise Agentic RAG System
category: Agentic AI Architecture / Agentic RAG
difficulty: Advanced
description: Design a RAG system that decides whether to retrieve, selects an authoritative source, evaluates evidence, and stops within bounded limits.
---

## Question

**Design an enterprise Agentic RAG system where the agent must decide whether to retrieve, which source to query, and when to stop.**

## Answer

A traditional RAG pipeline is fixed:

```text
User Query -> Retrieve Documents -> Generate Answer
```

An **Agentic RAG** system puts retrieval inside a controlled decision loop:

```text
User Query -> Understand Intent -> Should I Retrieve?
                                      | No  -> Generate Response
                                      | Yes -> Select Knowledge Source -> Retrieve
                                                 -> Evaluate Evidence
                                                    | sufficient   -> Generate Answer
                                                    | insufficient -> Select another source / loop
```

> **Retrieval becomes an agentic decision rather than a mandatory first step.**

The agent must decide: whether retrieval is required, which source or sources should be queried, and whether the evidence is sufficient to stop.

## High-Level Enterprise Architecture

```text
User Query -> Query Understanding + Intent Detection -> Retrieval Decision Agent
                                                           | no  -> LLM Response
                                                           | yes -> Source Selection Agent
                                                                      | Azure AI Search (vector + BM25)
                                                                      | SQL / ERP / APIs
                                                                      | SharePoint / GitHub
                                                                            -> Evidence Evaluator
                                                                               | sufficient   -> Generate Answer
                                                                               | insufficient -> query another source
```

An enterprise implementation can use LangGraph for orchestration and state, Azure AI Search for hybrid retrieval, Azure OpenAI for reasoning, APIs for structured business data, Managed Identity plus RBAC for authorization, Key Vault for secrets, OpenTelemetry/Application Insights for tracing, HITL for high-risk decisions, and persistent checkpoints for long-running workflows.

## Decision 1: Should the Agent Retrieve?

The agent first classifies the query.

| User Query | Retrieve? | Reason |
|---|---|---|
| Explain dependency injection | No | General knowledge |
| What is our testing policy? | Yes | Enterprise-specific |
| What was AMI's defect rate last month? | Yes | Current internal data |
| Summarize this document | Usually | Requires the supplied document |
| What is 2 + 2? | No | Deterministic and simple |

Example structured decision:

```json
{
  "retrieve": true,
  "reason": "The question requires enterprise-specific information.",
  "required_sources": ["ADO", "KnowledgeBase"]
}
```

## Decision 2: Which Source Should Be Queried?

Select the source from the query's intent and data type—and, crucially, from its authority.

| Need | Authoritative source |
|---|---|
| Acceptance criteria and stories | ADO / DevOps |
| Testing standards and policies | Approved knowledge base / SharePoint |
| Source code and scripts | GitHub |
| Current purchase-order status | ERP / API |
| Employee information | HR system |
| Historical defects | Defect repository |

> **Do not force structured data through vector search when an authoritative API or SQL query exists.**

For unstructured enterprise knowledge, use hybrid retrieval: BM25 for exact business terms, vector search for semantic similarity, semantic ranking for context, then optional LLM reranking. An example weighting is `0.3 * BM25 + 0.4 * vector + 0.3 * semantic`.

## Decision 3: Is the Evidence Sufficient?

After each retrieval, evaluate whether the context answers the actual question, contains enough evidence, comes from an authoritative source, and has sufficient confidence.

```json
{
  "sufficient": false,
  "confidence": 0.54,
  "missing_information": ["Historical defect information"],
  "next_source": "DefectRepository"
}
```

## When Should the Agent Stop?

Stopping conditions prevent unbounded cost and latency. Stop when required information is found, confidence exceeds the threshold, sources are authoritative, the question is fully answerable, maximum iterations are reached, no useful new information exists, or a cost/latency budget is reached.

```python
if evidence_confidence >= 0.85:
    STOP
elif iteration >= MAX_ITERATIONS:
    STOP
elif marginal_information_gain < MIN_GAIN:
    STOP
else:
    RETRIEVE_AGAIN
```

“No useful result found” can itself be a valid stopping condition.

## Example

For “Generate test cases for AMI story 123 and consider similar historical defects,” the agent identifies the required information: the ADO story, acceptance criteria, similar stories, defects, and testing standards. It retrieves the story through an ADO agent and standards through a Knowledge/Skills agent in parallel, then queries a defect repository where appropriate.

```text
Orchestrator -> ADO Search -> Story Context
             -> KB Search  -> Standards Context
                              -> Test Case Agent
```

If the story, acceptance criteria, and standards are sufficient but no relevant historic defect exists, it should stop retrieval and generate the test cases instead of searching forever.

## State and LangGraph Routing

Maintain explicit workflow state, including query, intent, retrieval requirement, checked sources, retrieved documents, evidence score, missing information, iteration count, and decision. This enables durable HITL interruptions and resume.

```python
def route_after_evaluation(state):
    if state["evidence_score"] >= 0.85:
        return "generate"
    if state["iteration"] >= state["max_iterations"]:
        return "generate_limited"
    if not state["missing_information"]:
        return "generate"
    return "retrieve_again"
```

LangGraph suits this design because it models conditional routing, state, loops, checkpoints, and parallel retrieval. The agent controls the route; the application does not blindly execute every retrieval node.

## Enterprise Guardrails

- Enforce user identity, Entra ID, RBAC, and source-level permissions before retrieval.
- Restrict sensitive sources such as HR, financial, or other-tenant data.
- Bound `MAX_ITERATIONS`, document count, token budget, latency, and cost.
- Treat retrieved documents as untrusted data, never as instructions; defend against prompt injection.

- Use HITL approval for high-risk actions and log decisions, sources, and outcomes.
## Evaluation Metrics

Evaluate retrieval with Recall@K, Precision@K, MRR, NDCG, and source relevance. Evaluate agent decisions with retrieval-decision accuracy, source-selection accuracy, stop/continue accuracy, and unnecessary-retrieval rate. Evaluate answers with groundedness, faithfulness, completeness, citation accuracy, and hallucination rate. Track latency, cost, token use, tool failures, and **average retrieval iterations per successful answer** in production.

## Strong Interview Answer

> **“I would design Agentic RAG as a controlled decision loop rather than a fixed retrieve-then-generate pipeline. The agent first decides whether enterprise knowledge is needed. If it is, it selects the appropriate authoritative source—for example ADO for requirements, a knowledge base for standards, or an ERP/API for current structured data. For unstructured sources, I would use hybrid retrieval with BM25, vector search, semantic ranking, and reranking. An evidence evaluator then checks relevance, authority, and sufficiency. The agent generates when evidence is sufficient; otherwise it chooses another source and iterates. I would bound the loop with confidence thresholds, maximum iterations, latency and cost budgets, and diminishing-information-gain checks. LangGraph fits naturally because it supports state, conditional routing, parallel retrieval, HITL, and checkpoints.”**

## Key Takeaways

1. Do not retrieve blindly for every query.
2. Select sources by intent, data type, and authority.
3. Evaluate evidence before producing the final answer.
4. Bound iteration with confidence, cost, latency, and information-gain limits.
5. Agentic RAG is: **Decide -> Retrieve -> Observe -> Evaluate -> Decide or Stop.**
