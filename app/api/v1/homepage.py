"""Landing page for Trust Trigger Agency."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
router = APIRouter(tags=["Public - Landing Page"])
PAGE = """<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Trust Snapshot™ — Free Digital Trust Assessment | TTA — Trust Trigger Agency</title>
  <meta name="description" content="Get a free Trust Snapshot in under 60 seconds. We analyse your website, Google Business Profile and customer journey, then show you exactly what's costing you enquiries.">
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23f59e0b'/%3E%3Ctext x='16' y='22' font-family='Arial' font-size='14' font-weight='900' fill='white' text-anchor='middle'%3ET%3C/text%3E%3C/svg%3E">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    html,body{font-family:'Inter',ui-sans-serif,system-ui,sans-serif}body{-webkit-font-smoothing:antialiased;background:#0f172a;color:#e2e8f0}
    .reveal{opacity:0;transform:translateY(20px);transition:opacity .6s ease-out,transform .6s ease-out}
    .reveal.in-view{opacity:1;transform:none}
    .gradient-hero{background:linear-gradient(135deg,#0f172a 0%,#1a2a4a 50%,#78350f 100%)}
    .gradient-card{background:linear-gradient(135deg,#1e293b,#0f172a)}
    .logo-icon{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:8px;background:#f59e0b;color:#fff;font-weight:800;font-size:12px;margin-right:8px}
    .pulse-glow{animation:pulseGlow 2s ease-in-out infinite}
    @keyframes pulseGlow{0%,100%{box-shadow:0 0 20px rgba(245,158,11,.3)}50%{box-shadow:0 0 40px rgba(245,158,11,.6)}}
    @media (max-width:640px){.text-4xl{font-size:1.875rem;line-height:1.15}.text-5xl{font-size:2.25rem;line-height:1.15}.grid{gap:1rem}}
  </style>
</head>
<body>
<!-- ===== NAV ===== -->
<nav class="fixed top-0 left-0 right-0 z-50 bg-slate-950/90 backdrop-blur-md border-b border-slate-800">
<div class="max-w-6xl mx-auto px-6 flex items-center justify-between h-20">
<a href="/" class="flex items-center gap-2 text-white no-underline">
  <span class="w-8 h-8 rounded-lg bg-amber-500 text-white flex items-center justify-center text-sm font-extrabold">TTA</span>
  <div>
    <div class="font-bold text-xl tracking-tight leading-tight text-amber-400">Trust Trigger Agency</div>
    <div class="text-xs font-semibold tracking-wider text-white">Measure. Transform. Prove. Maintain.</div>
  </div>
</a>
<div class="hidden md:flex items-center gap-6">
  <a href="#get-snapshot" class="inline-flex items-center gap-2 rounded-lg bg-amber-500 px-5 py-2.5 text-sm font-bold text-white shadow-sm transition hover:bg-amber-400">Get My Free Trust Snapshot →</a>
</div>
</div>
</nav>

<!-- ===== HERO ===== -->
<section class="relative pt-32 sm:pt-40 pb-20 sm:pb-28 overflow-hidden gradient-hero">
<div class="absolute inset-0 opacity-10">
  <div class="absolute top-20 left-10 w-72 h-72 bg-amber-500 rounded-full blur-3xl"></div>
  <div class="absolute bottom-10 right-10 w-96 h-96 bg-amber-300 rounded-full blur-3xl"></div>
</div>
<div class="relative max-w-6xl mx-auto px-6">
<div class="max-w-4xl mx-auto text-center">
  <div class="inline-flex items-center gap-2 bg-amber-500/20 border border-amber-500/40 text-amber-200 text-xs font-semibold uppercase tracking-widest px-4 py-2 rounded-full mb-6">Powered by The Trust Trigger Transformation Method™</div>
  <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.05] text-white">Discover Why Customers Don't Trust Your Website</h1>
  <p class="mt-6 text-lg text-slate-300 max-w-2xl mx-auto">Get a free Trust Snapshot in under 60 seconds. We'll analyse your website, Google Business Profile and customer journey, then show you exactly what's costing you enquiries.</p>
  <div class="flex flex-wrap gap-4 justify-center mt-10">
    <a href="#get-snapshot" class="inline-flex items-center gap-2 rounded-lg bg-amber-500 px-8 py-4 text-base font-bold text-white shadow-lg transition hover:bg-amber-400 pulse-glow">Get My Free Trust Snapshot →</a>
    <a href="#example-report" class="inline-flex items-center gap-2 rounded-lg border-2 border-slate-700 bg-slate-900 px-8 py-4 text-base font-medium text-slate-300 shadow-sm transition hover:bg-slate-800">See Example Report</a>
  </div>
  <p class="mt-6 text-xs text-slate-500">Trusted by local service businesses looking to turn more visitors into enquiries.</p>
  <p class="mt-2 text-xs italic text-slate-600">"We're helping local service businesses transform their digital trust — one website at a time. Case studies coming soon."</p>
</div>
</div>
</section>

<!-- ===== PROBLEM ===== -->
<section class="py-16 sm:py-20 bg-slate-900" id="problem">
<div class="max-w-6xl mx-auto px-6">
<div class="max-w-4xl mx-auto">
  <div class="text-center mb-10">
    <div class="inline-flex items-center gap-2 bg-amber-500/20 border border-amber-500/40 text-amber-200 text-xs font-semibold uppercase tracking-widest px-4 py-2 rounded-full mb-4">The Real Problem</div>
    <h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">Most business websites don't have a traffic problem.</h2>
    <p class="text-3xl sm:text-4xl font-extrabold tracking-tight text-amber-400 mt-2">They have a trust problem.</p>
  </div>
  <div class="grid sm:grid-cols-2 gap-4 mt-10">
    <div class="rounded-xl border border-slate-800 bg-slate-950 p-6 text-center">
      <div class="text-4xl mb-2">🤔</div>
      <p class="text-slate-300 font-medium">Can I trust this company?</p>
    </div>
    <div class="rounded-xl border border-slate-800 bg-slate-950 p-6 text-center">
      <div class="text-4xl mb-2">🧑‍🔧</div>
      <p class="text-slate-300 font-medium">Are they experienced?</p>
    </div>
    <div class="rounded-xl border border-slate-800 bg-slate-950 p-6 text-center">
      <div class="text-4xl mb-2">❓</div>
      <p class="text-slate-300 font-medium">Why should I choose them?</p>
    </div>
    <div class="rounded-xl border border-slate-800 bg-slate-950 p-6 text-center">
      <div class="text-4xl mb-2">⚠️</div>
      <p class="text-slate-300 font-medium">What happens if something goes wrong?</p>
    </div>
  </div>
  <p class="text-center text-slate-400 mt-6 text-lg">If your website doesn't answer those questions quickly, prospects leave.</p>
</div>
</div>
</section>

<!-- ===== FEATURES ===== -->
<section class="py-16 sm:py-20 bg-slate-950">
<div class="max-w-6xl mx-auto px-6">
<div class="text-center mb-12">
  <div class="inline-flex items-center gap-2 bg-amber-500/20 border border-amber-500/40 text-amber-200 text-xs font-semibold uppercase tracking-widest px-4 py-2 rounded-full mb-4">Your Free Trust Snapshot Includes</div>
  <h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">See exactly where you're losing trust</h2>
  <p class="mt-4 text-slate-400 max-w-xl mx-auto">We check your business against seven critical trust dimensions. Delivered in minutes.</p>
</div>
<div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
  <div class="rounded-xl border border-slate-800 bg-slate-900 p-6 hover:border-amber-500/40 transition">
    <span class="w-10 h-10 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center text-lg font-bold mb-4">1</span>
    <h3 class="font-bold text-white mb-2">Trust Score (0–100)</h3>
    <p class="text-sm text-slate-400">Your overall digital trust rating</p>
  </div>
  <div class="rounded-xl border border-slate-800 bg-slate-900 p-6 hover:border-amber-500/40 transition">
    <span class="w-10 h-10 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center text-lg font-bold mb-4">2</span>
    <h3 class="font-bold text-white mb-2">Homepage analysis</h3>
    <p class="text-sm text-slate-400">First impression audit</p>
  </div>
  <div class="rounded-xl border border-slate-800 bg-slate-900 p-6 hover:border-amber-500/40 transition">
    <span class="w-10 h-10 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center text-lg font-bold mb-4">3</span>
    <h3 class="font-bold text-white mb-2">Google Business Profile review</h3>
    <p class="text-sm text-slate-400">Your GBP listing assessed</p>
  </div>
  <div class="rounded-xl border border-slate-800 bg-slate-900 p-6 hover:border-amber-500/40 transition">
    <span class="w-10 h-10 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center text-lg font-bold mb-4">4</span>
    <h3 class="font-bold text-white mb-2">Trust signal assessment</h3>
    <p class="text-sm text-slate-400">Testimonials, badges, contact info</p>
  </div>
  <div class="rounded-xl border border-slate-800 bg-slate-900 p-6 hover:border-amber-500/40 transition">
    <span class="w-10 h-10 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center text-lg font-bold mb-4">5</span>
    <h3 class="font-bold text-white mb-2">Conversion opportunities</h3>
    <p class="text-sm text-slate-400">Where visitors drop off</p>
  </div>
  <div class="rounded-xl border border-slate-800 bg-slate-900 p-6 hover:border-amber-500/40 transition">
    <span class="w-10 h-10 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center text-lg font-bold mb-4">6</span>
    <h3 class="font-bold text-white mb-2">Personalised improvement plan</h3>
    <p class="text-sm text-slate-400">Quick wins + strategic fixes</p>
  </div>
</div>
<p class="text-center text-amber-400 mt-8 text-sm font-semibold">Delivered in minutes. No credit card needed.</p>
</div>
</section>

<!-- ===== HOW IT WORKS ===== -->
<section class="py-16 sm:py-20 bg-slate-900">
<div class="max-w-6xl mx-auto px-6">
<div class="text-center mb-12">
  <div class="inline-flex items-center gap-2 bg-amber-500/20 border border-amber-500/40 text-amber-200 text-xs font-semibold uppercase tracking-widest px-4 py-2 rounded-full mb-4">How It Works</div>
  <h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">Three steps to clarity</h2>
</div>
<div class="grid sm:grid-cols-3 gap-8 max-w-4xl mx-auto">
  <div class="text-center">
    <span class="w-14 h-14 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center text-2xl font-bold mx-auto mb-4">1</span>
    <h3 class="font-bold text-white text-lg mb-2">Enter your website</h3>
    <p class="text-sm text-slate-400">Type in your URL. It takes 10 seconds.</p>
  </div>
  <div class="text-center">
    <span class="w-14 h-14 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center text-2xl font-bold mx-auto mb-4">2</span>
    <h3 class="font-bold text-white text-lg mb-2">We analyse your presence</h3>
    <p class="text-sm text-slate-400">We scan your site, Google Business Profile (GBP) and trust signals.</p>
  </div>
  <div class="text-center">
    <span class="w-14 h-14 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center text-2xl font-bold mx-auto mb-4">3</span>
    <h3 class="font-bold text-white text-lg mb-2">Receive your personalised report</h3>
    <p class="text-sm text-slate-400">Your Trust Snapshot with actionable fixes. If you like what you see, we can implement the improvements for you.</p>
  </div>
</div>
</div>
</section>

<!-- ===== EXAMPLE REPORT ===== -->
<section class="py-16 sm:py-20 bg-slate-950" id="example-report">
<div class="max-w-6xl mx-auto px-6">
<div class="text-center mb-10">
  <div class="inline-flex items-center gap-2 bg-amber-500/20 border border-amber-500/40 text-amber-200 text-xs font-semibold uppercase tracking-widest px-4 py-2 rounded-full mb-4">Example Report</div>
  <h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">What a low-scoring business looks like</h2>
  <p class="mt-4 text-slate-400">This business scored 32/100. How does your website compare?</p>
</div>
<div class="max-w-3xl mx-auto">
<div class="rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
  <div class="flex items-center gap-6 mb-8">
    <div class="relative w-24 h-24 shrink-0">
      <svg class="w-24 h-24 -rotate-90" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="52" fill="none" stroke="#334155" stroke-width="10"/>
        <circle cx="60" cy="60" r="52" fill="none" stroke="#ef4444" stroke-width="10" stroke-dasharray="326.7" stroke-dashoffset="220"/>
      </svg>
      <div class="absolute inset-0 flex items-center justify-center"><span class="text-2xl font-extrabold text-white">32</span></div>
    </div>
    <div>
      <p class="text-xs font-bold uppercase tracking-wider text-slate-500">Trust Score</p>
      <p class="text-xl font-bold text-red-400">At Risk</p>
      <div class="flex gap-4 mt-1 text-xs text-slate-400">
        <span>Issues: 7</span>
        <span>Passed: 2/9</span>
        <span>Site: example.com</span>
      </div>
    </div>
  </div>
  <div class="mb-6">
    <p class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">Score Breakdown</p>
    <div class="grid sm:grid-cols-2 gap-3">
      <div><div class="flex justify-between text-sm mb-1"><span class="text-slate-300">Online Presence</span><span class="text-white font-bold">8/25</span></div><div class="bg-slate-800 rounded-full" style="height:8px"><div class="bg-red-500 rounded-full" style="width:32%;height:100%"></div></div><p class="text-xs text-red-400 mt-1">Your site is hard to find. Missing key pages. Visitors cannot verify your credibility.</p></div>
      <div><div class="flex justify-between text-sm mb-1"><span class="text-slate-300">Reputation</span><span class="text-white font-bold">6/30</span></div><div class="bg-slate-800 rounded-full" style="height:8px"><div class="bg-red-500 rounded-full" style="width:20%;height:100%"></div></div><p class="text-xs text-red-400 mt-1">No social proof. Zero reviews displayed. Customers choose competitors they can see.</p></div>
      <div><div class="flex justify-between text-sm mb-1"><span class="text-slate-300">Engagement</span><span class="text-white font-bold">7/20</span></div><div class="bg-slate-800 rounded-full" style="height:8px"><div class="bg-amber-500 rounded-full" style="width:35%;height:100%"></div></div><p class="text-xs text-amber-400 mt-1">No clear calls-to-action. Visitors leave without booking.</p></div>
      <div><div class="flex justify-between text-sm mb-1"><span class="text-slate-300">Transparency</span><span class="text-white font-bold">4/15</span></div><div class="bg-slate-800 rounded-full" style="height:8px"><div class="bg-red-500 rounded-full" style="width:27%;height:100%"></div></div><p class="text-xs text-red-400 mt-1">No About page, team photos, or privacy policy. You are asking visitors to trust a faceless business.</p></div>
      <div class="sm:col-span-2"><div class="flex justify-between text-sm mb-1"><span class="text-slate-300">Technical Health</span><span class="text-white font-bold">7/10</span></div><div class="bg-slate-800 rounded-full" style="height:8px"><div class="bg-emerald-500 rounded-full" style="width:70%;height:100%"></div></div><p class="text-xs text-emerald-400 mt-1">Your technical foundation is reasonable.</p></div>
    </div>
  </div>
  <div class="mb-6">
    <p class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">Standards</p>
    <div class="grid grid-cols-3 gap-2 text-xs">
      <div class="flex items-center gap-1.5"><span class="text-emerald-400">&#10003;</span><span class="text-slate-300">HTTPS</span></div>
      <div class="flex items-center gap-1.5"><span class="text-red-400">&#10007;</span><span class="text-slate-300">Contact Page</span></div>
      <div class="flex items-center gap-1.5"><span class="text-emerald-400">&#10003;</span><span class="text-slate-300">About Page</span></div>
      <div class="flex items-center gap-1.5"><span class="text-red-400">&#10007;</span><span class="text-slate-300">Mobile Ready</span></div>
      <div class="flex items-center gap-1.5"><span class="text-red-400">&#10007;</span><span class="text-slate-300">Testimonials</span></div>
      <div class="flex items-center gap-1.5"><span class="text-red-400">&#10007;</span><span class="text-slate-300">FAQ</span></div>
      <div class="flex items-center gap-1.5"><span class="text-red-400">&#10007;</span><span class="text-slate-300">Privacy Policy</span></div>
      <div class="flex items-center gap-1.5"><span class="text-red-400">&#10007;</span><span class="text-slate-300">CTA</span></div>
      <div class="flex items-center gap-1.5"><span class="text-red-400">&#10007;</span><span class="text-slate-300">Service Pages</span></div>
    </div>
  </div>
  <div>
    <p class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">Top Issues</p>
    <div class="space-y-2">
      <div class="flex items-start gap-3 bg-slate-950 rounded-lg p-3"><span class="text-red-400 shrink-0">!</span><div><p class="text-sm font-medium text-slate-200">No contact page or phone number</p><p class="text-xs text-slate-500">Hard to reach you</p></div></div>
      <div class="flex items-start gap-3 bg-slate-950 rounded-lg p-3"><span class="text-red-400 shrink-0">!</span><div><p class="text-sm font-medium text-slate-200">No SSL certificate (not HTTPS)</p><p class="text-xs text-slate-500">Visitors see "Not Secure"</p></div></div>
      <div class="flex items-start gap-3 bg-slate-950 rounded-lg p-3"><span class="text-red-400 shrink-0">!</span><div><p class="text-sm font-medium text-slate-200">Website not mobile-friendly</p><p class="text-xs text-slate-500">Poor mobile experience</p></div></div>
    </div>
  </div>
</div>
</div>
</div>
</section>

<!-- ===== OFFER ===== -->
<section class="py-16 sm:py-20 bg-slate-900">
<div class="max-w-6xl mx-auto px-6">
<div class="max-w-3xl mx-auto">
<div class="rounded-2xl border-2 border-amber-500 bg-slate-950 p-8 sm:p-12 text-center">
  <p class="text-xs font-bold text-amber-400 uppercase tracking-widest mb-2">The Offer</p>
  <h2 class="text-3xl sm:text-4xl font-extrabold text-white mb-4">Trust Transformation</h2>
  <p class="text-slate-400 mb-8">We don't just tell you what's wrong. We fix it.</p>
  <div class="grid sm:grid-cols-2 gap-3 text-left max-w-md mx-auto mb-8">
    <div class="flex items-start gap-2"><span class="text-emerald-400 shrink-0 mt-0.5">&#10003;</span><span class="text-slate-300 text-sm">Homepage rewrite</span></div>
    <div class="flex items-start gap-2"><span class="text-emerald-400 shrink-0 mt-0.5">&#10003;</span><span class="text-slate-300 text-sm">Trust-focused messaging</span></div>
    <div class="flex items-start gap-2"><span class="text-emerald-400 shrink-0 mt-0.5">&#10003;</span><span class="text-slate-300 text-sm">Review integration</span></div>
    <div class="flex items-start gap-2"><span class="text-emerald-400 shrink-0 mt-0.5">&#10003;</span><span class="text-slate-300 text-sm">Stronger calls to action</span></div>
    <div class="flex items-start gap-2"><span class="text-emerald-400 shrink-0 mt-0.5">&#10003;</span><span class="text-slate-300 text-sm">Google Business improvements</span></div>
    <div class="flex items-start gap-2"><span class="text-emerald-400 shrink-0 mt-0.5">&#10003;</span><span class="text-slate-300 text-sm">Email sequence</span></div>
    <div class="flex items-start gap-2"><span class="text-emerald-400 shrink-0 mt-0.5">&#10003;</span><span class="text-slate-300 text-sm">Social content</span></div>
    <div class="flex items-start gap-2"><span class="text-emerald-400 shrink-0 mt-0.5">&#10003;</span><span class="text-slate-300 text-sm">Before &amp; after evidence report</span></div>
  </div>
  <a href="#get-snapshot" class="inline-flex items-center gap-2 rounded-lg bg-amber-500 px-8 py-4 text-base font-bold text-white shadow-lg transition hover:bg-amber-400">Get Your Free Trust Snapshot First →</a>
</div>
</div>
</div>
</section>

<!-- ===== FAQ ===== -->
<section class="py-16 sm:py-20 bg-slate-950">
<div class="max-w-6xl mx-auto px-6">
<div class="max-w-3xl mx-auto">
<div class="text-center mb-10">
  <div class="inline-flex items-center gap-2 bg-amber-500/20 border border-amber-500/40 text-amber-200 text-xs font-semibold uppercase tracking-widest px-4 py-2 rounded-full mb-4">FAQ</div>
  <h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">Common questions</h2>
</div>
<div class="space-y-4">
  <div class="rounded-xl border border-slate-800 bg-slate-900 p-5">
    <p class="font-bold text-white mb-2">How long does the snapshot take?</p>
    <p class="text-sm text-slate-400">Under 60 seconds. Enter your URL and we scan your website and Google Business Profile automatically. Your personalised report is delivered within minutes.</p>
  </div>
  <div class="rounded-xl border border-slate-800 bg-slate-900 p-5">
    <p class="font-bold text-white mb-2">Is it really free?</p>
    <p class="text-sm text-slate-400">Yes. No credit card required, no trial, no hidden fees. You get a full Trust Score and improvement plan at zero cost.</p>
  </div>
  <div class="rounded-xl border border-slate-800 bg-slate-900 p-5">
    <p class="font-bold text-white mb-2">Do I need to buy anything?</p>
    <p class="text-sm text-slate-400">Not at all. The snapshot is yours to keep. If you decide you want help implementing the improvements, we can discuss a Trust Transformation — but there's no obligation.</p>
  </div>
  <div class="rounded-xl border border-slate-800 bg-slate-900 p-5">
    <p class="font-bold text-white mb-2">How accurate is the Trust Score?</p>
    <p class="text-sm text-slate-400">We analyse your site against 14 trust signals we've validated across real transformations. It's designed to surface the most impactful issues, not produce a perfect absolute score.</p>
  </div>
  <div class="rounded-xl border border-slate-800 bg-slate-900 p-5">
    <p class="font-bold text-white mb-2">What happens after the snapshot?</p>
    <p class="text-sm text-slate-400">You receive your report with your score, issues found, and recommended fixes. If you'd like us to implement the improvements, we can schedule a call to discuss a full Trust Transformation. If not, you have a clear roadmap to fix things yourself.</p>
  </div>
</div>
</div>
</div>
</section>

<!-- ===== CTA SECTION ===== -->
<section class="py-16 sm:py-20 gradient-hero" id="get-snapshot">
<div class="max-w-6xl mx-auto px-6">
<div class="max-w-lg mx-auto text-center mb-10">
  <h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">Get your free Trust Snapshot</h2>
  <p class="mt-4 text-slate-300">Enter your details below. Your personalised report will be ready in minutes.</p>
</div>
<div class="max-w-md mx-auto">
<div class="rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
  <div id="form-block">
    <input id="_n2" type="text" placeholder="Full name" class="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white mb-3 placeholder-slate-500 focus:outline-none focus:border-amber-500">
    <input id="_u2" type="text" placeholder="Website" class="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white mb-3 placeholder-slate-500 focus:outline-none focus:border-amber-500">
    <input id="_e2" type="email" placeholder="Email address" class="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white mb-4 placeholder-slate-500 focus:outline-none focus:border-amber-500">
    <button id="_go2" class="w-full rounded-lg bg-amber-500 px-4 py-3 text-sm font-bold text-white shadow-sm hover:bg-amber-400">Get My Free Trust Snapshot →</button>
    <p class="text-xs text-slate-500 text-center mt-3">No credit card needed. Your report will be ready in approximately 5 minutes.</p>
  </div>
  <div id="loading2" class="hidden text-center py-8">
    <div class="spinner mx-auto mb-4"></div>
    <p class="text-sm font-semibold text-slate-300">Analysing your website...</p>
  </div>
  <div id="error2" class="hidden text-center py-4">
    <p class="text-red-400 text-sm font-semibold mb-2">Something went wrong</p>
    <p id="_err2" class="text-slate-400 text-xs mb-3"></p>
    <button onclick="resetForm()" class="rounded-lg bg-slate-800 px-4 py-2 text-xs font-medium text-slate-300">Try again</button>
  </div>
  <div id="results2" class="hidden"></div>
  <div id="redirect2" class="hidden text-center py-4">
    <p class="text-amber-400 text-sm font-semibold">Your report is ready!</p>
    <p class="text-slate-300 text-xs mt-1">Redirecting to your personalised Trust Snapshot...</p>
  </div>
</div>
</div>
</div>
</section>

<!-- ===== FOOTER ===== -->
<footer class="bg-slate-950 border-t border-slate-800 py-12 px-6">
<div class="max-w-6xl mx-auto">
<div class="grid sm:grid-cols-2 md:grid-cols-3 gap-8">
  <div>
    <p class="font-bold text-white text-sm mb-4">Products</p>
    <div class="space-y-2 text-sm">
      <p class="text-slate-400">Discover — Trust Snapshot™ (Free)</p>
      <p class="text-slate-400">Transform — Trust Transformation™ (£995)</p>
      <p class="text-slate-400">Maintain — Trust Monitor™ (£99/mo)</p>
    </div>
  </div>
  <div>
    <p class="font-bold text-white text-sm mb-4">Contact</p>
    <div class="space-y-2 text-sm text-slate-400">
      <p>📞 +44 208 591 1163</p>
      <p>📞 +44 7956 393270</p>
      <p>✉️ info@trusttriggeragency.com</p>
      <p>📍 London, UK</p>
    </div>
  </div>
  <div class="sm:col-span-2 md:col-span-1">
    <p class="text-white text-sm">We help businesses earn and maintain trust online.</p>
    <p class="text-white text-xs mt-1">Powered by The Trust Trigger Transformation Method™</p>
  </div>
</div>
<div class="border-t border-slate-800 mt-8 pt-6 text-center">
  <p class="text-white text-xs">© 2025 Trust Trigger Agency. All rights reserved.</p>
</div>
</div>
</footer>

<style>
.spinner{border:3px solid #334155;border-top:3px solid #f59e0b;border-radius:50%;width:32px;height:32px;animation:spin .8s linear infinite}
@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
</style>

<script>
var A='https://trust-trigger-api.onrender.com';

function $(id){return document.getElementById(id);}
function hide(id){var e=$(id);if(e)e.classList.add('hidden');}
function show(id){var e=$(id);if(e)e.classList.remove('hidden');}
function resetForm(){hide('error2');show('form-block');}

$('_go2').onclick=function(){
  var N=$('_n2').value.trim();
  var U=$('_u2').value.trim();
  var E=$('_e2').value.trim();
  if(!N||!U||!E){alert('Please fill in all fields.');return;}
  hide('form-block');hide('error2');hide('results2');hide('redirect2');
  show('loading2');
  var x=new XMLHttpRequest();
  x.open('POST',A+'/api/v1/public/trust-snapshot',true);
  x.setRequestHeader('Content-Type','application/json');
  x.onload=function(){
    hide('loading2');
    if(x.status==201||x.status==200){
      try{
        var d=JSON.parse(x.responseText);
        if(d.error){$('_err2').textContent=d.error;show('error2');return;}
        if(d.report_url){
          show('redirect2');
          setTimeout(function(){window.location.href=A+d.report_url;},2000);
        }
      }catch(e){$('_err2').textContent='Invalid response';show('error2');}
    }else{$('_err2').textContent='Server error: '+x.status;show('error2');}
  };
  x.onerror=function(){$('_err2').textContent='Network error.';show('error2');};
  x.send(JSON.stringify({full_name:N,website:U,email:E}));
};
</script>
</body>
</html>"""

@router.get("/home", response_class=HTMLResponse)
async def get_homepage():
    return PAGE

@router.get("/", response_class=HTMLResponse)
async def get_root():
    return PAGE
