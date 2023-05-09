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
from fastapi import APIRouter, Depends
from typing import List
# db
from db import crud, schemas
from db.database import SessionLocal
from dependencies.dependencies import token_validity
from sqlalchemy.orm import Session

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Organization Admin: Clusters
router = APIRouter(
    prefix="/organization/admin/cluster",
    tags=["Organization Admin"]
)


# Clusters
@router.post(
    "/",
    response_model=schemas.Cluster,
    tags=["Organization Admin"],
    summary="Create Cluster"
)
async def create_cluster(
    cluster: schemas.ClusterCreate,
    token: str = Depends(token_validity)
):
    """HEROES Create cluster.

    This function allows the authenticated user to create a cluster.
    Return information about the created cluster.
    """
    try:
        db_organization = crud.get_organization_by_name(
            next(get_db()), organization_name=token["organization"]
        )
        cluster_response = crud.create_cluster(
            next(get_db()),
            cluster=cluster,
            organization_id=db_organization.id,
            cluster_type="Cloud"
        )
        return cluster_response
    except Exception as e:
        raise e


@router.get("/",
            response_model=List[schemas.Cluster],
            summary="List Clusters",
            tags=["Organization Admin"])
async def get_clusters(
    skip: int = 0,
    limit: int = 100,
    token: str = Depends(token_validity)
):
    """HEROES List cluster(s).

    This function allows the authenticated user to list the cluster of its
    organization.
    Return a list of cluster(s).
    """
    try:
        db_organization = crud.get_organization_by_name(
            next(get_db()), organization_name=token["organization"]
        )
        cluster_list_response = crud.list_clusters(
            next(get_db()),
            organization_id=db_organization.id,
            skip=skip,
            limit=limit
        )
        return cluster_list_response
    except Exception as e:
        raise e


@router.get("/{cluster_id}",
            response_model=schemas.Cluster,
            summary="Get cluster information",
            tags=["Organization Admin"])
async def get_cluster_information(
    cluster_id: str,
    token: str = Depends(token_validity)
):
    """HEROES Get cluster information.

    This function allows the authenticated user to get information of a cluster
    from its organization.
    Return information about the selected cluster.
    """
    try:
        db_organization = crud.get_organization_by_name(
            next(get_db()), organization_name=token["organization"]
        )
        cluster_information_response = crud.get_cluster_by_id(
            next(get_db()),
            organization_id=db_organization.id,
            cluster_id=cluster_id
        )
        return cluster_information_response
    except Exception as e:
        raise e


@router.delete("/{cluster_id}",
            summary="Delete cluster",
            tags=["Organization Admin"])
async def delete_cluster(
    cluster_id: str,
    token: str = Depends(token_validity)
):
    """HEROES Delete cluster.

    This function allows the authenticated user to delete a cluster
    from its organization.
    Return successfull deletion or error.
    """
    try:
        db_organization = crud.get_organization_by_name(
            next(get_db()), organization_name=token["organization"]
        )
        cluster_delete_response = crud.delete_cluster(
            next(get_db()),
            organization_id=db_organization.id,
            cluster_id=cluster_id
        )
        if cluster_delete_response == 1:
            return "Cluster deleted"
        elif cluster_delete_response == 0:
            return "Error: This cluster does not exist"
        else:
            return f"Error: {cluster_delete_response}"

    except Exception as e:
        raise e
