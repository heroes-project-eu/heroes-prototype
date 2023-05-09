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
from typing import List, Optional, Union
from datetime import datetime, time
from pydantic import BaseModel, FilePath, DirectoryPath


# Clients
class ClientBase(BaseModel):
    name: str
    secret: str


class ClientCreate(ClientBase):
    pass


class Client(ClientBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


# Servers
class ServerBase(BaseModel):
    name: str
    status: str


class ServerCreate(ServerBase):
    pass


class Server(ServerBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


# Workflow Instance Tasks


class WorkflowTaskCreate(BaseModel):
    name: str
    workflow_instance_id: int
    task_id: str
    status: str
    requested_cpu: Optional[str] = None
    requested_time: Optional[str] = None
    requested_memory: Optional[str] = None
    native_id: Optional[int] = None
    process: Optional[str] = None
    submit: Optional[datetime] = None
    start: Optional[datetime] = None
    rss: Optional[str] = None
    queue: Optional[str] = None
    exit: Optional[int] = None
    read_bytes: Optional[str] = None
    write_bytes: Optional[str] = None
    cpu_used: Optional[str] = None
    memory_used: Optional[str] = None

class WorkflowTask(WorkflowTaskCreate):
    id: int

    class Config:
        orm_mode = True


# Workflow Instances
class WorkflowInstanceCreate(BaseModel):
    name: str
    execution_time: datetime
    number_task: int
    input_dir: str
    input_size: str
    status: str = "PENDING"
    requested_memory: Union[int, str]
    requested_cpu: Union[int, str]
    requested_time: Union[int, str]


class WorkflowInstance(WorkflowInstanceCreate):
    id: int
    user_id: str
    workflow_template_id: str
    workflow_task: Optional[List[WorkflowTask]] = []

    class Config:
        orm_mode = True


# Workflow Templates
class WorkflowTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    script_template_path: str
    container_path: str
    application: str


class WorkflowTemplate(WorkflowTemplateCreate):
    id: int
    organization_id: int
    workflow_instances: Optional[List[WorkflowInstance]] = []

    class Config:
        orm_mode = True


# Clusters
class ClusterCreate(BaseModel):
    name: str
    user: str
    endpoint: str
    ssh_key: str
    port: int = 22
    work_dir: str


class Cluster(ClusterCreate):
    id: int
    type: str
    organization_id: int

    class Config:
        orm_mode = True

# Organizations
class OrganizationBase(BaseModel):
    name: str


class OrganizationCreate(OrganizationBase):
    pass


class Organization(OrganizationBase):
    id: int
    status: str
    clients: Optional[List[Client]] = []
    servers: Optional[List[Server]] = []
    clusters: Optional[List[Cluster]] = []
    # workflows = Optional[List[Workflow]]

    class Config:
        orm_mode = True
