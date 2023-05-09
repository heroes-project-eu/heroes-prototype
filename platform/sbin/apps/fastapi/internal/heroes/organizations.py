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
#   the heroes admin function
#
###############################################################################
import json
import requests
import tempfile
from fastapi import APIRouter, Depends, HTTPException, status
from jinja2 import FileSystemLoader, Environment
from typing import List
import secrets
import string
# db
from sqlalchemy.orm import Session
# custom db heroes
from db import crud, models, schemas
from db.database import SessionLocal, engine
from dependencies.dependencies import token_validity
from internal.organization import users
from internal.heroes import clients
import pika
from heroes_conf import settings


models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Organization Admin


router = APIRouter(
    prefix="/heroes/admin/organizations",
    tags=["HEROES Admin"]
)

# Admin
async def make_root_role(
    user_id: str,
    organization: str,
    token: str = Depends(token_validity)
):
    """HEROES
    """
    try:
        # POST /{realm}/users/{id}/role-mappings/realm

        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        # Get the list of clients
        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{organization}/clients"
        print(keycloak_org_admin)
        clients_reponse = requests.get(
            keycloak_org_admin,
            headers=headers
        )
        client_list = json.loads(clients_reponse.text)
        print(client_list)
        # Get the client id of "realm-management" and "account"
        client_roles = {}
        for org_client in client_list:
            if org_client["clientId"] == "realm-management":
                client_roles["realm-management"] = org_client["id"]
            if org_client["clientId"] == "account":
                client_roles["account"] = org_client["id"]
        # Get the list of roles for the client "realm-management" and "account"
        role_mapping_response = {}
        for client_id in client_roles:
            keycloak_org_admin = f"{settings.PROTOCOL}://" \
                + f"keycloak-server{settings.NAMESPACE}" \
                + ":8080/auth/admin/realms/" \
                + f"{organization}/clients/" \
                + f"{client_roles[client_id]}/roles"
            roles_response = requests.get(
                keycloak_org_admin,
                headers=headers
            )
            roles_list = json.loads(roles_response.text)
            print(f"LISTE DES ROLES : {roles_list}")
            data = []
            for role in roles_list:
                role_definition = {
                    "id": role["id"],
                    "name": role["name"],
                }
                data.append(role_definition)
            # Map the roles to the root account
            keycloak_org_admin = f"{settings.PROTOCOL}://" \
                + f"keycloak-server{settings.NAMESPACE}" \
                + ":8080/auth/admin/realms/" \
                + f"{organization}/users/" \
                + f"{user_id}/role-mappings/clients/" \
                + f"{client_roles[client_id]}"
            response = requests.post(
                keycloak_org_admin,
                data=json.dumps(data),
                headers=headers
            )
            role_mapping_response[client_id] = response
            print(response.text)
            print(f"role_mapping_response : {role_mapping_response[client_id]}")

        print(role_mapping_response)
        return role_mapping_response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


async def create_org_db(
    new_organization: schemas.OrganizationCreate,
    client_secret: str,
    token: str = Depends(token_validity)
):
    """HEROES Create organization in database function.

    This function is for internal usages only. It allows the internal
    organization creation function to create an organization in the
    'organizations' table of the HEROES database.
    """
    try:
        # Check if organization exists
        db_organization = crud.get_organization_by_name(
            next(get_db()),
            organization_name=new_organization.name
        )
        if db_organization:
            raise HTTPException(
                status_code=400,
                detail="name already registered"
            )
        # Create organization in db
        org_db_response = crud.create_organization(
            next(get_db()),
            organization=new_organization
        )
        organization_in_db = {}
        organization_in_db['id'] = org_db_response.id
        organization_in_db['name'] = org_db_response.name
        organization_in_db['status'] = org_db_response.status
        organization_in_db['type'] = org_db_response.type

        # Create the keycloak "account" client in the db
        client = schemas.ClientCreate(name="account", secret=client_secret)
        await clients.create_client_for_organization(
            organization_id=organization_in_db['id'],
            client=client,
            token=token
        )
        return organization_in_db
    except Exception as e:
        raise e


