upstream app_server {
    server unix:/tmp/template.sock;
    # server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name template.no www.template.no;
    rewrite ^(.*) https://template.no$1 permanent;

    access_log /var/log/nginx/template_access.log;
    error_log /var/log/nginx/template_error.log;
}

server {
    listen 443 default_server ssl;
    server_name template.no www.template.no test.template.no;
    keepalive_timeout 5;

    access_log /var/log/nginx/template_access.log;
    error_log /var/log/nginx/template_error.log;

    ssl_certificate /opt/www/template/config/template-positivessl.crt;
    ssl_certificate_key /opt/www/template/config/template.key; 

    location / {
        uwsgi_pass app_server;
        include /etc/nginx/uwsgi_params;
    }

    location /static {
        root /opt/www/template/app;
        access_log off;
        expires 30d;
        add_header Cache-Control public;
    }

    location /robots.txt { root /opt/www/template/app/static/; }
    location /google1234.html { root /opt/www/template/app/static/; }
    location /sitemap.xml { root /opt/www/template/app/static/; }

    #enables all versions of TLS, but not SSLv2 or 3 which are weak and now deprecated.
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;

    #Disables all weak ciphers
    ssl_ciphers "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA:ECDHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA256:DHE-RSA-AES128-SHA256:DHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA:ECDHE-RSA-DES-CBC3-SHA:EDH-RSA-DES-CBC3-SHA:AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-SHA256:AES128-SHA256:AES256-SHA:AES128-SHA:DES-CBC3-SHA:HIGH:!aNULL:!eNULL:!EXPORT:!DES:!MD5:!PSK:!RC4";
}