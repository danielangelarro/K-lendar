from alpine

run echo "net.ipv4.ip_forward=1" | tee -a /etc/sysctl.conf
RUN sysctl -p

CMD /bin/sh

# cmd while true; do sleep 1; done