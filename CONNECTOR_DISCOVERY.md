# Justworks Connector — Discovery & API Specification

## Provider Overview
Justworks is an integrated PEO (Professional Employer Organization) platform offering payroll, benefits, HR, and compliance support for growing businesses.

## Authentication Architecture
- **Auth Scheme:** OAuth 2.0 Bearer Token / API Token.
- **Header:** `Authorization: Bearer <api_token>`
- **Validation:** `GET /v1/members?limit=1` confirms token validity and scope permissions.

## Resource Endpoints
- `GET /v1/members` — query active/terminated employees
- `GET /v1/payroll` — query executed payroll batches
- `GET /v1/departments` — query department structure
- `GET /v1/time_off` — query leave balances and requests
- `GET /v1/benefit_plans` — query medical, dental, vision plans
- `GET /v1/direct_deposits` — query disbursement bank accounts
