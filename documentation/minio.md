# MinIO Server Installation

```bash
sudo su
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
mv minio /usr/local/bin
useradd -r minio -s /sbin/nologin
chown minio:minio /usr/local/bin/minio
mkdir /usr/local/share/minio
chown minio:minio /usr/local/share/minio
mkdir /etc/minio
chown minio:minio /etc/minio

cat > /etc/default/minio <<EOF
MINIO_ACCESS_KEY="minio"
MINIO_VOLUMES="/usr/local/share/minio/"
MINIO_OPTS="-C /etc/minio --address 0.0.0.0:9000 --console-address 0.0.0.0:9001"
MINIO_SECRET_KEY="miniostorage"
EOF

cat > /etc/systemd/system/minio.service <<EOF
[Unit]
Description=MinIO
Wants=network-online.target
After=network-online.target
AssertFileIsExecutable=/usr/local/bin/minio

[Service]
WorkingDirectory=/usr/local/
User=minio
Group=minio
ProtectProc=invisible
EnvironmentFile=/etc/default/minio
ExecStartPre=/bin/bash -c "if [ -z \"${MINIO_VOLUMES}\" ]; then echo \"Variable MINIO_VOLUMES not set in /etc/default/minio\"; exit 1; fi"
ExecStart=/usr/local/bin/minio server $MINIO_OPTS $MINIO_VOLUMES
# Let systemd restart this service always
Restart=always
# Specifies the maximum file descriptor number that can be opened by this process
LimitNOFILE=65536
# Specifies the maximum number of threads this process can create
TasksMax=infinity
# Disable timeout logic and wait until process is stopped
TimeoutStopSec=infinity
SendSIGKILL=no

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable minio
systemctl start minio
systemctl status minio
```

## MinIO Client Installation

wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
mv mc /usr/bin/

# Configure MinIO with OpenID:

Var:
minioAdminID
minioAdminPassword
minioServerName
keycloakClientId
keycloakClientSecret
IPv4
organization

>
minioAdminID='minio'
minioAdminPassword='xxxxxx'
minioServerName='xxxxxxx'
IPv4='xxx.xxx.xxx.xxx'
organization='UCit'
keycloakClientId='account'
keycloakClientSecret='xxxx'
scopes='openid+profile+roles+address+offline_access+web-origins+phone+email+microprofile-jwt+tpm+openid'
keycloakPolicy='minioPolicy'
realm="UCit"

```bash
mc config host add "${minioServerName}/" http://0.0.0.0:9000 "${minioAdminID}" "${minioAdminPassword}"
```

```bash
mc admin config set "${minioServerName}/" identity_openid config_url="http://${IPv4}:8080/auth/realms/${organization}/.well-known/openid-configuration"  \ client_id="${keycloakClientId}" client_secret="${keycloakClientSecret}" claim_name="${keycloakPolicy}" redirect_uri="http://${IPv4}:9001/oauth_callback"
```


### Sub-commands

```bash
mc admin config set "${minioServerName}/" identity_openid config_url="http://${IPv4}:8080/auth/realms/${organization}/.well-known/openid-configuration"
```

```bash
mc admin config set "${minioServerName}/" identity_openid client_id="${keycloakClientId}"
```

```bash
mc admin config set "${minioServerName}/" identity_openid client_secret="${keycloakClientSecret}"
```

```bash
mc admin config set "${minioServerName}/" identity_openid claim_name=="${keycloakPolicy}"
```

```bash
mc admin config set "${minioServerName}/" identity_openid redirect_uri="http://${IPv4}:9001/oauth_callback"
```

```bash
mc admin service restart "${minioServerName}/"
```

```bash
mc admin config get "${minioServerName}/" identity_openid
```
