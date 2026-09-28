## Title: How Do You Prevent Duplicate Processing in a Distributed System?

**Category:** Distributed Systems & Event Processing  
**Difficulty:** Hard  
**Description:** A practical guide to idempotency, deduplication, unique constraints, retries, and transactional patterns for preventing duplicate business actions.

## Question

How would you prevent **duplicate processing** in a distributed system?

## Short Answer

I assume duplicate delivery can happen because of retries, network timeouts, message redelivery, crashes, or concurrent consumers.

I prevent duplicate business actions through:

- Stable idempotency keys
- Durable deduplication records
- Database unique constraints
- Idempotent API and consumer design
- Transactional outbox pattern
- Kafka consumer-offset management
- Distributed locking only when truly necessary

The target is usually not “messages are delivered once.” The target is:

> A message may arrive multiple times, but the business outcome happens only once.

## Core Idea

```text
Client / Producer
      ↓
Request or Event with Idempotency Key
      ↓
API / Consumer
      ↓
Deduplication Store
      ├── Key already processed → return prior result
      └── New key → process action
                       ↓
               Persist outcome atomically
                       ↓
             Mark operation successful
```

## Why Duplicate Processing Happens

Distributed systems are unreliable at boundaries.

```text
Producer sends event
      ↓
Consumer receives event
      ↓
Consumer processes successfully
      ↓
Consumer crashes before acknowledging offset
      ↓
Broker redelivers same event
```

Or:

```text
API calls payment service
      ↓
Payment service succeeds
      ↓
Response is lost due to timeout
      ↓
API retries request
      ↓
Payment may happen twice ❌
```

Typical causes:

| Cause | Duplicate Risk |
|---|---|
| Network timeout | Caller does not know whether action succeeded |
| Retry policy | Same request is sent again |
| Kafka redelivery | Offset was not committed |
| Service crash | Work completed but state was not acknowledged |
| Concurrent consumers | Two nodes process same business request |
| Client double-click | Same request is submitted twice |
| Queue visibility timeout | Message becomes available again |
| Failover | New instance repeats unfinished work |

## 1. Use an Idempotency Key

An idempotency key identifies one intended business operation.

```text
Bad:
random UUID generated on every retry

Good:
invoiceId + action + originalRequestId
```

Example:

```text
invoice:INV-101:approve:req-42
```

The retry must reuse the same key.

```http
POST /invoices/INV-101/approve
Idempotency-Key: invoice:INV-101:approve:req-42
```

Processing behavior:

```text
First request:
Key does not exist
      ↓
Approve invoice
      ↓
Save result
      ↓
Return success

Retry:
Same key exists
      ↓
Return previous result
      ↓
Do not approve again
```

## 2. Store Idempotency State Durably

Do not keep idempotency only in memory.

```text
Server restarts
      ↓
Memory is lost
      ↓
Duplicate request is processed again ❌
```

Use a durable store such as SQL.

```sql
CREATE TABLE idempotency_operations (
    idempotency_key VARCHAR(255) PRIMARY KEY,
    request_hash VARCHAR(64) NOT NULL,
    status VARCHAR(30) NOT NULL,
    result_reference VARCHAR(255),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

Possible states:

```text
PENDING
SUCCESS
FAILED
```

```text
Request
   ↓
Create PENDING idempotency record
   ↓
Execute business action
   ↓
Update record to SUCCESS
```

## 3. Use a Unique Constraint

The database must enforce uniqueness.

Bad approach:

```text
Consumer A → check if key exists → no
Consumer B → check if key exists → no
Consumer A → process
Consumer B → process ❌
```

Better approach:

```text
Consumer A → INSERT idempotency key → succeeds
Consumer B → INSERT same key → duplicate-key error
```

```sql
ALTER TABLE idempotency_operations
ADD CONSTRAINT uq_idempotency_key
UNIQUE (idempotency_key);
```

The database constraint is the actual concurrency control.

## Java Example: Idempotent Spring Boot API

```java
@PostMapping("/invoices/{invoiceId}/approve")
@Transactional
public ResponseEntity<ApprovalResult> approve(
        @PathVariable String invoiceId,
        @RequestHeader("Idempotency-Key") String key) {

    try {
        idempotencyRepository.insertPending(key);

    } catch (DuplicateKeyException ex) {
        ApprovalResult previousResult =
            idempotencyRepository.findResultByKey(key);

        return ResponseEntity.ok(previousResult);
    }

    ApprovalResult result =
        invoiceService.approveInvoice(invoiceId);

    idempotencyRepository.markSuccess(
        key,
        result.approvalId()
    );

    return ResponseEntity.ok(result);
}
```

Production improvement:

```text
Idempotency record insertion
      +
Invoice status update
      +
Audit record creation
```

should occur in one local database transaction.

## Python Example: Idempotent Event Consumer

```python
def process_event(event, db):
    key = event["idempotency_key"]

    try:
        db.execute(
            """
            INSERT INTO processed_events
                (idempotency_key, event_id, status)
            VALUES
                (%s, %s, 'PROCESSING')
            """,
            [key, event["event_id"]],
        )
    except DuplicateKeyError:
        return {
            "status": "already_processed"
        }

    result = validate_invoice(event["invoice_id"])

    db.execute(
        """
        UPDATE processed_events
        SET status = 'SUCCESS',
            result_reference = %s
        WHERE idempotency_key = %s
        """,
        [result["report_id"], key],
    )

    return result
```

## 4. Make Consumers Idempotent

Every Kafka or queue consumer should assume:

```text
The same message can arrive again.
```

Example event:

```json
{
  "eventId": "evt-991",
  "idempotencyKey": "invoice:INV-101:validate:req-42",
  "invoiceId": "INV-101",
  "eventType": "invoice.received"
}
```

Consumer logic:

```text
Receive event
   ↓
