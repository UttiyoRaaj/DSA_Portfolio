## Title: Load Balancer vs API Gateway vs Reverse Proxy — When Do You Use Each?

**Category:** System Design & Microservices Architecture  
**Difficulty:** Intermediate  
**Description:** A practical comparison of traffic-distribution, API-management, and proxying layers in production systems.

## Question

What is the difference between a **load balancer**, **API gateway**, and **reverse proxy**? When would you use each in production?

## Short Answer

All three sit in front of backend services, but solve different problems:

- A **load balancer** distributes traffic across healthy service instances.
- A **reverse proxy** forwards client requests to backend services and can handle TLS termination, routing, caching, compression, and headers.
- An **API gateway** is an API-focused entry point that adds authentication, authorization, rate limiting, API versioning, request transformation, and observability.

In production, they are often used together.

## Core Idea

```text
Client
   ↓
CDN / WAF
   ↓
Load Balancer
   ↓
Reverse Proxy / Ingress
   ↓
API Gateway
   ↓
Microservices / AI Services / Databases
```

The exact order differs by cloud and platform. Sometimes one managed product performs more than one role.

## 1. What Is a Load Balancer?

A load balancer distributes incoming traffic across multiple healthy instances.

```text
Users
   ↓
Load Balancer
   ├── API Instance 1
   ├── API Instance 2
   ├── API Instance 3
   └── API Instance 4
```

Its primary goal is:

```text
High availability + traffic distribution + failover
```

If one instance fails its health check:

```text
Load Balancer
   ├── API Instance 1 ✅
   ├── API Instance 2 ❌ unhealthy
   ├── API Instance 3 ✅
   └── API Instance 4 ✅
```

The load balancer stops sending traffic to the unhealthy instance.

### Common Load-Balancing Algorithms

| Algorithm | How it works | Good for |
|---|---|---|
| Round robin | Requests rotate across instances | Similar-capacity services |
| Weighted round robin | More capable instances receive more traffic | Mixed instance sizes |
| Least connections | Routes to the least busy instance | Long-lived connections |
| IP hash | Same client tends to reach same instance | Session affinity cases |
| Least response time | Favors fastest backend | Latency-sensitive systems |

### Layer 4 vs Layer 7

| Type | Works at | Understands | Example use |
|---|---|---|---|
| Layer 4 load balancer | TCP/UDP | IP address and port | Very fast network routing |
| Layer 7 load balancer | HTTP/HTTPS | URL, headers, cookies, HTTP methods | Route `/api` and `/ai` differently |

Example Layer 7 routing:

```text
/api/*      → Java API service
/ai/*       → Python FastAPI service
/admin/*    → Admin service
```

## When to Use a Load Balancer

Use one when you need:

- Multiple instances of the same service
- High availability
- Health checks and failover
- Horizontal scaling
- Blue-green or canary deployment traffic routing
- Basic TLS termination
- Distribution of traffic across Kubernetes pods, VMs, or containers

For a sudden 100× traffic spike:

```text
More traffic
   ↓
Autoscaler creates more API instances
   ↓
Load balancer routes requests to new healthy instances
```

## 2. What Is a Reverse Proxy?

A reverse proxy sits in front of backend servers. The client talks to the proxy, and the proxy forwards the request to the correct backend.

```text
Client
   ↓
Reverse Proxy
   ├── Java Spring Boot Service
   ├── Python FastAPI AI Service
   └── React Static Frontend
```

The client does not directly know the internal service addresses.

### Common Reverse Proxy Responsibilities

- TLS/SSL termination
- URL-based routing
- Header injection or removal
- Compression
- Caching
- Static file serving
- Request-size limits
- Basic rate limiting
- Hiding internal service topology
- Forwarding client IP and trace headers

Common reverse proxies:

- NGINX
- Envoy
- HAProxy
- Traefik
- Kubernetes Ingress controllers

### Example NGINX Configuration

```nginx
server {
    listen 443 ssl;
    server_name app.example.com;

    location /api/ {
        proxy_pass http://spring-api:8080/;
        proxy_set_header X-Request-ID $request_id;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /ai/ {
        proxy_pass http://fastapi-ai-service:8000/;
        proxy_read_timeout 30s;
    }
}
```

This means:

```text
https://app.example.com/api/... → Spring Boot
https://app.example.com/ai/...  → FastAPI AI service
```

## When to Use a Reverse Proxy

Use one when you need:

- A single public domain for several internal services
- TLS termination
- URL/path routing
- Static frontend delivery
- Protection of internal IP addresses
- Header and request-size control
- Basic caching or compression
- Kubernetes ingress routing

For an Agentic AI application, request-size limits are useful because document uploads and large prompts can otherwise overload services.

## 3. What Is an API Gateway?

An API gateway is a specialized reverse proxy designed for managing APIs.

```text
Client Application
   ↓
API Gateway
   ├── Authentication
   ├── Authorization
   ├── Rate limiting
   ├── API versioning
   ├── Request validation
   ├── Logging / tracing
   ├── Request transformation
   └── Routing
          ↓
     Backend microservices
```

An API gateway is often the public entry point for mobile apps, web applications, partners, and external consumers.

### Common API Gateway Features

| Feature | Why it matters |
|---|---|
| Authentication | Verifies user or client identity |
| Authorization | Enforces allowed scopes and roles |
| Rate limiting | Prevents abuse and protects cost |
| API keys | Identifies external clients |
| OAuth/JWT validation | Secures protected APIs |
| API versioning | Supports `/v1` and `/v2` safely |
| Request validation | Rejects invalid payloads early |
| Request transformation | Adapts external API to internal services |
| API aggregation | Combines multiple service calls |
| Observability | Adds correlation IDs, logs, metrics |
| Quotas | Controls usage by client or tenant |
| WAF integration | Filters common attacks |

