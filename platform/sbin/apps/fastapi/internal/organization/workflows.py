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
from db.crud import get_organization_by_name
from db.database import SessionLocal
from db.schemas import WorkflowTemplateCreate
from db.models import WorkflowTemplate
from db import crud, models, schemas
from routers.data import decode_token
from dependencies.dependencies import token_validity
from heroes_conf import settings
from datetime import datetime
from typing import Optional
import json

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Organization Admin: Workflow
router = APIRouter(
    prefix="/organization/admin/workflow",
    tags=["Organization Admin"]
)


@router.post(
    "/template",
    response_model=schemas.WorkflowTemplate,
    tags=["Organization Admin"],
    summary="Create workflow template"
)
async def create_workflow_template(
    workflow_template: schemas.WorkflowTemplateCreate,
    token: str = Depends(token_validity)
):
    """HEROES Create Workflow template.

    This function allows the authenticated user to create a workflow template.
    Return the status
    """
    try:
        db_organization = get_organization_by_name(
            next(get_db()), organization_name=token["organization"]
        )
        workflow_template_response = crud.create_workflow_template(
            next(get_db()),
            workflow_template=workflow_template,
            organization_id=db_organization.id
        )
        return workflow_template_response
    except Exception as e:
        raise e


@router.delete("/template/{workflow_template_id}",
            summary="Delete workflow template",
            tags=["Organization Admin"])
async def delete_cluster(
    workflow_template_id: str,
    token: str = Depends(token_validity)
):
    """HEROES Delete workflow template.

    This function allows the authenticated user to delete a workflow template
    from its organization.
    Return successfull deletion or error.
    """
    try:
        db_organization = crud.get_organization_by_name(
            next(get_db()), organization_name=token["organization"]
        )
        workflow_template_delete_response = crud.delete_workflow_template(
            next(get_db()),
            organization_id=db_organization.id,
            workflow_template_id=workflow_template_id
        )
        if cluster_delete_response == 1:
            return "Cluster deleted"
        elif cluster_delete_response == 0:
            return "Error: This cluster does not exist"
        else:
            return f"Error: {cluster_delete_response}"

    except Exception as e:
        raise e


@router.get(
    "/instance/{workflow_template_id}",
    tags=["Organization Admin"],
    summary="List all running workflows Instance available for the organization, can be filtered on workflow template id",
)
async def list_workflow_instance(
    workflow_template_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    token: str = Depends(token_validity)
):
    """HEROES List user running accessible workflows.

    This function allows the authenticated user to list their running workflows.
    Return a list of  running workflows
    """
    try:
        list_workflow_instance_reponse = {}
        if workflow_template_id:
            list_workflow_instance_reponse = crud.list_workflow_instances_by_wf_id(
                next(get_db()),
                workflow_template_id=workflow_template_id,
                skip=skip,
                limit=limit
            )
        else:
            workflow_templates_list = await list_template_workflow(token=token)
            for template_workflow in workflow_templates_list:
                current_workflow_instances = crud.list_workflow_instances_by_wf_id(
                    next(get_db()),
                    workflow_template_id=template_workflow.id,
                    skip=skip,
                    limit=limit
                )
                list_workflow_instance_reponse[template_workflow.id] = current_workflow_instances
        return list_workflow_instance_reponse
    except Exception as e:
        raise e
