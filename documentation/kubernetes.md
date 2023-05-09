# Installation

## Download kubernetes binary
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

## Download kubernetes checksum
curl -LO "https://dl.k8s.io/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"

## Validate the kubectl binary against the checksum file
echo "$(<kubectl.sha256) kubectl" | sha256sum --check

## Install kubernetes
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
PATH=$PATH:/usr/local/bin

## Check install
kubectl version --client


# MinIo config

## Create namescape
kubectl create namespace minio-tenant-1

kubectl create namespace minio-ucit


## Install krew
(
  set -x; cd "$(mktemp -d)" &&
  OS="$(uname | tr '[:upper:]' '[:lower:]')" &&
  ARCH="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/\(arm\)\(64\)\?.*/\1\2/' -e 's/aarch64$/arm64/')" &&
  KREW="krew-${OS}_${ARCH}" &&
  curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/${KREW}.tar.gz" &&
  tar zxvf "${KREW}.tar.gz" &&
  ./"${KREW}" install krew
)

export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"

## Install minikube
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 \
  && chmod +x minikube

## Create a MinIO tenant

### Create a namespace
kubectl create namespace minio-${tenant}

### ?

apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
    name: direct-csi-min-io
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer

???

### ??

kubectl krew install minio

kubectl minio init

kubectl get pods -n minio-operator

#### Doc:
* https://docs.min.io/minio/k8s/deployment/deploy-minio-operator.html


kubectl apply -f ./my-manifest.yaml
kubectl create deployment minio --image=minio


kubectl apply -f quay.io/minio/minio

```bash
docker build -t minio-server .
```

```bash
docker run -t -d --privileged=true --name minio-server -p 0.0.0.0:9001:9001/tcp minio-server
```

```bash
sudo docker exec -it $container_name bash
```

```bash
docker run -t -d --privileged=true \
       --name "minio-${ORGANIZATION_NAME}" \
       -p "0.0.0.0:${MINIO_SERVER_CONSOLE_PORT}:${MINIO_SERVER_CONSOLE_PORT}/tcp" \
       #--mount source=selected_volume,target=/data \
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

```bash
kubectl -n $NAMESPACE describe pod $APP
```

minikube start --namespace minio --insecure-registry='$LOCAL_IP:5000:5000'

kubectl create namespace minio

kubectl run minio-ucit -n $NAMESPACE --image=$LOCAL_IP:5000/minio-server:latest --insecure-skip-tls-verify=true --port=9000 --port=9001

 3.249.17.4 8080 UCit account de46ee5a-7402-472e-9f1d-89a1651f10e9 3.249.17.4 9000 9001

kubectl expose pod minio-ucit --port 9000,9001 --type=NodePort
