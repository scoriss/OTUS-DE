docker run --rm --name elk_demo_logstash --net elastic -v $(pwd)/logstash:/app -it logstash:7.14.1 logstash -f /app/clickstream.conf
