"""HTTP API Gateway v2 helpers."""

from __future__ import annotations

import base64
import binascii
import json
import re
from collections.abc import Callable
from decimal import Decimal
from typing import Any


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def _json_default(value: object) -> int | float:
    if isinstance(value, Decimal):
        return int(value) if value == int(value) else float(value)
    raise TypeError(f"not JSON serializable: {type(value).__name__}")


def ok(body: object, status: int = 200) -> dict[str, object]:
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body, default=_json_default, separators=(",", ":")),
    }


def error(status: int, code: str, message: str) -> dict[str, object]:
    return ok({"error": {"code": code, "message": message}}, status)


def parse_json(event: dict[str, Any]) -> dict[str, Any]:
    raw = event.get("body")
    if raw in (None, ""):
        return {}
    if event.get("isBase64Encoded"):
        try:
            raw = base64.b64decode(raw).decode("utf-8")
        except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
            raise ApiError(400, "bad_json", "Request body is not valid JSON") from exc
    try:
        body = json.loads(raw)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ApiError(400, "bad_json", "Request body is not valid JSON") from exc
    if not isinstance(body, dict):
        raise ApiError(400, "bad_json", "Request body must be a JSON object")
    return body


def header(event: dict[str, Any], name: str) -> str | None:
    wanted = name.lower()
    for key, value in (event.get("headers") or {}).items():
        if str(key).lower() == wanted:
            return str(value) if value is not None else None
    return None


def _route_pattern(route_key: str) -> tuple[re.Pattern[str], list[str]]:
    method, _, path = route_key.partition(" ")
    if not method or not path:
        return re.compile(r"(?!)"), []
    names: list[str] = []
    pieces: list[str] = []
    for piece in path.split("/"):
        if piece.startswith("{") and piece.endswith("}"):
            names.append(piece[1:-1])
            pieces.append(r"([^/]+)")
        else:
            pieces.append(re.escape(piece))
    return re.compile(rf"{re.escape(method)} {'/'.join(pieces)}"), names


def match_route(
    event: dict[str, Any], routes: dict[str, Callable[..., object]]
) -> tuple[Callable[..., object] | None, dict[str, str]]:
    request = event.get("requestContext") or {}
    http = request.get("http") or {}
    method = str(http.get("method") or event.get("httpMethod") or "").upper()
    path = str(http.get("rawPath") or http.get("path") or event.get("rawPath") or event.get("path") or "")
    target = f"{method} {path}"
    for route, fn in routes.items():
        pattern, names = _route_pattern(route)
        match = pattern.fullmatch(target)
        if match:
            return fn, dict(zip(names, match.groups(), strict=True))
    return None, {}
