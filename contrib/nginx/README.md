# Nginx

This provides a experiment of how to set up a discovery server by nginx. It is useful for integration test.

Developer can build up via Dockerfile and run a discovery server:

```
$ docker build -t nginx:discovery-server .
$ docker run -d --name discovery-server -p 80:80 -p 443:443 nginx:discovery-server
```

Before accessing the discovery server, developer should add the `*.crt` to `/usr/local/share/ca-certificates` and update it.
