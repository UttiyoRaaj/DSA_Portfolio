---
title: RAG Deep Dive — End-to-End Production Architecture
category: Generative AI / Retrieval-Augmented Generation
difficulty: Advanced
description: A complete interview- and production-level walkthrough of Retrieval-Augmented Generation, from knowledge ingestion and chunking to embeddings, vector/hybrid retrieval, reranking, LLM generation, hallucination control, evaluation, iterative retrieval, fine-tuning, HITL, and LLM-as-a-Judge.
---

# Question

**Explain the complete RAG pipeline end-to-end — knowledge base, embeddings, tokenization, chunking, models, similarity scores, vector DB, SQL DB, hybrid search, LLM integration, hallucinations, evaluation, augmentation strategies, iterative retrieval, fine-tuning, HITL and LLM-as-a-Judge.**

---

# Short Answer

**RAG = Retrieve relevant external knowledge → Augment the LLM prompt with that knowledge → Generate a grounded answer.**

Instead of asking an LLM:

```text
User
  |
  v
LLM
  |
  v
Answer
```

we build:

```text
                         RAG
                          |
User Question ---> Retrieve ---> Relevant Knowledge
                          |             |
                          +-------------+
                                  |
                                  v
                              LLM
                                  |
                                  v
                             Grounded Answer
```

A production RAG system is considerably more than "PDF → embeddings → vector DB → LLM."

It includes:

```text
Data ingestion
      ↓
Parsing / OCR
      ↓
Cleaning
      ↓
Chunking
      ↓
Metadata enrichment
      ↓
Embedding
      ↓
Vector / Search Index
      ↓
Query understanding
      ↓
Hybrid retrieval
      ↓
Filtering
      ↓
Reranking
      ↓
Context compression
      ↓
Prompt construction
      ↓
LLM generation
      ↓
Grounding / citation validation
      ↓
Evaluation
      ↓
Human feedback
      ↓
Continuous improvement
```

Microsoft's current Azure RAG guidance similarly separates the solution into **data preparation, retrieval, and end-to-end generation/evaluation**, and emphasizes that each stage should be evaluated independently as well as end-to-end. :chatgpt-content-reference{index="0"}

---

# 1. The Running Example

Let's use an **enterprise ChatGPT-style assistant** rather than the public ChatGPT itself.

Imagine:

> **"Infosys Enterprise Assistant"**

Employees can ask:

```text
"What is the company's leave policy for employees who
have completed more than one year?"
```

The knowledge base contains:

```text
HR Policies
PDFs
Word documents
SharePoint
Confluence
FAQs
Employee handbook
Benefits documents
Internal announcements
Database records
```

We want:

```text
User
 |
 | Question
 v
Enterprise AI Assistant
 |
 +--> Search knowledge
 |
 +--> Retrieve evidence
 |
 +--> LLM
 |
 v
Answer + Citations
```

The key difference from a normal LLM:

> The answer should be based on **current enterprise data**, not merely what the model learned during training.

RAG is specifically designed to ground an LLM in proprietary or external content. :chatgpt-content-reference{index="1"}

---

# 2. Why Do We Need RAG?

An LLM has a knowledge boundary.

Suppose the model was trained before your company's:

```text
2026 Leave Policy
```

was published.

The model cannot magically know it.

Without RAG:

```text
Question
   |
   v
LLM
   |
   v
Potential hallucination
```

With RAG:

```text
Question
   |
   v
Search
   |
   v
2026 Leave Policy
   |
   v
LLM
   |
   v
Grounded Answer
```

### RAG solves mainly:

- Knowledge freshness
- Proprietary data access
- Domain-specific grounding
- Citations
- Reduced hallucination
- Data separation from model weights

---

# 3. RAG Is NOT Training

This is a very common interview question.

### RAG

```text
Documents
   ↓
Index
   ↓
Retrieve at runtime
   ↓
LLM
```

Knowledge remains outside the model.

### Fine-tuning

```text
Training Dataset
      ↓
Model Training
      ↓
Updated Model Weights
```

Knowledge/behavior becomes encoded into model parameters.

### Simple distinction

> **RAG changes the context. Fine-tuning changes the model.**

---

# 4. Complete RAG Architecture

A production architecture can look like:

```text
                           USER
                             |
                             v
                      Web / Mobile UI
                             |
                             v
                     API Gateway / BFF
                             |
                             v
                       RAG Orchestrator
                             |
                +------------+------------+
                |                         |
                v                         v
          Query Processing           Conversation
                |                    / Memory
                v
        +-------+--------+
        |                |
        v                v
   Keyword Search    Vector Search
        |                |
        +-------+--------+
                |
                v
          Hybrid Retrieval
                |
                v
             Reranker
                |
                v
         Context Selection
                |
                v
          Prompt Builder
                |
                v
              LLM
                |
        +-------+-------+
        |               |
        v               v
   Citation Check   Safety Check
        |               |
        +-------+-------+
                |
                v
          Final Response
```

Behind the retrieval layer:

```text
             KNOWLEDGE SOURCES
                    |
      +-------------+-------------+
      |             |             |
     PDF         SharePoint      SQL
      |             |             |
      +-------------+-------------+
                    |
              Ingestion Pipeline
                    |
              Parse / OCR
                    |
                Chunking
                    |
             Metadata Enrichment
                    |
                Embeddings
                    |
              Search Index
```

---

# 5. Two Completely Different RAG Phases

This distinction is critical.

## Phase A — Indexing / Offline Pipeline

Happens before the user asks questions.

```text
Documents
   ↓
Parse
   ↓
Clean
   ↓
Chunk
   ↓
Enrich
   ↓
Embed
   ↓
Index
```

## Phase B — Query / Online Pipeline

Happens when the user asks something.

```text
Question
   ↓
Query processing
   ↓
Search
   ↓
Reranking
   ↓
Context
   ↓
LLM
   ↓
Answer
```

Microsoft's Azure guidance explicitly separates the RAG data pipeline from the online application/retrieval flow. :chatgpt-content-reference{index="2"}

---

# 6. Phase A — Knowledge Base

First we need data.

Example:

```text
SharePoint
Confluence
Azure Blob
PDF
DOCX
CSV
JSON
SQL
APIs
Emails
```

Suppose:

```text
leave_policy.pdf
```

contains:

```text
Employees with more than one year of service
are eligible for 24 days of annual leave...
```

We don't directly put the entire PDF into the LLM.

We first process it.

---

# 7. Document Parsing

Different files require different processing.

```text
PDF
 ↓
PDF parser / OCR
 ↓
Text

DOCX
 ↓
Document parser
 ↓
Text

Image
 ↓
OCR / Vision model
 ↓
Text

Web page
 ↓
HTML parser
 ↓
Text
```

