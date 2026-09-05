/* 야구 투구 트레이너 — 집 와이파이 서버
   사용법: 이 폴더에서  node serve.js  실행 → 아이폰(같은 와이파이)에서 표시된 주소 접속 */
const http = require('http'), fs = require('fs'), path = require('path'), os = require('os');
const root = __dirname, port = 8770;
const MIME = {
  '.html':'text/html; charset=utf-8', '.js':'text/javascript', '.mjs':'text/javascript',
  '.glb':'model/gltf-binary', '.png':'image/png', '.jpg':'image/jpeg', '.md':'text/markdown; charset=utf-8'
};
http.createServer((req, res)=>{
  let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if(p === '/') p = '/index.html';
  const f = path.normalize(path.join(root, p));
  if(!f.startsWith(root)){ res.statusCode = 403; return res.end('forbidden'); }
  fs.readFile(f, (e, b)=>{
    if(e){ res.statusCode = 404; res.end('not found'); }
    else { res.setHeader('Content-Type', MIME[path.extname(f).toLowerCase()] || 'application/octet-stream'); res.end(b); }
  });
}).listen(port, ()=>{
  const ips = [];
  for(const arr of Object.values(os.networkInterfaces()))
    for(const i of arr || []) if(i.family === 'IPv4' && !i.internal) ips.push(i.address);
  console.log('\n== Baseball Pitch Trainer server is running! ==\n');
  console.log('  On this PC:                http://localhost:' + port);
  for(const ip of ips)
    console.log('  On iPhone (same Wi-Fi):    http://' + ip + ':' + port);
  console.log('\n  * iPhone Safari > Share > "Add to Home Screen" = use like an app');
  console.log('  * Stop: Ctrl+C\n');
});
