#!/bin/bash

set -ev

mkdir .aws
echo -e '[profile default]\noutput = table\nregion = eu-central-1' > .aws/config
echo -e '[default]\naws_access_key_id = key\naws_secret_access_key = key' > .aws/credentials
make build
make run-test-command
