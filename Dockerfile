FROM ghcr.io/euro-office/documentserver@sha256:2fadc1b3dc99250d6576fc0c0f34349db6725b752b08e91db9831fbb803fc5c2
COPY brand/ /opt/christian-office/brand/
COPY portal/ /opt/christian-office/portal/
COPY brand/ /opt/christian-office/portal/brand/
COPY fonts/ChristianSans-*.woff /opt/christian-office/portal/fonts/
COPY fonts/*.ttf /usr/local/share/fonts/christian-office/
COPY brand/Chancel-Regular.ttf /usr/local/share/fonts/christian-office/
COPY fonts/OFL.txt fonts/FONTLOG.txt /usr/local/share/fonts/christian-office/
COPY server/editor.* /opt/christian-office/portal/
COPY tools/apply_server_brand.py /opt/christian-office/
COPY LICENSE NOTICE.md /opt/christian-office/portal/
COPY server/start.sh /opt/christian-office/start.sh
RUN rm -f /etc/nginx/sites-enabled/default && python3 /opt/christian-office/apply_server_brand.py && fc-cache -f && nginx -t
ENV JWT_ENABLED=true JWT_HEADER=AuthorizationJwt GENERATE_FONTS=true EXAMPLE_ENABLED=false PLUGINS_ENABLED=false
EXPOSE 80
ENTRYPOINT ["/opt/christian-office/start.sh"]
