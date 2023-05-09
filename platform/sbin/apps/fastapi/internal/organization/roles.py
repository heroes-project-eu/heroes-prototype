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
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
# db
from dependencies.dependencies import token_validity
from heroes_conf import settings


# Organization Admin: Roles
router = APIRouter(
    prefix="/organization/admin/roles",
    tags=["Organization Admin"]
    # dependencies=[Depends(token_validity)]
)


@router.post("/",
             tags=["Organization Admin"],
             summary="Create role")
async def new_role(
    role_name: str,
    client_name: str,
    client_roles: list,
    token: str = Depends(token_validity)
):
    """HEROES Create role function.

    This function allows the authenticated and authorized users to
    create a new role in Keycloak.
    """
    try:
        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        # Create the role
        role_definition = {
            "name": role_name,
            "composite": true
        }
        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{organization}/roles"
        role_creation_response = requests.post(
            keycloak_org_admin,
            data=json.dumps(role_definition),
            headers=headers
        )
        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{organization}/roles/{role_name}/composites"
        response = requests.post(
            keycloak_org_admin,
            data=json.dumps(client_roles),
            headers=headers
        )
        print(response)
        composite_role_response = json.loads(response.text)
        return composite_role_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/",
             tags=["Organization Admin"],
             summary="Add role to user")
async def map_role(
    user_id: str,
    role_id: str,
    role_name: str,
    token: str = Depends(token_validity)
):
    """HEROES Create role function.

    This function allows the authenticated and authorized users to
    create a new role in Keycloak.
    """
    try:
        # POST /{realm}/users/{id}/role-mappings/realm
        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{token['organization']}/users/" \
            + f"{user_id}/role-mappings/realm"
        data = [
            {
                "id": f"{role_id}",
                "name": f"{role_name}"
            }
        ]
        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        response = requests.post(
            keycloak_org_admin,
            data=json.dumps(data),
            headers=headers
        )
        role_mapping_response = json.loads(response.text)
        return role_mapping_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/",
            tags=["Organization Admin"],
            summary="List roles")
async def list_roles(
    token: str = Depends(token_validity)
):
    """HEROES List roles function.

    This function allows the authenticated and authorized users to
    create a new role in Keycloak.
    """
    try:
        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{token['organization']}/roles"
        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        response = requests.get(keycloak_org_admin, headers=headers)
        roles_list = json.loads(response.text)
        return roles_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e,
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/{rolename}",
            tags=["Organization Admin"],
            summary="Get role information")
async def get_role(
    role_name: str,
    token: str = Depends(token_validity)
):
    """HEROES Get role information function.

    This function allows the authenticated and authorized users to
    get information about a role.
    """
    try:
        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{token['organization']}/roles/{role_name}"
        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        response = requests.get(keycloak_org_admin, headers=headers)
        role_info = json.loads(response.text)
        return role_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e,
            headers={"WWW-Authenticate": "Bearer"}
        )


# @router.patch("/{rolename}",
#               tags=["Organization Admin"],
#               summary="Update role")
# async def patch_roles(
#     rolename: str,
#     token: str = Depends(token_validity)
# ):
#     """HEROES Update role function.
#
#     This function allows the authenticated and authorized users to
#     update the information of a specified role with the "rolename"
#     parameter.
#     """
#     try:
#         keycloak_org_admin = f"{settings.PROTOCOL}://" \
#             + f"keycloak-server{settings.NAMESPACE}" \
#             + ":8080/auth/admin/realms/" \
#             + f"{token['organization']}/roles"
#         headers = {
#             "Authorization": "Bearer " + token['access_token'],
#             "Content-Type": "application/json"
#         }
#         response = requests.get(keycloak_org_admin, headers=headers)
#         roles_list = json.loads(response.text)
#         return roles_list
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=e,
#             headers={"WWW-Authenticate": "Bearer"}
#         )
#
#

@router.delete("/{rolename}",
               tags=["Organization Admin"],
               summary="Delete role")
async def delete_roles(
    role_name: str,
    token: str = Depends(token_validity)
):
    """HEROES Delete role function.

    This function allows the authenticated and authorized users to
    delete a specified role with the "rolename" parameter.
    """
    try:
        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{token['organization']}/roles/{role_name}"
        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        response = requests.delete(keycloak_org_admin, headers=headers)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e,
            headers={"WWW-Authenticate": "Bearer"}
        )
