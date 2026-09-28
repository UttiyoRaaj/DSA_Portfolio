## Title: SQL vs NoSQL — How Do You Choose for a Large-Scale System?

**Category:** System Design Fundamentals  
**Difficulty:** Beginner  
**Description:** A practical guide to choosing SQL or NoSQL based on data relationships, consistency, scale, and access patterns.

## Question

How do you choose between **SQL and NoSQL** for a large-scale system?

## Short Answer

**SQL databases** store structured relational data in tables and are best when strong consistency, transactions, joins, and well-defined relationships matter.

**NoSQL databases** use flexible data models such as documents, key-value pairs, wide columns, or graphs. They are useful when a system needs flexible schema, very high horizontal scale, or low-latency access for large volumes of semi-structured data.

For most real systems, the right answer is often **polyglot persistence**: use SQL for transactional business data and NoSQL for specialized workloads such as caching, search, events, sessions, or high-volume document data.

## Core Idea

Choose based on the system’s data and access patterns—not because one database is always more scalable.

```text
Client
   ↓
Application / Microservice
   ↓
Choose storage based on workload
   ├── SQL → transactions, relationships, reporting
   └── NoSQL → flexible schema, cache, high-volume reads/writes
```

## SQL Databases

Examples:

- PostgreSQL
- MySQL
- Microsoft SQL Server
- Oracle

SQL databases organize data into related tables.

```text
Users
+---------+--------+
| user_id | name   |
+---------+--------+
| 101     | Uttiya |
+---------+--------+

Orders
+----------+---------+--------+
| order_id | user_id | amount |
+----------+---------+--------+
| 501      | 101     | 5000   |
+----------+---------+--------+
```

A SQL query can join related data:

```sql
SELECT u.name, o.order_id, o.amount
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE u.user_id = 101;
```

## When to Choose SQL

Use SQL when you need:

- Strong consistency
- ACID transactions
- Complex joins and relationships
- Structured and stable schema
- Financial, billing, order, or inventory data
- Reporting and analytics queries
- Referential integrity through foreign keys

Example: Invoice processing.

```text
Invoice
   ↓
Purchase Order
   ↓
Vendor
   ↓
Payment Status
```

These entities have clear relationships. If an invoice is approved and a payment record is created, both operations may need to succeed or fail together.

```text
Begin transaction
   ↓
Update invoice status
   ↓
Create payment record
   ↓
Commit transaction
```

This is a strong SQL use case.

## NoSQL Databases

NoSQL means “not only SQL.” It includes several database types.

| Type | Example | Good for |
|---|---|---|
| Key-value | Redis, DynamoDB | Cache, sessions, rate limits |
| Document | MongoDB, Cosmos DB | Flexible JSON-like data |
| Wide-column | Cassandra, HBase | Very large write-heavy workloads |
| Graph | Neo4j | Highly connected data |
| Search / vector | Elasticsearch, Azure AI Search, FAISS | Search, RAG, semantic retrieval |

A document database can store flexible data in JSON-like form:

```json
{
  "invoiceId": "INV-101",
  "vendor": {
    "name": "ABC Supplies",
    "country": "India"
  },
  "lineItems": [
    {
      "description": "Laptop",
      "quantity": 2,
      "amount": 150000
    }
  ],
  "language": "English",
  "extractionConfidence": 0.92
}
```

Different invoices may have different fields without requiring an immediate schema migration.

## When to Choose NoSQL

Use NoSQL when you need:

- Flexible or rapidly changing schema
- Very high write throughput
- Horizontal scaling across many nodes
- Low-latency key-based access
- Semi-structured JSON/document data
- Event, telemetry, log, session, cache, or chat data
- Specialized retrieval such as vector search

Example: Agentic AI / RAG system.

```text
User Query
   ↓
Embedding Model
   ↓
Vector Database / Search Index
   ↓
Relevant Document Chunks
   ↓
LLM Answer
```

For RAG, a vector store or search service is more suitable than a traditional relational database for semantic similarity retrieval.

## Key Comparison

| Factor | SQL | NoSQL |
|---|---|---|
| Data model | Tables and relations | Document, key-value, graph, wide-column |
| Schema | Fixed / strongly defined | Flexible |
| Joins | Strong support | Usually limited or avoided |
| Transactions | Strong ACID support | Varies by database |
| Scaling | Often vertical first; can scale horizontally | Usually designed for horizontal scaling |
| Consistency | Usually strong consistency | Often configurable or eventual consistency |
| Best use case | Payments, orders, users, ERP | Cache, events, documents, search, high-volume data |
| Query style | SQL | Database-specific APIs/query language |

## Consistency Trade-Off

For a large-scale distributed system, there is often a trade-off between consistency and availability during network failures.

```text
Network partition happens
        ↓
System must decide:
        ├── Return only strongly consistent data
        └── Stay available but possibly return slightly stale data
```

For example:

- A bank balance should be strongly consistent.
- A social-media like counter can tolerate eventual consistency.
- A Redis cache can be temporarily stale.
- An invoice payment decision should use authoritative SQL/ERP data.

## Example: Agentic Invoice Auditor Architecture

A realistic system can use both SQL and NoSQL.

```text
Incoming Invoice
      ↓
Object Storage
      ↓
Kafka Event
      ↓
Invoice Processing Service
      ├── SQL Database
      │     ├── Invoice status
      │     ├── Audit decisions
      │     ├── Payment references
      │     └── Reviewer approvals
      │
      ├── Redis
      │     ├── Rate limiting
      │     ├── Temporary workflow state
      │     └── ERP response cache
      │
      └── Vector Store / Azure AI Search
            ├── Invoice chunks
            ├── Embeddings
            └── RAG retrieval
```

## Interview-Ready Answer

> I choose SQL when the domain has strong relationships, transactions, and consistency requirements—for example invoices, purchase orders, payments, users, and audit records. SQL gives me ACID transactions, joins, constraints, and reliable reporting.

> I choose NoSQL when the workload needs flexible schema, high horizontal scale, low-latency key-value access, or specialized retrieval. For example, Redis is useful for caching and rate limiting, while a vector database or Azure AI Search is useful for RAG and semantic search.

> In a large-scale enterprise system, I would often use both. I would keep financial and audit data in SQL as the source of truth, use Redis for temporary high-speed data, Kafka for asynchronous events, and a vector search platform for AI retrieval.