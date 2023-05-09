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
import boto3
import io
from fastapi import APIRouter, \
                    Depends, \
                    HTTPException, \
                    status
import requests
import jwt
from OpenSSL import crypto
# pip install python-keycloak
from minio import Minio
# pip install minio
from typing import Optional, List
from fastapi import Request, Response
from pydantic import BaseModel, Json
from fastapi.encoders import jsonable_encoder
# custom db heroes
from db import crud
from db.database import SessionLocal
from dependencies.dependencies import token_validity
from routers.data import minio_bucket_size
from heroes_conf import settings
from .utils import process_conf_file, request_connection, get_data, send_data, get_ear_data, get_simple_data
import requests

from .custom_responses import decide_response
requests_client = requests.session()

class JobFeatures(BaseModel):
    input_size: str
    Application: str

class Organization(BaseModel):
    name: str

class JobBase(BaseModel):
    JobName : Optional[str]
    Requested_Memory: Optional[float]
    Requested_Cores: Optional[int]
    Timelimit: Optional[float]
    Application: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "JobName": "dummy",
                "Requested_Memory": 2,
                "Requested_Cores": 2,
                "Timelimit": 10.0,
                "Application": "Openfoam"
            }
        }

class Jobs(BaseModel):
    data: List[JobBase]


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(
    prefix="/organization/decision",
    tags=["Decision Module"],
    responses={404: {"description": "Not found"}},
)


async def decode_token(
    token: str = Depends(token_validity)
):
    """HEROES Decode token

    This function allows to decode a token to retrieve the information
    encoded inside.
    """
    try:
        # Check existence of the organization
        current_organization = crud.get_organization_by_name(
            organization_name=token['organization'],
            db=next(get_db())
        )
        if current_organization is None:
            raise HTTPException(
                status_code=404,
                detail="Organization not found"
            )
        url_cert = f"{settings.PROTOCOL}://" \
            + f"keycloak-server{settings.NAMESPACE}" \
            + ":8080/auth/realms/" \
            + f"{token['organization']}" \
            + "/protocol/openid-connect/certs"
        # Get the organization certificate in order to decode the token with
        cert_response = requests.get(url_cert)
        cert_response = cert_response.json()
        keycloak_certificate = cert_response['keys'][0]['x5c'][0]
        keycloak_certificate = "-----BEGIN CERTIFICATE-----\n" \
            + keycloak_certificate \
            + "\n-----END CERTIFICATE-----"
        crtObj = crypto.load_certificate(
            crypto.FILETYPE_PEM,
            keycloak_certificate
        )
        pubKeyObject = crtObj.get_pubkey()
        publicPEM = crypto.dump_publickey(
            crypto.FILETYPE_PEM,
            pubKeyObject
        ).decode('utf-8')
        # Return the token decoded with the organization public key
        return jwt.decode(
            token['access_token'],
            key=publicPEM,
            algorithms=["RS256"],
            options={"verify_signature": False})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

