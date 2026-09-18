"""Trust Report — clean standalone page served from the API."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
router = APIRouter(prefix="/trust-report", tags=["Public - Trust Report"])

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Trust Report | Trust Trigger Agency</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
<script src="https://cdn.tailwindcss.com"></script>
<style>
body{font-family:'Inter',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
.green1{background:linear-gradient(135deg,#064e3b,#065f46,#047857)}
.spinner{border:3px solid #e5e7eb;border-top:3px solid #14b8a6;border-radius:50%;width:32px;height:32px;animation:s .8s linear infinite}
@keyframes s{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
</style>
</head>
<body class="bg-emerald-50 text-zinc-800 antialiased">

<nav class="bg-black border-b border-zinc-800 h-14 flex items-center px-6">
<div class="max-w-5xl mx-auto w-full flex items-center justify-between">
<a href="/home" class="flex items-center gap-2 text-lg font-extrabold text-yellow-400"><span class="text-xl">🛡️</span> Trust Trigger Agency</a>
<a href="/home" class="rounded-lg bg-teal-500 px-3 py-1.5 text-xs font-semibold text-white">Get Free Snapshot →</a>
</div>
</nav>

<div class="green1 text-white py-16 px-6 text-center">
<p class="text-xs font-bold uppercase tracking-[.2em] text-teal-300 mb-2">The Trust Trigger Method™</p>
<h1 class="text-3xl sm:text-4xl font-extrabold">Trust Report</h1>
<p class="text-emerald-200 text-sm mt-2 max-w-xl mx-auto">5 trust pillars. 14 standards. See where your site wins trust and where it leaks.</p>
</div>

<div class="max-w-3xl mx-auto px-6 py-10">

<div id="step-form" class="max-w-md mx-auto">
<div class="rounded-xl border border-emerald-200 bg-white shadow p-5">
<p class="text-sm font-bold text-zinc-800 mb-3">Enter your details</p>
<input id="fn" type="text" placeholder="Business name" class="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm mb-2 focus:outline-none focus:ring-2 focus:ring-teal-500">
<input id="wu" type="text" placeholder="Website URL" class="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm mb-2 focus:outline-none focus:ring-2 focus:ring-teal-500">
<input id="em" type="email" placeholder="Your email" class="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-teal-500">
<button id="go" class="w-full rounded-lg bg-teal-500 px-4 py-2.5 text-sm font-bold text-white shadow hover:bg-teal-400">Generate Your Report →</button>
<p class="text-xs text-zinc-400 text-center mt-2">Free. No card.</p>
</div>
</div>

<div id="step-loading" class="hidden text-center py-10">
<div class="spinner mx-auto mb-3"></div>
<p class="text-sm font-semibold text-zinc-700">Scanning...</p>
</div>

<div id="step-results" class="hidden"></div>

<div id="step-error" class="hidden text-center py-10">
<p class="text-red-600 text-sm font-semibold mb-2">Something went wrong</p>
<p id="errmsg" class="text-zinc-500 text-xs mb-3"></p>
<button onclick="resetForm()" class="rounded-lg bg-zinc-200 px-4 py-2 text-xs font-medium">Try again</button>
</div>

</div>

<footer class="bg-zinc-900 text-zinc-400 py-8 px-6 text-center text-xs">
<p class="text-yellow-400">© 2025 Trust Trigger Agency™</p>
</footer>

<script>
var API = '';
function q(id){return document.getElementById(id);}

document.getElementById('go').addEventListener('click', function(){
  var n = q('fn').value.trim();
  var u = q('wu').value.trim();
  var e = q('em').value.trim();
  if(!n||!u||!e){ alert('Fill in all fields.'); return; }
  
  q('step-form').classList.add('hidden');
  q('step-error').classList.add('hidden');
  q('step-results').classList.add('hidden');
  q('step-loading').classList.remove('hidden');
  
  var x = new XMLHttpRequest();
  x.open('POST', API+'/api/v1/public/trust-snapshot', true);
  x.setRequestHeader('Content-Type','application/json');
  x.onload = function(){
    q('step-loading').classList.add('hidden');
    if(x.status==201||x.status==200){
      try {
        var d = JSON.parse(x.responseText);
        if(d.error){ showError(d.error); return; }
        render(d,n,u);
      } catch(e){ showError('Invalid response'); }
    } else { showError('Server error: '+x.status); }
  };
  x.onerror = function(){ showError('Network error'); };
  x.send(JSON.stringify({full_name:n,website:u,email:e}));
});

function showError(m){ q('errmsg').textContent=m; q('step-error').classList.remove('hidden'); }
function resetForm(){ q('step-error').classList.add('hidden'); q('step-form').classList.remove('hidden'); }

function gr(s){ if(s>=90)return'Excellent'; if(s>=75)return'Good'; if(s>=55)return'Average'; if(s>=35)return'Weak'; return'Critical'; }

function render(d,n,u){
  var sc = d.score||0;
  var g = gr(sc);
  var sum = {Excellent:'Strong trust engine. Visitors feel confident.',Good:'Building trust well. Minor gaps remain.',Average:'Losing enquiries. Gaps below cost you.',Weak:'Most visitors leave without contacting you.',Critical:'Site is actively repelling visitors.'};
  
  var isWP = d.is_wordpress||false;
  var pbadge = isWP ? '<div class="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-center text-xs font-semibold text-emerald-800 mb-4">✅ WordPress Site — We publish content directly to your site</div>'
    : '<div class="bg-amber-50 border border-amber-200 rounded-lg p-3 text-center text-xs font-semibold text-amber-800 mb-4">🔧 Custom Platform — We build you a new dedicated website</div>';
  
  var pills = d.pillars||[];
  var pl = {online_presence:'Online Presence',reputation:'Reputation',engagement:'Engagement',transparency:'Transparency',technical:'Technical'};
  var ph = '';
  pills.forEach(function(p){
    var pc = Math.round(p.percentage);
    var c = pc>=80?'#14b8a6':pc>=60?'#eab308':pc>=40?'#f97316':'#ef4444';
    ph += '<div class="bg-white border border-zinc-200 rounded-lg p-3"><div class="flex justify-between text-xs mb-1"><span class="font-medium">'+(pl[p.name]||p.label)+'</span><span class="font-bold" style="color:'+c+'">'+pc+'%</span></div><div class="h-2 bg-zinc-100 rounded-full"><div class="h-full rounded-full" style="width:'+pc+'%;background:'+c+'"></div></div></div>';
  });
  
  var stds = d.standards||[];
  var ok=[],bad=[];
  stds.forEach(function(s){
    var lb=s.name.replace(/([A-Z])/g,' $1').replace(/^./,function(x){return x.toUpperCase()}).trim();
    if(s.name==='Https')lb='HTTPS';
    if(s.name==='Cta')lb='Call-to-Action';
    if(s.name==='Faq')lb='FAQ';
    if(s.passed)ok.push(lb); else bad.push(lb);
  });
  
  var sh = '';
  if(ok.length) sh += '<p class="text-xs font-bold text-zinc-900 mb-2">✓ Passing ('+ok.length+'/'+stds.length+')</p><div class="flex flex-wrap gap-1 mb-3">'+ok.map(function(x){return '<span class="text-xs bg-emerald-100 text-emerald-800 px-2 py-1 rounded">'+x+'</span>'}).join('')+'</div>';
  if(bad.length) sh += '<p class="text-xs font-bold text-red-800 mb-2">✗ Missing ('+bad.length+'/'+stds.length+')</p><div class="flex flex-wrap gap-1">'+bad.map(function(x){return '<span class="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">'+x+'</span>'}).join('')+'</div>';
  
  var iss = d.issues||[];
  var ih = '';
  if(iss.length){
    ih = '<p class="text-xs font-bold text-zinc-900 mb-2">⚠ Issues Found</p>';
    iss.forEach(function(x){ ih += '<div class="flex gap-2 text-xs bg-red-50 border border-red-100 rounded-lg p-3 mb-2"><span class="text-red-500 shrink-0">⚠</span><div><p class="font-semibold text-zinc-900">'+x.title+'</p><p class="text-zinc-500 mt-0.5">'+x.detail+'</p></div></div>'; });
  }
  
  var now = new Date();
  var html = '<div class="rounded-xl border border-emerald-200 bg-white shadow p-5">'+pbadge;
  html += '<div class="flex items-center gap-4"><div class="relative w-24 h-24 shrink-0"><svg class="w-24 h-24 -rotate-90" viewBox="0 0 120 120"><circle cx="60" cy="60" r="52" fill="none" stroke="#e5e7eb" stroke-width="8"/><circle id="sc" cx="60" cy="60" r="52" fill="none" stroke="#14b8a6" stroke-width="8" stroke-dasharray="326.7" stroke-dashoffset="326.7"/></svg><div class="absolute inset-0 flex items-center justify-center"><span id="sn" class="text-3xl font-extrabold text-zinc-900">'+sc+'</span></div></div><div><p class="text-xs text-emerald-700 font-bold uppercase tracking-wider">Trust Score</p><h2 class="text-xl font-bold text-zinc-900">'+g+'</h2><p class="text-xs text-zinc-500 mt-0.5">'+n+'</p><p class="text-xs text-zinc-400 break-all">'+u+'</p></div></div></div>';
  if(ph) html += '<div class="rounded-xl border border-zinc-200 bg-white shadow p-5 mt-4"><p class="text-xs font-bold text-zinc-900 mb-3">Trust Pillars</p><div class="grid grid-cols-2 gap-3">'+ph+'</div></div>';
  if(sh) html += '<div class="rounded-xl border border-zinc-200 bg-emerald-50 shadow p-5 mt-4">'+sh+'</div>';
  if(ih) html += '<div class="rounded-xl border border-red-200 bg-red-50 shadow p-5 mt-4">'+ih+'</div>';
  html += '<div class="text-center mt-6"><div class="rounded-xl border-2 border-teal-500 bg-white shadow p-6"><p class="text-sm font-bold text-zinc-900 mb-2">Want us to fix these gaps?</p><a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone" class="inline-block rounded-lg bg-teal-500 px-5 py-2.5 text-sm font-bold text-white shadow hover:bg-teal-400">Book Your Free Review →</a></div></div>';
  
  q('step-results').innerHTML = html;
  q('step-results').classList.remove('hidden');
  
  setTimeout(function(){
    var circ = document.getElementById('sc');
    if(circ) circ.style.strokeDashoffset = 326.7 - (sc/100)*326.7;
  }, 200);
}

</script>
</body>
</html>"""

@router.get("", response_class=HTMLResponse)
async def get_page():
    return PAGE

@router.get("/", response_class=HTMLResponse)
async def get_page_root():
    return PAGE
