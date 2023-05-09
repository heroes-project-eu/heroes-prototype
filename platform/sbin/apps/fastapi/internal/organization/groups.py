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
from fastapi import APIRouter, Depends, HTTPException, status
# db
from dependencies.dependencies import token_validity
from heroes_conf import settings


# Organization Admin: Groups
router = APIRouter(
    prefix="/organization/admin/groups",
    tags=["Organization Admin"]
    # dependencies=[Depends(token_validity)]
)


@router.post("/",
             tags=["Organization Admin"],
             summary="Create group")
async def new_group(
    groupname: str,
    token: str = Depends(token_validity)
):
    """HEROES Create group function.

    This function allows the authenticated and authorized users to
    create a new group in Keycloak.
    """
    try:

        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{token['organization']}/groups"
        data = {
            "name": groupname
        }
        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        response = requests.post(
            keycloak_org_admin,
            data=json.dumps(data),
            headers=headers
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/",
            tags=["Organization Admin"],
            summary="List groups")
async def list_groups(
    token: str = Depends(token_validity)
):
    """HEROES List groups function.

    This function allows the authenticated and authorized users to
    create a new group in Keycloak.
    """
    try:
        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{token['organization']}/groups"
        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        response = requests.get(keycloak_org_admin, headers=headers)
        groups_list = json.loads(response.text)
        return groups_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e,
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/{groupname}",
            tags=["Organization Admin"],
            summary="Get group information")
async def get_group(
    groupname: str,
    token: str = Depends(token_validity)
):
    """HEROES Get group information function.

    This function allows the authenticated and authorized users to
    get information about a group.
    """
    try:
        groups_list = await list_groups(token)

        for group in groups_list:
            if groupname == group['name']:
                group_id = group['id']
        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{token['organization']}/groups/{group_id}"
        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        response = requests.get(keycloak_org_admin, headers=headers)
        group_info = json.loads(response.text)
        return group_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e,
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.patch("/{groupname}",
              tags=["Organization Admin"],
              summary="Update group")
async def patch_groups(
    groupname: str,
    token: str = Depends(token_validity)
):
    """HEROES Update group function.

    This function allows the authenticated and authorized users to
    update the information of a specified group with the "groupname"
    parameter.
    """
    try:
        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{token['organization']}/groups"
        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        response = requests.get(keycloak_org_admin, headers=headers)
        groups_list = json.loads(response.text)
        return groups_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e,
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.delete("/{groupname}",
               tags=["Organization Admin"],
               summary="Delete group")
async def delete_groups(
    groupname: str,
    token: str = Depends(token_validity)
):
    """HEROES Delete group function.

    This function allows the authenticated and authorized users to
    delete a specified group with the "groupname" parameter.
    """
    try:
        groups_list = await list_groups(token)
        for group in groups_list:
            if groupname == group['name']:
                group_id = group['id']
        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{token['organization']}/groups/{group_id}"
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
