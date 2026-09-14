"""Main Trust Trigger Agency Homepage — served by the API with on-page trust snapshot scan."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
router = APIRouter(prefix="/home", tags=["Public - Homepage"])

PAGE = """<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Trust Trigger Agency</title>
<meta name="description" content="Free Trust Snapshot for healthcare practices. See your trust score in 30 seconds and get a free 20-minute review call.">
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
<a href="/home" class="flex items-center gap-2 text-2xl font-extrabold text-yellow-400"><span class="text-3xl">🛡️</span> Trust Trigger Agency</a>
<div class="flex items-center gap-5">
<a href="#contact" class="text-base font-semibold text-zinc-300 hover:text-white">Contact</a>
<a href="#snapshot" class="rounded-lg bg-teal-500 px-5 py-2.5 text-base font-semibold text-white hover:bg-teal-400">Get Free Snapshot →</a>
</div>
</div>
</nav>

<div class="h-20"></div>

<!-- HERO -->
<section class="green1 text-white py-24 sm:py-32 px-6">
<div class="max-w-6xl mx-auto text-center">
<p class="text-sm font-bold uppercase tracking-[.2em] text-teal-300 mb-4">Trust Trigger Transformation Method™</p>
<h1 class="text-4xl sm:text-5xl md:text-7xl font-extrabold tracking-tight mb-6 leading-[1.05]">Is your healthcare practice<br>losing patients to <span class="gt">your website?</span></h1>
<p class="text-lg sm:text-xl text-emerald-200 max-w-3xl mx-auto leading-relaxed font-medium mb-10">Get a free Trust Snapshot in 30 seconds, then book a 20-minute call and we'll screenshare your full Extensive Trust Report together — at no cost.</p>
<div class="flex flex-col sm:flex-row items-center justify-center gap-4">
<a href="#snapshot" class="inline-flex items-center gap-2 rounded-xl bg-teal-500 px-7 py-4 text-base font-bold text-white shadow-xl hover:bg-teal-400 transition">Get Your Free Trust Snapshot →</a>
<a href="#about" class="inline-flex items-center gap-2 rounded-xl border border-emerald-400 px-7 py-4 text-base font-bold text-emerald-100 hover:bg-emerald-800 transition">See what we do</a>
</div>
</div>
</section>

<!-- ABOUT -->
<section id="about" class="py-20 sm:py-28 px-6 bg-white">
<div class="max-w-6xl mx-auto">
<div class="max-w-3xl mx-auto text-center">
<p class="text-sm font-bold uppercase tracking-[.2em] text-emerald-700 mb-3">About</p>
<h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-zinc-900 mb-6">We help healthcare practices turn website visitors into booked patients.</h2>
<p class="text-base sm:text-lg text-zinc-600 leading-relaxed font-medium">Most healthcare websites look fine — but to a first-time patient, they don't inspire enough confidence to pick up the phone. Every gap costs you new patients.</p>
</div>
</div>
</section>

