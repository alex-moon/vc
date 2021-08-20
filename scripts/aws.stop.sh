#!/bin/bash

id=$(aws ec2 describe-instances | jq -r '.[][].Instances[] | select(.Tags[].Key=="Name" and .Tags[].Value=="vc") | .InstanceId')
aws ec2 stop-instances --instance-ids $id

