# Keycloak deployment

```bash
sudo su
yum install -y java
keycloakVersion="15.0.2"
wget "https://github.com/keycloak/keycloak/releases/download/${keycloakVersion}/keycloak-${keycloakVersion}.tar.gz"
tar -xvzf "keycloak-${keycloakVersion}.tar.gz"
mv "keycloak-${keycloakVersion}" /opt/keycloak
groupadd keycloak
useradd -r -g keycloak -d /opt/keycloak -s /sbin/nologin keycloak
chown -R keycloak: /opt/keycloak/
chmod o+x /opt/keycloak/bin/
cat > /etc/keycloak/keycloak.conf <<EOF
# The configuration you want to run
WILDFLY_CONFIG=standalone.xml

# The mode you want to run
WILDFLY_MODE=standalone

# The address to bind to
WILDFLY_BIND=0.0.0.0
EOF
cp /opt/keycloak/docs/contrib/scripts/systemd/launch.sh /opt/keycloak/bin/
chown keycloak: /opt/keycloak/bin/launch.sh

cat > /etc/systemd/system/keycloak.service <<EOF
[Unit]
Description=The WildFly Application Server
After=syslog.target network.target
Before=httpd.service

[Service]
Environment=LAUNCH_JBOSS_IN_BACKGROUND=1
EnvironmentFile=/etc/keycloak/keycloak.conf
User=keycloak
Group=keycloak
LimitNOFILE=102642
PIDFile=/var/run/wildfly/keycloak.pid
ExecStart=/opt/keycloak/bin/launch.sh $WILDFLY_MODE $WILDFLY_CONFIG $WILDFLY_BIND
StandardOutput=null

[Install]
WantedBy=multi-user.target
EOF

sed -i -- 's/jboss.bind.address:127.0.0.1/jboss.bind.address:0.0.0.0/g' /opt/keycloak/standalone/configuration/standalone.xml
sed -i -- 's/jboss.bind.address.management:127.0.0.1/jboss.bind.address.management:0.0.0.0/g' /opt/keycloak/standalone/configuration/standalone.xml

systemctl daemon-reload
systemctl enable keycloak
systemctl start keycloak
systemctl status keycloak
```


## Configure Keycloak tenant

Go to Clients
    Click on account
        Settings
        Change Access Type to confidential.
        Save
    Click on credentials tab
        Copy the Secret to clipboard.
        This value is needed for MINIO_IDENTITY_OPENID_CLIENT_SECRET for MinIO.

Go to Users
    Click on the user
    Attribute, add a new attribute
      Key => minioPolicy
      Value => Existing policy in MinIO (e.g., readwrite, readonly, consoleAdmin)
    Add and Save

Go to Clients
    Click on account
    Settings, set Valid Redirect URIs to *, expand Advanced Settings and set Access Token Lifespan to 1 Hours
    Save

Go to Clients
    Client on account
    Mappers
    Create
        Name => minio_mapper
        Mapper Type => User Attribute
        User Attribute => minioPolicy
        Token Claim Name => minioPolicy
        Claim JSON Type => string
    Save

Open http://localhost:8080/auth/realms/minio/.well-known/openid-configuration to verify OpenID discovery document, verify it has authorization_endpoint and jwks_uri


# Keycloak usage

  keycloakClientId
  keycloakClientSecret
  IPv4

  keycloakClientId='account'
  keycloakClientSecret='de46ee5a-7402-472e-9f1d-89a1651f10e9'
  IPv4='54.74.6.211'

```bash
curl -k -d "client_id=${keycloakClientId}" -d "client_secret=${keycloakClientSecret}" -d "grant_type=client_credentials" "http://${IPv4}:8080/auth/realms/UCit/protocol/openid-connect/token"
```

Example:
> curl -k -d "client_id=account" -d "client_secret=8bf7178f-8bc6-4f76-9417-9698364d898f" -d "grant_type=client_credentials" "http://127.0.0.1:8080/auth/realms/UCit/protocol/openid-connect/token"


Get access token if service account:
```bash
access_token=$(curl -k -d "client_id=${keycloakClientId}" -d "client_secret=${keycloakClientSecret}" -d "grant_type=client_credentials" "http://${IPv4}:8080/auth/realms/${organization}/protocol/openid-connect/token" | jq -r '.access_token')
```

Get access token if user account:
```bash
access_token=$(curl -k -d "client_id=${keycloakClientId}" -d "client_secret=${keycloakClientSecret}" -d "username=${userName}" -d "password=${userPassword}" -d "grant_type=password" "http://${IPv4}:8080/auth/realms/${organization}/protocol/openid-connect/token" | jq -r '.access_token')
```

Get uerinfo:
```bash
curl -H "Authorization: Bearer ${access_token}" "http://${IPv4}:8080/auth/realms/${organization}/protocol/openid-connect/userinfo"
```


Get information about specific user:
```bash
curl -H "Authorization: Bearer ${access_token}" "http://${IPv4}:8080/auth/admin/master/console/#/realms/${organization}/users/${userId}"
```

### Mapper configuration

#### Share group in token id
Clients > account > Mappers > groups
  Name                  groups
  Mapper Type           Group Membership
  Token Claim Name      groups
  Add to ID token       yes
  Add to access token   yes
  Add to userinfo       yes

#### Share role in token id
Clients > account > Mappers > groups
  Name                  realm roles
  Mapper Type           User Realm Role
  Multivalued           on
  Token Claim Name      roles
  Claim JSON Type       string
  Add to ID token       yes
  Add to access token   yes
  Add to userinfo       yes


### Logs

Log path:
> /opt/keycloak/standalone/log

https://github.com/minio/operator/issues/603

Retirer les id des exports keycloak
```bash
sed -i '/\"id\":/d' /opt/heroes/org.json
```
Virer:
"authenticationFlowBindingOverrides": {
  "direct_grant": "6019b415-a3aa-4db8-ac98-b9b92a33ae0a"
},

Documentation:
* Keycloak: https://www.keycloak.org/documentation
* Authorization: https://www.keycloak.org/docs/latest/authorization_services/index.html
* Keycloak + MinIO: https://github.com/minio/minio/blob/master/docs/sts/keycloak.md