async def create_org_keycloak(
    new_organization: schemas.OrganizationCreate,
    user_email: str,
    client_secret: str,
    token: str = Depends(token_validity),
):
    """HEROES Create organization in keycloak function.

    This function is for internal usages only. It allows the internal
    organization creation function to create an organization as tenant of
    the keycloak server.
    """
    try:
        # Load configuration template of organization
        file_loader = FileSystemLoader(
            f"{settings.FASTAPI_DIR}/templates/"
        )
        env = Environment(loader=file_loader)
        template = env.get_template('organization.template.j2')
        organization_template = template.render(
            HEROES_REALM_NAME=new_organization.name,
            HEROES_CLIENT_ACCOUNT_SECRET=client_secret
        )
        tmpF = tempfile.NamedTemporaryFile()

        with open(tmpF.name, 'w') as template_file:
            template_file.write(organization_template)
        with open(tmpF.name) as template_file:
            data = json.load(template_file)

        # Create the organization in keycloak
        keycloak_admin_url = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/" \
            + "admin/realms"
        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        requests.post(
            keycloak_admin_url,
            headers=headers,
            data=json.dumps(data)
        )

        # Create the first user of the organization
        await users.new_user(
            user_name="root",
            user_email=user_email,
            user_password="orgroot2022",
            organization=new_organization.name,
            token=token
        )

        # Get user_id
        root_profile_response = await users.get_user("root", new_organization.name, token)
        print(root_profile_response)
        await make_root_role(root_profile_response["id"], new_organization.name, token)
        return root_profile_response
    except Exception as e:
        raise e


async def create_org_minio(
    new_organization: schemas.OrganizationCreate,
    client_secret: str
):
    """HEROES Create organization in keycloak function.

    This function is for internal usages only. It allows the internal
    organization creation function to create an organization as tenant of
    the keycloak server.
    """
    from kubernetes import client as k8s_client
    from kubernetes import config as k8s_config
    import base64
    import os
    import yaml
    # loading k8s client
    k8s_config.load_incluster_config()

    # jinja2
    template_dir = f"{settings.FASTAPI_DIR}/templates/minio/"
    file_loader = FileSystemLoader(template_dir)
    context = {
        'KEYCLOAK_BASEURL':  f"{settings.PROTOCOL}://keycloak-server{settings.NAMESPACE}:8080/auth",
        'ORGANIZATION_NAME': new_organization.name,
        'ORGANIZATION_CLIENT_ID': 'account',
        'ORGANIZATION_CLIENT_SECRET': base64.b64encode(client_secret.encode("ascii")).decode()
    }

    for template_file in os.listdir(template_dir):
        template = Environment(loader=file_loader).get_template(
            template_file).render(**context)
        k8s_obj = yaml.safe_load(template)

        if template_file.startswith('service.'):
            k8s_client.CoreV1Api().create_namespaced_service(
                namespace=settings.K8S_NAMESPACE,
                body=k8s_obj
            )
        elif template_file.startswith('statefulset.'):
            k8s_client.AppsV1Api().create_namespaced_stateful_set(
                namespace=settings.K8S_NAMESPACE,
                body=k8s_obj,
            )
        elif template_file.startswith('configmap.'):
            k8s_client.CoreV1Api().create_namespaced_config_map(
                namespace=settings.K8S_NAMESPACE,
                body=k8s_obj,
            )
        elif template_file.startswith('secret.'):
            k8s_client.CoreV1Api().create_namespaced_secret(
                namespace=settings.K8S_NAMESPACE,
                body=k8s_obj,
            )
        else:
            raise HTTPException(
                500, f'Invalid template {template_dir}/{template_file}')


# Admin
@router.post("/",
             response_model=schemas.Organization,
             tags=["HEROES Admin"],
             summary="Create a new organization")
async def create_organization(
    new_organization: schemas.OrganizationCreate,
    user_email: str,
    token: str = Depends(token_validity),
    db: Session = Depends(get_db)
):
    """HEROES Create organization function.

    This function allows the authenticated and authorized users from the
    master organization to create organization with organization schemas.
    """
    try:
        # Generate client-secret for the "account" client of the organization
        client_secret = ''.join(secrets.choice(
            string.ascii_letters + string.digits)
            for x in range(20)
        )
        # Create organization in db
        db_response = await create_org_db(
            new_organization,
            client_secret,
            token)
        # Create the organization in keycloak
        await create_org_keycloak(
            new_organization,
            user_email,
            client_secret,
            token)
        # Create the organization servers
        await create_org_minio(new_organization, client_secret)  # Todo: test
        return db_response
    except Exception as e:
        raise e


