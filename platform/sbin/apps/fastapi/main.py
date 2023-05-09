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
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# from dependencies.dependencies import token_validity
from internal.organization import users as organization_users
from internal.organization import groups as organization_groups
from internal.organization import roles as organization_roles
from internal.organization import clusters as organization_clusters
from internal.organization import workflows as organization_workflows
from internal.heroes import organizations as heroes_admin_organizations
from internal.heroes import clients as heroes_admin_clients
from internal.heroes import servers as heroes_admin_servers
from routers import auth, data, decision, workflow

from db import models
from db.database import engine

models.Base.metadata.create_all(bind=engine)
# app = FastAPI(dependencies=[Depends(get_query_token)])
# FastAPI
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]
app = FastAPI(
    middleware=middleware,
    title="[Prototype] HEROES",
    description="""

The HEROES platform allows end-users to submit their complex Simulation
and ML workflows to both HPC Data Centres and Cloud Infrastructures.

The APIs presented below can be used by the following types of users to interact with the platform:

* HEROES Organization users
* HEROES Organization administrators
* HEROES global administrators

                """,
    version="1.0.0",
    contact={
        "name": "HEROES",
        "url": "https://heroes-project.eu/"
    },
    openapi_tags=[
        {
            "name": "Identity Management",
            "description": "Authentication and authorization APIs"
        },
        {
            "name": "Data Management",
            "description": "Data Management APIs"
        },
        {
            "name": "Workflow Management",
            "description": "Workflow Management APIs"
        },
        {
            "name": "Organization Admin",
            "description": "APIs for the administrators of an Organization"
        },
        {
            "name": "HEROES Admin",
            "description": "APIs for the global HEROES Platform Administrators"
        },
        {
            "name": "Decision Module",
            "description": "Workflow placement APIs"
        }
    ]
)

@app.on_event("startup")
@repeat_every(seconds=60)
def hook_workflow_monitoring():
    # call monitoring
    workflow.workflow_monitoring()

app.include_router(auth.router)
app.include_router(data.router)
app.include_router(decision.router)
app.include_router(workflow.router)
app.include_router(organization_users.router)
app.include_router(organization_groups.router)
app.include_router(organization_roles.router)
app.include_router(organization_clusters.router)
app.include_router(organization_workflows.router)
app.include_router(heroes_admin_organizations.router)
app.include_router(heroes_admin_clients.router)
app.include_router(heroes_admin_servers.router)
