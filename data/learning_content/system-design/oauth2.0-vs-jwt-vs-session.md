---
title: OAuth 2.0 vs JWT vs Session — When to Use What?
category: System Design Fundamentals
difficulty: Hard
description: Understand the difference between OAuth 2.0, JWT, and session-based authentication, with production architectures, real-life examples, security trade-offs, and practical selection guidance.
---

## Question

What is the difference between **OAuth 2.0, JWT, and Session-based authentication**? When should I use each in production?

## Short Answer

**Session, JWT, and OAuth 2.0 are not direct alternatives.**

- **Session** → a mechanism for maintaining authenticated user state on the server.
- **JWT** → a token format that carries claims.
- **OAuth 2.0** → a framework for obtaining authorization to access protected resources.
- **OpenID Connect (OIDC)** → commonly used with OAuth 2.0 when you need user authentication/identity.

### Simple rule

```text
Traditional Web App
       ↓
    Session

Distributed APIs / Microservices
       ↓
 OAuth 2.0 + Access Token
       ↓
   JWT or Opaque Token

User Login / SSO
       ↓
 OAuth 2.0 + OIDC
```

---

# Core Idea

Think of the three concepts at different levels:

```text
                Authentication / Authorization
                           |
              +------------+------------+
              |                         |
        Authentication              Authorization
        "Who are you?"              "What can you access?"
              |                         |
          Session                  OAuth 2.0
              |                         |
             JWT                Access Token
                                    |
                              +-----+-----+
                              |           |
                             JWT        Opaque
```

A production system can therefore use **OAuth 2.0 + OIDC + JWT** together.

---

# 1. Session-Based Authentication

A session stores authentication state on the **server side**.

### How it works

Suppose you log into an online banking website.

```text
You
 |
 | username + password
 v
Bank Web Server
 |
 | Create session
 v
Session Store
 |
 | sessionId = ABC123
 v
Browser
```

The browser receives:

```text
Cookie: SESSION_ID=ABC123
```

For every subsequent request:

```text
Browser
   |
   | Cookie: SESSION_ID=ABC123
   v
Web Server
   |
   v
Session Store
   |
   v
User = Rana
```

The browser does **not** need to carry all user information.

---

## Real-Life Example — Amazon-like Web Application

Imagine an e-commerce website.

You log in:

```text
amazon-like-site.com/login
```

The server authenticates you and creates:

```text
SESSION_ID = abc123
```

Now you visit:

```text
/cart
/orders
/profile
```

Your browser automatically sends the session cookie.

```text
Browser
   |
   | SESSION_ID
   +------------------+
   |                  |
   v                  v
Cart Service       Order Service
   |                  |
   +--------+---------+
            |
            v
       Session Store
```

The application knows:

```text
SESSION_ID abc123
        ↓
User ID 101
        ↓
Authenticated
```

### Why is this useful?

Because the server can immediately invalidate the session:

```text
Logout
  ↓
Delete SESSION_ID
  ↓
abc123 no longer valid
```

---

# Session in Production

With multiple application servers:

```text
                    Load Balancer
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
         Server A    Server B    Server C
             |           |           |
             +-----------+-----------+
                         |
                         v
                       Redis
                    Session Store
```

Redis can be used as a centralized session store.

### Production stack

```text
Browser
   ↓
Secure + HttpOnly Cookie
   ↓
Load Balancer
   ↓
Spring Boot
   ↓
Redis Session Store
```

---

# Session Advantages

- Easy logout/revocation
- Small cookie
- Server controls authentication state
- Good fit for traditional web applications
- Easy to change server-side permissions/session state

### Disadvantages

- Server-side state is required
- Distributed deployments need shared session storage or another strategy
- Additional session-store infrastructure
- Less convenient for many independent APIs

---

# 2. JWT

**JWT = JSON Web Token.**

JWT is a **token format**, not an authentication protocol.

A JWT looks conceptually like:

```text
xxxxx.yyyyy.zzzzz
  ↑      ↑      ↑
Header  Payload Signature
```

Example payload:

```json
{
  "sub": "101",
  "role": "ADMIN",
  "scope": "orders:read",
  "exp": 1790000000
}
```

The client sends:

```http
Authorization: Bearer <JWT>
```

The API validates the token.

```text
Client
   |
   | JWT
   v
API
   |
   +--> Verify signature
   +--> Check expiration
   +--> Check issuer
   +--> Check audience
   +--> Check scopes
   |
   v
Allow / Reject
```

---

# Why Is JWT Useful?

Suppose you have:

```text
Frontend
   |
   v
API Gateway
   |
   +----> Order Service
   |
   +----> Payment Service
   |
   +----> Inventory Service
   |
   +----> User Service
```

With a properly designed JWT access token, services can validate the token without maintaining a server-side session for every user.