Try to insert event ID / idempotency key
   ├── Duplicate → ignore or return stored result
   └── New → process event
```

For some use cases, an upsert is naturally idempotent:

```sql
UPDATE invoices
SET validation_status = 'VALIDATED'
WHERE invoice_id = 'INV-101';
```

Setting a status to the same value repeatedly is safer than:

```text
Increment invoice-processing count
```

because increments are not idempotent.

## 5. Use the Transactional Outbox Pattern

A common failure occurs during a dual write.

Bad approach:

```text
Save invoice in SQL
      ↓
Publish Kafka event
```

Failure case:

```text
Database commit succeeds
Kafka publish fails
      ↓
Invoice exists, but downstream processing never starts ❌
```

Better approach:

```text
Single SQL transaction
   ├── Save invoice
   └── Save outbox event
          ↓
Outbox relay / CDC
          ↓
Kafka topic
```

```text
Application
      ↓
SQL Transaction
   ├── invoices table
   └── outbox_events table
          ↓
Kafka relay publishes event
```

If the relay publishes an event more than once, consumers still deduplicate using the event ID or idempotency key.

## 6. Use Optimistic Locking for Concurrent Updates

For concurrent business updates, use a version field.

```text
Invoice version = 5

Reviewer A approves invoice using version 5
Reviewer B rejects invoice using version 5
```

Only one update should succeed.

```java
@Entity
public class Invoice {

    @Id
    private String invoiceId;

    @Version
    private Long version;

    private String status;
}
```

```text
Reviewer A update succeeds → version becomes 6
Reviewer B update fails → stale version conflict
```

This prevents one user or service from silently overwriting another decision.

## 7. Use Distributed Locks Carefully

A distributed lock can prevent two instances from running the same work at once.

```text
Worker A acquires lock for invoice INV-101
      ↓
Worker B cannot process INV-101 until lock expires/releases
```

Redis is sometimes used for this.

But locks are not the first choice for business correctness because they can fail due to:

- Lock expiration during slow work
- Node crashes
- Clock/network issues
- Incorrect release logic
- Split-brain behavior

Prefer:

```text
Unique database constraint
+ idempotency key
+ transactional state
```

Use distributed locks mainly for coordination, such as ensuring only one scheduled index refresh runs per tenant.

## 8. Handle External Side Effects

External calls need their own idempotency support.

```text
Kafka event
      ↓
Payment API
      ↓
Payment succeeds
      ↓
Consumer crashes before saving result
      ↓
Event is retried
```

The payment API should receive the same key:

```http
POST /payments
Idempotency-Key: payment:INV-101:req-42
```

```text
Retry with same key
      ↓
Payment API returns existing payment ID
      ↓
No second payment
```

If the external service does not support idempotency:

- Store an operation record before calling it
- Query its status using a stable external reference
- Use a reconciliation job
- Require manual review for uncertain high-risk cases
- Avoid automatic retries for irreversible actions

## 9. Design Retry Policies Carefully

| Error Type | Retry? | Example |
|---|---|---|
| Network timeout | Yes, bounded | ERP temporarily unavailable |
| HTTP 429 | Yes, respect retry-after | LLM/provider throttling |
| HTTP 503 | Yes, with backoff | Temporary service outage |
| Invalid request | No | Schema validation failure |
| Authorization failure | No | Missing OAuth scope |
| Business rejection | No | Invoice already rejected |
| Duplicate key | No new action | Return stored result |

Use exponential backoff with jitter:

```text
Attempt 1 → wait 1 second
Attempt 2 → wait 2 seconds
Attempt 3 → wait 4 seconds
```

Jitter prevents many services from retrying simultaneously.

## Example: Invoice Auditor

```text
Invoice uploaded
      ↓
Create SQL invoice record
      ↓
Create outbox event with event ID
      ↓
Kafka: invoice.received
      ↓
Validation consumer receives event
      ↓
Insert processed-event record
      ├── New event → validate invoice
      └── Duplicate event → return previous result
      ↓
Save validation status + audit report
      ↓
Publish invoice.validated event
```

```text
Same Kafka event arrives again
      ↓
Same idempotency key
      ↓
Processed event exists
      ↓
No duplicate validation report or approval action
```

## Common Mistakes

### 1. Relying Only on Kafka Offset Commit

Offset commit alone does not protect external database or API actions.

```text
Business update succeeds
      ↓
Offset commit fails
      ↓
Kafka retries event
```

The consumer must still be idempotent.

### 2. Generating a New Key on Every Retry

```text
Attempt 1 → key-1
Attempt 2 → key-2
```

The backend sees two separate operations.

The key must represent the original business intent.

### 3. Using a Cache as the Only Deduplication Store

Redis can help with short-term deduplication, but cache eviction or restart may allow duplicates.

For critical work:

```text
Use SQL unique constraint / durable operation record
```

### 4. Blindly Retrying Mutating Calls

Never automatically retry a payment, email, ticket creation, or approval unless the downstream operation is idempotent.

## Interview-Ready Answer

> In a distributed system, I assume duplicate messages and retries can happen. I design for at-least-once delivery but effectively-once business outcomes.

> Each business operation gets a stable idempotency key. The service stores that key and the final result in a durable database with a unique constraint. If the same request or Kafka event arrives again, the service returns the stored result instead of performing the action again.

> I make consumers idempotent, use transactional outbox for reliable database-to-Kafka publication, use optimistic locking for concurrent updates, and apply retries only to transient failures. For external systems such as payment or ERP APIs, I propagate the same idempotency key or reconcile using a stable external reference.

> I use distributed locks only for coordination when necessary. For correctness, durable state and unique constraints are more reliable than trusting locks or message offsets alone.