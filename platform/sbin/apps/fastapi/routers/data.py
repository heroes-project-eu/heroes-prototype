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
                    status, \
                    File, \
                    UploadFile
import requests
import jwt
from OpenSSL import crypto
# pip install python-keycloak
from minio import Minio
# pip install minio
from typing import Optional, List
from pydantic import BaseModel
from fastapi.responses import FileResponse
# custom db heroes
from db import crud, models
from db.database import SessionLocal, engine
from dependencies.dependencies import token_validity
import datetime
from heroes_conf import settings
import re

models.Base.metadata.create_all(bind=engine)


class Organization(BaseModel):
    name: str


class MinioBucket(BaseModel):
    bucket_name: str
    creation_date: datetime.datetime


class MinioObject(BaseModel):
    bucket_name: str
    content_type: Optional[str] = None
    etag: Optional[str] = None
    is_delete_marker: bool
    is_dir: bool
    is_latest: Optional[str] = None
    last_modified: Optional[datetime.datetime] = None
    metadata: Optional[dict] = None
    object_name: str
    owner_id: Optional[str] = None
    owner_name: Optional[str] = None
    size: Optional[int] = None
    storage_class: Optional[str] = None
    version_id: Optional[str] = None


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(
    prefix="/organization/data",
    tags=["Data Management"],
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


# Data Management
async def get_minio_server(organization_name: str):
    """HEROES Get Minio Server function

    !! DEPRECATED !!

    Retrieve the minio server associated to the organization_name parameter
    in the sql database. Return all information associated to this server.
    """

    try:
        # Check existence of the organization
        db_organization = crud.get_organization_by_name(
            next(get_db()),
            organization_name=organization_name
        )
        for organization_servers in db_organization.servers:
            if organization_servers.name == "minio":
                minio_server = organization_servers
        # Build minio server url with its db parameters: ip and server_port
        minio_url = minio_server.ip + ":" + str(minio_server.server_port)
        return minio_url
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


async def minio_credentials(
    username: str,
    userid: str,
    token: str = Depends(token_validity),
):
    """HEROES Get minio credentials function

    This function uses the id_token integrated in the token to
    return minio STS credentials to the authenticated user.
    """
    try:
        # Retrieve the minio server connexion information from its
        # organization.
        # minio_url = f"minio-server-{token['organization']}" \
        #             + f"{settings.NAMESPACE}:9000"
        # minio_sts_client = boto3.client(
        #     'sts',
        #     use_ssl=False,
        #     endpoint_url=f'http://{minio_url}'
        # )
        # # Get user credentials with web identity using the user id_token
        # user_credentials = minio_sts_client.assume_role_with_web_identity(
        #     RoleArn=f'arn:heroes:iam::12345789:{username}/minio-sts-api',
        #     RoleSessionName=f'{username}Session',
        #     WebIdentityToken=token['id_token'],
        #     DurationSeconds=3600
        # )
        # return user_credentials
        r = requests.post(
            f"http://minio-server-{token['organization']}{settings.NAMESPACE}:9000",
            params = {
                "Action": "AssumeRoleWithWebIdentity",
                "Version": "2011-06-15",
                "WebIdentityToken": token['id_token']
            }
        )
        text = r.text.replace("\n", "")
        secret_access_key = re.match(".*<SecretAccessKey>(.*)</SecretAccessKey>.*", text).group(1)
        access_key_id = re.match(".*<AccessKeyId>(.*)</AccessKeyId>.*", text).group(1)
        session_token = re.match(".*<SessionToken>(.*)</SessionToken>.*", text).group(1)

        return {
            'Credentials': {
                'AccessKeyId': access_key_id,
                'SecretAccessKey': secret_access_key,
                'SessionToken':  session_token
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/list",
            response_model=List[MinioBucket],
            tags=["Data Management"],
            summary="List all buckets available for the authenticated user")
async def minio_bucket_list(
    token: str = Depends(token_validity)
):
    """HEROES List user accessible buckets function.

    This function allows the authenticated user to list their buckets.
    """
    try:
        # Step1: Decode the user token with the organization public key
        decoded_token = await decode_token(token)
        # Step2: Get minio sts credentials with the user token
        userCredentials = await minio_credentials(
            decoded_token["preferred_username"],
            decoded_token['sub'],
            token
        )
        # Step3: Bind the minioClient mandatory parameters
        # from minio_credentials.
        UserAccessKeyId = userCredentials['Credentials']['AccessKeyId']
        UserSecretAccessKey = userCredentials['Credentials']['SecretAccessKey']
        UserSessionToken = userCredentials['Credentials']['SessionToken']
        minio_url = f"minio-server-{token['organization']}" \
                    + f"{settings.NAMESPACE}:9000"
        # Step4: Create minioClient with the minio user sts credentials
        minioClient = Minio(
            f"{minio_url}",
            secure=False,
            access_key=UserAccessKeyId,
            secret_key=UserSecretAccessKey,
            session_token=UserSessionToken
        )
        buckets = minioClient.list_buckets()
        user_buckets = []
        for bucket in buckets:
            user_buckets.append(MinioBucket(
                bucket_name=bucket.name,
                creation_date=bucket.creation_date)
            )
        return user_buckets
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/size",
            tags=["Data Management"],
            summary="Return the size of the selected bucket for the authenticated user")
async def minio_bucket_size(
    bucket: str,
    bucket_prefix: Optional[str] = None,
    token: str = Depends(token_validity)
):
    """HEROES Size of buckets function.

    This function allows the authenticated user to get the size of the selected
    bucket and optional subfolder.
    """
    try:
        object_list_response = await minio_list_objects_in_bucket(
            bucket=bucket,
            bucket_recursive=True,
            bucket_prefix=bucket_prefix,
            token=token
        )
        object_list_size = 0
        for bucket_object in object_list_response:
            if bucket_object.size != "null":
                object_list_size = object_list_size + bucket_object.size
        return object_list_size

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/bucket",
             response_model=MinioBucket,
             tags=["Data Management"],
             summary="Create a new bucket in organization minio server")
