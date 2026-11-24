import json, unittest.mock as m
m.patch("cv2.VideoCapture", return_value=m.Mock(read=m.Mock(return_value=(False, None)))).start()
import ar_hologram
jets = json.dumps([[n, p, e, [list(q) for q in f]] for n, (p, e, f) in ar_hologram.AIRCRAFT.items()])

html = f'''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"><title>AR Aircraft Hologram</title><style>
*{{margin:0;padding:0;user-select:none;-webkit-user-select:none}}body{{background:#000;overflow:hidden;font-family:-apple-system,sans-serif}}video,canvas{{position:fixed;inset:0;width:100vw;height:100vh;object-fit:cover}}
#hud{{position:fixed;top:16px;left:16px;right:16px;display:flex;justify-content:space-between;color:#0ff;font-weight:700;font-size:14px;text-shadow:0 0 8px currentColor}}
#bar{{position:fixed;bottom:24px;left:12px;right:12px;display:flex;gap:8px}}button{{flex:1;padding:13px 6px;border:1.5px solid #0ff;background:rgba(0,15,25,.65);color:#0ff;font-weight:700;border-radius:12px;font-size:13px}}
</style></head><body><video id="v" autoplay playsinline muted></video><canvas id="c"></canvas><canvas id="tc" width="160" height="120" style="display:none"></canvas>
<div id="hud"><span id="nm"></span><span id="st">Wave Both Hands or Pinch</span></div>
<div id="bar"><button onclick="si=(si+9)%10;upd()">◀ Prev</button><button onclick="ci=(ci+1)%6;upd()">Color</button><button onclick="cam=!cam;start();upd()">Cam: <span id="cm">Front</span></button><button onclick="si=(si+1)%10;upd()">Next ▶</button></div>
<script>
const JETS={jets},COLS=['#00ffff','#32ff32','#ff00ff','#3b82f6','#ffd700','#ff3b30'],v=document.getElementById('v'),c=document.getElementById('c'),ctx=c.getContext('2d'),tc=document.getElementById('tc'),tctx=tc.getContext('2d',{{willReadFrequently:true}});
let cam=true,st=null,si=0,ci=0,sc=95,ax=.42,ay=0,pd=0,lx=0,ly=0,dr=false,sh1=null,sh2=null,aspan=null,asc=null,hold=0,prev=null;
function start(){{if(st)st.getTracks().forEach(t=>t.stop());prev=null;navigator.mediaDevices.getUserMedia({{video:{{facingMode:cam?'user':'environment'}},audio:false}}).then(s=>{{st=s;v.srcObject=s;v.style.transform=cam?'scaleX(-1)':'none';}});}}start();
const upd=()=>{{const col=COLS[ci];document.getElementById('nm').textContent=JETS.at(si).at(0);document.getElementById('cm').textContent=cam?'Front':'Rear';document.getElementById('hud').style.color=col;document.querySelectorAll('button').forEach(b=>{{b.style.color=col;b.style.borderColor=col;}});}};upd();
c.ontouchstart=e=>{{if(e.touches.length===2)pd=Math.hypot(e.touches.item(0).clientX-e.touches.item(1).clientX,e.touches.item(0).clientY-e.touches.item(1).clientY);else{{dr=true;lx=e.touches.item(0).clientX;ly=e.touches.item(0).clientY;}}}};
c.ontouchmove=e=>{{e.preventDefault();if(e.touches.length===2){{const d=Math.hypot(e.touches.item(0).clientX-e.touches.item(1).clientX,e.touches.item(0).clientY-e.touches.item(1).clientY);if(pd>0)sc=Math.max(35,Math.min(240,sc*(d/pd)));pd=d;}}else if(dr){{ay+=(e.touches.item(0).clientX-lx)*.012;ax+=(e.touches.item(0).clientY-ly)*.012;lx=e.touches.item(0).clientX;ly=e.touches.item(0).clientY;}}}};
c.ontouchend=()=>{{dr=false;pd=0;}};
function track(){{if(v.readyState<2)return null;tctx.drawImage(v,0,0,160,120);const d=tctx.getImageData(0,0,160,120).data;let lx=0,ly=0,lc=0,rx=0,ry=0,rc=0;
for(let y=8;y<116;y+=2)for(let x=4;x<156;x+=2){{if(x>58&&x<102&&y<78)continue;const i=(y*160+x)*4,R=d.at(i),G=d.at(i+1),B=d.at(i+2);
const Y=.299*R+.587*G+.114*B,Cr=128+.5*R-.419*G-.081*B,Cb=128-.169*R-.331*G+.5*B;
const skin=(Cr>128&&Cr<185&&Cb>70&&Cb<135&&Y>30);
const diff=prev?(Math.abs(R-prev.at(i))+Math.abs(G-prev.at(i+1))+Math.abs(B-prev.at(i+2))):0;
if(skin||diff>55){{const mx=cam?160-x:x,w=diff>55?2:1;if(mx<74){{lx+=mx*w;ly+=y*w;lc+=w;}}else if(mx>86){{rx+=mx*w;ry+=y*w;rc+=w;}}}}}}
prev=new Uint8ClampedArray(d);
return(lc>12&&rc>12)?[[(lx/lc)*(c.width/160),(ly/lc)*(c.height/120)],[(rx/rc)*(c.width/160),(ry/rc)*(c.height/120)]]:null;}}
function loop(){{c.width=innerWidth;c.height=innerHeight;ctx.clearRect(0,0,c.width,c.height);const col=COLS.at(ci),h=track();
if(h){{hold++;const h1=h.at(0),h2=h.at(1);if(!sh1){{sh1=h1;sh2=h2;}}else{{sh1=[sh1.at(0)*.65+h1.at(0)*.35,sh1.at(1)*.65+h1.at(1)*.35];sh2=[sh2.at(0)*.65+h2.at(0)*.35,sh2.at(1)*.65+h2.at(1)*.35];}}
const sp=Math.hypot(sh2.at(0)-sh1.at(0),sh2.at(1)-sh1.at(1));
if(hold===3){{aspan=Math.max(sp,40);asc=sc;}}else if(hold>3&&aspan){{const dl=sp-aspan;if(Math.abs(dl)>12)sc=Math.max(35,Math.min(250,sc*.65+(asc*((aspan+dl-Math.sign(dl)*12)/aspan))*.35));}}
ctx.strokeStyle=hold>=3?col:'#888';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(sh1.at(0),sh1.at(1));ctx.lineTo(sh2.at(0),sh2.at(1));ctx.stroke();
[sh1,sh2].forEach(p=>{{ctx.beginPath();ctx.arc(p.at(0),p.at(1),18,0,6.28);ctx.stroke();}});
document.getElementById('st').textContent=hold>=3?'LOCKED: Pull Arms Apart!':'Locking...';}}else{{hold=0;sh1=sh2=aspan=null;document.getElementById('st').textContent='Wave Both Hands or Pinch';}}
if(!dr)ay+=.015;const jet=JETS.at(si),pts=jet.at(1),edges=jet.at(2),polys=jet.at(3),cx=c.width/2,cy=c.height/2,ca=Math.cos(ax),sa=Math.sin(ax),cb=Math.cos(ay),sb=Math.sin(ay);
const p2=pts.map(([x,y,z])=>{{const y1=y*ca-z*sa,z1=y*sa+z*ca,x2=x*cb+z1*sb,z2=-x*sb+z1*cb,f=4.2/(4.2+z2);return[cx+x2*sc*f,cy+y1*sc*f];}});
ctx.fillStyle=col+'28';polys.forEach(q=>{{ctx.beginPath();q.forEach((i,k)=>k?ctx.lineTo(p2.at(i).at(0),p2.at(i).at(1)):ctx.moveTo(p2.at(i).at(0),p2.at(i).at(1)));ctx.closePath();ctx.fill();}});
ctx.strokeStyle=col;ctx.lineWidth=4;ctx.shadowColor=col;ctx.shadowBlur=12;edges.forEach(([a,b])=>{{ctx.beginPath();ctx.moveTo(p2.at(a).at(0),p2.at(a).at(1));ctx.lineTo(p2.at(b).at(0),p2.at(b).at(1));ctx.stroke();}});
ctx.strokeStyle='#fff';ctx.lineWidth=1;ctx.shadowBlur=0;edges.forEach(([a,b])=>{{ctx.beginPath();ctx.moveTo(p2.at(a).at(0),p2.at(a).at(1));ctx.lineTo(p2.at(b).at(0),p2.at(b).at(1));ctx.stroke();}});
requestAnimationFrame(loop);}}loop();</script></body></html>'''

open("index.html", "w").write(html)
open("app.py", "w").write(f'''import streamlit as st, streamlit.components.v1 as components\nst.set_page_config(page_title="AR Aircraft Hologram", layout="wide")\nst.markdown("<style>.block-container{{padding:0;max-width:100%}}header,footer{{visibility:hidden}}</style>", unsafe_allow_html=True)\ncomponents.html({repr(html)}, height=900)\n''')
print("Fixed index.html and app.py!")
