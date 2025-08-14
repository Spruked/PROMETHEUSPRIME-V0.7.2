import os
from fastapi import Header, HTTPException, status

EXPECTED_KEY = os.getenv("API_KEY")  # leave unset if you don't want key checks

def require_api_key(x_api_key: str | None = Header(default=None)):
    if not EXPECTED_KEY:
        # No API key configured => no check
        return
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required")
    if x_api_key != EXPECTED_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
