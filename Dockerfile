FROM alpine:3.17
RUN apk add --no-cache bash curl wget python3 py3-pip borgbackup borgmatic openssh jq bind-tools
RUN pip3 install pyyaml
COPY src /filebup
RUN mkdir /filebup/config
RUN mkdir /filebup/volumes
RUN mkdir -p /root/.ssh/
RUN chmod +x /filebup/entrypoint.sh
ENTRYPOINT ["/filebup/entrypoint.sh"] 