```text
JWT
 |
 +----> Order API
 |
 +----> Payment API
 |
 +----> Inventory API
```

This is particularly useful in distributed API architectures.

---

# Real-Life Example — Google/Microsoft-Style Enterprise Application

Imagine your company has:

```text
Employee Portal
      |
      +----> HR API
      |
      +----> Leave API
      |
      +----> Payroll API
      |
      +----> Project API
```

You authenticate through an enterprise identity provider.

After authentication, you receive an access token.

```text
Employee
   |
   v
Identity Provider
   |
   | Access Token
   v
Employee Portal
   |
   v
API Gateway
   |
   +----> HR API
   +----> Leave API
   +----> Payroll API
```

If the access token is a JWT, the APIs can validate its signature and claims.

For example:

```json
{
  "sub": "employee123",
  "aud": "leave-api",
  "scope": "leave.read leave.write",
  "exp": 1790000000
}
```

The Leave API can determine:

```text
Is token valid?        ✓
Is it intended for me? ✓
Has it expired?        ✗
Does it have scope?    ✓
```

Then allow the operation.

---

# JWT Advantages

### 1. Good for distributed systems

Multiple services can validate the token.

```text
JWT
 |
 +--> Service A
 +--> Service B
 +--> Service C
```

### 2. No mandatory session lookup

The token itself contains claims.

### 3. Easy horizontal scaling

You can have:

```text
API Server 1
API Server 2
API Server 3
API Server 4
```

without necessarily sharing per-user session state.

---

# JWT Disadvantages

### Revocation is harder

Suppose:

```text
JWT expiry = 1 hour
```

User account gets disabled after 10 minutes.

The token can still be cryptographically valid until it expires unless you have an additional revocation/introspection mechanism.

With sessions:

```text
Delete Session
     ↓
Immediately invalid
```

With JWT:

```text
JWT issued
    ↓
Potentially valid until expiry
```

Therefore production systems commonly use **short-lived access tokens**.

---

### JWT can become large

If you put too many claims:

```text
Authorization: Bearer <very-large-token>
```

every request carries that data.

Keep JWTs relatively small.

---

### Stolen JWT is dangerous

A bearer token generally means:

```text
Whoever possesses it
        ↓
Can use it
```

Therefore:

```text
HTTPS
Short expiration
Secure storage
Proper audience
Proper scopes
```

are important.

---

# 3. OAuth 2.0

OAuth 2.0 is an **authorization framework**.

It answers:

> "How can an application obtain permission to access an API/resource?"

For example:

```text
Your Application
       |
       | "I need access to user's calendar"
       v
Authorization Server
       |
       | Access Token
       v
Calendar API
```

The application does not need the user's password.

---

# Real-Life Example — "Login with Google"

A common interview simplification is:

> "OAuth is used for login with Google."

More precisely, **OAuth 2.0 provides authorization**, while **OpenID Connect (OIDC)** provides the identity/authentication layer used for modern "Sign in with Google"-style login.

Flow:

```text
             +----------------+
             |     User       |
             +-------+--------+
                     |
                     v
              Your Application
                     |
                     | Redirect
                     v
             +---------------+
             | Google / IdP  |
             +-------+-------+
                     |
              User authenticates
                     |
                     v
              Authorization
                     |
                     v
                Your App
                     |
                     | Access Token
                     v
                 Google API
```

With OIDC, the application can also receive an **ID token** representing the user's authenticated identity.

---

# OAuth 2.0 Components

There are four important actors:

```text
+------------------+
| Resource Owner   |
|      User        |
+--------+---------+
         |
         v
+------------------+
| Client           |
| Your Application |
+--------+---------+
         |
         v
+------------------+
| Authorization    |
| Server / IdP     |
+--------+---------+
         |
         v
+------------------+
| Resource Server  |
| Protected API    |
+------------------+
```

---

# OAuth 2.0 + OIDC

For enterprise login/SSO:

```text
OAuth 2.0
      +
OpenID Connect
      |
      v
Authentication + Authorization
```

Examples of identity-provider platforms include:

- Microsoft Entra ID
- Okta
- Auth0
- Google Identity

---

# OAuth 2.0 vs JWT

This is the **most important interview distinction**.

They are not competitors.

```text
OAuth 2.0
    |
    | obtains/accesses
    v
Access Token
    |
    +--------> JWT
    |
    +--------> Opaque Token
```

OAuth 2.0 tells you **how authorization works**.

JWT tells you **how a token can be represented**.

---

# 4. Session vs JWT

This is the more meaningful comparison.

| Feature | Session | JWT |
|---|---|---|
| Where state lives | Server | Token/client side |
| Token format | Session ID | JWT |
| Server lookup | Usually required | Often not |
| Revocation | Easy | More difficult |
| Horizontal scaling | Shared session store commonly needed | Simpler |
| Token size | Small | Larger |
| Best fit | Traditional web apps | Distributed APIs |
| Server control | High | Lower once token issued |

