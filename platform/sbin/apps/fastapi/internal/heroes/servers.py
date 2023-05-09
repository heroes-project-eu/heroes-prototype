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
from fastapi import APIRouter, Depends
from typing import List
# db
from sqlalchemy.orm import Session
# custom db heroes
from db import crud, models, schemas
from db.database import SessionLocal, engine
from dependencies.dependencies import token_validity


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
    prefix="/heroes/admin/organizations/{organization_id}/servers",
    tags=["HEROES Admin"]
)


# Admin
@router.post("/",
             response_model=schemas.Server,
             tags=["HEROES Admin"],
             summary="Create a new organization server")
async def new_organization_server(
    organization_id: int,
    server: schemas.ServerCreate
):
    """HEROES Create organization server function.

    This function allows the authenticated and authorized services to
    Create organization servers.
    """
    try:
        server_response = crud.create_organization_server(
            next(get_db()),
            server=server,
            organization_id=organization_id
        )
        return server_response
    except Exception as e:
        raise e


@router.delete("/",
               tags=["HEROES Admin"],
               summary="Delete organization")
async def delete_organization_server(
    server_id: str,
    token: str = Depends(token_validity),
    db: Session = Depends(get_db)
):
    """HEROES Delete organization server function.

    This function allows the authenticated and authorized services to
    delete organization servers.
    """
    try:
        organization_response = crud.delete_organization_server(
            db=db,
            server_id=server_id
        )
        # Todo: change the return
        return organization_response
    except Exception as e:
        raise e


@router.get("/",
            response_model=List[schemas.Server],
            tags=["HEROES Admin"])
async def list_organization_servers(
    organization_target: str,
    db: Session = Depends(get_db)
):
    """HEROES List organization server function.

    This function allows the authenticated and authorized services to
    list organization servers.
    """
    try:
        # Get all servers from organization
        organization_response = crud.get_organization_by_name(
            db=db,
            organization_name=organization_target
        )
        return organization_response.servers
    except Exception as e:
        raise e


# @router.get("/{organization_target}",
#             response_model=schemas.Server,
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
