/* Neurasoft: progressive enhancement. No production resident, tracking, or AI connection. */
(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  const menu = $('.menu-toggle'), nav = $('#primary-nav');
  function menuState(open) {
    if (!menu || !nav) return;
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    menu.textContent = open ? '×' : '☰';
    nav.classList.toggle('open', open);
  }
  menu?.addEventListener('click', () => menuState(menu.getAttribute('aria-expanded') !== 'true'));
  nav?.addEventListener('click', e => { if (e.target.closest('a')) menuState(false); });
  document.addEventListener('click', e => { if (!e.target.closest('.header')) menuState(false); });
  window.matchMedia('(min-width: 821px)').addEventListener('change', e => { if (e.matches) menuState(false); });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && menu?.getAttribute('aria-expanded') === 'true') { menuState(false); menu.focus(); }
  });

  // Particle sculpture. An original geometric illustration; never presented as telemetry.
  let artPaused = reduce.matches;
  const artEngines = [];
  // The edition 3 illustration is a semantic SVG, not a particle renderer.
  // CSS advances a single path accent. Hidden, offscreen and reduced-motion views stop it.
  $$('[data-continuum]').forEach(figure => {
    let visible = false;
    const engine = {
      pause: () => figure.classList.remove('is-moving'),
      resume: () => figure.classList.toggle('is-moving', visible && !artPaused && !document.hidden)
    };
    artEngines.push(engine);
    new IntersectionObserver(entries => {
      visible = entries[0].isIntersecting;
      engine.resume();
    }).observe(figure);
  });
  $$('[data-field]').forEach(canvas => {
    const ctx = canvas.getContext('2d', { alpha: true });
    if (!ctx) return;
    const dark = false; // Edition 2 uses one paper-colored environment.
    const banner = canvas.dataset.field === 'banner';
    const engine = { raf: 0, visible: true, frame: 0, time: 0 };
    let w = 0, h = 0, dpr = 1;
    let points = [];
    const n = window.innerWidth < 640 ? 4700 : 9600;
    for (let i = 0; i < n; i++) {
      const u = i / n * Math.PI * 2;
      const v = i * 2.399963229728653;
      const tube = .355 + .058 * Math.sin(u * 3 + .7);
      const radius = .97 + .04 * Math.sin(u * 5);
      points.push([(radius + tube * Math.cos(v)) * Math.cos(u), tube * Math.sin(v), (radius + tube * Math.cos(v)) * Math.sin(u), i / n]);
    }
    const fit = () => {
      const box = canvas.getBoundingClientRect();
      w = box.width; h = box.height;
      if (!w || !h) return;
      dpr = Math.min(window.devicePixelRatio || 1, 1.6);
      canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      draw(engine.time);
    };
    function draw(time) {
      if (!w || !h) return;
      ctx.clearRect(0, 0, w, h);
      const scale = Math.min(w * .32, h * (banner ? .34 : .34));
      const cx = w * .52, cy = h * .49;
      const phase = time * .00008;
      const ax = 1.00 + Math.sin(phase * .65) * .08;
      const ay = .1 + phase * .23;
      const az = -.5 + Math.sin(phase * .4) * .08;
      const sx = Math.sin(ax), coX = Math.cos(ax), sy = Math.sin(ay), coY = Math.cos(ay), sz = Math.sin(az), coZ = Math.cos(az);
      const projected = [];
      for (let i = 0; i < points.length; i++) {
        const p = points[i];
        const breathe = 1 + .012 * Math.sin(phase * 3 + p[3] * Math.PI * 2);
        let x = p[0] * breathe, y = p[1], z = p[2] * breathe;
        let yy = y * coX - z * sx, zz = y * sx + z * coX;
        let xx = x * coY + zz * sy; z = -x * sy + zz * coY;
        x = xx * coZ - yy * sz; y = xx * sz + yy * coZ;
        const perspective = 3.7 / (3.7 - z);
        projected.push([cx + x * scale * perspective, cy + y * scale * perspective, z, i]);
      }
      projected.sort((a, b) => a[2] - b[2]);
      // A very faint reference field, drawn without pseudo measurements.
      ctx.strokeStyle = dark ? 'rgba(204,227,178,.09)' : 'rgba(60,91,63,.07)';
      ctx.lineWidth = .7;
      ctx.beginPath();ctx.moveTo(w*.08,cy);ctx.lineTo(w*.93,cy);ctx.moveTo(cx,h*.06);ctx.lineTo(cx,h*.91);ctx.stroke();
      ctx.beginPath();ctx.ellipse(cx,cy,scale*1.44,scale*1.44,0,0,Math.PI*2);ctx.setLineDash([1,7]);ctx.stroke();ctx.setLineDash([]);
      for (const [x,y,z,i] of projected) {
        const depth = (z + 1.5) / 3;
        const a = .13 + depth * .74;
        if (dark) ctx.fillStyle = i % 11 === 0 ? `rgba(226,234,158,${a})` : `rgba(142,199,163,${a * .9})`;
        else ctx.fillStyle = i % 19 === 0 ? `rgba(153,142,76,${a*.9})` : `rgba(42,90,66,${a})`;
        const r = .50 + depth * .7;
        ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();
      }
      canvas.parentElement.classList.add('canvas-ready');
    }
    function tick(now) {
      engine.raf = 0;
      if (artPaused || !engine.visible || document.hidden) return;
      if (now - engine.frame > 48) { engine.time += Math.min(now - engine.frame, 70); engine.frame = now; draw(engine.time); }
      engine.raf = requestAnimationFrame(tick);
    }
    engine.resume = () => { if (!engine.raf && !artPaused && engine.visible && !document.hidden) { engine.frame = performance.now(); engine.raf = requestAnimationFrame(tick); } };
    engine.pause = () => { cancelAnimationFrame(engine.raf); engine.raf = 0; };
    artEngines.push(engine);
    new ResizeObserver(fit).observe(canvas);
    new IntersectionObserver(entries => { engine.visible = entries[0].isIntersecting; engine.visible ? engine.resume() : engine.pause(); }).observe(canvas);
    fit();engine.resume();
  });
  function syncArt() {
    $$('[data-pause-art]').forEach(b => { b.setAttribute('aria-pressed',String(artPaused)); b.textContent = artPaused ? 'Play visual' : 'Pause visual'; });
    artEngines.forEach(e => artPaused ? e.pause() : e.resume());
  }
  $$('[data-pause-art]').forEach(b => b.addEventListener('click', () => { artPaused = !artPaused; syncArt(); }));
  reduce.addEventListener('change', () => { artPaused = reduce.matches; syncArt(); });
  document.addEventListener('visibilitychange', () => artEngines.forEach(e => document.hidden ? e.pause() : e.resume()));
  syncArt();

  // Locally searched, public-only site index. Render with textContent, never raw query HTML.
  const dialog = $('.search-dialog'), input = $('#site-search'), results = $('.search-results');
  let index = null, loadFailed = false;
  function search() {
    const query = input.value.trim().toLowerCase();results.replaceChildren();
    if (loadFailed) { const p=document.createElement('p');p.className='search-empty';p.textContent='Search could not load. Browse Research or Journal using the main navigation.';results.append(p);return; }
    if (!index) { const p=document.createElement('p');p.className='search-empty';p.textContent='Loading the public index…';results.append(p);return; }
    const found=window.NeurasoftSearch.searchPages(index,query);
    if(!found.length){const p=document.createElement('p');p.className='search-empty';p.textContent='No matching pages. Try memory, evidence, or Luna.';results.append(p);return;}
    found.forEach(row=>{const a=document.createElement('a');a.href=row.url;a.className='search-result';const k=document.createElement('span');k.className='micro';k.textContent=row.type;const h=document.createElement('h3');h.textContent=row.title;a.append(k,h);results.append(a);});
  }
  async function openSearch(){
    menuState(false);
    if(typeof dialog.showModal!=='function'){window.location.assign('/journal/');return;}
    if(!dialog.open)dialog.showModal();input.focus();search();
    if(!index&&!loadFailed){try{const res=await fetch('/assets/search-index.json',{credentials:'same-origin'});if(!res.ok)throw new Error('Index unavailable');index=await res.json();}catch{loadFailed=true;}search();}
  }
  $$('[data-search-open]').forEach(b=>b.addEventListener('click',openSearch));
  $('.search-close')?.addEventListener('click',()=>dialog.close());
  dialog?.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
  input?.addEventListener('input',search);
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&dialog?.open){e.preventDefault();dialog.close();return;}const editing=/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)||e.target.isContentEditable;if((e.key==='/'&&!editing)||((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k')){e.preventDefault();openSearch();}});

  // Journal filters leave all content visible with JavaScript disabled.
  $$('[data-filter]').forEach(btn=>btn.addEventListener('click',()=>{
    const selected=btn.dataset.filter;$$('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===btn)));
    let count=0;$$('.journal-index [data-category]').forEach(card=>{card.hidden=selected!=='All'&&card.dataset.category!==selected;if(!card.hidden)count++;});
    $('.journal-count').textContent=`${count} ${count===1?'note':'notes'} · ${selected==='All'?'Inaugural public edition':selected}`;
  }));
  if(document.body.dataset.article){const bar=$('.read-progress');const update=()=>{const max=document.documentElement.scrollHeight-window.innerHeight;bar.style.width=`${max?Math.min(100,window.scrollY/max*100):0}%`;};window.addEventListener('scroll',update,{passive:true});update();}
  $('#copy-email')?.addEventListener('click',async e=>{const address=e.currentTarget.dataset.email;const status=$('#copy-status');try{await navigator.clipboard.writeText(address);status.textContent='Email address copied. No message has been sent.';}catch{status.textContent=`Copy this address: ${address}. Clipboard access is unavailable in this browser.`;}});

  // Transparent teaching model, intentionally not the private research implementation.
  const chart=$('#trajectory');
  if(chart){
    const ctx=chart.getContext('2d');const retention=$('#memory-retention'), value=$('#retention-value'), status=$('#exhibit-status');
    let intervention=false,last=null,current=null,animation=0,progress=0;
    const seed=42,steps=96;
    function rng(seed){let state=seed>>>0;return()=>{state^=state<<13;state^=state>>>17;state^=state<<5;return(state>>>0)/4294967296;};}
    function simulate(r,changed){
      const random=rng(seed),rows=[];let m=0;
      for(let t=0;t<steps;t++){const original=.42*Math.sin(t/8)+.16*Math.sin(t/3.1)+(random()-.5)*.12;const pulse=changed&&t>=32&&t<40?.65:0;const input=original+pulse;m=r*m+(1-r)*input;rows.push({step:t,input,memory:m,response:Math.tanh(1.9*m+.55*input)});}
      return rows;
    }
    function record(){const r=Number(retention.value)/100;return{schema:'neurasoft-illustration/v1',illustrative_only:true,connected_to_live_system:false,seed,steps,retention:r,intervention:intervention?{start:32,end_exclusive:40,input_delta:.65}:null,baseline:simulate(r,false),counterfactual:intervention?simulate(r,true):null};}
    function stale(){current=null;cancelAnimationFrame(animation);status.textContent='Controls changed. Run the model to create a record for these conditions.';draw(null,0);}
    retention.addEventListener('input',()=>{value.textContent=(Number(retention.value)/100).toFixed(2);stale();});
    function draw(data,fraction=1){
      const box=chart.getBoundingClientRect(),w=box.width,h=box.height,dpr=Math.min(devicePixelRatio||1,2);
      if(chart.width!==Math.round(w*dpr)||chart.height!==Math.round(h*dpr)){chart.width=Math.round(w*dpr);chart.height=Math.round(h*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);}
      ctx.clearRect(0,0,w,h);const left=36,right=16,top=18,bottom=27;
      const X=t=>left+t/(steps-1)*(w-left-right),Y=y=>top+(1-y)/2*(h-top-bottom);
      ctx.lineWidth=.6;ctx.strokeStyle='#476054';ctx.fillStyle='#aebfb0';ctx.font='10px monospace';
      [-1,-.5,0,.5,1].forEach(y=>{ctx.beginPath();ctx.moveTo(left,Y(y));ctx.lineTo(w-right,Y(y));ctx.stroke();ctx.fillText(y.toFixed(1),0,Y(y)+3);});
      [0,16,32,48,64,80,95].forEach(t=>ctx.fillText(String(t),X(t)-6,h-5));
      if(data?.intervention){ctx.fillStyle='rgba(136,202,173,.09)';ctx.fillRect(X(32),top,X(40)-X(32),h-top-bottom);ctx.fillStyle='#aabfb0';ctx.fillText('INPUT PULSE',X(32)+5,top+12);}
      if(!data)return;
      const count=Math.max(1,Math.floor(steps*fraction));
      function line(rows,color){if(!rows)return;ctx.strokeStyle=color;ctx.lineWidth=2;ctx.beginPath();rows.slice(0,count).forEach((r,i)=>i?ctx.lineTo(X(i),Y(r.response)):ctx.moveTo(X(i),Y(r.response)));ctx.stroke();}
      line(data.baseline,'#d8ed7f');line(data.counterfactual,'#77cdbb');
    }
    function outcome(data,prefix='Run complete.'){
      if(data.counterfactual){const diffs=data.baseline.map((r,i)=>Math.abs(r.response-data.counterfactual[i].response));const max=Math.max(...diffs);const tail=diffs[48];return`${prefix} ${steps} steps. Largest response difference: ${max.toFixed(4)}. Difference at step 48, after the pulse: ${tail.toFixed(4)}. Illustrative units only.`;}
      return`${prefix} ${steps} deterministic steps recorded. Add an intervention to compare a different input history. Illustrative model only.`;
    }
    function show(data,text){current=data;cancelAnimationFrame(animation);if(reduce.matches){progress=1;draw(data,1);status.textContent=text;return;}const start=performance.now();status.textContent='Drawing the locally computed trajectory…';function frame(now){progress=Math.min(1,(now-start)/1000);draw(data,progress);if(progress<1)animation=requestAnimationFrame(frame);else status.textContent=text;}animation=requestAnimationFrame(frame);}
    $('#run-exhibit').addEventListener('click',()=>{const next=record();last=next;show(next,outcome(next));});
    $('#replay-exhibit').addEventListener('click',()=>{const next=record();if(!last){last=next;show(next,outcome(next,'First record created. Replay again to compare.'));return;}if(next.retention!==last.retention||JSON.stringify(next.intervention)!==JSON.stringify(last.intervention)){last=next;show(next,outcome(next,'Conditions changed; a new baseline record was created.'));return;}const equal=JSON.stringify(next)===JSON.stringify(last);show(next,outcome(next,equal?'Exact replay: all recorded values match.':'Replay mismatch: the records differ.'));});
    $('#perturb-exhibit').addEventListener('click',e=>{intervention=!intervention;e.currentTarget.setAttribute('aria-pressed',String(intervention));e.currentTarget.textContent=intervention?'Remove intervention':'Add an intervention';stale();const next=record();last=next;show(next,outcome(next));});
    $('#reset-exhibit').addEventListener('click',()=>{intervention=false;retention.value='80';value.textContent='0.80';const b=$('#perturb-exhibit');b.setAttribute('aria-pressed','false');b.textContent='Add an intervention';last=null;current=null;cancelAnimationFrame(animation);draw(null,0);status.textContent='Reset. No record is selected. Run the model to begin again.';});
    $('#export-exhibit').addEventListener('click',()=>{if(!current){status.textContent='Run the model first. A changed control must be rerun before its record can be exported.';return;}const blob=new Blob([JSON.stringify(current,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='neurasoft-illustrative-record.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent='A local export was requested. The JSON is labeled illustrative and contains no resident or laboratory data.';});
    new ResizeObserver(()=>draw(current,progress||1)).observe(chart);draw(null,0);
  }
})();

/* Public teaching model only. State remains in this page's memory. */
(() => {
  const root = document.getElementById('choice-exhibit');
  if (!root) return;
  const q = s => root.querySelector(s);
  let recovered = false, grant = 0, count = 0, decision = null;
  function record(text) {
    const row = document.createElement('li'); row.textContent = text;
    q('#choice-log').append(row); row.scrollIntoView({block:'nearest'});
    q('#choice-status').textContent = text;
    q('#choice-project').textContent = recovered ? 'Recovered' : 'Not recovered';
    q('#choice-grant').textContent = grant ? 'One unused action' : 'None';
    q('#choice-count').textContent = String(count);
  }
  q('#choice-recover').onclick = () => { recovered = true; record('Project recovered. No action occurred.'); };
  q('#choice-authorize').onclick = () => {
    if (!recovered) return record('Recover the project before adding a grant. No action occurred.');
    if (grant) return record('The existing one-action grant is still available. It was not multiplied.');
    grant = 1; record('One local observation authorized. Still no action occurred.');
  };
  q('#choice-defer').onclick = () => { decision = 'defer'; record('Deferred. Project history and any unused grant remain; no action occurred.'); };
  q('#choice-act').onclick = () => {
    if (!recovered) return record('Cannot act: the project has not been recovered.');
    if (!grant) return record('Cannot act: no unused authorization remains.');
    decision = 'act'; grant = 0; count += 1;
    record('The simulated observation completed. The one-action grant is now spent.');
  };
  q('#choice-restart').onclick = () => { decision = null; record('Restart simulated. History and remaining grant preserved; no action replayed.'); };
  q('#choice-reset').onclick = () => {
    recovered = false; grant = 0; count = 0; decision = null;
    q('#choice-log').replaceChildren(); record('New study. Recover the project to begin.');
  };
})();
