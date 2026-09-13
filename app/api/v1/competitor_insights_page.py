"""Competitor Trust Insights page — served by the API with real competitor scanning."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
router = APIRouter(prefix="/competitor-insights", tags=["Public - Competitor Insights"])

PAGE = """<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Competitor Trust Insights — Trust Trigger Agency</title>
  <meta name="description" content="Free competitor trust comparison. Enter your URL — we automatically find and compare 2 real competitors across 5 trust pillars.">
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ctext y='26' font-size='26'%3E🛡️%3C/text%3E%3C/svg%3E">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body{font-family:Inter,sans-serif;-webkit-font-smoothing:antialiased}
    .gt{background:linear-gradient(135deg,#059669,#0d9488);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
    .green1{background:linear-gradient(135deg,#064e3b,#065f46,#047857)}
    .sg{background:#22c55e}.sy{background:#eab308}.so{background:#f97316}.sr{background:#ef4444}
  </style>
</head>
<body class="bg-emerald-50 text-zinc-800">

<nav class="bg-black border-b border-zinc-800 fixed top-0 left-0 right-0 z-50 h-20 flex items-center px-6">
  <div class="max-w-6xl mx-auto w-full flex items-center justify-between">
    <a href="https://trust-trigger-api.onrender.com/home" class="flex items-center gap-2 text-2xl font-extrabold text-yellow-400"><span class="text-3xl">🛡️</span> Trust Trigger Agency</a>
    <div class="flex items-center gap-5">
      <a href="https://trust-trigger-api.onrender.com/home#contact" class="text-base font-semibold text-zinc-300 hover:text-white">Contact</a>
      <a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone?month=2026-09" class="rounded-lg bg-teal-500 px-5 py-2.5 text-base font-semibold text-white hover:bg-teal-400">Get A Free Trust Review →</a>
    </div>
  </div>
</nav>

<div class="h-20"></div>

<div class="green1 text-white py-20 sm:py-28 px-6">
  <div class="max-w-6xl mx-auto text-center">
    <p class="text-sm font-bold uppercase tracking-[.2em] text-teal-300 mb-4">Free Competitive Analysis</p>
    <h1 class="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight mb-4">Competitor <span class="gt">Trust Insights</span></h1>
    <p class="text-lg sm:text-xl text-emerald-200 max-w-3xl mx-auto leading-relaxed font-medium">Enter your website URL. We will find 2 real competitors in your industry and compare your trust scores across 5 pillars.</p>
  </div>
</div>

<div class="max-w-4xl mx-auto px-6 py-16">
  <div class="bg-white border border-emerald-200 rounded-2xl shadow-xl p-8 text-center max-w-lg mx-auto">
    <p class="text-lg font-bold text-zinc-900 mb-2">Enter your website</p>
    <p class="text-zinc-600 mb-6 font-medium">We will auto-detect 2 real competitors in your industry.</p>
    <div class="space-y-4">
      <input id="yourUrl" type="text" placeholder="e.g. yourbusiness.co.uk" class="w-full rounded-xl border border-emerald-300 px-5 py-3.5 text-base font-medium text-zinc-800 placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-teal-500">
      <button onclick="runCompare()" id="compareBtn" class="w-full rounded-xl bg-teal-500 px-6 py-3.5 text-base font-bold text-white shadow-lg hover:bg-teal-400 transition flex items-center justify-center gap-2">
        <span id="btnText">Compare My Score →</span>
        <span id="btnSpinner" class="hidden inline-block w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
      </button>
    </div>
    <p id="inputError" class="hidden text-red-600 text-sm mt-2 font-medium">Please enter a valid website address</p>
    <p class="text-sm text-zinc-500 mt-4 font-medium">Free. No card. Results in seconds.</p>
  </div>
</div>

<div id="resultsSection" class="hidden bg-emerald-50 py-20 px-6">
  <div class="max-w-6xl mx-auto">
    <div class="text-center mb-12">
      <p class="text-sm font-bold uppercase tracking-[.2em] text-emerald-700 mb-3">Competitor Comparison</p>
      <h2 class="text-4xl sm:text-5xl font-extrabold text-zinc-900 mb-4">How you stack up</h2>
      <p id="comparisonContext" class="text-zinc-600 max-w-xl mx-auto font-medium">Scores out of 100 based on 42 trust signal checks.</p>
    </div>

    <div id="overallScores" class="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-10"></div>

    <div class="overflow-x-auto rounded-2xl border border-emerald-200 bg-white shadow-xl mb-10">
      <table class="w-full text-left">
        <thead>
          <tr class="bg-emerald-50">
            <th class="px-6 py-4 text-sm font-bold uppercase tracking-wider text-emerald-700">Pillar</th>
            <th class="px-6 py-4 text-sm font-bold uppercase tracking-wider text-teal-600">You</th>
            <th id="comp1Header" class="px-6 py-4 text-sm font-bold uppercase tracking-wider text-zinc-600">Competitor 1</th>
            <th id="comp2Header" class="px-6 py-4 text-sm font-bold uppercase tracking-wider text-zinc-600">Competitor 2</th>
          </tr>
        </thead>
        <tbody id="pillarBody"></tbody>
      </table>
    </div>

    <div class="rounded-2xl border border-emerald-200 bg-white shadow-xl p-8 mb-8">
      <p class="text-lg font-bold text-zinc-900 mb-6">Overall scores at a glance</p>
      <div id="barChart" class="space-y-4"></div>
    </div>

    <div class="rounded-2xl border-l-4 border-emerald-600 bg-white shadow-xl p-8 mb-6">
      <div class="flex items-center gap-3 mb-4">
        <span class="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center text-sm">✅</span>
        <div><p class="text-base font-bold text-zinc-900">Where you are winning</p><p class="text-sm text-zinc-600">Trust signals where you outperform competitors</p></div>
      </div>
      <div id="winningDiv"></div>
    </div>

    <div class="rounded-2xl border-l-4 border-amber-500 bg-white shadow-xl p-8 mb-6">
      <div class="flex items-center gap-3 mb-4">
        <span class="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center text-sm">⚡</span>
        <div><p class="text-base font-bold text-zinc-900">Where you can outperform them</p><p class="text-sm text-zinc-600">Gaps competitors are exploiting. Fix these to pull ahead.</p></div>
      </div>
      <div id="outperformDiv"></div>
    </div>

    <div class="rounded-2xl border-l-4 border-indigo-500 bg-white shadow-xl p-8 mb-6">
      <div class="flex items-center gap-3 mb-4">
        <span class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-sm">🔍</span>
        <div><p class="text-base font-bold text-zinc-900">How We Scored You</p><p class="text-sm text-zinc-600">Your website was checked against 9 trust standards. Each pass contributes to your score.</p></div>
      </div>
      <div id="standardsBreakdown" class="space-y-2"></div>
    </div>

    <div class="rounded-2xl bg-gradient-to-r from-emerald-50 to-teal-50 border border-teal-500 shadow-xl p-8">
      <div class="flex items-center gap-3 mb-4">
        <span class="w-8 h-8 rounded-full bg-teal-100 flex items-center justify-center text-sm">📊</span>
        <p class="text-base font-bold text-zinc-900">Competitive Trust Summary</p>
      </div>
      <div id="summaryDiv" class="text-zinc-700 leading-relaxed font-medium"></div>
      <div class="mt-6 text-center">
        <a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone?month=2026-09" class="rounded-xl bg-teal-500 px-6 py-3 text-base font-bold text-white shadow-lg hover:bg-teal-400 transition">Book a Free 20-Minute Review →</a>
      </div>
    </div>

    <div class="text-center mt-8">
      <a href="#" onclick="resetPage();return false;" class="text-zinc-500 hover:text-zinc-700 underline text-sm font-medium">← Compare a different website</a>
    </div>
  </div>
</div>

<footer class="bg-zinc-900 text-zinc-300 py-12 px-6 border-t border-zinc-800">
  <div class="max-w-6xl mx-auto">
    <div class="grid grid-cols-2 gap-10">
      <div><div class="flex items-center gap-2 text-lg font-extrabold mb-4"><span class="text-xl">🛡️</span> <span class="text-yellow-400">Trust Trigger Agency</span></div><p class="text-zinc-400 text-sm">Helping healthcare practices turn websites into patient booking engines.</p></div>
      <div><p class="text-sm font-bold uppercase tracking-wider text-emerald-400 mb-4">Service</p><ul class="space-y-3 text-sm font-medium"><li><a href="https://trust-trigger-api.onrender.com/home" class="text-zinc-300 hover:text-white">Home</a></li><li><a href="https://trust-trigger-api.onrender.com/extensive-report" class="text-zinc-300 hover:text-white">Extensive Report</a></li><li><a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone?month=2026-09" class="text-zinc-300 hover:text-white">Book a Review</a></li></ul></div>
    </div>
    <div class="border-t border-zinc-800 mt-8 pt-6 text-sm font-medium text-center"><p class="text-yellow-400">© 2025 Trust Trigger Agency™ · The Trust Trigger Transformation Method™</p></div>
  </div>
</footer>

<script>
function $(i){return document.getElementById(i);}
function h(e){e.classList.add('hidden');}
function s(e){e.classList.remove('hidden');}
function grade(score){if(score>=90)return'Excellent';if(score>=70)return'Good';if(score>=50)return'Average';if(score>=30)return'Weak';return'At Risk';}
function badgeHtml(s){var b=s>=75?'emerald':s>=45?'amber':'red';var cl={emerald:'background:#d1fae5;color:#047857;border-color:#a7f3d0',amber:'background:#fef3c7;color:#b45309;border-color:#fcd34d',red:'background:#fef2f2;color:#dc2626;border-color:#fecaca'};return'<span class="inline-flex items-center justify-center w-9 h-7 rounded-md text-sm font-bold border" style="'+cl[b]+'">'+s+'</span>';}
function scoreColor(s){if(s>=80)return'#22c55e';if(s>=60)return'#eab308';if(s>=40)return'#f97316';return'#ef4444';}
function isValidUrl(u){u=u.trim().toLowerCase();if(!u)return false;if(!u.startsWith('http'))u='https://'+u;try{new URL(u);var h=u.replace(/https?:\/\/(www\.)?/,'').split('/')[0].split('?')[0];if(!h||h.length<3)return false;if(h.indexOf('.')===-1)return false;return true;}catch(e){return false;}}
function hasValidScore(d){return d&&d.score&&d.score>0;}
function norm(u){u=u.trim();if(!u)return null;if(!u.startsWith('http'))u='https://'+u;try{new URL(u);return u;}catch(e){return null;}}
function bizName(u){return u.replace(/https?:\/\/(www\.)?/,'').split('/')[0].split('?')[0];}
function scanBusiness(n,u,e){return fetch('/api/v1/public/trust-snapshot',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({full_name:n,website:u,email:e})}).then(function(r){return r.json();});}
function findCompetitors(i,w,b){return fetch('/api/v1/public/find-competitors?industry='+encodeURIComponent(i)+'&website='+encodeURIComponent(w)+'&business_name='+encodeURIComponent(b)).then(function(r){return r.json();});}
function runCompare(){
  var url=$('yourUrl').value.trim();var err=$('inputError');
  if(!isValidUrl(url)){err.textContent='Please enter a valid website address (e.g. yourbusiness.co.uk)';err.classList.remove('hidden');return;}
  err.classList.add('hidden');
  if(!url.startsWith('http'))url='https://'+url;
  var bt=$('btnText'),sp=$('btnSpinner'),btn=$('compareBtn');
  bt.textContent='Analysing...';sp.classList.remove('hidden');btn.disabled=true;
  scanBusiness('Your Business',url,'you_'+Date.now()+'@temp.com').then(function(you){
    if(!you||you.error)throw new Error(you?you.error:'Scan failed');
    you.grade=you.grade||grade(you.score||0);
    bt.textContent='Finding competitors...';
    return findCompetitors(bizName(url),url,'Your Business').then(function(compResult){
      var comps=compResult.competitors||[];
      if(comps.length<2)comps=[{name:'Competitor A',site:''},{name:'Competitor B',site:''}];
      var c1=comps[0],c2=comps[1];
      bt.textContent='Scanning: '+c1.name+'...';
      return scanBusiness(c1.name,c1.site,'c1_'+Date.now()+'@temp.com').then(function(c1Data){
        bt.textContent='Scanning: '+c2.name+'...';
        return scanBusiness(c2.name,c2.site,'c2_'+Date.now()+'@temp.com').then(function(c2Data){
          bt.textContent='Compare My Score';sp.classList.add('hidden');btn.disabled=false;
          showResults(you,c1Data,c2Data,c1.name,c2.name,url);
        });
      });
    });
  }).catch(function(e){
    bt.textContent='Compare My Score';sp.classList.add('hidden');btn.disabled=false;
    err.textContent='Could not scan this website. Please check the URL and try again.';
    err.classList.remove('hidden');
  });
}
function showResults(you,c1Data,c2Data,c1name,c2name,url){
  h($('inputError'));s($('resultsSection'));
  var ys=you.score||0,cs1=hasValidScore(c1Data)?c1Data.score:0,cs2=hasValidScore(c2Data)?c2Data.score:0;
  var c1Valid=hasValidScore(c1Data);var c2Valid=hasValidScore(c2Data);
  var c1n=c1name||'Competitor 1',c2n=c2name||'Competitor 2';
  $('comparisonContext').textContent='Scores out of 100 based on 42 trust signal checks.';
  $('comp1Header').textContent=c1n;$('comp2Header').textContent=c2n;
  var sd=$('overallScores');sd.innerHTML='';
  var all=[{s:ys,n:bizName(url),isYou:true}];
  if(c1Valid)all.push({s:cs1,n:c1n,isYou:false});else all.push({s:0,n:c1n+' (unavailable)',isYou:false});
  if(c2Valid)all.push({s:cs2,n:c2n,isYou:false});else all.push({s:0,n:c2n+' (unavailable)',isYou:false});
  for(var i=0;i<all.length;i++){var a=all[i];sd.innerHTML+='<div class="rounded-2xl border border-emerald-200 bg-white shadow-xl p-6 text-center'+(a.isYou?' border-2 border-teal-500 bg-teal-50/20':'')+'"><p class="text-sm font-bold uppercase tracking-wider text-zinc-500 mb-1">'+(a.isYou?'You':'Competitor')+'</p><p class="text-4xl font-extrabold mb-1" style="color:'+scoreColor(a.s)+'">'+a.s+'</p><p class="text-xs text-zinc-400">/100</p><p class="text-sm text-zinc-600 mt-2 font-medium">'+a.n+'</p></div>';}
  var pillars=[{k:'Online Presence',l:'Online Presence',d:'Website visibility and reach'},{k:'Reputation',l:'Reputation',d:'Reviews and testimonials'},{k:'Engagement',l:'Engagement',d:'Social proof and interaction'},{k:'Transparency',l:'Transparency',d:'Clear policies and trust signals'},{k:'Technical Health',l:'Technical Health',d:'SSL, speed, mobile readiness'}];
  function gp(data,label){if(!data||!data.pillars)return null;for(var i=0;i<data.pillars.length;i++){if(data.pillars[i].label===label)return Math.round(data.pillars[i].percentage);}return null;}
  var tb=$('pillarBody');tb.innerHTML='';
  for(var pi=0;pi<pillars.length;pi++){var p=pillars[pi],yv=gp(you,p.k),c1v=c1Valid?gp(c1Data,p.k):null,c2v=c2Valid?gp(c2Data,p.k):null;var row='<tr class="border-b border-zinc-100"><td class="py-4 pr-4 font-medium text-zinc-800">'+p.l+'</td>';var av=[yv,c1v,c2v];for(var j=0;j<av.length;j++){row+='<td class="py-4 px-4"><div class="flex items-center gap-2">'+(av[j]!==null?badgeHtml(av[j]):'<span class="inline-flex items-center justify-center w-9 h-7 rounded-md text-sm font-bold border bg-zinc-100 text-zinc-400 border-zinc-200">-</span>')+'</div></td>';}row+='</tr>';tb.innerHTML+=row;}
  var bar=$('barChart');bar.innerHTML='';
  for(var bi=0;bi<all.length;bi++){var a2=all[bi];var barCol=scoreColor(a2.s);bar.innerHTML+='<div><div class="flex justify-between text-sm font-semibold mb-1"><span>'+(a2.isYou?'You':a2.n)+'</span><span style="color:'+barCol+'" class="font-bold">'+a2.s+'/100</span></div><div class="h-3 rounded-full bg-zinc-200 overflow-hidden"><div class="h-full rounded-full" style="width:'+a2.s+'%;background:'+barCol+'"></div></div></div>';}
  var wins=[],losses=[];
  for(var pi2=0;pi2<pillars.length;pi2++){var p2=pillars[pi2],yval=gp(you,p2.k);if(yval===null)continue;var compVals=[];if(c1Valid){var c1val=gp(c1Data,p2.k);if(c1val!==null)compVals.push({val:c1val,name:c1n});}if(c2Valid){var c2val=gp(c2Data,p2.k);if(c2val!==null)compVals.push({val:c2val,name:c2n});}if(compVals.length===0){wins.push({p:p2.l,y:yval});continue;}var bestComp=compVals[0];for(var cv=1;cv<compVals.length;cv++){if(compVals[cv].val>bestComp.val)bestComp=compVals[cv];}if(yval>=bestComp.val){wins.push({p:p2.l,y:yval});}else{losses.push({p:p2.l,y:yval,best:bestComp.val,d:bestComp.val-yval,w:bestComp.name});}}
  losses.sort(function(a,b){return b.d-a.d;});
  var wd=$('winningDiv');wd.innerHTML=wins.length===0?'<p class="text-zinc-600">You are not leading on any pillar yet.</p>':'';for(var wi=0;wi<wins.length;wi++){wd.innerHTML+='<div class="flex gap-3 text-sm font-medium text-zinc-700"><span class="text-emerald-600 font-bold">✓</span><p><strong>'+wins[wi].p+'</strong> — You score '+wins[wi].y+', ahead of competitors.</p></div>';}
  var od=$('outperformDiv');od.innerHTML=losses.length===0?'<p class="text-zinc-600">You are ahead across the board.</p>':'';var maxL=Math.min(losses.length,5);for(var li=0;li<maxL;li++){od.innerHTML+='<div class="flex gap-3 text-sm font-medium text-zinc-700"><span class="text-amber-500 font-bold">⚡</span><p><strong>'+losses[li].p+'</strong> — '+losses[li].w+' leads by '+losses[li].d+' points.</p></div>';}
  var sum=$('summaryDiv');var txt='';
  if(c1Valid||c2Valid){
    if(wins.length>0&&losses.length===0){txt+='You lead across all pillars against your competitors. ';}
    else if(wins.length>0){var wn=[];for(var wi2=0;wi2<wins.length;wi2++)wn.push(wins[wi2].p);txt+='You are ahead on <strong>'+wn.join(', ')+'</strong>. ';}else{txt+='You are not leading on any measurable pillar yet. ';}
    if(losses.length>0){txt+='Biggest opportunities: ';var tl=Math.min(losses.length,2);for(var li2=0;li2<tl;li2++){txt+='<strong>'+losses[li2].p+'</strong> ('+losses[li2].w+' leads by '+losses[li2].d+' pts)';if(li2<tl-1)txt+=', ';}txt+='. ';}
  }else{txt='Competitor data unavailable. Book a review for a full competitive analysis. ';}
  if(you.issues&&you.issues.length>0){txt+='Top issue for you: <strong>'+you.issues[0].title+'</strong>. ';}
  txt+='Need a deeper dive? <a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone?month=2026-09" style="color:#0d9488;text-decoration:underline;">Book a Free 20-Minute Review</a> for a full audit.';
  sum.innerHTML=txt;
  var sb=$('standardsBreakdown');sb.innerHTML='';var stds=you.standards||[];var passed=0,total=stds.length;for(var si=0;si<stds.length;si++){if(stds[si].passed)passed++;var st=stds[si];var icon=st.passed?'✅':'❌';var bg=st.passed?'background:#ecfdf5;border-color:#bbf7d0':'background:#fef2f2;border-color:#fecaca';var label=st.name.replace(/([A-Z])/g,' $1').replace(/^./,function(s){return s.toUpperCase();}).trim();if(st.name==='Https')label='HTTPS';if(st.name==='Cta')label='Clear CTAs';if(st.name==='Faq')label='FAQ Section';sb.innerHTML+='<div class="flex items-center gap-3 px-4 py-3 rounded-xl border" style="'+bg+'"><span>'+icon+'</span><span class="text-sm font-medium text-zinc-800">'+label+'</span><span class="ml-auto text-xs font-bold" style="color:'+(st.passed?'#059669':'#dc2626')+'">'+(st.passed?'✓ Passed':'✗ Failed')+'</span></div>';}
  sb.innerHTML+='<div class="flex justify-between px-4 pt-3 text-sm text-zinc-600 border-t border-zinc-200 mt-3"><span><strong>'+passed+'/'+total+'</strong> standards passed</span><span>Score: <strong>'+Math.round(passed/total*100)+'/100</strong></span></div>';
  $('resultsSection').scrollIntoView({behavior:'smooth',block:'start'});
}
function resetPage(){h($('resultsSection'));s($('inputError'));$('yourUrl').value='';window.scrollTo({top:0,behavior:'smooth'});}
</script>
</body>
</html>"""

@router.get("", response_class=HTMLResponse)
async def get_competitor_insights_page():
    return PAGE

@router.get("/", response_class=HTMLResponse)
async def get_competitor_insights_page_root():
    return PAGE
