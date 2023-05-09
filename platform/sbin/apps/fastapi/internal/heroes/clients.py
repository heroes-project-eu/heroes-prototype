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
    prefix="/heroes/admin/organizations/{organization_id}/clients",
    tags=["HEROES Admin"]
)


@router.get("/",
            response_model=List[schemas.Client],
            tags=["HEROES Admin"])
async def read_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """HEROES List clients of organization function.

    This function allows the authenticated and authorized users from the
    master organization to list the availables clients for each organization.
    """
    try:
        clients = crud.get_clients(db, skip=skip, limit=limit)
        return clients
    except Exception as e:
        raise e


@router.post("/",
             response_model=schemas.Client,
             tags=["HEROES Admin"])
async def create_client_for_organization(
    organization_id: int,
    client: schemas.ClientCreate,
    token: str = Depends(token_validity)
):
    """HEROES Create organization client function.

    This function allows the authenticated and authorized users from the
    master organization to get information about a specific organization with
    organization_target as parameter.
    """
    try:
        client_response = crud.create_organization_client(
            next(get_db()),
            client=client,
            organization_id=organization_id
        )
        return client_response
    except Exception as e:
        raise e
