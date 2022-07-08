# Gxiba #

## Deploy to Kubernetes Cluster ##

### Useful commands: ###

```commandline
helm install postgres bitnami/postgresql
```
To get the password for "postgres" run:
```commandline
export POSTGRES_PASSWORD=$(kubectl get secret gxiba-postgresql \
-o jsonpath="{.data.postgres-password}" | base64 -d)
```
