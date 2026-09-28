---
title: Design a System That Remains Available When a Downstream Service Is Failing?
category: System Design Fundamentals
difficulty: Hard
description: A production-oriented approach to maintaining availability during downstream failures using timeouts, retries, circuit breakers, bulkheads, fallbacks, and graceful degradation.
---

## Question

How would you design a system that remains **available when a downstream service is failing**?

## Short Answer

I would design the system with **timeouts, limited retries, circuit breakers, bulkheads, fallbacks, and graceful degradation**.

The key principle is:

> **A failure in one downstream service should not bring down the entire system.**

```text
Client
   |
   v
API / Service A
   |
   +--------------------+
   |                    |
   v                    v
Service B           Service C
   |                    |
   v                    v
Database             External API
```

If Service C fails:

```text
Service A
   |
   +----> Service B ---> Continue normally
   |
   +----> Service C ---> FAIL
                       |
                       v
                    Fallback
                       |
                       v
                  Partial Response
```

---

# Core Idea

A resilient system assumes:

> **Failures will happen.**

Instead of allowing a downstream failure to propagate:

```text
Service A
   |
   v
Service B
   |
   v
Service C ❌
   |
   v
Service B ❌
   |
   v
Service A ❌
   |
   v
Client ❌
```

we contain the failure:

```text
Service A
   |
   +----> Service B ---> Success
   |
   +----> Service C
             |
             X Failure
             |
             v
          Fallback
             |
             v
       Partial Response
```

---

# 1. Start With Timeouts

**Never wait indefinitely for a downstream service.**

Bad:

```text
Service A ---> Service B
                  |
               waiting...
                  |
               waiting...
                  |
               waiting...
```

If Service B is down, Service A's threads/connections can get exhausted.

Instead:

```text
Service A ---> Service B
                  |
              500 ms timeout
                  |
                  X
                  |
               Fallback
```

Example:

```text
Connect timeout = 100 ms
Read timeout    = 500 ms
```

The exact values depend on the service's latency SLO and request path.

### Interview point

> **Timeouts prevent a slow dependency from consuming resources indefinitely.**

---

# 2. Add Retries — But Carefully

A temporary network failure doesn't necessarily mean the service is permanently down.

```text
Request
   |
   v
Service B
   |
   X
   |
 Retry 1
   |
   X
   |
 Retry 2
   |
   X
   |
Fallback
```

But **retries can make an outage worse**.

Suppose 1,000 requests arrive:

```text
1,000 original requests
       |
       +-- Retry
       +-- Retry
       +-- Retry
```

The downstream could suddenly receive:

```text
3,000–4,000 requests
```

This is called a **retry storm**.

### Therefore:

Use:

- limited retry count
- exponential backoff
- jitter
- retry only transient failures
- retry only idempotent/safe operations where appropriate

Example:

```text
Attempt 1 -> immediately
Attempt 2 -> 100 ms
Attempt 3 -> 200 ms
Attempt 4 -> 400 ms
```

Add random jitter:

```text
delay = exponential_backoff + random_jitter
```

This prevents many clients from retrying simultaneously.

---

# 3. Circuit Breaker

This is one of the most important patterns for this question.

A circuit breaker prevents your application from continuously calling a known-failing dependency.

It has three main states:

```text
             failures
CLOSED -----------------> OPEN
   ^                        |
   |                        |
   |                    timeout
   |                        |
   |                        v
   +------------------- HALF-OPEN
```

## CLOSED

Everything is working normally.

```text
Service A ---> Service B
                |
                v
             Success
```

Requests flow normally.

---

## OPEN

Suppose Service B starts failing repeatedly.

```text
Service B
   |
   X
   X
   X
   X
```

Circuit breaker opens:

```text
Service A
   |
   v
Circuit Breaker
   |
   X
   |
   v
Fallback
```

The application **doesn't even call Service B**.

This protects the failing service and your own resources.

---

## HALF-OPEN

After some recovery period, allow a small number of test requests.

```text
Circuit
   |
   v
HALF-OPEN
   |
   +---- Test request
            |
        +---+---+
        |       |
     Success   Fail
        |       |
        v       v
     CLOSED    OPEN
```

If Service B recovered:

```text
HALF-OPEN -> CLOSED
```

If it is still failing:

```text
HALF-OPEN -> OPEN
```

---

# 4. Bulkheads

Bulkhead isolation prevents one failing dependency from consuming **all available resources**.

Think of a ship:

```text
+-----------------------------+
| Compartment A | Compartment B|
| Service B     | Service C    |
+-----------------------------+
```

