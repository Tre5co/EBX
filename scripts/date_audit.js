// Prints the five dates for every mission straight from EBX.Cycle.missionDates
// (loaded in a real page context), so the model can be read in one table.
const { JSDOM, VirtualConsole } = require('jsdom');
const BASE='http://127.0.0.1:8000';
(async()=>{
  const vc=new VirtualConsole();
  const dom=await JSDOM.fromURL(BASE+'/cause.html?id=atmosphere',{runScripts:'dangerously',resources:'usable',
    pretendToBeVisual:true,virtualConsole:vc,
    beforeParse(w){w.fetch=(u,o)=>fetch(String(u).startsWith('http')?u:BASE+u,o);
      w.matchMedia=w.matchMedia||(()=>({matches:false,addListener(){},removeListener(){}}));}});
  await new Promise(r=>setTimeout(r,5500));
  const W=dom.window, EBX=W.EBX;
  const f=d=>d.toLocaleDateString('en-US',{month:'short',day:'2-digit'});
  const causes=EBX.config.causes.slice().sort((a,b)=>a.index-b.index);
  const byIdx={}; causes.forEach(c=>byIdx[c.id]=c.index);
  const ms=EBX.config.missions.slice().sort((a,b)=>(byIdx[a.cause_id]-byIdx[b.cause_id])||((a.cycle_num||0)-(b.cycle_num||0)));
  const GEN=EBX.config.cycleStart.getTime(), WK=7*86400000;
  // Is d on the same point of this cause's 7-week cycle as its window opening?
  // T = started_at + 7wk, and started_at is a cause-week START, so T is too.
  const bnd=(idx,d)=>{
    const diff=(d.getTime()-(GEN+idx*WK));
    return diff>=0 && diff % (7*WK) === 0;
  };
  console.log('mission  started_at   causeFinalized(window)     causeOpened   T=missionStarted   phlElected   creditRelease');
  for(const m of ms){
    const d=EBX.Cycle.missionDates(m); const idx=byIdx[m.cause_id];
    console.log(
      m.id.padEnd(8)+f(d.startedAt).padEnd(13)+
      (f(d.causeFinalizedFrom)+' – '+f(d.causeFinalizedTo)).padEnd(27)+
      f(d.causeOpened).padEnd(14)+
      (f(d.missionStarted)+(bnd(idx,d.missionStarted)?' ✓':' ✗')).padEnd(19)+
      (f(d.phlElected)+(bnd(idx,d.phlElected)?' ✓':' ✗')).padEnd(13)+
      f(d.creditRelease));
  }
  console.log('\n✓/✗ = sits on this cause\'s own 7-week cycle point.');
  console.log('T should be ✓ everywhere; phlElected is EXPECTED ✗ (T+8wk is not a multiple of the 7-week rotation).');
  // invariants
  let bad=0;
  for(const m of ms){
    const d=EBX.Cycle.missionDates(m); const idx=byIdx[m.cause_id];
    if(!bnd(idx,d.missionStarted)){console.log('  ! T off-boundary for '+m.id);bad++;}
    if(d.causeOpened.getTime()!==d.missionStarted.getTime()-7*86400000*7){console.log('  ! causeOpened ≠ T-7wk for '+m.id);bad++;}
    if(d.phlElected.getTime()!==d.missionStarted.getTime()+8*7*86400000){console.log('  ! phl ≠ T+8wk for '+m.id);bad++;}
    if(d.causeFinalizedTo.getTime()!==d.causeOpened.getTime()){console.log('  ! finalized window does not end at causeOpened for '+m.id);bad++;}
  }
  // FIXED POINTS. Jax gave these two philanthropy dates directly (§5). They are
  // the anchor the T=+7 vs +8 confusion was finally settled against, so they are
  // asserted here: if a date change breaks either, the change is wrong.
  const FIXED = { atm0: 'Aug 11', atm1: 'Sep 29' };
  for (const [mid, want] of Object.entries(FIXED)) {
    const m = ms.find(x => x.id === mid);
    if (!m) { console.log('  ! fixed-point mission missing: ' + mid); bad++; continue; }
    const got = f(EBX.Cycle.missionDates(m).phlElected);
    const ok = got === want;
    console.log('fixed point ' + mid + ' phlElected = ' + got + ' (want ' + want + ') ' + (ok ? 'ok' : 'FAIL'));
    if (!ok) bad++;
  }
  console.log(bad?('\nDATE PROBLEMS: '+bad):'\nDATE MODEL CONSISTENT');
  dom.window.close();process.exit(bad?1:0);
})();
