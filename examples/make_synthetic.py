"""All example values and pixels are invented, not drawn from any research dataset."""
import csv,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def dump(p,x):p.write_text(json.dumps(x,indent=2),encoding='utf-8')
def make_examples():
    out=ROOT/'examples/synthetic_data';out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for i,(t,c,st,sc,nt,nc) in enumerate([(10.0,9.3,1.8,2.1,18,18),(12.0,11.8,2.3,1.7,24,22),(8.0,9.0,1.5,1.8,16,16),(9.0,9.8,2.0,2.2,28,26),(11.0,10.1,2.5,2.3,21,21),(9.0,10.3,1.9,2.4,30,28)],1):
        rows.append(dict(id=f'Synthetic_{i}',independence_id=f'Cohort_{i}',independent=True,shared_control=False,control_id=f'Control_{i}',construct='Synthetic continuous outcome',unit='synthetic_units',mean_t=t,mean_c=c,error_t=st,error_c=sc,error_type_t='SD',error_type_c='SD',n_t=nt,n_c=nc,risk='HIGH' if i==2 else 'LOW',setting='delayed' if i in [3,4,6] else 'early'))
    write_csv(out/'groups.csv',rows)
    effects=[dict(id=f'Effect_{i}',independence_id=f'Effect_cohort_{i}',independent=True,unit='synthetic_units',yi=y,vi=v) for i,(y,v) in enumerate([(0.2,.04),(-.5,.08),(1.1,.12),(-.2,.06),(.8,.05)],1)]
    write_csv(out/'effects.csv',effects)
    dump(out/'analysis_config.json',dict(subsets=[dict(name='exclude_high_risk',exclude=True,where=[dict(field='risk',operator='eq',value='HIGH')]),dict(name='delayed_subset',where=[dict(field='setting',operator='eq',value='delayed')])]))
    rob=[]
    for i in range(1,6):
        for j,domain in enumerate(['Sequence','Masking','Missing outcomes','Reporting']):rob.append(dict(study=f'Sample {i}',domain=domain,judgment=['LOW','UNCLEAR','HIGH','LOW','NR'][(i+j)%5]))
    write_csv(out/'risk_of_bias.csv',rob)
    write_csv(out/'evidence.csv',[dict(id=f'Sample {i}',Endpoint_A=['UP','DOWN','NO_CHANGE','NR','DOWN'][i-1],Marker_B=['DOWN','UP','QUALITATIVE_UP','NR','NO_CHANGE'][i-1],Marker_C=['NR','DOWN','QUALITATIVE_DOWN','UP','NO_CHANGE'][i-1]) for i in range(1,6)])
    dump(out/'selection_counts.json',dict(identified=240,duplicates=70,screened=170,title_excluded=125,sought=45,not_retrieved=3,assessed=42,fulltext_excluded=28,included=14))
    dump(out/'plot_config.json',dict(title='Synthetic continuous-outcome analysis',xlab='Difference in synthetic units',font='sans',width=10,font_size=10,dpi=600,show_CI=True,show_PI=True,show_I2=True))
    dump(out/'plot_minimal.json',dict(title='Synthetic minimal comparison',xlab='Synthetic units',width=10,dpi=300,show_CI=False,show_PI=False,show_I2=False,legend=False))
    font=ImageFont.load_default(size=16)
    for name,baseline,ticks,bars,scale in [
        ('linear',530,[(530,0),(430,2),(330,4),(230,6),(130,8)],[330,270,410],'linear'),
        ('negative',320,[(530,-4),(425,-2),(320,0),(215,2),(110,4)],[430,250,390],'linear'),
        ('nonzero',530,[(530,10),(430,12),(330,14),(230,16),(130,18)],[330,270,410],'linear'),
        ('log',530,[(530,1),(330,10),(130,100)],[330,270,410],'log10'),
        ('bracket',530,[(530,0),(430,2),(330,4),(230,6),(130,8)],[330,270,410],'linear')]:
        im=Image.new('RGB',(900,640),'white');d=ImageDraw.Draw(im);d.line([(90,100),(90,550)],fill='black',width=2);d.line([(90,baseline),(820,baseline)],fill='black',width=2)
        for y,v in ticks:d.line([(80,y),(90,y)],fill='black',width=2);d.text((35,y-9),str(v),font=font,fill='black')
        groups=[]
        for i,y in enumerate(bars):
            x=260+i*200;lo,hi=sorted([y,baseline]);d.rectangle((x-40,lo,x+40,hi),fill='#6C99AA',outline='black',width=2)
            d.line([(x,y-25),(x,y+25)],fill='black',width=2);d.line([(x-14,y-25),(x+14,y-25)],fill='black',width=2);d.line([(x-14,y+25),(x+14,y+25)],fill='black',width=2)
            d.text((x-32,580),f'Group {i+1}',font=font,fill='black')
            groups.append(dict(id=f'Group_{i+1}',x=x,bar_y=y,upper_y=y-25,lower_y=y+25,variance_type='SD' if scale=='linear' else 'CI',n=12,confirmed=True,unit='synthetic_units'))
        if name=='bracket':d.line([(230,210),(230,195),(690,195),(690,210)],fill='black',width=2);d.text((440,172),'***',font=font,fill='black')
        d.text((90,40),'SYNTHETIC DATA - no empirical measurements',font=font,fill='black');im.save(out/(name+'.png'))
        dump(out/(name+'_points.json'),dict(unit='synthetic_units',plot_region=[80,90,830,560],segments=[dict(id='main',scale=scale,ticks=[dict(pixel_y=y,value=v) for y,v in ticks])],groups=groups))
    Image.new('RGB',(900,640),'white').save(out/'unreadable.png')
    # Distinct ranges ensure the broken axis is never treated as one continuous line.
    im=Image.new('RGB',(900,640),'white');d=ImageDraw.Draw(im);d.text((90,40),'SYNTHETIC broken-axis diagram',font=font,fill='black')
    d.line([(90,120),(90,310)],fill='black',width=2);d.line([(90,380),(90,530)],fill='black',width=2);d.line([(90,530),(800,530)],fill='black',width=2)
    for y,v in [(120,12),(310,8),(380,2),(530,0)]:d.line([(80,y),(90,y)],fill='black',width=2);d.text((40,y-8),str(v),font=font,fill='black')
    d.rectangle((220,430,300,530),fill='#6C99AA',outline='black',width=2);d.line([(260,410),(260,450)],fill='black',width=2)
    for y in [410,450]:d.line([(245,y),(275,y)],fill='black',width=2)
    im.save(out/'broken.png')
    dump(out/'broken_points.json',dict(segments=[dict(id='high',ticks=[dict(pixel_y=120,value=12),dict(pixel_y=310,value=8)]),dict(id='low',ticks=[dict(pixel_y=380,value=2),dict(pixel_y=530,value=0)])],groups=[dict(id='Broken_sample',x=260,bar_y=430,upper_y=410,lower_y=450,segment='low',variance_type='SEM',n=9,confirmed=True)]))
    (out/'SYNTHETIC_DATA.md').write_text('All values, labels, pixel coordinates and images in this directory are invented for software testing. They are not observations, published study data or reusable empirical benchmarks.\n',encoding='utf-8')
    print('Synthetic examples created')
if __name__=='__main__':make_examples()
