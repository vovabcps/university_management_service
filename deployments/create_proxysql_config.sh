#!/usr/bin/env bash
kubectl create configmap proxysql-configmap --from-file=k8s/proxysql/proxysql.cnf --namespace=proxysql