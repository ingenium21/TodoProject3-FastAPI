from .utils import *
from ..routers.auth import get_db, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM, get_current_user
from datetime import timedelta
from jose import jwt
import pytest
from fastapi import HTTPException
app.dependency_overrides[get_db] = override_get_db

def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(db=db, username="codingwithrobytest", password="testpassword")
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_existent_user = authenticate_user(db=db, username="nonexistent", password="wrongpassword")
    assert non_existent_user is None

    wrong_password_user = authenticate_user(db=db, username="codingwithrobytest", password="wrongpassword")
    assert wrong_password_user is None

def test_create_access_token():
    username = 'testuser'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, 
                               algorithms=[ALGORITHM],
                               options={"verify_signature": False})
    assert decoded_token.get("sub") == username
    assert decoded_token.get("id") == user_id
    assert decoded_token.get("role") == role

@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {
        'sub': 'testuser',
        'id': 1,
        'role': 'admin'}
    
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    user = await get_current_user(token=token, db=TestingSessionLocal())
    assert user.get("username") == 'testuser'
    assert user.get("id") == 1
    assert user.get("user_role") == 'admin'

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {
        'id': 1,
        'role': 'user'}
    
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=token, db=TestingSessionLocal())
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"