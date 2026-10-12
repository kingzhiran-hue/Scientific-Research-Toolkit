"""Open vector/raster outputs and check actual content; PDF rendering is additional visual QA."""
import json,sys,xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
try:import pymupdf
except ImportError:raise SystemExit('Install requirements-dev.txt for PDF validation')
ROOT=Path(__file__).resolve().parents[1]
checks=[]
for kind in ['forest','sensitivity','loo','rob-summary','rob-matrix','evidence','prisma','comparison']:
    stem=ROOT/'outputs/figures'/kind
    doc=pymupdf.open(stem.with_suffix('.pdf'));assert len(doc)==1
    text=doc[0].get_text();assert 'Synthetic continuous-outcome analysis' in text
    assert doc[0].rect.width>=4*72
    if kind in ['forest','sensitivity','loo','comparison']:assert 'Difference in synthetic units' in text
    if kind=='prisma':assert '240' in text and '14' in text
    if kind=='evidence':assert 'causal interpretation' in text
    if kind=='forest':
        result=json.loads((ROOT/'outputs/meta/results.json').read_text(encoding='utf-8'))['results']['primary'];assert f"{result['estimate']:.3f}" in text;assert f"{result['CI'][0]:.3f}" in text
    for block in doc[0].get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            for span in line['spans']:
                r=pymupdf.Rect(span['bbox']);assert r.x0>=0 and r.y0>=0 and r.x1<=doc[0].rect.width+1 and r.y1<=doc[0].rect.height+1,(kind,span['text'],'clipped')
    preview=ROOT/'outputs/tests/previews';preview.mkdir(parents=True,exist_ok=True);doc[0].get_pixmap(matrix=pymupdf.Matrix(1.4,1.4)).save(preview/(kind+'.png'));doc.close()
    svg=ET.parse(stem.with_suffix('.svg'));assert svg.getroot().tag.endswith('svg')
    im=Image.open(stem.with_suffix('.png'));assert abs(im.info.get('dpi',(0,0))[0]-600)<1;assert im.width>=2400
    checks.append(dict(type=kind,PDF_open=True,SVG_parse=True,PNG_600dpi=True,text_bounds=True))
doc=pymupdf.open(ROOT/'outputs/tests/minimal.pdf');text=doc[0].get_text();assert 'CI: solid line' not in text and 'PI: dashed line' not in text;doc.close()
for kind in ['minimal','long_labels','single_effect']:
    doc=pymupdf.open(ROOT/'outputs/tests'/f'{kind}.pdf');doc[0].get_pixmap(matrix=pymupdf.Matrix(1.4,1.4)).save(ROOT/'outputs/tests/previews'/f'{kind}.png');doc.close()
(ROOT/'outputs/tests/file_validation.json').write_text(json.dumps(dict(PASS=True,checks=checks,minimal_flags_checked=True),indent=2),encoding='utf-8')
print('Eight PDF/SVG/600-DPI PNG sets opened and validated')
