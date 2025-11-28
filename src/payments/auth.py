from __future__ import annotations

import os
from typing import Dict, Any
from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError


def _decode_token(token: str) -> Dict[str, Any]:
    secret = os.getenv("UNISON_AUTH_SECRET")
    issuer = os.getenv("UNISON_AUTH_ISSUER", "unison-auth")
    audience = os.getenv("UNISON_AUTH_AUDIENCE", "unison-internal")
    if not secret:
        raise RuntimeError("UNISON_AUTH_SECRET is required for payments auth")
    return jwt.decode(token, secret, algorithms=["HS256"], issuer=issuer, audience=audience)


def auth_dependency():
    if os.getenv("DISABLE_AUTH_FOR_TESTS", "false").lower() == "true":
        async def _test_user():
            return {"username": "test-user", "roles": ["admin"], "baton": "test-baton"}

        return _test_user

    async def _dep(authorization: str = Header(None)):
        if not authorization or not isinstance(authorization, str) or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="missing or invalid auth")
        token = authorization.split(" ", 1)[1]
        try:
            return _decode_token(token)
        except JWTError:
            raise HTTPException(status_code=401, detail="invalid token")

    return _dep
