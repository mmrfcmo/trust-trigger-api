"""Homepage with embedded Trust Snapshot scan."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
router = APIRouter(prefix="/home", tags=["Public - Homepage"])

PAGE = """<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Trust Trigger Agency</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap">
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
<a href="#" class="flex items-center gap-2 text-2xl font-extrabold text-yellow-400"><span class="text-3xl">🛡️</span> Trust Trigger Agency</a>
<div class="flex items-center gap-5">
<a href="#contact" class="text-base font-semibold text-zinc-300 hover:text-white">Contact</a>
<a href="#snapshot" class="rounded-lg bg-teal-500 px-5 py-2.5 text-base font-semibold text-white hover:bg-teal-400">Get Free Snapshot →</a>
</div>
</div>
</nav>

<section class="green1 text-white pt-32 pb-24 sm:pb-32 px-6">
<div class="max-w-6xl mx-auto text-center">
<p class="text-sm font-bold uppercase tracking-[.2em] text-teal-300 mb-4">Trust Trigger Transformation Method™</p>
<h1 class="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.05] mb-6">Is your healthcare practice<br><span class="gt">losing patients to your website?</span></h1>
<p class="text-lg sm:text-xl text-emerald-200 max-w-3xl mx-auto mb-10 leading-relaxed font-medium">Get a free Trust Snapshot, then book a 20-minute call and we'll screenshare your full Extensive Trust Report together — at no cost.</p>
<div class="flex flex-col sm:flex-row items-center justify-center gap-4">
<a href="#snapshot" class="rounded-xl bg-teal-500 px-7 py-4 text-base font-bold text-white shadow-xl hover:bg-teal-400">Get Your Free Trust Snapshot →</a>
<a href="#about" class="rounded-xl border border-emerald-400 px-7 py-4 text-base font-semibold text-emerald-200 hover:bg-white/10">See what we do</a>
</div>
</div>
</section>

<section id="about" class="py-20 px-6 bg-white">
<div class="max-w-4xl mx-auto text-center">
<p class="text-sm font-bold uppercase tracking-[.2em] text-emerald-700 mb-3">About</p>
<h2 class="text-4xl sm:text-5xl font-extrabold text-zinc-900 mb-6">We help healthcare practices turn website visitors into booked patients.</h2>
<p class="text-lg text-zinc-700 leading-relaxed">Most healthcare websites look fine — but to a first-time patient, they don't inspire enough confidence to pick up the phone. <strong class="text-zinc-900">Every gap costs you new patients.</strong></p>
</div>
</section>

<section class="py-20 px-6 bg-emerald-50">
<div class="max-w-6xl mx-auto text-center">
<p class="text-sm font-bold uppercase tracking-[.2em] text-emerald-700 mb-3">How It Works</p>
<h2 class="text-4xl sm:text-5xl font-extrabold text-zinc-900 mb-4">Three steps to clarity.</h2>
<div class="grid grid-cols-1 sm:grid-cols-3 gap-8 mt-12 text-left">
<div class="rounded-2xl border border-emerald-200 bg-white p-8 shadow-lg"><div class="w-14 h-14 rounded-xl bg-emerald-100 flex items-center justify-center text-2xl mb-5">🎯</div><p class="text-sm font-bold uppercase tracking-wider text-emerald-700">Step 1</p><h3 class="text-xl font-bold text-zinc-900 mb-3">Data-driven diagnosis</h3><p class="text-zinc-700">42 checks across 5 pillars. No guesswork — every issue has evidence and a clear fix priority.</p></div>
<div class="rounded-2xl border border-emerald-200 bg-white p-8 shadow-lg"><div class="w-14 h-14 rounded-xl bg-emerald-100 flex items-center justify-center text-2xl mb-5">🔧</div><p class="text-sm font-bold uppercase tracking-wider text-emerald-700">Step 2</p><h3 class="text-xl font-bold text-zinc-900 mb-3">Fix what's broken</h3><p class="text-zinc-700">Not every practice needs a new website. We can optimise or build. <strong class="text-zinc-900">You decide.</strong></p></div>
<div class="rounded-2xl border border-emerald-200 bg-white p-8 shadow-lg"><div class="w-14 h-14 rounded-xl bg-emerald-100 flex items-center justify-center text-2xl mb-5">📈</div><p class="text-sm font-bold uppercase tracking-wider text-emerald-700">Step 3</p><h3 class="text-xl font-bold text-zinc-900 mb-3">Proven results</h3><p class="text-zinc-700">Documented before/after for every client. <strong class="text-zinc-900">We prove what changed.</strong></p></div>
</div>
</div>
</section>

