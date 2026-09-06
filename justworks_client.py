"""Official Justworks Partner REST API client aligned with public-api.justworks.com v1."""
from __future__ import annotations
import httpx
from typing import Any, Optional

DEFAULT_JUSTWORKS_BASE = "https://public-api.justworks.com/v1"

class JustworksClient:
    def __init__(self, api_token: str, base_url: str = ""):
        self.api_token = api_token.strip()
        self.base_url = (base_url.strip() if base_url else DEFAULT_JUSTWORKS_BASE).rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Imperal-Justworks/0.1.0"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    def _sanitize_msg(self, msg: str) -> str:
        if not msg:
            return ""
        if self.api_token and len(self.api_token) > 6:
            msg = msg.replace(self.api_token, self.api_token[:3] + "..." + self.api_token[-3:])
        return msg

    def _classify_error(self, resp: httpx.Response, action_name: str) -> dict[str, Any]:
        status = resp.status_code
        err_msg = ""
        try:
            data = resp.json()
            if "errors" in data and isinstance(data["errors"], list) and len(data["errors"]) > 0:
                err_msg = "; ".join(e.get("message", "") for e in data["errors"])
            elif "message" in data:
                err_msg = data["message"]
            elif "error" in data:
                err_msg = str(data["error"])
        except Exception:
            err_msg = resp.text[:200]
        err_msg = self._sanitize_msg(err_msg)

        if status == 429:
            retry_after = resp.headers.get("Retry-After", "60")
            return {
                "status": "error",
                "code": "RATE_LIMITED",
                "message": f"Justworks rate limit reached during {action_name}. Retry after {retry_after}s.",
                "retry_after": int(retry_after) if retry_after.isdigit() else 60
            }
        if status in (401, 403):
            return {
                "status": "error",
                "code": "UNAUTHORIZED" if status == 401 else "FORBIDDEN",
                "message": f"Justworks authentication failed during {action_name}: {err_msg or 'Invalid token or insufficient permissions'}."
            }
        return {
            "status": "error",
            "code": f"HTTP_{status}",
            "message": f"Justworks error during {action_name} ({status}): {err_msg}"
        }

    async def verify_auth(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/company", headers=self.headers)
                if resp.status_code in (200, 201):
                    return resp.json()
                # fallback check members
                resp2 = await client.get(f"{self.base_url}/members?limit=1", headers=self.headers)
                if resp2.status_code in (200, 201):
                    return resp2.json()
                return self._classify_error(resp, "verify_auth")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def list_employees(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/members", headers=self.headers, params=params)
                if resp.status_code in (200, 201):
                    data = resp.json()
                    items = data if isinstance(data, list) else data.get("members", data.get("data", []))
                    return {"items": items, "next_cursor": data.get("next_cursor", "") if isinstance(data, dict) else ""}
                return self._classify_error(resp, "list_employees")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def get_employee(self, employee_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/members/{employee_id}", headers=self.headers)
                if resp.status_code in (200, 201):
                    return resp.json()
                return self._classify_error(resp, "get_employee")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def create_employee(self, name: str, details: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        payload = {"name": name, **(details or {})}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{self.base_url}/members", headers=self.headers, json=payload)
                if resp.status_code in (200, 201):
                    return resp.json()
                return self._classify_error(resp, "create_employee")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def update_employee(self, employee_id: str, details: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.patch(f"{self.base_url}/members/{employee_id}", headers=self.headers, json=details)
                if resp.status_code in (200, 201):
                    return resp.json()
                return self._classify_error(resp, "update_employee")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def delete_employee(self, employee_id: str) -> bool:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.delete(f"{self.base_url}/members/{employee_id}", headers=self.headers)
                return resp.status_code in (200, 204)
            except Exception:
                return False

    async def list_payroll_runs(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit}
        if cursor: params["cursor"] = cursor
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/payrolls", headers=self.headers, params=params)
                if resp.status_code in (200, 201):
                    data = resp.json()
                    items = data if isinstance(data, list) else data.get("payrolls", data.get("data", []))
                    return {"items": items, "next_cursor": data.get("next_cursor", "") if isinstance(data, dict) else ""}
                return self._classify_error(resp, "list_payroll_runs")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def get_payroll_run(self, payroll_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/payrolls/{payroll_id}", headers=self.headers)
                if resp.status_code in (200, 201): return resp.json()
                return self._classify_error(resp, "get_payroll_run")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def create_payroll_run(self, name: str, details: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        payload = {"name": name, **(details or {})}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{self.base_url}/payrolls", headers=self.headers, json=payload)
                if resp.status_code in (200, 201): return resp.json()
                return self._classify_error(resp, "create_payroll_run")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def update_payroll_run(self, payroll_id: str, details: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.patch(f"{self.base_url}/payrolls/{payroll_id}", headers=self.headers, json=details)
                if resp.status_code in (200, 201): return resp.json()
                return self._classify_error(resp, "update_payroll_run")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def delete_payroll_run(self, payroll_id: str) -> bool:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.delete(f"{self.base_url}/payrolls/{payroll_id}", headers=self.headers)
                return resp.status_code in (200, 204)
            except Exception:
                return False

    async def list_departments(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit}
        if cursor: params["cursor"] = cursor
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/departments", headers=self.headers, params=params)
                if resp.status_code in (200, 201):
                    data = resp.json()
                    items = data if isinstance(data, list) else data.get("departments", data.get("data", []))
                    return {"items": items, "next_cursor": data.get("next_cursor", "") if isinstance(data, dict) else ""}
                return self._classify_error(resp, "list_departments")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def get_department(self, department_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/departments/{department_id}", headers=self.headers)
                if resp.status_code in (200, 201): return resp.json()
                return self._classify_error(resp, "get_department")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def create_department(self, name: str, details: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        payload = {"name": name, **(details or {})}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{self.base_url}/departments", headers=self.headers, json=payload)
                if resp.status_code in (200, 201): return resp.json()
                return self._classify_error(resp, "create_department")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def update_department(self, department_id: str, details: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.patch(f"{self.base_url}/departments/{department_id}", headers=self.headers, json=details)
                if resp.status_code in (200, 201): return resp.json()
                return self._classify_error(resp, "update_department")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def delete_department(self, department_id: str) -> bool:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.delete(f"{self.base_url}/departments/{department_id}", headers=self.headers)
                return resp.status_code in (200, 204)
            except Exception:
                return False

    async def list_time_off_requests(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit}
        if cursor: params["cursor"] = cursor
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/time_off_requests", headers=self.headers, params=params)
                if resp.status_code in (200, 201):
                    data = resp.json()
                    items = data if isinstance(data, list) else data.get("time_off_requests", data.get("data", []))
                    return {"items": items, "next_cursor": data.get("next_cursor", "") if isinstance(data, dict) else ""}
                return self._classify_error(resp, "list_time_off_requests")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def get_time_off_request(self, request_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/time_off_requests/{request_id}", headers=self.headers)
                if resp.status_code in (200, 201): return resp.json()
                return self._classify_error(resp, "get_time_off_request")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def create_time_off_request(self, name: str, details: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        payload = {"name": name, **(details or {})}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{self.base_url}/time_off_requests", headers=self.headers, json=payload)
                if resp.status_code in (200, 201): return resp.json()
                return self._classify_error(resp, "create_time_off_request")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def update_time_off_request(self, request_id: str, details: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.patch(f"{self.base_url}/time_off_requests/{request_id}", headers=self.headers, json=details)
                if resp.status_code in (200, 201): return resp.json()
                return self._classify_error(resp, "update_time_off_request")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def delete_time_off_request(self, request_id: str) -> bool:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.delete(f"{self.base_url}/time_off_requests/{request_id}", headers=self.headers)
                return resp.status_code in (200, 204)
            except Exception:
                return False

    async def list_benefit_plans(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit}
        if cursor: params["cursor"] = cursor
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/benefits", headers=self.headers, params=params)
                if resp.status_code in (200, 201):
                    data = resp.json()
                    items = data if isinstance(data, list) else data.get("benefits", data.get("data", []))
                    return {"items": items, "next_cursor": data.get("next_cursor", "") if isinstance(data, dict) else ""}
                return self._classify_error(resp, "list_benefit_plans")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def get_benefit_plan(self, plan_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/benefits/{plan_id}", headers=self.headers)
                if resp.status_code in (200, 201): return resp.json()
                return self._classify_error(resp, "get_benefit_plan")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def create_benefit_plan(self, name: str, details: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        payload = {"name": name, **(details or {})}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{self.base_url}/benefits", headers=self.headers, json=payload)
                if resp.status_code in (200, 201): return resp.json()
                return self._classify_error(resp, "create_benefit_plan")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def update_benefit_plan(self, plan_id: str, details: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.patch(f"{self.base_url}/benefits/{plan_id}", headers=self.headers, json=details)
                if resp.status_code in (200, 201): return resp.json()
                return self._classify_error(resp, "update_benefit_plan")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def delete_benefit_plan(self, plan_id: str) -> bool:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.delete(f"{self.base_url}/benefits/{plan_id}", headers=self.headers)
                return resp.status_code in (200, 204)
            except Exception:
                return False

    async def list_direct_deposits(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit}
        if cursor: params["cursor"] = cursor
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/direct_deposits", headers=self.headers, params=params)
                if resp.status_code in (200, 201):
                    data = resp.json()
                    items = data if isinstance(data, list) else data.get("direct_deposits", data.get("data", []))
                    return {"items": items, "next_cursor": data.get("next_cursor", "") if isinstance(data, dict) else ""}
                return self._classify_error(resp, "list_direct_deposits")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def get_direct_deposit(self, deposit_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/direct_deposits/{deposit_id}", headers=self.headers)
                if resp.status_code in (200, 201): return resp.json()
                return self._classify_error(resp, "get_direct_deposit")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def create_direct_deposit(self, name: str, details: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        payload = {"name": name, **(details or {})}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{self.base_url}/direct_deposits", headers=self.headers, json=payload)
                if resp.status_code in (200, 201): return resp.json()
                return self._classify_error(resp, "create_direct_deposit")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def update_direct_deposit(self, deposit_id: str, details: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.patch(f"{self.base_url}/direct_deposits/{deposit_id}", headers=self.headers, json=details)
                if resp.status_code in (200, 201): return resp.json()
                return self._classify_error(resp, "update_direct_deposit")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(str(e))}

    async def delete_direct_deposit(self, deposit_id: str) -> bool:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.delete(f"{self.base_url}/direct_deposits/{deposit_id}", headers=self.headers)
                return resp.status_code in (200, 204)
            except Exception:
                return False
