import copy,json,tempfile,unittest,threading,urllib.request,urllib.error
from pathlib import Path
from http.server import HTTPServer
from digitizer import AxisCalibration,CalibrationError,digitize
from digitizer.detection import propose
from digitizer.gui import make_handler
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'examples/synthetic_data'
def config(name='linear'):return json.loads((DATA/(name+'_points.json')).read_text(encoding='utf-8'))

class DigitizerTests(unittest.TestCase):
    def measure(self,name,c=None):
        with tempfile.TemporaryDirectory() as t:return digitize(DATA/(name+'.png'),config(name) if c is None else c,t)
    def test_linear_and_independent_two_tick_interpolation(self):
        c=config();axis=AxisCalibration(c['segments']);actual=axis.value(285)
        independent=0+(530-285)/(530-130)*8
        self.assertAlmostEqual(actual,independent,12);self.assertAlmostEqual(self.measure('linear')[0]['mean'],4,12)
    def test_negative(self):self.assertLess(self.measure('negative')[0]['mean'],0)
    def test_nonzero_baseline(self):self.assertAlmostEqual(self.measure('nonzero')[0]['mean'],14,10)
    def test_log_and_independent_transform(self):
        axis=AxisCalibration(config('log')['segments']);self.assertAlmostEqual(axis.value(330),10,10);self.assertAlmostEqual(axis.value(230),10**1.5,10)
        row=self.measure('log')[0];self.assertNotAlmostEqual(row['error_upper'],row['error_lower'],6)
    def test_broken_axis_gap_and_separate_endpoints(self):
        axis=AxisCalibration(config('broken')['segments'])
        with self.assertRaises(CalibrationError):axis.value(345)
        self.assertAlmostEqual(axis.span(430,200,'low','high'),axis.value(200,'high')-axis.value(430,'low'),12)
    def test_sd_sem_labels_are_user_supplied(self):
        self.assertEqual(self.measure('linear')[0]['variance_type'],'SD');row=self.measure('broken')[0];self.assertEqual(row['variance_type'],'SEM');self.assertEqual(row['n'],9)
    def test_unknown_type_n_retained(self):
        c=config();c['groups'][0]['variance_type']='NR';c['groups'][0]['n']=None;row=self.measure('linear',c)[0];self.assertEqual(row['variance_type'],'NR');self.assertIsNone(row['n'])
    def test_asymmetric_endpoints_not_averaged(self):
        c=config();c['groups'][0]['lower_y']=350;c['groups'][0]['variance_type']='CI';r=self.measure('linear',c)[0];self.assertFalse(r['symmetric']);self.assertAlmostEqual(r['error_upper'],.5);self.assertAlmostEqual(r['error_lower'],.4)
    def test_unreadable(self):
        with self.assertRaises(ValueError):propose(DATA/'unreadable.png')
    def test_bracket_rejected_as_bar_top(self):
        result=propose(DATA/'bracket.png',[80,90,830,560],530);self.assertEqual(len(result['bar_candidates']),3);self.assertEqual(sorted(g['bar_y'] for g in result['bar_candidates']),[270,330,410])
    def test_error_cap_candidates(self):
        r=propose(DATA/'linear.png',[80,90,830,560],530)
        self.assertEqual(r['bar_candidates'][0]['upper_y'],305);self.assertEqual(r['bar_candidates'][0]['lower_y'],355)
    def test_manual_override_is_deterministic(self):
        c=config();c['groups'][0]['bar_y']=320;c['groups'][0]['upper_y']=295;c['groups'][0]['lower_y']=345
        self.assertEqual(self.measure('linear',c),self.measure('linear',c));self.assertAlmostEqual(self.measure('linear',c)[0]['mean'],4.2)
    def test_unconfirmed_rejected(self):
        c=config();c['groups'][0]['confirmed']=False
        with self.assertRaises(ValueError):self.measure('linear',c)
    def test_bad_tick_and_log_values(self):
        c=config();c['segments'][0]['ticks'][1]['pixel_y']=530
        with self.assertRaises(CalibrationError):AxisCalibration(c['segments'])
        with self.assertRaises(CalibrationError):AxisCalibration([dict(scale='log10',ticks=[dict(pixel_y=1,value=0),dict(pixel_y=2,value=1)])])
    def test_reversed_upper_rejected(self):
        c=config();c['groups'][0]['upper_y']=350
        with self.assertRaises(ValueError):self.measure('linear',c)
    def test_user_input_not_mutated(self):
        c=config();before=copy.deepcopy(c);self.measure('linear',c);self.assertEqual(c,before)
    def test_jpeg_tiff_and_original_coordinate_frame(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as td:
            for suffix in ['jpg','tiff']:
                p=Path(td)/('image.'+suffix);Image.open(DATA/'linear.png').save(p)
                r=digitize(p,config(),Path(td)/suffix);self.assertAlmostEqual(r[0]['mean'],4,10)
    def test_point_outside_panel_rejected(self):
        c=config();c['groups'][0]['upper_y']=85
        with self.assertRaises(ValueError):self.measure('linear',c)
    def test_local_editor_save_and_cross_origin_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            server=HTTPServer(('127.0.0.1',0),make_handler(DATA/'linear.png',config(),td));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();url=f'http://127.0.0.1:{server.server_port}'
            try:
                self.assertIn(b'Scientific figure point editor',urllib.request.urlopen(url).read())
                req=urllib.request.Request(url+'/save',data=json.dumps(config()).encode(),headers={'Content-Type':'application/json','Origin':url});self.assertTrue(json.loads(urllib.request.urlopen(req).read())['saved'])
                self.assertTrue((Path(td)/'overlay.png').exists())
                req=urllib.request.Request(url+'/save',data=json.dumps(config()).encode(),headers={'Origin':'https://another-site.invalid'})
                with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(req)
            finally:server.shutdown();server.server_close();thread.join()
if __name__=='__main__':unittest.main()
