FROM alpine:3.17
RUN apk add --no-cache bash curl python3 py3-pip borgbackup openssh
RUN pip3 install pyyaml
COPY src /filebup
RUN mkdir /filebup/config
RUN mkdir /filebup/volumes
RUN mkdir /filebup/cronhelpers
RUN mkdir -p /root/.ssh/
RUN chmod +x /filebup/entrypoint.sh
ENTRYPOINT ["/filebup/entrypoint.sh"] 