#!/usr/bin/env bash
kubectl create secret generic cloudsql --namespace=wyvern --from-literal=username=$1 --from-literal=password=$2