#!/bin/sh

cf create-service p-redis development mongodb-service
cf create-service p-rabbitmq standard rabbitmq-service
