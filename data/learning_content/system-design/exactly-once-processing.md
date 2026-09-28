## Title: How Do You Design Exactly-Once Processing? Is It Really Possible?

**Category:** Distributed Systems & Event Processing  
**Difficulty:** Hard  
**Description:** How to reason about duplicates, idempotency, Kafka transactions, and the realistic limits of “exactly-once” guarantees.

## Question

How do you design a system that guarantees **exactly-once processing**? Is exactly-once really possible?

## Short Answer

True exactly-once processing across all distributed systems is extremely difficult and often impossible to guarantee end-to-end.

In practice, systems usually provide **at-least-once delivery** and achieve an **effectively-once business outcome** through:

- Idempotency keys
- Durable operation records
- Database uniqueness constraints
- Transactions
- Kafka transactions where applicable
- Transactional outbox pattern
- Deduplication at consumers

The key idea is:

> A message may arrive more than once, but the business action must happen only once.

## Core Idea

```text
Producer
   ↓
Kafka Topic
   ↓
Consumer receives message
   ↓
Check idempotency / processed-event store
   ├── Already processed → return stored result
   └── New event → process safely
                     ↓
               Persist result
                     ↓
              Mark event processed
```

## Why Exactly-Once Is Difficult

Distributed systems can fail at any point.

```text
Consumer receives event
        ↓
Consumer writes payment to database
        ↓
Consumer crashes before committing Kafka offset
        ↓
Kafka sends same event again
```

When the consumer restarts, Kafka does not know whether the database write succeeded.

```text
Kafka sees:
“Offset was not committed”
        ↓
Retry event

Database sees:
“Payment may already exist”
```

Without protection, this can create duplicate business actions.

```text
Event: Create payment for invoice INV-101
        ↓
First attempt → Payment created
        ↓
Crash before offset commit
        ↓
Second attempt → Payment created again ❌
```

## Delivery Semantics

| Delivery Type | Meaning | Risk |
|---|---|---|
| At-most-once | Process zero or one time | Messages can be lost |
| At-least-once | Process one or more times | Duplicates are possible |
| Exactly-once | Process one time only | Difficult across distributed systems |

Most event-driven systems are designed around **at-least-once delivery**.

## The Practical Solution: Idempotency

Idempotency means repeating the same request produces the same final business result.

Example:

```text
Operation:
Create payment for INV-101

Idempotency key:
payment:INV-101:request-8f2a
```

```text
First request:
POST /payments
Idempotency-Key: payment:INV-101:request-8f2a

Result:
Payment PAY-778 created
```

If the request is retried:

```text
Second request:
POST /payments
Idempotency-Key: payment:INV-101:request-8f2a

Result:
Return existing payment PAY-778
Do not create a second payment
```

## Idempotency Table

A database table can store completed operations.

```sql
CREATE TABLE processed_operations (
    idempotency_key VARCHAR(255) PRIMARY KEY,
    event_id VARCHAR(255) NOT NULL,
    status VARCHAR(30) NOT NULL,
    result_reference VARCHAR(255),
    created_at TIMESTAMP NOT NULL
);
```

Processing flow:

```text
Receive event
   ↓
Start database transaction
   ↓
Insert idempotency key
   ├── Insert succeeds → this is first processing attempt
   └── Duplicate key → operation already processed
   ↓
Perform business update
   ↓
Store final result
   ↓
Commit transaction
```

Example SQL logic:

```sql
INSERT INTO processed_operations (
    idempotency_key,
    event_id,
    status
)
VALUES (
    'payment:INV-101:request-8f2a',
    'event-991',
    'PROCESSING'
);
```

If this fails with a duplicate-key error:

```text
This operation was already processed.
Return stored result.
```

## Java Example: Idempotent Kafka Consumer

```java
@KafkaListener(
    topics = "payment.requested",
    groupId = "payment-service"
)
@Transactional
public void processPayment(PaymentRequested event) {

    if (processedOperationRepository.existsById(event.idempotencyKey())) {
        return; // Duplicate event: do nothing
    }

    processedOperationRepository.save(
        new ProcessedOperation(
            event.idempotencyKey(),
            event.eventId(),
            "PROCESSING"
        )
    );

    Payment payment = paymentService.createPayment(
        event.invoiceId(),
        event.amount()
    );

    processedOperationRepository.markSuccess(
        event.idempotencyKey(),
        payment.getId()
    );
}
```

Important improvement: use a database unique constraint on the idempotency key. Do not rely only on `existsById()` because two consumers could check at the same time.

```text
Consumer A → existsById = false
Consumer B → existsById = false
Consumer A → creates payment
Consumer B → creates payment ❌
```

The unique database constraint is the real protection.

## Better Java Pattern

```java
@Transactional
public PaymentResult process(PaymentRequested event) {
    try {
        processedOperationRepository.insertProcessing(
            event.idempotencyKey(),
            event.eventId()
        );
    } catch (DuplicateKeyException duplicate) {
        return processedOperationRepository
            .findById(event.idempotencyKey())
            .toResult();
    }

    Payment payment = paymentService.createPayment(
        event.invoiceId(),
        event.amount()
    );

    processedOperationRepository.markSuccess(
        event.idempotencyKey(),
        payment.getId()
    );

    return PaymentResult.success(payment.getId());
}
```

## Kafka Exactly-Once Semantics

Kafka supports **Exactly-Once Semantics (EOS)** for a specific Kafka workflow:

```text
Read from Kafka
   ↓
Process
   ↓
Write result to another Kafka topic
   ↓
Commit consumer offset
```

Kafka transactions can atomically commit:

- Produced records
- Consumer offset updates