async def minio_bucket_create(
    bucket_name: str,
    token: str = Depends(token_validity)
):
    """HEROES Create minio bucket function

    This function allows the authenticated and authorized users to
    create new buckets.
    """
    try:
        # Step1: Decode the user token with the organization public key
        decoded_token = await decode_token(token)
        # Step2: Get minio sts credentials with the user token
        userCredentials = await minio_credentials(
            decoded_token["preferred_username"],
            decoded_token['sub'],
            token
        )
        # Step3: Bind the minioClient mandatory parameters
        # from minio_credentials.
        UserAccessKeyId = userCredentials['Credentials']['AccessKeyId']
        UserSecretAccessKey = userCredentials['Credentials']['SecretAccessKey']
        UserSessionToken = userCredentials['Credentials']['SessionToken']

        minio_url = f"minio-server-{token['organization']}" \
                    + f"{settings.NAMESPACE}:9000"
        # Step4: Create minioClient with the minio user sts credentials
        minioClient = Minio(
            f"{minio_url}",
            secure=False,
            access_key=UserAccessKeyId,
            secret_key=UserSecretAccessKey,
            session_token=UserSessionToken
        )
        bucket = minioClient.make_bucket(bucket_name)
        return bucket
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/bucket/{bucket}/",
             tags=["Data Management"],
             summary="Create a new subfolder in the specified bucket")
async def minio_subfolder_bucket_create(
    bucket: str,
    subfolder_path: str,
    token: str = Depends(token_validity)
):
    """HEROES Create minio subfolder bucket function

    This function allows the authenticated and authorized users to
    create new subfolder buckets.
    """
    try:
        # Step1: Decode the user token with the organization public key
        decoded_token = await decode_token(token)
        # Step2: Get minio sts credentials with the user token
        userCredentials = await minio_credentials(
            decoded_token["preferred_username"],
            decoded_token['sub'],
            token
        )
        if subfolder_path[-1] != '/':
            subfolder_path = subfolder_path + '/'
        # Step3: Bind the minioClient mandatory parameters
        # from minio_credentials.
        UserAccessKeyId = userCredentials['Credentials']['AccessKeyId']
        UserSecretAccessKey = userCredentials['Credentials']['SecretAccessKey']
        UserSessionToken = userCredentials['Credentials']['SessionToken']

        minio_url = f"minio-server-{token['organization']}" \
                    + f"{settings.NAMESPACE}:9000"
        # Step4: Create minioClient with the minio user sts credentials
        minioClient = Minio(
            f"{minio_url}",
            secure=False,
            access_key=UserAccessKeyId,
            secret_key=UserSecretAccessKey,
            session_token=UserSessionToken
        )
        subfolder_bucket = minioClient.put_object(bucket, subfolder_path, io.BytesIO(b""), 0)
        return subfolder_bucket
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.delete("/bucket",
               response_model=MinioBucket,
               tags=["Data Management"],
               summary="Delete bucket from organization minio server")