For scanned PDFs:

```text
PDF
 ↓
Image
 ↓
OCR
 ↓
Text
```

For tables:

```text
Table
 ↓
Structured representation
```

This is important because blindly extracting text can destroy:

- table relationships
- headings
- page structure
- columns
- captions
- metadata

Azure AI Search supports document extraction, OCR/image processing and integrated vectorization as part of content preparation. :chatgpt-content-reference{index="3"}

---

# 8. Cleaning

Raw documents contain noise.

Example:

```text
Page 1
CONFIDENTIAL

Employee Handbook

Page 2
CONFIDENTIAL

Employee Handbook
```

You don't want repeated headers polluting embeddings.

Typical cleaning:

```text
Remove:
- repeated headers
- footers
- unnecessary whitespace
- HTML noise
- duplicate content
- malformed characters
```

But be careful:

> **Don't clean away information that carries meaning.**

For example:

```text
"NOT eligible"
```

must not accidentally become:

```text
"eligible"
```

---

# 9. Tokenization

Before understanding chunking and embeddings, understand **tokens**.

An LLM doesn't necessarily process text as complete words.

Example:

```text
"unbelievable"
```

might be represented approximately as:

```text
["un", "believ", "able"]
```

The exact tokenization depends on the tokenizer/model.

Think:

```text
Text
 ↓
Tokenizer
 ↓
Token IDs
 ↓
Model
```

Example conceptually:

```text
"How does caching work?"

        ↓

[How] [does] [caching] [work] [?]

        ↓

[1523, 832, 9821, 412, 30]
```

The exact IDs are model-specific.

---

# 10. Why Tokenization Matters in RAG

Tokens affect:

### Chunk size

```text
Chunk = 500 tokens
```

versus:

```text
Chunk = 5,000 tokens
```

### Embedding limits

Embedding models have maximum input sizes.

### LLM context window

You cannot send:

```text
100,000 tokens
```

to a model with a smaller context capacity.

### Cost

More tokens:

```text
→ higher latency
→ higher cost
→ potentially more noise
```

Microsoft specifically notes that chunking helps stay within model input limits and can improve retrieval representation even when the entire document technically fits. :chatgpt-content-reference{index="4"}

---

# 11. Chunking

This is one of the **most important RAG topics**.

A 100-page document should not normally become:

```text
One giant vector
```

Instead:

```text
Document
   |
   +-- Chunk 1
   +-- Chunk 2
   +-- Chunk 3
   +-- ...
   +-- Chunk N
```

Why?

Because retrieval needs to find the **specific relevant portion**.

---

# 12. Why Chunking Is Difficult

Suppose:

```text
Chunk 1:
Employee eligibility...

Chunk 2:
Employees with >1 year...

Chunk 3:
Leave calculation...

Chunk 4:
Exceptions...
```

Question:

> "How many leave days do employees with more than one year receive?"

Chunk 2 is ideal.

But poor chunking might create:

```text
Chunk 1:
Employees with...

Chunk 2:
more than one year receive...

```

The meaning is split.

Therefore:

> **A good chunk should preserve enough semantic context to stand alone.**

---

# 13. Chunking Strategies

## A. Fixed-size chunking

```text
Every 500 tokens
```

Simple:

```text
0-500
400-900
800-1300
...
```

with overlap.

### Pros

- Simple
- Fast
- Predictable

### Cons

- Can split concepts
- Doesn't respect document structure

---

# 14. Overlapping Chunks

Suppose:

```text
Chunk size = 500
Overlap = 100
```

Then:

```text
Chunk 1 = 0–500
Chunk 2 = 400–900
Chunk 3 = 800–1300
```

Why overlap?

If an important sentence occurs near the boundary, it appears in both chunks.

```text
--------Chunk 1--------
             |
             | overlap
             v
        --------Chunk 2--------
```

Too much overlap increases:

```text
storage
embedding cost
duplicate retrieval
context noise
```

So overlap must be evaluated rather than chosen blindly.

---

# 15. Semantic Chunking

Instead of:

```text
Every 500 tokens
```

split according to meaning:

```text
Heading
   ↓
Paragraphs
   ↓
Subheading
   ↓
Related paragraphs
```

Example:

```text
1. Eligibility
   → related paragraphs

2. Leave entitlement
   → related paragraphs

3. Carry forward
   → related paragraphs
```

This is usually more semantically meaningful for structured enterprise documents.

---

# 16. Hierarchical Chunking

For complex documents:

```text
Document
 |
 +-- Section
      |
      +-- Subsection
             |
             +-- Paragraph
```

Store metadata:

```json
{
  "document": "LeavePolicy.pdf",
  "section": "Annual Leave",
  "subsection": "Eligibility",
  "page": 12,
  "chunk_id": "leave-12-03"
}
```

This becomes extremely useful for:

- filtering
- citations
- reranking
- context reconstruction

Microsoft's current RAG guidance recommends choosing chunking based on the structure of the source media rather than treating all documents identically. :chatgpt-content-reference{index="5"}

---

# 17. Metadata Enrichment

Don't store only:

```text
chunk_text
```

Store:

```text
chunk_id
document_id
title
section
page
source
created_at
updated_at
department
language
document_type
security_acl
version
summary
keywords
entities
```

Example:

```json
{
  "chunk_id": "HR-001-12",
  "document": "LeavePolicy.pdf",
  "section": "Annual Leave",
  "page": 12,
  "department": "HR",
  "version": "2026.1",
  "text": "Employees with..."
}
```

Metadata can be used for **filtering and retrieval quality**.

---

# 18. Chunk Enrichment

An advanced technique is to generate additional information for each chunk.

Original:

```text
Employees with more than one year
of service receive 24 days...
```

Enriched:

```text
Title:
Annual Leave Eligibility

Summary:
Policy for employees with >1 year service.

Keywords:
annual leave, eligibility, 1 year, 24 days
```

Then store:

```text
Original text
+
Summary
+
Keywords
+
Metadata
```

This can improve retrieval because the original chunk may not contain the exact wording users ask for.

Microsoft's RAG design guidance explicitly recommends cleaning and enriching chunks before embedding/search. :chatgpt-content-reference{index="6"}

---

# 19. Embeddings

Now we convert chunks into vectors.

Example:

```text
"Employees with more than one year receive 24 days."
```

↓

```text
Embedding Model
```

↓

```text
[0.021, -0.183, 0.721, ..., 0.092]
```

This vector represents semantic information.

---

# 20. What Is an Embedding?

An embedding is a numerical representation of text in a high-dimensional vector space.

Conceptually:

```text
                Leave
                  *
                 / \
                /   \
         PTO  *       * Vacation
```

Semantically similar text tends to be closer in the embedding space.

Example:

