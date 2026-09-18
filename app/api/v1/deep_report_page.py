"""Deep Trust Report — comprehensive diagnostic with proposal and fulfilment builder."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
router = APIRouter(prefix="/deep-report", tags=["Public - Deep Report"])

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Deep Trust Report | Trust Trigger Agency</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap">
<script src="https://cdn.tailwindcss.com"></script>
<style>
body{font-family:'Inter',system-ui,sans-serif}
.green1{background:linear-gradient(135deg,#064e3b,#065f46,#047857)}
.spinner{border:3px solid #e5e7eb;border-top:3px solid #14b8a6;border-radius:50%;width:32px;height:32px;animation:s .8s linear infinite}@keyframes s{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
.score-ring{transition:stroke-dashoffset 1.2s ease-out}
</style>
</head>
<body class="bg-stone-50 text-zinc-800">

<nav class="bg-zinc-900 border-b border-zinc-700 h-14 flex items-center px-6">
<div class="max-w-5xl mx-auto w-full flex items-center justify-between">
<a href="/home" class="text-lg font-extrabold text-yellow-400"><span class="mr-1">🛡️</span> Trust Trigger Agency</a>
</div>
</nav>

<div class="green1 text-white py-16 px-6 text-center">
<p class="text-xs font-bold uppercase tracking-[.2em] text-teal-300 mb-2">The Trust Trigger Method</p>
<h1 class="text-3xl sm:text-4xl font-extrabold">Your Trust Trigger Report</h1>
<p class="text-teal-200 text-sm mt-2 max-w-lg mx-auto">We analyse your website across 14 trust standards — then tell you exactly what's costing you patients and how to fix it.</p>
</div>

<div class="max-w-3xl mx-auto px-6 py-10">

<div id="form" class="max-w-md mx-auto">
<div class="rounded-xl border border-zinc-200 bg-white shadow-sm p-6">
<p class="text-sm font-bold text-zinc-800 mb-4">Enter a website to analyse</p>
<input id="_n" type="text" placeholder="Business name" class="w-full rounded-lg border border-zinc-200 px-3 py-2.5 text-sm mb-2.5">
<input id="_u" type="text" placeholder="Website URL" class="w-full rounded-lg border border-zinc-200 px-3 py-2.5 text-sm mb-2.5">
<input id="_e" type="email" placeholder="Your email" class="w-full rounded-lg border border-zinc-200 px-3 py-2.5 text-sm mb-4">
<button id="_go" class="w-full rounded-lg bg-teal-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm hover:bg-teal-500">Generate Your Trust Report →</button>
<p class="text-xs text-zinc-400 text-center mt-2">Free. No card. Takes 30 seconds.</p>
</div>
</div>

<div id="loading" class="hidden text-center py-16">
<div class="spinner mx-auto mb-4"></div>
<p class="text-sm font-semibold text-zinc-700">Scanning your website...</p>
</div>

<div id="error" class="hidden text-center py-10">
<p class="text-red-600 text-sm font-semibold mb-2">Something went wrong</p>
<p id="_err" class="text-zinc-500 text-xs mb-3"></p>
<button onclick="f()" class="rounded-lg bg-zinc-200 px-4 py-2 text-xs font-medium">Try again</button>
</div>

<div id="results" class="hidden"></div>

</div>

<footer class="bg-zinc-900 text-zinc-500 py-10 px-6 text-center text-xs">
<p class="text-yellow-400">&copy; 2025 Trust Trigger Agency &middot; The Trust Trigger Transformation Method</p>
</footer>

<script>
var A='';var R=null,N='',U='';

function $(i){return document.getElementById(i);}
function h(i){var e=$(i);if(e)e.classList.add('hidden');}
function s(i){var e=$(i);if(e)e.classList.remove('hidden');}
function f(){h('error');s('form');}

$('_go').onclick=function(){
  N=$('_n').value.trim();U=$('_u').value.trim();var E=$('_e').value.trim();
  if(!N||!U||!E){alert('Fill in all fields.');return;}
  h('form');h('error');h('results');s('loading');
  var x=new XMLHttpRequest();
  x.open('POST',A+'/api/v1/public/trust-snapshot',true);
  x.setRequestHeader('Content-Type','application/json');
  x.onload=function(){h('loading');
    if(x.status==201||x.status==200){try{var d=JSON.parse(x.responseText);if(d.error){$('_err').textContent=d.error;s('error');return;}R=d;render();}catch(e){$('_err').textContent='Invalid response';s('error');}}
    else{$('_err').textContent='Server error: '+x.status;s('error');}
  };
  x.onerror=function(){$('_err').textContent='Network error.';s('error');};
  x.send(JSON.stringify({full_name:N,website:U,email:E}));
};

function gr(s){
  if(s>=80) return {label:'Strong (B)',color:'text-emerald-700',desc:'Your website builds trust reasonably well, but specific gaps still prevent some visitors from booking.',impact:'2-4 enquiries/week',loss:'£800-£2,000/week'};
  if(s>=60) return {label:'Good (C)',color:'text-emerald-600',desc:'Your site is credible but missing key trust signals that convert visitors into patients.',impact:'5-8 enquiries/week',loss:'£2,000-£4,000/week'};
  if(s>=40) return {label:'Average (D)',color:'text-amber-600',desc:'Your website is losing potential patients. Several trust signals are missing.',impact:'10-15 enquiries/week',loss:'£4,000-£7,500/week'};
  if(s>=20) return {label:'Weak (E)',color:'text-orange-600',desc:'Significant trust gaps. Most visitors leave without contacting you.',impact:'15-20+ enquiries/week',loss:'£7,500-£10,000/week'};
  return {label:'At Risk (F)',color:'text-red-600',desc:'Critical trust issues. Your website is actively repelling patients.',impact:'20+ enquiries/week',loss:'£10,000+/week'};
}

var DIAG={
  'Https':{issue:'Your site does not use HTTPS or redirects to a non-secure version.',means:'Browsers show a "Not Secure" warning. In healthcare, this destroys trust immediately.',benefit:'Green padlock = instant trust. Google ranks HTTPS sites higher.',notfix:'Patients leave on sight. You lose every visitor who lands on a non-secure page.',probe:'Would you enter your details on a site your browser flagged as unsafe?'},
  'contact_page':{issue:'No clear contact page with full details.',means:'Patients who want to book have to hunt for how to reach you. Extra clicks = lost leads.',benefit:'A clear contact page can increase enquiries by 20-30%.',notfix:'You are sending ready-to-book patients straight to competitors who make it easy.',probe:'How many patients have told you they could not find your number?'},
  'about_page':{issue:'No compelling About page showing your team and story.',means:'You are asking visitors to trust a faceless business. They will choose a practice with real people.',benefit:'An About page with team photos humanises your practice. It is one of the most visited pages.',notfix:'Patients book with people they trust. If they cannot see you, they choose someone who shows their team.',probe:'Would you let a stranger treat you without knowing anything about them?'},
  'cta':{issue:'No clear calls-to-action telling visitors what to do.',means:'Visitors land, browse, then leave. Without a "Book Now" button, you are not asking for the booking.',benefit:'A well-placed CTA can double your conversion rate.',notfix:'Every visitor who leaves without acting is traffic you paid for with no return.',probe:'If you walked into a shop and nobody told you where to pay, would you leave money on the counter?'},
  'testimonials':{issue:'No patient reviews or testimonials displayed.',means:'Social proof is everything in healthcare. Without reviews, new visitors have no reason to trust you.',benefit:'Displaying reviews builds instant credibility. Patients who see testimonials are 58% more likely to book.',notfix:'Patients check Google reviews anyway. If your site does not show them, they leave your site to check — and may book a competitor.',probe:'When was the last time you chose a service without checking reviews first?'},
  'faq':{issue:'No FAQ section addressing common patient questions.',means:'Every patient asks: cost, duration, pain, booking. Without answers, they call a competitor who has answers ready.',benefit:'FAQs answer objections before they arise. Saves reception time, builds trust.',notfix:'Every unanswered question is a barrier to booking.',probe:'How many calls does your reception take answering the same questions every week?'},
  'service_pages':{issue:'Services not clearly detailed on your website.',means:'Patients arrive looking for specific treatments. If they cannot find clear info, they leave.',benefit:'Detailed service pages establish you as an expert and answer questions before they are asked.',notfix:'Patients searching for a treatment choose the practice that clearly explains it.',probe:'If a patient searches for a treatment and your site does not mention it, do they stay?'},
  'privacy_policy':{issue:'No privacy policy or GDPR compliance page.',means:'Patients need to know their data is safe. Missing privacy policy creates legal risk too.',benefit:'A privacy policy builds trust and keeps you compliant with GDPR.',notfix:'Without one, privacy-conscious patients will not submit their details. Fines can reach 4% of turnover.',probe:'Would you submit medical information to a site that does not explain how it is used?'},
  'mobile_responsive':{issue:'Site not fully optimised for mobile devices.',means:'Over 60% of healthcare visits come from phones. If your site is hard to use on mobile, you lose most of your traffic.',benefit:'Mobile-friendly sites keep patients engaged and rank higher on Google.',notfix:'You lose the majority of visitors who land on their phone. They choose a competitor whose site works.',probe:'Pull out your phone and try to book through your own website. If you struggle, so do your patients.'}
};

function render(){
  var d=R;if(!d)return;
  var sc=d.score||0,g=gr(sc),isWP=d.is_wordpress||false,pills=d.pillars||[],stds=d.standards||[],iss=d.issues||[];
  var now=new Date();
  var h='';
  
  h+='<div class="rounded-xl border border-zinc-200 bg-white shadow-sm p-6">';
  h+='<div class="flex items-start gap-5"><div class="relative w-20 h-20 shrink-0"><svg class="w-20 h-20 -rotate-90" viewBox="0 0 120 120"><circle cx="60" cy="60" r="52" fill="none" stroke="#e5e7eb" stroke-width="10"/><circle class="score-ring" id="sc" cx="60" cy="60" r="52" fill="none" stroke="#0d9488" stroke-width="10" stroke-dasharray="326.7" stroke-dashoffset="326.7"/></svg><div class="absolute inset-0 flex items-center justify-center"><span class="text-xl font-extrabold text-zinc-900" id="sn">0</span></div></div>';
  h+='<div><p class="text-xs font-bold uppercase tracking-wider text-zinc-500">Trust Trigger Score</p><h2 class="text-xl font-bold text-zinc-900">'+g.label+'</h2><p class="font-semibold text-zinc-800 text-sm">'+N+'</p><p class="text-xs text-zinc-400">'+U+'</p><p class="text-sm text-zinc-600 mt-2">'+g.desc+'</p></div></div>';
  h+='<div class="mt-4 bg-red-50 border border-red-200 rounded-lg p-4"><p class="text-sm font-bold text-red-800">Estimated Revenue Impact</p><p class="text-sm text-red-700 mt-1">Your current trust gaps are likely costing you <strong>'+g.impact+'</strong> — an estimated <strong>'+g.loss+'</strong> in missed patient revenue.</p></div>';
  h+='<div class="mt-3 text-xs text-zinc-500 flex flex-wrap gap-3"><span>'+now.toLocaleDateString("en-GB",{day:"numeric",month:"long",year:"numeric"})+'</span><span>'+pills.length+' pillars</span><span>'+iss.length+' issues</span></div>';
  h+='</div>';
  
  h+='<div class="mt-5 rounded-xl border border-zinc-200 bg-white shadow-sm p-4">';
  if(isWP) h+='<p class="text-sm font-semibold text-emerald-800">WordPress Site — We can publish content directly to your existing site. Your theme is preserved.</p>';
  else h+='<p class="text-sm font-semibold text-amber-800">Custom Platform — We will build you a brand new dedicated website. Full design control. Ready in 7 days.</p>';
  h+='</div>';
  
  if(pills.length){
    h+='<div class="mt-8"><p class="text-lg font-bold text-zinc-900 mb-1">Trust Pillar Breakdown</p><p class="text-sm text-zinc-500 mb-5">Your website scored across 5 trust dimensions.</p>';
    pills.forEach(function(p){
      var pc=Math.round(p.percentage),l=p.label||p.name;
      var b=pc>=80?'bg-emerald-500':pc>=60?'bg-amber-500':pc>=40?'bg-orange-500':'bg-red-500';
      var t=pc>=80?'text-emerald-700':pc>=60?'text-amber-700':pc>=40?'text-orange-700':'text-red-700';
      h+='<div class="rounded-xl border border-zinc-200 bg-white shadow-sm p-4 mb-3"><div class="flex justify-between items-center mb-1"><span class="text-sm font-bold text-zinc-900">'+l+'</span><span class="text-sm font-bold '+t+'">'+pc+'%</span></div><div class="h-2 bg-zinc-100 rounded-full overflow-hidden"><div class="h-full rounded-full '+b+'" style="width:'+pc+'%"></div></div></div>';
    });
    h+='</div>';
  }
  
  if(stds.length){
    h+='<div class="mt-8"><p class="text-lg font-bold text-zinc-900 mb-1">Deep Diagnostic: Every Standard Checked</p><p class="text-sm text-zinc-500 mb-5">Below is what we found, what it means, and what happens if you do not fix it.</p>';
    stds.forEach(function(st){
      var dg=DIAG[st.name]||{issue:'Standard checked.',means:'Affects patient perception.',benefit:'Fixing this improves trust.',notfix:'Leaving this unfixed costs enquiries.',probe:'Consider this.'};
      var lb=st.name.replace(/([A-Z])/g,' $1').replace(/^./,function(x){return x.toUpperCase()}).trim();
      if(st.name==='Https')lb='HTTPS';if(st.name==='Cta')lb='Call-to-Action';if(st.name==='Faq')lb='FAQ Section';
      var icon=st.passed?'✅':'❌';var border=st.passed?'border-emerald-200':'border-red-200';
      h+='<div class="rounded-xl border '+border+' bg-white shadow-sm p-5 mb-4"><div class="flex items-center gap-2 mb-3"><span>'+icon+'</span><p class="text-sm font-bold text-zinc-900">'+lb+'</p></div>';
      if(!st.passed){
        h+='<div class="space-y-3">';
        h+='<div><p class="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-1">What we found</p><p class="text-sm text-zinc-700">'+dg.issue+'</p></div>';
        h+='<div><p class="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-1">What this means for your business</p><p class="text-sm text-zinc-700">'+dg.means+'</p></div>';
        h+='<div class="bg-emerald-50 border border-emerald-200 rounded-lg p-3"><p class="text-xs font-bold text-emerald-700 uppercase tracking-wider mb-1">Benefit of fixing this</p><p class="text-sm text-emerald-800">'+dg.benefit+'</p></div>';
        h+='<div class="bg-red-50 border border-red-200 rounded-lg p-3"><p class="text-xs font-bold text-red-700 uppercase tracking-wider mb-1">Cost of not fixing this</p><p class="text-sm text-red-800">'+dg.notfix+'</p></div>';
        h+='<div class="bg-amber-50 border border-amber-200 rounded-lg p-3"><p class="text-xs font-bold text-amber-700 uppercase tracking-wider mb-1">Consider this</p><p class="text-sm text-amber-800 font-medium">'+dg.probe+'</p></div>';
        h+='</div>';
      } else { h+='<p class="text-sm text-emerald-700 font-medium">This trust signal is working in your favour.</p>'; }
      h+='</div>';
    });
    h+='</div>';
  }
  
  if(iss.length){
    h+='<div class="mt-8"><p class="text-lg font-bold text-zinc-900 mb-1">Priority Issues</p><p class="text-sm text-zinc-500 mb-5">These specific gaps are costing you revenue right now.</p>';
    iss.forEach(function(x,i){
      h+='<div class="border-l-4 border-red-500 bg-white rounded-r-xl shadow-sm p-5 mb-3"><div class="flex items-start gap-3"><span class="shrink-0 w-7 h-7 rounded-full bg-red-100 text-red-600 flex items-center justify-center text-sm font-bold">'+(i+1)+'</span><div><p class="text-sm font-bold text-zinc-900">'+x.title+'</p><p class="text-sm text-zinc-600 mt-1">'+x.detail+'</p></div></div></div>';
    });
    h+='</div>';
  }
  
  h+='<div class="mt-10"><div class="rounded-xl border-2 border-teal-600 bg-white shadow-sm p-6">';
  h+='<p class="text-xs font-bold text-teal-600 uppercase tracking-wider">Our Recommendation</p>';
  h+='<p class="text-2xl font-bold text-zinc-900 mt-1 mb-5">Trust Transformation Proposal</p>';
  h+='<div class="bg-zinc-50 border border-zinc-200 rounded-lg p-4 mb-5"><table class="w-full text-sm"><tbody>';
  h+='<tr class="border-b border-zinc-200"><td class="py-2 font-medium">Package</td><td class="py-2 text-right font-bold">Trust Transformation</td></tr>';
  h+='<tr class="border-b border-zinc-200"><td class="py-2 font-medium">Price</td><td class="py-2 text-right"><span class="text-xl font-extrabold text-teal-700">&pound;995</span><span class="text-xs text-zinc-500 ml-1">one-time</span></td></tr>';
  h+='<tr class="border-b border-zinc-200"><td class="py-2 font-medium">Delivery</td><td class="py-2 text-right font-semibold">7 days</td></tr>';
  h+='<tr><td class="py-2 font-medium">Projected score</td><td class="py-2 text-right font-semibold text-emerald-700">'+sc+' &rarr; 85+</td></tr>';
  h+='</tbody></table></div>';
  h+='<ul class="space-y-2 mb-5 text-sm">';
  h+='<li class="flex items-start gap-2"><span class="text-emerald-600">&#10003;</span> Full website trust audit completed</li>';
  h+='<li class="flex items-start gap-2"><span class="text-emerald-600">&#10003;</span> New homepage copy optimised for conversion</li>';
  h+='<li class="flex items-start gap-2"><span class="text-emerald-600">&#10003;</span> 5-email nurture sequence for new enquiries</li>';
  h+='<li class="flex items-start gap-2"><span class="text-emerald-600">&#10003;</span> Google Business Profile content (10 posts)</li>';
  h+='<li class="flex items-start gap-2"><span class="text-emerald-600">&#10003;</span> Social media content (Facebook + Instagram)</li>';
  if(isWP) h+='<li class="flex items-start gap-2"><span class="text-emerald-600">&#10003;</span> Direct WordPress publishing</li>';
  else h+='<li class="flex items-start gap-2"><span class="text-emerald-600">&#10003;</span> Brand new website build (5-7 pages, hosted)</li>';
  h+='<li class="flex items-start gap-2"><span class="text-emerald-600">&#10003;</span> Before/after evidence report with score improvement</li>';
  h+='</ul>';
  h+='<div class="text-center"><a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone" class="inline-block rounded-lg bg-teal-600 px-8 py-3 text-base font-bold text-white shadow-sm hover:bg-teal-500">Book Your Free 20-Minute Trust Review &rarr;</a><p class="text-xs text-zinc-400 mt-2">Free. No obligation.</p></div>';
  h+='</div></div>';
  
  h+='<div class="mt-8"><div class="rounded-xl border border-zinc-200 bg-white shadow-sm p-6">';
  h+='<p class="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-1">How We Deliver</p>';
  h+='<h3 class="text-lg font-bold text-zinc-900 mb-5">Your 7-Day Fulfilment Timeline</h3>';
  [['1','Strategy Call','We review your report. You confirm scope.'],['2-3','Content Creation','We generate homepage copy, emails, GBP posts, social content.'],['4','Your Review','Preview link sent. You approve or request changes.'],['5-6','Publishing','Content goes live on WordPress (Path A) or new site deploys (Path B).'],['7','Evidence Report','Rescan + before/after report showing score improvement.']].forEach(function(s){
    h+='<div class="flex items-start gap-4 mb-4"><span class="shrink-0 w-8 h-8 rounded-full bg-teal-100 text-teal-700 flex items-center justify-center text-sm font-bold">'+s[0]+'</span><div><p class="text-sm font-bold text-zinc-900">'+s[1]+'</p><p class="text-xs text-zinc-500">'+s[2]+'</p></div></div>';
  });
  h+='<div class="mt-4 bg-zinc-50 border border-zinc-200 rounded-lg p-4"><p class="text-sm text-zinc-700">Your time commitment: <strong>~20 minutes total</strong> (one call + one approval). We do the rest.</p></div>';
  h+='</div></div>';
  
  h+='<div class="mt-8 text-center"><a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone" class="inline-block rounded-lg bg-teal-600 px-8 py-3.5 text-base font-bold text-white shadow-sm hover:bg-teal-500">Book Your Free Trust Review &rarr;</a></div>';
  
  $('results').innerHTML=h;
  s('results');
  $('results').scrollIntoView({behavior:'smooth',block:'start'});
  
  setTimeout(function(){var c=document.getElementById('sc');if(c)c.style.strokeDashoffset=326.7-(sc/100)*326.7;},300);
  var ct=0,ti=setInterval(function(){ct++;if(ct>sc||ct>100)clearInterval(ti);var e=document.getElementById('sn');if(e)e.textContent=ct;},15);
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
