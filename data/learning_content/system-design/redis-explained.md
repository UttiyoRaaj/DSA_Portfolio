---
title: Redis Explained
category: System Design Fundamentals
difficulty: Intermediate
description: A concise explanation of Redis, why it is extremely fast despite being primarily single-threaded, and when to use it in production.
---

## Question

What is **Redis**? Why is it used in system design?

## Short Answer

**Redis** is an in-memory key-value data store commonly used as a **cache, session store, distributed lock, counter, queue, and fast data-access layer**.

It is extremely fast because most operations happen **in memory**, avoiding disk/database latency. Redis historically processed commands through a primarily **single-threaded command-execution model**, which simplifies concurrency and avoids many locking costs. Modern Redis can also use additional threads for networking and some background work.

## Core Idea

Instead of every request going directly to a slower database:

```text
Client
   |
   v
Application
   |
   v
Redis Cache
   |
   +---- Cache Hit ----> Return Data
   |
   +---- Cache Miss
             |
             v
          Database
             |
             v
       Store in Redis
             |
             v
          Return Data
```

The main idea is:

> **Keep frequently accessed data close to the application and in memory.**

---

## Why Is Redis So Fast?

### 1. Data is primarily stored in RAM

Traditional databases often involve:

```text
Application -> Database -> Disk / Storage
```

Redis primarily works with:

```text
Application -> RAM
```

RAM access is much faster than disk-based I/O.

For example:

```text
Redis:
GET user:101
        |
        v
      RAM
        |
        v
     Result
```

---

### 2. Simple data structures

Redis is optimized for operations such as:

```text
GET
SET
INCR
DEL
HGET
LPUSH
SADD
```

Many operations have very low algorithmic complexity.

For example:

```text
SET user:101 "Rana"
GET user:101
```

Hash-table based key lookup is approximately:

```text
O(1) average
```

So Redis can process a very large number of simple operations efficiently.

---

## Why Single-Threaded?

This is one of the most common interview questions.

The traditional Redis architecture used a **single main thread for executing commands**.

```text
             Redis
               |
       Command Execution
               |
        +------+------+
        |             |
      GET            SET
        |             |
       RAM           RAM
```

Why?

Because Redis operations are generally:

- very fast
- memory-based
- short-running
- simple

Redis doesn't want multiple threads simultaneously modifying the same data structures and constantly fighting over locks.

### Example

With multiple worker threads:

```text
Thread 1 ----\
Thread 2 -----+--> Shared Redis Data
Thread 3 ----/
```

You may need:

```text
locks
mutexes
synchronization
context switching
```

Redis's single command-execution thread can instead process commands sequentially:

```text
GET
 |
SET
 |
INCR
 |
HGET
 |
DEL
```

This provides a simple concurrency model.

---

## Does Single-Threaded Mean Redis Uses Only One CPU Core?

**No.**

This is an important modern distinction.

"Redis is single-threaded" usually refers to the **core command execution model**, not that every part of Redis can use only one CPU core.

Modern Redis versions can use multiple threads for things such as:

- network I/O
- background operations
- persistence-related work
- other internal tasks

So in an interview, say:

> **Redis's core command processing has traditionally been single-threaded, while modern Redis can use multiple threads for networking and other background activities.**

---

## How Can Single-Threaded Redis Handle High Traffic?

Suppose requests arrive:

```text
10,000 requests/sec
```

Redis doesn't necessarily need 10,000 threads.

Instead:

```text
Requests
   |
   v
Event Loop
   |
   +--> GET
   +--> SET
   +--> INCR
   +--> GET
   +--> HGET
   |
   v
  RAM
```

The operations are extremely short.

The event-driven model allows Redis to process many requests efficiently without creating a thread for every request.

---

## Why Doesn't Redis Become Slow?

The biggest advantage is that Redis operations should generally be **small and fast**.

For example:

```text
GET user:123
```

is cheap.

But if you execute a computationally expensive operation that blocks the Redis event loop, other commands can wait.

Therefore:

