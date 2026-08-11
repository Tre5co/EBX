const { JSDOM, VirtualConsole } = require('jsdom');
const BASE='http://127.0.0.1:8000';
(async()=>{
  const errs=[];const vc=new VirtualConsole();
  vc.on('jsdomError',e=>errs.push(String(e.message||e).slice(0,240)));
  vc.on('error',(...a)=>errs.push('console.error: '+a.join(' ').slice(0,200)));
  const dom=await JSDOM.fromURL(BASE+'/cause.html?id=atmosphere',{runScripts:'dangerously',resources:'usable',
    pretendToBeVisual:true,virtualConsole:vc,
    beforeParse(w){w.fetch=(u,o)=>fetch(String(u).startsWith('http')?u:BASE+u,o);
      w.matchMedia=w.matchMedia||(()=>({matches:false,addListener(){},removeListener(){}}));}});
  await new Promise(r=>setTimeout(r,5500));
  const d=dom.window.document, W=dom.window;
  let bad=0;
  const openCount=()=>d.querySelectorAll('.ct-sec--open').length;
  const openIds=()=>[...d.querySelectorAll('.ct-sec--open')].map(e=>e.id).join(',');
  const railBtns=d.querySelectorAll('#ct-rail .ct-node');
  console.log('rail lines:', railBtns.length, railBtns.length===4?'ok':'EXPECTED 4');
  if(railBtns.length!==4) bad++;
  const dates=[...d.querySelectorAll('#ct-rail .ct-node__date')].map(e=>e.textContent.trim());
  console.log('rail dates:', dates.join(' | '));
  if(dates.some(x=>!x||x==='not scheduled')) { console.log('  ! a rail line has no date'); bad++; }
  console.log('open on load:', openCount(), '('+openIds()+')');
  if(openCount()!==1){console.log('  ! expected exactly one open');bad++;}
  for(const n of [4,1,3,2]){
    W.ctOpenSection(n);
    await new Promise(r=>setTimeout(r,600));
    const c=openCount(), ids=openIds();
    const ok = c===1 && ids==='ct-sec-'+n;
    console.log('click '+n+' -> open='+c+' ('+ids+')', ok?'ok':'FAIL');
    if(!ok) bad++;
    const body=d.getElementById('ct-secbody-'+n);
    const filled = body && body.innerHTML.trim().length>40;
    console.log('   body '+n+' rendered:', filled?'ok':'EMPTY');
    if(!filled) bad++;
  }
  // the other three bodies must be empty (only the open one is built)
  const built=[1,2,3,4].filter(n=>{const b=d.getElementById('ct-secbody-'+n);return b&&b.innerHTML.trim().length>40;});
  console.log('bodies built:', built.join(',')||'none', built.length===1?'ok':'EXPECTED 1');
  if(built.length!==1) bad++;
  // no leftovers from the deleted systems
  for(const s of ['#phase-recap-1','#p1-dual-panels','#phase-disc-1','.ct-states']){
    const n=d.querySelectorAll(s).length;
    console.log('removed '+s+':', n===0?'ok':'STILL PRESENT x'+n);
    if(n) bad++;
  }
  const real=errs.filter(e=>!/Not implemented|getContext|SVGElement|fonts.googleapis/i.test(e));
  console.log('script errors:', real.length?('\n  ! '+real.slice(0,5).join('\n  ! ')):'none');
  bad+=real.length;
  console.log(bad?('\nACCORDION PROBLEMS: '+bad):'\nACCORDION CLEAN');
  dom.window.close();process.exit(bad?1:0);
})();
