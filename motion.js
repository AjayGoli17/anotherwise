/* Anotherwise shared motion layer (JS) */
(function(){
'use strict';
var D=document,H=D.documentElement,
RM=matchMedia('(prefers-reduced-motion:reduce)').matches,
FINE=matchMedia('(hover:hover) and (pointer:fine)').matches,
HAS_IO='IntersectionObserver' in window;
var $=function(s,c){return(c||D).querySelector(s)},
lerp=function(a,b,t){return a+(b-a)*t},
clamp=function(v,a,b){return Math.min(b,Math.max(a,v))},
damp=function(rate,k){return 1-Math.pow(rate,k)}; /* frame-rate independent smoothing */
var SS=function(k,v){try{if(v===undefined)return sessionStorage.getItem(k);if(v===null)sessionStorage.removeItem(k);else sessionStorage.setItem(k,v)}catch(e){}};
function mk(c,html){var e=D.createElement('div');e.className=c;if(html)e.innerHTML=html;return e}
function maxY(){return Math.max(1,H.scrollHeight-innerHeight)}

/* progress bar: CSS scroll-timeline when supported, tiny passive handler otherwise */
var bar=mk('mo-bar');D.body.appendChild(bar);
if(!(window.CSS&&CSS.supports&&CSS.supports('animation-timeline','scroll()'))){
  var pf=function(){bar.style.transform='scaleX('+clamp(scrollY/maxY(),0,1)+')'};
  addEventListener('scroll',pf,{passive:true});pf();
}
if(RM){H.classList.remove('mo-pre','mo-arrive');return}

/* word-mask CSS, injected into the page and every shadow root (tokens inherit; fallbacks included) */
var MOCSS='.mo-w{display:inline-block;overflow:hidden;vertical-align:top;padding-bottom:.16em;margin-bottom:-.16em}'
+'.mo-wi{display:inline-block;transform:translateY(112%);transition:transform .9s var(--mo-expo,cubic-bezier(.16,1,.3,1));transition-delay:var(--d,0ms)}'
+'.mo-split.mo-on .mo-wi{transform:none}'
+'.card .vis{transition:transform .8s var(--mo-expo,cubic-bezier(.16,1,.3,1))}.card .vis.mo-live{transition:transform .18s var(--mo-out,cubic-bezier(.22,1,.36,1))}';
var roots=[D];
(function walk(r){r.querySelectorAll('*').forEach(function(e){if(e.shadowRoot){roots.push(e.shadowRoot);walk(e.shadowRoot)}})})(D);
roots.forEach(function(r){var s=D.createElement('style');s.textContent=MOCSS;(r===D?D.head:r).appendChild(s)});
function deep(sel){var o=[];roots.forEach(function(r){r.querySelectorAll(sel).forEach(function(e){o.push(e)})});return o}

/* split headings into masked words: total stagger capped at ~420ms, screen readers get the full heading */
var heads=deep('h1,h2').filter(function(h){return !h.closest('.aw-menu,.cap')&&h.textContent.trim()&&h.id!=='ch'});
heads.forEach(function(h){
  var tw=D.createTreeWalker(h,NodeFilter.SHOW_TEXT),ns=[],total=0,i=0;
  while(tw.nextNode())ns.push(tw.currentNode);
  ns.forEach(function(n){total+=(n.nodeValue.match(/\S+/g)||[]).length});
  var step=total>1?Math.min(55,420/(total-1)):0;
  if(!h.hasAttribute('aria-label'))h.setAttribute('aria-label',h.textContent.replace(/\s+/g,' ').trim());
  ns.forEach(function(n){
    if(!n.nodeValue.trim())return;var f=D.createDocumentFragment();
    n.nodeValue.split(/(\s+)/).forEach(function(p){
      if(!p)return;if(/^\s+$/.test(p)){f.appendChild(D.createTextNode(' '));return}
      var w=D.createElement('span'),x=D.createElement('span');
      w.className='mo-w';w.setAttribute('aria-hidden','true');x.className='mo-wi';
      x.style.setProperty('--d',Math.round(i++*step)+'ms');x.textContent=p;w.appendChild(x);f.appendChild(w)});
    n.parentNode.replaceChild(f,n)});
  h.classList.add('mo-split');
});

/* counters */
var counts=deep('.kp b').filter(function(b){return /\d/.test(b.textContent)});
counts.forEach(function(b){var m=b.textContent.match(/^(\D*)(\d+(?:\.\d+)?)(.*)$/);if(!m)return;b._c={p:m[1],n:+m[2],s:m[3],d:(m[2].split('.')[1]||'').length};b.style.fontVariantNumeric='tabular-nums';b.textContent=b._c.p+(0).toFixed(b._c.d)+b._c.s});
function setCount(b,v){var c=b._c;b.textContent=c.p+v.toFixed(c.d)+c.s}
function runCount(b){var t0=performance.now();(function t(n){var p=clamp((n-t0)/1800,0,1),e=p===1?1:1-Math.pow(2,-10*p);setCount(b,b._c.n*e);if(p<1)requestAnimationFrame(t)})(t0)}

/* image reveal (clip-path once, then removed) + parallax targets */
var revs=deep('.stage2');
revs.forEach(function(e){
  e.classList.add('mo-rev');
  e.addEventListener('transitionend',function(ev){if(ev.propertyName==='clip-path'&&e.classList.contains('mo-on'))e.classList.add('mo-done')});
});
var pars=revs.slice(),vis=new Set(); /* only on-screen parallax targets are measured */

/* nav text roll */
deep('.aw-links a').forEach(function(a){var t=a.textContent.trim();a.innerHTML='<span class="mo-roll"><span>'+t+'</span><span aria-hidden="true">'+t+'</span></span>'});

/* marquee above footer (width cached, only animated while on screen) */
var mqEl=null,mqWrap=null,mqW=0,mqOn=false,ft=$('footer');
function measure(){if(mqEl)mqW=mqEl.scrollWidth/4}
if(ft){var u='Another way <em>&#10022;</em> Built to work <em>&#10022;</em> ';mqWrap=mk('mo-mq');mqWrap.setAttribute('aria-hidden','true');mqEl=D.createElement('div');mqEl.innerHTML=u+u+u+u;mqWrap.appendChild(mqEl);ft.parentNode.insertBefore(mqWrap,ft);measure();
  if(D.fonts&&D.fonts.ready)D.fonts.ready.then(measure);addEventListener('load',measure)}

/* grain */
D.body.appendChild(mk('mo-grain'));

/* start: observers after intro (with safety net) */
var started=false;
function start(){
  if(started)return;started=true;
  var all=heads.concat(revs,counts.filter(function(b){return b._c}));
  if(!HAS_IO){all.forEach(function(t){t.classList.add('mo-on');if(t._c)setCount(t,t._c.n)});return}
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(!e.isIntersecting)return;
    var t=e.target;t.classList.add('mo-on');if(t._c)runCount(t);io.unobserve(t)})},{threshold:.25,rootMargin:'0px 0px -6% 0px'});
  all.forEach(function(e){io.observe(e)});
}
setTimeout(start,7000); /* if the intro ever stalls, headings must not stay hidden */