> **Redis is extremely fast when used for the operations it is designed for—not because single-threading magically makes everything fast.**

---

# When Do We Use Redis in Production?

Redis is commonly introduced when the database or service is becoming a bottleneck due to repeated access to the same data.

### 1. Caching

Most common use case.

```text
Client
   |
   v
Application
   |
   v
Redis
   |
   | Cache Hit
   v
Response

Cache Miss
   |
   v
Database
```

Example:

```text
GET product:1001
```

Instead of repeatedly querying:

```text
PostgreSQL
   |
SELECT * FROM products WHERE id = 1001
```

you can cache the product.

### Good candidates

- product information
- user profile
- configuration
- frequently accessed reference data
- API responses
- expensive computation results

---

# 2. Session Management

Instead of storing sessions only inside one application server:

```text
User
 |
 +--> Server 1
 +--> Server 2
 +--> Server 3
```

store session data centrally:

```text
Server 1 ----\
Server 2 -----+--> Redis
Server 3 ----/
```

Now any application instance can retrieve the session.

This is particularly useful when running multiple instances behind a load balancer.

---

# 3. Distributed Locks

Suppose two application instances attempt the same operation:

```text
Server A ----\
              \
               Redis Lock
              /
Server B ----/
```

Redis can be used to coordinate access to a shared resource.

Example:

```text
lock:payment:123
```

This can help prevent two workers from processing the same operation simultaneously.

**Important:** distributed locking needs careful design; simply doing `SET` without an appropriate expiration/ownership strategy is not sufficient.

---

# 4. Counters

Redis provides atomic operations such as:

```text
INCR
```

Example:

```text
INCR page_views
```

Useful for:

- view counters
- API usage counters
- quotas
- metrics
- rate limiting

---

# 5. Rate Limiting

Example:

```text
User
 |
 v
API Gateway
 |
 v
Redis
```

Redis can maintain request counters:

```text
rate:user:101 = 87
```

For example:

```text
Maximum = 100 requests/minute
```

Redis's atomic increment operations make this pattern practical.

---

# 6. Leaderboards

Redis sorted sets are useful for ranking systems.

Example:

```text
ZADD leaderboard 950 user1
ZADD leaderboard 875 user2
ZADD leaderboard 990 user3
```

Conceptually:

```text
Leaderboard

1. user3   990
2. user1   950
3. user2   875
```

This is useful for:

- gaming leaderboards
- rankings
- scores
- priority systems

---

# 7. Queues / Background Processing

Redis data structures can also support queue-like workloads.

```text
Producer
   |
   v
 Redis Queue
   |
   +----> Worker 1
   +----> Worker 2
   +----> Worker 3
```

For more sophisticated messaging requirements, dedicated systems such as Kafka or RabbitMQ may be more appropriate.

---

# How Redis Fits Into a Production Architecture

A typical Spring Boot application might look like:

```text
                    +----------------+
                    |    Clients     |
                    +-------+--------+
                            |
                            v
                    +----------------+
                    | Load Balancer  |
                    +-------+--------+
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
          Spring Boot   Spring Boot   Spring Boot
           Instance 1    Instance 2    Instance 3
              |             |             |
              +-------------+-------------+
                            |
                            v
                       +---------+
                       |  Redis  |
                       +----+----+
                            |
                      Cache Miss
                            |
                            v
                       +---------+
                       |   DB    |
                       +---------+
```

Redis becomes a **shared fast-access layer** between your application and database.

---

# Redis vs Database

| Redis | PostgreSQL / MySQL / Oracle |
|---|---|
| Primarily in-memory | Primarily persistent storage |
| Extremely low latency | Higher latency |
| Excellent for caching | Excellent for durable data |
| Key-value/data structures | Relational queries |
| Often used as a secondary layer | Usually system of record |
| Data can be evicted | Data normally persists |
| Limited query capability compared with SQL DB | Rich SQL/query capabilities |

### Important production principle

**Do not automatically replace your database with Redis.**

Usually:

