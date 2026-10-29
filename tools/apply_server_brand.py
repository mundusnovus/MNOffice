#!/usr/bin/env python3
"""Small, fail-closed overlay on a pinned DocumentServer image. Never edit licenses."""
from pathlib import Path
import re, shutil, os
root=Path(os.environ.get('EO_ROOT','/var/www/euro-office/documentserver'))
conf=Path(os.environ.get('EO_CONF','/etc/euro-office/documentserver'))
htmls=list((root/'web-apps/apps').glob('*/main/index.html'))
if len(htmls)<3:raise SystemExit('Unexpected editor layout; update the pinned overlay before building.')
for p in htmls:
    s=p.read_text()
    if '</head>' not in s:raise SystemExit('Missing editor head: '+str(p))
    s=re.sub(r'<title>[^<]*</title>','<title>Christian Office</title>',s)
    s=s.replace('</head>','<link rel="stylesheet" href="/christian-office/editor.css"><script defer src="/christian-office/editor.js"></script></head>')
    p.write_text(s)
for p in (root/'web-apps').rglob('favicon.ico'):
    shutil.copy('/opt/christian-office/brand/icons/office.ico',p)
p=conf/'nginx/includes/ds-docservice.conf'
s=p.read_text();s,n=re.subn(r'location = / \{ return 302 [^;]+; \}', 'location = / { root /opt/christian-office/portal; try_files /index.html =404; }',s)
if n!=1:raise SystemExit('Root route changed upstream; refusing to guess.')
s+='\nlocation ^~ /christian-office/ { alias /opt/christian-office/portal/; add_header X-Content-Type-Options nosniff; }\n'
p.write_text(s)
print('Branded',len(htmls),'editor entry points and the Office portal.')
