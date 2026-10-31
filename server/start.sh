#!/bin/sh
set -eu
: "${JWT_SECRET:?Set the same JWT secret in Cloud and Office}"
if [ "${#JWT_SECRET}" -lt 32 ]; then echo 'JWT_SECRET must have at least 32 characters' >&2; exit 1; fi
# nginx must start, or the editors are unreachable. Test the configuration first and say why it fails. Some hosts
# cannot bind IPv6 even when the kernel has it; then serve on IPv4 only (Railway's proxy reaches us either way).
CONF=/etc/euro-office/documentserver/nginx/ds.conf
# The stock nginx site also claims the default server on port 80; the document server is the only site here.
rm -f /etc/nginx/sites-enabled/default
if ! out=$(nginx -t 2>&1); then
  echo "[asteria-office] nginx config test failed:" >&2; echo "$out" >&2
fi
if ! nginx -t >/dev/null 2>&1 || ! (command -v python3 >/dev/null && python3 -c "import socket;s=socket.socket(socket.AF_INET6);s.bind(('::',0))" 2>/dev/null); then
  echo "[asteria-office] no usable IPv6: serving on IPv4 only" >&2
  sed -i '/listen[[:space:]]*\[::\]/d; s/listen 0\.0\.0\.0:80;/listen 0.0.0.0:80 default_server;/' "$CONF"
  for f in /etc/euro-office/documentserver/nginx/ds.conf.tmpl /etc/euro-office/documentserver/nginx/ds-ssl.conf.tmpl; do [ -f "$f" ] && sed -i '/listen[[:space:]]*\[::\]/d' "$f" || true; done
fi
nginx -t 2>&1 | sed 's/^/[asteria-office] /' >&2 || true
exec /entrypoint.sh "$@"