<!-- HOW IT WORKS -->
<section class="py-20 sm:py-28 px-6 bg-emerald-50">
<div class="max-w-6xl mx-auto">
<p class="text-sm font-bold uppercase tracking-[.2em] text-emerald-700 text-center mb-3">How It Works</p>
<h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-zinc-900 text-center mb-16">Three steps to clarity.</h2>
<div class="grid grid-cols-1 sm:grid-cols-3 gap-8">
<div class="rounded-2xl border border-emerald-200 bg-white p-8 text-center shadow-sm"><div class="w-14 h-14 rounded-full bg-emerald-100 text-2xl flex items-center justify-center mx-auto mb-5">🎯</div><p class="text-sm font-bold uppercase tracking-wider text-emerald-700 mb-2">Step 1</p><h3 class="text-xl font-bold text-zinc-900 mb-3">Data-driven diagnosis</h3><p class="text-zinc-600 text-sm leading-relaxed">42 checks across 5 pillars. No guesswork — every issue has evidence and a clear fix priority.</p></div>
<div class="rounded-2xl border border-emerald-200 bg-white p-8 text-center shadow-sm"><div class="w-14 h-14 rounded-full bg-emerald-100 text-2xl flex items-center justify-center mx-auto mb-5">🔧</div><p class="text-sm font-bold uppercase tracking-wider text-emerald-700 mb-2">Step 2</p><h3 class="text-xl font-bold text-zinc-900 mb-3">Fix what's broken</h3><p class="text-zinc-600 text-sm leading-relaxed">Not every practice needs a new website. We can optimise or build. You decide.</p></div>
<div class="rounded-2xl border border-emerald-200 bg-white p-8 text-center shadow-sm"><div class="w-14 h-14 rounded-full bg-emerald-100 text-2xl flex items-center justify-center mx-auto mb-5">📈</div><p class="text-sm font-bold uppercase tracking-wider text-emerald-700 mb-2">Step 3</p><h3 class="text-xl font-bold text-zinc-900 mb-3">Proven results</h3><p class="text-zinc-600 text-sm leading-relaxed">Documented before/after for every client. We prove what changed.</p></div>
</div>
</div>
</section>

<!-- SNAPSHOT SECTION (on-page scan) -->
<section id="snapshot" class="py-20 sm:py-28 px-6 bg-white">
<div class="max-w-6xl mx-auto">
<p class="text-sm font-bold uppercase tracking-[.2em] text-emerald-700 text-center mb-3">Your Free Trust Snapshot</p>
<h2 id="snapHeading" class="text-3xl sm:text-4xl font-extrabold tracking-tight text-zinc-900 text-center mb-4">See your score in 30 seconds</h2>
<p id="snapSubtext" class="text-center text-zinc-500 mb-12 font-medium">Enter your details below and get an instant trust analysis.</p>

<!-- EXAMPLE SCORE CARD (black bg, score below 60) -->
<div id="exampleCard" class="max-w-4xl mx-auto mb-12">
<div class="rounded-2xl bg-zinc-900 shadow-xl p-8">
<p class="text-sm font-bold uppercase tracking-[.2em] text-zinc-400 text-center mb-6">Example Snapshot</p>
<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
<div class="text-center lg:col-span-1">
<div class="text-7xl font-extrabold text-red-400 mb-2">48</div>
<p class="text-lg font-bold text-zinc-100 mb-1">Trust Score</p>
<p class="text-sm text-zinc-400 leading-relaxed">Your website has significant trust gaps that are likely costing you patient enquiries every day.</p>
</div>
<div class="lg:col-span-2 space-y-3">
<div><div class="flex items-center justify-between mb-1"><span class="text-sm font-medium text-zinc-300">Credibility</span><span class="text-sm font-semibold text-amber-400">45%</span></div><div class="w-full h-2.5 bg-zinc-700 rounded-full overflow-hidden"><div class="h-full rounded-full bg-amber-500" style="width:45%"></div></div></div>
<div><div class="flex items-center justify-between mb-1"><span class="text-sm font-medium text-zinc-300">Social Proof</span><span class="text-sm font-semibold text-red-400">25%</span></div><div class="w-full h-2.5 bg-zinc-700 rounded-full overflow-hidden"><div class="h-full rounded-full bg-red-500" style="width:25%"></div></div></div>
<div><div class="flex items-center justify-between mb-1"><span class="text-sm font-medium text-zinc-300">Authority</span><span class="text-sm font-semibold text-amber-400">55%</span></div><div class="w-full h-2.5 bg-zinc-700 rounded-full overflow-hidden"><div class="h-full rounded-full bg-amber-500" style="width:55%"></div></div></div>
<div><div class="flex items-center justify-between mb-1"><span class="text-sm font-medium text-zinc-300">Clarity</span><span class="text-sm font-semibold text-amber-400">40%</span></div><div class="w-full h-2.5 bg-zinc-700 rounded-full overflow-hidden"><div class="h-full rounded-full bg-amber-500" style="width:40%"></div></div></div>
<div><div class="flex items-center justify-between mb-1"><span class="text-sm font-medium text-zinc-300">Conversion</span><span class="text-sm font-semibold text-red-400">30%</span></div><div class="w-full h-2.5 bg-zinc-700 rounded-full overflow-hidden"><div class="h-full rounded-full bg-red-500" style="width:30%"></div></div></div>
</div>
</div>
<div class="mt-6 rounded-xl border border-red-800 bg-red-950 p-5">
<p class="text-sm font-bold text-red-300 mb-3">&#9888;&#65039; Top Issues</p>
<ol class="space-y-2 text-sm text-red-400 list-decimal list-inside font-medium">
<li>Homepage value proposition unclear — visitors can't immediately tell what you do</li>
<li>No visible reviews or testimonials — your best social proof is hidden</li>
<li>Booking CTA is buried or generic — doesn't motivate action</li>
</ol>
</div>
</div>
</div>

