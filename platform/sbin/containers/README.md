# Container within ArgoCD

## Prerequisites:
* Access to the DoIt VPN
* Account on DoIt VPN
  * Including git SSH key

## Build containers

### Every containers
You can build and push the platform containers to the gitlab using
the push_containers script.

```bash
push_containers.sh
```

### Single container
If you only want to build/push/update a container, you can use the build
script available in each container directory.
```bash
${container_name}/build.sh
```

## ArgoCD deployment




# Containers within Docker

## Vars

```bash
image_name="string"
container_name="string"
container_port="port"  # Port of the container to expose
host_port="host_port"  # Port of the docker host
ipv4="xxx.xxx.xxx.xxx"

```

## Commands

### Build container
```bash
docker build -t "${image_name}" .
```

### Run container
```bash
docker run -t -d
  --privileged=true \
  --name minio-server \
  -p "${ipv4}:${container_port}:${host_port}/tcp" \
  "${image_name}"  # "${container_arg}"
```

### Interact with container
```bash
sudo docker exec -it "${container_name}" bash
```


# Containers within Kubernetes

## Vars
```bash
image_name="string"
container_name="string"
container_port="port"  # Port of the container to expose
host_port="host_port"  # Port of the docker host
ipv4="xxx.xxx.xxx.xxx"
# Container registry to find container images
container_registry_ip="xxx.xxx.xxx.xxx"
container_registry_port="port"
```

## Commands

### Run container
```bash
kubectl run "${container_name}" \
  -n "${namespace}" \
  --image="${container_registry_ip}:${container_registry_port}/${image_name}:latest" \
  --insecure-skip-tls-verify=true \
  --privileged=true \
  --port "${container_port}" \  # Optional: Allow multiple port: port1,port2..
  "${container_arg}"  # Optional: Allow 1 arg per line
```

### Expose container
```bash
kubectl expose pod "${container_name}" \
  --port "${container_port}" \  # Allow multiple port: port1,port2..
  --type=NodePort
```
