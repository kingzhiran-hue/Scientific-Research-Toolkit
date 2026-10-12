"""Local browser point editor. No cloud, telemetry, or outside network binding."""
import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler,HTTPServer
from .measure import digitize

def make_handler(image,config,output):
    image=Path(image)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            if self.path=='/':data=(Path(__file__).parent/'point_editor.html').read_bytes();kind='text/html; charset=utf-8'
            elif self.path=='/image':data=image.read_bytes();kind='application/octet-stream'
            elif self.path=='/config':data=json.dumps(config).encode();kind='application/json'
            else:self.send_error(404);return
            self.send_response(200);self.send_header('Content-Type',kind);self.end_headers();self.wfile.write(data)
        def do_POST(self):
            if self.path!='/save':self.send_error(404);return
            # Only same-origin browser requests; do not let another website submit points.
            origin=self.headers.get('Origin');host=self.headers.get('Host')
            if origin and origin!='http://'+host:self.send_error(403);return
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<1000000:self.send_error(413);return
            try:
                supplied=json.loads(self.rfile.read(length));rows=digitize(image,supplied,output);data=json.dumps({'saved':True,'groups':len(rows)}).encode();status=200
            except (ValueError,KeyError,TypeError) as e:data=json.dumps({'saved':False,'error':str(e)}).encode();status=400
            self.send_response(status);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(data)
    return Handler

def serve(image,config,output,port):
    server=HTTPServer(('127.0.0.1',port),make_handler(image,config,output))
    print(f'Open http://127.0.0.1:{server.server_port}/ ; Ctrl+C stops the local editor',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