```text
Input topic
   ↓
Kafka consumer
   ↓
Kafka transaction
   ├── Write output topic event
   └── Commit input offset
```

If the transaction fails:

```text
Output event is not visible
Offset is not committed
Input can be safely retried
```

This is strong—but its guarantee is mainly inside Kafka.

## Kafka Transaction Example

```java
@Transactional("kafkaTransactionManager")
public void processEvent(ConsumerRecord<String, InvoiceEvent> record) {

    InvoiceValidated validated = validate(record.value());

    kafkaTemplate.send(
        "invoice.validated",
        record.key(),
        validated
    );

    // Output event and consumed offset commit together
}
```

This is useful for:

```text
Kafka topic A
   ↓
Transform / enrich event
   ↓
Kafka topic B
```

## Where Kafka EOS Stops

Kafka cannot automatically make an external API, database, email, payment provider, or ERP system exactly-once.

```text
Kafka Consumer
   ↓
External payment API
   ↓
Payment succeeds
   ↓
Consumer crashes before Kafka transaction completes
```

On retry, Kafka may replay the event.

The external payment API must also support idempotency.

```text
Kafka retry
   ↓
Payment API receives same idempotency key
   ↓
Returns original payment result
```

## Transactional Outbox Pattern

The transactional outbox solves a common dual-write problem.

Bad approach:

```text
Save invoice to database
   ↓
Publish Kafka event
```

Failure case:

```text
Database save succeeds
Kafka publish fails
   ↓
Database and event stream become inconsistent ❌
```

Better approach:

```text
Single database transaction
   ├── Save invoice
   └── Save outbox event
        ↓
Outbox relay publishes event to Kafka
        ↓
Mark outbox event as published
```

```text
Invoice Database
   ├── invoices table
   └── outbox_events table
        ↓
Outbox Relay / CDC
        ↓
Kafka Topic
```

Even if the relay publishes the same event twice, consumers use idempotency.

## Python Example: Idempotent Consumer Logic

```python
def process_invoice_event(event, db):
    key = event["idempotency_key"]

    try:
        db.execute(
            """
            INSERT INTO processed_operations
                (idempotency_key, status)
            VALUES
                (%s, 'PROCESSING')
            """,
            [key],
        )
    except DuplicateKeyError:
        return db.fetch_one(
            """
            SELECT status, result_reference
            FROM processed_operations
            WHERE idempotency_key = %s
            """,
            [key],
        )

    result = validate_invoice(event["invoice_id"])

    db.execute(
        """
        UPDATE processed_operations
        SET status = 'SUCCESS',
            result_reference = %s
        WHERE idempotency_key = %s
        """,
        [result["report_id"], key],
    )

    return result
```

## Important Design Rules

### 1. Use a Stable Business Key

Bad key:

```text
random UUID created again on every retry
```

Good key:

```text
invoiceId + requestedAction + originalRequestId
```

Example:

```text
invoice:INV-101:approve:req-42
```

The same logical request must reuse the same idempotency key.

### 2. Make Consumers Idempotent

Every consumer should assume:

```text
This event can arrive again.
```

Use:

- Unique constraints
- Processed-event table
- Upsert operations
- Version numbers
- Conditional updates
- Idempotency keys

### 3. Keep Transactions Local

A database transaction is reliable within one database.

```text
Database transaction
   ├── Update invoice
   └── Insert outbox event
```

Avoid pretending one transaction can safely cover:

```text
Database + Kafka + ERP + Email + Payment Provider
```

Use idempotency, outbox, retries, and compensation instead.

### 4. Use Retry Carefully

Retry only transient failures:

```text
Timeout
Temporary network failure
Rate limit
Service unavailable
```

Do not repeatedly retry:

```text
Invalid invoice
Authorization failure
Schema validation failure
Business-rule rejection
```

Use bounded retries with exponential backoff and a dead-letter topic.

## Example: Invoice Auditor

```text
Invoice uploaded
      ↓
Create SQL invoice record
      ↓
Create outbox event in same transaction
      ↓
Publish invoice.received to Kafka
      ↓
Extraction consumer processes invoice
      ↓
Store extraction result + processed event key
      ↓
Publish extraction.completed
      ↓
Validation consumer processes once logically
```

If the same event arrives twice:

```text
Same event ID / idempotency key
      ↓
Processed operation exists
      ↓
Return prior result
      ↓
No duplicate report, validation, or payment action
```

## Is Exactly-Once Really Possible?

A strong answer is:

> Exactly-once is possible in limited, controlled boundaries—for example, Kafka can provide exactly-once semantics when consuming from Kafka and producing to Kafka within a Kafka transaction. However, true end-to-end exactly-once processing across independent databases, external APIs, payment systems, and network failures is usually not realistically guaranteed.

> In production, I design for at-least-once delivery and effectively-once business outcomes. I use idempotency keys, unique database constraints, transactional outbox, durable operation state, retries, dead-letter queues, and compensating actions where needed.

## Interview-Ready Answer

> I do not assume messages are delivered exactly once. I assume at-least-once delivery, which means a consumer may receive the same event again after a crash or timeout.

> To achieve an effectively-once business outcome, I assign a stable idempotency key to each business operation and persist it with a unique constraint. The consumer performs the business update and stores the operation result in a local database transaction. If the same event is retried, it returns the prior result instead of repeating the action.

> For database-to-Kafka consistency, I use the transactional outbox pattern. Kafka transactions can provide exactly-once semantics within Kafka read-process-write workflows, but external systems still need idempotent APIs. Therefore, end-to-end exactly-once is usually a design goal achieved through idempotency and durable state, not a guarantee I would claim blindly.