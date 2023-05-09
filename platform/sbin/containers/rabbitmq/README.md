# RabbitMQ container deployment

## Package the RabbitMQ sources
```bash
FASTAPI_VERSION="0.3"
cd platform/sbin/deployment/apps/rabbitmq
tar zcvf ../../containers/rabbitmq/src/heroes-rabbitmq-${FASTAPI_VERSION}.tar.gz .
```

## Build the RabbitMQ container
```bash
docker build -t rabbitmq-server heroes/sbin/deployment/containers/rabbitmq/
```

## Run the RabbitMQ container
```bash
FASTAPI_SERVER_PORT=80
docker run -t -d \
       "rabbitmq-server" \
       --name "rabbitmq-server" \
       -p "0.0.0.0:${FASTAPI_SERVER_PORT}:${FASTAPI_SERVER_PORT}/tcp"
```

## Stop the RabbitMQ container
```bash
docker stop $container_name
```

## Remove the RabbitMQ container
```bash
docker rm $container_name
```