<div class="max-w-lg mx-auto">
<div class="rounded-2xl border border-emerald-200 bg-emerald-50 shadow-xl p-6 sm:p-8">
<div class="space-y-4">
<div><input id="snapName" type="text" placeholder="Your full name" class="w-full rounded-xl border border-emerald-300 px-5 py-3.5 text-base font-medium text-zinc-800 placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"></div>
<div><input id="snapWebsite" type="text" placeholder="yourpractice.co.uk" class="w-full rounded-xl border border-emerald-300 px-5 py-3.5 text-base font-medium text-zinc-800 placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"></div>
<div><input id="snapEmail" type="email" placeholder="info@yourpractice.co.uk" class="w-full rounded-xl border border-emerald-300 px-5 py-3.5 text-base font-medium text-zinc-800 placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"></div>
<button onclick="runSnapshot()" id="snapBtn" class="w-full rounded-xl bg-teal-500 px-6 py-3.5 text-base font-bold text-white shadow-lg hover:bg-teal-400 transition flex items-center justify-center gap-2">
<span id="snapBtnText">Get My Score →</span>
<span id="snapBtnSpin" class="hidden inline-block w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
</button>
</div>
<p id="snapError" class="hidden text-red-600 text-sm mt-3 text-center font-medium">Please fill in all fields with valid info.</p>
<p class="text-sm text-zinc-500 mt-4 text-center font-medium">Free. No card. Takes 30 seconds.</p>
</div>
</div>

<!-- RESULTS (replaces example card on scan) -->
<div id="snapResults" class="hidden mt-16 max-w-4xl mx-auto">
<div class="rounded-2xl bg-zinc-900 shadow-xl p-8 mb-8 text-center">
<p class="text-sm font-bold uppercase tracking-[.2em] text-teal-400 mb-2">Your Trust Snapshot</p>
<div class="text-7xl font-extrabold mb-2" id="snapScoreColor"><span id="snapScore">0</span></div>
<p class="text-lg font-bold text-zinc-100 mb-1"><span id="snapGrade">—</span></p>
<p id="snapGradeDesc" class="text-zinc-400 max-w-lg mx-auto">Assessment complete. Review the findings below.</p>
</div>

<div id="snapPillars" class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8"></div>

<div class="rounded-2xl bg-zinc-900 shadow-xl p-8 mb-6">
<h3 class="text-lg font-bold text-zinc-100 mb-4">&#9888;&#65039; Top Issues Found</h3>
<div id="snapIssues" class="space-y-3"></div>
</div>

<div class="rounded-2xl bg-zinc-900 shadow-xl p-8 mb-6">
<h3 class="text-lg font-bold text-zinc-100 mb-4">&#128295; Priority Actions</h3>
<div id="snapActions" class="space-y-3"></div>
</div>

