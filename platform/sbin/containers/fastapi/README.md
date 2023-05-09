# Fastapi container deployment

## Package the FastAPI sources
```bash
FASTAPI_VERSION="0.3"
cd platform/sbin/deployment/apps/fastapi
tar zcvf ../../containers/fastapi/src/heroes-fastapi-${FASTAPI_VERSION}.tar.gz .
```

## Build the fastapi container
```bash
docker build -t fastapi-server heroes/sbin/deployment/containers/fastapi/
```

## Run the fastapi container
```bash
FASTAPI_SERVER_PORT=80
docker run -t -d \
       "fastapi-server" \
       --name "fastapi-server" \
       -p "0.0.0.0:${FASTAPI_SERVER_PORT}:${FASTAPI_SERVER_PORT}/tcp"
```

## Stop the fastapi container
```bash
docker stop $container_name
```

## Remove the fastapi container
```bash
docker rm $container_name
```