```text
"annual leave entitlement"
```

and:

```text
"how many vacation days do I get?"
```

can be close even though the words differ.

---

# 21. Same Embedding Model for Query and Documents

This is important.

During indexing:

```text
Chunk
 ↓
Embedding Model
 ↓
Vector
```

During query:

```text
Question
 ↓
Same / compatible embedding model
 ↓
Query Vector
```

Then compare:

```text
Query Vector
      |
      v
Vector Index
      |
      v
Nearest Chunks
```

Microsoft's Azure documentation explicitly describes embedding both document chunks and user queries and comparing them in the same vector space. :chatgpt-content-reference{index="7"}

---

# 22. Similarity Search

Now we need to measure:

> How similar is the question to each chunk?

Common metrics:

```text
Cosine similarity
Dot product
Euclidean distance
```

Azure AI Search supports cosine, dot product and Euclidean metrics; Microsoft recommends cosine for Azure OpenAI embeddings. :chatgpt-content-reference{index="8"}

---

# 23. Cosine Similarity

Conceptually:

```text
                    A · B
cosine(A,B) = ----------------
              ||A|| × ||B||
```

It measures the angle between vectors.

Conceptually:

```text
Query
  \
   \  small angle
    \
     Chunk A

Query
  \
   \
    \------ Chunk B
```

Smaller angle → greater semantic similarity.

---

# 24. Similarity Score Is NOT Probability

Very important interview point.

Suppose:

```text
Chunk A = 0.91
Chunk B = 0.87
```

You cannot automatically say:

```text
91% probability A is correct.
```

The score means something about **vector similarity**, not answer correctness.

Also:

> Similarity scores are model/index dependent and shouldn't be treated as universally calibrated probabilities.

---

# 25. Vector Database / Vector Index

We now store:

```text
chunk text
+
embedding vector
+
metadata
```

Example:

```text
Vector Store
-----------------------------------
ID | Vector | Text | Metadata
-----------------------------------
1  | [..]   | ...  | ...
2  | [..]   | ...  | ...
3  | [..]   | ...  | ...
```

Examples of technologies include:

- Azure AI Search
- PostgreSQL + pgvector
- Elasticsearch/OpenSearch
- Pinecone
- Weaviate
- Milvus
- FAISS for local/indexing use cases

For Azure enterprise architectures, Azure AI Search can combine vector and non-vector fields in the same search index. :chatgpt-content-reference{index="9"}

---

# 26. Vector Search Algorithms

A naive approach:

```text
Query
 ↓
Compare against EVERY vector
```

That's:

```text
Brute-force / exact KNN
```

Accurate but potentially expensive at scale.

A common approximate approach is:

```text
ANN
Approximate Nearest Neighbor
```

For example:

```text
HNSW
```

HNSW builds a graph-like index to find approximate nearest neighbors efficiently.

Azure AI Search supports exhaustive KNN and HNSW. :chatgpt-content-reference{index="10"}

---

# 27. SQL Database — Why Do We Still Need It?

A common misconception:

> "If we have a vector DB, why do we need SQL?"

Because vector search and transactional data solve different problems.

### SQL

Good for:

```text
Users
Orders
Transactions
Permissions
Relationships
ACID operations
```

### Vector search

Good for:

```text
Semantic similarity
Unstructured knowledge
Document retrieval
```

Production architecture:

```text
                 Application
                 /         \
                /           \
              SQL         Vector DB
               |              |
        transactions       knowledge
        users              embeddings
        permissions        chunks
        business data      metadata
```

---

# 28. SQL + RAG Example

Question:

> "What is my remaining leave?"

This may require:

```text
SQL:
employee_id = 123
remaining_leave = 12
```

and:

```text
RAG:
Company policy explaining leave calculation
```

Then:

```text
SQL -> factual employee data

RAG -> policy / explanation

LLM -> combines them
```

This is much better than putting transactional information into a vector database.

---

# 29. Query-Time Pipeline

Now the user asks:

> "How many annual leaves can I carry forward?"

Pipeline:

```text
User Query
    |
    v
Query Processing
    |
    v
Query Embedding
    |
    +--------------------+
    |                    |
    v                    v
Keyword Search       Vector Search
    |                    |
    +---------+----------+
              |
              v
        Hybrid Retrieval
              |
              v
          Reranking
              |
              v
        Top N Chunks
              |
              v
       Context Builder
              |
              v
             LLM
              |
              v
      Grounded Answer
```

---

# 30. Keyword Search vs Vector Search

Suppose the query is:

> "What is policy HR-2026-17?"

### Keyword search

Excellent because:

```text
HR-2026-17
```

is an exact identifier.

### Vector search

May find conceptually related documents but potentially miss exact code/identifier matches.

Conversely:

> "How many vacation days can I save for next year?"

Vector search can understand semantic similarity even if the document says:

> "Annual leave carry-forward entitlement."

---

# 31. Hybrid Search

Therefore production RAG commonly uses:

```text
Keyword Search
       +
Vector Search
       |
       v
Hybrid Search
```

Azure AI Search runs full-text and vector queries in parallel and combines results using **Reciprocal Rank Fusion (RRF)**. :chatgpt-content-reference{index="11"}

Conceptually:

```text
                Query
                  |
          +-------+-------+
          |               |
          v               v
       BM25            Vector
       Search          Search
          |               |
       Results          Results
          \               /
           \             /
            +-----------+
                 |
                RRF
                 |
                 v
            Unified Rank
```

---

# 32. BM25

Traditional search often uses **BM25**.

It considers factors such as:

- term frequency
- inverse document frequency
- document length

So exact terms matter.

Example:

```text
"Azure AI Search"
```

will strongly favor documents containing those terms.

---

# 33. Why Hybrid Search Is Powerful

Consider:

```text
Query:
"What is the max amount allowed under policy FIN-102?"
```

Keyword search:

```text
FIN-102
```

Vector search:

```text
maximum allowed amount
```

Together:

```text
Keyword -> exact terminology
Vector  -> semantic meaning
```

Microsoft's current Azure guidance recommends hybrid search where both exact terminology and semantic matching matter, particularly for specialized jargon, identifiers, dates and names. :chatgpt-content-reference{index="12"}

---

# 34. Filtering

Before or alongside retrieval, apply filters.

Example:

```text
department = "HR"
country = "India"
document_version = "2026"
user_access = true
```

Then search:

```text
Vector similarity
ONLY within authorized documents
```

This is extremely important for enterprise RAG.

Never:

```text
Retrieve everything
↓
Ask LLM to hide unauthorized information
```

Instead:

```text
Authorization filter
        ↓
Retrieval
        ↓
LLM
```

---

# 35. Security-Aware RAG

Suppose:

```text
Employee A
```

shouldn't see:

