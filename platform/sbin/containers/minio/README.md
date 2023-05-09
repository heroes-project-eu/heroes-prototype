# MinIo container deployment

## Build the minio container
```bash
docker build -t gitlab.doit.priv:5050/heroes/k8s-apps/minio-server:latest heroes/sbin/deployment/containers/minio/
```

## Vars
```bash
ORGANIZATION_NAME="ucit"
MINIO_SERVER_PORT="9000"
MINIO_SERVER_CONSOLE_PORT="9001"
MINIO_IMAGE="gitlab.doit.priv:5050/heroes/k8s-apps/minio-server:latest"
KEYCLOAK_URL="keycloak-server"
KEYCLOAK_PORT="8080"
ORGANIZATION_CLIENT_ID="account"
ORGANIZATION_CLIENT_SECRET="secret"
MINIO_SERVER_URL="localip"

```


## Run the minio container
```bash
docker run -t -d \
       --name "minio-${ORGANIZATION_NAME}" \
       -p "0.0.0.0:${MINIO_SERVER_PORT}:${MINIO_SERVER_PORT}/tcp" \
       -p "0.0.0.0:${MINIO_SERVER_CONSOLE_PORT}:${MINIO_SERVER_CONSOLE_PORT}/tcp" \
       "${MINIO_IMAGE}" \
       "${KEYCLOAK_URL}" \
       "${KEYCLOAK_PORT}" \
       "${ORGANIZATION_NAME}" \
       "${ORGANIZATION_CLIENT_ID}" \
       "${ORGANIZATION_CLIENT_SECRET}" \
       "${MINIO_SERVER_URL}" \
       "${MINIO_SERVER_PORT}" \
       "${MINIO_SERVER_CONSOLE_PORT}"
```

## Stop the minio container
```bash
docker stop $container_name
```

## Remove the minio container
```bash
docker rm $container_name
```