async def minio_bucket_delete(
    bucket_name: str,
    token: str = Depends(token_validity)
):
    """HEROES Delete minio bucket function

    This function allows the authenticated and authorized users to
    delete buckets.
    """
    try:
        # Step1: Decode the user token with the organization public key
        decoded_token = await decode_token(token)
        # Step2: Get minio sts credentials with the user token
        userCredentials = await minio_credentials(
            decoded_token["preferred_username"],
            decoded_token['sub'],
            token
        )
        # Step3: Bind the minioClient mandatory parameters
        # from minio_credentials.
        UserAccessKeyId = userCredentials['Credentials']['AccessKeyId']
        UserSecretAccessKey = userCredentials['Credentials']['SecretAccessKey']
        UserSessionToken = userCredentials['Credentials']['SessionToken']

        minio_url = f"minio-server-{token['organization']}" \
                    + f"{settings.NAMESPACE}:9000"
        # Step4: Create minioClient with the minio user sts credentials
        minioClient = Minio(
            f"{minio_url}",
            secure=False,
            access_key=UserAccessKeyId,
            secret_key=UserSecretAccessKey,
            session_token=UserSessionToken
        )
        bucket = minioClient.remove_bucket(bucket_name)
        return {'status_code': '200', 'message': f'Bucket {bucket_name} deleted'}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/bucket/{bucket}/list",
            response_model=List[MinioObject],
            tags=["Data Management"],
            summary="List all objects presents in the target bucket of the \
            authenticated user")
async def minio_list_objects_in_bucket(
    bucket: str,
    bucket_recursive: Optional[bool] = None,
    bucket_prefix: Optional[str] = None,
    token: str = Depends(token_validity)
):
    """HEROES List objets from a user bucket.

    This function allows the authenticated users to
    list the objects in their accessible buckets.
    """
    try:
        decoded_token = await decode_token(token)
        userCredentials = await minio_credentials(
            decoded_token["preferred_username"],
            decoded_token['sub'],
            token
        )

        UserAccessKeyId = userCredentials['Credentials']['AccessKeyId']
        UserSecretAccessKey = userCredentials['Credentials']['SecretAccessKey']
        UserSessionToken = userCredentials['Credentials']['SessionToken']
        minio_url = f"minio-server-{token['organization']}" \
                    + f"{settings.NAMESPACE}:9000"
        minioClient = Minio(
            f"{minio_url}",
            secure=False,
            access_key=UserAccessKeyId,
            secret_key=UserSecretAccessKey,
            session_token=UserSessionToken
        )
        bucket_exist = minioClient.bucket_exists(bucket)
        if bucket_exist:
            if bucket_prefix != None:
                objects = minioClient.list_objects(
                    bucket_name=bucket,
                    recursive=bucket_recursive,
                    prefix=bucket_prefix)
            else:
                objects = minioClient.list_objects(
                    bucket_name=bucket,
                    recursive=bucket_recursive)
            user_objects = []
            for object in objects:
                user_objects.append(
                    MinioObject(
                        bucket_name=object.bucket_name,
                        content_type=object.content_type,
                        etag=object.etag,
                        is_delete_marker=object.is_delete_marker,
                        is_dir=object.is_dir,
                        is_latest=object.is_latest,
                        last_modified=object.last_modified,
                        metadata=object.metadata,
                        object_name=object.object_name,
                        owner_id=object.owner_id,
                        owner_name=object.owner_name,
                        size=object.size,
                        storage_class=object.storage_class,
                        version_id=object.version_id
                    )
                )
            return user_objects
        else:
            return "This bucket does not exist"
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.delete("/bucket/{bucket}",
               tags=["Data Management"],
               summary="Delete object from user bucket")
