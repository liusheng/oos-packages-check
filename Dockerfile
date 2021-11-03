FROM ubuntu

RUN apt-get -q update && \
  apt-get -q install python3 python3-pip

RUN pip3 install requests click pyyaml prettytable

ADD entrypoint.sh /
ADD hub-mirror /hub-mirror
ADD action.yml /

ENTRYPOINT ["/entrypoint.sh"]