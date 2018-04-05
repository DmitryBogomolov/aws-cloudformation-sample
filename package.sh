#!/bin/bash

source .config

aws cloudformation package --template-file template.yaml --output-template-file output.yaml --s3-bucket $BUCKET