```text
Executive Compensation.pdf
```

The index might contain:

```text
ACL:
HR-ADMIN
```

At query time:

```text
User Identity
     |
     v
Authorization Filter
     |
     v
Search only permitted chunks
```

This is **retrieval-time authorization**.

Azure's current RAG guidance explicitly calls granular access control a major challenge when exposing private enterprise content to LLMs. :chatgpt-content-reference{index="13"}

---

# 36. Top-K Retrieval

Suppose vector search finds:

```text
Chunk 17 -> 0.91
Chunk 92 -> 0.89
Chunk 31 -> 0.86
Chunk 44 -> 0.83
...
```

We retrieve:

```text
Top K = 5
```

But:

> **Top-K is a hyperparameter, not a universal constant.**

Too low:

```text
Relevant information may be missed.
```

Too high:

```text
Context becomes noisy.
Cost increases.
```

Microsoft recommends evaluating the number of chunks passed to the LLM because fewer chunks reduce noise/cost while more chunks can improve recall. :chatgpt-content-reference{index="14"}

---

# 37. Reranking

Initial retrieval optimizes for **recall**.

Then a reranker can improve precision.

```text
Query
 |
 v
Retrieve Top 50
 |
 v
Reranker
 |
 v
Top 5
```

Architecture:

```text
             Query
               |
        Hybrid Retrieval
               |
          Top 50 chunks
               |
            Reranker
               |
           Top 5 chunks
               |
              LLM
```

A cross-encoder/reranking model can examine:

```text
Query + Candidate Chunk
```

together and estimate relevance more precisely than basic vector similarity.

---

# 38. Why Reranking Helps

Suppose initial search:

```text
1. General leave information
2. Leave eligibility
3. Leave carry-forward
4. Holiday policy
5. Attendance policy
```

Question:

> "How much leave can I carry forward?"

Reranker can promote:

```text
Carry-forward policy
```

to the top.

---

# 39. Context Compression

Suppose top 10 chunks contain 8,000 tokens.

You don't necessarily want to send all 8,000.

You can:

```text
Retrieve
 ↓
Remove irrelevant sentences
 ↓
Compress
 ↓
Send focused context
```

Example:

```text
8,000 tokens
     ↓
2,000 useful tokens
     ↓
LLM
```

This improves:

- cost
- latency
- signal-to-noise ratio

---

# 40. Context Window ≠ Infinite Knowledge

Modern models may have very large context windows.

But:

> More context is not automatically better.

Large irrelevant context can cause:

```text
attention dilution
conflicting evidence
higher cost
higher latency
```

Good RAG tries to provide:

> **the smallest sufficient set of high-quality evidence.**

---

# 41. Prompt Construction

Now we construct:

```text
System Instructions
+
User Question
+
Retrieved Context
+
Conversation History
```

Example:

```text
SYSTEM:
Answer only using the supplied enterprise context.
If the context does not contain the answer, say you don't know.
Cite the source for factual claims.

CONTEXT:

[Document 1]
Annual leave policy...
Source: LeavePolicy.pdf, page 12

[Document 2]
Carry-forward rules...
Source: LeavePolicy.pdf, page 15

USER:
How much leave can I carry forward?
```

Then:

```text
Prompt
 ↓
LLM
```

---

# 42. LLM's Actual Job in RAG

The LLM should primarily:

```text
Understand question
+
Interpret retrieved evidence
+
Synthesize answer
+
Explain
+
Cite
```

It should **not** be responsible for discovering all knowledge itself.

That's why:

```text
Retrieval quality
```

is just as important as:

```text
LLM quality
```

---

# 43. Hallucination

RAG reduces hallucination but does **not eliminate it**.

Possible failure:

```text
Retrieved Context:
No information about maternity leave.

LLM:
"Maternity leave is 26 weeks."
```

That's still hallucination.

---

# 44. Why Hallucination Still Happens

### 1. Retrieval failure

Correct document wasn't retrieved.

```text
Question
 ↓
Wrong chunks
 ↓
LLM
 ↓
Wrong answer
```

### 2. Insufficient context

Retrieved chunks don't contain enough information.

### 3. Conflicting documents

```text
Policy 2025 -> 20 days
Policy 2026 -> 24 days
```

### 4. LLM inference

The model fills gaps from pretrained knowledge.

### 5. Prompt failure

Instructions aren't strong enough.

---

# 45. Hallucination Control

Use multiple layers:

```text
Query rewriting
      ↓
Better retrieval
      ↓
Reranking
      ↓
Evidence filtering
      ↓
Strong grounding prompt
      ↓
Citation generation
      ↓
Grounding verification
      ↓
Abstain if unsupported
```

A good instruction:

```text
"If the retrieved evidence does not support
the answer, do not infer or invent information.
Respond that the information is unavailable."
```

But prompt instructions alone are not enough.

---

# 46. Groundedness Check

After generation:

```text
Answer
  |
  v
Grounding Evaluator
  |
  +-- Supported
  |
  +-- Unsupported
```

Example:

```text
Context:
Leave = 24 days

Answer:
Employees receive 24 days and can carry forward 10 days.
```

But context never mentioned:

```text
10 days
```

Evaluator detects:

```text
Claim 1 -> supported
Claim 2 -> unsupported
```

Then:

```text
Regenerate / remove unsupported claim / escalate
```

---

# 47. Citation Grounding

A production RAG response should ideally map claims to sources:

```text
Answer:
Employees receive 24 days of annual leave. [1]

[1] LeavePolicy.pdf, Page 12
```

Internally:

```text
claim_id
chunk_id
document_id
page
```

This gives traceability.

---

# 48. Query Transformation

The user's question isn't always optimal for retrieval.

User:

> "What about that leave thing we discussed earlier?"

Conversation context:

```text
Previous:
"How much annual leave do I receive?"
```

Transform into:

```text
"What is the annual leave entitlement?"
```

Then retrieve.

---

# 49. Query Rewriting

Original:

```text
"How much can I carry?"
```

Rewrite:

```text
"Annual leave carry-forward limit for employees"
```

This can improve retrieval.

---

# 50. Multi-Query Retrieval

One question can be transformed into several searches:

```text
Original:
"How does maternity leave work for employees
who joined recently?"
```

Generate:

```text
Query 1:
maternity leave eligibility

Query 2:
maternity leave new employees

Query 3:
maternity leave service requirement
```

Retrieve for each:

```text
Q1 -> chunks
Q2 -> chunks
Q3 -> chunks
```

Then merge/rerank.

Azure's current agentic retrieval architecture supports LLM-based query planning and decomposition for complex queries, while classic RAG can implement query decomposition manually. :chatgpt-content-reference{index="15"}

---

# 51. HyDE

