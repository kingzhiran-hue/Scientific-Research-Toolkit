import argparse,json,copy
from pathlib import Path
from .detection import propose
from .measure import digitize

def main():
    p=argparse.ArgumentParser(description='Scientific bar-chart digitizer; candidates require manual confirmation')
    sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('propose');a.add_argument('--image',required=True);a.add_argument('--out',required=True);a.add_argument('--region',nargs=4,type=int);a.add_argument('--baseline',type=int)
    a=sub.add_parser('measure');a.add_argument('--image',required=True);a.add_argument('--config',required=True);a.add_argument('--out',required=True);a.add_argument('--interactive',action='store_true')
    a=sub.add_parser('gui');a.add_argument('--image',required=True);a.add_argument('--config',required=True);a.add_argument('--out',required=True);a.add_argument('--port',type=int,default=8765)
    args=p.parse_args()
    try:
        if args.command=='propose':
            out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(propose(args.image,args.region,args.baseline),indent=2),encoding='utf-8')
        else:
            config=json.loads(Path(args.config).read_text(encoding='utf-8'))
            if args.command=='gui':
                from .gui import serve
                serve(args.image,config,args.out,args.port);return
            if args.interactive:
                config=copy.deepcopy(config)
                for g in config['groups']:
                    print('Group:',g['id'],'existing:',json.dumps(g))
                    for field in ['x','bar_y','upper_y','lower_y']:
                        v=input(field+' (Enter=retain, NR=missing error endpoint): ').strip()
                        if v:g[field]=None if v=='NR' and field in ['upper_y','lower_y'] else float(v)
                    g['confirmed']=input('Confirmed against original figure? Type YES: ').strip()=='YES'
            digitize(args.image,config,args.out)
    except (ValueError,KeyError,OSError) as e:
        p.exit(2,'Input/measurement error: '+str(e)+'\n')
if __name__=='__main__':main()
