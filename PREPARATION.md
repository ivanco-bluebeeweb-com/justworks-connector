# Justworks Connector — Preparation

## Product Scope
Build a comprehensive Imperal connector for **Justworks** (C28. Payroll & Benefits Administration). The integration connects directly to the official **Justworks Partner REST API** (`https://public-api.justworks.com/v1`), providing workforce management across employees/members, payroll runs, departments, time-off requests, benefit plans, and direct deposits.

## Official API Specifications
- **API Version:** Justworks Partner API (Members & Payroll) v1
- **Base URL:** `https://public-api.justworks.com/v1`
- **Core Endpoints:**
  - `GET /v1/members` — list members with status filters and cursor pagination
  - `GET /v1/members/{id}` — member details and profiles
  - `GET /v1/payroll` — payroll runs and pay history
  - `GET /v1/departments` — departments and cost centers
  - `GET /v1/time_off` — time off policies and requests
  - `GET /v1/benefit_plans` — health and retirement plans
  - `GET /v1/direct_deposits` — payment distributions
- **Authentication Model:** Bearer Token via `Authorization: Bearer <api_token>`
- **Mandatory Requirements:**
  - Strict error classification: HTTP 429 rate limits, HTTP 401/403 differentiation (Standard B8/B10).
  - Sanitization of Bearer tokens in error traces (Standard B8).
  - Multi-tenant connection tracking via `connection_id` (Standard B9).

## Delivery Gates
1. [x] Official API discovery completed with Justworks Partner API v1 specifications.
2. [x] Partner endpoints and Bearer auth verified.
3. [x] Five mandatory specification documents authored.
4. [x] Client implemented with B8-B10 compliance, secret redaction, and 429/401 classification.
5. [x] Panel sidebar implemented conforming to UI_INTERFACE_STANDARD.md.
6. [x] Verification of functions, imports, and type hints passed.
7. [x] Deployment to Imperal platform completed.
8. [x] Per-action pricing configured per PRICING_POLICY.md.