Common API gateways:

- Azure API Management
- AWS API Gateway
- Kong
- Apigee
- NGINX Plus
- Spring Cloud Gateway
- Envoy Gateway

## When to Use an API Gateway

Use one when you need:

- A secure public API layer
- OAuth/JWT/API-key validation
- Per-user, per-client, or per-tenant rate limiting
- API lifecycle and version management
- Partner or third-party integrations
- Centralized API analytics and governance
- API request aggregation or transformation
- Protection of expensive AI/LLM endpoints

For an Agentic AI platform:

```text
User
   ↓
API Gateway
   ├── Validate JWT
   ├── Enforce user rate limit
   ├── Enforce tenant quota
   ├── Attach correlation ID
   └── Route request
          ↓
      Agent API / RAG API / Tool Gateway
```

This prevents an unauthenticated or over-limit user from reaching the LLM, search index, or MCP tools.

## Key Difference

| Capability | Load Balancer | Reverse Proxy | API Gateway |
|---|---:|---:|---:|
| Distribute traffic across instances | Strong | Sometimes | Sometimes |
| Health checks and failover | Strong | Sometimes | Sometimes |
| TLS termination | Often | Strong | Strong |
| URL-based routing | Layer 7 only | Strong | Strong |
| Hide backend topology | Limited | Strong | Strong |
| Static content / compression | Limited | Strong | Sometimes |
| OAuth/JWT validation | Limited | Possible | Strong |
| Rate limits / quotas | Basic or limited | Basic | Strong |
| API versioning | No | Limited | Strong |
| API analytics / developer portal | No | No | Often |
| Request transformation | Limited | Basic | Strong |
| External API governance | No | No | Strong |

## Production Architecture Example

```text
Internet Users
      ↓
CDN + WAF
      ↓
Layer 7 Load Balancer
      ↓
API Gateway
      ├── OAuth/JWT validation
      ├── Rate limiting
      ├── Request logging
      └── API routing
             ↓
Kubernetes Ingress / Reverse Proxy
      ├── /api/* → Spring Boot services
      ├── /ai/*  → FastAPI Agent service
      └── /ui/*  → Frontend
             ↓
Internal services
      ├── Kafka
      ├── Redis
      ├── SQL database
      ├── Azure AI Search
      └── Azure OpenAI
```

In a smaller system, one product may perform multiple roles:

```text
Azure Application Gateway
   ├── Layer 7 load balancing
   ├── TLS termination
   ├── WAF
   └── Path-based routing
```

Or:

```text
NGINX
   ├── Reverse proxy
   ├── Load balancing
   ├── TLS termination
   └── Basic rate limiting
```

The distinction is about responsibility, not always separate physical products.

## Example: Spring Cloud Gateway

```java
@Bean
RouteLocator routes(RouteLocatorBuilder builder) {
    return builder.routes()
        .route("invoice-api", route -> route
            .path("/api/invoices/**")
            .uri("lb://invoice-service"))
        .route("agent-api", route -> route
            .path("/ai/**")
            .uri("lb://agent-service"))
        .build();
}
```

`lb://` means the gateway can use service discovery or load balancing to find healthy instances.

## Example: API Gateway Rate-Limit Logic

```text
Incoming request
      ↓
Validate JWT
      ↓
Read tenant/user ID
      ↓
Check Redis rate-limit counter
      ├── Limit exceeded → 429 Too Many Requests
      └── Allowed → route to Agent API
```

For AI endpoints:

```text
Standard user: 20 AI requests/minute
Premium user: 100 AI requests/minute
Internal service: separate quota
```

Rate limits protect:

- LLM cost
- Azure OpenAI quota
- Search-service capacity
- ERP/tool APIs
- Application availability

## Common Mistakes

### 1. Treating a Load Balancer as Full API Security

A load balancer can distribute traffic, but it may not provide detailed JWT scope validation, tenant quotas, API-version governance, or developer onboarding.

### 2. Giving the Agent Direct Access to Internal Services

Bad design:

```text
Agent Service
   ↓
Direct unrestricted database / ERP / payment access
```

Better design:

```text
Agent
   ↓
Authorized Tool Gateway
   ↓
Validated internal API
   ↓
Service / Database
```

### 3. Making Every Service Public

Bad design:

```text
Internet → Invoice Service
Internet → ERP Service
Internet → Payment Service
Internet → Agent Tool Service
```

Better design:

```text
Internet
   ↓
Gateway / reverse proxy
   ↓
Private internal services
```

### 4. No Timeout or Request Limits for LLM Endpoints

AI calls can be expensive and unpredictable.

```text
API Gateway
   ├── Max request body size
   ├── Per-user rate limit
   ├── Request timeout
   ├── Tenant quota
   └── Authentication
```

## Interview-Ready Answer

> A load balancer mainly distributes traffic across healthy service instances and supports high availability and horizontal scaling. A reverse proxy sits in front of backend services and handles request forwarding, TLS termination, path routing, headers, compression, and sometimes caching. An API gateway is an API-specific entry layer that adds capabilities such as OAuth or JWT validation, rate limiting, quotas, API versioning, request transformation, and centralized observability.

> In production, I may use all three. For example, a load balancer distributes internet traffic, an API gateway secures and governs public APIs, and a reverse proxy or Kubernetes ingress routes requests to internal Spring Boot or FastAPI services. In an Agentic AI system, the gateway is especially important because it protects expensive LLM and tool calls using authentication, authorization, quotas, and rate limits.