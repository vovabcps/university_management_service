#!/usr/bin/env bash
gcloud container clusters create wyvern-cluster \
  --scopes "https://www.googleapis.com/auth/userinfo.email","cloud-platform" \
  --num-nodes 3 --zone "europe-west1-b"
gcloud container clusters get-credentials wyvern-cluster --zone "europe-west1-b"