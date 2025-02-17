FROM python:3-alpine

RUN apk update && apk add iptables
RUN echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
RUN sysctl -p

CMD ["/bin/sh"]