"""Conservative image candidates. These are proposals, never confirmed measurements."""
import numpy as np
from PIL import Image

def runs(mask):
    a = np.flatnonzero(np.diff(np.r_[False, mask, False].astype(int)))
    return [(int(s), int(e-1)) for s,e in zip(a[::2],a[1::2])]

def propose(image, plot_region=None, baseline_y=None, threshold=210):
    a = np.asarray(Image.open(image).convert('RGB'))
    height,width = a.shape[:2]
    box = plot_region or [0,0,width,height]
    x0,y0,x1,y1 = map(int,box)
    if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
        raise ValueError('Invalid plot region')
    gray = a.mean(axis=2)
    ink = gray < threshold
    cap_ink = gray < 90
    region = ink[y0:y1,x0:x1]
    axis_x = int(x0+np.argmax(region.sum(axis=0)))
    axis_y = int(y0+np.argmax(region.sum(axis=1)))
    if region.sum(axis=0).max() < .3*(y1-y0):
        raise ValueError('No reliable axis/body candidate; use manual coordinates')
    ticks = []
    if axis_x-x0 >= 5:
        m = ink[y0:y1,max(x0,axis_x-18):axis_x-1].sum(axis=1) >= 5
        ticks = [int(y0+(s+e)//2) for s,e in runs(m)]
    baseline = int(axis_y if baseline_y is None else baseline_y)
    if not y0 < baseline < y1:
        raise ValueError('Baseline must be inside plot region')
    # Wide-body support immediately above OR below baseline accommodates negative bars.
    score = ink[max(y0,baseline-24):max(y0,baseline-3),x0:x1].sum(axis=0)
    score = np.maximum(score,ink[min(y1,baseline+3):min(y1,baseline+24),x0:x1].sum(axis=0))
    feet = [(x0+s,x0+e) for s,e in runs(score>=7) if e-s>=9 and x0+s>axis_x+5]
    bars = []
    for l,r in feet:
        band = ink[y0:y1,l:r+1]
        broad = band.sum(axis=1) >= .65*(r-l+1)
        candidates = []
        for s,e in runs(broad):
            if e-s >= 8:
                # Sustained wide body rejects thin significance brackets and caps.
                near_base = min(abs(y0+s-baseline),abs(y0+e-baseline)) < 8
                if near_base:
                    top = y0+s if abs(y0+s-baseline)>abs(y0+e-baseline) else y0+e
                    candidates.append(top)
        if len(candidates) != 1:
            continue
        top = int(candidates[0]); cx=(l+r)//2
        # Caps need a central stem and cannot be a full-width significance bracket.
        cap_rows=[]
        for yy in range(y0+1,y1-1):
            if abs(yy-top)<4 or abs(yy-baseline)<4:continue
            run = runs(cap_ink[yy,l:r+1])
            central = [z for z in run if z[0] <= cx-l <= z[1] and 3 <= z[1]-z[0]+1 <= .6*(r-l+1)]
            if not central:continue
            lo,hi=sorted([top,yy]); stem=cap_ink[lo:hi+1,max(l,cx-2):min(r+1,cx+3)].any(axis=1)
            if stem.mean() >= .85:cap_rows.append(yy)
        caps=[int((s+e)/2) for s,e in runs(np.isin(np.arange(y0,y1),cap_rows))]
        caps=[v+y0 for v in caps]
        bars.append(dict(x=cx,bar_y=top,upper_y=max([v for v in caps if v<top],default=None),lower_y=min([v for v in caps if v>top],default=None),width=r-l+1,confirmed=False,variance_type='NR',n=None))
    if not bars:
        raise ValueError('No reliable bar-body candidates; manual point selection required')
    return dict(axis_x_candidate=axis_x,baseline_y_candidate=baseline,tick_y_candidates=ticks,bar_candidates=bars,status='CANDIDATES_REQUIRE_USER_CONFIRMATION')