/* preloader v2: the Y draws in, counts to 100, then flies into the nav logo (first visit only) */
function intro(){
  if(!SS('moSeen')){
    SS('moSeen','1');
    var nl=$('.aw-logo svg'),ps=nl?[].slice.call(nl.querySelectorAll('path')):[],
    VB='viewBox="339 213 338 610" aria-hidden="true"',
    p=mk('mo-pre mo-v2','<div class="mo-y"><svg class="mo-a" '+VB+'><path fill="#fff" d="M339 339h62v58l141 141v286h-61V563L339 422z"/></svg><svg class="mo-b" '+VB+'><path fill="#B8FF00" d="M614 213h63v218L563 542l-42-44 93-93z"/></svg></div><b class="mo-pct">0%</b>'),
    y=$('.mo-y',p),n=$('.mo-pct',p),done=false,
    show=function(){ps.forEach(function(e){e.style.opacity=''})},
    fly=function(){
      if(done)return;done=true;
      var r=nl&&nl.getBoundingClientRect(),b=y.getBoundingClientRect();
      p.classList.add('go');
      if(r&&r.width&&b.width){
        y.style.transform='translate('+(r.left+r.width*339/1024-b.left)+'px,'+(r.top+r.height*213/1024-b.top)+'px) scale('+(r.width*338/1024/b.width)+')';
      }else y.style.opacity='0';
      setTimeout(start,550);
      setTimeout(function(){show();p.remove()},1150);
    };
    ps.forEach(function(e){e.style.opacity='0'});
    D.body.appendChild(p);H.classList.remove('mo-pre');
    var t0=performance.now();
    (function t(x){
      var el=x-t0,q=clamp(el/1700,0,1),e=1-Math.pow(1-q,3),
          cap=D.readyState==='complete'||el>3500?1:D.readyState==='interactive'?.9:.6,
          v=Math.min(e,cap);
      n.textContent=Math.round(v*100)+'%';
      if(v<1)requestAnimationFrame(t);else setTimeout(fly,250);
    })(t0);
    setTimeout(fly,9000); /* safety net */
  }else{
    if(H.classList.contains('mo-arrive')){SS('moNav',null);requestAnimationFrame(function(){requestAnimationFrame(function(){H.classList.remove('mo-arrive');setTimeout(start,250)})})}
    else start();
  }
}
intro();

/* page-transition curtain (shortened) */
var cv=mk('mo-curtain');D.body.appendChild(cv);
addEventListener('pageshow',function(e){if(e.persisted){cv.classList.remove('on');H.classList.remove('mo-arrive')}});

