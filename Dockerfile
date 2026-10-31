FROM ghcr.io/euro-office/documentserver@sha256:2fadc1b3dc99250d6576fc0c0f34349db6725b752b08e91db9831fbb803fc5c2
COPY brand/ /opt/asteria-office/brand/
COPY portal/ /opt/asteria-office/portal/
COPY brand/ /opt/asteria-office/portal/brand/
COPY fonts/AsteriaSerif-*.woff /opt/asteria-office/portal/fonts/
COPY fonts/*.ttf /usr/local/share/fonts/asteria-office/
COPY brand/AsteriaPixel-Regular.ttf /usr/local/share/fonts/asteria-office/
COPY fonts/OFL.txt fonts/FONTLOG.txt /usr/local/share/fonts/asteria-office/
COPY server/editor.* /opt/asteria-office/portal/
COPY tools/apply_server_brand.py /opt/asteria-office/
COPY LICENSE NOTICE.md /opt/asteria-office/portal/
COPY server/start.sh /opt/asteria-office/start.sh
RUN rm -f /etc/nginx/sites-enabled/default && python3 /opt/asteria-office/apply_server_brand.py && fc-cache -f && nginx -t
ENV JWT_ENABLED=true JWT_HEADER=AuthorizationJwt GENERATE_FONTS=true EXAMPLE_ENABLED=false PLUGINS_ENABLED=false
EXPOSE 80
ENTRYPOINT ["/opt/asteria-office/start.sh"]
