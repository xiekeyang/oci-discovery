FROM nginx:1.12

COPY nginx.conf /etc/nginx/nginx.conf
COPY data/oci-host-ref-engines /srv/example.com/.well-known/oci-host-ref-engines
COPY data/app /srv/example.com/oci-index/app
COPY data/oci-cas /srv/example.com/oci-cas
COPY ssl /etc/ssl