async def minio_object_delete(
    bucket: str,
    object_path: str,
    token: str = Depends(token_validity)
):
    """HEROES Delete minio object(s) function

    This function allows the authenticated and authorized users to
    delete objects in the specified bucket.
    """
    try:
        # Step1: Decode the user token with the organization public key
        decoded_token = await decode_token(token)
        # Step2: Get minio sts credentials with the user token
        userCredentials = await minio_credentials(
            decoded_token["preferred_username"],
            decoded_token['sub'],
            token
        )
        # Step3: Bind the minioClient mandatory parameters
        # from minio_credentials.
        UserAccessKeyId = userCredentials['Credentials']['AccessKeyId']
        UserSecretAccessKey = userCredentials['Credentials']['SecretAccessKey']
        UserSessionToken = userCredentials['Credentials']['SessionToken']

        minio_url = f"minio-server-{token['organization']}" \
                    + f"{settings.NAMESPACE}:9000"
        # Step4: Create minioClient with the minio user sts credentials
        minioClient = Minio(
            f"{minio_url}",
            secure=False,
            access_key=UserAccessKeyId,
            secret_key=UserSecretAccessKey,
            session_token=UserSessionToken
        )
        if object_path[-1] == '/':
            object_list = map(
                lambda x: x.object_name,
                minioClient.list_objects(bucket, object_path, recursive=True)
            )
            print(object_list)
            for current_object in object_list:
                remove_object = minioClient.remove_object(bucket, current_object)
            remove_object = minioClient.remove_object(bucket, object_path)
        else:
            remove_object = minioClient.remove_object(bucket, object_path)
        print(remove_object)
        return {'status_code': '200', 'message': f'Object {object_path} deleted from {bucket}'}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.get("/download",
            tags=["Data Management"],
            summary="Download file from bucket")
async def minio_bucket_download(
    bucket: str,
    file: str,
    token: str = Depends(token_validity)
):
    """HEROES Download object from bucket function.

    This function allows the authenticated users to
    download object from accessible minio bucket.
    """
    try:
        decoded_token = await decode_token(token)
        userCredentials = await minio_credentials(
            decoded_token["preferred_username"],
            decoded_token['sub'],
            token
        )
        UserAccessKeyId = userCredentials['Credentials']['AccessKeyId']
        UserSecretAccessKey = userCredentials['Credentials']['SecretAccessKey']
        UserSessionToken = userCredentials['Credentials']['SessionToken']
        minio_url = f"minio-server-{token['organization']}" \
                    + f"{settings.NAMESPACE}:9000"
        minioClient = Minio(
            f"{minio_url}",
            secure=False,
            access_key=UserAccessKeyId,
            secret_key=UserSecretAccessKey,
            session_token=UserSessionToken
        )
        print("Download file")
        minioClient.fget_object(bucket, file, file.split('/')[-1])
        print(f"file : {file.split('/')[-1]}")
        # with open(file.split('/')[-1], 'r') as file_downloaded:
        #     print(file_downloaded.read())
        return FileResponse(path=file.split('/')[-1],
                            filename=file.split('/')[-1],
                            media_type='application/octet-stream')
    except Exception as e:
        raise e


@router.post("/upload",
             tags=["Data Management"],
             summary="Upload file to bucket")
async def minio_bucket_upload(
    bucket: str,
    bucket_prefix: Optional[str] = None,
    file: UploadFile = File(...),
    token: str = Depends(token_validity)
):
    """HEROES Upload object from bucket function.

    This function allows the authenticated users to
    upload object from accessible minio bucket.
    """
    try:
        decoded_token = await decode_token(token)
        userCredentials = await minio_credentials(
            decoded_token["preferred_username"],
            decoded_token['sub'],
            token
        )
        UserAccessKeyId = userCredentials['Credentials']['AccessKeyId']
        UserSecretAccessKey = userCredentials['Credentials']['SecretAccessKey']
        UserSessionToken = userCredentials['Credentials']['SessionToken']
        minio_url = f"minio-server-{token['organization']}" \
                    + f"{settings.NAMESPACE}:9000"
        minioClient = Minio(
            f"{minio_url}",
            secure=False,
            access_key=UserAccessKeyId,
            secret_key=UserSecretAccessKey,
            session_token=UserSessionToken
        )
        if bucket_prefix != None:
            file_path = bucket_prefix + "/" + file.filename
        else:
            file_path = file.filename
        upload_response = minioClient.fput_object(
            bucket,
            file_path,
            file.file.fileno()
        )
        return upload_response
    except Exception as e:
        raise e




# @router.get("/bucket/credentials",
#                tags=["Data Management"],
#                summary="Get data credentials for dev only")
async def minio_get_credentials(
    token: str = Depends(token_validity)
):
    """HEROES Credentials dev function
    Give simple credentials for MinIO
    """
    try:
        # Step1: Decode the user token with the organization public key
        decoded_token = await decode_token(token)
        # Step2: Get minio sts credentials with the user token
        userCredentials = await minio_credentials(
            decoded_token["preferred_username"],
            decoded_token['sub'],
            token
        )
        # Step3: Bind the minioClient mandatory parameters
        # from minio_credentials.
        # userCredentials['Credentials']['AccessKeyId']
        # userCredentials['Credentials']['SecretAccessKey']
        # userCredentials['Credentials']['SessionToken']
        return userCredentials
    except Exception as e:
        raise e
