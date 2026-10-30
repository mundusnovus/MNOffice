#!/usr/bin/env python3
"""Rebuild Novus Serif from the unmodified, checksum-pinned OFL source fonts.
Install fonttools==4.60.1. All outlines, metrics, hints and copyright records stay intact.
"""
from pathlib import Path
from io import BytesIO
import hashlib, tarfile
from fontTools.ttLib import TTFont
ROOT = Path(__file__).resolve().parents[1]
archive = ROOT / 'fonts/upstream/liberation-fonts-ttf-2.1.5.tar.gz'
assert hashlib.sha256(archive.read_bytes()).hexdigest() == '7191c669bf38899f73a2094ed00f7b800553364f90e2637010a69c0e268f25d0'
with tarfile.open(archive) as tar:
    license_member = next(m for m in tar.getmembers() if m.name.endswith('/LICENSE'))
    (ROOT / 'fonts/OFL.txt').write_bytes(tar.extractfile(license_member).read())
    for style in ('Regular', 'Bold', 'Italic', 'BoldItalic'):
        member = next(m for m in tar.getmembers() if m.name.endswith('/LiberationSerif-' + style + '.ttf'))
        font = TTFont(BytesIO(tar.extractfile(member).read()), recalcTimestamp=False)
        for record in font['name'].names:
            if record.nameID in (1, 3, 4, 6, 16, 18, 21):
                text = record.toUnicode().replace('Liberation Serif', 'Novus Serif').replace('LiberationSerif', 'NovusSerif')
                record.string = text.encode(record.getEncoding())
        for flavor, suffix in ((None, 'ttf'), ('woff', 'woff')):
            font.flavor = flavor
            font.save(ROOT / ('fonts/NovusSerif-' + style + '.' + suffix))
        assert font['name'].getDebugName(1) == 'Novus Serif'
        print('Novus Serif', style, len(font.getBestCmap()), 'characters')