<section id="snapshot" class="py-20 px-6 bg-black text-white">
<div class="max-w-6xl mx-auto">
<div class="text-center mb-12" id="snapshotHeader">
<p class="text-sm font-bold uppercase tracking-[.2em] text-teal-400 mb-3">Your Free Trust Snapshot</p>
<h2 class="text-4xl sm:text-5xl font-extrabold text-white mb-4" id="snapshotTitle">See your score in 30 seconds</h2>
</div>

<div class="max-w-4xl mx-auto mb-10" id="exampleSnapshot">
<div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-6">
<div class="rounded-2xl border-2 border-zinc-700 bg-zinc-900 p-8 text-center lg:col-span-1">
<p class="text-sm font-bold uppercase tracking-wider text-teal-400 mb-1">Example Snapshot</p>
<p class="text-7xl font-extrabold text-white mb-1">72</p>
<p class="text-base font-semibold text-teal-400 mb-4">Trust Score</p>
<p class="text-zinc-400">Your website is credible — but specific trust gaps are preventing it from converting at full potential.</p>
</div>
<div class="lg:col-span-2 space-y-4">
<div><div class="flex justify-between text-sm font-semibold mb-1"><span class="text-zinc-300">Credibility</span><span class="text-green-400">85</span></div><div class="h-3 rounded-full bg-zinc-700 overflow-hidden"><div class="h-full rounded-full sg" style="width:85%"></div></div></div>
<div><div class="flex justify-between text-sm font-semibold mb-1"><span class="text-zinc-300">Social Proof</span><span class="text-orange-400">45</span></div><div class="h-3 rounded-full bg-zinc-700 overflow-hidden"><div class="h-full rounded-full so" style="width:45%"></div></div></div>
<div><div class="flex justify-between text-sm font-semibold mb-1"><span class="text-zinc-300">Authority</span><span class="text-yellow-400">60</span></div><div class="h-3 rounded-full bg-zinc-700 overflow-hidden"><div class="h-full rounded-full sy" style="width:60%"></div></div></div>
<div><div class="flex justify-between text-sm font-semibold mb-1"><span class="text-zinc-300">Clarity</span><span class="text-yellow-400">70</span></div><div class="h-3 rounded-full bg-zinc-700 overflow-hidden"><div class="h-full rounded-full sy" style="width:70%"></div></div></div>
<div><div class="flex justify-between text-sm font-semibold mb-1"><span class="text-zinc-300">Conversion</span><span class="text-orange-400">55</span></div><div class="h-3 rounded-full bg-zinc-700 overflow-hidden"><div class="h-full rounded-full so" style="width:55%"></div></div></div>
</div>
</div>
<div class="bg-red-950 border border-red-800 rounded-2xl p-6">
<p class="text-lg font-bold text-red-400 mb-3">⚠️ Top Issues</p>
<div class="space-y-2 text-red-300 font-medium">
<div>#1 Homepage value proposition unclear — visitors can't immediately tell what you do</div>
<div>#2 No visible reviews or testimonials — your best social proof is hidden</div>
<div>#3 Booking CTA is buried or generic — doesn't motivate action</div>
</div>
</div>
</div>

<div id="liveResult" class="hidden max-w-4xl mx-auto"></div>

<div id="scanBox" class="max-w-xl mx-auto bg-white border border-emerald-200 rounded-2xl shadow-xl p-8">
<div class="flex flex-col sm:flex-row gap-3">
<input id="scanUrl" type="text" placeholder="yourpractice.co.uk" class="flex-1 rounded-xl border border-emerald-300 bg-white px-5 py-3.5 text-zinc-800 placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-teal-500">
<button onclick="doScan()" id="scanBtn" class="rounded-xl bg-teal-500 px-6 py-3.5 text-base font-bold text-white hover:bg-teal-400 whitespace-nowrap">Get My Score →</button>
</div>
<div id="scanStatus" class="text-sm text-zinc-500 mt-4"></div>
</div>
<p class="text-sm text-emerald-200 mt-4 text-center" id="freeTag">Free. No card. Takes 30 seconds.</p>