@router.delete("/",
               tags=["HEROES Admin"],
               summary="Delete organization")
async def delete_organization(
    organization_target: str,
    token: str = Depends(token_validity),
    db: Session = Depends(get_db)
):
    """HEROES Delete organization function.

    This function allows the authenticated and authorized users from the
    master organization to delete organization with organization_target as
    parameter.
    """
    try:
        # MinIO deletion
        from kubernetes import client as k8s_client
        from kubernetes import config as k8s_config

        # loading k8s client
        k8s_config.load_incluster_config()
        
        # delete service
        k8s_client.CoreV1Api().delete_namespaced_service(
            f"minio-server-{organization_target}",
            namespace=settings.K8S_NAMESPACE
        )
        # delete deployment
        k8s_client.AppsV1Api().delete_namespaced_stateful_set(
            f"minio-server-{organization_target}",
            namespace=settings.K8S_NAMESPACE
        )
        # delete configmap
        k8s_client.CoreV1Api().delete_namespaced_config_map(
            f"minio-server-{organization_target}",
            namespace=settings.K8S_NAMESPACE
        )
        # delete secret
        k8s_client.CoreV1Api().delete_namespaced_secret(
            f"minio-server-{organization_target}",
            namespace=settings.K8S_NAMESPACE
        )


        keycloak_org_admin = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/admin/realms/" \
            + f"{organization_target}/"
        headers = {
            "Authorization": "Bearer " + token['access_token'],
            "Content-Type": "application/json"
        }
        # Delete organization from keycloak
        response = requests.delete(keycloak_org_admin, headers=headers)
        if response.status_code != 204:
            raise HTTPException(
                status_code=response.status_code,
                detail="Forbidden"
            )
        # Get all clients from organization
        organization_response = crud.get_organization_by_name(
            db=db,
            organization_name=organization_target
        )
        organization_id = organization_response.id
        organization_clients = organization_response.clients
        # Delete all clients of the organization from the db
        for client in organization_clients:
            organization_response = crud.delete_organization_client(
                db=db,
                client_id=client.id
            )
        # Delete the organization from the db
        organization_response = crud.delete_organization(
            db=db,
            organization_id=organization_id
        )

        delete_response = {
            "name": organization_target,
            "id": organization_id,
            "status": "DELETE_IN_PROGRESS",
            "status_code": "200"
        }
        return delete_response
    except Exception as e:
        raise e


@router.get("/",
            response_model=List[schemas.Organization],
            tags=["HEROES Admin"])
async def list_organizations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    organizations = crud.get_organizations(db, skip=skip, limit=limit)
    return organizations


@router.get("/{organization_target}",
            response_model=schemas.Organization,
            tags=["HEROES Admin"])
async def read_organization(
    organization_target: str,
    token: str = Depends(token_validity),
    db: Session = Depends(get_db)
):
    """HEROES Read organization function.

    This function allows the authenticated and authorized users from the
    master organization to get information about a specific organization with
    organization_target as parameter.
    """
    try:
        # Get organization information in the db
        db_organization = crud.get_organization_by_name(
            db,
            organization_name=organization_target
        )
        if db_organization is None:
            raise HTTPException(
                status_code=404,
                detail="Organization not found")
        return db_organization
    except Exception as e:
        raise e


# @router.get("/{organization_target}",
#             response_model=schemas.Organization,
#             tags=["HEROES Admin"])
# async def update_db_organization(
#     organization_target: str,
#     token: str = Depends(token_validity),
#     db: Session = Depends(get_db)
# ):
#     """HEROES Read organization function.
#
#     This function allows the authenticated and authorized users from the
#     master organization to get information about a specific organization with
#     organization_target as parameter.
#     """
#     try:
#         # Get organization information in the db
#         db_organization = crud.get_organization_by_name(
#             db,
#             organization_name=organization_target
#         )
#         if db_organization is None:
#             raise HTTPException(
#                 status_code=404,
#                 detail="Organization not found")
#         return db_organization
#     except Exception as e:
#         raise e
