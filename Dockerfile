FROM ghcr.io/euro-office/documentserver@sha256:2fadc1b3dc99250d6576fc0c0f34349db6725b752b08e91db9831fbb803fc5c2
COPY brand/ /opt/mn-office/brand/
COPY portal/ /opt/mn-office/portal/
COPY brand/ /opt/mn-office/portal/brand/
COPY fonts/NovusSerif-*.woff /opt/mn-office/portal/fonts/
COPY fonts/*.ttf /usr/local/share/fonts/mn-office/
COPY brand/Chancel-Regular.ttf /usr/local/share/fonts/mn-office/
COPY fonts/OFL.txt fonts/FONTLOG.txt /usr/local/share/fonts/mn-office/
COPY server/editor.* /opt/mn-office/portal/
COPY tools/apply_server_brand.py /opt/mn-office/
COPY LICENSE NOTICE.md /opt/mn-office/portal/
COPY server/start.sh /opt/mn-office/start.sh
RUN rm -f /etc/nginx/sites-enabled/default && python3 /opt/mn-office/apply_server_brand.py && fc-cache -f && nginx -t
ENV JWT_ENABLED=true JWT_HEADER=AuthorizationJwt GENERATE_FONTS=true EXAMPLE_ENABLED=false PLUGINS_ENABLED=false
EXPOSE 80
ENTRYPOINT ["/opt/mn-office/start.sh"]
