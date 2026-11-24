import streamlit as st, streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.markdown("<style>.block-container{padding:0!important;max-width:100%!important}header,footer,#MainMenu{visibility:hidden}iframe{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;border:none!important}</style>", unsafe_allow_html=True)

HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"><style>
*{margin:0;padding:0;box-sizing:border-box;user-select:none;-webkit-user-select:none}html,body{width:100%;height:100%;background:#050a10;overflow:hidden;font-family:-apple-system,sans-serif}
video,canvas{position:fixed;inset:0;width:100%;height:100%;object-fit:cover}
#hud{position:fixed;top:14px;left:14px;right:14px;display:flex;justify-content:space-between;align-items:center;color:#0ff;font-weight:700;font-size:14px;text-shadow:0 0 8px currentColor;z-index:10;pointer-events:none}
#info{padding:4px 10px;border-radius:16px;border:1px solid currentColor;background:rgba(0,0,0,.65);font-size:12px}
#pad{position:fixed;bottom:16px;left:12px;right:12px;display:flex;flex-direction:column;gap:8px;z-index:10}
.row{display:flex;gap:8px}
button{flex:1;padding:13px 4px;border:1.5px solid #0ff;background:rgba(0,15,25,.78);color:#0ff;font-weight:700;border-radius:12px;font-size:13px;backdrop-filter:blur(4px)}
button:active{transform:scale(.94);background:rgba(0,255,255,.25)}
</style></head><body><video id="v" autoplay playsinline muted></video><canvas id="c"></canvas>
<div id="hud"><span id="nm"></span><span id="info">Size: 105</span></div>
<div id="pad">
  <div class="row">
    <button onclick="sc=Math.max(30,sc-18);upd()">Size −</button>
    <button onclick="sc=Math.min(290,sc+18);upd()">Size +</button>
    <button onclick="auto=!auto;upd()" id="ab">Spin: ON</button>
    <button onclick="ax=.42;ay=0;sc=105;upd()">Reset</button>
  </div>
  <div class="row">
    <button onclick="auto=false;ay-=.35;upd()">◀ Yaw</button>
    <button onclick="auto=false;ay+=.35;upd()">Yaw ▶</button>
    <button onclick="ax=Math.max(-1.4,ax-.25);upd()">Tilt ▲</button>
    <button onclick="ax=Math.min(1.4,ax+.25);upd()">Tilt ▼</button>
  </div>
  <div class="row">
    <button onclick="si=(si+9)%10;upd()">◀ Jet</button>
    <button onclick="ci=(ci+1)%6;upd()">Color</button>
    <button onclick="cam=!cam;startCam();upd()">Cam: <span id="cm">Front</span></button>
    <button onclick="si=(si+1)%10;upd()">Jet ▶</button>
  </div>
</div>
<script>
const build=(p,e,f,sym)=>{const pts=p.map(a=>[...a]),mp={};sym.forEach(i=>{mp[i]=pts.length;pts.push([-p.at(i).at(0),p.at(i).at(1),p.at(i).at(2)]);});const m=i=>mp[i]??i;return{pts,edges:[...e,...e.map(([a,b])=>[m(a),m(b)])],polys:[...f,...f.map(q=>q.map(m))]};};
const JP=[[0,.02,-2.1],[0,-.09,-1.45],[0,-.28,-.95],[0,-.24,-.25],[0,-.12,.45],[0,-.05,1.4],[0,.11,-1.35],[0,.14,-.1],[0,.12,1.4],[.24,.01,-1.25],[.38,-.02,-.5],[.42,-.02,.75],[.34,0,1.45],[.22,.12,-.5],[.28,.11,1.45],[1.68,.02,.48],[1.58,.02,.82],[.42,0,.88],[.92,.02,1.45],[.38,.01,1.52],[.58,-.64,1.35],[.48,-.64,1.6],[.36,-.03,1.42]];
const JE=[[0,1],[1,2],[2,3],[3,4],[4,5],[0,6],[6,7],[7,8],[0,9],[9,10],[10,11],[11,12],[9,6],[10,13],[13,14],[14,12],[13,7],[14,8],[1,9],[2,10],[3,10],[4,11],[5,12],[10,15],[15,16],[16,17],[17,11],[11,18],[18,19],[19,12],[11,20],[20,21],[21,22],[22,12],[5,8]];
const JF=[[0,1,9],[1,2,10,9],[2,3,10],[3,4,11,10],[4,5,12,11],[10,15,16,17,11],[11,18,19,12],[11,20,21,22,12],[9,10,13,6]],S23=[9,10,11,12,13,14,15,16,17,18,19,20,21,22];
const mod=(sx,sy,sz,tx=0)=>JP.map(([x,y,z],i)=>[(i===20||i===21?x+tx:x)*sx,y*sy,z*sz]);
const BP=[[0,.04,-1.25],[0,-.22,-.65],[0,-.16,.15],[0,-.04,.85],[0,.12,-.5],[0,.1,.75],[.38,-.12,-.45],[.45,-.05,.25],[2.2,.04,.55],[2,.04,.78],[1.38,.02,.52],[.78,0,.88],[.38,0,.62]];
const BE=[[0,1],[1,2],[2,3],[0,4],[4,5],[5,3],[0,6],[1,6],[6,7],[2,7],[6,4],[7,5],[0,8],[8,9],[9,10],[10,11],[11,12],[12,3],[6,10],[7,11],[7,12]],BF=[[0,1,6],[1,2,7,6],[2,3,12,7],[0,6,8,9,10],[6,7,11,10],[7,12,11],[0,4,6]];
const JETS=[
  {name:"1. F-22 Raptor",...build(JP,JE,JF,S23)},{name:"2. F-35 Lightning II",...build(mod(.9,1.15,.9,.06),JE,JF,S23)},
  {name:"3. B-2 Spirit",...build(BP,BE,BF,[6,7,8,9,10,11,12])},{name:"4. B-21 Raider",...build(BP.map(([x,y,z])=>[x*.94,y*.88,z*.86]),BE,BF,[6,7,8,9,10,11,12])},
  {name:"5. F-15 Eagle",...build(mod(.96,1,.98,-.22),JE,JF,S23)},{name:"6. F-16 Falcon",...build(mod(.84,1.05,.94,-.52),JE,JF,S23)},
  {name:"7. F/A-18 Hornet",...build(mod(.95,.95,.98,.08),JE,JF,S23)},{name:"8. B-1B Lancer",...build(mod(1.12,.82,1.22,-.52),JE,JF,S23)},
  {name:"9. AH-64 Apache",...build(mod(.7,1.2,.85,-.4),JE,JF,S23)},{name:"10. A-10 Thunderbolt",...build(mod(1.25,1.05,.88,-.1),JE,JF,S23)}
];
const COLS=['#00ffff','#32ff32','#ff00ff','#3b82f6','#ffd700','#ff3b30'],v=document.getElementById('v'),c=document.getElementById('c'),ctx=c.getContext('2d');
let cam=true,st=null,si=0,ci=0,sc=105,ax=.42,ay=0,auto=true,pd=0,lx=0,ly=0,dr=false;
function upd(){const col=COLS.at(ci);document.getElementById('nm').textContent=JETS.at(si).name;document.getElementById('info').textContent=`Size: ${Math.round(sc)}`;document.getElementById('ab').textContent=auto?'Spin: ON':'Spin: OFF';document.getElementById('cm').textContent=cam?'Front':'Rear';document.getElementById('hud').style.color=col;document.querySelectorAll('button').forEach(b=>{b.style.color=col;b.style.borderColor=col;});}
function startCam(){if(st)st.getTracks().forEach(t=>t.stop());navigator.mediaDevices?.getUserMedia({video:{facingMode:cam?'user':'environment'},audio:false}).then(s=>{st=s;v.srcObject=s;v.style.transform=cam?'scaleX(-1)':'none';}).catch(()=>{});}
upd();startCam();
c.ontouchstart=e=>{if(e.touches.length===2)pd=Math.hypot(e.touches.item(0).clientX-e.touches.item(1).clientX,e.touches.item(0).clientY-e.touches.item(1).clientY);else{dr=true;lx=e.touches.item(0).clientX;ly=e.touches.item(0).clientY;}};
c.ontouchmove=e=>{e.preventDefault();if(e.touches.length===2){const d=Math.hypot(e.touches.item(0).clientX-e.touches.item(1).clientX,e.touches.item(0).clientY-e.touches.item(1).clientY);if(pd>0){sc=Math.max(30,Math.min(290,sc*(d/pd)));upd();}pd=d;}else if(dr){auto=false;ay+=(e.touches.item(0).clientX-lx)*.012;ax=Math.max(-1.4,Math.min(1.4,ax+(e.touches.item(0).clientY-ly)*.012));lx=e.touches.item(0).clientX;ly=e.touches.item(0).clientY;upd();}};c.ontouchend=()=>{dr=false;pd=0;};
function loop(){const W=innerWidth||360,H=innerHeight||640;if(c.width!==W)c.width=W;if(c.height!==H)c.height=H;ctx.clearRect(0,0,W,H);
if(auto&&!dr)ay+=.014;const col=COLS.at(ci),jet=JETS.at(si),cx=W/2,cy=H*0.42,ca=Math.cos(ax),sa=Math.sin(ax),cb=Math.cos(ay),sb=Math.sin(ay);
const p2=jet.pts.map(([x,y,z])=>{const y1=y*ca-z*sa,z1=y*sa+z*ca,x2=x*cb+z1*sb,z2=-x*sb+z1*cb,f=4.2/(4.2+z2);return[cx+x2*sc*f,cy+y1*sc*f];});
ctx.fillStyle=col+'28';jet.polys.forEach(q=>{ctx.beginPath();q.forEach((i,k)=>k?ctx.lineTo(p2.at(i).at(0),p2.at(i).at(1)):ctx.moveTo(p2.at(i).at(0),p2.at(i).at(1)));ctx.closePath();ctx.fill();});
ctx.strokeStyle=col;ctx.lineWidth=4;ctx.shadowColor=col;ctx.shadowBlur=12;jet.edges.forEach(([a,b])=>{ctx.beginPath();ctx.moveTo(p2.at(a).at(0),p2.at(a).at(1));ctx.lineTo(p2.at(b).at(0),p2.at(b).at(1));ctx.stroke();});
ctx.strokeStyle='#fff';ctx.lineWidth=1;ctx.shadowBlur=0;jet.edges.forEach(([a,b])=>{ctx.beginPath();ctx.moveTo(p2.at(a).at(0),p2.at(a).at(1));ctx.lineTo(p2.at(b).at(0),p2.at(b).at(1));ctx.stroke();});
requestAnimationFrame(loop);}loop();</script></body></html>"""

components.html(HTML, height=800)

