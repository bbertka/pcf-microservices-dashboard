#!/bin/sh

cf create-service p-redis shared-vm redis-service
cf create-service p-rabbitmq standard rabbitmq-service
