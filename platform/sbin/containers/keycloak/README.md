# Keycloak container deployment

## Build the keycloak container
```bash
docker build -t keycloak-server heroes/sbin/deployment/containers/keycloak/
```

## Run the keycloak container
```bash
KEYCLOAK_SERVER_PORT=8080
docker run -t -d \
       "keycloak-server" \
       --name "keycloak-server" \
       -p "0.0.0.0:${KEYCLOAK_SERVER_PORT}:${KEYCLOAK_SERVER_PORT}/tcp"
```

## Stop the keycloak container
```bash
docker stop $container_name
```

## Remove the keycloak container
```bash
docker rm $container_name
```