<div id="surprisedSection" class="hidden max-w-2xl mx-auto mt-8 text-center">
<p class="text-2xl sm:text-3xl font-extrabold text-white mb-6">Surprised with your score?</p>
<p class="text-lg text-zinc-300 max-w-xl mx-auto mb-8 leading-relaxed font-medium">Let's go through your full report together and we'll show you how to improve your score quickly to convert more enquiries.</p>
<a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone?month=2026-09" class="rounded-xl bg-teal-500 px-8 py-4 text-lg font-bold text-white shadow-xl hover:bg-teal-400 transition">Book A Free 20 Minute Review →</a>
</div>
</div>
</section>

<section class="py-20 px-6 bg-white">
<div class="max-w-4xl mx-auto text-center">
<p class="text-sm font-bold uppercase tracking-[.2em] text-emerald-700 mb-3">Real Results</p>
<h2 class="text-4xl sm:text-5xl font-extrabold text-zinc-900 mb-4">Practices like yours, transformed</h2>
<div class="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12 text-left">
<div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-8 shadow-lg"><div class="text-teal-500 text-xl mb-4">★★★★★</div><p class="text-zinc-700 mb-6">"Calls went from 3 a week to 14. Trust score went from 42 to 91."</p><div class="flex items-center gap-3"><div class="w-10 h-10 rounded-full bg-emerald-200 flex items-center justify-center text-lg font-bold text-emerald-700">PM</div><div><p class="font-bold text-zinc-900">Paul M.</p><p class="text-sm text-zinc-600">Dental Practice, London</p></div></div></div>
<div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-8 shadow-lg"><div class="text-teal-500 text-xl mb-4">★★★★★</div><p class="text-zinc-700 mb-6">"8 calls this month from the site — that never happened before."</p><div class="flex items-center gap-3"><div class="w-10 h-10 rounded-full bg-emerald-200 flex items-center justify-center text-lg font-bold text-emerald-700">SD</div><div><p class="font-bold text-zinc-900">Dr. S. Davies</p><p class="text-sm text-zinc-600">Healthcare Clinic, Birmingham</p></div></div></div>
<div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-8 shadow-lg"><div class="text-teal-500 text-xl mb-4">★★★★★</div><p class="text-zinc-700 mb-6">"Patient enquiries went up 3x in the first month."</p><div class="flex items-center gap-3"><div class="w-10 h-10 rounded-full bg-emerald-200 flex items-center justify-center text-lg font-bold text-emerald-700">AK</div><div><p class="font-bold text-zinc-900">Dr. A. Khan</p><p class="text-sm text-zinc-600">Medical Aesthetics, Manchester</p></div></div></div>
</div>
</div>
</section>

<section class="py-20 px-6 bg-black text-white">
<div class="max-w-6xl mx-auto text-center">
<p class="text-sm font-bold uppercase tracking-[.2em] text-teal-400 mb-3">What We Measure</p>
<h2 class="text-4xl sm:text-5xl font-extrabold text-white mb-4">5 trust pillars. 42 checks.</h2>
<div class="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-12 text-left">
<div class="rounded-2xl border border-zinc-700 bg-zinc-900 p-7 shadow-lg"><h3 class="text-lg font-bold text-white mb-2">🪪 Credibility</h3><p class="text-zinc-400">Contact, about page, SSL, legal pages.</p></div>
<div class="rounded-2xl border border-zinc-700 bg-zinc-900 p-7 shadow-lg"><h3 class="text-lg font-bold text-white mb-2">⭐ Social Proof</h3><p class="text-zinc-400">Reviews, testimonials, trust badges.</p></div>
<div class="rounded-2xl border border-zinc-700 bg-zinc-900 p-7 shadow-lg"><h3 class="text-lg font-bold text-white mb-2">🏆 Authority</h3><p class="text-zinc-400">Content, certifications, team bios.</p></div>
<div class="rounded-2xl border border-zinc-700 bg-zinc-900 p-7 shadow-lg"><h3 class="text-lg font-bold text-white mb-2">👁️ Clarity</h3><p class="text-zinc-400">Headline, value proposition, navigation.</p></div>
<div class="rounded-2xl border border-zinc-700 bg-zinc-900 p-7 shadow-lg"><h3 class="text-lg font-bold text-white mb-2">🎯 Conversion</h3><p class="text-zinc-400">Booking CTAs, forms, phone prominence.</p></div>
<div class="rounded-2xl border-2 border-teal-500 bg-zinc-900 p-7 flex flex-col items-center justify-center text-center shadow-lg"><p class="text-5xl font-extrabold text-teal-400 mb-1">42</p><p class="text-zinc-300">Checks Across 5 Pillars</p></div>
</div>
</div>
</section>