An advanced strategy is **Hypothetical Document Embeddings (HyDE)**.

Instead of embedding the user's question directly:

```text
Question
 ↓
LLM generates hypothetical answer/document
 ↓
Embed hypothetical document
 ↓
Retrieve
```

Conceptually:

```text
Question
   ↓
Hypothetical Answer
   ↓
Embedding
   ↓
Vector Search
```

Useful when:

```text
Question wording
```

and:

```text
Document wording
```

are very different.

But it adds LLM latency/cost and should be benchmarked rather than assumed beneficial.

---

# 52. Query Decomposition

Complex query:

> "Compare the 2025 and 2026 leave policies and explain what changed for employees with less than one year of service."

Break into:

```text
Q1:
2025 leave policy

Q2:
2026 leave policy

Q3:
Eligibility under one year

Q4:
Differences between 2025 and 2026
```

Retrieve independently.

Then synthesize.

---

# 53. Iterative / Corrective RAG

Now we reach **advanced RAG**.

Normal RAG:

```text
Question
 ↓
Retrieve
 ↓
LLM
 ↓
Answer
```

Corrective RAG:

```text
Question
 ↓
Retrieve
 ↓
Evaluate Retrieval
 ↓
Good? -------- Yes --> LLM
  |
  No
  |
  v
Rewrite Query
  |
  v
Retrieve Again
```

This creates a loop.

---

# 54. Retrieval Loop

Example:

```text
Question
   |
Retrieve Top 5
   |
Evaluate relevance
   |
   +---- Good ----> Generate
   |
   +---- Bad
          |
          v
      Rewrite Query
          |
          v
      Retrieve Top 10
          |
          v
        Rerank
          |
          v
       Generate
```

This is particularly useful for:

- complex questions
- ambiguous queries
- multi-hop questions
- poor initial retrieval

But:

> **Always impose a maximum iteration count.**

Otherwise you can create an infinite agentic loop.

---

# 55. Agentic RAG

A more advanced architecture:

```text
                    User
                      |
                      v
                 Agent/Planner
                      |
        +-------------+-------------+
        |             |             |
        v             v             v
     Search        SQL Tool      API Tool
        |             |             |
        +-------------+-------------+
                      |
                 Evaluate Evidence
                      |
                  Enough?
                 /       \
               No         Yes
               |           |
          Search Again      v
                       Generate
```

The system dynamically decides:

- which source to query
- whether to search again
- whether SQL is needed
- whether documents are sufficient
- whether to ask another agent

This moves from:

```text
Static RAG
```

toward:

```text
Agentic RAG
```

Azure's current RAG guidance distinguishes classic RAG from agentic retrieval, where an LLM can plan/decompose queries and retrieve across multiple knowledge sources. :chatgpt-content-reference{index="16"}

---

# 56. SQL + Vector + API — Multi-Source RAG

Suppose user asks:

> "Why did my electricity bill increase this month?"

You might need:

```text
Vector DB:
Billing policy

SQL:
Actual billing amount

Meter DB:
Consumption history

API:
Current tariff

LLM:
Explain the difference
```

Architecture:

```text
                    User
                     |
                     v
                RAG Agent
               /    |     \
              /     |      \
             v      v       v
         Vector    SQL      API
          DB       DB       |
           |        |       |
        Policies  Usage    Tariff
              \     |      /
               \    |     /
                  LLM
                   |
                   v
              Explanation
```

This is a very strong production interview example.

---

# 57. RAG Evaluation — Don't Evaluate Only the Final Answer

This is one of the most important concepts.

There are at least two major evaluation layers.

## Retrieval Evaluation

Ask:

> Did we retrieve the right information?

## Generation Evaluation

Ask:

> Did the LLM use the retrieved information correctly?

Microsoft's current RAG evaluation guidance explicitly recommends evaluating retrieval independently from end-to-end generation. :chatgpt-content-reference{index="17"}

---

# 58. Retrieval Metrics

### Precision@K

Of the top K retrieved documents:

> How many are relevant?

```text
Precision@5 =
Relevant retrieved documents / 5
```

Example:

```text
Top 5:
Relevant = 4

Precision@5 = 4/5 = 0.8
```

---

# 59. Recall@K

Of all relevant documents:

> How many did we retrieve?

```text
Recall@K =
Relevant retrieved / Total relevant
```

Example:

```text
Total relevant = 5
Retrieved = 4

Recall@5 = 4/5 = 0.8
```

---

# 60. MRR

**Mean Reciprocal Rank**

Useful when the first relevant result is especially important.

If first relevant document is:

```text
Rank 1 → 1
Rank 2 → 1/2
Rank 3 → 1/3
```

Higher is better.

---

# 61. NDCG

**Normalized Discounted Cumulative Gain**

Useful when relevance has levels:

```text
3 = highly relevant
2 = relevant
1 = somewhat relevant
0 = irrelevant
```

It rewards highly relevant results appearing near the top.

Azure's current retrieval evaluation tooling includes metrics such as NDCG and other relevance-oriented measures. :chatgpt-content-reference{index="18"}

---

# 62. Generation Metrics

Important metrics include:

### Groundedness / Faithfulness

> Is the answer supported by retrieved context?

### Relevance

> Does the answer address the question?

### Completeness

> Did it cover the necessary information?

### Citation correctness

> Do citations actually support claims?

### Answer correctness

> Does the answer match trusted ground truth where one exists?

Microsoft's current RAG evaluation guidance explicitly identifies groundedness, completeness, utilization and relevance as useful end-to-end dimensions. :chatgpt-content-reference{index="19"}

---

# 63. LLM-as-a-Judge

An evaluator LLM can score:

```text
Question
+
Retrieved Context
+
Generated Answer
+
Rubric
```

Example:

```text
Groundedness = 0.95
Relevance = 0.92
Completeness = 0.87
```

But remember:

> **LLM-as-a-Judge is itself fallible.**

Therefore:

```text
LLM Judge
+
Deterministic checks
+
Golden dataset
+
Human evaluation
```

is stronger.

---

# 64. Human-in-the-Loop

HITL is especially useful when:

```text
Confidence low
        OR
High-risk domain
        OR
Conflicting sources
        OR
Low retrieval quality
```

Example:

```text
RAG
 |
Evaluator
 |
Confidence < threshold
 |
 v
Human reviewer
 |
 +---- Correct
 |
 +---- Correct/modify
 |
 +---- Reject
```

Human feedback can become future evaluation data.

---

# 65. Fine-Tuning vs RAG

This is another major interview topic.

### Use RAG for:

```text
Changing knowledge
Private documents
Current policies
Enterprise data
Citations
```

### Use fine-tuning for:

```text
Behavior
Style
Format
Domain-specific task patterns
Tool-use behavior
Classification
```

Example:

If you want the model to always produce:

```json
{
  "test_case": "...",
  "preconditions": [],
  "steps": [],
  "expected_result": "..."
}
```

fine-tuning may help.

If you want it to know:

```text
2026 company policy
```

RAG is generally more appropriate.

---

# 66. Can You Use Both?

Absolutely.

```text
Fine-tuned Model
       +
RAG
       |
       v
Enterprise Assistant
```

Fine-tuning:

```text
How the model behaves
```

RAG:

```text
What information it should use
```

---

# 67. RAG vs Fine-Tuning

| Requirement | RAG | Fine-tuning |
|---|---:|---:|
| Fresh information | ✅ | ❌ |
| Private documents | ✅ | Possible, but not ideal |
| Citations | ✅ | ❌ |
| Easy document updates | ✅ | ❌ |
| Change response style | Limited | ✅ |
| Teach output format | Possible | ✅ |
| Domain knowledge | ✅ | Possible |
| Remove hallucination | Helps | Doesn't guarantee |
| Requires retraining after document update | ❌ | ✅ |
| Runtime retrieval | ✅ | ❌ |

---

# 68. Advanced RAG Architecture

A production-grade system could look like:

```text
                         USER
                           |
                           v
                     API Gateway
                           |
                     Authentication
                           |
                           v
                    RAG Orchestrator
                           |
                  Query Understanding
                           |
                +----------+----------+
                |                     |
                v                     v
           Query Rewrite         Conversation
                |                  Context
                +----------+----------+
                           |
                    Query Planner
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      Keyword           Vector            SQL
      Search            Search            Query
          |                |                |
          +----------------+----------------+
                           |
                      Hybrid Merge
                           |
                         Rerank
                           |
                    ACL / Security
                           |
                  Context Compression
                           |
                    Context Builder
                           |
                           v
                         LLM
                           |
              +------------+------------+
              |            |            |
              v            v            v
          Citation      Safety      Grounding
           Check         Check        Check
              |            |            |
              +------------+------------+
                           |
                    Evaluation Layer
                           |
                 +---------+---------+
                 |                   |
              Accept              Review
                 |                   |
                 v                   v
              User               Human
```

---

# 69. Knowledge Ingestion Architecture

The offline side:

```text
                     DATA SOURCES
                          |
          +---------------+---------------+
          |               |               |
         PDF         SharePoint          SQL
          |               |               |
          +---------------+---------------+
                          |
                     Data Pipeline
                          |
                     Parser / OCR
                          |
                       Cleaner
                          |
                      Chunker
                          |
                  Metadata Enrichment
                          |
                      Embedding
                          |
              +-----------+-----------+
              |                       |
              v                       v
         Vector Index            Metadata/SQL
              |                       |
              +-----------+-----------+
                          |
                     Search Layer
```

---

# 70. Updating the Knowledge Base

Suppose:

```text
LeavePolicy v1
```

becomes:

```text
LeavePolicy v2
```

You don't retrain the LLM.

Instead:

```text
New Document
   ↓
Parse
   ↓
Chunk
   ↓
Embed
   ↓
Upsert
   ↓
Index
```

Old version can be:

```text
deleted
```

or:

```text
marked inactive
```

This is one of RAG's major operational advantages.

---

# 71. Document Versioning

Store:

```json
{
  "document_id": "leave-policy",
  "version": "2026.2",
  "effective_from": "2026-07-01",
  "active": true
}
```

Then filter:

```text
active = true
```

or:

```text
effective_from <= current_date
```

This prevents retrieval of outdated policies.

---

# 72. Temporal RAG

Some questions are time-sensitive:

> "What was the leave policy in 2024?"

Don't simply retrieve the newest document.

Use metadata:

```text
effective_from
effective_to
version
```

Then:

```text
Question Date
      |
      v
Temporal Filter
      |
      v
Historical Documents
```

This is important in financial, legal and regulatory systems.

---

# 73. Multi-Modal RAG

RAG doesn't have to be text-only.

Knowledge may contain:

```text
Text
Images
Tables
Diagrams
Charts
PDFs
Audio
Video
```

Example:

```text
Architecture PDF
      |
      +-- Text extraction
      +-- Table extraction
      +-- Image extraction
      +-- OCR
```

Then retrieve the appropriate representation.

---

# 74. Parent-Child Retrieval

A powerful technique:

```text
Small child chunks
       |
       v
Precise retrieval
       |
       v
Parent section/document
       |
       v
LLM context
```

Why?

Small chunks provide:

```text
high retrieval precision
```

but may lack context.

Parent retrieval restores:

```text
surrounding context
```

Example:

```text
Document
 |
 +-- Section
      |
      +-- Child Chunk 1
      +-- Child Chunk 2  <-- matched
      +-- Child Chunk 3
```

Return:

```text
Entire Section
```

instead of only:

```text
Child Chunk 2
```

---

# 75. Graph RAG

Normal RAG:

```text
Query → Vector Search → Chunks
```

Graph RAG:

```text
Query
 ↓
Entities
 ↓
Relationships
 ↓
Knowledge Graph
 ↓
Relevant subgraph
 ↓
LLM
```

Useful when relationships matter.

Example:

```text
Employee
   |
works_for
   |
Department
   |
owns
   |
Project
   |
uses
   |
Technology
```

Question:

> "Which projects are affected by the retirement of technology X?"

A graph can traverse relationships more naturally than simple semantic similarity.

---

# 76. When Normal RAG Is Not Enough

Use more advanced retrieval when questions involve:

### Multi-hop reasoning

```text
A → B → C → answer
```

### Structured data

Use:

```text
SQL
```

### Relationships

Use:

```text
Knowledge Graph
```

### Complex multi-source questions

Use:

```text
Agentic RAG
```

### Exact identifiers

Use:

```text
Keyword + Hybrid Search
```

---

# 77. Common RAG Failure Modes

### Failure 1 — Bad chunking

```text
Relevant information split across chunks
```

### Failure 2 — Wrong embedding model

```text
Semantic similarity poor
```

### Failure 3 — Retrieval misses answer

```text
Recall too low
```

### Failure 4 — Too many chunks

```text
Noise
```

### Failure 5 — No reranking

```text
Less relevant chunks dominate
```

### Failure 6 — Stale documents

```text
Old policy retrieved
```

### Failure 7 — Missing ACL filtering

```text
Unauthorized information exposed
```

### Failure 8 — LLM ignores context

```text
Hallucination
```

### Failure 9 — Conflicting sources

```text
2025 policy vs 2026 policy
```

### Failure 10 — No abstention

```text
No evidence
↓
LLM invents answer
```

---

# 78. How I Would Debug a Bad RAG Answer

This is an excellent interview question.

Suppose:

> "The RAG answer is wrong."

