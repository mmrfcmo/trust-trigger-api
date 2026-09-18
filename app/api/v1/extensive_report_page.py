"""Extensive Trust Report — served by the API with full JS support."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
router = APIRouter(prefix="/extensive-report", tags=["Public - Extensive Report"])
PAGE = """<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Extensive Trust Report | Trust Trigger Agency</title>
<meta name="description" content="Get your full Extensive Trust Report. 5 pillars. 14 standards. Every gap and fix prioritised.">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ctext y='26' font-size='26'%3E🛡️%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap">
<script src="https://cdn.tailwindcss.com"></script>
<style>
body{font-family:'Inter',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
.green1{background:linear-gradient(135deg,#064e3b,#065f46,#047857)}
</style>
</head>
<body class="antialiased bg-emerald-50 text-zinc-800">
<nav class="bg-black border-b border-zinc-800 fixed top-0 left-0 right-0 z-50 h-16 flex items-center px-6">
<div class="max-w-6xl mx-auto w-full flex items-center justify-between">
<a href="https://trust-trigger-api.onrender.com/home" class="flex items-center gap-2 text-xl font-extrabold text-yellow-400"><span class="text-2xl">🛡️</span> Trust Trigger Agency</a>
<a href="https://trust-trigger-api.onrender.com/home" class="rounded-lg bg-teal-500 px-4 py-2 text-xs font-semibold text-white hover:bg-teal-400">Get Free Snapshot &rarr;</a>
</div>
</nav>

<div class="h-16"></div>

<div class="green1 text-white py-20 px-6">
<div class="max-w-4xl mx-auto text-center">
<p class="text-sm font-bold uppercase tracking-[.2em] text-teal-300 mb-4">The Trust Trigger Method&trade;</p>
<h1 class="text-4xl sm:text-5xl font-extrabold tracking-tight mb-4">Extensive Trust Report</h1>
<p class="text-lg text-emerald-200 max-w-2xl mx-auto">Enter any business website. We analyse it across <strong class="text-white">5 trust pillars</strong> and <strong class="text-white">14 standards</strong>.</p>
</div>
</div>

<div class="max-w-4xl mx-auto px-6 py-12">

<div id="inputSection" class="max-w-lg mx-auto">
<div class="rounded-2xl border border-emerald-200 bg-white shadow-xl p-6">
<div class="space-y-4">
<div><label class="block text-sm font-bold text-zinc-800 mb-1">Business Name</label><input id="fullName" type="text" placeholder="e.g. Ivy Dentistry" class="w-full rounded-xl border border-emerald-300 px-4 py-3 text-base focus:outline-none focus:ring-2 focus:ring-teal-500"></div>
<div><label class="block text-sm font-bold text-zinc-800 mb-1">Website URL</label><input id="website" type="text" placeholder="e.g. ivydentistry.co.uk" class="w-full rounded-xl border border-emerald-300 px-4 py-3 text-base focus:outline-none focus:ring-2 focus:ring-teal-500"></div>
<div><label class="block text-sm font-bold text-zinc-800 mb-1">Your Email</label><input id="email" type="email" placeholder="e.g. info@practice.co.uk" class="w-full rounded-xl border border-emerald-300 px-4 py-3 text-base focus:outline-none focus:ring-2 focus:ring-teal-500"></div>
<button onclick="generate()" class="w-full rounded-xl bg-teal-500 px-5 py-3 text-base font-bold text-white shadow-lg hover:bg-teal-400 transition">Generate Your Report &rarr;</button>
<p class="text-xs text-center text-zinc-500">Free. No card. Takes ~30 seconds.</p>
</div>
</div>
</div>

<div id="loadingSection" class="hidden text-center py-12">
<div class="inline-block w-10 h-10 border-4 border-emerald-200 border-t-emerald-700 rounded-full animate-spin mb-4"></div>
<p id="loadingText" class="text-lg font-semibold text-zinc-700">Scanning your website...</p>
<p class="text-sm text-zinc-500 mt-2">Analysing trust signals across 5 pillars</p>
</div>

<div id="resultsSection" class="hidden"></div>

</div>

<footer class="bg-zinc-900 text-zinc-300 py-10 px-6">
<div class="max-w-6xl mx-auto text-center text-sm">
<p class="text-yellow-400">&copy; 2025 Trust Trigger Agency&trade; &middot; The Trust Trigger Transformation Method&trade;</p>
</div>
</footer>

<script>
function $(i){return document.getElementById(i);}
function h(e){e.classList.add('hidden');}
function s(e){e.classList.remove('hidden');}

function generate(){
  var n=$('fullName').value.trim(),u=$('website').value.trim(),e=$('email').value.trim();
  if(!n||!u||!e){alert('Fill in all fields.');return;}
  h($('inputSection'));h($('resultsSection'));s($('loadingSection'));
  $('loadingText').textContent='Scanning your website...';

  fetch('/api/v1/public/trust-snapshot',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({full_name:n,website:u,email:e})
  })
  .then(function(r){return r.json();})
  .then(function(d){
    h($('loadingSection'));
    if(d.error){alert(d.error);s($('inputSection'));return;}
    showReport(d,n,u);
  })
  .catch(function(){
    h($('loadingSection'));
    alert('Network error. Please try again.');
    s($('inputSection'));
  });
}

function grade(s){if(s>=90)return'Excellent';if(s>=75)return'Good';if(s>=55)return'Average';if(s>=35)return'Weak';return'Critical';}

function showReport(d,n,u){
  var sc=d.score||0;
  var g=grade(sc);
  var summaries={Excellent:'Your website is a strong trust engine. Visitors feel confident reaching out.',Good:'You are building trust well. Minor gaps are preventing some conversions.',Average:'Your website is losing potential customers. The gaps below are costing you enquiries.',Weak:'Significant trust gaps found. Most visitors are likely leaving.',Critical:'Critical trust issues detected. Your website is actively repelling visitors.'};

  // Platform badge
  var platform=d.platform||'unknown';
  var isWP=d.is_wordpress||false;
  var platHtml='';
  if(isWP){
    platHtml='<div class="rounded-xl border border-emerald-200 bg-emerald-50 p-4 mb-6 text-center"><span class="inline-flex items-center gap-2 text-sm font-semibold text-emerald-800"><span class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span> WordPress Site Detected &mdash; Content can be published directly to your existing site (styled by your theme)</span></div>';
  } else {
    platHtml='<div class="rounded-xl border border-amber-200 bg-amber-50 p-4 mb-6 text-center"><span class="inline-flex items-center gap-2 text-sm font-semibold text-amber-800"><span class="w-3 h-3 rounded-full bg-amber-500"></span> Custom Platform / No Site &mdash; We will build you a brand new dedicated website</span></div>';
  }

  var pills=d.pillars||[];
  var labels={online_presence:'Online Presence',reputation:'Reputation',engagement:'Engagement',transparency:'Transparency',technical:'Technical Health'};
  var pillHtml='';
  pills.forEach(function(p){
    var l=labels[p.name]||p.label;
    var pc=Math.round(p.percentage);
    var c=pc>=80?'#14b8a6':pc>=60?'#eab308':pc>=40?'#f97316':'#ef4444';
    pillHtml+='<div class="rounded-xl border border-zinc-200 bg-white p-4"><div class="flex justify-between items-center mb-2"><span class="font-semibold text-zinc-800">'+l+'</span><span class="font-bold" style="color:'+c+'">'+pc+'%</span></div><div class="h-2.5 rounded-full bg-zinc-200 overflow-hidden"><div class="h-full rounded-full" style="width:'+pc+'%;background:'+c+'"></div></div></div>';
  });

  var stds=d.standards||[];
  var passedStds=[],failedStds=[];
  stds.forEach(function(st){
    var lb=st.name.replace(/([A-Z])/g,' $1').replace(/^./,function(s){return s.toUpperCase();}).trim();
    if(st.name==='Https')lb='HTTPS';
    if(st.name==='Cta')lb='Clear Calls to Action';
    if(st.name==='Faq')lb='FAQ Section';
    if(st.passed){passedStds.push(lb);}else{failedStds.push(lb);}
  });

  var stdHtml='';
  if(passedStds.length>0){
    stdHtml='<h3 class="font-bold text-zinc-900 mb-3">✓ What is Working ('+passedStds.length+'/'+stds.length+')</h3><div class="grid sm:grid-cols-2 gap-2">';
    passedStds.forEach(function(lb){stdHtml+='<div class="flex items-center gap-2 p-3 rounded-lg border border-emerald-200 bg-white"><span class="text-teal-600 font-bold">✓</span><span class="text-sm text-zinc-800">'+lb+'</span></div>';});
    stdHtml+='</div>';
  }
  if(failedStds.length>0){
    stdHtml+='<h3 class="font-bold text-red-800 mb-3 mt-6">✗ Missing ('+failedStds.length+'/'+stds.length+')</h3><div class="grid sm:grid-cols-2 gap-2">';
    failedStds.forEach(function(lb){stdHtml+='<div class="flex items-center gap-2 p-3 rounded-lg border border-red-200 bg-red-50"><span class="text-red-500 font-bold">✗</span><span class="text-sm text-zinc-800">'+lb+'</span></div>';});
    stdHtml+='</div>';
  }

  var issues=d.issues||[];
  var issuesHtml='';
  if(issues.length>0){
    issuesHtml='<h3 class="font-bold text-zinc-900 mb-3">⚠ Priority Gaps</h3>';
    issues.forEach(function(iss){
      issuesHtml+='<div class="flex items-start gap-3 p-4 rounded-xl border border-red-100 bg-red-50 mb-3"><span class="text-red-500 font-bold mt-0.5">⚠</span><div><p class="font-semibold text-zinc-900">'+iss.title+'</p><p class="text-sm text-zinc-600 mt-1">'+iss.detail+'</p></div></div>';
    });
  }

  var now=new Date();
  var html='';
  html+='<div class="rounded-2xl border border-emerald-200 bg-white shadow-xl p-6 sm:p-8">';
  html+=platHtml;
  html+='<div class="flex flex-col sm:flex-row items-center gap-8"><div class="relative w-36 h-36 flex items-center justify-center shrink-0"><svg class="w-36 h-36 -rotate-90" viewBox="0 0 120 120"><circle cx="60" cy="60" r="52" fill="none" stroke="#e5e7eb" stroke-width="8"/><circle id="scoreCircle" cx="60" cy="60" r="52" fill="none" stroke="#14b8a6" stroke-width="8" stroke-linecap="round" stroke-dasharray="326.7" stroke-dashoffset="326.7"/></svg><div class="absolute text-center"><span id="scoreNum" class="text-5xl font-extrabold text-zinc-900">0</span><span class="text-xs font-semibold text-zinc-500">/100</span></div></div><div><p class="text-xs font-bold uppercase tracking-wider text-emerald-700 mb-1">Trust Trigger Score</p><h2 class="text-2xl font-bold text-zinc-900">'+g+'</h2><p class="font-bold text-zinc-900 mt-1">'+n+'</p><p class="text-sm text-zinc-500 break-all">'+u+'</p><p class="text-sm text-zinc-700 mt-3">'+summaries[g]+'</p><div class="flex flex-wrap gap-4 mt-4 text-sm text-zinc-600"><span>📅 '+now.toLocaleDateString('en-GB',{day:'numeric',month:'long',year:'numeric'})+'</span><span>📊 '+pills.length+' pillars</span><span>🔍 '+issues.length+' issues</span></div></div></div></div>';
  if(pills.length>0){
    html+='<div class="rounded-2xl border border-emerald-200 bg-white shadow-xl p-6 mt-6"><h3 class="font-bold text-zinc-900 mb-4">Trust Pillar Breakdown</h3><div class="grid sm:grid-cols-2 gap-4">'+pillHtml+'</div></div>';
  }
  if(stdHtml){
    html+='<div class="rounded-2xl border border-emerald-200 bg-emerald-50 shadow-xl p-6 mt-6">'+stdHtml+'</div>';
  }
  if(issuesHtml){
    html+='<div class="rounded-2xl border border-red-200 bg-red-50 shadow-xl p-6 mt-6">'+issuesHtml+'</div>';
  }
  html+='<div class="text-center mt-8"><div class="rounded-2xl border-2 border-teal-500 bg-white shadow-xl p-8"><h3 class="text-xl font-bold text-zinc-900 mb-3">Want us to fix these gaps?</h3><p class="text-zinc-600 mb-6">Book a free 20-minute call and we will walk through your report together.</p><a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone" class="inline-block rounded-xl bg-teal-500 px-6 py-3 text-base font-bold text-white shadow-lg hover:bg-teal-400 transition">Book Your Free Review &rarr;</a></div></div>';

  $('resultsSection').innerHTML=html;
  s($('resultsSection'));

  var circ=$('scoreCircle');
  if(circ){
    var r=52;
     var cl=2Math.PIr;
    setTimeout(function(){circ.style.strokeDashoffset=cl-(sc/100)*cl;},300);
  }
  var ct=0;
  var ti=setInterval(function(){ct++;if(ct>sc||ct>100){clearInterval(ti);}$('scoreNum').textContent=ct;},15);
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
