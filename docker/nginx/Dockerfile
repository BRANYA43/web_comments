FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf

COPY default.conf /etc/nginx/conf.d/
COPY healthcheck.sh /usr/local/bin

RUN chmod +x /usr/local/bin/healthcheck.sh