/* clicks: anchors (native smooth scroll) + page transitions */
D.addEventListener('click',function(e){
  var a=e.composedPath().filter(function(x){return x&&x.tagName==='A'})[0];
  if(!a||e.defaultPrevented||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||e.button)return;
  var h=a.getAttribute('href')||'';
  if(h.charAt(0)==='#'){var el=h.length>1?D.getElementById(h.slice(1)):null;
    if(h==='#'||h==='#home'||el){e.preventDefault();scrollTo({top:clamp(h==='#'||h==='#home'?0:el.getBoundingClientRect().top+scrollY-88,0,maxY()),behavior:'smooth'})}return}
  if(a.target||a.hasAttribute('download')||/^(mailto|tel|javascript):/.test(h))return;
  var u;try{u=new URL(a.href,location.href)}catch(x){return}
  if(u.origin!==location.origin||u.pathname===location.pathname)return;
  e.preventDefault();SS('moNav','1');cv.classList.add('on');setTimeout(function(){location.href=a.href},400);
});

/* single idle-aware frame loop: runs only while something is actually moving */
var raf=0,lastT=performance.now(),sy=scrollY,dir=-1,vel=0,mv=0,dirty=true;
var mags=new Map(),curMag=null,magRect=null,tilt=null,tiltRect=null;
function kick(){if(!raf)raf=requestAnimationFrame(frame)}
function frame(now){
  raf=0;var dt=Math.min(64,now-lastT);lastT=now;var k=dt/16.667,go=false,y=scrollY;
  /* parallax: only on scroll/resize, only for visible targets */
  if(dirty){dirty=false;vis.forEach(function(el){var r=el.getBoundingClientRect();el.style.translate='0 '+((r.top+r.height/2-innerHeight/2)*-.07).toFixed(1)+'px'})}
  /* marquee: time-based, cached width, only while on screen */
  var dy=y-sy;sy=y;
  if(mqEl&&mqOn&&mqW){if(dy)dir=dy>0?-1:1;vel=lerp(vel,Math.abs(dy),damp(.9,k));mv+=dir*(.6+vel*.35)*k;if(mv<-mqW)mv+=mqW;if(mv>0)mv-=mqW;mqEl.style.transform='translate3d('+mv.toFixed(1)+'px,0,0)';go=true}
  /* magnetic buttons: eased in the loop, no per-move transitions */
  mags.forEach(function(st,el){
    st.x=lerp(st.x,st.tx,damp(st.tx||st.ty?.82:.9,k));st.y=lerp(st.y,st.ty,damp(st.tx||st.ty?.82:.9,k));
    if(!st.tx&&!st.ty&&Math.abs(st.x)<.05&&Math.abs(st.y)<.05){el.style.translate='';mags.delete(el)}
    else{el.style.translate=st.x.toFixed(1)+'px '+st.y.toFixed(1)+'px';go=true}});
  if(go)kick();
}
if(mqWrap&&HAS_IO)new IntersectionObserver(function(es){mqOn=es[0].isIntersecting;if(mqOn){lastT=performance.now();kick()}},{rootMargin:'100px 0px'}).observe(mqWrap);
if(pars.length&&HAS_IO){var po=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting)vis.add(e.target);else vis.delete(e.target)});dirty=true;kick()},{rootMargin:'200px 0px'});pars.forEach(function(p){po.observe(p)})}
addEventListener('scroll',function(){dirty=true;magRect=null;tiltRect=null;kick()},{passive:true});
addEventListener('resize',function(){measure();dirty=true;magRect=null;tiltRect=null;kick()});

/* magnetic + tilt (delegated, shadow-DOM aware; rects cached, not re-read per move) */
function relTilt(t){if(!t)return;t.classList.remove('mo-live');t.style.transform=''}
if(FINE){
  addEventListener('pointermove',function(e){
    var p=e.composedPath(),m=null,tl=null;
    for(var i=0;i<p.length;i++){var el=p[i];if(!el||!el.matches)continue;
      if(!m&&el.matches('.btn,.aw-cta,.aw-go,.cb'))m=el;
      if(!tl&&el.matches('.card .vis'))tl=el}
    if(m){
      var st=mags.get(m);if(!st){st={x:0,y:0,tx:0,ty:0};mags.set(m,st)}
      if(m!==curMag||!magRect){var r=m.getBoundingClientRect();magRect={cx:r.left-st.x+r.width/2,cy:r.top-st.y+r.height/2};curMag=m}
      st.tx=(e.clientX-magRect.cx)*.28;st.ty=(e.clientY-magRect.cy)*.35;
    }else curMag=null;
    mags.forEach(function(s,el){if(el!==m){s.tx=0;s.ty=0}});
    if(tl){
      if(tl!==tilt){relTilt(tilt);tilt=tl;tiltRect=null}
      if(!tiltRect)tiltRect=tl.getBoundingClientRect();
      var X=(e.clientX-tiltRect.left)/tiltRect.width-.5,Y=(e.clientY-tiltRect.top)/tiltRect.height-.5;
      tl.classList.add('mo-live');tl.style.transform='perspective(900px) rotateY('+X*7+'deg) rotateX('+-Y*7+'deg) scale(1.015)';
    }else if(tilt){relTilt(tilt);tilt=null;tiltRect=null}
    kick();
  },{passive:true});
}
kick();
})();
