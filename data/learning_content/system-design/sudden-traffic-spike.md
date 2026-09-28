## Title: How Do You Handle a Sudden 100× Traffic Spike?

**Category:** System Design Fundamentals  
**Difficulty:** Intermediate  
**Description:** A practical approach to protecting availability, controlling cost, and processing work safely when traffic suddenly increases by 100×.

## Question

How would you handle a sudden **100× traffic spike** in a large-scale system?

## Short Answer

I would protect the system in layers: use load balancing and autoscaling for stateless APIs, caching for repeated reads, queues for long-running work, rate limits and load shedding for overload protection, and monitoring to identify bottlenecks.

The goal is not necessarily to process every request immediately. The goal is to keep critical services available, degrade gracefully, and process non-urgent work safely.

## Core Idea

```text
Users
   ↓
CDN / Load Balancer
   ↓
Rate Limit + WAF
   ↓
Autoscaled API Instances
   ├── Redis Cache
   ├── SQL / NoSQL Database
   └── Queue / Kafka
          ↓
      Async Workers
          ↓
   OCR / LLM / ERP / Notifications
```

## 1. Load Balancing

A load balancer distributes traffic across multiple API instances.

```text
100× Incoming Requests
          ↓
     Load Balancer
     ├── API Instance 1
     ├── API Instance 2
     ├── API Instance 3
     └── API Instance N
```

This prevents one server from becoming overloaded.

For example:

- Azure Load Balancer
- Azure Application Gateway
- Azure Front Door
- Kubernetes Service / Ingress
- API Gateway

## 2. Autoscaling

Stateless services should scale horizontally.

```text
Normal traffic:
2 API instances

Traffic spike:
100× traffic
   ↓
Autoscaler detects CPU, memory, request rate, or queue lag
   ↓
Scale to 20, 50, or more instances
```

I would scale on more than CPU.

Useful metrics include:

- Requests per second
- p95 latency
- CPU and memory
- Active connections
- Kafka consumer lag
- Queue depth
- Error rate
- LLM request concurrency

For async workers, queue depth and consumer lag are often better scaling signals than CPU.

```text
Queue depth > threshold
        ↓
Add more worker instances
        ↓
Reduce queue backlog
```

## 3. Caching

Many requests may be identical or repeatedly fetch the same data.

```text
User Request
   ↓
Redis Cache
   ├── Cache hit  → return immediately
   └── Cache miss → call database/service → cache result
```

Examples of safe cache candidates:

- Static configuration
- Product catalog
- Read-only reference data
- Frequently accessed purchase-order details
- User session data
- Repeated RAG retrieval results, where authorization is preserved
- Public API results

Avoid caching highly dynamic or sensitive data without a clear TTL and authorization-aware cache key.

```text
Cache key:
user:{userId}:invoice:{invoiceId}

Not:
invoice:{invoiceId}
```

The first version prevents one user from receiving another user’s data from cache.

## 4. Queues for Long-Running Work

Do not make users wait for slow processing such as OCR, document extraction, LLM workflows, report generation, or notification delivery.

```text
Client uploads invoice
        ↓
API validates request
        ↓
Store file + create operation record
        ↓
Publish event to Kafka / queue
        ↓
Return HTTP 202 Accepted + operation ID
        ↓
Workers process asynchronously
```

```text
Kafka Topic: invoice.received
        ↓
Extraction Worker
        ↓
Validation Worker
        ↓
Reporting Worker
        ↓
Notification / Dashboard Update
```

This absorbs spikes because the queue stores work until workers can process it.

Important controls:

- Idempotency keys
- Retry with exponential backoff
- Dead-letter queue/topic
- Queue retention limits
- Priority queues for critical work
- Backpressure when downstream systems are overloaded

## 5. Rate Limiting

Rate limiting prevents one user, client, bot, or buggy service from consuming all capacity.

```text
User / API Key
      ↓
Rate Limiter
      ↓
Allowed? ── No → HTTP 429 Too Many Requests
      │
     Yes
      ↓
API
```

Example policy:

```text
Anonymous user: 10 requests/minute
Authenticated user: 60 requests/minute
Premium client: 500 requests/minute
Internal service: separate limit
```

For an Agentic AI application, rate limiting is especially important because each user request may create multiple expensive operations:

```text
1 user request
   ↓
RAG retrieval
   ↓
LLM call
   ↓
Tool call
   ↓
Second LLM call
```

One user request can create several downstream requests and significant model cost.