Don't immediately blame the LLM.

Trace:

```text
1. Was the correct document ingested?
        ↓
2. Was parsing correct?
        ↓
3. Was chunking correct?
        ↓
4. Was metadata correct?
        ↓
5. Was embedding generated correctly?
        ↓
6. Did retrieval find the correct chunk?
        ↓
7. Was ranking correct?
        ↓
8. Was the correct context sent to LLM?
        ↓
9. Did LLM use the context?
        ↓
10. Did post-generation evaluation detect the issue?
```

This gives you:

```text
Data problem
Retrieval problem
Ranking problem
Prompt problem
Generation problem
Evaluation problem
```

---

# 79. Retrieval vs Generation Debugging

This distinction is extremely useful.

### Case A

Correct document was **not retrieved**.

Problem:

```text
Retrieval
```

### Case B

Correct document was retrieved, but LLM ignored it.

Problem:

```text
Generation / prompt
```

### Case C

Correct answer generated but evaluator rejects it.

Problem:

```text
Evaluation
```

### Case D

Unauthorized document retrieved.

Problem:

```text
Security / authorization
```

---

# 80. Production Observability

Trace every RAG request:

```text
trace_id
 |
 +-- user_id
 |
 +-- query
 |
 +-- rewritten_query
 |
 +-- embedding_model
 |
 +-- search_strategy
 |
 +-- retrieved_chunks
 |
 +-- similarity_scores
 |
 +-- reranker_scores
 |
 +-- prompt_tokens
 |
 +-- completion_tokens
 |
 +-- model
 |
 +-- latency
 |
 +-- answer
 |
 +-- citations
 |
 +-- evaluation
```

Then you can answer:

> "Why did the assistant give this answer?"

---

# 81. RAG Cost Model

Approximate cost comes from:

```text
Ingestion:
documents × chunks × embedding cost

Query:
embedding cost
+
search cost
+
reranking cost
+
LLM input tokens
+
LLM output tokens
+
evaluation cost
```

One major optimization:

```text
Don't send 30,000 retrieved tokens
to the LLM if 3,000 useful tokens are enough.
```

---

# 82. Latency Optimization

Typical pipeline:

```text
Query
 ↓
Embedding
 ↓
Search
 ↓
Rerank
 ↓
LLM
```

Optimize through:

```text
Parallel search
Caching
Smaller embedding model
ANN/HNSW
Top-K tuning
Reranker optimization
Context compression
Streaming LLM response
```

For complex agentic retrieval, run independent searches in parallel when possible. Azure's current agentic retrieval approach explicitly uses parallel execution of focused subqueries. :chatgpt-content-reference{index="20"}

---

# 83. Caching

Cache:

```text
Query embedding
Search result
Frequently asked question
```

Example:

```text
"What is the leave policy?"
```

may be asked thousands of times.

Architecture:

```text
Query
 |
Redis
 |
 +-- Cached answer/context
 |
No cache
 |
Search → LLM
```

But cache invalidation matters when documents change.

---

# 84. Production Azure Implementation

Given your Azure/Agentic AI background, a typical architecture could be:

```text
                    User
                      |
                  APIM / WAF
                      |
                 Entra ID
                      |
                      v
              Agent / RAG API
                      |
          +-----------+-----------+
          |                       |
          v                       v
   Azure AI Search            Azure SQL
          |                       |
   Vector + BM25              Business data
          |
      Blob / ADLS
          |
      Documents
          |
    Embeddings
          |
    Azure OpenAI /
    Foundry Models
          |
          v
       LLM Answer
          |
     Evaluation
          |
 +--------+--------+
 |        |        |
RAI    Grounding  HITL
          |
          v
        User
```

Azure AI Search supports classic hybrid RAG and current agentic retrieval patterns; its vector index can contain both vector and human-readable fields, while Azure OpenAI/Foundry models can provide embedding and generation capabilities. :chatgpt-content-reference{index="21"}

---

# 85. Complete End-to-End Example

Let's execute one request:

> **"How many annual leaves can an employee carry forward?"**

### Step 1 — User

```text
Question
```

### Step 2 — Query understanding

```text
Intent:
Leave policy

Entities:
Annual leave
Carry forward
```

### Step 3 — Query rewrite

```text
"Annual leave carry-forward entitlement"
```

### Step 4 — Embedding

```text
Question
 ↓
Embedding model
 ↓
Vector Q
```

### Step 5 — Hybrid retrieval

```text
Vector search
+
BM25
```

### Step 6 — Filtering

```text
Active policy
+
India
+
Employee-accessible
```

### Step 7 — Retrieve

```text
Top 20
```

### Step 8 — Rerank

```text
20 → 5
```

### Step 9 — Context compression

```text
5 → relevant passages
```

### Step 10 — Prompt

```text
Question
+
5 relevant passages
+
grounding instructions
```

### Step 11 — LLM

```text
Generate answer
```

### Step 12 — Citation

```text
LeavePolicy.pdf
Page 15
```

### Step 13 — Grounding evaluator

```text
Does answer follow evidence?
```

### Step 14 — Final

```text
Employees can carry forward X days...
[Source: Leave Policy, page 15]
```

---

# 86. The Full Production Pipeline

Memorize this:

```text
                  OFFLINE / INDEXING
                  ==================

Documents
   ↓
Connectors
   ↓
Parsing / OCR
   ↓
Cleaning
   ↓
Structure Detection
   ↓
Chunking
   ↓
Metadata Enrichment
   ↓
Embedding Model
   ↓
Vector Index
   ↓
Keyword Index
   ↓
ACL / Metadata
```

Then:

```text
                  ONLINE / QUERY
                  ==============

User Query
   ↓
Authentication
   ↓
Query Understanding
   ↓
Conversation Resolution
   ↓
Query Rewrite
   ↓
Query Decomposition
   ↓
Embedding
   ↓
Keyword Search + Vector Search
   ↓
Hybrid Fusion
   ↓
Metadata / ACL Filtering
   ↓
Reranking
   ↓
Top-K
   ↓
Context Compression
   ↓
Prompt Construction
   ↓
LLM
   ↓
Citation / Grounding Check
   ↓
Safety / RAI Check
   ↓
LLM-as-Judge / Evaluation
   ↓
Accept / Regenerate / Escalate
   ↓
Final Answer
```

---

# 87. Where Fine-Tuning Fits

Don't put fine-tuning inside every RAG request.

It is usually an **offline model-improvement path**:

```text
Production failures
       ↓
Human feedback
       ↓
Golden dataset
       ↓
Fine-tuning / prompt optimization
       ↓
Evaluate
       ↓
Deploy
```

Meanwhile:

```text
Current enterprise knowledge
       ↓
RAG
```

So:

```text
Fine-tuning → model behavior
RAG         → runtime knowledge
```

---

# 88. Where HITL Fits

HITL can occur at multiple points:

```text
             Retrieval
                |
         Low confidence?
                |
              Human
                |
                v
            Continue
```

or:

```text
LLM answer
    |
High-risk?
    |
Human approval
```

or:

```text
Evaluation
    |
Disagreement
    |
Human labels correct answer
    |
Golden Dataset
```

That last one is especially valuable because HITL becomes a **continuous evaluation/improvement mechanism**.

---

# 89. Continuous RAG Improvement Loop

A mature system doesn't stop after deployment.

```text
                  Production
                      |
                      v
                  User Query
                      |
                      v
                    RAG
                      |
                      v
                   Answer
                      |
                      v
                 Evaluation
                      |
          +-----------+-----------+
          |                       |
        Good                    Bad
          |                       |
          |                  Root Cause
          |                       |
          |        +--------------+--------------+
          |        |       |       |      |      |
          |      Data   Chunking Retrieval Prompt LLM
          |        |       |       |      |      |
          |        +-------+-------+------+------+
          |                        |
          |                     Improve
          |                        |
          +------------------------+
```

This is how production RAG systems become better over time.

---

# 90. RAG Maturity Levels

### Level 1 — Basic RAG

```text
Chunk → Embed → Vector DB → LLM
```

### Level 2 — Production RAG

```text
Chunk
+
Metadata
+
Hybrid Search
+
Reranking
+
Citations
```

### Level 3 — Enterprise RAG

```text
ACL
+
SQL
+
Multiple sources
+
Versioning
+
Evaluation
+
Observability
+
HITL
```

### Level 4 — Advanced RAG

```text
Query rewriting
+
Multi-query
+
Query decomposition
+
Corrective retrieval
+
Context compression
+
Parent-child retrieval
```

### Level 5 — Agentic RAG

```text
Planner
+
Dynamic source selection
+
Tool calling
+
Iterative retrieval
+
SQL
+
APIs
+
Multiple agents
+
Evaluation
```

---

# 91. Most Important Interview Questions

Be prepared for these:

### Fundamentals

1. What is RAG?
2. RAG vs fine-tuning?
3. Why use RAG?
4. What is an embedding?
5. What is a vector database?
6. What is chunking?
7. Why overlap chunks?
8. What is cosine similarity?
9. What is top-K?

### Retrieval

10. Vector vs keyword search?
11. What is hybrid search?
12. What is BM25?
13. What is HNSW?
14. What is reranking?
15. How do you improve retrieval recall?
16. How do you improve precision?
17. What is query rewriting?
18. What is multi-query retrieval?
19. What is query decomposition?
20. What is HyDE?

### Production

21. How do you handle document updates?
22. How do you handle permissions?
23. How do you prevent stale documents?
24. How do you handle conflicting documents?
25. How do you reduce hallucinations?
26. How do you control token cost?
27. How do you reduce latency?
28. How do you monitor RAG?
29. How do you debug bad retrieval?
30. How do you scale vector search?

### Advanced

31. What is corrective RAG?
32. What is agentic RAG?
33. What is Graph RAG?
34. What is parent-child retrieval?
35. How do you evaluate RAG?
36. Precision vs Recall@K?
37. What is NDCG?
38. What is groundedness?
39. What is LLM-as-a-Judge?
40. When can an LLM judge be wrong?
41. How do you use HITL?
42. How do you combine RAG and fine-tuning?

---

# 92. 🔴 Interview-Ready 2-Minute Answer

If an interviewer says:

> **"Explain your RAG architecture end-to-end."**

Say:

> **"I divide RAG into two pipelines: offline ingestion and online query processing.**
>
> **During ingestion, I take data from sources such as Blob Storage, SharePoint, PDFs and databases. I parse and OCR documents where required, clean them, and chunk them based on document structure. I enrich each chunk with metadata such as document ID, section, page, version, timestamp and access control information. I then generate embeddings using an embedding model and store the vectors, chunk text and metadata in a vector-capable search index.**
>
> **At runtime, the user's query first goes through authentication, query understanding and potentially query rewriting or decomposition. I generate a query embedding and perform hybrid retrieval using vector similarity and keyword search. I apply authorization filters, retrieve candidate chunks, and then rerank them to improve precision. I select the most relevant context and build a grounded prompt containing the user's question, retrieved evidence and instructions to answer only from that evidence.**
>
> **The LLM generates the response, ideally with citations. After generation, I can run grounding, safety and correctness evaluation. If evidence is insufficient, I can abstain, rewrite the query and retrieve again, or escalate to a human.**
>
> **For evaluation, I separate retrieval metrics such as Recall@K, Precision@K, MRR and NDCG from generation metrics such as groundedness, relevance, completeness and answer correctness. I can use LLM-as-a-Judge, but I don't treat it as ground truth; I calibrate it against human-labeled datasets and use deterministic checks wherever possible.**
>
> **For production, I also handle ACL-based retrieval, document versioning, caching, observability, cost, latency, hallucination detection and continuous improvement through human feedback. Fine-tuning is complementary: I use RAG for dynamic knowledge and fine-tuning primarily for behavior, style or specialized task performance."**

---

# 93. Final Mental Model

If you remember only one diagram, remember this:

```text
                     RAG
                      |
        +-------------+-------------+
        |                           |
   OFFLINE                        ONLINE
   INDEXING                       QUERY
        |                           |
    Documents                    Question
        ↓                           ↓
     Parse                    Query Rewrite
        ↓                           ↓
     Clean                     Embedding
        ↓                           ↓
    Chunking              +------+------+
        ↓                 |             |
    Enrich              BM25          Vector
        ↓                 |             |
   Embedding              +------+------+
        ↓                        |
 Vector / Search                 ↓
     Index                    Hybrid
        |                        ↓
        |                     Rerank
        |                        ↓
        |                   ACL Filter
        |                        ↓
        |                Context Selection
        |                        ↓
        |                   Prompt Builder
        |                        ↓
        +--------------------> LLM
                                 |
                     +-----------+-----------+
                     |           |           |
                 Grounding     Safety     Citation
                     |           |           |
                     +-----------+-----------+
                                 |
                            Evaluation
                                 |
                    +------------+------------+
                    |            |            |
                  Accept      Retry        HITL
                                 |
                          Query Again /
                         Better Retrieval
```

### The deepest interview takeaway:

> **RAG is not a vector database architecture. It is an information-retrieval + context-engineering + generation + evaluation system.**

And when debugging it:

> **First ask: "Did we retrieve the right evidence?" Then ask: "Did the LLM use that evidence correctly?"**

That distinction alone separates a **basic RAG implementation** from a **production-grade RAG architecture**.