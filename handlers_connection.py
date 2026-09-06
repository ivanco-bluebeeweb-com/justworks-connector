"""Connection lifecycle for Justworks Connector."""
from __future__ import annotations
import json, uuid
from imperal_sdk import ActionResult
from justworks_client import JustworksClient
from app import chat
from schemas import (
    NoParams,
    ConnectParams, ConnectionIdParams, ConnectionList, ConnectionRecord, DeleteResult
)

_SECRET = "justworks_connections"

def _mask(value: str) -> str:
    return value[:4] + "…" + value[-4:] if len(value) > 10 else "***"

async def _load_connections(ctx) -> list[dict]:
    raw = await ctx.secrets.get(_SECRET)
    if not raw: return []
    try: data = json.loads(raw)
    except: return []
    return data if isinstance(data, list) else []

async def _save_connections(ctx, conns: list[dict]) -> None:
    await ctx.secrets.set(_SECRET, json.dumps(conns))

async def resolve_connection(ctx, connection_id: str = "") -> dict | None:
    conns = await _load_connections(ctx)
    if not conns: return None
    if not connection_id:
        for c in conns:
            if c.get("is_active"):
                return c
        return conns[0]
    for c in conns:
        if c["id"] == connection_id:
            return c
    return None

@chat.function(
    "connect_justworks",
    "Connect Justworks account via credentials.",
    action_type="write",
    chain_callable=True,
    event="justworks-connector.connect_justworks",
    effects=["create:connection"],
    data_model=ConnectParams
)
async def connect_justworks(ctx, params: ConnectParams) -> ActionResult[ConnectionRecord]:
    """Connect a new Justworks account."""
    client = JustworksClient(
        api_token=params.api_token,
        base_url=params.base_url
    )
    v_res = await client.verify_auth()
    if v_res.get("status") == "error":
        return ActionResult.error(
            v_res.get("message", "Authentication failed"),
            code=v_res.get("code", "UNAUTHORIZED"),
            retry_after=v_res.get("retry_after")
        )
    cid = str(uuid.uuid4())
    conns = await _load_connections(ctx)
    for c in conns:
        c["is_active"] = False
    record = {
        "id": cid,
        "label": params.label or "Justworks",
        "masked_key": _mask(params.api_token),
        "api_token": params.api_token,
        "base_url": client.base_url,
        "is_active": True
    }
    conns.append(record)
    await _save_connections(ctx, conns)
    return ActionResult.ok(
        ConnectionRecord(
            id=cid,
            label=record["label"],
            masked_key=record["masked_key"],
            base_url=record["base_url"],
            is_active=True
        ),
        summary=f"Connected Justworks account '{record['label']}'."
    )

@chat.function(
    "list_connections",
    "List connected Justworks accounts.",
    action_type="read",
    chain_callable=True,
    event="justworks-connector.list_connections",
    data_model=NoParams
)
async def list_connections(ctx, params: NoParams) -> ActionResult[ConnectionList]:
    """List all connected Justworks accounts."""
    conns = await _load_connections(ctx)
    records = [
        ConnectionRecord(
            id=c["id"],
            label=c.get("label", "Justworks"),
            masked_key=c.get("masked_key", "***"),
            base_url=c.get("base_url", ""),
            is_active=c.get("is_active", False)
        )
        for c in conns
    ]
    return ActionResult.ok(ConnectionList(connections=records, total=len(records)))

@chat.function(
    "disconnect_justworks",
    "Disconnect Justworks account.",
    action_type="write",
    chain_callable=True,
    event="justworks-connector.disconnect_justworks",
    effects=["delete:connection"],
    data_model=ConnectionIdParams
)
async def disconnect_justworks(ctx, params: ConnectionIdParams) -> ActionResult[DeleteResult]:
    """Disconnect a Justworks account."""
    conns = await _load_connections(ctx)
    target = params.connection_id
    if not target:
        for c in conns:
            if c.get("is_active"):
                target = c["id"]
                break
    new_conns = [c for c in conns if c["id"] != target]
    if len(conns) == len(new_conns):
        return ActionResult.error(f"Connection '{target}' not found.", code="NOT_FOUND")
    if new_conns and not any(c.get("is_active") for c in new_conns):
        new_conns[0]["is_active"] = True
    await _save_connections(ctx, new_conns)
    return ActionResult.ok(DeleteResult(id=target, deleted=True, message="Disconnected successfully."))