<div class="rounded-2xl border border-teal-500 bg-gradient-to-r from-emerald-900 to-teal-900 shadow-xl p-8 text-center">
<p class="text-2xl font-bold text-white mb-4">Surprised with your score?</p>
<p class="text-lg text-zinc-300 mb-6">Let's go through your full report together and we'll show you how to improve your score quickly to convert more enquiries.</p>
<a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone?month=2026-09" class="inline-flex items-center gap-2 rounded-xl bg-teal-500 px-8 py-4 text-lg font-bold text-white shadow-xl hover:bg-teal-400 transition">Book A Free 20 Minute Review →</a>
</div>
</div>
</div>
</section>

<!-- REAL RESULTS -->
<section class="py-20 sm:py-28 px-6 bg-emerald-50">
<div class="max-w-6xl mx-auto">
<p class="text-sm font-bold uppercase tracking-[.2em] text-emerald-700 text-center mb-3">Real Results</p>
<h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-zinc-900 text-center mb-12">Practices like yours, transformed</h2>
<div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
<div class="rounded-2xl border border-emerald-200 bg-white p-8 shadow-sm"><p class="text-yellow-400 text-lg mb-1">&#9733;&#9733;&#9733;&#9733;&#9733;</p><p class="text-zinc-700 italic mb-4 leading-relaxed">"Calls went from 3 a week to 14. Trust score went from 42 to 91."</p><p class="font-bold text-zinc-900">Paul M.</p><p class="text-sm text-zinc-500">Dental Practice, London</p></div>
<div class="rounded-2xl border border-emerald-200 bg-white p-8 shadow-sm"><p class="text-yellow-400 text-lg mb-1">&#9733;&#9733;&#9733;&#9733;&#9733;</p><p class="text-zinc-700 italic mb-4 leading-relaxed">"8 calls this month from the site — that never happened before."</p><p class="font-bold text-zinc-900">Dr. S. Davies</p><p class="text-sm text-zinc-500">Healthcare Clinic, Birmingham</p></div>
<div class="rounded-2xl border border-emerald-200 bg-white p-8 shadow-sm"><p class="text-yellow-400 text-lg mb-1">&#9733;&#9733;&#9733;&#9733;&#9733;</p><p class="text-zinc-700 italic mb-4 leading-relaxed">"Patient enquiries went up 3x in the first month. Game changer."</p><p class="font-bold text-zinc-900">Dr. A. Khan</p><p class="text-sm text-zinc-500">Medical Aesthetics, Manchester</p></div>
</div>
</div>
</section>

<!-- WHAT WE MEASURE -->
<section class="py-20 sm:py-28 px-6 bg-white">
<div class="max-w-6xl mx-auto">
<p class="text-sm font-bold uppercase tracking-[.2em] text-emerald-700 text-center mb-3">What We Measure</p>
<h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-zinc-900 text-center mb-6">5 trust pillars. 42 checks.</h2>
<div class="grid grid-cols-1 sm:grid-cols-5 gap-4 max-w-4xl mx-auto">
<div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-6 text-center"><div class="text-3xl mb-3">&#128170;</div><h3 class="font-bold text-zinc-900 mb-1">Credibility</h3><p class="text-sm text-zinc-600">Contact, about page, SSL, legal pages.</p></div>
<div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-6 text-center"><div class="text-3xl mb-3">&#11088;</div><h3 class="font-bold text-zinc-900 mb-1">Social Proof</h3><p class="text-sm text-zinc-600">Reviews, testimonials, trust badges.</p></div>
<div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-6 text-center"><div class="text-3xl mb-3">&#127942;</div><h3 class="font-bold text-zinc-900 mb-1">Authority</h3><p class="text-sm text-zinc-600">Content, certifications, team bios.</p></div>
<div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-6 text-center"><div class="text-3xl mb-3">&#128065;</div><h3 class="font-bold text-zinc-900 mb-1">Clarity</h3><p class="text-sm text-zinc-600">Headline, value proposition, navigation.</p></div>
<div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-6 text-center"><div class="text-3xl mb-3">&#127919;</div><h3 class="font-bold text-zinc-900 mb-1">Conversion</h3><p class="text-sm text-zinc-600">Booking CTAs, forms, phone prominence.</p></div>
</div>
<div class="text-center mt-8"><p class="inline-flex items-center gap-2 rounded-xl bg-zinc-900 px-6 py-3 text-base font-bold text-white shadow-lg">42 Checks Across 5 Pillars</p></div>
</div>
</section>

