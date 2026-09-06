# Justworks Connector — Ideal Onboarding Flow

1. Admin accesses Justworks Account Settings > Developer Integrations.
2. Generates an API Access Token.
3. In Imperal, pastes API Token into Justworks sidebar.
4. Connector runs `verify_auth()` against `GET /v1/members?limit=1`.
5. Connection saved securely and ready for automated workflows.
