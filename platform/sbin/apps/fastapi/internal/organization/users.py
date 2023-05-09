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
#   the organization admin function
#
###############################################################################
import requests
import json
import secrets
import string
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from dependencies.dependencies import token_validity
from routers.data import minio_bucket_create, minio_bucket_delete
from heroes_conf import settings


# Organization Admin: Users
router = APIRouter(
    prefix="/organization/admin/users",
    tags=["Organization Admin"]
)


@router.post("/",
             tags=["Organization Admin"],
             summary="Create new user")
async def new_user(
    user_name: str,
    user_email: str,
    organization: str,
    user_password: Optional[str] = None,
    token: str = Depends(token_validity)
):
    """HEROES Create user function.

    This function allows the authenticated and authorized users to
    create a new user with its "user_name" and "user_email" as parameters.
    """
    try:
        if token['organization'] != "master":
            organization = token['organization']
        else:
            if not organization:
                organization == "master"
        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{organization}/users"
        if not user_password:
            user_password = ''.join(secrets.choice(
                string.ascii_letters + string.digits) for x in range(12)
            )
        if user_name == "root":
            minioPolicy = "userPolicy, consoleAdmin"
        else:
            minioPolicy = "userPolicy"
        data = {
            "username": user_name,
            "lastName": "",
            "firstName": "",
            "email": user_email,
            "attributes": {"minioPolicy": minioPolicy},
            "enabled": "true",
            "credentials": [{
                "type": "password",
                "value": user_password,
                "temporary": "false"  # If true, modify keycloak config
            }],
            "clientRoles": {}
            # "realmRoles": "default-roles-" + organization
        }
        # if user_name == "root":
        #     clientRoles = {
        #         "realm-management": [
        #             "view-realm",
        #             "view-identity-providers",
        #             "manage-identity-providers",
        #             "impersonation",
        #             "realm-admin",
        #             "create-client",
        #             "manage-users",
        #             "query-realms",
        #             "view-authorization",
        #             "query-clients",
        #             "query-users",
        #             "manage-events",
        #             "manage-realm",
        #             "view-events",
        #             "view-users",
        #             "view-clients",
        #             "manage-authorization",
        #             "manage-clients",
        #             "query-groups"
        #         ],
        #         "account": [
        #             "manage-account",
        #             "delete-account"
        #         ]
        #     }
        #     data["clientRoles"] = clientRoles
        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        response = requests.post(
            keycloak_org_admin,
            data=json.dumps(data),
            headers=headers
        )
        # Todo: Use a file to protect the bucket list
        protectedList = ["root", "workflows", "projects"]
        if user_name not in protectedList:
            # Add MinIO bucket for the current user
            await minio_bucket_create(
                bucket_name=user_name,
                token=token
            )
        if response.status_code == 201:
            return response
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )
    except Exception as e:
        raise e


@router.get("/",
            tags=["Organization Admin"],
            summary="List users")
async def list_users(
    organization: Optional[str] = None,
    token: str = Depends(token_validity)
):
    """HEROES List users function.

    This function allows the authenticated and authorized users to
    list the users from their organization.
    """
    try:
        print("START LIST USER")
        if token['organization'] != "master" or (token['organization'] == "master" and organization == None):
            organization = token['organization']
        print(f"organization: {organization}")
        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{organization}/users"
        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        response = requests.get(keycloak_org_admin, headers=headers)
        users_list = json.loads(response.text)
        return users_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e,
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/{username}",
            tags=["Organization Admin"],
            summary="Get user information")
async def get_user(
    username: str,
    organization: Optional[str] = None,
    token: str = Depends(token_validity)
):
    """HEROES Get user information function.

    This function allows the authenticated and authorized users to
    create a new user with its "user_name" and "user_email" as parameters.
    """
    try:
        print("START GET USER")
        if token['organization'] != "master" or (token['organization'] == "master" and organization == None):
            organization = token['organization']
        print("SHOW ORGANIZATION")
        print(f"organization: {organization}")
        users_list = await list_users(organization=organization, token=token)
        for user in users_list:
            if username == user["username"]:
                user_id = user["id"]
        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{organization}/users/{user_id}"
        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        response = requests.get(keycloak_org_admin, headers=headers)
        user_info = json.loads(response.text)
        return user_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e,
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.patch("/{username}",
              tags=["Organization Admin"],
              summary="Update user")
async def patch_users(
    username: str,
    token: str = Depends(token_validity)
):
    """HEROES Patch user function.

    This function allows the authenticated and authorized users to
    update the information of a user.
    """
    try:
        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{token['organization']}/users"
        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        response = requests.get(keycloak_org_admin, headers=headers)
        users_list = json.loads(response.text)
        return users_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e,
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.delete("/{username}",
               tags=["Organization Admin"],
               summary="Delete user")
async def delete_users(
    username: str,
    organization: Optional[str] = None,
    token: str = Depends(token_validity)
):
    """HEROES Delete user function.

    This function allows the authenticated and authorized users to
    delete a specific user witht the "username" parameter.
    """
    try:
        if token['organization'] != "master" or (token['organization'] == "master" and organization == None):
            organization = token['organization']
        users_list = await list_users(token)
        for user in users_list:
            if username == user["username"]:
                user_id = user["id"]
        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{token['organization']}/users/{user_id}"
        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        await minio_bucket_delete(
            bucket_name=username,
            token=token
        )
        response = requests.delete(keycloak_org_admin, headers=headers)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e,
            headers={"WWW-Authenticate": "Bearer"}
        )
