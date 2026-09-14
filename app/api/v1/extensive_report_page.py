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
.gt{background:linear-gradient(135deg,#059669,#0d9488);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.green1{background:linear-gradient(135deg,#064e3b,#065f46,#047857)}
.reveal{opacity:0;transform:translateY(20px);transition:opacity .6s ease-out,transform .6s ease-out}
.reveal.in-view{opacity:1;transform:none}
.pillar-bar{transition:width 1.2s ease-out}
@keyframes pulse-dot{0%,100%{opacity:1}50%{opacity:.4}}
.pulse-dot{animation:pulse-dot 1.5s ease-in-out infinite}
</style>
</head>
<body class="antialiased bg-emerald-50 text-zinc-800">

<nav class="bg-black border-b border-zinc-800 fixed top-0 left-0 right-0 z-50 h-20 flex items-center px-6">
<div class="max-w-6xl mx-auto w-full flex items-center justify-between">
<a href="https://trust-trigger-api.onrender.com/home" class="flex items-center gap-2 text-2xl font-extrabold text-yellow-400"><span class="text-3xl">🛡️</span> Trust Trigger Agency</a>
<div class="flex items-center gap-3">
<a href="https://trust-trigger-api.onrender.com/home" class="rounded-lg bg-teal-500 px-4 py-2 text-xs font-semibold text-white hover:bg-teal-400">Get Free Snapshot →</a>
</div>
</div>
</nav>

<div class="h-20"></div>

<div class="green1 text-white py-20 sm:py-28 px-6">
<div class="max-w-5xl mx-auto text-center">
<p class="text-sm font-bold uppercase tracking-[.2em] text-teal-300 mb-4">The Trust Trigger Method™</p>
<h1 class="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight mb-4">Extensive Trust Report</h1>
<p class="text-lg sm:text-xl text-emerald-200 max-w-3xl mx-auto leading-relaxed font-medium">Enter any business website. We analyse it across <strong class="text-white">5 trust pillars</strong> and <strong class="text-white">14 standards</strong> to show you exactly where trust is winning and where it is leaking.</p>
</div>
</div>

<div class="max-w-5xl mx-auto px-6 py-16">
<div id="inputSection" class="max-w-lg mx-auto">
<div class="rounded-2xl border border-emerald-200 bg-white shadow-xl p-6 sm:p-8">
<div class="space-y-5">
<div><label class="block text-sm font-bold text-zinc-800 mb-1.5">Business Name</label><input id="fullName" type="text" placeholder="e.g. Ivy Dentistry Aesthetics" class="w-full rounded-xl border border-emerald-300 px-5 py-3.5 text-base font-medium text-zinc-800 placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-teal-500"></div>
<div><label class="block text-sm font-bold text-zinc-800 mb-1.5">Website URL</label><input id="website" type="text" placeholder="e.g. ivydentistryaesthetics.co.uk" class="w-full rounded-xl border border-emerald-300 px-5 py-3.5 text-base font-medium text-zinc-800 placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-teal-500"></div>
<div><label class="block text-sm font-bold text-zinc-800 mb-1.5">Your Email</label><input id="email" type="email" placeholder="e.g. info@yourpractice.co.uk" class="w-full rounded-xl border border-emerald-300 px-5 py-3.5 text-base font-medium text-zinc-800 placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-teal-500"><p class="text-xs text-zinc-500 mt-1.5 font-medium">Your report will appear below.</p></div>
<button onclick="generate()" class="w-full rounded-xl bg-teal-500 px-6 py-3.5 text-base font-bold text-white shadow-lg hover:bg-teal-400 transition">Generate Your Extensive Trust Report →</button>
<p class="text-xs text-center text-zinc-500 font-medium">Free. No card. Takes ~30 seconds.</p>
</div>
</div>
</div>

<div id="loadingSection" class="hidden max-w-2xl mx-auto mt-8">
<div class="rounded-2xl border border-emerald-200 bg-white shadow-xl p-8 sm:p-10 text-center">
<h2 class="text-xl font-bold text-zinc-900 mb-6">Generating your Trust Trigger Report</h2>
<p class="text-sm text-zinc-600 mb-8 font-medium">Analysing your website across our Trust Trigger framework</p>
<div class="max-w-md mx-auto space-y-4 text-left">
<div class="flex items-center gap-4"><span id="s1" class="w-7 h-7 rounded-full bg-zinc-200 flex items-center justify-center text-sm font-bold text-zinc-500 shrink-0">1</span><div class="flex-1"><p class="text-sm font-semibold text-zinc-800">Website structure</p><p class="text-xs text-zinc-500">Layout, navigation, page architecture</p></div><span id="d1" class="text-teal-600 text-sm font-medium">⏳</span></div>
<div class="flex items-center gap-4"><span id="s2" class="w-7 h-7 rounded-full bg-zinc-200 flex items-center justify-center text-sm font-bold text-zinc-500 shrink-0">2</span><div class="flex-1"><p class="text-sm font-semibold text-zinc-800">Trust signals</p><p class="text-xs text-zinc-500">Credibility markers, reviews, authority</p></div><span id="d2" class="text-zinc-400 text-sm font-medium">⏳</span></div>
<div class="flex items-center gap-4"><span id="s3" class="w-7 h-7 rounded-full bg-zinc-200 flex items-center justify-center text-sm font-bold text-zinc-500 shrink-0">3</span><div class="flex-1"><p class="text-sm font-semibold text-zinc-800">Social proof</p><p class="text-xs text-zinc-500">Testimonials, badges, case studies</p></div><span id="d3" class="text-zinc-400 text-sm font-medium">⏳</span></div>
<div class="flex items-center gap-4"><span id="s4" class="w-7 h-7 rounded-full bg-zinc-200 flex items-center justify-center text-sm font-bold text-zinc-500 shrink-0">4</span><div class="flex-1"><p class="text-sm font-semibold text-zinc-800">Conversion journey</p><p class="text-xs text-zinc-500">CTAs, forms, enquiry path</p></div><span id="d4" class="text-zinc-400 text-sm font-medium">⏳</span></div>
<div class="flex items-center gap-4"><span id="s5" class="w-7 h-7 rounded-full bg-zinc-200 flex items-center justify-center text-sm font-bold text-zinc-500 shrink-0">5</span><div class="flex-1"><p class="text-sm font-semibold text-zinc-800">Finalising analysis</p><p class="text-xs text-zinc-500">Scoring, gaps, building your report</p></div><span id="d5" class="text-zinc-400 text-sm font-medium">⏳</span></div>
</div>
<p id="loadingStatus" class="text-sm text-teal-700 font-bold mt-8 pulse-dot">Analysing website structure...</p>
</div>
</div>

<div id="resultsSection" class="hidden mt-8 space-y-8"></div>
<div id="ctaSection" class="hidden mt-8 text-center">
<div class="max-w-xl mx-auto rounded-2xl border-2 border-teal-500 bg-white shadow-xl p-8">
<h3 class="text-xl font-bold text-zinc-900 mb-4">Want to fix these gaps?</h3>
<p class="text-zinc-600 mb-6 font-medium">Book a free 20-minute call and we will walk through your report together - every gap, every fix, prioritised by impact.</p>
<a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone?month=2026-09" class="rounded-xl bg-teal-500 px-6 py-3.5 text-base font-bold text-white shadow-lg hover:bg-teal-400 transition">Book Your Free Review →</a>
</div>
</div>
</div>

<footer class="bg-zinc-900 text-zinc-300 py-12 px-6 border-t border-zinc-800">
<div class="max-w-6xl mx-auto">
<div class="grid grid-cols-2 gap-10">
<div><div class="flex items-center gap-2 text-lg font-extrabold mb-4"><span class="text-xl">🛡️</span> <span class="text-yellow-400">Trust Trigger Agency</span></div><p class="text-zinc-400 text-sm">Helping healthcare practices turn websites into patient booking engines.</p></div>
<div><p class="text-sm font-bold uppercase tracking-wider text-emerald-400 mb-4">Service</p><ul class="space-y-3 text-sm font-medium"><li><a href="https://trust-trigger-api.onrender.com/home" class="text-zinc-300 hover:text-white">Home</a></li><li><a href="https://trust-trigger-api.onrender.com/competitor-insights" class="text-zinc-300 hover:text-white">Compare Competitors</a></li><li><a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone?month=2026-09" class="text-zinc-300 hover:text-white">Book a Review</a></li></ul></div>
</div>
<div class="border-t border-zinc-800 mt-8 pt-6 text-sm font-medium text-center"><p class="text-yellow-400">© 2025 Trust Trigger Agency™ · The Trust Trigger Transformation Method™</p></div>
</div>
</footer>

<script>
var API='';function $(i){return document.getElementById(i);}
function h(e){e.classList.add('hidden');}function s(e){e.classList.remove('hidden');}
function al(step){
  var steps=['s1','s2','s3','s4','s5'],dots=['d1','d2','d3','d4','d5'],msgs=['Analysing website structure...','Checking trust signals...','Evaluating social proof...','Mapping conversion journey...','Finalising your Trust Trigger Report...'];
  for(var i=0;i<steps.length;i++){
    var el=$(steps[i]),dt=$(dots[i]);
    if(i<step){
      el.className='w-7 h-7 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-sm font-bold shrink-0';el.textContent='✓';dt.textContent='✓';dt.className='text-emerald-600 text-sm font-medium';
    }else if(i===step){
      el.className='w-7 h-7 rounded-full bg-teal-500 text-white flex items-center justify-center text-sm font-bold shrink-0 pulse-dot';dt.innerHTML='<span class="pulse-dot">⏳</span>';dt.className='text-teal-600 text-sm font-medium';
    }
  }
  if(step<msgs.length)$('loadingStatus').textContent=msgs[step];
}
function generate(){
  var n=$('fullName').value.trim(),u=$('website').value.trim(),e=$('email').value.trim();
  if(!n||!u||!e){alert('Please fill in all fields.');return;}
  h($('inputSection'));h($('resultsSection'));h($('ctaSection'));s($('loadingSection'));al(0);
  var si=setInterval(function(){for(var i=0;i<5;i++){if($('s'+(i+1)).classList.contains('pulse-dot')){if(i+1<5)al(i+1);break;}}},4000);
  fetch('/api/v1/public/trust-snapshot',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({full_name:n,website:u,email:e})})
  .then(function(r){return r.json();}).then(function(d){
    clearInterval(si);h($('loadingSection'));if(d.error){alert(d.error);s($('inputSection'));return;}
    setTimeout(function(){showReport(d);},5000);
  });
}
function gl(s){if(s>=90)return'Excellent';if(s>=75)return'Good';if(s>=55)return'Average';if(s>=35)return'Weak';return'Critical';}
function showReport(d){
  var sc=d.score||0;h($('loadingSection'));s($('resultsSection'));
  var summaries={Excellent:'Your website builds strong trust. Minor refinements can maximise conversion.',Good:'Your website is credible - but specific trust gaps are preventing it from converting at full potential.',Average:'Your website has foundational elements but lacks the trust signals needed to convert visitors.',Weak:'Significant trust gaps exist. Visitors are likely leaving without enquiring.',Critical:'Your website is actively losing patients. Urgent improvements needed.'};
  var now=new Date();var pills=d.pillars||[];
  var labels={online_presence:'Online Presence',reputation:'Reputation',engagement:'Engagement',transparency:'Transparency',technical:'Technical Health'};
  var pillHtml='';pills.forEach(function(p){var l=labels[p.name]||p.label;var pc=Math.round(p.percentage);var col=pc>=80?'#14b8a6':pc>=60?'#eab308':pc>=40?'#f97316':'#ef4444';pillHtml+='<div class="rounded-xl border border-zinc-200 bg-white p-4"><div class="flex justify-between items-center mb-2"><span class="font-semibold text-zinc-800">'+l+'</span><span class="font-bold" style="color:'+col+'">'+pc+'</span></div><div class="h-2.5 rounded-full bg-zinc-200 overflow-hidden"><div class="h-full rounded-full" style="width:'+pc+'%;background:'+col+'"></div></div></div>';});
  var issuesHtml='';var issues=d.issues||[];if(issues.length){issuesHtml='<div class="rounded-2xl border border-emerald-200 bg-white shadow-xl p-6 sm:p-8"><h3 class="font-bold text-zinc-900 mb-4">Trust Gaps Identified</h3>';issues.forEach(function(iss){issuesHtml+='<div class="flex items-start gap-3 p-4 rounded-xl border border-red-100 bg-red-50 mb-3"><span class="text-red-500 font-bold mt-0.5">⚠️</span><div><p class="font-semibold text-zinc-900">'+iss.title+'</p><p class="text-sm text-zinc-600 mt-1">'+iss.detail+'</p></div></div>';});issuesHtml+='</div>';}
  var stdHtml='';var stds=d.standards||[];var pcnt=0;stds.forEach(function(st){if(st.passed){pcnt++;var lb=st.name.replace(/([A-Z])/g,' $1').replace(/^./,function(s){return s.toUpperCase();}).trim();if(st.name==='Https')lb='HTTPS';if(st.name==='Cta')lb='Clear CTAs';if(st.name==='Faq')lb='FAQ Section';stdHtml+='<div class="flex items-center gap-2 p-3 rounded-lg border border-emerald-200 bg-white"><span class="text-teal-600 font-bold">✓</span><span class="text-sm font-medium text-zinc-800">'+lb+'</span></div>';}});
  var rs=$('resultsSection');rs.innerHTML='<div class="rounded-2xl border border-emerald-200 bg-white shadow-xl p-6 sm:p-8"><p class="text-xs font-bold uppercase tracking-wider text-emerald-700 mb-1">Your Trust Trigger Score</p><div class="flex flex-col sm:flex-row items-center gap-8"><div class="relative w-36 h-36 flex items-center justify-center shrink-0"><svg class="w-36 h-36 -rotate-90" viewBox="0 0 120 120"><circle cx="60" cy="60" r="52" fill="none" stroke="#e5e7eb" stroke-width="8"/><circle id="scoreCircle" cx="60" cy="60" r="52" fill="none" stroke="#14b8a6" stroke-width="8" stroke-linecap="round" stroke-dasharray="326.7" stroke-dashoffset="326.7" style="transition:stroke-dashoffset 1.2s"/></svg><div class="absolute text-center"><span id="scoreNum" class="text-5xl font-extrabold text-zinc-900">0</span><span class="text-xs font-semibold text-zinc-500">/100</span></div></div><div><h2 class="text-2xl sm:text-3xl font-bold mb-1">'+gl(sc)+'</h2><p class="text-lg font-bold text-zinc-900">'+$('fullName').value+'</p><p class="text-sm text-zinc-500">'+$('website').value+'</p><p class="text-sm text-zinc-700 mt-3 max-w-lg leading-relaxed font-medium">'+summaries[gl(sc)]+'</p><div class="flex flex-wrap gap-4 mt-4 text-sm text-zinc-600 font-medium"><span>📅 '+now.toLocaleDateString('en-GB',{day:'numeric',month:'long',year:'numeric'})+'</span><span>📊 '+(d.pillars?d.pillars.length:0)+' pillars</span><span>⚠️ '+(d.issues_found||0)+' issues</span></div></div></div></div><div class="rounded-2xl border border-emerald-200 bg-white shadow-xl p-6 sm:p-8 mt-8"><h3 class="font-bold text-zinc-900 mb-1">The 5 Trust Pillars</h3><p class="text-sm text-zinc-600 mb-6 font-medium">Your website scored across each dimension of trust</p><div class="grid sm:grid-cols-2 gap-4">'+pillHtml+'</div></div>'+issuesHtml+(stdHtml?'<div class="rounded-2xl border border-emerald-200 bg-emerald-50 shadow-xl p-6 sm:p-8 mt-8"><h3 class="font-bold text-zinc-900 mb-1">✓ Trust Triggers Already Working</h3><p class="text-sm text-zinc-600 mb-6 font-medium">Your website is getting these right. Do not change them.</p><div class="grid sm:grid-cols-2 gap-3">'+stdHtml+'</div></div>':'')+'<div class="text-center mt-8"><a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone?month=2026-09" class="rounded-xl bg-teal-500 px-6 py-3.5 text-base font-bold text-white shadow-lg hover:bg-teal-400 transition">Book Your Free Review →</a></div>';
  s($('ctaSection'));
  setTimeout(function(){var circ=$('scoreCircle');var r=52,cl=2Math.PIr;circ.style.strokeDashoffset=cl-(sc/100)*cl;},200);
  var ct=0;var ti=setInterval(function(){ct++;if(ct>sc){clearInterval(ti);}$('scoreNum').textContent=ct;},20);
  rs.querySelector('.rounded-2xl').scrollIntoView({behavior:'smooth',block:'start'});
}
</script>
</body>
</html>"""

@router.get("", response_class=HTMLResponse)
async def get_extensive_report_page():
    return PAGE

@router.get("/", response_class=HTMLResponse)
async def get_extensive_report_page_root():
    return PAGE
