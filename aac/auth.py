from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import requests
import os

# Load from .env or hardcode for now
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID")

bearer_scheme = HTTPBearer()

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
        return payload["sub"]  # This is user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    user_id = verify_jwt_token(token)
    return user_id