<!-- FAQ -->
<section class="py-20 sm:py-28 px-6 bg-emerald-50">
<div class="max-w-4xl mx-auto">
<p class="text-sm font-bold uppercase tracking-[.2em] text-emerald-700 text-center mb-3">FAQ</p>
<h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-zinc-900 text-center mb-12">Common questions</h2>
<div class="space-y-4">
<div class="rounded-2xl border border-emerald-200 bg-white p-6 shadow-sm"><h3 class="font-bold text-zinc-900 mb-2">Do I need a new website?</h3><p class="text-zinc-600 text-sm leading-relaxed">Not at all. Many clients optimise their existing site. No pressure either way.</p></div>
<div class="rounded-2xl border border-emerald-200 bg-white p-6 shadow-sm"><h3 class="font-bold text-zinc-900 mb-2">What's the difference between the Snapshot and the full report?</h3><p class="text-zinc-600 text-sm leading-relaxed">Snapshot = score in 30 seconds. Full report = every gap and fix, screenshared on a free call.</p></div>
<div class="rounded-2xl border border-emerald-200 bg-white p-6 shadow-sm"><h3 class="font-bold text-zinc-900 mb-2">Is the review call really free?</h3><p class="text-zinc-600 text-sm leading-relaxed">Yes. 20 minutes. No cost, no commitment, no sales pitch.</p></div>
</div>
</div>
</section>

<!-- CONTACT -->
<section id="contact" class="py-20 sm:py-28 px-6 bg-white">
<div class="max-w-4xl mx-auto text-center">
<p class="text-sm font-bold uppercase tracking-[.2em] text-emerald-700 mb-3">Contact Us</p>
<h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-zinc-900 mb-4">Let's talk</h2>
<p class="text-zinc-500 mb-8 font-medium">We'll respond within 24 hours.</p>
<form id="contactForm" class="max-w-lg mx-auto space-y-4" onsubmit="event.preventDefault();alert('Thanks! We\'ll be in touch within 24 hours.');">
<input type="text" placeholder="Your name" class="w-full rounded-xl border border-emerald-300 px-5 py-3.5 text-base font-medium focus:outline-none focus:ring-2 focus:ring-teal-500">
<input type="email" placeholder="Your email" class="w-full rounded-xl border border-emerald-300 px-5 py-3.5 text-base font-medium focus:outline-none focus:ring-2 focus:ring-teal-500">
<textarea rows="3" placeholder="Message" class="w-full rounded-xl border border-emerald-300 px-5 py-3.5 text-base font-medium focus:outline-none focus:ring-2 focus:ring-teal-500"></textarea>
<button type="submit" class="w-full rounded-xl bg-teal-500 px-6 py-3.5 text-base font-bold text-white shadow-lg hover:bg-teal-400 transition">Send Message →</button>
</form>
</div>
</section>

<!-- FINAL CTA -->
<section class="green1 text-white py-20 sm:py-28 px-6">
<div class="max-w-4xl mx-auto text-center">
<p class="text-3xl sm:text-5xl font-extrabold tracking-tight mb-4">&#128737;</p>
<h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight mb-4">Stop guessing. Start knowing.</h2>
<a href="#snapshot" class="inline-flex items-center gap-2 rounded-xl bg-teal-500 px-8 py-4 text-lg font-bold text-white shadow-xl hover:bg-teal-400 transition">Get Instant Access To Your Free Trust Snapshot →</a>
</div>
</section>

