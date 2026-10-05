# ADR 001 — Modular monolith over microservices

**Status:** Accepted

## Context
The assessment has ~10,000 employees and two cohesive capabilities: employee records and compensation analytics.

## Decision
Use one relational data model and one FastAPI backend organized into clear service/repository boundaries, with a separate Next.js UI. Deploy both together as one product boundary.

## Why
- transactions remain local and understandable;
- SQL aggregations are sufficient at this scale;
- operational overhead is low;
- code can still be split later if a measured bottleneck appears.

## Rejected
Microservices, Kafka, Redis and an analytics warehouse: all add failure modes and operational cost without solving a demonstrated scale problem.
