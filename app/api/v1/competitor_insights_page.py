function startCompare(){
  var n=$('businessName').value.trim(),u=$('website').value.trim(),i=$('industry').value.trim();
  if(!n||!u||!i){alert('Fill in all fields.');return;}
  h($('inputSection'));h($('errorSection'));h($('resultsSection'));s($('loadingSection'));
  $('compLoadingStatus').textContent='Scanning your website...';
  var e='c'+Date.now()+'@temp.com';
  rs(n,u,e).then(function(you){
    $('compLoadingStatus').textContent='Finding competitors...';
    return fc(i,u,n).then(function(r){
      var comps=r.competitors||[];
      if(comps.length>0){
        var c1=comps[0],c2=comps.length>1?comps[1]:comps[0];
        $('compLoadingStatus').textContent='Scanning competitor: '+c1.name+'...';
        var e1='c1_'+Date.now()+'@temp.com';
        return rs(c1.name,c1.site,e1).then(function(c1Data){
          $('compLoadingStatus').textContent='Scanning competitor: '+c2.name+'...';
          var e2='c2_'+Date.now()+'@temp.com';
          return rs(c2.name,c2.site,e2).then(function(c2Data){
            $('compLoadingStatus').textContent='Building comparison...';
            setTimeout(function(){showComp(you,c1Data,c2Data,n,u,c1.name||'Competitor 1',c1.site||'unknown',c2.name||'Competitor 2',c2.site||'unknown');},300);
          });
        });
      } else {
        showComp(you,null,null,n,u,'Not found','','Not found','');
      }
    });
  }).catch(function(){
    h($('loadingSection'));
    $('compErrorMsg').textContent='Unable to scan your website. Please check the URL and try again.';
    s($('errorSection'));
  });
}
function showComp(you,c1Data,c2Data,n,u,c1n,c1u,c2n,c2u){
  h($('loadingSection'));s($('resultsSection'));
  var ys=you.score||0;
  var cs1=c1Data?c1Data.score||0:0;
  var cs2=c2Data?c2Data.score||0:0;
  $('hdrYou').textContent=n;$('hdrC1').textContent=c1n;$('hdrC2').textContent=c2n;
  $('yourLabel').textContent=n;$('yourScore').textContent=ys;
  setTimeout(function(){$('yourBar').style.width=ys+'%';},200);
  $('c1Label').textContent=c1n;$('c1Score').textContent=cs1;
  setTimeout(function(){$('c1Bar').style.width=cs1+'%';},400);
  $('c2Label').textContent=c2n;$('c2Score').textContent=cs2;
  setTimeout(function(){$('c2Bar').style.width=cs2+'%';},600);
  var tb=$('comparisonBody');tb.innerHTML='';
  function ar(l,y,c1v,c2v){
    var tr=document.createElement('tr');tr.className='border-b border-zinc-100';
    tr.innerHTML='<td class="py-3 pr-4 text-sm font-medium text-zinc-700">'+l+'</td><td class="py-3 px-4 text-sm font-semibold text-emerald-700">'+(y||'-')+'</td><td class="py-3 px-4 text-sm text-zinc-600">'+(c1v||'-')+'</td><td class="py-3 px-4 text-sm text-zinc-600">'+(c2v||'-')+'</td>';
    tb.appendChild(tr);
  }
  ar('Trust Score',ys,cs1,cs2);
  ar('Grade',you.grade||gr(ys),c1Data?c1Data.grade||gr(cs1):'N/A',c2Data?c2Data.grade||gr(cs2):'N/A');
  var youPills=you.pillars||[];var c1Pills=c1Data?c1Data.pillars||[]:[];var c2Pills=c2Data?c2Data.pillars||[]:[];
  var allLabels=['Online Presence','Reputation','Engagement','Transparency','Technical Health'];
  for(var i=0;i<allLabels.length;i++){
    var yp='-',c1p='-',c2p='-';
    for(var j=0;j<youPills.length;j++){if(youPills[j].label===allLabels[i]){yp=Math.round(youPills[j].percentage)+'%';break;}}
    for(var j=0;j<c1Pills.length;j++){if(c1Pills[j].label===allLabels[i]){c1p=Math.round(c1Pills[j].percentage)+'%';break;}}
    for(var j=0;j<c2Pills.length;j++){if(c2Pills[j].label===allLabels[i]){c2p=Math.round(c2Pills[j].percentage)+'%';break;}}
    ar(allLabels[i],yp,c1p,c2p);
  }
  ar('Issues Found',you.issues_found||0,c1Data?c1Data.issues_found||'-':'-',c2Data?c2Data.issues_found||'-':'-');
  var il=$('insightsList');il.innerHTML='';var ins=[];
  if(ys>cs1&&ys>cs2){ins.push('<strong>You have the highest Trust Score</strong> among your competitors.');}
  else if(ys<cs1&&ys<cs2){ins.push('<strong>Your score is lower than competitors.</strong> Significant opportunities to improve.');}
  else if(ys<cs1||ys<cs2){ins.push('<strong>You are behind at least one competitor.</strong>');}
  else{ins.push('<strong>You are competitive.</strong> Small improvements could give you an edge.');}
  if(you.issues&&you.issues.length>0){ins.push('<strong>Top issue: '+you.issues[0].title+'</strong>. Fixing this could increase your score.');}
  ins.push('<strong>Need a deeper dive?</strong> Book a Trust Review for a full in-depth competitor audit.');
  ins.forEach(function(t){var dv=document.createElement('div');dv.className='flex items-start gap-3 p-4 rounded-xl border border-zinc-200 bg-white';dv.innerHTML='<div class="text-sm text-zinc-700 leading-relaxed">'+t+'</div>';il.appendChild(dv);});
  setTimeout(function(){$('resultsSection').scrollIntoView({behavior:'smooth',block:'start'});},300);
