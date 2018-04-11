#!/bin/bash

source .config

aws cloudformation deploy --template-file .package/template.yaml --stack-name $STACK --capabilities CAPABILITY_IAM