---

# 5. OAuth 2.0 vs Session

These also aren't necessarily mutually exclusive.

You can have:

```text
Browser
   |
   | Secure Cookie
   v
BFF
   |
   | OAuth 2.0 / OIDC
   v
Identity Provider
```

The browser maintains a session with the BFF, while the BFF uses OAuth tokens to communicate with downstream APIs.

This is a common architectural pattern for browser applications because it keeps API tokens away from browser JavaScript.

---

# 6. When Should I Use What?

## Case 1 — Traditional Server-Rendered Application

Example:

```text
Spring Boot
+
Thymeleaf
+
Browser
```

Use:

```text
Session + Secure Cookie
```

Architecture:

```text
Browser
   |
   | HttpOnly Cookie
   v
Spring Boot
   |
   v
Redis
```

Good for:

- admin portals
- internal web applications
- server-rendered enterprise applications
- traditional MVC applications

---

# Case 2 — Microservices

Example:

```text
                    API Gateway
                         |
        +----------------+----------------+
        |                |                |
        v                v                v
   Order API       Payment API      Inventory API
```

Use an identity provider with:

```text
OAuth 2.0
+
Access Tokens
```

The access token may be JWT.

```text
IdP
 |
 | JWT access token
 v
API Gateway
 |
 +--> Order
 +--> Payment
 +--> Inventory
```

---

# Case 3 — Third-Party API Access

Example:

```text
Your App
   |
   | Access user's data
   v
Third-party API
```

Use:

```text
OAuth 2.0
```

For example:

```text
Your application
       |
       v
Authorization Server
       |
       v
Access Token
       |
       v
Third-party API
```

This is where OAuth 2.0's delegated-authorization model is particularly useful.

---

# Case 4 — Service-to-Service Authentication

Suppose:

```text
Order Service
      |
      v
Payment Service
```

There is no human user.

OAuth 2.0 can still be used through the **Client Credentials** flow:

```text
Order Service
      |
      | Client credentials
      v
Authorization Server
      |
      | Access Token
      v
Order Service
      |
      v
Payment API
```

Again, the access token might be a JWT.

---

# Case 5 — Browser + Backend API

Suppose:

```text
React
  |
  v
Spring Boot API
```

There are several valid architectures.

### Option A — BFF + Session

```text
Browser
   |
   | Session Cookie
   v
BFF
   |
   | OAuth access token
   v
Backend APIs
```

### Option B — SPA directly calling APIs

```text
Browser
   |
   | OAuth access token
   v
API Gateway
   |
   v
Microservices
```

The exact choice depends on your security model and architecture.

Don't use:

> "SPA always means JWT."

That's an oversimplification.

---

# 7. Access Token vs ID Token

Very important in interviews.

### Access Token

Purpose:

```text
Call an API
```

```text
Client
   |
   | Access Token
   v
API
```

### ID Token

Purpose:

```text
Tell the client about the authenticated user
```

```text
Identity Provider
       |
       | ID Token
       v
     Client
```

**Do not send an ID token to an API just because it happens to be a JWT.**

---

# 8. Refresh Tokens

Access tokens should generally have a relatively short lifetime.

```text
Access Token
     |
     v
Short lifetime
```

A refresh token can be used to obtain a new access token.

```text
             Access Token
                  |
                  X Expired
                  |
                  v
            Refresh Token
                  |
                  v
         Authorization Server
                  |
                  v
           New Access Token
```

This allows you to avoid making access tokens unnecessarily long-lived.

---

# 9. Production Security

Regardless of architecture:

```text
HTTPS
   ↓
Protect credentials/tokens
   ↓
Validate issuer
   ↓
Validate audience
   ↓
Validate expiration
   ↓
Validate signature
   ↓
Validate scopes/roles
```

For browser cookies:

```text
HttpOnly
Secure
SameSite
CSRF protection where applicable
```

For access tokens:

```text
Short lifetime
Correct audience
Least-privilege scopes
HTTPS
Secure token handling
```

---

# 10. Real Production Example

Imagine you're designing an **enterprise employee platform**.

It has:

```text
Employee Portal
      |
      +---- Leave Service
      |
      +---- Payroll Service
      |
      +---- Project Service
      |
      +---- HR Service
```

You don't want each service maintaining its own username/password database.

Instead:

```text
                    Identity Provider
                    OAuth 2.0 + OIDC
                           |
                           |
                      Access Token
                           |
                           v
Employee Browser ---> API Gateway
                         |
              +----------+----------+
              |          |          |
              v          v          v
           Leave      Payroll      HR
           Service    Service     Service
```

