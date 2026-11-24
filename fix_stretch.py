cat << 'EOF' > ~/gen_pro.py
import json, unittest.mock as m
m.patch("cv2.VideoCapture", return_value=m.Mock(read=m.Mock(return_value=(False, None)))).start()
import ar_hologram

jets = json.dumps([[n, p, e, [list(q) for q in f]] for n, (p, e, f) in ar_hologram.AIRCRAFT.items()])

html = f'''<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<script src="https://jsdelivr.net" crossorigin="anonymous"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box;user-select:none;-webkit-user-select:none}}
html,body{{width:100%;height:100%;background:#000;overflow:hidden;font-family:-apple-system,sans-serif}}
video,canvas{{position:fixed;top:0;left:0;width:100%;height:100%;object-fit:cover}}
#hud{{position:fixed;top:14px;left:14px;right:14px;display:flex;justify-content:space-between;align-items:center;color:#0ff;font-weight:700;font-size:14px;text-shadow:0 0 10px currentColor;z-index:10;pointer-events:none}}
#badge{{padding:4px 10px;border-radius:20px;border:1px solid currentColor;background:rgba(0,0,0,.5);font-size:12px}}
#bar{{position:fixed;bottom:20px;left:12px;right:12px;display:flex;gap:8px;z-index:10}}
button{{flex:1;padding:13px 6px;border:1.5px solid #0ff;background:rgba(0,15,25,.7);color:#0ff;font-weight:700;border-radius:12px;font-size:13px;backdrop-filter:blur(6px)}}
button:active{{transform:scale(.95)}}
</style></head><body>
<video id="v" autoplay playsinline muted></video>
<canvas id="c"></canvas>
<div id="hud"><span id="nm"></span><span id="badge">Loading AI Hand Tracker...</span></div>
<div id="bar">
  <button onclick="si=(si+9)%10;upd()">◀ Prev</button>
  <button onclick="ci=(ci+1)%6;upd()">Color</button>
  <button onclick="cam=!cam;startCam();upd()">Cam: <span id="cm">Front</span></button>
  <button onclick="si=(si+1)%10;upd()">Next ▶</button>
</div>
<script>
const JETS={jets},COLS=['#00ffff','#32ff32','#ff00ff','#3b82f6','#ffd700','#ff3b30'];
const v=document.getElementById('v'),c=document.getElementById('c'),ctx=c.getContext('2d'),badge=document.getElementById('badge');
let cam=true,stream=null,si=0,ci=0,sc=100,ax=0.42,ay=0,pd=0,lx=0,ly=0,dr=false;
let p1=null,p2=null,baseSpan=null,baseSc=null,aiReady=false,busy=false;

function startCam(){{
  if(stream)stream.getTracks().forEach(t=>t.stop());
  navigator.mediaDevices.getUserMedia({{video:{{facingMode:cam?'user':'environment',width:{{ideal:640}},height:{{ideal:480}}}},audio:false}})
  .then(s=>{{stream=s;v.srcObject=s;v.style.transform=cam?'scaleX(-1)':'none';}});
}}
startCam();

const upd=()=>{{
  const col=COLS.at(ci);
  document.getElementById('nm').textContent=JETS.at(si).at(0);
  document.getElementById('cm').textContent=cam?'Front':'Rear';
  document.getElementById('hud').style.color=col;
  document.querySelectorAll('button').forEach(b=>{{b.style.color=col;b.style.borderColor=col;}});
}};
upd();

// MediaPipe Skeletal Hand Tracking
const hands=new Hands({{locateFile:f=>`https://jsdelivr.net{{f}}`}});
hands.setOptions({{maxNumHands:2,modelComplexity:0,minDetectionConfidence:0.6,minTrackingConfidence:0.6}});
hands.onResults(res=>{{
  aiReady=true;
  const lms=res.multiHandLandmarks;
  if(lms&&lms.length===2){{
    // Landmark 8 = Index Finger Tip
    const hA=lms.at(0).at(8),hB=lms.at(1).at(8);
    const xA=(cam?(1-hA.x):hA.x)*c.width,yA=hA.y*c.height;
    const xB=(cam?(1-hB.x):hB.x)*c.width,yB=hB.y*c.height;
    const raw1=xA<xB?[xA,yA]:[xB,yB],raw2=xA<xB?[xB,yB]:[xA,yA];
    if(!p1){{p1=raw1;p2=raw2;baseSpan=Math.max(Math.hypot(p2.at(0)-p1.at(0),p2.at(1)-p1.at(1)),40);baseSc=sc;}}
    else{{
      p1=[p1.at(0)*0.6+raw1.at(0)*0.4,p1.at(1)*0.6+raw1.at(1)*0.4];
      p2=[p2.at(0)*0.6+raw2.at(0)*0.4,p2.at(1)*0.6+raw2.at(1)*0.4];
      const span=Math.hypot(p2.at(0)-p1.at(0),p2.at(1)-p1.at(1));
      sc=Math.max(35,Math.min(260,baseSc*(span/baseSpan)));
    }}
    badge.textContent='2 HANDS LOCKED • Stretch!';
  }}else{{
    p1=p2=baseSpan=null;
    badge.textContent=aiReady?'Show 2 Hands or Pinch Screen':'Loading AI Hand Tracker...';
  }}
}});

setInterval(async()=>{{
  if(!busy&&v.readyState>=2){{busy=true;try{{await hands.send({{image:v}});}}catch(e){{}}busy=false;}}
}},45);

// Touch Pinch & Drag Fallback
c.ontouchstart=e=>{{if(e.touches.length===2)pd=Math.hypot(e.touches.item(0).clientX-e.touches.item(1).clientX,e.touches.item(0).clientY-e.touches.item(1).clientY);else{{dr=true;lx=e.touches.item(0).clientX;ly=e.touches.item(0).clientY;}}}};
c.ontouchmove=e=>{{e.preventDefault();if(e.touches.length===2){{const d=Math.hypot(e.touches.item(0).clientX-e.touches.item(1).clientX,e.touches.item(0).clientY-e.touches.item(1).clientY);if(pd>0)sc=Math.max(35,Math.min(260,sc*(d/pd)));pd=d;}}else if(dr){{ay+=(e.touches.item(0).clientX-lx)*.012;ax+=(e.touches.item(0).clientY-ly)*.012;lx=e.touches.item(0).clientX;ly=e.touches.item(0).clientY;}}}};
c.ontouchend=()=>{{dr=false;pd=0;}};

function loop(){{
  c.width=window.innerWidth;c.height=window.innerHeight;
  ctx.clearRect(0,0,c.width,c.height);
  const col=COLS.at(ci);

  if(p1&&p2){{
    ctx.strokeStyle=col;ctx.lineWidth=3;ctx.shadowColor=col;ctx.shadowBlur=12;
    ctx.beginPath();ctx.moveTo(p1.at(0),p1.at(1));ctx.lineTo(p2.at(0),p2.at(1));ctx.stroke();
    [p1,p2].forEach(pt=>{{
      ctx.beginPath();ctx.arc(pt.at(0),pt.at(1),16,0,6.28);ctx.stroke();
      ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(pt.at(0),pt.at(1),5,0,6.28);ctx.fill();
    }});
    ctx.shadowBlur=0;
  }}

  if(!dr)ay+=0.015;
  const jet=JETS.at(si),pts=jet.at(1),edges=jet.at(2),polys=jet.at(3);
  const cx=c.width/2,cy=c.height/2,ca=Math.cos(ax),sa=Math.sin(ax),cb=Math.cos(ay),sb=Math.sin(ay);
  const p2d=pts.map(([x,y,z])=>{{
    const y1=y*ca-z*sa,z1=y*sa+z*ca,x2=x*cb+z1*sb,z2=-x*sb+z1*cb,f=4.2/(4.2+z2);
    return[cx+x2*sc*f,cy+y1*sc*f];
  }});

  ctx.fillStyle=col+'28';
  polys.forEach(q=>{{ctx.beginPath();q.forEach((i,k)=>k?ctx.lineTo(p2d.at(i).at(0),p2d.at(i).at(1)):ctx.moveTo(p2d.at(i).at(0),p2d.at(i).at(1)));ctx.closePath();ctx.fill();}});
  ctx.strokeStyle=col;ctx.lineWidth=4;ctx.shadowColor=col;ctx.shadowBlur=12;
  edges.forEach(([a,b])=>{{ctx.beginPath();ctx.moveTo(p2d.at(a).at(0),p2d.at(a).at(1));ctx.lineTo(p2d.at(b).at(0),p2d.at(b).at(1));ctx.stroke();}});
  ctx.strokeStyle='#fff';ctx.lineWidth=1;ctx.shadowBlur=0;
  edges.forEach(([a,b])=>{{ctx.beginPath();ctx.moveTo(p2d.at(a).at(0),p2d.at(a).at(1));ctx.lineTo(p2d.at(b).at(0),p2d.at(b).at(1));ctx.stroke();}});
  requestAnimationFrame(loop);
}}
loop();
</script></body></html>'''

app_code = f'''import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AR Aircraft Hologram", layout="wide")
st.markdown("""
<style>
  .block-container {{padding: 0 !important; max-width: 100% !important;}}
  header, footer, #MainMenu {{visibility: hidden;}}
  iframe {{position: fixed !important; inset: 0 !important; width: 100vw !important; height: 100vh !important; border: none !important;}}
</style>
""", unsafe_allow_html=True)

components.html({repr(html)}, height=800)
'''

open("app.py", "w").write(app_code)
open("index.html", "w").write(html)
print("Generated AI MediaPipe app.py and copied to clipboard!")
EOF
python3 ~/gen_pro.py && cat ~/app.py | pbcopy
