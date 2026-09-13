"""Snapshot scan endpoint — embedded in the homepage."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
router = APIRouter(prefix="/embed-snapshot", tags=["Public - Embed Snapshot"])

SNAPSHOT_EMBED_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,Arial,sans-serif;background:transparent;color:white}
.flex{display:flex}.flex-col{flex-direction:column}.gap-3{gap:12px}
.text-center{text-align:center}.rounded-xl{border-radius:12px}.rounded-2xl{border-radius:16px}
.border{border:1px solid #52525b}.border-2{border-width:2px}.border-zinc-700{border-color:#3f3f46}
.border-red-800{border-color:#991b1b}.border-teal-500{border-color:#14b8a6}
.bg-zinc-800{background:#27272a}.bg-zinc-900{background:#18181b}.bg-red-950{background:#450a0a}
.bg-black{background:black}.bg-teal-500{background:#14b8a6}.bg-zinc-700{background:#3f3f46}
.text-white{color:white}.text-zinc-300{color:#d4d4d8}.text-zinc-400{color:#a1a1aa}
.text-zinc-500{color:#71717a}.text-teal-400{color:#2dd4bf}.text-red-400{color:#f87171}
.text-red-300{color:#fca5a5}.text-green-400{color:#4ade80}.text-yellow-400{color:#facc15}
.text-orange-400{color:#fb923c}.font-bold{font-weight:700}.font-semibold{font-weight:600}
.font-medium{font-weight:500}.text-sm{font-size:14px}.text-base{font-size:16px}
.text-lg{font-size:18px}.text-7xl{font-size:72px}.text-2xl{font-size:24px}
.tracking-wider{letter-spacing:0.05em}.uppercase{text-transform:uppercase}
.px-5{padding-left:20px;padding-right:20px}.px-6{padding-left:24px;padding-right:24px}
.px-8{padding-left:32px;padding-right:32px}.p-8{padding:32px}.py-3\\.5{padding-top:14px;padding-bottom:14px}
.py-6{padding-top:24px;padding-bottom:24px}.w-full{width:100%}.flex-1{flex:1}
.h-3{height:12px}.rounded-full{border-radius:999px}.overflow-hidden{overflow:hidden}
.grid{display:grid}.gap-8{gap:32px}.space-y-2>+{margin-top:8px}.mb-1{margin-bottom:4px}
.mb-3{margin-bottom:12px}.mb-6{margin-bottom:24px}.mb-4{margin-bottom:16px}.mt-6{margin-top:24px}
.mt-8{margin-top:32px}.mt-12{margin-top:48px}
.justify-between{justify-content:space-between}.items-center{align-items:center}
.whitespace-nowrap{white-space:nowrap}.no-underline{text-decoration:none}
.inline-flex{display:inline-flex}.gap-2{gap:8px}
.hover\\:bg-teal-400:hover{background:#2dd4bf}.transition{transition:all .2s}
.shadow-xl{box-shadow:0 20px 25px -5px rgba(0,0,0,.1)}
@media(min-width:640px){.sm\\:flex-row{flex-direction:row}.sm\\:grid-cols-3{grid-template-columns:1fr 1fr 1fr}.sm\\:col-span-2{grid-column:span 2}}
</style>
</head>
<body>
<div class="bg-black rounded-2xl p-8 text-center">
<div class="flex flex-col sm:flex-row gap-3 mb-4">
<input id="urlInput" type="text" placeholder="yourpractice.co.uk" class="flex-1 rounded-xl border border-zinc-600 bg-zinc-900 px-5 py-3.5 text-white">
<button onclick="scan()" id="scanBtn" class="rounded-xl bg-teal-500 px-6 py-3.5 text-base font-bold text-white whitespace-nowrap">Get My Score →</button>
</div>
<div id="status" class="text-sm text-zinc-500"></div>
<div id="result" class="hidden mt-6 text-left"></div>
<div id="cta" class="hidden mt-8 text-center">
<p class="text-2xl font-bold text-white mb-6">Surprised with your score?</p>
<p class="text-lg text-zinc-300 mb-8">Let's go through your full report together and we'll show you how to improve your score quickly.</p>
<a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone?month=2026-09" class="inline-flex items-center gap-2 rounded-xl bg-teal-500 px-8 py-4 text-lg font-bold text-white shadow-xl hover:bg-teal-400 transition no-underline">Book A Free 20 Minute Review →</a>
</div>
</div>
<script>
async function scan(){
  var u=document.getElementById('urlInput').value.trim();
  var s=document.getElementById('status');
  var b=document.getElementById('scanBtn');
  var r=document.getElementById('result');
  var c=document.getElementById('cta');
  if(!u){s.textContent='Please enter a URL.';return;}
  if(!u.startsWith('http')) u='https://'+u;
  s.textContent=''; b.disabled=true; b.textContent='Scanning...';
  try{
    var res=await fetch('/api/v1/public/trust-snapshot',{
      method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({full_name:'Your Business',website:u,email:'s_'+Date.now()+'@t.com'})
    });
    var d=await res.json();
    b.disabled=false; b.textContent='Get My Score →';
    if(!d.score){s.textContent='Could not scan.';return;}
    s.textContent='';
    var pills={}; if(d.pillars) d.pillars.forEach(function(p){pills[p.label]=Math.round(p.percentage);});
    var labs=['Online Presence','Reputation','Engagement','Transparency','Technical Health'];
    var bars='';
    labs.forEach(function(l){
      var v=pills[l]||0;
      var cl=v>=80?'#22c55e':v>=60?'#eab308':v>=40?'#f97316':'#ef4444';
      var tc=v>=80?'text-green-400':v>=60?'text-yellow-400':v>=40?'text-orange-400':'text-red-400';
      bars+='<div><div class="flex justify-between text-sm font-semibold mb-1"><span class="text-zinc-300">'+l+'</span><span class="'+tc+'">'+v+'</span></div><div class="h-3 rounded-full bg-zinc-700 overflow-hidden"><div class="h-full rounded-full" style="width:'+v+'%;background:'+cl+'"></div></div></div>';
    });
    var g=d.grade?d.grade.charAt(0).toUpperCase()+d.grade.slice(1):'Strong';
    var iss='';
    if(d.issues&&d.issues.length){
      iss='<div class="mt-6 bg-red-950 border border-red-800 rounded-2xl p-6"><p class="text-lg font-bold text-red-400 mb-3">⚠️ Top Issues</p>';
      d.issues.slice(0,3).forEach(function(x,i){iss+='<div class="text-red-300 font-medium mb-1">#'+(i+1)+' '+x.title+'</div>';});
      iss+='</div>';
    }
    r.innerHTML='<div class="rounded-2xl border-2 border-teal-500 bg-zinc-900 p-8"><div class="grid grid-cols-1 sm:grid-cols-3 gap-8"><div class="text-center"><p class="text-sm font-bold uppercase tracking-wider text-teal-400 mb-1">Your Snapshot</p><p class="text-7xl font-extrabold text-white mb-1">'+d.score+'</p><p class="text-base font-semibold text-teal-400 mb-4">'+g+'</p></div><div class="sm:col-span-2 space-y-4">'+bars+'</div></div>'+iss+'</div>';
    r.classList.remove('hidden'); c.classList.remove('hidden');
  }catch(e){
    b.disabled=false; b.textContent='Get My Score →';
    s.textContent='Server error. Try again.';
  }
}
</script>
</body>
</html>"""

@router.get("", response_class=HTMLResponse)
async def get_embed_snapshot():
    return SNAPSHOT_EMBED_PAGE

@router.get("/", response_class=HTMLResponse)
async def get_embed_snapshot_root():
    return SNAPSHOT_EMBED_PAGE
