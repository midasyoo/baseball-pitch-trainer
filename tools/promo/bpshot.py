# -*- coding: utf-8 -*-
"""baseball-pitch-trainer 캡처 유틸 — CDP 세션을 열어두고 여러 장을 찍는다."""
import os, json, time, base64, subprocess, urllib.request, websocket
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
S = os.environ.get("PROMO_WORK", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_work"))
URL = 'file:///C:/Users/ADMIN/Antigravity/baseball-pitch-trainer/index.html'

class Session:
    def __init__(self, port=9470, w=1920, h=1080, tag='s'):
        self.proc = subprocess.Popen([CHROME,'--headless=new','--disable-gpu',
            '--use-angle=swiftshader','--enable-unsafe-swiftshader',
            '--remote-debugging-port=%d'%port,'--remote-allow-origins=*',
            '--user-data-dir='+os.path.join(S,'bpc_'+tag),'--hide-scrollbars',
            '--allow-file-access-from-files','--force-device-scale-factor=1','about:blank'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ws_url=None
        for _ in range(120):
            try:
                for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json'%port)):
                    if t.get('type')=='page': ws_url=t['webSocketDebuggerUrl']; break
                if ws_url: break
            except Exception: pass
            time.sleep(.25)
        if not ws_url: raise RuntimeError('CDP 접속 실패')
        self.ws = websocket.create_connection(ws_url, timeout=120, suppress_origin=True)
        self.i = 0
        self.cmd('Page.enable')
        self.cmd('Emulation.setDeviceMetricsOverride', width=w, height=h,
                 deviceScaleFactor=1, mobile=False, screenWidth=w, screenHeight=h)
    def cmd(self, m, **pr):
        self.i += 1
        self.ws.send(json.dumps({'id':self.i,'method':m,'params':pr}))
        while True:
            r = json.loads(self.ws.recv())
            if r.get('id') == self.i:
                if 'error' in r: raise RuntimeError(str(r['error'])[:300])
                return r.get('result', {})
    def goto(self, frag, wait=24):
        self.cmd('Page.navigate', url=URL + '#cap=1&' + frag)
        t0=time.time()
        while time.time()-t0 < wait:
            time.sleep(1.0)
            try:
                v = self.cmd('Runtime.evaluate', expression='!!(window.__CAP)', returnByValue=True)
                if v['result'].get('value'): break
            except Exception: pass
        time.sleep(3.0)
    def js(self, expr):
        return self.cmd('Runtime.evaluate', expression=expr, returnByValue=True)['result'].get('value')
    def shot(self, path):
        d = self.cmd('Page.captureScreenshot', format='png')['data']
        open(path,'wb').write(base64.b64decode(d))
        return os.path.getsize(path)
    def close(self):
        try: self.ws.close()
        except Exception: pass
        self.proc.terminate()