For a browser-facing application, you might use a **BFF + secure session**:

```text
Browser
   |
   | Secure HttpOnly Session Cookie
   v
BFF
   |
   | OAuth access token
   v
API Gateway
   |
   +--> Leave
   +--> Payroll
   +--> HR
```

This combines the strengths of both approaches:

```text
Browser security/control
        +
OAuth-based API authorization
```

---

# 11. Decision Tree

Use this in system-design interviews:

```text
                What are you building?
                        |
          +-------------+-------------+
          |                           |
     Traditional Web            API / Distributed
          |                           |
          v                           v
       SESSION                 Need centralized IdP?
                                      |
                              +-------+-------+
                              |               |
                             YES              NO
                              |               |
                              v               v
                        OAuth 2.0/OIDC    Simpler auth
                              |
                              v
                       Access Token
                              |
                         +----+----+
                         |         |
                        JWT      Opaque
```

Then ask:

```text
Do I need delegated access?
        |
       YES
        ↓
   OAuth 2.0

Do I need user identity/SSO?
        |
       YES
        ↓
 OAuth 2.0 + OIDC

Do I need server-side session control?
        |
       YES
        ↓
    Session

Do distributed APIs benefit from
self-contained token validation?
        |
       YES
        ↓
  JWT access token
```

---

# Production Trade-Offs

| Requirement | Session | JWT | OAuth 2.0/OIDC |
|---|---|---|---|
| Traditional web app | ✅ | Possible | Possible |
| Server-side state | ✅ | ❌/not required | Depends |
| Easy revocation | ✅ | More difficult | Depends on token strategy |
| Distributed APIs | Possible | ✅ | ✅ |
| SSO | Possible | Possible | ✅ |
| Third-party delegated access | ❌ | ❌ by itself | ✅ |
| Token format | Session ID | JWT | JWT or opaque |
| Central IdP | Optional | Optional | Common |
| User authentication | ✅ | Can be used | OIDC for identity |
| API authorization | Possible | Claims/scopes | ✅ |

---

# Common Interview Traps

### ❌ "OAuth 2.0 and JWT are alternatives."

No.

```text
OAuth 2.0
    ↓
Access Token
    ↓
JWT or Opaque
```

---

### ❌ "JWT is an authentication protocol."

JWT is a **token format**.

---

### ❌ "OAuth 2.0 is authentication."

OAuth 2.0 primarily addresses **authorization**.

For identity/login:

```text
OAuth 2.0 + OIDC
```

---

### ❌ "JWT is always better because it's stateless."

Statelessness is useful, but you trade away some easy revocation and server-side control.

---

### ❌ "Sessions don't scale."

They can scale:

```text
App Servers
     |
     v
 Redis Cluster
     |
     v
Session State
```

The trade-off is the additional shared state infrastructure.

---

# Interview-Ready Answer

If the interviewer asks:

**"OAuth 2.0 vs JWT vs Session — what would you use in production?"**

> **First, I would clarify that these are different concepts. A session is a server-side state mechanism, JWT is a token format, and OAuth 2.0 is an authorization framework. For a traditional server-rendered web application, I'd typically use a secure HttpOnly session cookie because revocation and server-side control are straightforward. For distributed APIs and microservices, especially with an enterprise identity provider, I'd typically use OAuth 2.0 and OIDC, with short-lived access tokens. Those access tokens can be JWTs when distributed services benefit from local token validation. For third-party delegated access, I'd use OAuth 2.0. JWTs aren't automatically better than sessions: they simplify distributed validation but make revocation and token management more complex. The production choice depends on the client type, number of services, SSO requirements, delegated access, revocation requirements, and security model.**

## Quick Revision

```text
SESSION
→ Server-side authentication state
→ Secure HttpOnly cookie
→ Traditional web applications
→ Easy revocation
→ Shared store such as Redis when horizontally scaled

JWT
→ Token FORMAT
→ Self-contained claims
→ Useful for distributed API validation
→ No mandatory session lookup
→ Revocation is harder
→ Keep access tokens short-lived

OAuth 2.0
→ AUTHORIZATION framework
→ Delegated access
→ Access tokens
→ JWT OR opaque tokens

OIDC
→ Identity/authentication layer
→ Built on OAuth 2.0
→ SSO / "Sign in with..." scenarios

PRODUCTION
→ Traditional web → Session
→ Enterprise SSO → OAuth 2.0 + OIDC
→ Microservices → OAuth 2.0 access tokens
→ Distributed validation → JWT can be appropriate
→ Third-party API → OAuth 2.0
→ Browser + many APIs → Consider BFF + session + OAuth
```

### One-line mental model

> **Session = where authentication state lives; JWT = how a token is represented; OAuth 2.0 = how authorization is delegated; OIDC = how identity is established on top of OAuth 2.0.**