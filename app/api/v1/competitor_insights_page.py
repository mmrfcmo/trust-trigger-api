"""Competitor Trust Insights page — served by the API with real competitor scanning."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
router = APIRouter(prefix="/competitor-insights", tags=["Public - Competitor Insights"])

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Competitor Trust Insights — Trust Trigger Agency</title>
  <meta name="description" content="Free competitor trust comparison. Enter your URL — we automatically find and compare 2 real competitors across 5 trust pillars.">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; }
    html, body { font-family: 'Inter', sans-serif; margin: 0; background: #f8fafb; color: #475569; }
    .hidden { display: none !important; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .spinner { display: inline-block; width: 20px; height: 20px; border: 2px solid rgba(255,255,255,.3); border-top-color: white; border-radius: 50%; animation: spin .6s linear infinite; vertical-align: middle; }
    .card { background: white; border: 1px solid #e2e8f0; border-radius: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.06); padding: 24px; }
    input { padding: 14px 16px; border-radius: 12px; border: 1px solid #e2e8f0; font-size: 14px; outline: none; width: 100%; }
    input:focus { border-color: #00d4aa; box-shadow: 0 0 0 2px rgba(0,212,170,.2); }
    .btn { background: linear-gradient(135deg, #00d4aa, #10b981); color: white; font-weight: 600; border-radius: 12px; padding: 14px 24px; font-size: 14px; border: none; cursor: pointer; box-shadow: 0 4px 14px rgba(0,212,170,.25); display: inline-flex; align-items: center; justify-content: center; gap: 8px; }
    .btn:hover { box-shadow: 0 6px 24px rgba(0,212,170,.3); transform: scale(1.02); }
    .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
    table { width: 100%; text-align: left; border-collapse: collapse; }
    th { padding: 16px 20px; font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; }
    td { padding: 12px 20px; border-bottom: 1px solid #e2e8f0; font-size: 14px; }
    tr:last-child td { border-bottom: none; }
    .badge { display: inline-flex; align-items: center; justify-content: center; width: 36px; height: 28px; border-radius: 6px; font-size: 13px; font-weight: 700; border: 1px solid; }
    .bar-bg { height: 12px; border-radius: 999px; background: rgba(0,0,0,.06); overflow: hidden; }
    .bar-fill { height: 100%; border-radius: 999px; }
    .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
    @media (max-width: 640px) { .grid-3 { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div style="background:#0b1120;border-bottom:1px solid rgba(255,255,255,.05);position:fixed;top:0;left:0;right:0;z-index:50;height:64px;display:flex;align-items:center;padding:0 24px;">
    <div style="max-width:1200px;margin:0 auto;width:100%;display:flex;align-items:center;justify-content:space-between;">
      <a href="https://srv16.aisoftllc.com/agent_sites/7322820b2e5f.html" style="display:flex;align-items:center;gap:8px;font-size:15px;font-weight:600;color:white;text-decoration:none;">
        <span style="font-size:22px;">🛡️</span> Trust Trigger Agency
      </a>
      <a href="https://srv16.aisoftllc.com/agent_sites/f137db9d5899.html" class="btn" style="padding:8px 18px;font-size:13px;text-decoration:none;">
        Get Free Snapshot →
      </a>
    </div>
  </div>

  <div style="padding:120px 24px 80px;background:#0b1120;color:white;text-align:center;">
    <div style="max-width:1200px;margin:0 auto;">
      <div style="width:64px;height:64px;margin:0 auto 16px;border-radius:16px;background:linear-gradient(135deg,#00d4aa,#10b981);display:flex;align-items:center;justify-content:center;box-shadow:0 4px 20px rgba(0,212,170,.2);">
        <span style="font-size:28px;">⚔️</span>
      </div>
      <p style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.15em;color:#00d4aa;margin:0 0 12px;">Free Competitive Analysis</p>
      <h1 style="font-size:40px;font-weight:700;letter-spacing:-.02em;line-height:1.05;margin:0 0 16px;">
        Competitor <span style="background:linear-gradient(135deg,#00d4aa,#10b981);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Trust Insights</span>
      </h1>
      <p style="font-size:18px;color:#a1a1aa;max-width:600px;margin:0 auto;font-weight:300;">Enter your website URL. We will find 2 real competitors in your industry and compare your trust scores across 5 pillars.</p>
    </div>
  </div>

  <div style="padding:48px 0;background:white;border-bottom:1px solid #e2e8f0;">
    <div style="max-width:560px;margin:0 auto;padding:0 24px;">
      <div class="card" style="text-align:center;padding:32px;">
        <p style="font-size:14px;font-weight:600;color:#0f172a;margin:0 0 6px;">Enter your website</p>
        <p style="font-size:13px;color:#94a3b8;margin:0 0 20px;">We will auto-detect 2 real competitors in your industry.</p>
        <div style="display:flex;flex-direction:column;gap:12px;">
          <input id="yourUrl" type="url" placeholder="e.g. yourbusiness.co.uk">
          <button id="compareBtn" class="btn" style="justify-content:center;" onclick="runCompare()">
            <span id="btnText">Compare My Score →</span>
            <span id="btnSpinner" class="hidden spinner"></span>
          </button>
        </div>
        <p id="inputError" class="hidden" style="color:#ef4444;font-size:13px;margin:8px 0 0;">Please enter a valid URL</p>
        <p style="font-size:12px;color:#94a3b8;margin:12px 0 0;">Free. No card. Results in seconds.</p>
      </div>
    </div>
  </div>

  <div id="resultsSection" class="hidden" style="padding:80px 0;background:white;">
    <div style="max-width:1200px;margin:0 auto;padding:0 24px;">
      <div style="text-align:center;margin-bottom:48px;">
        <p style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.15em;color:#94a3b8;margin:0 0 8px;">Competitor Comparison</p>
        <h2 style="font-size:32px;font-weight:700;color:#0f172a;margin:0 0 12px;">How you stack up</h2>
        <p id="comparisonContext" style="color:#94a3b8;max-width:500px;margin:0 auto;font-size:15px;">Scores out of 100 based on 42 trust signal checks.</p>
      </div>

      <div id="overallScores" class="grid-3" style="margin-bottom:40px;"></div>

      <div style="overflow-x:auto;border-radius:16px;border:1px solid #e2e8f0;background:white;box-shadow:0 1px 3px rgba(0,0,0,.06);margin-bottom:40px;">
        <table>
          <thead>
            <tr style="background:#f8fafc;">
              <th>Pillar</th>
              <th style="color:#0d9488;">You</th>
              <th id="comp1Header">Competitor 1</th>
              <th id="comp2Header">Competitor 2</th>
            </tr>
          </thead>
          <tbody id="pillarBody"></tbody>
        </table>
      </div>

      <div class="card" style="margin-bottom:40px;">
        <p style="font-size:14px;font-weight:600;color:#0f172a;margin:0 0 16px;">Overall scores at a glance</p>
        <div id="barChart" style="display:flex;flex-direction:column;gap:12px;"></div>
      </div>

      <div class="card" style="margin-bottom:24px;border-left:4px solid #10b981;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
          <span style="width:32px;height:32px;border-radius:50%;background:#d1fae5;display:flex;align-items:center;justify-content:center;">✅</span>
          <div>
            <p style="font-size:14px;font-weight:600;color:#0f172a;margin:0;">Where you are winning</p>
            <p style="font-size:12px;color:#64748b;margin:2px 0 0;">Trust signals where you outperform competitors</p>
          </div>
        </div>
        <div id="winningDiv" style="display:flex;flex-direction:column;gap:8px;"></div>
      </div>

      <div class="card" style="margin-bottom:24px;border-left:4px solid #f59e0b;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
          <span style="width:32px;height:32px;border-radius:50%;background:#fef3c7;display:flex;align-items:center;justify-content:center;">⚡</span>
          <div>
            <p style="font-size:14px;font-weight:600;color:#0f172a;margin:0;">Where you can outperform them</p>
            <p style="font-size:12px;color:#64748b;margin:2px 0 0;">Gaps competitors are exploiting. Fix these to pull ahead.</p>
          </div>
        </div>
        <div id="outperformDiv" style="display:flex;flex-direction:column;gap:8px;"></div>
      </div>

      <!-- NEW: Standards breakdown -->
      <div class="card" style="margin-bottom:24px;border-left:4px solid #6366f1;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
          <span style="width:32px;height:32px;border-radius:50%;background:#e0e7ff;display:flex;align-items:center;justify-content:center;">🔍</span>
          <div>
            <p style="font-size:14px;font-weight:600;color:#0f172a;margin:0;">How We Scored You</p>
            <p style="font-size:12px;color:#64748b;margin:2px 0 0;">Your website was checked against 9 trust standards. Each pass contributes to your score.</p>
          </div>
        </div>
        <div id="standardsBreakdown" style="display:flex;flex-direction:column;gap:6px;"></div>
      </div>

      <div class="card" style="background:linear-gradient(135deg,#f0fdfa,#ecfdf5);border-color:#14b8a6;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
          <span style="width:32px;height:32px;border-radius:50%;background:#ccfbf1;display:flex;align-items:center;justify-content:center;">📊</span>
          <p style="font-size:14px;font-weight:600;color:#0f172a;margin:0;">Competitive Trust Summary</p>
        </div>
        <div id="summaryDiv" style="font-size:14px;color:#334155;line-height:1.7;"></div>
        <div style="margin-top:20px;">
          <a href="#" class="btn" style="font-size:13px;padding:12px 24px;text-decoration:none;">Book a Free 20-Minute Review →</a>
        </div>
      </div>

      <div style="text-align:center;margin-top:32px;">
        <a href="#" onclick="resetPage();return false;" style="font-size:13px;color:#94a3b8;text-decoration:underline;">← Compare a different website</a>
      </div>
    </div>
  </div>

  <footer style="background:#060a14;color:#71717a;padding:48px 24px;border-top:1px solid rgba(255,255,255,.05);">
    <div style="max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;">
      <div style="display:flex;align-items:center;gap:8px;">
        <span style="font-size:18px;">🛡️</span>
        <span style="color:white;font-size:13px;font-weight:600;">Trust Trigger Agency</span>
      </div>
      <p style="font-size:11px;color:#52525b;">Copyright 2025 Trust Trigger Agency</p>
    </div>
  </footer>

<script>
function $(id) { return document.getElementById(id); }
function hide(el) { el.classList.add('hidden'); }
function show(el) { el.classList.remove('hidden'); }
function grade(score) {
  if (score >= 90) return 'Excellent';
  if (score >= 70) return 'Good';
  if (score >= 50) return 'Average';
  if (score >= 30) return 'Weak';
  return 'At Risk';
}
function badgeHtml(score) {
  var b = score >= 75 ? 'emerald' : score >= 45 ? 'amber' : 'red';
  var colors = { emerald: 'background:#d1fae5;color:#047857;border-color:#a7f3d0', amber: 'background:#fef3c7;color:#b45309;border-color:#fcd34d', red: 'background:#fef2f2;color:#dc2626;border-color:#fecaca' };
  return '<span class="badge" style="' + colors[b] + '">' + score + '</span>';
}
function norm(u) { u = u.trim(); if (!u) return null; if (!u.startsWith('http')) u = 'https://' + u; try { new URL(u); return u; } catch(e) { return null; } }
function bizName(u) { return u.replace(/https?:\/\/(www\.)?/, '').split('/')[0].split('?')[0]; }
function scanBusiness(name, website, email) {
  return fetch('/api/v1/public/trust-snapshot', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ full_name: name, website: website, email: email }) }).then(function(r) { return r.json(); });
}
function findCompetitors(industry, website, businessName) {
  return fetch('/api/v1/public/find-competitors?industry=' + encodeURIComponent(industry) + '&website=' + encodeURIComponent(website) + '&business_name=' + encodeURIComponent(businessName)).then(function(r) { return r.json(); });
}
function runCompare() {
  var url = norm($('yourUrl').value);
  var err = $('inputError');
  if (!url) { err.classList.remove('hidden'); return; }
  err.classList.add('hidden');
  var bt = $('btnText'), sp = $('btnSpinner'), btn = $('compareBtn');
  bt.textContent = 'Analysing...'; sp.classList.remove('hidden'); btn.disabled = true;
  var yourEmail = 'you_' + Date.now() + '@temp.com';
  scanBusiness('Your Business', url, yourEmail).then(function(you) {
    if (!you || you.error) throw new Error(you ? you.error : 'Scan failed');
    you.displayName = 'You - ' + bizName(url);
    you.grade = you.grade || grade(you.score || 0);
    bt.textContent = 'Finding competitors...';
    return findCompetitors(bizName(url), url, 'Your Business').then(function(compResult) {
      var comps = compResult.competitors || [];
      if (comps.length < 2) comps = [{ name: 'Competitor A', site: '' }, { name: 'Competitor B', site: '' }];
      var c1 = comps[0], c2 = comps[1];
      bt.textContent = 'Scanning: ' + c1.name + '...';
      return scanBusiness(c1.name, c1.site, 'c1_' + Date.now() + '@temp.com').then(function(c1Data) {
        bt.textContent = 'Scanning: ' + c2.name + '...';
        return scanBusiness(c2.name, c2.site, 'c2_' + Date.now() + '@temp.com').then(function(c2Data) {
          bt.textContent = 'Compare My Score'; sp.classList.add('hidden'); btn.disabled = false;
          showResults(you, c1Data, c2Data, c1.name, c2.name);
        });
      });
    });
  }).catch(function(e) {
    bt.textContent = 'Compare My Score'; sp.classList.add('hidden'); btn.disabled = false;
    alert('Error: ' + (e.message || 'Could not scan. Please check the URL and try again.'));
  });
}
function showResults(you, c1Data, c2Data, c1name, c2name) {
  hide($('inputError')); show($('resultsSection'));
  var ys = you.score || 0, cs1 = c1Data && c1Data.score ? c1Data.score : 0, cs2 = c2Data && c2Data.score ? c2Data.score : 0;
  var c1n = c1name || 'Competitor 1', c2n = c2name || 'Competitor 2';
  $('comparisonContext').innerHTML = 'Your website was scanned against competitors. Scores out of 100 based on 42 trust signal checks.';
  $('comp1Header').textContent = c1n; $('comp2Header').textContent = c2n;
  var sd = $('overallScores'); sd.innerHTML = '';
  var all = [{ s: ys, n: 'You - ' + (you.displayName || 'Your Business'), isYou: true }, { s: cs1, n: c1n, isYou: false }, { s: cs2, n: c2n, isYou: false }];
  for (var i = 0; i < all.length; i++) {
    var a = all[i];
    sd.innerHTML += '<div class="card" style="text-align:center;padding:20px;' + (a.isYou ? 'border:2px solid #14b8a6;background:rgba(20,184,166,.04)' : '') + '"><p style="font-size:11px;font-weight:600;text-transform:uppercase;color:' + (a.isYou ? '#0d9488' : '#94a3b8') + ';margin:0 0 4px;">' + (a.isYou ? 'You' : 'Competitor') + '</p><p style="font-size:36px;font-weight:700;color:' + (a.isYou ? '#0f766e' : '#0f172a') + ';margin:0;">' + a.s + '</p><p style="font-size:10px;color:#94a3b8;margin:0;">/100</p><p style="font-size:13px;color:#64748b;margin:6px 0 0;">' + a.n + '</p></div>';
  }
  var pillars = [{k:'Online Presence',l:'Online Presence',d:'Website visibility and reach'},{k:'Reputation',l:'Reputation',d:'Reviews and testimonials'},{k:'Engagement',l:'Engagement',d:'Social proof and interaction'},{k:'Transparency',l:'Transparency',d:'Clear policies and trust signals'},{k:'Technical Health',l:'Technical Health',d:'SSL, speed, mobile readiness'}];
  function gp(data,label){if(!data||!data.pillars)return null;for(var i=0;i<data.pillars.length;i++){if(data.pillars[i].label===label)return Math.round(data.pillars[i].percentage);}return null;}
  var tb = $('pillarBody'); tb.innerHTML = '';
  for (var pi = 0; pi < pillars.length; pi++) {
    var p = pillars[pi], yv = gp(you,p.k), c1v = gp(c1Data,p.k), c2v = gp(c2Data,p.k);
    var vals = [yv,c1v,c2v], mx = -1;
    for (var vi = 0; vi < vals.length; vi++) { if(vals[vi]!==null && vals[vi] > mx) mx = vals[vi]; }
    var row = '<tr><td><p style="font-weight:500;color:#0f172a;margin:0;">' + p.l + '</p><p style="font-size:11px;color:#94a3b8;margin:2px 0 0;">' + p.d + '</p></td>';
    var av = [yv,c1v,c2v];
    for (var j = 0; j < av.length; j++) {
      row += '<td><div style="display:flex;align-items:center;gap:4px;">' + (av[j]!==null ? badgeHtml(av[j]) : '<span class="badge" style="background:#f1f5f9;color:#94a3b8;border-color:#e2e8f0;">-</span>') + (av[j]!==null && av[j]===mx && mx>-1 ? '<span>🥇</span>' : '') + '</div></td>';
    }
    row += '</tr>'; tb.innerHTML += row;
  }
  var bar = $('barChart'); bar.innerHTML = '';
  for (var bi = 0; bi < all.length; bi++) { var a2 = all[bi]; bar.innerHTML += '<div><div style="display:flex;justify-content:space-between;font-size:14px;margin-bottom:4px;"><span style="font-weight:500;color:'+(a2.isYou?'#0f766e':'#64748b')+';">'+(a2.isYou?'You':a2.n)+'</span><span style="font-weight:700;color:'+(a2.isYou?'#0f766e':'#334155')+';">'+a2.s+'/100</span></div><div class="bar-bg"><div class="bar-fill" style="width:'+a2.s+'%;background:'+(a2.isYou?'linear-gradient(135deg,#00d4aa,#10b981)':'#d4d4d8')+';"></div></div></div>'; }
  var wins = [], losses = [];
  for (var pi2 = 0; pi2 < pillars.length; pi2++) { var p2 = pillars[pi2], yval = gp(you,p2.k), c1val = gp(c1Data,p2.k), c2val = gp(c2Data,p2.k); if(yval===null)continue; var compVals=[]; if(c1val!==null)compVals.push({val:c1val,name:c1n}); if(c2val!==null)compVals.push({val:c2val,name:c2n}); if(compVals.length===0){wins.push({p:p2.l,y:yval});continue;} var bestComp=compVals[0]; for(var cv=1;cv<compVals.length;cv++){if(compVals[cv].val>bestComp.val)bestComp=compVals[cv];} if(yval>=bestComp.val){wins.push({p:p2.l,y:yval});}else{losses.push({p:p2.l,y:yval,best:bestComp.val,d:bestComp.val-yval,w:bestComp.name});} }
  losses.sort(function(a,b){return b.d-a.d;});
  var wd = $('winningDiv'); wd.innerHTML = wins.length===0?'<p style="font-size:14px;color:#64748b;">You are not leading on any pillar yet.</p>':''; for(var wi=0;wi<wins.length;wi++){wd.innerHTML+='<div style="display:flex;gap:8px;font-size:14px;"><span style="color:#10b981;">✓</span><p style="margin:0;"><strong>'+wins[wi].p+'</strong> &mdash; You score '+wins[wi].y+', ahead of competitors.</p></div>';}
  var od = $('outperformDiv'); od.innerHTML = losses.length===0?'<p style="font-size:14px;color:#64748b;">You are ahead across the board.</p>':''; var maxL=Math.min(losses.length,5); for(var li=0;li<maxL;li++){od.innerHTML+='<div style="display:flex;gap:8px;font-size:14px;"><span style="color:#f59e0b;">⚡</span><p style="margin:0;"><strong>'+losses[li].p+'</strong> &mdash; '+losses[li].w+' leads by '+losses[li].d+' points.</p></div>';}
  var sum = $('summaryDiv'); var txt = ''; if(wins.length>0){var wn=[];for(var wi2=0;wi2<wins.length;wi2++)wn.push(wins[wi2].p);txt+='You are ahead on <strong>'+wn.join(', ')+'</strong>. ';}else{txt+='You are not leading on any pillar yet. ';} if(losses.length>0){txt+='Biggest opportunities: ';var tl=Math.min(losses.length,2);for(var li2=0;li2<tl;li2++){txt+='<strong>'+losses[li2].p+'</strong> ('+losses[li2].w+' leads by '+losses[li2].d+' pts)';if(li2<tl-1)txt+=', ';}txt+='. ';} if(you.issues&&you.issues.length>0){txt+='Top issue for you: <strong>'+you.issues[0].title+'</strong>. ';} txt+='Need a deeper dive? <a href="#" style="color:#0d9488;text-decoration:underline;">Book a Free 20-Minute Review</a> for a full audit.'; sum.innerHTML = txt;

  // Standards breakdown
  var sb = $('standardsBreakdown'); sb.innerHTML = '';
  var stds = you.standards || [];
  var passed = 0, total = stds.length;
  for (var si = 0; si < stds.length; si++) {
    if (stds[si].passed) passed++;
    var st = stds[si];
    var icon = st.passed ? '✅' : '❌';
    var bg = st.passed ? 'background:#ecfdf5;border-color:#bbf7d0' : 'background:#fef2f2;border-color:#fecaca';
    var label = st.name.replace(/([A-Z])/g, ' $1').replace(/^./, function(s){ return s.toUpperCase(); }).trim();
    if (st.name === 'Https') label = 'HTTPS';
    if (st.name === 'Cta') label = 'Clear CTAs';
    if (st.name === 'Faq') label = 'FAQ Section';
    if (st.name === 'Service Pages') label = 'Service Pages';
    if (st.name === 'Privacy Policy') label = 'Privacy Policy';
    if (st.name === 'Mobile Responsive') label = 'Mobile Responsive';
    sb.innerHTML += '<div style="display:flex;align-items:center;gap:10px;padding:8px 12px;border-radius:8px;border:1px solid;' + bg + '">' +
      '<span>' + icon + '</span>' +
      '<span style="font-size:14px;font-weight:500;color:#0f172a;">' + label + '</span>' +
      '<span style="margin-left:auto;font-size:12px;font-weight:600;color:' + (st.passed ? '#059669' : '#dc2626') + ';">' + (st.passed ? '✓ Passed' : '✗ Failed') + '</span></div>';
  }
  sb.innerHTML += '<div style="display:flex;justify-content:space-between;padding:10px 12px 0;font-size:13px;color:#64748b;border-top:1px solid #e2e8f0;margin-top:8px;">' +
    '<span><strong>' + passed + '/' + total + '</strong> standards passed</span>' +
    '<span>Score: <strong>' + Math.round(passed/total*100) + '/100</strong></span></div>';

  $('resultsSection').scrollIntoView({behavior:'smooth',block:'start'});
}
function resetPage() { hide($('resultsSection')); show($('inputError')); $('yourUrl').value = ''; window.scrollTo({top:0,behavior:'smooth'}); }
</script>
</body>
</html>"""

@router.get("", response_class=HTMLResponse)
async def get_competitor_insights_page():
    return PAGE

@router.get("/", response_class=HTMLResponse)
async def get_competitor_insights_page_root():
    return PAGE