If compartment A floods, B can continue operating.

In software:

```text
Application
 |
 +-- Thread Pool A --> Service B
 |
 +-- Thread Pool B --> Service C
 |
 +-- Thread Pool C --> Database
```

Suppose Service B becomes extremely slow:

```text
Service B
   |
   v
Thread Pool A
   |
   X exhausted
```

Service C can still use:

```text
Thread Pool B
```

This prevents **resource exhaustion from cascading**.

---

# 5. Graceful Degradation

Not every feature needs to be available for the entire application to remain useful.

Suppose an e-commerce system has:

```text
Product Service
Pricing Service
Recommendation Service
Review Service
Payment Service
```

Recommendation Service fails:

```text
Product page
   |
   +--> Product information  ✓
   +--> Price                ✓
   +--> Reviews              ✓
   +--> Recommendations     ❌
```

Instead of:

```text
HTTP 500
```

return:

```text
Product information
Price
Reviews

Recommendations temporarily unavailable
```

The core functionality remains available.

---

# 6. Fallbacks

A fallback provides an alternative response when the downstream is unavailable.

Example:

```text
Recommendation Service
          |
          X
          |
          v
      Redis Cache
          |
          v
 Previous recommendations
```

Or:

```text
Live Pricing Service
       |
       X
       |
       v
Cached price
```

Or simply:

```text
Service unavailable
```

depending on the business requirement.

### Important

A fallback should be **safe and meaningful**.

Don't return incorrect business data just to avoid an error.

---

# 7. Combine the Patterns

A production request might look like:

```text
                    +----------------+
                    |     Client     |
                    +-------+--------+
                            |
                            v
                    +----------------+
                    | API Service A  |
                    +-------+--------+
                            |
                    +-------+-------+
                    |               |
                    v               v
              Service B        Service C
                    |               |
             +------+-----+         |
             |            |         |
          Timeout      Retry        |
             |            |         |
             +------+-----+         |
                    |               |
              Circuit Breaker       |
                    |               |
                Bulkhead            |
                    |               |
                    v               v
                Fallback         Response
```

A typical request flow:

```text
Request
   |
   v
Timeout
   |
   v
Retry transient failure
   |
   v
Still failing?
   |
   v
Circuit Breaker
   |
   v
Fallback
```

---

# Example: Payment Service Failure

Imagine:

```text
Order Service ---> Payment Service
```

Payment Service becomes unavailable.

### Without resilience

```text
Order Request
      |
      v
Payment Service
      |
      X
      |
      v
Timeout
      |
      v
Order Service
      |
      v
500 Error
```

Every request waits for the failing service.

---

### With resilience

```text
Order Request
      |
      v
Payment Service
      |
      X
      |
   Timeout
      |
      v
 Retry
      |
      X
      |
      v
Circuit Breaker
      |
      v
Fallback
```

For payment, however, the fallback **cannot simply pretend that payment succeeded**.

Instead:

```text
Order
  |
  v
Payment unavailable
  |
  v
Order = PAYMENT_PENDING
```

Then an asynchronous mechanism can retry payment later.

This is an important distinction:

> **Graceful degradation must preserve business correctness.**

---

# 8. Asynchronous Processing

For operations that don't need an immediate response, decouple the services.

Instead of:

```text
Order Service
     |
     | synchronous
     v
Payment Service
```

use:

```text
Order Service
     |
     v
Message Queue / Kafka
     |
     v
Payment Worker
     |
     v
Payment Service
```

If Payment Service is temporarily down:

```text
Order Service
     |
     v
Queue
     |
     +--> Payment Service ❌
```

The message remains available for later processing.

When the service recovers:

```text
Queue
  |
  v
Payment Worker
  |
  v
Payment Service ✓
```

This is particularly useful for **eventual-consistency workflows**.

---

# 9. Idempotency

Retries introduce another problem.

Suppose:

```text
POST /payment
```

The client sends:

```text
Pay ₹10,000
```

Payment succeeds, but the response is lost:

```text
Payment Service
      |
      v
Payment SUCCESS
      |
      X Response lost
```

Client retries.

Without idempotency:

```text
Payment 1 -> ₹10,000
Payment 2 -> ₹10,000
```

The customer could be charged twice.

Use an idempotency key:

```text
Idempotency-Key: abc123
```

Then:

```text
Request abc123
       |
       v
Payment Service
       |
       v
Already processed?
       |
      YES
       |
       v
Return previous result
```

This is critical for payment/order APIs.

---

# 10. Rate Limiting

When a downstream is struggling, don't allow unlimited traffic toward it.

