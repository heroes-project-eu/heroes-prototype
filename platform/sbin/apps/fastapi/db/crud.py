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
from typing import List, Union
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException
from . import models, schemas
from .exception import ObjectNotFoundError


# Organizations
def get_organization(db: Session, organization_id: int):
    return db.query(models.Organization).filter(
        models.Organization.id == organization_id
    ).first()


def get_organization_by_name(db: Session, organization_name: str):
    return db.query(models.Organization).filter(
        models.Organization.name == organization_name
    ).first()


def get_organizations(db: Session, skip: int = 0, limit: int = 1000):
    return db.query(models.Organization).offset(skip).limit(limit).all()


def create_organization(db: Session, organization: schemas.OrganizationCreate):
    name = organization.name
    status = "CREATE_IN_PROGRESS"
    db_organization = models.Organization(name=name, status=status)
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization


def update_organization(
    db: Session,
    organization: schemas.Organization
):
    db_organization = db.query(models.Organization).filter(
       models.Organization.name == organization.name
    ).first()
    if organization.status:
        db_organization.status = organization.status
    db.add(db_organization)
    db.commit()
    return db_organization


def delete_organization(
    db: Session,
    organization_id: int
):
    db_organization = db.query(models.Organization).filter(
        models.Organization.id == organization_id
    ).first()
    db.delete(db_organization)
    db.commit()
    return db_organization


# Clients
def get_clients(db: Session, skip: int = 0, limit: int = 1000):
    return db.query(models.Client).offset(skip).limit(limit).all()


def create_organization_client(
    db: Session,
    client: schemas.ClientCreate,
    organization_id: int
):
    db_client = models.Client(**client.dict(), owner_id=organization_id)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def delete_organization_client(
    db: Session,
    client_id: int
):
    db_client = db.query(models.Client).filter(
        models.Client.id == client_id
    ).first()
    db.delete(db_client)
    db.commit()
    return db_client


# Servers
def get_servers(db: Session, skip: int = 0, limit: int = 1000):
    return db.query(models.Server).offset(skip).limit(limit).all()


def create_organization_server(
    db: Session,
    server: schemas.ServerCreate,
    organization_id: int
):
    db_server = models.Server(**server.dict(), owner_id=organization_id)
    db.add(db_server)
    db.commit()
    db.refresh(db_server)
    return db_server


def delete_organization_server(
    db: Session,
    server_id: int
):
    db_server = db.query(models.Server).filter(
        models.Server.id == server_id
    ).first()
    db.delete(db_server)
    db.commit()
    return db_server


# Workflow Templates
def create_workflow_template(
    db: Session,
    workflow_template: schemas.WorkflowTemplateCreate,
    organization_id: int
):
    db_workflow = models.WorkflowTemplate(
        **workflow_template.dict(),
        organization_id=organization_id
    )
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow


def get_workflow_template_by_id(
    db: Session,
    organization_id: int,
    workflow_template_id: int
):
    return db.query(models.WorkflowTemplate).filter(
        models.WorkflowTemplate.organization_id == organization_id,
        models.WorkflowTemplate.id == workflow_template_id
    ).first()


def list_workflow_templates(db: Session, organization_id: int, skip: int = 0, limit: int = 1000):
    return db.query(models.WorkflowTemplate).filter(
        models.WorkflowTemplate.organization_id == organization_id
    ).offset(skip).limit(limit).all()


def delete_workflow_template(db: Session, organization_id: int, workflow_template_id: int):
    db_workflow = db.query(models.WorkflowTemplate).filter(
        models.WorkflowTemplate.organization_id == organization_id,
        models.WorkflowTemplate.id == workflow_template_id
    ).delete()
    db.commit()
    return db_workflow


# Workflow Instances
def create_workflow_instance(
    db: Session,
    workflow_instance: schemas.WorkflowInstanceCreate,
    workflow_template_id: int,
    user_id: int
):
    db_workflow = models.WorkflowInstance(
        **workflow_instance.dict(),
        workflow_template_id=workflow_template_id,
        user_id=user_id
    )
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow


def create_workflow_task(db: Session, workflow_task: schemas.WorkflowTaskCreate):
    db_workflow_task = models.WorkflowTask(**workflow_task.dict())
    db.add(db_workflow_task)
    db.commit()
    db.refresh(db_workflow_task)
    return db_workflow_task


def list_workflow_task_by_workflow_instance_id(db: Session, workflow_instance_id, skip: int = 0, limit: int = 1000):
    return db.query(models.WorkflowTask).filter(
        models.WorkflowTask.workflow_instance_id == workflow_instance_id
    ).offset(skip).limit(limit).all()


def list_workflow_task_by_status(db: Session, status: List[str] = [], skip: int = 0, limit: int = 1000):
    return db.query(models.WorkflowTask).filter(
        models.WorkflowTask.status.in_(status)
    ).offset(skip).limit(limit).all()


def get_workflow_task_by_id(db: Session, task_id):
    return db.query(models.WorkflowTask).filter(
        models.WorkflowTask.id == task_id
    ).first()