<section class="py-20 px-6 bg-white">
<div class="max-w-3xl mx-auto">
<p class="text-sm font-bold uppercase tracking-[.2em] text-emerald-700 mb-3 text-center">FAQ</p>
<div class="space-y-4 mt-8">
<div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-6 shadow-lg"><h3 class="font-bold text-zinc-900 mb-2">Do I need a new website?</h3><p class="text-zinc-700">Not at all. Many clients optimise their existing site. No pressure either way.</p></div>
<div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-6 shadow-lg"><h3 class="font-bold text-zinc-900 mb-2">What's the difference between the Snapshot and the full report?</h3><p class="text-zinc-700">Snapshot = score in 30 seconds. Full report = every gap and fix, screenshared on a free call.</p></div>
<div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-6 shadow-lg"><h3 class="font-bold text-zinc-900 mb-2">Is the review call really free?</h3><p class="text-zinc-700">Yes. 20 minutes. No cost, no commitment, no sales pitch.</p></div>
</div>
</div>
</section>

<section id="contact" class="py-20 px-6 bg-black text-white">
<div class="max-w-xl mx-auto text-center">
<p class="text-sm font-bold uppercase tracking-[.2em] text-teal-400 mb-3">Contact Us</p>
<h2 class="text-4xl sm:text-5xl font-extrabold text-white mb-4">Let's talk</h2>
<form class="bg-zinc-800 border border-zinc-700 rounded-2xl p-8 space-y-5 text-left mt-8 shadow-lg" onsubmit="event.preventDefault(); alert('Thanks! We will get back to you within 24 hours.');">
<div><input type="text" placeholder="Full Name" class="w-full rounded-xl border border-zinc-600 bg-zinc-900 px-5 py-3.5 text-white placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-teal-500" required></div>
<div><input type="text" placeholder="Practice Name" class="w-full rounded-xl border border-zinc-600 bg-zinc-900 px-5 py-3.5 text-white placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-teal-500" required></div>
<div><input type="email" placeholder="Email Address" class="w-full rounded-xl border border-zinc-600 bg-zinc-900 px-5 py-3.5 text-white placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-teal-500" required></div>
<div><input type="tel" placeholder="Phone Number" class="w-full rounded-xl border border-zinc-600 bg-zinc-900 px-5 py-3.5 text-white placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-teal-500"></div>
<div><input type="url" placeholder="Website URL" class="w-full rounded-xl border border-zinc-600 bg-zinc-900 px-5 py-3.5 text-white placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-teal-500"></div>
<div><textarea rows="3" placeholder="Message" class="w-full rounded-xl border border-zinc-600 bg-zinc-900 px-5 py-3.5 text-white placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-teal-500" required></textarea></div>
<button type="submit" class="w-full rounded-xl bg-teal-500 px-6 py-4 font-bold text-white hover:bg-teal-400">Send Message →</button>
<p class="text-sm text-zinc-500 text-center">We'll respond within 24 hours.</p>
</form>
</div>
</section>

<section class="green1 text-white py-24 px-6">
<div class="max-w-3xl mx-auto text-center">
<div class="text-6xl mb-6">🛡️</div>
<h2 class="text-4xl sm:text-5xl font-extrabold mb-6">Stop guessing. Start knowing.</h2>
<div><a href="#snapshot" class="rounded-xl bg-teal-500 px-7 py-4 text-lg font-bold text-white shadow-xl hover:bg-teal-400">Get Instant Access To Your Free Trust Snapshot →</a></div>
</div>
</section>

