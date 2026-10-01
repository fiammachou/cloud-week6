FROM nginxinc/nginx-unprivileged:alpine

COPY index.html /usr/share/nginx/html/index.html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY images /usr/share/nginx/html/images

EXPOSE 8080