def get_workflow_task_by_name(db: Session, name):
    return db.query(models.WorkflowTask).filter(
        models.WorkflowTask.name == name
    ).first()


def update_workflow_task(
    db: Session,
    workflow_instance_id: int,
    task_id: int,
    data
):
    # print(f"{workflow_instance_id} : {task_id}")
    workflow_task = db.query(models.WorkflowTask).filter(
       models.WorkflowTask.workflow_instance_id == workflow_instance_id,
       models.WorkflowTask.task_id == task_id
    ).first()
    if workflow_task is None:
        return ObjectNotFoundError()
    data["name"] = workflow_task.name
    for key, value in data.items():
        # print(f"{key} == {value}")
        setattr(workflow_task, key, value)
    db.add(workflow_task)
    db.commit()
    db.refresh(workflow_task)
    return workflow_task


def get_workflow_instance_by_id(
    db: Session,
    user_id: int,
    workflow_instance_id: int
):
    return db.query(models.WorkflowInstance).filter(
        models.WorkflowInstance.user_id == user_id,
        models.WorkflowInstance.id == workflow_instance_id
    ).first()


def list_workflow_instances_by_wf_id(
    db: Session,
    workflow_template_id: int,
    skip: int = 0,
    limit: int = 1000
):
    return db.query(models.WorkflowInstance).filter(
        models.WorkflowInstance.workflow_template_id == workflow_template_id
    ).offset(skip).limit(limit).all()


def list_workflow_instances_by_user_id(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 1000
):
    return db.query(models.WorkflowInstance).filter(
        models.WorkflowInstance.user_id == user_id
    ).order_by(models.WorkflowInstance.id.desc()).offset(skip).limit(limit).all()


def delete_workflow_instance(db: Session, workflow_instance_id: int):
    db_workflow = db.query(models.WorkflowInstance).filter(
        models.WorkflowInstance.id == workflow_instance_id
    ).delete()
    db.commit()
    return db_workflow


def update_workflow_instance(
    db: Session,
    id: int,
    status: str
):
    db_workflow_instance = db.query(models.WorkflowInstance).filter(
       models.WorkflowInstance.id == id
    ).first()
    if db_workflow_instance.status:
        db_workflow_instance.status = status
    db.add(db_workflow_instance)
    db.commit()
    return db_workflow_instance

# def update_workflow(db: Session, workflow: Union[int, models.Workflow], data: schemas.WorkflowCreate):
#     if isinstance(workflow, int):
#         workflow = get_workflow_by_id(db, workflow)
#     if workflow is None:
#         return None
#     for key, value in data:
#         setattr(workflow, key, value)
#     db.commit()
#     return workflow


# Clusters
def create_cluster(
    db: Session,
    cluster: schemas.ClusterCreate,
    organization_id: int,
    cluster_type: int
):
    db_cluster = models.Cluster(
        **cluster.dict(),
        organization_id=organization_id,
        type=cluster_type
    )
    db.add(db_cluster)
    db.commit()
    db.refresh(db_cluster)
    return db_cluster


def get_cluster_by_id(
    db: Session,
    organization_id: int,
    cluster_id: int
):
    return db.query(models.Cluster).filter(
        models.Cluster.organization_id == organization_id,
        models.Cluster.id == cluster_id
    ).first()


def get_cluster_by_name(
    db: Session,
    organization_id: int,
    cluster_name: int
):
    return db.query(models.Cluster).filter(
        models.Cluster.organization_id == organization_id,
        models.Cluster.name == cluster_name
    ).first()


def list_clusters(db: Session, organization_id: int, skip: int = 0, limit: int = 1000):
    return db.query(models.Cluster).filter(
        models.Cluster.organization_id == organization_id
    ).offset(skip).limit(limit).all()


def delete_cluster(db: Session, organization_id: int, cluster_id: int):
    db_cluster = db.query(models.Cluster).filter(
        models.Cluster.organization_id == organization_id,
        models.Cluster.id == cluster_id
    ).delete()
    db.commit()
    return db_cluster


# generic function
def create_object(db: Session, db_object):
    db.add(db_object)
    db.commit()
    db.refresh(db_object)
    return db_object

def list_objects(db: Session, Object, skip: int = 0, limit: int = 1000):
    return db.query(Object).offset(skip).limit(limit).all()


def get_object_by_name(db: Session, Object, element_name):
    try:
        return db.query(Object).filter(name=element_name)
    except ObjectNotFoundError as e:
        raise HTTPException(**e.__dict__)


def get_object_by_id(db: Session, Object, element_id: int):
    try:
        return db.query(Object).get(element_id)
    except ObjectNotFoundError as e:
        raise HTTPException(**e.__dict__)


def delete_object(db: Session, Object, element_id: int):
    db_object = db.query(Object).filter(object.id == element_id).delete()
    db.commit()
    return db_object


def update_object(db: Session, element_id: int, data):
    if isinstance(element_id, int):
        object = get_object_by_id(db, element_id)
    if object is None:
        return ObjectNotFoundError()
    for key, value in data:
        setattr(object, key, value)
    db.commit()
    return object
