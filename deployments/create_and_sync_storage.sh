#!/usr/bin/env bash
gsutil mb gs://$1
gsutil defacl set public-read gs://$1
gsutil rsync -R static/ gs://$1