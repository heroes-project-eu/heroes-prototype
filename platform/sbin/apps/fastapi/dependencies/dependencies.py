###############################################################################
# Copyright (c) 2017-2021 UCit SAS
# All Rights Reserved
#
# This software is the confidential and proprietary information
# of UCit SAS ("Confidential Information").
# You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of
# the license agreement you entered into with UCit.
###############################################################################
from fastapi import Header, HTTPException, status
from pydantic import BaseModel
import json

# custom db heroes
import requests
from heroes_conf import settings

# from app.schemas import TokenPayload, SystemUser
# from replit import db


class UserToken(BaseModel):
    access_token: str
    expires_in: int
    refresh_expires_in: int
    refresh_token: str
    token_type: str
    id_token: str
    session_state: str
    scope: str
    organization: str


async def token_validity(token: str = Header(None)):
    """HEROES Authentication token validity

    This function checks the validity of authentication tokens,
    as defined in the UserToken class. If the token is valid, it returns
    the token, also it returns error.
    """

    try:
        token: UserToken = json.loads(token)
        keycloak_userinfo_url = (
            f"{settings.PROTOCOL}://"
            + f"keycloak-server{settings.NAMESPACE}"
            + ":8080/auth/"
            + f"realms/{token['organization']}/"
            + "PROTOCOL/openid-connect/userinfo"
        )
        headers = {
            "Authorization": "bearer " + token["access_token"],
            "Content-Type": "application/json",
        }
        requests.post(keycloak_userinfo_url, headers=headers)
        return token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
