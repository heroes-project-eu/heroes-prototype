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
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from heroes_conf import settings

if settings.SQLITE == True:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./heroes.sqlite"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL
    )
else:

    SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DB_USER}" \
        + f":{settings.DB_PASSWORD}" \
        + f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

    # for database
    # SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://fastapi:fastapidevpswd@localhost:5432/heroes_db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, pool_size=32, max_overflow=64
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
