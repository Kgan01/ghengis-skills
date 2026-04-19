#!/usr/bin/env python3
"""
In-memory permission request queue for Claude Agent Monitor.
Thread-safe via threading.Lock. No disk persistence - permissions expire.
"""

import threading
import time
import uuid
from typing import Dict, List, Optional


_lock = threading.Lock()
_requests: Dict[str, Dict] = {}


def add_permission_request(tool_name: str, tool_input_preview: str,
                           timeout: int = 60) -> str:
    """Add a new permission request and return its request_id."""
    request_id = uuid.uuid4().hex[:12]
    expires_at = time.time() + timeout
    with _lock:
        _requests[request_id] = {
            "id": request_id,
            "tool_name": tool_name,
            "input_preview": tool_input_preview,
            "status": "pending",
            "created_at": time.time(),
            "expires_at": expires_at,
            "decided_at": None,
        }
    return request_id


def get_pending() -> List[Dict]:
    """Return all non-expired pending requests."""
    now = time.time()
    with _lock:
        return [
            dict(r) for r in _requests.values()
            if r["status"] == "pending" and r["expires_at"] > now
        ]


def decide(request_id: str, approved: bool) -> bool:
    """Record a decision. Returns False if expired or not found."""
    now = time.time()
    with _lock:
        req = _requests.get(request_id)
        if req is None or req["status"] != "pending":
            return False
        if req["expires_at"] <= now:
            req["status"] = "expired"
            return False
        req["status"] = "approved" if approved else "denied"
        req["decided_at"] = now
        return True


def wait_for_decision(request_id: str, poll_interval: float = 0.5,
                      timeout: int = 60) -> Optional[str]:
    """Block until decided or timeout. Returns 'approved', 'denied', or None."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        with _lock:
            req = _requests.get(request_id)
            if req is None:
                return None
            if req["status"] == "approved":
                return "approved"
            if req["status"] == "denied":
                return "denied"
            if req["expires_at"] <= time.time():
                req["status"] = "expired"
                return None
        time.sleep(poll_interval)
    return None
