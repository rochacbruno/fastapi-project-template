from project_name import security
from fastapi.exceptions import HTTPException
import pytest


def test_get_current_user():
    malformed_token_no_username = security.create_access_token({})
    with pytest.raises(HTTPException):
        user = security.get_current_user(token=malformed_token_no_username)

    malformed_token_invalid_username = security.create_access_token(
        {"sub": "InvalidUserName"}
    )
    with pytest.raises(HTTPException):
        user = security.get_current_user(
            token=malformed_token_invalid_username
        )
