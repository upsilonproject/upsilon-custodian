FROM registry.fedoraproject.org/fedora-minimal:40-x86_64

LABEL org.opencontainers.image.source https://github.com/upsilonproject/upsilon-custodian
LABEL org.opencontainers.image.authors James Read
LABEL org.opencontainers.image.title upsilon-custodian

ADD upsilon-custodian /opt/

ENTRYPOINT /opt/upsilon-custodian
