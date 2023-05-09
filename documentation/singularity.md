# Docker & Docker-compose

## Dependencies

Install docker and docker-compose with pip3:
```bash
pip3 install docker
pip3 install docker-compose
```

```bash
yum install git -y
```

Start docker:
```bash
sudo systemctl start docker
```

Create syumbolic link for root:
```bash
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
```

## Build sregister and

Dockerfile:
```bash
FROM continuumio/miniconda3
#########################################
# Singularity Registry Global Client
#
# docker build -t quay.io/vanessa/sregistry-cli .
# docker run quay.io/vanessa/sregistry-cli
#########################################
LABEL maintainer vsochat@stanford.edu
RUN apt-get update && apt-get install -y git build-essential \
                   libtool \
                   squashfs-tools \
                   libarchive-dev \
                   autotools-dev \
                   automake \
                   autoconf \
                   uuid-dev \
                   libssl-dev
RUN /opt/conda/bin/pip install dateutils
# Install Singularity
WORKDIR /opt
RUN git clone -b vault/release-2.6 https://www.github.com/sylabs/singularity.git
WORKDIR singularity
RUN ./autogen.sh && ./configure --prefix=/usr/local && make && make install
RUN mkdir /code
ADD . /code
RUN /opt/conda/bin/pip install setuptools
RUN /opt/conda/bin/pip install scif
RUN scif install /code/sregistry-cli.scif
ENTRYPOINT ["sregistry"]
WORKDIR /code
RUN test -f /usr/bin/python || ln -s /opt/conda/bin/python /usr/bin/python
RUN /opt/conda/bin/pip install -e .[all]
```

```bash
git clone https://github.com/singularityhub/sregistry-cli
cd sregistry-cli
sudo docker build -t quay.io/vanessa/sregistry-cli .
```

## Store singularity container on minio or aws s3
Create a docker-compose template in yaml.

docker-compose.yml:
```yaml
version: '2'
services:
    minio:
      image: minio/minio
      container_name: minio
      ports:
        - "9000:9000"
      environment:
        MINIO_ACCESS_KEY: minio
        MINIO_SECRET_KEY: minio123
      command: server /data
      links:
        - sregistrycli
    sregistrycli:
      image: quay.io/vanessa/sregistry-cli
      container_name: sregistrycli
      volumes:
        - type: bind
          source: /home/ec2-user/demo/containers
          target: /home/ec2-user/heroes
      privileged: true
      command: -F /dev/null
      entrypoint: tail
      environment:
        SREGISTRY_CLIENT: s3
        SREGISTRY_S3_BUCKET: ${S3_BUCKET_NAME}
        AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
        AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
```

## Configuration of Docker-compose file for minio or AWS s3
For minIO S3:
```yaml
 environment:                         
        SREGISTRY_S3_BASE: http://minio:9000
        SREGISTRY_S3_BUCKET: ${SREGISTRY_S3_BUCKET}
        MINIO_ACCESS_KEY: minio
        MINIO_SECRET_KEY: minio123
```

For AWS S3:
```yaml
 environment:                         
        SREGISTRY_CLIENT: s3
        SREGISTRY_S3_BUCKET: ${SREGISTRY_S3_BUCKET}
        AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
        AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
```

## Launch containers
```bash
docker-compose up -d
```

### Shell navigation in containers
```bash
sudo docker exec -it $container_name bash
```

Example:
```bash
sudo docker exec -it sregistrycli bash
```

### Push a container with sregistry
In the sregister container:
sregistry push --name path/of/s3/image:tag /local/path/of/image

Example:
```bash
sregistry push --name images/centos7:jq /home/ec2-user/heroes/container.sif
```
### List available containers in registry
```bash
sregistry search
```
### Pull images with sregistry
```bash
sregistry pull images/centos7:jq
```

# Singularity Installation

## Install Go

Get GO sources:
```bash
export VERSION=1.16 OS=linux ARCH=amd64 && \
    wget https://dl.google.com/go/go$VERSION.$OS-$ARCH.tar.gz && \
    sudo tar -C /usr/local -xzvf go$VERSION.$OS-$ARCH.tar.gz && \
    rm go$VERSION.$OS-$ARCH.tar.gz
```

```bash
echo 'export GOPATH=${HOME}/go' >> ~/.bashrc && \
    echo 'export PATH=/usr/local/go/bin:${PATH}:${GOPATH}/bin' >> ~/.bashrc && \
    source ~/.bashrc
```
## Install Singularity

