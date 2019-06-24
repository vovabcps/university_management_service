#!/usr/bin/env bash
kubectl create secret generic cloudsql-oauth-credentials --namespace=wyvern --from-file=credentials.json=$1