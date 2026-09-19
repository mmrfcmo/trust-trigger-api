"""Deep Trust Report — comprehensive diagnostic with proposal and fulfilment builder."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
router = APIRouter(prefix="/deep-report", tags=["Public - Deep Report"])
PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Deep Trust Report | TTA — Trust Trigger Agency</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap">
<script src="https://cdn.tailwindcss.com"></script>
<style>
body{font-family:'Inter',system-ui,sans-serif}
.dark-hero{background:linear-gradient(135deg,#0f172a 0%,#1a2a4a 50%,#78350f 100%)}
.spinner{border:3px solid #e5e7eb;border-top:3px solid #f59e0b;border-radius:50%;width:32px;height:32px;animation:s .8s linear infinite}@keyframes s{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
.score-ring{transition:stroke-dashoffset 1.2s ease-out}
</style>
</head>
<body class="bg-slate-950 text-slate-200">

<nav class="bg-slate-900 border-b border-slate-800 h-14 flex items-center px-6">
<div class="max-w-5xl mx-auto w-full flex items-center justify-between">
<a href="/home" class="flex items-center gap-2"><span class="w-8 h-8 rounded-lg bg-amber-500 text-white flex items-center justify-center text-xs font-bold">TTA</span> <span class="hidden sm:inline text-amber-400 font-extrabold text-lg">Trust Trigger Agency</span></a>
</div>
</nav>

<div class="dark-hero text-white py-16 px-6 text-center">
<p class="text-xs font-bold uppercase tracking-[.2em] text-amber-300 mb-2">The Trust Trigger Method</p>
<h1 class="text-3xl sm:text-4xl font-extrabold">Your Trust Trigger Report</h1>
<p class="text-slate-300 text-sm mt-2 max-w-lg mx-auto">We analyse your website across 14 trust standards — then tell you exactly what's costing you customers and how to fix it.</p>
</div>

<div class="max-w-3xl mx-auto px-6 py-10">

<div id="form" class="max-w-md mx-auto">
<div class="rounded-xl border border-slate-800 bg-slate-900 shadow-sm p-6">
<p class="text-sm font-bold text-white mb-4">Enter a website to analyse</p>
<input id="_n" type="text" placeholder="Business name" class="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white mb-2.5 placeholder-slate-500 focus:outline-none focus:border-amber-500">
<input id="_u" type="text" placeholder="Website URL" class="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white mb-2.5 placeholder-slate-500 focus:outline-none focus:border-amber-500">
<input id="_e" type="email" placeholder="Your email" class="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white mb-4 placeholder-slate-500 focus:outline-none focus:border-amber-500">
<button id="_go" class="w-full rounded-lg bg-amber-500 px-4 py-2.5 text-sm font-bold text-white shadow-sm hover:bg-amber-400">Generate Your Trust Report →</button>
<p class="text-xs text-slate-500 text-center mt-2">Free. No card. Takes 30 seconds.</p>
</div>
</div>

<div id="loading" class="hidden text-center py-16">
<div class="spinner mx-auto mb-4"></div>
<p class="text-sm font-semibold text-slate-300">Scanning your website...</p>
</div>

<div id="error" class="hidden text-center py-10">
<p class="text-red-400 text-sm font-semibold mb-2">Something went wrong</p>
<p id="_err" class="text-slate-500 text-xs mb-3"></p>
<button onclick="f()" class="rounded-lg bg-slate-800 px-4 py-2 text-xs font-medium text-slate-300">Try again</button>
</div>

<div id="results" class="hidden"></div>

</div>

<footer class="bg-slate-900 text-slate-500 py-10 px-6 text-center text-xs">
<p class="text-amber-400">&copy; 2025 TTA — Trust Trigger Agency &middot; The Trust Trigger Transformation Method</p>
</footer>

<script>
var A='';var R=null,N='',U='';
var AVG_CUSTOMER_LTV = 3500;

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
  var weeklyLoss = Math.round((100 - s) / 100 x 10 x AVG_CUSTOMER_LTV;
  var weeklyImpact = Math.round((100 - s) / 100 * 10);
  if(s>=80) return {label:'Strong (B)',color:'text-emerald-400',desc:'Your website builds trust reasonably well, but specific gaps still prevent some visitors from booking.',impact:weeklyImpact+' enquiries/week',loss:'&pound;'+weeklyLoss.toLocaleString()+'/week'};
  if(s>=60) return {label:'Good (C)',color:'text-emerald-400',desc:'Your site is credible but missing key trust signals that convert visitors into customers.',impact:weeklyImpact+' enquiries/week',loss:'&pound;'+weeklyLoss.toLocaleString()+'/week'};
  if(s>=40) return {label:'Average (D)',color:'text-amber-400',desc:'Your website is losing potential customers. Several trust signals are missing.',impact:weeklyImpact+' enquiries/week',loss:'&pound;'+weeklyLoss.toLocaleString()+'/week'};
  if(s>=20) return {label:'Weak (E)',color:'text-orange-400',desc:'Significant trust gaps. Most visitors leave without contacting you.',impact:weeklyImpact+' enquiries/week',loss:'&pound;'+weeklyLoss.toLocaleString()+'/week'};
  return {label:'At Risk (F)',color:'text-red-400',desc:'Critical trust issues. Your website is actively repelling customers.',impact:weeklyImpact+' enquiries/week',loss:'&pound;'+weeklyLoss.toLocaleString()+'/week'};
}

var PILLAR_INSIGHTS={
  'Online Presence':{
    critical:'Your website is hard to find or looks unprofessional on first glance. Visitors judge your business in under 3 seconds — and they are leaving before they even read your content. Missing or incomplete key pages means every prospect who lands on your site struggles to decide if you are legitimate.',
    warning:'Your online presence exists but lacks polish. Key pages may be missing or incomplete. Each missing page is a prospect who cannot decide to trust you and leaves for a competitor.',
    good:'Your online presence is solid. Maintain it to keep your competitive edge.'
  },
  'Reputation':{
    critical:'You have zero or dangerously low social proof online. No reviews, no testimonials, no case studies displayed on your site. 71% of customers check reviews before choosing a business — you are invisible during the most critical part of their decision process. Your competitors are collecting reviews while you remain silent.',
    warning:'You have some reputation signals but they are not prominent or recent enough. Customers who see testimonials are 58% more likely to book. You are leaving money on the table by not featuring your best reviews.',
    good:'Your reputation signals are working. Keep collecting and prominently displaying fresh reviews.'
  },
  'Engagement':{
    critical:'Your site has no clear calls-to-action, no visible contact options, and no clear path for visitors to take the next step. You are actively sending ready-to-buy prospects to competitors who make it easy to convert. Every page without a "Book Now" or "Contact Us" button is a silent revenue leak.',
    warning:'Some calls-to-action exist but they are not prominent or compelling enough. Every extra click a customer makes to contact you reduces conversion by roughly 20%. Your CTAs need to be impossible to miss.',
    good:'Your engagement flow is solid. Test different CTAs and placements to keep improving conversion rates.'
  },
  'Transparency':{
    critical:'Your business appears faceless online. No About page, no team photos, no credentials, no privacy policy. You are asking visitors to trust a business they cannot see or verify. In competitive markets, a faceless business is an untrusted business — prospects choose the company that shows their people and story.',
    warning:'Basic information exists but lacks depth and warmth. Detailed About pages with real team photos increase enquiry volume by 20-35%. Customers want to know who they are trusting before they commit.',
    good:'Your transparency is solid. Customers know who you are and what you stand for.'
  },
  'Technical Health':{
    critical:'Your site has serious technical issues — slow loading, not mobile-friendly, or missing HTTPS. Over 60% of visitors come from mobile devices. If your site does not work perfectly on their phone, they leave within 3 seconds and never return. Google also penalises slow and non-mobile sites in search rankings.',
    warning:'Some technical issues exist that may be costing you visitors. Page speed and mobile responsiveness directly impact both user trust and Google ranking. Every second of delay reduces conversion by 7%.',
    good:'Your technical foundation is solid. Fast, secure, and mobile-friendly.'
  }
};

var DIAG={
  'Https':{
    issue:'Your site does not use HTTPS or redirects to a non-secure version.',
    means:'Browsers show a "Not Secure" warning. In your industry, this destroys trust immediately.',
    benefit:'Green padlock = instant trust. Google ranks HTTPS sites higher.',
    findings:['Your site loads over unencrypted HTTP, triggering browser "Not Secure" warnings','This means customers see a red warning triangle before seeing your content','Any form submissions on your site are sent without encryption — a data protection risk'],
    bizImplications:['Customers who see "Not Secure" warnings rarely proceed — bounce rates increase by 60-80% on first visit','Google Chrome flags non-HTTPS sites, which directly lowers your search ranking and visibility','Industry compliance bodies (CQC, ICO) expect encrypted data handling — you are at regulatory risk'],
    notfixReasons:['Every customer who lands on a non-secure page leaves before booking — estimated 7-8 lost enquiries per week','Google demotes non-HTTPS sites in search results by up to 2 positions, costing 30-40% of organic traffic','Data protection regulators can fine businesses up to 4% of turnover for failing to secure customer data in transit'],
    considerations:['A single SSL certificate costs less than &pound;50/year — the ROI from recovered bookings is over 100x','Customers compare your site against competitors. A "Not Secure" warning makes them choose the business with a padlock','Search engines now treat HTTPS as a ranking signal — without it you are invisible for half your potential search traffic']
  },
  'contact_page':{
    issue:'No clear contact page with full details.',
    means:'Customers who want to book have to hunt for how to reach you. Extra clicks = lost leads.',
    benefit:'A clear contact page can increase enquiries by 20-30%.',
    findings:['Your site does not prominently display a phone number, email, or address','There is no dedicated contact page with a form for enquiries','Opening hours and business location information is not easily accessible'],
    bizImplications:['Customers ready to book have to search for contact details — 30-40% leave the site before finding them','Without a contact form, enquiry abandonment rates are significantly higher','Missing address and hours means local customers cannot assess convenience or proximity'],
    notfixReasons:['30-40% of motivated customers cannot find how to contact you and choose a competitor who makes it easy','Staff waste time on the phone giving directions and hours that should be on the site — estimated 5-8 hours/week','Google Local Pack visibility requires consistent NAP (name, address, phone) data — missing contact page undermines local SEO'],
    considerations:['Adding phone, email, form, and map in one place costs a single page and can recover 3-5 lost bookings per week (worth &pound;10K-&pound;18K/year in customer LTV)','Every extra click a customer makes to contact you reduces conversion rate by roughly 20%','Businesses with a clear contact page receive 25% more inbound enquiry calls within the first month alone']
  },
  'about_page':{
    issue:'No compelling About page showing your team and story.',
    means:'You are asking visitors to trust a faceless business. They will choose a business with real people.',
    benefit:'An About page with team photos humanises your business. It is one of the most visited pages.',
    findings:['Your site has no About page — or the one it has lacks team photos, bios, and credentials','Visitors cannot see who runs the business or what qualifications the team holds','There is no story or founding philosophy to build an emotional connection'],
    bizImplications:['Customers choose providers they trust — a faceless site leads to comparison shopping with competitors who show their team','Without credentials and experience displayed, price sensitivity increases and perceived value drops','The About page is the second-most visited page on industry websites after the homepage'],
    notfixReasons:['Customers researching your business will compare you against competitors — those with team pages convert at roughly double the rate','Without visible credentials, customers assume lower expertise and are 40% less likely to book high-value services','Businesses that add an About page with team photos typically see enquiry volume increase by 20-35% within 6 weeks'],
    considerations:['Customers pay a premium for expertise they can see. Displaying 20+ years of experience justifies higher service fees','A well-written About page with photos adds emotional trust — the primary factor in choosing a service provider','Without an About page, your site costs you an estimated 4-8 lost opportunities per week worth &pound;14K-&pound;30K/year']
  },
  'cta':{
    issue:'No clear calls-to-action telling visitors what to do.',
    means:'Visitors land, browse, then leave. Without a "Book Now" button, you are not asking for the booking.',
    benefit:'A well-placed CTA can double your conversion rate.',
    findings:['Your site lacks prominent "Book Now" or "Contact Us" buttons above the fold','There is no clear next step on service pages — customers read and then hit a dead end','No sticky header or floating CTA that follows the user as they scroll'],
    bizImplications:['Without explicit calls-to-action, visitors consume content and leave without taking action — conversion rates drop by 50-70%','Customers are often on mobile and expect a one-tap call or booking button — without it, they bounce','Each service page without a CTA is a missed booking opportunity worth thousands in customer LTV'],
    notfixReasons:['Every visitor who reads a service page and finds no "Book Now" button is a lost booking — typically 5-10 per week','Without CTAs, your website acts as a brochure rather than a revenue channel — the difference between &pound;0 and &pound;25K+/month from your site','80% of website visitors use mobile — a floating "Call Now" button can double phone enquiries overnight'],
    considerations:['A single well-placed CTA button costs nothing to add but can generate 4-8 new bookings per week worth &pound;14K-&pound;30K/year in customer LTV','Customers on your site have high intent — failing to ask for the booking is the most expensive mistake in marketing','Every CTA you add shortens the time between "interested" and "booked", reducing competitor exposure']
  },
  'testimonials':{
    issue:'No customer reviews or testimonials displayed.',
    means:'Social proof is everything. Without reviews, new visitors have no reason to trust you.',
    benefit:'Displaying reviews builds instant credibility. Customers who see testimonials are 58% more likely to book.',
    findings:['Your site displays no customer reviews, testimonials, or case studies','There are no before/after images or outcome stories','Online reviews exist but are not embedded or referenced on your website'],
    bizImplications:['71% of customers read online reviews before choosing a provider — without social proof on your site, they check elsewhere and may book a competitor','Website visitors who see testimonials convert at 58% higher rates than those who do not','Without customer stories, your service pages lack the emotional proof that justifies your pricing'],
    notfixReasons:['Customers who leave your site to check reviews may not return — 3-5 enquiries per week lost to competitors with stronger social proof','Testimonials increase perceived value by 25-40%, directly supporting your pricing. Without them, customers are more price-sensitive','Case studies of successful outcomes build authority and justify premium fees for specialist services'],
    considerations:['Embedding 5-8 customer reviews on your site can increase conversion by up to 58% — this typically recovers 4-6 bookings/week worth &pound;14K-&pound;22K/year','A single video testimonial from a happy customer carries more trust value than any amount of marketing copy','Customers trust peer experiences over marketing claims — testimonials are the most cost-effective trust builder']
  },
  'faq':{
    issue:'No FAQ section addressing common customer questions.',
    means:'Every customer asks: cost, duration, process, booking. Without answers, they call a competitor who has answers ready.',
    benefit:'FAQs answer objections before they arise. Saves staff time, builds trust.',
    findings:['Your site has no FAQ section answering the most common customer questions','Key questions — service costs, timeline, process — are not addressed','Customers cannot self-serve basic information and must call or email for answers'],
    bizImplications:['Without FAQs, every potential customer hits the same objections with no answers — increasing friction and abandonment','Staff spend 30-50% of their time answering the same questions that a FAQ page could handle','Customers who have to call for basic information often comparison-shop before booking — giving competitors a chance to win them'],
    notfixReasons:['Each day without FAQs costs 10-20 minutes of staff time per repeated question — adding up to 5-10 hours/week of wasted labour','FAQ pages reduce phone enquiry volume by 25-30%, freeing staff for booking conversations rather than information calls','Without cost information on your site, price-sensitive customers self-select out before even contacting you — losing 3-5 potential bookings/week'],
    considerations:['An FAQ page addressing 15-20 common questions can save 5-10 hours of staff time per week — worth &pound;6K-&pound;12K/year in labour hours','Customers who find answers on your site are 2x more likely to book than those who have to call for information','Putting pricing transparency in FAQs filters for qualified, committed customers — reducing wasted phone calls by 30%']
  },
  'service_pages':{
    issue:'Services not clearly detailed on your website.',
    means:'Customers arrive looking for specific services. If they cannot find clear info, they leave.',
    benefit:'Detailed service pages establish you as an expert and answer questions before they are asked.',
    findings:['Your service pages lack depth — little detail on what each service involves','There is no information about outcomes, process, or what to expect','Prices or price ranges are not visible for common services'],
    bizImplications:['Customers searching for a specific service will choose the business that explains it clearly — you lose to competitors with detailed pages','Thin service pages signal low expertise to both customers and search engines, harming organic rankings','Without outcome information, customers cannot visualise the benefit, reducing perceived value and willingness to book'],
    notfixReasons:['Detailed service pages rank higher in Google and drive 3-5x more organic traffic than thin pages — you are losing 8-12 visits per service per month','Customers who cannot find service details leave within 15 seconds — costing 4-7 lost opportunities per week','Without pricing transparency on key services, customers assume costs are higher than they are and self-select out'],
    considerations:['Each well-written service page can generate 2-4 direct booking enquiries per month — worth &pound;7K-&pound;14K/year per page in customer LTV','Customers who read detailed service information before calling are 60% more likely to book on the first contact','Investing in 5 detailed service pages typically recovers the cost of a full website rebuild within 3-4 months']
  },
  'privacy_policy':{
    issue:'No privacy policy or GDPR compliance page.',
    means:'Customers need to know their data is safe. Missing privacy policy creates legal risk too.',
    benefit:'A privacy policy builds trust and keeps you compliant with GDPR.',
    findings:['Your site has no visible privacy policy — customers have no way to understand how their data is handled','There is no cookie consent banner or data processing notice','Customer data submission (forms, bookings) happens without a clear data protection statement'],
    bizImplications:['Privacy-conscious customers will not submit personal details without knowing how data is handled — losing form completions and bookings','GDPR non-compliance can result in fines of up to 4% of annual turnover or &pound;17.5M, whichever is higher','Customer data is classified as special category data under GDPR — the requirements and risks are significant'],
    notfixReasons:['Without a privacy policy, you risk ICO enforcement action — businesses have received fines of &pound;10K-&pound;60K for basic GDPR failures','Privacy-conscious customers (25-35% of visitors) will not submit contact forms — losing 2-4 potential bookings per week','Missing privacy pages undermine trust signals for AI systems and search engines, reducing your overall trust score'],
    considerations:['A compliant privacy policy takes one hour to draft and removes a significant legal risk — the cost of non-compliance is far higher than the effort to fix it','Customers are 2x more likely to submit their details when a privacy statement is visible next to the form','Displaying GDPR compliance actively builds trust with privacy-aware customer segments — a competitive advantage']
  },
  'mobile_responsive':{
    issue:'Site not fully optimised for mobile devices.',
    means:'Over 60% of website visits come from phones. If your site is hard to use on mobile, you lose most of your traffic.',
    benefit:'Mobile-friendly sites keep customers engaged and rank higher on Google.',
    findings:['Your site does not display properly on mobile devices — text is too small, buttons are hard to tap, content is cut off','Navigation is difficult on phone screens, making it hard for customers to find key information','Page load speed on mobile is slow, causing visitors to leave before the content loads'],
    bizImplications:['Over 60% of website visits come from mobile devices — a poor mobile experience alienates the majority of your traffic','Google uses mobile-first indexing — your mobile experience determines your search ranking for ALL visitors','Mobile users are 3x more likely to leave a site that takes longer than 3 seconds to load'],
    notfixReasons:['A non-mobile-friendly site loses 60%+ of potential customers before they even see your content — typically 8-12 lost opportunities per week','Google penalises non-mobile-friendly sites by 3-5 search positions, reducing organic traffic by 40-50%','Mobile bounce rates above 70% indicate your site is actively repelling phone users — costing an estimated &pound;20K-&pound;40K/year'],
    considerations:['Making your site mobile-friendly can reduce bounce rates from 70% to 30% and double mobile enquiry volume within weeks','Google mobile-first indexing means your mobile site IS your primary site — fixing mobile is non-negotiable for search visibility','Customers browsing on their phone are high-intent — failing to serve them loses bookings you have already earned']
  }
};

function render(){
  var d=R;if(!d)return;
  var sc=d.score||0,g=gr(sc),isWP=d.is_wordpress||false,pills=d.pillars||[],stds=d.standards||[],iss=d.issues||[];
  var now=new Date();
  var h='';
  
  h+='<div class="rounded-xl border border-slate-800 bg-slate-900 shadow-sm p-6">';
  h+='<div class="flex items-start gap-5"><div class="relative w-20 h-20 shrink-0"><svg class="w-20 h-20 -rotate-90" viewBox="0 0 120 120"><circle cx="60" cy="60" r="52" fill="none" stroke="#334155" stroke-width="10"/><circle class="score-ring" id="sc" cx="60" cy="60" r="52" fill="none" stroke="#f59e0b" stroke-width="10" stroke-dasharray="326.7" stroke-dashoffset="326.7"/></svg><div class="absolute inset-0 flex items-center justify-center"><span class="text-xl font-extrabold text-white" id="sn">0</span></div></div>';
  h+='<div><p class="text-xs font-bold uppercase tracking-wider text-slate-400">Trust Trigger Score</p><h2 class="text-xl font-bold text-white">'+g.label+'</h2><p class="font-semibold text-slate-300 text-sm">'+N+'</p><p class="text-xs text-slate-500">'+U+'</p><p class="text-sm text-slate-400 mt-2">'+g.desc+'</p></div></div>';

  var weeklyLossVal = Math.round((100 - sc) / 100 x 10 x AVG_CUSTOMER_LTV;
  h+='<div class="mt-4 bg-red-950 border border-red-900 rounded-lg p-4"><p class="text-sm font-bold text-red-400">Estimated Revenue Impact</p><p class="text-sm text-red-300 mt-1">Based on an average customer lifetime value of <strong class="text-white">&pound;'+AVG_CUSTOMER_LTV.toLocaleString()+'</strong>, your current trust gaps are likely costing you <strong>'+g.impact+'</strong> — approximately <strong>&pound;'+weeklyLossVal.toLocaleString()+'/week</strong> (&pound;'+(weeklyLossVal*52).toLocaleString()+'/year) in missed revenue.</p></div>';
  h+='<div class="mt-3 text-xs text-slate-500 flex flex-wrap gap-3"><span>'+now.toLocaleDateString("en-GB",{day:"numeric",month:"long",year:"numeric"})+'</span><span>'+pills.length+' pillars</span><span>'+iss.length+' issues</span></div>';
  h+='</div>';
  
  h+='<div class="mt-5 rounded-xl border border-slate-800 bg-slate-900 shadow-sm p-4">';
  if(isWP) h+='<p class="text-sm font-semibold text-emerald-400">WordPress Site — We can publish content directly to your existing site. Your theme is preserved.</p>';
  else h+='<p class="text-sm font-semibold text-amber-400">Custom Platform — We will build you a brand new dedicated website. Full design control. Ready in 28 days.</p>';
  h+='</div>';
  
  if(pills.length){
    h+='<div class="mt-8"><p class="text-lg font-bold text-white mb-1">Trust Pillar Breakdown</p><p class="text-sm text-slate-400 mb-5">Your website scored across 5 trust dimensions. Each pillar reveals a specific reason visitors may leave without converting.</p>';
    pills.forEach(function(p){
      var pc=Math.round(p.percentage),l=p.label||p.name;
      if(pc<1 && p.percentage===0) { pc=0; }
      var insight = '';
      var insightColor = '';
      var pi = PILLAR_INSIGHTS[l];
      if(pi) {
        if(pc<40) { insight = pi.critical; insightColor = 'text-red-400'; }
        else if(pc<80) { insight = pi.warning; insightColor = 'text-amber-400'; }
        else { insight = pi.good; insightColor = 'text-emerald-400'; }
      }
      var b=pc>=80?'bg-emerald-500':pc>=60?'bg-amber-500':pc>=40?'bg-orange-500':'bg-red-500';
      var t=pc>=80?'text-emerald-400':pc>=60?'text-amber-400':pc>=40?'text-orange-400':'text-red-400';
      var displayLabel = pc+'%';
      if(pc===0) { b='bg-zinc-600'; t='text-zinc-400'; displayLabel='Not scored'; insight = 'This pillar was not scored because the data was insufficient or unavailable. This itself is a red flag — it means your business is invisible across critical trust dimensions that customers check before converting.'; insightColor = 'text-red-400'; }
      h+='<div class="rounded-xl border border-slate-800 bg-slate-900 shadow-sm p-4 mb-3">';
      h+='<div class="flex justify-between items-center mb-1"><span class="text-sm font-bold text-white">'+l+'</span><span class="text-sm font-bold '+t+'">'+displayLabel+'</span></div>';
      h+='<div class="h-2 bg-slate-800 rounded-full overflow-hidden"><div class="h-full rounded-full '+b+'" style="width:'+(pc||5)+'%"></div></div>';
      if(insight){ h+='<p class="text-xs '+insightColor+' mt-2 leading-relaxed">'+insight+'</p>'; }
      h+='</div>';
    });
    h+='</div>';
  }
  
  if(stds.length){
    h+='<div class="mt-8"><p class="text-lg font-bold text-white mb-1">Deep Diagnostic: Every Standard Checked</p><p class="text-sm text-slate-400 mb-5">Below is what we found, what it could mean for your business, and 3 reasons why each issue matters.</p>';
    stds.forEach(function(st){
      var dg=DIAG[st.name]||{issue:'Standard checked.',findings:['This standard was evaluated during your scan.','No specific issues were detected for this area.','Your performance here appears satisfactory.'],bizImplications:['No significant business impact identified.','Your site meets expectations in this area.','Continue monitoring for any changes.'],notfixReasons:['No critical issues found in this category.','Your current setup is adequate.','Address related issues from other categories first.'],considerations:['Keep this area maintained as part of ongoing trust optimisation.','Review quarterly for any changes in best practices.','Include this in your regular site audits.']};
      var lb=st.name.replace(/([A-Z])/g,' $1').replace(/^./,function(x){return x.toUpperCase()}).trim();
      if(st.name==='Https')lb='HTTPS';if(st.name==='Cta')lb='Call-to-Action';if(st.name==='Faq')lb='FAQ Section';
      var icon=st.passed?'&#10004;':'&#10008;';var border=st.passed?'border-emerald-900':'border-red-900';
      h+='<div class="rounded-xl border '+border+' bg-slate-900 shadow-sm p-5 mb-4"><div class="flex items-center gap-2 mb-3"><span>'+icon+'</span><p class="text-sm font-bold text-white">'+lb+'</p></div>';
      if(!st.passed){
        h+='<div class="space-y-4">';
        h+='<div><p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">What we found</p>';
        dg.findings.forEach(function(f){ h+='<p class="text-sm text-slate-300 mb-1">&bull; '+f+'</p>'; });
        h+='</div>';
        h+='<div><p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">What this could mean for your business</p>';
        dg.bizImplications.forEach(function(b){ h+='<p class="text-sm text-slate-300 mb-1">&bull; '+b+'</p>'; });
        h+='</div>';
        h+='<div class="bg-emerald-950 border border-emerald-900 rounded-lg p-3"><p class="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-1">Benefit of fixing this</p><p class="text-sm text-emerald-300">'+dg.benefit+'</p></div>';
        h+='<div class="bg-red-950 border border-red-900 rounded-lg p-3"><p class="text-xs font-bold text-red-400 uppercase tracking-wider mb-1">The cost of not fixing this</p>';
        dg.notfixReasons.forEach(function(n){ h+='<p class="text-sm text-red-300 mb-1">&bull; '+n+'</p>'; });
        h+='</div>';
        h+='<div class="bg-amber-950 border border-amber-900 rounded-lg p-3"><p class="text-xs font-bold text-amber-400 uppercase tracking-wider mb-1">Why you should act now</p>';
        dg.considerations.forEach(function(c){ h+='<p class="text-sm text-amber-300 mb-1">&bull; '+c+'</p>'; });
        h+='</div>';
        h+='</div>';
      } else { h+='<p class="text-sm text-emerald-400 font-medium">This trust signal is working in your favour.</p>'; }
      h+='</div>';
    });
    h+='</div>';
  }
  
  if(iss.length){
    h+='<div class="mt-8"><p class="text-lg font-bold text-white mb-1">Priority Issues</p><p class="text-sm text-slate-400 mb-5">These specific gaps are costing you revenue right now.</p>';
    iss.forEach(function(x,i){
      h+='<div class="border-l-4 border-red-500 bg-slate-900 rounded-r-xl shadow-sm p-5 mb-3"><div class="flex items-start gap-3"><span class="shrink-0 w-7 h-7 rounded-full bg-red-900 text-red-400 flex items-center justify-center text-sm font-bold">'+(i+1)+'</span><div><p class="text-sm font-bold text-white">'+x.title+'</p><p class="text-sm text-slate-400 mt-1">'+x.detail+'</p></div></div></div>';
    });
    h+='</div>';
  }
  
  h+='<div class="mt-10"><div class="rounded-xl border-2 border-amber-500 bg-slate-950 shadow-sm p-6">';
  h+='<p class="text-xs font-bold text-amber-400 uppercase tracking-wider">Our Recommendation</p>';
  h+='<p class="text-2xl font-bold text-white mt-1 mb-5">Trust Transformation Proposal</p>';
  h+='<div class="bg-slate-900 border border-slate-800 rounded-lg p-4 mb-5"><table class="w-full text-sm"><tbody>';
  h+='<tr class="border-b border-slate-800"><td class="py-2 font-medium text-slate-300">Package</td><td class="py-2 text-right font-bold text-white">Trust Transformation</td></tr>';
  h+='<tr class="border-b border-slate-800"><td class="py-2 font-medium text-slate-300">Price</td><td class="py-2 text-right"><span class="text-xl font-extrabold text-amber-400">&pound;995</span><span class="text-xs text-slate-500 ml-1">one-time</span></td></tr>';
  var deliveryDays = isWP ? 14 : 28;
  h+='<tr class="border-b border-slate-800"><td class="py-2 font-medium text-slate-300">Delivery</td><td class="py-2 text-right font-semibold text-white">'+deliveryDays+' days</td></tr>';
  h+='<tr><td class="py-2 font-medium text-slate-300">Projected score</td><td class="py-2 text-right font-semibold text-emerald-400">'+sc+' &rarr; 85+</td></tr>';
  h+='</tbody></table></div>';
  h+='<ul class="space-y-2 mb-5 text-sm">';
  h+='<li class="flex items-start gap-2"><span class="text-emerald-400">&#10003;</span><span class="text-slate-300">Full website trust audit completed</span></li>';
  h+='<li class="flex items-start gap-2"><span class="text-emerald-400">&#10003;</span><span class="text-slate-300">New homepage copy optimised for conversion</span></li>';
  h+='<li class="flex items-start gap-2"><span class="text-emerald-400">&#10003;</span><span class="text-slate-300">5-email nurture sequence for new enquiries</span></li>';
  h+='<li class="flex items-start gap-2"><span class="text-emerald-400">&#10003;</span><span class="text-slate-300">Google Business Profile content (10 posts)</span></li>';
  h+='<li class="flex items-start gap-2"><span class="text-emerald-400">&#10003;</span><span class="text-slate-300">Social media content (Facebook + Instagram)</span></li>';
  if(isWP) h+='<li class="flex items-start gap-2"><span class="text-emerald-400">&#10003;</span><span class="text-slate-300">Direct WordPress publishing (14-day delivery)</span></li>';
  else h+='<li class="flex items-start gap-2"><span class="text-emerald-400">&#10003;</span><span class="text-slate-300">Brand new website build (5-7 pages, hosted — 28-day delivery)</span></li>';
  h+='<li class="flex items-start gap-2"><span class="text-emerald-400">&#10003;</span><span class="text-slate-300">Before/after evidence report with score improvement</span></li>';
  h+='</ul>';
  h+='<div class="text-center"><a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone" class="inline-block rounded-lg bg-amber-500 px-8 py-3 text-base font-bold text-white shadow-sm hover:bg-amber-400">Book Your Free 20-Minute Trust Review &rarr;</a><p class="text-xs text-slate-500 mt-2">Free. No obligation.</p></div>';
  h+='</div></div>';
  
  h+='<div class="mt-8"><div class="rounded-xl border border-slate-800 bg-slate-900 shadow-sm p-6">';
  h+='<p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">How We Deliver</p>';
  h+='<h3 class="text-lg font-bold text-white mb-5">Your '+deliveryDays+'-Day Fulfilment Timeline</h3>';
  var timeline;
  if(isWP){
    timeline = [['1','Strategy Call','We review your report. You confirm scope.'],['2-5','Content Creation','Homepage copy, emails, GBP posts, social content.'],['6-8','Your Review','Preview link sent. You approve or request changes.'],['9-12','Publishing','Content goes live on WordPress. Theme preserved.'],['13-14','Evidence Report','Rescan + before/after report showing score improvement.']];
  } else {
    timeline = [['1-2','Strategy &amp; Scope','We review your report. You confirm scope and design preferences.'],['3-10','Design &amp; Build','5-7 page website designed and built on custom platform.'],['11-16','Content Creation','All copy, images, and trust signals integrated into site.'],['17-22','Your Review','Preview link sent. You review and request changes.'],['23-26','Revisions &amp; Polish','We implement your feedback and finalise the site.'],['27-28','Launch &amp; Evidence','Site goes live. Rescan + before/after report with score improvement.']];
  }
  timeline.forEach(function(s){
    h+='<div class="flex items-start gap-4 mb-4"><span class="shrink-0 w-8 h-8 rounded-full bg-amber-900 text-amber-300 flex items-center justify-center text-sm font-bold">'+s[0]+'</span><div><p class="text-sm font-bold text-white">'+s[1]+'</p><p class="text-xs text-slate-400">'+s[2]+'</p></div></div>';
  });
  h+='<div class="mt-4 bg-slate-900 border border-slate-800 rounded-lg p-4"><p class="text-sm text-slate-300">Your time commitment: <strong class="text-white">~20 minutes total</strong> (one call + one approval). We do the rest.</p></div>';
  h+='</div></div>';
  
  h+='<div class="mt-8 text-center"><a href="https://calendly.com/mrfcmo/ai-readiness-review-call-clone" class="inline-block rounded-lg bg-amber-500 px-8 py-3.5 text-base font-bold text-white shadow-sm hover:bg-amber-400">Book Your Free Trust Review &rarr;</a></div>';
  
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