<!-- FOOTER -->
<footer class="bg-zinc-900 text-zinc-300 py-12 px-6 border-t border-zinc-800">
<div class="max-w-6xl mx-auto">
<div class="grid grid-cols-1 sm:grid-cols-3 gap-10">
<div><div class="flex items-center gap-2 text-lg font-extrabold mb-4"><span class="text-xl">&#128737;</span> <span class="text-yellow-400">Trust Trigger Agency</span></div><p class="text-zinc-400 text-sm">Helping healthcare practices turn websites into patient booking engines.</p></div>
<div><p class="text-sm font-bold uppercase tracking-wider text-emerald-400 mb-4">Service</p><ul class="space-y-3 text-sm font-medium"><li><a href="/home" class="text-zinc-300 hover:text-white">Free Snapshot</a></li><li><a href="/competitor-insights" class="text-zinc-300 hover:text-white">Compare Competitors</a></li><li><a href="/extensive-report" class="text-zinc-300 hover:text-white">Extensive Report</a></li><li><a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone?month=2026-09" class="text-zinc-300 hover:text-white">Book a Review</a></li></ul></div>
<div><p class="text-sm font-bold uppercase tracking-wider text-emerald-400 mb-4">Contact</p><ul class="space-y-3 text-sm font-medium"><li><a href="#contact" class="text-zinc-300 hover:text-white">Get in Touch</a></li></ul></div>
</div>
<div class="border-t border-zinc-800 mt-10 pt-8 text-sm text-zinc-500 text-center">&copy; 2025 Trust Trigger Agency&trade; &middot; The Trust Trigger Transformation Method&trade;</div>
</div>
</footer>

