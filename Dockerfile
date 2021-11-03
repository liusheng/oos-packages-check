FROM ubuntu

RUN apt-get -q update && \
  apt-get -q -y install python3 python3-pip

RUN pip3 install requests click pyyaml prettytable

ADD entrypoint.sh /
ADD oos-pkgs-checker /oos-pkgs-checker
ADD action.yml /

ENTRYPOINT ["/entrypoint.sh"]