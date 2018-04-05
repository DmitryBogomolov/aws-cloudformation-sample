#!/bin/bash

source .config

aws cloudformation deploy --template-file output.yaml --stack-name $STACK --capabilities CAPABILITY_IAM
