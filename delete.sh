#!/bin/bash

source .config

aws cloudformation delete-stack --stack-name $STACK