# TODO: [HER-55] Change type of Data pass to fastApi  from json file to json data
@router.post("/decide",
    tags=["Decision Module"],
    summary="",
    responses= {
        200: {
            "description": "Decision Module Response",
            "content": {
                "application/json": {
                    "example": decide_response,
                }
            },
        },
    },        
)
async def decide(
    policy: str,
    ranking: str, # rank = "workload" or "job"
    jobs: Jobs,
    workflow_template_id: int,
    workflow_input_dir: str,
    token: str = Depends(token_validity)
):
    """HEROES Request placement function

    This function allows the authenticated and authorized users to
    request placement decision to the decision module
    """
    try:
        # -X POST f"{PROTOCOL}://{OKA_NAMESPACE}:8000/ait/decision_module/decide?optimize={policy}&ranking={ranking}
        #   -F "data=@${path_to_jobs_json}"

        decoded_token = await decode_token(token)
        db_organization = crud.get_organization_by_name(
            next(get_db()), organization_name=token["organization"]
        )
        placement_decision = {}
        jobs = jsonable_encoder(jobs)
        url = f"{settings.PROTOCOL}://{settings.OKA_NAMESPACE}"
        # request connection to decision module Api
        res = request_connection(requests_client,
                                 url,
                                 settings.OKA_USERNAME,
                                 settings.OKA_PASSWORD)
        # jobs["data"][0]["JobID"] = random.randint(1, 101)
        jobs["data"][0]["Partition"] = "test"
        jobs["data"][0]["QOS"] = "1"
        jobs["data"][0]["Account"] = "default"
        jobs["data"][0]["Cluster"] = "heroes"

        if workflow_input_dir[0] != "/":
            workflow_input_dir = f"/{workflow_input_dir}"
        bucket_name = workflow_input_dir.split("/")[1]
        bucket_prefix = "/".join(workflow_input_dir.split("/")[2:])
        jobs["data"][0]["Cust_Input_Size"] = await minio_bucket_size(
            bucket=bucket_name,
            bucket_prefix=bucket_prefix,
            token=token
        )
        jobs["data"][0]["Cust_HEROES_ORGANIZATION_ID"] = db_organization.id
        jobs["data"][0]["Cust_HEROES_ORGANIZATION_NAME"] = token["organization"]
        jobs["data"][0]["Cust_HEROES_TEMPLATE_WORKFLOW_ID"] = workflow_template_id
        # jobs["data"][0]["Requested_Nodes"] = ""

        if decoded_token["sub"] == "4622fbf9-0db6-47bb-a8ee-b080edddc68e":
            jobs["data"][0]["Cust_HEROES_USER_ID"] = "0"
        elif decoded_token["sub"] == "a2a9f44a-623f-4092-bcbc-128a6dfefcfa":
            jobs["data"][0]["Cust_HEROES_USER_ID"] = "1"
        elif decoded_token["sub"] == "ddd46aff-147c-42b3-9fd5-603effe07fd3":
            jobs["data"][0]["Cust_HEROES_USER_ID"] = "2"
        elif decoded_token["sub"] == "3a858a48-ad0a-4090-88f2-7326150b8cc0":
            jobs["data"][0]["Cust_HEROES_USER_ID"] = "3"
        elif decoded_token["sub"] == "0e1f06cd-9846-45e7-9900-c5798b481e63":
            jobs["data"][0]["Cust_HEROES_USER_ID"] = "4"
        elif decoded_token["sub"] == "97ee1818-2de4-4a0c-8072-f0e99fd307ef":
            jobs["data"][0]["Cust_HEROES_USER_ID"] = "5"
        elif decoded_token["sub"] == "906cc9f3-96a9-40ef-bd72-87f767dcd879":
            jobs["data"][0]["Cust_HEROES_USER_ID"] = "6"
        elif decoded_token["sub"] == "520d77ce-472b-43f6-aea7-a6f15b0657ec":
            jobs["data"][0]["Cust_HEROES_USER_ID"] = "7"
        elif decoded_token["sub"] == "20e407b7-37a9-4c95-894e-52c81856b683":
            jobs["data"][0]["Cust_HEROES_USER_ID"] = "8"
        elif decoded_token["sub"] == "1bfcf12e-3f5f-4e2d-be24-9197ccc0b2c3":
            jobs["data"][0]["Cust_HEROES_USER_ID"] = "9"
        else:
            jobs["data"][0]["Cust_HEROES_USER_ID"] = "0"

        # get decision
        placement_decision = get_data(requests_client,
                                      f"{url}/ait/decision_module/decide?optimize={policy}&ranking={ranking}",
                                      res["csrf_token"],
                                      jobs["data"])

        return placement_decision
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/ingest_ear_files",
             tags=["Decision Module"],
             summary="")
async def ingest_ear_files(
    cluster_name: str,
    path_to_csv_app_file: str,  # Todo: make file
    path_to_csv_loops_file: str,  # Todo: make file
    input_size: int,
    application: str,
    token: str = Depends(token_validity)
):
    """HEROES Request placement function

    This function allows the authenticated and authorized users to
    ...
    """
    try:
        res = request_connection(
            requests_client,
            f"{settings.PROTOCOL}://{settings.OKA_NAMESPACE}",
            settings.OKA_USERNAME,
            settings.OKA_PASSWORD,
        )
        files = get_ear_data(path_to_csv_app_file, path_to_csv_loops_file)
        job_features = {
            "input_size": input_size,
            "application": application,
        }

        return send_data(requests_client,
                         f"{settings.PROTOCOL}://{settings.OKA_NAMESPACE}/ait/decision_module/ingest_ear_files?cluster={cluster_name}",
                         res["csrf_token"],
                         files["apps"],
                         files["loops"],
                         job_features)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.get("/policies",
             tags=["Decision Module"],
             summary="")
async def get_policies(
    token: str = Depends(token_validity)
):
    """HEROES List decision policies function

    This function allows the authenticated and authorized users to
    list the available policies of the decision module
    """
    try:

        url = f"{settings.PROTOCOL}://{settings.OKA_NAMESPACE}"
        # request connection to decision module Api
        res = request_connection(requests_client,
                                 url,
                                 settings.OKA_USERNAME,
                                 settings.OKA_PASSWORD)
        decision_policies = {}
        decision_policies = get_simple_data(requests_client,
                                      f"{url}/ait/decision_module/get_policies",
                                      res["csrf_token"])
        return decision_policies
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