Singularity 2.6 is available from most of Linux repositories.
The latest (3.8) version is only available for compilation.

### Install dependencies

Install GO deps for Singularity:
```bash
go get -u github.com/golang/dep/cmd/dep
```

Install cryptsetup for singularity signatures:
```bash
yum/apt install cryptsetup-bin
```

### Compile Singularity

Get singularity sources:
```bash
export VERSION=3.8.0 && # adjust this as necessary \
    mkdir -p $GOPATH/src/github.com/sylabs && \
    cd $GOPATH/src/github.com/sylabs && \
    wget https://github.com/sylabs/singularity/releases/download/v${VERSION}/singularity-ce-${VERSION}.tar.gz && \
    tar -xzf singularity-ce-${VERSION}.tar.gz && \
    cd ./singularity-ce-${VERSION} && \
    ./mconfig
```

Mconfig, make and install Singularity:
```bash
./mconfig && \
    make -C ./builddir && \
    sudo make -C ./builddir install
```

Add singularity bash completion:
```bash
. /usr/local/etc/bash_completion.d/singularity
```

# Singularity usage

## Container definition file

A singularity's container can be defined by a file as following.
centos7_container.def:
```bash
Bootstrap: docker
From: centos:7

%setup
    echo ""

%files

%environment

%post
    yum update -y && yum install epel-release -y
    yum install jq -y
    NOW=`date`
    echo "export NOW=\"${NOW}\"" >> $SINGULARITY_ENVIRONMENT

%runscript
    echo "Container was created $NOW"
    echo "Arguments received: $*"
    exec echo "$@"

%startscript

%test
    cat /etc/os-release
    grep ID=\"centos\" /etc/os-release
    if [[ $? -eq 0 ]]; then
      echo "Container is a correct Centos"
    else
      echo "Container is not a Centos"
    fi

%labels
    Author jRemy
    Version v1.0.0

%help
    This is a PoC container of HEROES.
```

## Build container

```bash
sudo singularity build centos7.sif centos7_container.def
```

Returns:
```bash
Build target 'centos7.sif' already exists and will be deleted during the build process. Do you want to continue? [N/y] y
INFO:    Starting build...
Getting image source signatures
Copying blob 2d473b07cdd5 [--------------------------------------] 0.0b / 0.0b
Copying config adf3bb6cc8 done  
Writing manifest to image destination
Storing signatures
[ Installations... ]
Complete!
++ date
+ NOW='Thu Jun  3 09:29:28 UTC 2021'
+ echo 'export NOW="Thu Jun  3 09:29:28 UTC 2021"'
INFO:    Adding help info
INFO:    Adding labels
INFO:    Adding environment to container
INFO:    Adding startscript
INFO:    Adding runscript
INFO:    Adding testscript
INFO:    Running testscript
NAME="CentOS Linux"
VERSION="7 (Core)"
ID="centos"
ID_LIKE="rhel fedora"
VERSION_ID="7"
PRETTY_NAME="CentOS Linux 7 (Core)"
ANSI_COLOR="0;31"
CPE_NAME="cpe:/o:centos:centos:7"
HOME_URL="https://www.centos.org/"
BUG_REPORT_URL="https://bugs.centos.org/"

CENTOS_MANTISBT_PROJECT="CentOS-7"
CENTOS_MANTISBT_PROJECT_VERSION="7"
REDHAT_SUPPORT_PRODUCT="centos"
REDHAT_SUPPORT_PRODUCT_VERSION="7"

ID="centos"
Container is a correct Centos
INFO:    Creating SIF file...
INFO:    Build complete: centos7.sif
```

## Container execution

data/file.json:
```json
  {
      "Parameters": {
          "Key1": "VK1",
          "Key2": "VK2"
      },
     "Pkgs": {
         "PkgName1": "VN1",
         "PkgName2": "VN2"
     }
  }
```

```bash
singularity exec --home /home/$(whoami)/organisation/user1 --bind data/:/home/$(whoami)/heroes:ro centos7.sif jq .Parameters.Key1 /home/$(whoami)/heroes/file.json
```

With:
- --home $user_home
- --bind
  - src/ as host directory
  - :/home/$(whoami)/heroes as container directory
  - :ro as read only (rw is also available)
