from .utils import *
from ..routers.users import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    response = client.get("/user/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == "codingwithrobytest"
    assert response.json()['phone_number'] == "123-555-1234"
    assert response.json()['email'] == "codingwithroby@email.com"
    assert response.json()['first_name'] == "eric"
    assert response.json()['last_name'] == "roby"
    assert response.json()['role'] == "admin"

def test_change_password_success(test_user):
    response = client.put(
        "/user/password",
        json={"password": "testpassword", "new_password": "newtestpassword"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_incorrect_current(test_user):
    response = client.put(
        "/user/password",
        json={"password": "wrongpassword", "new_password": "newtestpassword"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Current password is incorrect."}

def test_update_phone_number(test_user):
    response = client.put("/user/phonenumber/987-654-3210")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    user_in_db = db.query(Users).filter(Users.id == 1).first()
    assert user_in_db.phone_number == "987-654-3210"