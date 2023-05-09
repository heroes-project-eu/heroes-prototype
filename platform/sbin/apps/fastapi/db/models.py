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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship


Base = declarative_base()


# class OrganizationWorkflow(Base):
#     __tablename__ = "organization_workflow"
#     organization_id = Column(ForeignKey("organizations.id"), primary_key=True)
#     workflow_id = Column(ForeignKey("workflows.id"), primary_key=True)

#     @property
#     def workflow_instances(self):
#         q = WorkflowInstance.query.join(Workflow).filter(
#             WorkflowInstance.workflow_id == self.workflow_id
#         )
#         return q.all()


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    status = Column(String, index=True)
    type = Column(String, index=True)
    clients = relationship("Client", back_populates="owner")
    servers = relationship("Server", back_populates="owner")
    clusters = relationship("Cluster", back_populates="organization")
    workflow_templates = relationship("WorkflowTemplate", back_populates="organization")
    # subscription = relationship("Shared_Object", back_populates="organization")


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    secret = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("organizations.id"))
    owner = relationship("Organization", back_populates="clients")


class Server(Base):
    __tablename__ = "servers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("organizations.id"))
    owner = relationship("Organization", back_populates="servers")


# Resources


class WorkflowTemplate(Base):
    __tablename__ = "workflow_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150))
    description = Column(String(255))
    workflow_instances = relationship("WorkflowInstance", back_populates="workflow_template")
    script_template_path = Column(String)  # Path of main.nf file
    container_path = Column(String)
    application = Column(String)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="workflow_templates")
    # license = Column(String)
    # publishment = relationship("Shared_Object", back_populates="resource_workflow")


class WorkflowInstance(Base):
    __tablename__ = "workflow_instances"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    execution_time = Column(DateTime)
    number_task = Column(Integer)
    input_dir = Column(String)
    input_size = Column(String)
    status = Column(String)
    requested_memory = Column(String)
    requested_cpu = Column(Integer)
    requested_time = Column(String)
    user_id = Column(String)
    workflow_template_id = Column(Integer, ForeignKey("workflow_templates.id"))
    workflow_template = relationship(
        "WorkflowTemplate",
        back_populates="workflow_instances"
    )
    workflow_tasks = relationship("WorkflowTask", back_populates="workflow_instance")


class WorkflowTask(Base):
    __tablename__ = "workflow_tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"))
    workflow_instance = relationship(
        "WorkflowInstance", back_populates="workflow_tasks"
    )
    requested_cpu = Column(String)
    requested_memory = Column(String)
    requested_time = Column(String)
    task_id = Column(String)
    native_id = Column(Integer)
    process = Column(String)
    name = Column(String)
    status = Column(String)
    submit = Column(DateTime)
    start = Column(DateTime)
    rss = Column(String)
    queue = Column(String)
    exit = Column(Integer)
    read_bytes = Column(String)
    write_bytes = Column(String)
    cpu_used = Column(String)
    memory_used = Column(String)


class Cluster(Base):
    __tablename__ = "clusters"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)  # Todo: Cloud or HPC_Centre
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="clusters")
    name = Column(String)
    user = Column(String)
    endpoint = Column(String)
    ssh_key = Column(String)
    port = Column(Integer)
    work_dir = Column(String)
    # partitions = relationship("Cluster_Queue", back_populates="calcul_centre")
#
#
# class Cluster_Queue(Base):
#     __tablename__ = "cluster_queues"
#     id = Column(Integer, primary_key=True, index=True)
#     calcul_centre_id = Column(Integer, ForeignKey("clusters.id"))
#     calcul_centre = relationship("Cluster", back_populates="partitions")
#     publishment = relationship("Shared_Object", back_populates="resource_partition")
#     name = Column(String)
#
#
# class Shared_Object(Base):
#     __tablename__ = "shared_objects"
#     id = Column(Integer, primary_key=True, index=True)
#     TermsOfService = Column(String)
#     resource_partition_id = Column(Integer, ForeignKey("cluster_queues.id"))
#     resource_partition = relationship("Cluster_Queue", back_populates="publishment")
#     resource_workflow_id = Column(Integer, ForeignKey("workflows.id"))
#     resource_workflow = relationship("Workflow", back_populates="publishment")
#     pricing = relationship("Object_Prices", back_populates="published_resource")
#
#
# class Object_Prices(Base):
#     __tablename__ = "object_prices"
#     id = Column(Integer, primary_key=True, index=True)
#     published_resource_id = Column(Integer, ForeignKey("shared_objects.id"))
#     published_resource = relationship("Shared_Object", back_populates="pricing")
#     target_organization_id = Column(Integer, ForeignKey("organizations.id"))
#     name = Column(String)
#     unit = Column(Integer)
#     initial = Column(Integer)
#     initial_per_unit = Column(Integer)
#     time_cost_per_unit = Column(Integer)
