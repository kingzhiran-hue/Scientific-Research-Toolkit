"""Convert user-confirmed points; save overlays, coordinates and reproducible CSV/JSON."""
import csv,json,hashlib,math
from pathlib import Path
from PIL import Image,ImageDraw
from .calibration import AxisCalibration

def digitize(image, config, output):
    image=Path(image);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    im=Image.open(image).convert('RGB');axis=AxisCalibration(config['segments'])
    groups=config.get('groups',[])
    if not groups:raise ValueError('No confirmed group coordinates provided')
    ids=[str(g['id']) for g in groups]
    if len(set(ids))!=len(ids):raise ValueError('Duplicate group ids')
    rows=[]
    for g in groups:
        if g.get('confirmed') is not True:raise ValueError('Each group must be explicitly confirmed by the user')
        x=float(g['x']);y=float(g['bar_y'])
        if not 0<=x<im.width or not 0<=y<im.height:raise ValueError('Coordinates outside original image')
        if config.get('plot_region'):
            x0,y0,x1,y1=config['plot_region']
            if not x0<=x<=x1 or not y0<=y<=y1:raise ValueError('Coordinates outside declared panel')
        kind=g.get('variance_type','NR')
        if kind not in ['SD','SEM','CI','OTHER','NR']:raise ValueError('Unknown variance label')
        n=g.get('n')
        if n is not None and (not isinstance(n,int) or isinstance(n,bool) or n<1):raise ValueError('n must be user-supplied positive integer or null')
        mean=axis.value(y,g.get('segment'));ends={}
        for name in ['upper','lower']:
            py=g.get(name+'_y')
            if py is None:ends[name]=None;continue
            if not math.isfinite(float(py)) or not 0<=py<im.height:raise ValueError('Error endpoint outside image')
            if config.get('plot_region') and not config['plot_region'][1]<=py<=config['plot_region'][3]:raise ValueError('Error endpoint outside declared panel')
            ends[name]=axis.value(py,g.get(name+'_segment',g.get('segment')))
        if ends['upper'] is not None and ends['upper']<mean-1e-10:raise ValueError('Upper endpoint below mean in value space')
        if ends['lower'] is not None and ends['lower']>mean+1e-10:raise ValueError('Lower endpoint above mean in value space')
        eu=None if ends['upper'] is None else ends['upper']-mean
        el=None if ends['lower'] is None else mean-ends['lower']
        symmetric=eu is not None and el is not None and math.isclose(eu,el,rel_tol=1e-6,abs_tol=1e-9)
        rows.append(dict(group_id=g['id'],mean=mean,upper_value=ends['upper'],lower_value=ends['lower'],error_upper=eu,error_lower=el,variance_type=kind,n=n,unit=g.get('unit',config.get('unit','NR')),symmetric=symmetric,x=x,bar_y=y,upper_y=g.get('upper_y'),lower_y=g.get('lower_y'),confirmed=True))
    draw=ImageDraw.Draw(im)
    for s in config['segments']:
        for t in s['ticks']:
            y=t['pixel_y'];draw.line([(0,y),(im.width-1,y)],fill='#9AABD0',width=1)
    for g in groups:
        x=g['x'];y=g['bar_y'];draw.line([(x-12,y),(x+12,y)],fill='#00765A',width=3)
        for key in ['upper_y','lower_y']:
            if g.get(key) is not None:draw.line([(x-10,g[key]),(x+10,g[key])],fill='#A33B31',width=3);draw.line([(x,y),(x,g[key])],fill='#A33B31',width=2)
        draw.text((x+14,y),str(g['id']),fill='#00382B')
    im.save(output/'overlay.png')
    with (output/'measurements.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (output/'measurements.json').write_text(json.dumps(rows,indent=2,allow_nan=False),encoding='utf-8')
    metadata={'image_name':image.name,'image_sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'coordinate_frame':'original image pixels; x right, y down','configuration':config,'calibration':{k:vars(v) for k,v in axis.segments.items()},'automatic_attribution_performed':False}
    (output/'confirmed_coordinates.json').write_text(json.dumps(metadata,indent=2,allow_nan=False),encoding='utf-8')
    return rows
