FROM registry.fedoraproject.org/fedora-minimal:40-x86_64

ADD upsilon-custodian /opt/

ENTRYPOINT /opt/upsilon-custodian
