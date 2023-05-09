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
#   the data management function provided by minio
#
###############################################################################
from fastapi import APIRouter, Depends, HTTPException
from db import crud, models, schemas
from db.database import SessionLocal, engine, Base
from routers.data import decode_token, minio_credentials
from routers.utils import parse_workflow, slice_to_string_key
from routers.data import minio_bucket_size
from dependencies.dependencies import token_validity
from heroes_conf import settings
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
import pika
import uuid
import json
import pandas as pd

from .custom_responses import examples_body
from .utils import add_unit
Base.metadata.create_all(bind=engine)

class WorkflowSubmitParameters(BaseModel):
    workflow_name: str
    workflow_input_dir: str
    workflow_placement: dict
    workflow_parameters: Optional[dict] = None


class NextflowWorkerClient(object):

    def __init__(self):
        rabbitmq_host = f"rabbitmq-worker-workflow{settings.NAMESPACE}"
        credentials = pika.PlainCredentials('heroes_fastapi', 'xxxx')
        # credentials = pika.PlainCredentials(settings.RABBITMQ_USERNAME, settings.RABBITMQ_PASSWORD)

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=rabbitmq_host,
                port=5672,
                heartbeat=60,
                connection_attempts=5,
                retry_delay=1,
                credentials=credentials))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, data):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='worker_workflow_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(data))
        self.connection.process_data_events(time_limit=None)
        return self.response

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(
    prefix="/organization/workflow",
    tags=["Workflow Management"],
    responses={404: {"description": "Not found"}},
)


def workflow_monitoring():
    try:
        db_response = None
        data = { "action": "listener" }
        status = ["PENDING", "RUNNING"]
        data_columns = {"process":"process_name", "time":"requested_time", "memory":"requested_memory", "cpus":"requested_cpu"}

        # get workflow_task from nexflow task id
        print("WORKFLOW MONITORING")
        workflow_tasks = crud.list_workflow_task_by_status(
            next(get_db()),
            status=status
        )
        # print(workflow_tasks)

        workflow_instance_id_list = []

        for workflow_current_task in workflow_tasks:
            current_workflow_instance_id = f"wiid-{workflow_current_task.workflow_instance_id}"
            print(f"Current task workflow instance id: {current_workflow_instance_id}")
            if current_workflow_instance_id not in workflow_instance_id_list:
                workflow_instance_id_list.append(current_workflow_instance_id)

        print(workflow_instance_id_list)
        for workflow_instance_id in workflow_instance_id_list:
            print(workflow_instance_id)
            data["instance_id"] = workflow_instance_id
            nextflow_client = NextflowWorkerClient()
            response = nextflow_client.call(data)
            print("NextflowWorkerClient: DONE")
            print(response)
            workflow_response = eval(response)
            workflow_tasks_list = eval(workflow_response.decode("utf-8").split('\n')[0])

            for current_task in workflow_tasks_list:
                db_response = crud.update_workflow_task(
                    db=next(get_db()),
                    workflow_instance_id=workflow_instance_id.split("wiid-")[1],
                    task_id=current_task["task_id"],
                    data=current_task
                )
                # print(db_response)

            workflow_tasks = crud.list_workflow_task_by_workflow_instance_id(
                next(get_db()),
                workflow_instance_id=workflow_instance_id.split("wiid-")[1]
            )

            workflow_tasks_status = []
            for task in workflow_tasks:
                workflow_tasks_status.append(task.status)

            print(workflow_tasks_status)
            workflow_status = "PENDING"
            if "FAILED" in workflow_tasks_status:
                workflow_status = "FAILED"
            elif "ABORTED" in workflow_tasks_status:
                workflow_status = "ABORTED"
            elif "RUNNING" in workflow_tasks_status:
                workflow_status = "RUNNING"
            elif "PENDING" in workflow_tasks_status:
                workflow_status = "PENDING"
            elif not [task_status for task_status in workflow_tasks_status if task_status != "COMPLETED"]:
                workflow_status = "COMPLETED"

            # print(f"FINAL STATUS: {workflow_status}")
            response = crud.update_workflow_instance(
                db=next(get_db()),
                id=workflow_instance_id.split("wiid-")[1],
                status=workflow_status
            )
            # print(response)

    except Exception as e:
        raise e


