#!/usr/bin/env python3
"""Retain upstream OOXML templates, replacing default writing faces only."""
from pathlib import Path
import zipfile, re, shutil, argparse
parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);args=parser.parse_args()
out=Path(__file__).resolve().parents[1]/'portal/templates'
for extension in ('docx','xlsx','pptx','pdf'):
    source=args.source/('new.'+extension);dest=out/('blank.'+extension)
    if extension=='pdf':shutil.copy(source,dest);continue
    with zipfile.ZipFile(source) as src,zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as dst:
        for name in src.namelist():
            data=src.read(name)
            if name.endswith('.xml'):
                text=data.decode('utf-8')
                for old in ('Times New Roman','Calibri','Aptos','Arial','Liberation Serif','Cambria','Carlito'):
                    text=text.replace('"'+old+'"','"Asteria Serif"')
                # Explicit faces must outrank Office theme font references.
                text=re.sub(r' w:(asciiTheme|hAnsiTheme|eastAsiaTheme|cstheme)="[^"]*"','',text)
                data=text.encode('utf-8')
            info=zipfile.ZipInfo(name,(2026,10,29,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;dst.writestr(info,data)
print('Built blank document, workbook, presentation and PDF templates.')
