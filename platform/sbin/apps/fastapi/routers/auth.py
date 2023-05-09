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
#
#   This scripts allows fastapi to use
#   the authentication function with keycloak
#
###############################################################################
from fastapi import APIRouter, Depends, HTTPException, status
import requests
from pydantic import BaseModel
# db
from sqlalchemy.orm import Session
# # custom db heroes
from db import crud
from db.database import SessionLocal
from dependencies.dependencies import token_validity
from heroes_conf import settings


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


class UserCredentials(BaseModel):
    organization: str
    username: str
    password: str


class UserInformation(BaseModel):
    sub: str
    minioPolicy: list
    email_verified: bool
    name: str
    preferred_username: str
    given_name: str
    family_name: str


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(
    prefix="/organization/auth",
    tags=["Identity Management"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


# Identity Management
@router.post("/login",
             response_model=UserToken,
             tags=["Identity Management"],
             summary="Login the user after UserCredentials check")
async def login(
    user_credentials: UserCredentials,
    db: Session = Depends(get_db)
):
    """HEROES Authentication token validity

    This function allows users to authenticate to the heores platform,
    it returns a UserToken if the authentication is successfull.
    """

    try:
        # Build the API keycloak url
        keycloak_token_url = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/realms/" \
            + f"{user_credentials.organization}/" \
            + "protocol/openid-connect/token"
        if user_credentials.organization == "master":
            # Set up data for API call to keycloak
            data = {'grant_type': 'password',
                    'client_id': 'admin-cli',
                    'scope': 'openid',
                    'username': user_credentials.username,
                    'password': user_credentials.password}
            client_id = 'admin-cli'
            id_token_response = requests.post(
                keycloak_token_url,
                data=data,
                verify=False,
                allow_redirects=False
            )
        else:
            # Check organization exists
            current_organization = crud.get_organization_by_name(
                organization_name=user_credentials.organization,
                db=db
            )
            if current_organization is None:
                raise HTTPException(
                    status_code=404,
                    detail="Organization not found"
                )
            else:
                # Set up data for API call to keycloak
                data = {'grant_type': 'password',
                        'scope': 'openid',
                        'username': user_credentials.username,
                        'password': user_credentials.password}
                for organization_client in current_organization.clients:
                    if organization_client.name == "account":
                        client_id = organization_client.name
                        client_secret_key = organization_client.secret
                id_token_response = requests.post(
                    keycloak_token_url,
                    data=data,
                    verify=False,
                    allow_redirects=False,
                    auth=(client_id, client_secret_key)
                )
        if "error" in id_token_response.json():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(f"Error: {id_token_response.json()['error']}"),
                headers={"WWW-Authenticate": "Bearer"}
            )
        token = id_token_response.json()
        # Add the organization name to the returned token
        token.update({"organization": user_credentials.organization})
        return token
    except Exception as e:
        raise e


@router.post("/logout",
             tags=["Identity Management"],
             summary="Logout the authenticated user")
async def logout(
    token: str = Depends(token_validity),
    db: Session = Depends(get_db)
):
    """HEROES Logout function

    This function allows authenticated users to logout from the
    HEROES platform.
    """

    try:
        # Build the API keycloak url
        keycloak_logout_url = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/realms/" \
            + f"{token['organization']}/" \
            + "protocol/openid-connect/logout"
        if token['organization'] == "master":
            # Set up data for API call to keycloak
            client_id = "admin-cli"
            data = {
                "client_id": client_id,
                "refresh_token": token['refresh_token']
            }
        else:
            # Check organization exists
            current_organization = crud.get_organization_by_name(
                organization_name=token['organization'],
                db=db
            )
            if current_organization is None:
                raise HTTPException(
                    status_code=404,
                    detail="Organization not found"
                )
            # Get the organization_client.secret from the fastapi db
            client_id = "account"
            for organization_client in current_organization.clients:
                if organization_client.name == client_id:
                    client_secret_key = organization_client.secret
            # Set up data for API call to keycloak
            data = {
                'client_id': client_id,
                'client_secret': client_secret_key,
                "refresh_token": token['refresh_token']
            }
        logout_response = requests.post(
            keycloak_logout_url,
            data=data,
            verify=False,
            allow_redirects=False
        )
        if "error" in logout_response.text:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(f"Error: {logout_response.json()['error']}"),
                headers={"WWW-Authenticate": "Bearer"}
            )
        return {'message': 'You have been log out'}
    except Exception as e:
        raise e


@router.get("/refresh_token",
            tags=["Identity Management"],
            summary="Refresh the access token of the authenticated user")
async def refresh_token(
    token: str = Depends(token_validity),
    db: Session = Depends(get_db)
):
    """HEROES Refresh token function

    This function allows authenticated users to refresh their token against
    a valid token from a previous authentication.
    """

    try:
        # Build the API keycloak url
        keycloak_token_url = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/realms/" \
            + f"{token['organization']}/" \
            + "protocol/openid-connect/token"
        if token['organization'] == "master":
            # Set up data for API call to keycloak
            client_id = "admin-cli"
            data = {'grant_type': 'refresh_token',
                    'client_id': client_id,
                    'refresh_token': token['refresh_token']}
        else:
            # Check if the organization exists
            current_organization = crud.get_organization_by_name(
                organization_name=token['organization'],
                db=db
            )
            if current_organization is None:
                raise HTTPException(
                    status_code=404,
                    detail="Organization not found"
                )
            else:
                client_id = "account"
                # Get the organization_client.secret from the fastapi db
                for organization_client in current_organization.clients:
                    if organization_client.name == client_id:
                        client_secret_key = organization_client.secret
                # Set up data for API call to keycloak
                data = {'grant_type': 'refresh_token',
                        'client_id': client_id,
                        'client_secret': client_secret_key,
                        'refresh_token': token['refresh_token']}
        id_token_response = requests.post(
            keycloak_token_url,
            data=data,
            verify=False,
            allow_redirects=False
        )
        new_token = id_token_response.json()
        new_token.update({"organization": token['organization']})
        return new_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/me",
            # response_model=UserInformation,
            tags=["Identity Management"],
            summary="List all information available \
            about the authenticated user")
async def user_me(
    token: str = Depends(token_validity),
    db: Session = Depends(get_db)
):
    try:
        if token['organization'] != "master":
            # Check if the organization exists
            current_organization = crud.get_organization_by_name(
                organization_name=token['organization'],
                db=db
            )
            if current_organization is None:
                raise HTTPException(
                    status_code=404,
                    detail="Organization not found")
        # Build the API keycloak url
        keycloak_userinfo_url = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/realms/" \
            + f"{token['organization']}/" \
            + "protocol/openid-connect/userinfo"
        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        userinfo = requests.post(
            keycloak_userinfo_url,
            headers=headers
        )
        return userinfo.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

# @app.get('/me', summary='Get details of currently logged in user', response_model=UserOut)
# async def get_me(user: User = Depends(get_current_user)):
#     return user