## 6. Load Shedding

Load shedding means intentionally rejecting or reducing non-critical work when the system is overloaded, so critical operations remain available.

```text
System overloaded
      ↓
Keep:
- Authentication
- Payment / approval actions
- Critical invoice validation

Delay or reject:
- Analytics
- Report regeneration
- Non-essential notifications
- Expensive broad RAG searches
- Large batch exports
```

Possible responses:

```text
HTTP 429 Too Many Requests
HTTP 503 Service Unavailable
HTTP 202 Accepted — queued for processing
```

For an AI application, graceful degradation can mean:

```text
Normal mode:
Hybrid retrieval + reranking + GPT model + multiple tools

Degraded mode:
Cached answer or smaller model
OR
Keyword retrieval only
OR
Queue request for later
OR
Return: “The system is busy. Please retry shortly.”
```

Do not silently provide lower-quality answers for a high-risk decision without telling the user.

## 7. Protect Downstream Dependencies

Scaling API instances alone can make the situation worse if every new instance overloads the database, ERP, LLM provider, or third-party API.

```text
More API instances
      ↓
More ERP calls
      ↓
ERP becomes overloaded
      ↓
Entire workflow fails
```

Use:

- Connection pool limits
- Circuit breakers
- Timeouts
- Bulkheads
- Bounded retries
- Cached fallback data where safe
- Per-dependency concurrency limits

```text
API
 ├── Database pool: max 50 connections
 ├── ERP calls: max 20 concurrent requests
 ├── LLM calls: max 10 concurrent requests
 └── OCR jobs: max 5 concurrent workers
```

## 8. Database Protection

A traffic spike can overload the database through too many connections or expensive queries.

Use:

- Read replicas for read-heavy workloads
- Connection pooling
- Query optimization and indexes
- Caching
- Pagination
- Database rate limits
- Separate read and write paths where appropriate

```text
Read request
   ↓
Redis cache
   ↓ cache miss
Read replica

Write request
   ↓
Primary database
```

For critical writes, protect correctness first. Do not send transactional payment or audit writes to an eventually consistent cache.

## 9. Monitoring and Incident Response

During a spike, monitor:

| Area | Important metrics |
|---|---|
| API | Request rate, p95/p99 latency, error rate |
| Autoscaling | Instance count, CPU, memory, saturation |
| Queue/Kafka | Queue depth, consumer lag, retry volume |
| Redis | Cache hit rate, latency, evictions |
| Database | Connection count, slow queries, CPU |
| AI/LLM | Token usage, model latency, throttling, cost |
| Dependencies | ERP/API timeout and error rate |

A useful alert pattern:

```text
Request rate increases
      +
p95 latency increases
      +
Queue lag increases
      ↓
Trigger incident alert
      ↓
Enable degraded mode / scale workers
```

## Example: Agentic Invoice Auditor Under 100× Load

```text
100× invoice uploads
        ↓
API Gateway rate limits clients
        ↓
Upload API stores document in object storage
        ↓
Creates SQL operation record
        ↓
Kafka: invoice.received
        ↓
Autoscaled extraction workers
        ↓
Autoscaled validation workers
        ↓
Human review queue for risky exceptions
```

Protection mechanisms:

```text
Redis:
- Cache safe ERP lookups
- Rate limit users
- Store short-lived workflow state

Kafka:
- Buffer incoming work
- Support independent worker scaling
- Preserve processing history

SQL:
- Store invoice status and audit trail
- Enforce unique/idempotency constraints

LLM:
- Limit concurrency
- Apply token budgets
- Queue non-urgent work
- Use fallback/degraded responses
```

## Interview-Ready Answer

> For a sudden 100× traffic spike, I would first protect the edge using a load balancer, rate limits and WAF rules. I would horizontally autoscale stateless API services based on request rate, latency and resource usage.

> I would cache safe repeated reads using Redis to reduce database and ERP load. Long-running work such as OCR, document processing, LLM calls and report generation would move to Kafka or a queue, allowing the API to return quickly with an operation ID while workers process the backlog asynchronously.

> I would protect downstream dependencies with timeouts, circuit breakers, concurrency limits and bounded retries. If the system remains overloaded, I would apply load shedding by delaying or rejecting non-critical work while preserving critical business operations.

> Finally, I would monitor p95 latency, error rate, queue lag, cache hit rate, database saturation and LLM throttling. The objective is graceful degradation and safe recovery—not simply adding servers.