@router.get(
    "/template",
    tags=["Workflow Management"],
    summary="List the available workflows for the authenticated user",
)
async def list_template_workflow(
    skip: int = 0,
    limit: int = 100,
    token: str = Depends(token_validity)
):
    """HEROES List user accessible workflows.

    This function allows the authenticated user to list their workflows.
    Return a list of workflows
    """
    try:
        db_organization = crud.get_organization_by_name(
            next(get_db()), organization_name=token["organization"]
        )
        return crud.list_workflow_templates(
            next(get_db()),
            organization_id=db_organization.id,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise e


@router.get(
    "/instance",
    tags=["Workflow Management"],
    summary="List all running workflows Instance available for the authenticated user",
)
async def list_my_workflow_instances(
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
        decoded_token = await decode_token(token)
        print(decoded_token["sub"])
        list_workflow_instance_reponse = crud.list_workflow_instances_by_user_id(
            next(get_db()),
            user_id=decoded_token["sub"],
            skip=skip,
            limit=limit
        )
        print(print(decoded_token["sub"]))
        return list_workflow_instance_reponse
    except Exception as e:
        raise e


@router.post("/submit",
    response_model=schemas.WorkflowInstance,
    tags=["Workflow Management"],
    summary="Submit a workflow"
)
async def submit_workflow(
    workflow_template_id: str,
    workflow_submit_parameters: WorkflowSubmitParameters= examples_body,
    token: str = Depends(token_validity)

):
    """HEROES Submit workflow to Nextflow container.

    This function is for internal usages only. It allows the user to submit
    a workflow in its authorized clusters.
    """
    try:
        print(workflow_template_id)
        print(workflow_submit_parameters)

        db_organization = crud.get_organization_by_name(
            next(get_db()), organization_name=token["organization"]
        )
        decoded_token = await decode_token(token)
        print(decoded_token["sub"])
        userCredentials = await minio_credentials(
            decoded_token["preferred_username"], decoded_token["sub"], token
        )

        workflow_information = crud.get_workflow_template_by_id(
            next(get_db()),
            organization_id=db_organization.id,
            workflow_template_id=workflow_template_id
        )
        print(workflow_information.script_template_path)
        tasks = await parse_workflow(workflow_information.script_template_path, token)


        if workflow_submit_parameters.workflow_parameters and "cpus" in workflow_submit_parameters.workflow_parameters:
            requested_cpu = workflow_submit_parameters.workflow_parameters["cpus"]
        else:
            requested_cpu = 0

        if workflow_submit_parameters.workflow_parameters and "memory" in workflow_submit_parameters.workflow_parameters:
            requested_memory = add_unit("memory", workflow_submit_parameters.workflow_parameters["memory"])
        else:
            requested_memory = 0

        if workflow_submit_parameters.workflow_parameters and "time" in workflow_submit_parameters.workflow_parameters:
            requested_time = add_unit("time", workflow_submit_parameters.workflow_parameters["time"])
        else:
            requested_time = 0
        # Get the worfklow_input_size
        bucket_name = workflow_submit_parameters.workflow_input_dir.split("/")[1]
        bucket_prefix = "/".join(workflow_submit_parameters.workflow_input_dir.split("/")[2:])
        workflow_input_size = await minio_bucket_size(bucket=bucket_name,bucket_prefix=bucket_prefix, token=token)
        workflow_instance = schemas.WorkflowInstanceCreate(
            name=workflow_submit_parameters.workflow_name,
            execution_time=datetime.now(),
            number_task=len(tasks.keys()),
            input_dir=workflow_submit_parameters.workflow_input_dir,
            input_size=workflow_input_size,
            status="PENDING",
            requested_memory=requested_memory,
            requested_cpu=requested_cpu,
            requested_time=requested_time
        )

        workflow_instance_response = crud.create_workflow_instance(
            db=next(get_db()),
            workflow_instance=workflow_instance,
            workflow_template_id=workflow_template_id,
            user_id=decoded_token["sub"]
        )
        print(workflow_instance_response)
        print(str(workflow_instance_response.id))
        # print(tasks)
        # Task binding
        cluster_dict = {}
        workflow_cluster = None
        # Check if there is 1 cluster per task or 1 cluster for the workflow
        if len(workflow_submit_parameters.workflow_placement) == 1 and workflow_submit_parameters.workflow_placement["cluster"]:
            workflow_cluster = workflow_submit_parameters.workflow_placement["cluster"]
            workflow_submit_parameters.workflow_placement = {}
            print("Mode: Cluster per workflow")
        else:
            print("Mode: Cluster per task")

        task_id = 0
        for task in tasks:
            task_id = task_id+1
            if workflow_cluster != None:
                workflow_submit_parameters.workflow_placement[task] = {}
                workflow_submit_parameters.workflow_placement[task]["cluster"] = workflow_cluster

            if workflow_submit_parameters.workflow_placement[task]["cluster"] not in cluster_dict:
                current_cluster = crud.get_cluster_by_name(
                    next(get_db()),
                    organization_id=db_organization.id,
                    cluster_name=workflow_submit_parameters.workflow_placement[task]['cluster']
                )
                # print(current_cluster)
                cluster_dict[workflow_submit_parameters.workflow_placement[task]["cluster"]] = {
                    "name": current_cluster.name,
                    "user": current_cluster.user,
                    "address": current_cluster.endpoint,
                    "ssh_path": current_cluster.ssh_key,
                    "port": current_cluster.port,
                    "work_dir": current_cluster.work_dir
                }

            tasks[task]["cluster"] = cluster_dict[workflow_submit_parameters.workflow_placement[task]["cluster"]]
            tasks[task]["container"] = f"{cluster_dict[workflow_submit_parameters.workflow_placement[task]['cluster']]['work_dir']}/{db_organization.id}/{decoded_token['sub']}/{workflow_template_id}/wiid-{workflow_instance_response.id}/{workflow_information.container_path.split('/')[-1]}"
            tasks[task]["singularityContainer"] = workflow_information.container_path

            if "cpus" in tasks[task] and tasks[task]["cpus"] == "HEROES_CPUS":
                # tasks[task]["cpus"] = workflow_submit_parameters.workflow_parameters[task]["cpus"]
                # print("cpus = HEROES_CPUS")
                tasks[task]["cpus"] = workflow_submit_parameters.workflow_parameters["cpus"]
            if "memory" in tasks[task] and tasks[task]["memory"] == "HEROES_MEMORY":
                # print("memory = HEROES_MEMORY")
                # tasks[task]["memory"] = workflow_submit_parameters.workflow_parameters[task]["memory"]
                tasks[task]["memory"] = workflow_submit_parameters.workflow_parameters["memory"]
            if "time" in tasks[task] and tasks[task]["time"] == "HEROES_TIME":
                # print("time = HEROES_TIME")
                # tasks[task]["time"] = workflow_submit_parameters.workflow_parameters[task]["time"]
                tasks[task]["time"] = workflow_submit_parameters.workflow_parameters["time"]

            workflow_task = schemas.WorkflowTaskCreate(
                name=task,
                workflow_instance_id=workflow_instance_response.id,
                task_id=task_id,
                status="PENDING",
                requested_cpu=str(requested_cpu),
                requested_memory=str(requested_memory),
                requested_time=str(requested_time)
            )

            print("Show workflow_task object")
            print(workflow_task.name)
            print(workflow_task.workflow_instance_id)
            print(workflow_task.status)
            print(workflow_task.requested_cpu)
            print(workflow_task.requested_memory)
            print(workflow_task.requested_time)

            create_workflow_task_response = crud.create_workflow_task(
                db=next(get_db()),
                workflow_task=workflow_task
            )
            print(create_workflow_task_response)

        print("END OF TASKS")

        data = {
            "action": "executor",
            "organization": {
                "organization": [
                    {
                        "name": token["organization"],
                        "uuid": str(db_organization.id),
                        "users": [
                            {
                                "name": decoded_token["preferred_username"],
                                "uuid": decoded_token["sub"],
                                "mail": "example@ucit.fr",
                            }
                        ],
                    }
                ]
            },
            "workflow": {
                "id": workflow_template_id,
                "instance_id": f"wiid-{str(workflow_instance_response.id)}",
                "script": workflow_information.script_template_path,
                "job_name": workflow_submit_parameters.workflow_name,
                "tasks": tasks,
                "data": {
                    "inputDir": workflow_submit_parameters.workflow_input_dir,
                    "credentials": {
                        "AccessKeyId": userCredentials["Credentials"]["AccessKeyId"],
                        "SecretAccessKey": userCredentials["Credentials"]["SecretAccessKey"],
                        "SessionToken": userCredentials["Credentials"]["SessionToken"]
                    }
                }
            }
        }

        print(data)
        nextflow_client = NextflowWorkerClient()
        print("NextflowWorkerClient: DONE")
        response = nextflow_client.call(data)
        print("CALL IS DONE")
        print(response)

        return workflow_instance_response

    except Exception as e:
        raise e



@router.get("/instance/{workflow_instance_id}",
            tags=["Workflow Management"],
            summary="Get information and status about a submitted workflow"
)
async def workflow_status(
    workflow_instance_id: str,
    token: str = Depends(token_validity)
):
    """HEROES Status of running workflows.

    This function allows the authenticated user to get the status their
    instance workflows.
    Return workflow informations
    """
    try:
        db_organization = crud.get_organization_by_name(
            next(get_db()), organization_name=token["organization"]
        )

        decoded_token = await decode_token(token)
        data = {
            "action": "listener",
            "organization": {
                "organization": [
                    {
                        "name": token["organization"],
                        "uuid": str(db_organization.id),
                        "users": [
                            {
                                "name": decoded_token["preferred_username"],
                                "uuid": decoded_token["sub"],
                                "mail": "example@ucit.fr",
                            }
                        ],
                    }
                ]
            },
            "workflow": {
                "instance_id": workflow_instance_id
            }
        }

        workflow_instance_response = None
        workflow_instance_response = crud.get_workflow_instance_by_id(next(get_db()), decoded_token["sub"], workflow_instance_id)
        if not workflow_instance_response:
            raise HTTPException(status_code=404, detail="User not authorized to access")

        return workflow_instance_response

    except Exception as e:
        raise e


@router.delete("/instance/{workflow_instance_id}",
    tags=["Workflow Management"],
    summary="Cancel a running workflow"
)
async def workflow_cancel(workflow_instance_id: str, token: str = Depends(token_validity)):
    """HEROES Status of running workflows.

    This function allows the authenticated user to get the status their
    running workflows.
    Return workflow informations
    """
    try:
        db_organization = crud.get_organization_by_name(
            next(get_db()), organization_name=token["organization"]
        )
        decoded_token = await decode_token(token)
        data = {
            "action": "canceler",
            "organization": {
                "organization": [
                    {
                        "name": token["organization"],
                        "uuid": str(db_organization.id),
                        "users": [
                            {
                                "name": decoded_token["preferred_username"],
                                "uuid": decoded_token["sub"],
                                "mail": "example@ucit.fr",
                            }
                        ],
                    }
                ]
            },
            "workflow": {
                "instance_id": workflow_instance_id
            }
        }

        nextflow_client = NextflowWorkerClient()
        print("NextflowWorkerClient: DONE")
        response = nextflow_client.call(data)

        return response
    except Exception as e:
        raise e


@router.get("/visualization",
    tags=["Workflow Management"],
    summary="Get Visualization Node informations"
)
async def get_visualization(token: str = Depends(token_validity)):
    """HEROES Call Visualization Node.

    This function allows the authenticated user to get visualization node informations
    Return Visualization informations to connect
    """
    try:
        decoded_token = await decode_token(token)
        data = [
            {
                "host": "http://ingr-nlb-heroes-infra-aa6e5ae4a2ff1eba.elb.eu-west-1.amazonaws.com:6081/vnc.html",
                "port": "5901",
                "password" : "xxxx"
            },
        ]

        return data
    except Exception as e:
        raise e
