# PostgreSQL container deployment

## Build the postgresql container
```bash
docker build -t postgresql-server heroes/sbin/deployment/containers/postgresql/
```

## Run the postgresql container
```bash
POSTGRESQL_SERVER_PORT=5432
docker run -t -d \
       "postgresql-server" \
       --name "postgresql-server" \
       -p "0.0.0.0:${POSTGRESQL_SERVER_PORT}:${POSTGRESQL_SERVER_PORT}/tcp"
```

## Stop the postgresql container
```bash
docker stop $container_name
```

## Remove the postgresql container
```bash
docker rm $container_name
```
