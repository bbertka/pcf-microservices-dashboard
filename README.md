# PCF RabbitMQ Twitter Demo

This demo uses RabbitMQ to queue tweets streamed by the Producer, ready for processing by the Consumer. In this example, the processing is just a sleep function.

Setup Instructions:
- Using Apps Manager, create a RabbitMQ service in your Org and note the name, do not bind the service
- Update each manifest file with the name of your RabbitMQ service in the 'services' field of the file
- Before deployment, go to apps.twitter.com an create an application to generate keys.
- Add Twitter keys to twitter-producer/manifest.yml

Deploy:
- Choose unique names for you Producer and Consumer, note them into the cooresponding manifest files
- execute 'cf push' in each folder

Monitor:
- Open two terminal windows to view streaming and messages
- In first terminal execute: 'cf logs twitter-producer'
- In second terminal execute: 'cf logs twitter-consumer'

The consumer by default is scaled to 4 instances so note the '[APP/x]' to see which instance is processing the tweets

Ref: https://www.rabbitmq.com/tutorials/tutorial-two-python.html