<script>
async function runSnapshot(){
  var name=document.getElementById('snapName').value.trim();
  var web=document.getElementById('snapWebsite').value.trim();
  var email=document.getElementById('snapEmail').value.trim();
  var err=document.getElementById('snapError');
  var btn=document.getElementById('snapBtn');
  var btxt=document.getElementById('snapBtnText');
  var bspin=document.getElementById('snapBtnSpin');
  if(!name||!web||!email||!email.includes('@')){err.classList.remove('hidden');return;}
  err.classList.add('hidden');
  btn.disabled=true;btxt.textContent='Scanning...';bspin.classList.remove('hidden');
  try{
    var u=web;if(!u.startsWith('http')) u='https://'+u;
    var res=await fetch('/api/v1/public/trust-snapshot',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({full_name:name,website:u,email:email})
    });
    var d=await res.json();
    if(d.success){
      document.getElementById('snapHeading').style.display='none';
      document.getElementById('snapSubtext').style.display='none';
      document.getElementById('exampleCard').style.display='none';
      var s=d.score||0;
      var sc=document.getElementById('snapScoreColor');
      if(s>=80){sc.className='text-7xl font-extrabold text-emerald-400 mb-2';}
      else if(s>=60){sc.className='text-7xl font-extrabold text-amber-400 mb-2';}
      else if(s>=40){sc.className='text-7xl font-extrabold text-amber-400 mb-2';}
      else{sc.className='text-7xl font-extrabold text-red-400 mb-2';}
      document.getElementById('snapScore').textContent=s;
      var gradeMap={'Excellent Trust':'Excellent Trust — Your website is a strong trust engine. Visitors feel confident reaching out.','Good Trust':'Good Trust — You\'re building trust well, but there are clear opportunities to convert more visitors.','Average Trust':'Average Trust — Your website is losing potential customers. The gaps below are costing you enquiries.','Weak Trust':'Weak Trust — Significant trust gaps found. Most visitors are likely leaving without contacting you.','At Risk':'At Risk — Critical trust issues detected. Your website is actively repelling potential customers.'};
      var g=d.grade||'Assessment complete.';
      document.getElementById('snapGrade').textContent=g;
      document.getElementById('snapGradeDesc').textContent=gradeMap[g]||'Assessment complete. Review the findings below.';
      var ph='';
      if(d.pillars&&d.pillars.length){
        d.pillars.forEach(function(p){
          var pct=Math.round(p.percentage);
          var bc=pct>=80?'bg-emerald-500':(pct>=50?'bg-amber-500':'bg-red-500');
          var tc=pct>=80?'text-emerald-400':(pct>=50?'text-amber-400':'text-red-400');
          ph+='<div class="rounded-xl bg-zinc-800 p-4"><div class="flex items-center justify-between mb-1"><span class="text-sm font-medium text-zinc-300">'+p.label+'</span><span class="text-sm font-semibold '+tc+'">'+pct+'%</span></div><div class="w-full h-2.5 bg-zinc-700 rounded-full overflow-hidden"><div class="h-full rounded-full '+bc+'" style="width:'+pct+'%"></div></div></div>';
        });
      }
      document.getElementById('snapPillars').innerHTML=ph;
      var ih='';
      if(d.issues&&d.issues.length){
        d.issues.slice(0,5).forEach(function(issue,i){
          ih+='<div class="flex items-start gap-3 p-4 rounded-xl bg-zinc-800"><span class="shrink-0 w-6 h-6 rounded-full bg-red-900 text-red-300 flex items-center justify-center text-xs font-bold">'+(i+1)+'</span><div><p class="text-sm font-medium text-zinc-100">'+issue.title+'</p><p class="text-sm text-zinc-400 mt-0.5">'+(issue.detail||'')+'</p></div></div>';
        });
      }else{ih='<p class="text-sm text-zinc-400">No issues found — great work!</p>';}
      document.getElementById('snapIssues').innerHTML=ih;
      var ah='';
      if(d.actions&&d.actions.length){
        d.actions.slice(0,4).forEach(function(a,i){
          var label=a.effort==='low'?'Quick win':(a.effort==='medium'?'Medium effort':'Larger project');
          var bc2=a.effort==='low'?'bg-emerald-900 text-emerald-300':(a.effort==='medium'?'bg-amber-900 text-amber-300':'bg-red-900 text-red-300');
          ah+='<div class="flex items-start gap-3 p-4 rounded-xl bg-zinc-800"><span class="shrink-0 w-6 h-6 rounded-full bg-teal-900 text-teal-300 flex items-center justify-center text-xs font-bold">'+(i+1)+'</span><div class="flex-1"><div class="flex items-center justify-between gap-2"><p class="text-sm font-medium text-zinc-100">'+a.title+'</p><span class="text-xs font-semibold '+bc2+' px-2 py-0.5 rounded-full">'+label+'</span></div><p class="text-sm text-zinc-400 mt-0.5">'+(a.detail||'')+'</p></div></div>';
        });
      }else{ah='<p class="text-sm text-zinc-400">No recommendations yet.</p>';}
      document.getElementById('snapActions').innerHTML=ah;
      document.getElementById('snapResults').classList.remove('hidden');
      document.getElementById('snapResults').scrollIntoView({behavior:'smooth',block:'start'});
    }else{
      err.textContent=d.error||'Something went wrong. Please try again.';
      err.classList.remove('hidden');
    }
  }catch(e){
    err.textContent='Network error. Please check your connection.';
    err.classList.remove('hidden');
  }
  btn.disabled=false;btxt.textContent='Get My Score →';bspin.classList.add('hidden');
}

try{
  document.querySelectorAll('section,footer').forEach(function(el){el.classList.add('reveal');});
  var io=new IntersectionObserver(function(entries){
    entries.forEach(function(e){if(e.isIntersecting) e.target.classList.add('in-view');});
  },{threshold:0.1,rootMargin:'0px 0px -50px 0px'});
  document.querySelectorAll('.reveal').forEach(function(el){io.observe(el);});
}catch(e){}
</script>
</body>
</html>"""

@router.get("", response_class=HTMLResponse)
async def homepage():
    return HTMLResponse(content=PAGE)
