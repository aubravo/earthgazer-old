# PROYECTO DE TESIS DE TITULACIÓN DE MAESTRIA #

## Deploy to Kubernetes Cluster ##

### Useful commands: ###

```commandline
helm install gxiba-postgresql bitnami/postgresql \
--values ./postgresql-values.yaml 
```
To get the password for "postgres" run:
```commandline
export POSTGRES_PASSWORD=$(kubectl get secret gxiba-postgresql \
-o jsonpath="{.data.postgres-password}" | base64 -d)
```

```commandline
kubectl run gxiba-postgresql-client \
--rm --tty -i --restart='Never' \
--image docker.io/bitnami/postgresql:14.3.0-debian-10-r17 \
--env="PGPASSWORD=$POSTGRES_PASSWORD" \
--command -- psql --host gxiba-postgresql \
-U postgres -d gxiba -p 5432
```

### Default connection: ###
```commandline
gxiba-postgresql.default.svc.cluster.local
```