<footer class="bg-zinc-900 text-zinc-300 py-12 px-6 border-t border-zinc-800">
<div class="max-w-6xl mx-auto">
<div class="grid grid-cols-2 gap-10">
<div><div class="flex items-center gap-2 text-lg font-extrabold mb-4"><span class="text-xl">🛡️</span> <span class="text-yellow-400">Trust Trigger Agency</span></div><p class="text-zinc-400 text-sm">Helping healthcare practices turn websites into patient booking engines.</p></div>
<div><p class="text-sm font-bold uppercase tracking-wider text-emerald-400 mb-4">Service</p><ul class="space-y-3 text-sm font-medium"><li><a href="#snapshot" class="text-zinc-300 hover:text-white">Free Snapshot</a></li><li><a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone?month=2026-09" class="text-zinc-300 hover:text-white">Book a Review</a></li><li><a href="#contact" class="text-zinc-300 hover:text-white">Contact Us</a></li></ul></div>
</div>
<div class="border-t border-zinc-800 mt-8 pt-6 text-sm font-medium text-center"><p class="text-yellow-400">© 2025 Trust Trigger Agency™ · The Trust Trigger Transformation Method™</p></div>
</div>
</footer>

<script>
function doScan(){
var u=document.getElementById('scanUrl').value.trim();
var s=document.getElementById('scanStatus');
var b=document.getElementById('scanBtn');
var r=document.getElementById('liveResult');
var e=document.getElementById('exampleSnapshot');
var sur=document.getElementById('surprisedSection');
if(!u){s.textContent='Please enter a URL.';return;}
if(!u.startsWith('http')) u='https://'+u;
s.textContent='Scanning...'; b.disabled=true; b.textContent='Scanning...';
fetch('/api/v1/public/trust-snapshot',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({full_name:'Your Business',website:u,email:'s_'+Date.now()+'@t.com'})})
.then(function(res){return res.json();})
.then(function(d){
b.disabled=false; b.textContent='Get My Score →';
if(!d.score){s.textContent='Could not scan. Try again.';return;}
s.textContent=''; e.classList.add('hidden'); r.classList.remove('hidden'); sur.classList.remove('hidden');
document.getElementById('scanBox').classList.add('hidden');
document.getElementById('snapshotTitle').classList.add('hidden');
document.getElementById('freeTag').classList.add('hidden');
var pills={};if(d.pillars)d.pillars.forEach(function(p){pills[p.label]=Math.round(p.percentage);});
var labels=['Online Presence','Reputation','Engagement','Transparency','Technical Health'];
var bars='';
labels.forEach(function(l){
var v=pills[l]||0;
var c=v>=80?'#22c55e':v>=60?'#eab308':v>=40?'#f97316':'#ef4444';
var tc=v>=80?'text-green-400':v>=60?'text-yellow-400':v>=40?'text-orange-400':'text-red-400';
bars+='<div><div class="flex justify-between text-sm font-semibold mb-1"><span class="text-zinc-300">'+l+'</span><span class="'+tc+'">'+v+'</span></div><div class="h-3 rounded-full bg-zinc-700 overflow-hidden"><div class="h-full rounded-full" style="width:'+v+'%;background:'+c+'"></div></div></div>';
});
var g=d.grade?d.grade.charAt(0).toUpperCase()+d.grade.slice(1):'Strong';
var issues='';
if(d.issues&&d.issues.length){
issues='<div class="mt-6 bg-red-950 border border-red-800 rounded-2xl p-6"><p class="text-lg font-bold text-red-400 mb-3">⚠️ Top Issues</p>';
d.issues.slice(0,3).forEach(function(x,i){issues+='<div class="text-red-300 font-medium mb-1">#'+(i+1)+' '+x.title+'</div>';});
issues+='</div>';
}
r.innerHTML='<div class="rounded-2xl border-2 border-teal-500 bg-zinc-900 p-8"><div class="grid grid-cols-1 lg:grid-cols-3 gap-8"><div class="text-center lg:col-span-1"><p class="text-sm font-bold uppercase tracking-wider text-teal-400 mb-1">Your Snapshot</p><p class="text-7xl font-extrabold text-white mb-1">'+d.score+'</p><p class="text-base font-semibold text-teal-400 mb-4">'+g+'</p></div><div class="lg:col-span-2 space-y-4">'+bars+'</div></div>'+issues+'</div>';
r.scrollIntoView({behavior:'smooth',block:'start'});
})
.catch(function(){b.disabled=false;b.textContent='Get My Score →';s.textContent='Error. Try again.';});
}
</script>
</body>
</html>"""

@router.get("", response_class=HTMLResponse)
async def get_homepage():
    return PAGE

@router.get("/", response_class=HTMLResponse)
async def get_homepage_root():
    return PAGE