```text
Database = Source of Truth
Redis    = Fast Access Layer
```

---

# What Happens on a Cache Miss?

Suppose:

```text
GET user:101
```

Redis doesn't have it.

```text
Application
     |
     v
   Redis
     |
  MISS
     |
     v
 Database
     |
     v
 User Data
     |
     +------> Redis SET
     |
     v
 Response
```

This is commonly called **cache-aside** or **lazy caching**.

Pseudo-code:

```java
User user = redis.get("user:101");

if (user == null) {
    user = database.findUser(101);
    redis.set("user:101", user);
}

return user;
```

---

# What If Data Changes?

This is where production Redis design becomes more interesting.

Suppose:

```text
Database:
user.name = "Rana"
```

Redis also has:

```text
user:101 -> "Rana"
```

Then application updates the database:

```text
user.name = "Rahul"
```

But Redis still contains:

```text
user:101 -> "Rana"
```

Now you have **stale cache data**.

A common approach is:

```text
Update DB
   |
   v
Delete/Invalidate Redis Cache
```

```java
database.update(user);
redis.delete("user:101");
```

The next request causes a cache miss and reloads the new value.

---

# When Should You NOT Use Redis?

Don't introduce Redis simply because:

> "Redis is fast."

It adds another distributed component and therefore additional operational complexity.

Avoid unnecessary Redis when:

- database performance is already sufficient
- data is rarely accessed
- caching doesn't provide meaningful benefit
- data must always be strongly consistent
- the workload requires complex relational queries
- the data doesn't fit an appropriate Redis usage pattern

---

# Key Production Concerns

When using Redis in production, think about:

### 1. TTL

Don't necessarily keep cache entries forever.

```text
user:101
TTL = 10 minutes
```

After expiration:

```text
Redis -> MISS -> Database -> Redis
```

---

### 2. Eviction

Redis has limited memory.

If memory becomes full, configured eviction policies determine what happens to cached data.

Examples include policies based on:

```text
LRU
LFU
TTL
```

---

### 3. Persistence

Redis can also persist data using mechanisms such as:

```text
RDB
AOF
```

But the appropriate persistence configuration depends on whether Redis is being used as:

```text
cache
```

or

```text
important data store
```

---

### 4. High Availability

For production systems requiring availability, Redis can be deployed with mechanisms such as:

```text
Primary
   |
   +---- Replica
   |
   +---- Replica
```

and Redis Sentinel or Redis Cluster depending on requirements.

---

### 5. Cache Stampede

Suppose a very popular cache entry expires:

```text
Redis key expires
       |
       v
10,000 requests
       |
       +----> Database
       +----> Database
       +----> Database
       +----> Database
```

Now the database receives a sudden huge load.

Solutions include:

- locking
- request coalescing
- early refresh
- randomized TTLs
- appropriate cache warming

---

# Interview Answer

If an interviewer asks:

**"Why is Redis so fast despite being single-threaded?"**

A concise answer is:

> **Redis is primarily an in-memory data store, so it avoids most disk I/O. Its core command execution has traditionally been single-threaded, which simplifies concurrency and avoids lock contention. Redis uses an event-driven architecture to efficiently process many short operations, and modern Redis can also use multiple threads for networking and other background tasks. Its speed comes mainly from in-memory access, efficient data structures, and a lightweight execution model—not simply from being single-threaded.**

### Remember

```text
Redis
 |
 +-- In-memory       -> Very low latency
 |
 +-- Simple commands -> Efficient operations
 |
 +-- Event-driven     -> Handles many connections
 |
 +-- Single command execution model
 |                    -> Simple concurrency
 |
 +-- Production uses
      |
      +-- Cache
      +-- Sessions
      +-- Rate limiting
      +-- Counters
      +-- Locks
      +-- Leaderboards
      +-- Queues
```

**Interview takeaway:** Redis is usually not your primary database. Think of it as a **very fast shared data layer** that you introduce when low-latency access, caching, coordination, or high-frequency operations justify the additional infrastructure.