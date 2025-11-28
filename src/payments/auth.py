from __future__ import annotations

import os
from typing import Dict, Any
from fastapi import Depends, HTTPException
from unison_common.auth import BatonAuth


def _load_auth() -> BatonAuth:
    secret = os.getenv("UNISON_AUTH_SECRET")
    issuer = os.getenv("UNISON_AUTH_ISSUER", "unison-auth")
    audience = os.getenv("UNISON_AUTH_AUDIENCE", "unison-internal")
    if not secret:
        raise RuntimeError("UNISON_AUTH_SECRET is required for payments auth")
    return BatonAuth(secret_key=secret, issuer=issuer, audience=audience)


def auth_dependency():
    baton_auth = _load_auth()

    def _dep(token: Dict[str, Any] = Depends(baton_auth)):
        return token

    return _dep
