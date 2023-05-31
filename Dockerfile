FROM fedora-minimal

ADD upsilon-custodian /opt/

ENTRYPOINT /opt/upsilon-custodian