```text
Clients
   |
   v
Rate Limiter
   |
   +---- allowed ---> Service
   |
   +---- rejected --> 429
```

This protects both your service and downstream dependencies.

---

# 11. Observability

You cannot build resilience effectively without knowing when failures occur.

Monitor:

```text
Latency
Error rate
Timeout rate
Retry count
Circuit state
Request volume
Queue depth
Thread-pool utilization
```

For example:

```text
Service B

Error Rate       = 35%
P95 Latency      = 2.8 sec
Timeouts         = increasing
Circuit          = OPEN
```

This tells operators that the dependency is unhealthy and traffic is being blocked.

---

# Complete Production Architecture

A strong interview architecture could look like:

```text
                           Client
                             |
                             v
                      +-------------+
                      | API Gateway |
                      +------+------+
                             |
                             v
                      +-------------+
                      | Order Svc   |
                      +------+------+
                             |
                     +-------+-------+
                     |               |
                     v               v
              +-------------+  +-------------+
              | Payment Svc |  | Product Svc |
              +-------------+  +-------------+
                     |
               Timeout
                     |
               Retry + Backoff
                     |
               Circuit Breaker
                     |
               Bulkhead
                     |
             +-------+-------+
             |               |
          Service         Fallback
          healthy           |
             |               v
             |           Cache/Queue
             |
             v
          Response
```

For asynchronous operations:

```text
Order Service
      |
      v
 Kafka / Queue
      |
      v
Payment Worker
      |
      v
Payment Service
```

---

# What Happens During an Actual Outage?

Suppose Payment Service starts failing.

### Step 1 — Timeout

Don't wait forever.

```text
500 ms -> timeout
```

### Step 2 — Limited Retry

```text
Retry 1 -> failure
Retry 2 -> failure
```

with exponential backoff + jitter.

### Step 3 — Circuit Opens

```text
CLOSED
   |
   v
OPEN
```

Further requests don't hit Payment Service.

### Step 4 — Bulkhead Protects Resources

Payment-related threads/connections cannot consume resources needed by other functionality.

### Step 5 — Graceful Fallback

For a payment workflow:

```text
PAYMENT_PENDING
```

rather than falsely reporting success.

### Step 6 — Asynchronous Retry

```text
Queue
  |
  v
Payment Worker
  |
  v
Payment Service
```

### Step 7 — Recovery

Circuit enters:

```text
HALF-OPEN
```

A few requests are tested.

If successful:

```text
HALF-OPEN -> CLOSED
```

Normal traffic resumes.

---

# Key Difference Between the Patterns

| Pattern | Main Purpose |
|---|---|
| **Timeout** | Don't wait indefinitely |
| **Retry** | Recover from transient failures |
| **Backoff + Jitter** | Prevent retry storms |
| **Circuit Breaker** | Stop calling a failing dependency |
| **Bulkhead** | Isolate resources |
| **Fallback** | Provide alternative behavior |
| **Rate Limiter** | Control traffic |
| **Queue/Kafka** | Decouple services |
| **Idempotency** | Make retries safe |
| **Graceful Degradation** | Keep core functionality available |
| **Observability** | Detect and diagnose failures |

---

# Interview-Ready Answer

If the interviewer asks this as a system-design question, a strong concise answer is:

> **I would assume downstream failures are inevitable and prevent them from cascading into my service. First, I would configure strict connection and read timeouts. For transient failures, I'd use a small number of retries with exponential backoff and jitter. I'd put a circuit breaker around the dependency so repeated failures cause the circuit to open and stop sending traffic. I'd use bulkheads or separate connection/thread pools so a failing dependency cannot exhaust resources needed by other operations. For non-critical functionality, I'd provide a fallback or cached response and gracefully degrade the feature. For operations that can be asynchronous, I'd decouple them using a queue such as Kafka. For retryable operations like payments, I'd also use idempotency keys to prevent duplicate processing. Finally, I'd monitor latency, errors, retries, circuit state, and resource utilization so the system can detect and recover from failures.**

### Remember the flow

```text
        DOWNSTREAM FAILURE
                |
                v
             TIMEOUT
                |
                v
        LIMITED RETRIES
       (backoff + jitter)
                |
                v
         CIRCUIT BREAKER
                |
        +-------+-------+
        |               |
     OPEN           FALLBACK
        |               |
        v               v
     Stop calls      Cache/Queue
        |
        v
     BULKHEAD
        |
        v
   Protect resources
```

**Core principle:**

> **Fail fast, isolate the failure, retry carefully, degrade gracefully, and recover automatically.**