---
title: Your RAG Retrieves Correct Documents but Gives the Wrong Answer
category: Agentic RAG / RAG Debugging / LLM Reliability
difficulty: Advanced
description: Debug a RAG pipeline after retrieval by tracing evidence, context assembly, prompts, reasoning, token limits, and grounding validation.
---

## Question

**Your RAG retrieves the correct documents, but the LLM still gives the wrong answer. How would you debug it?**

## Answer

I would **not immediately change the embedding model or retrieval algorithm**, because the correct documents were already retrieved. I would trace the post-retrieval pipeline:

```text
Retrieved Documents -> Chunk Selection / Reranking -> Context Construction
                    -> Prompt -> LLM -> Output -> Grounding / Validation
```

The core question is: **at which stage did the correct evidence stop influencing the final answer?**

## 1. Verify “Correct Documents” Means Sufficient Evidence

A relevant document is not necessarily a document containing the exact evidence required for the answer. If a configuration guide is retrieved but the relevant timeout value is absent from the selected chunk, the model can still hallucinate.

Check document relevance, evidence completeness, and evidence correctness.

## 2. Inspect the Exact Context Sent to the LLM

Do not only inspect search results. Log the full payload reaching the model: user query, retrieved IDs, reranked IDs, final context, system prompt, user prompt, model, token use, and output.

```json
{
  "query": "What is the test standard?",
  "retrieved_docs": ["doc_17", "doc_42", "doc_91"],
  "reranked_docs": ["doc_42", "doc_17"],
  "final_context": "...actual text sent to model..."
}
```

The context-building layer may accidentally drop, truncate, transform, or replace the evidence.

## 3. Check Chunking, Reranking, and Context Order

The right document may be split across chunks. Inspect chunk size and overlap, parent-child relations, neighboring chunks, tables, headings, and metadata. Then compare initial retrieval ranking, reranked ranking, and final context: a reranker can remove the one chunk containing the answer.

Test the strongest evidence first, last, isolated, and alongside competing documents. Large language models can use context unevenly; an answer that changes under these tests indicates a context-utilization problem.

## 4. Resolve Conflicting or Outdated Sources

Both documents can be relevant while disagreeing:

```text
Document A: Timeout = 30 seconds
Document B: Timeout = 60 seconds
```

Store `document_id`, source, created/updated date, version, document type, and authority. Use a source policy such as `current approved policy > old policy > draft`. The model should not select whichever statement merely sounds plausible.

## 5. Validate Prompt, History, and Token Budget

The system prompt should require the model to use supplied context as source of truth, avoid unsupported inferences, report insufficient evidence, cite sources, and resolve conflicts by authority and version.

Run an isolation test with a minimal context. If the context says “The timeout is 60 seconds” but the model still answers 30 seconds, the issue is not retrieval; inspect prompt contamination, hidden instructions, incorrect injection, model behavior, and application state.

Compare a fresh conversation with an existing one: prior conversation can override correct current context. Also log retrieved tokens, final-context tokens, prompt and output tokens, model limit, and truncation behavior. More `top-K` documents do not automatically improve answers.

## 6. Separate Reasoning Failures from Retrieval Failures

Sometimes the answer requires combining evidence. For example, one document specifies three validation stages and another says stage two is skipped for manual workflows. Test the model with the exact context separately. A consistent failure indicates reasoning or task-formulation issues, not a retrieval failure.

For factual RAG, compare model, temperature, output limit, reasoning configuration, and prompt across repeated runs. Temperature zero reduces variation but is not a complete hallucination solution.

## 7. Add Grounding and Citation Validation

Do not rely only on generated text. Validate whether the answer is supported by cited evidence before returning it.

```text
LLM Answer -> Grounding Validator -> Supported: return
                                -> Unsupported: regenerate or escalate
```

Use an LLM judge carefully alongside rule-based checks, citation validation, and human review for high-value workflows. A judge is useful evidence, not absolute truth.

## Production Trace and Decision Tree

Use one `trace_id` across intent classification, retrieval, document IDs and scores, reranking, final context, prompt, model call, tokens, output, and grounding validation. This reveals exactly where evidence was lost.

```text
Correct documents retrieved?
  No  -> retrieval problem
  Yes -> sufficient evidence in chunks?
           No  -> chunking / document problem
           Yes -> evidence reaches final context?
                    No  -> reranking / context assembly
                    Yes -> context truncated? prompt correct? history interfering?
                             -> reasoning and grounding validation
```

## Production Fixes

| Problem | Fix |
|---|---|
| Relevant chunk incomplete | Improve chunking and overlap |
| Reranker drops evidence | Tune reranking and top-K |
| Conflicting sources | Authority and version ranking |
| Context too large or truncated | Compression and token budgeting |
| Weak instructions | Structured prompt with citations |
| History contamination | Better state management |
| Unsupported answer | Grounding validation, regeneration, or escalation |

## Strong Interview Answer

> **“If RAG retrieves correct documents but gives a wrong answer, I would stop debugging embeddings first and trace everything after retrieval. I would verify the documents contain sufficient evidence, inspect the exact chunks and final context passed to the LLM, then check reranking, chunking, assembly, conflicts, truncation, and conversation history. I would ensure the prompt requires evidence-grounded answers and reproduce the problem with a controlled context-only test. Finally, I would add grounding and citation validation so unsupported answers are blocked before reaching the user. A trace ID across retrieval, reranking, final context, model call, and validation identifies where the evidence was lost or ignored.”**

## Key Takeaways

1. Correct retrieval does not guarantee a correct answer.
2. Verify sufficient evidence, not merely relevant documents.
3. Inspect the exact context passed to the LLM.
4. Check chunking, reranking, context assembly, conflicts, history, and truncation.
5. Isolate generation with a controlled context-only test.
6. Add grounding/citation validation and end-to-end tracing.
