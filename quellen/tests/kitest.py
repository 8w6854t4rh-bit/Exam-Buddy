import sys, json
from playwright.sync_api import sync_playwright
MOCK = r"""
(()=>{
 const store={};let nid=1;
 const coll=(path,filters=[])=>({path,
   where:(f,op,v)=>coll(path,[...filters,[f,op,v]]),orderBy:()=>coll(path,filters),limit:()=>coll(path,filters),
   get:async()=>{const docs=Object.entries(store).filter(([k])=>k.startsWith(path+'/')&&k.split('/').length===path.split('/').length+1).map(([k,v])=>({id:k.split('/').pop(),exists:true,data:()=>v})).filter(d=>filters.every(([f,op,v])=>d.data()[f]===v));return{docs,size:docs.length,empty:!docs.length}},
   doc:id=>docRef(path+'/'+(id||('d'+nid++))),
   add:async d=>{const r=docRef(path+'/d'+(nid++));store[r.path]=JSON.parse(JSON.stringify(d));return r}});
 const docRef=p=>({path:p,id:p.split('/').pop(),get:async()=>({exists:!!store[p],data:()=>store[p]}),set:async d=>{store[p]=d},update:async d=>{if(!store[p])throw{code:'invalid_argument'};Object.assign(store[p],d)},delete:async()=>{delete store[p]}});
 window.__store=store;window.__calls=[];
 const sample=async(input,opts)=>{window.__calls.push(['text',String(input).slice(0,80)]);const t='Skonto ist ein Preisnachlass für schnelle Zahlung.\n– Rabatt gibt es vorher.';if(opts&&opts.onText)opts.onText({text:t.slice(0,10),delta:''});return{text:t,truncated:false}};
 sample.limits=async()=>({images:true});
 sample.json=async(input,opts)=>{const p=String(input);window.__calls.push(['json',p.slice(0,60),opts&&opts.images?opts.images.length:0]);
   if(p.includes('bewertungen'))return{bewertungen:[...p.matchAll(/Nr\. (\d+)/g)].map((m,i)=>({nr:+m[1],anteil:i%2?0.5:1,begruendung:'Passt inhaltlich, nur anders formuliert.'}))};
   return{ok:true,probleme:[],thema:'Preiskalkulation',lernfeld:'LF 9',zusammenfassung:'Vorwärtskalkulation im Einzelhandel.',
     karten:[{frage:'Was ist der Kalkulationszuschlag?',antwort:'Aufschlag vom Bezugspreis auf den Nettoverkaufspreis in Prozent.'}],
     quiz:[{frage:'Was erhöht den Listenverkaufspreis?',optionen:['Skonto','Rabatt','Gewinnzuschlag','Bezugskosten'],richtig:2,erklaerung:'Der Gewinn wird aufgeschlagen.'}],
     rechnen:[{aufgabe:'Bezugspreis 50 €, Zuschlag 40 %. Nettoverkaufspreis?',ergebnis:70,einheit:'€',rechenweg:'50 × 1,4 = 70'}],zuordnen:[],buchen:[]}};
 const user={isOwner:()=>true,can:()=>true,id:async()=>'u1'};
 window.claude={use:async n=>n==='sample'?sample:n==='db'?{collection:p=>coll(p),doc:p=>docRef(p)}:n==='user'?user:null};
})();
"""
errs=[]
def log(*a): print(*a, flush=True)
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
  def page(f, mock=True, beruf='auto'):
    pg=b.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
    pg.on('pageerror',lambda e:errs.append(f+': '+str(e)))
    if mock: pg.add_init_script(MOCK)
    pg.add_init_script("try{localStorage.setItem('eb-beruf','%s');localStorage.setItem('pv-eb-beruf','%s');localStorage.setItem('pv-ak-trainer-v1',JSON.stringify({tut:1}));localStorage.setItem('pv-pv-ak-trainer-v1',JSON.stringify({tut:1}));localStorage.setItem('ak-trainer-v1',JSON.stringify({tut:1}))}catch(e){}"%(beruf,beruf))
    return pg
  def clean(pg): pg.evaluate("document.getElementById('tut')&&document.getElementById('tut').remove()")
  U='file:///home/claude/out/preview.html'
  pg=page('preview')
  # 1 Frag Claude
  pg.goto(U+'#wissen');pg.wait_for_timeout(700);clean(pg)
  log('ask box', pg.locator('.kibox').count())
  pg.fill('#kiq','Was ist Skonto?');pg.locator('.kibox button.primary').click();pg.wait_for_timeout(400)
  log('ask out', pg.locator('.kiout').inner_text()[:40])
  pg.screenshot(path='/tmp/ki_ask.png')
  # 2 Pruefung mit offenen Fragen
  pg.goto(U+'#pruefung');pg.wait_for_timeout(500);clean(pg)
  pg.evaluate("startExam('KUP');E.items.forEach(it=>{if(it.type==='o')it.val='Meine Antwort in Stichpunkten'});finishExam();vExam()")
  pg.wait_for_timeout(400)
  n_o=pg.evaluate("E.items.filter(x=>x.type==='o').length");before=pg.evaluate("E.score")
  btn=pg.locator('.kibox button.primary');log('open items',n_o,'grade btn',btn.count())
  if btn.count(): btn.click();pg.wait_for_timeout(600)
  log('score before/after',round(before,2),round(pg.evaluate("E.score"),2),'kiwhy',pg.locator('.kiwhy').count(),'unrated',pg.evaluate("E.items.filter(x=>x.type==='o'&&x.self===null).length"))
  pg.screenshot(path='/tmp/ki_exam.png')
  # 3 Upload
  pg.goto(U+'#mitmachen');pg.wait_for_timeout(600);clean(pg)
  log('upload box',pg.locator('#kiup').count(),'mail heading',pg.locator('h2.shd').count())
  import base64
  png=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==')
  open('/tmp/t.png','wb').write(png)
  pg.locator('#kiup .chip',has_text='Rechnen').click()
  pg.set_input_files('#kiFi','/tmp/t.png')
  pg.locator('#kiup button.primary').click();pg.wait_for_timeout(300)
  log('ds sheet',pg.locator('.dsov').count())
  pg.screenshot(path='/tmp/ki_ds.png')
  pg.locator('.dsov button.primary').click();pg.wait_for_timeout(1500)
  log('preview items',pg.locator('#kiup .kiitem').count(),'calls',pg.evaluate("window.__calls.map(c=>c[0]+':'+c[2]).join(',')"))
  pg.screenshot(path='/tmp/ki_up.png',full_page=False)
  pg.locator('#kiup button',has_text='Zur Freigabe einreichen').click();pg.wait_for_timeout(500)
  log('submitted',pg.locator('#kiup .note.ok').count(),'store',list(pg.evaluate("Object.keys(window.__store)")))
  # 4 Start zeigt Freigabe-Karte
  pg.evaluate("location.hash='#start'");pg.wait_for_timeout(600);clean(pg)
  log('wait card',pg.locator('.kiwait').count())
  pg.evaluate("location.hash='#freigabe'");pg.wait_for_timeout(500)
  log('freigabe items',pg.locator('.kisel').count())
  pg.screenshot(path='/tmp/ki_frei.png')
  pg.locator('.kisel input').first.uncheck()
  pg.locator('.kisel input').first.check()
  pg.locator('button',has_text='Auswahl freigeben').click();pg.wait_for_timeout(600)
  log('after approve: inhalte',pg.evaluate("Object.keys(window.__store).filter(k=>k.startsWith('inhalte')).length"),'text',pg.locator('#app').inner_text()[:60].replace('\n',' '))
  pg.evaluate("location.hash='#start'");pg.wait_for_timeout(400)
  log('community card',pg.locator('a.bwopt[href=\"#gemeinsam\"]').count())
  pg.evaluate("location.hash='#gemeinsam'");pg.wait_for_timeout(400)
  log('gemeinsam chips',pg.locator('#app .chip.grow').count(),pg.locator('#app').inner_text()[:120].replace('\n',' | '))
  pg.locator('#app .chip.grow',has_text='Quiz').click();pg.wait_for_timeout(200)
  pg.locator('.opt',has_text='Gewinnzuschlag').click();log('quiz ok',pg.locator('.opt.ok').count())
  pg.locator('#app .chip.grow',has_text='Rechnen').click();pg.wait_for_timeout(200)
  pg.fill('#app input[inputmode=decimal]','70');pg.locator('#app button',has_text='Prüfen').click();log('rechnen ok',pg.locator('.note.ok').count())
  pg.screenshot(path='/tmp/ki_gem.png')
  # Datenschutz-Fenster Layout
  pg.goto(U+'#mitmachen');pg.wait_for_timeout(500);clean(pg)
  pg.locator('#einsend .dslink').click();pg.wait_for_timeout(300)
  log('ds flex dir',pg.evaluate("getComputedStyle(document.querySelector('.dsbody')).flexDirection+'/'+getComputedStyle(document.querySelector('.dsbody')).display"),'KI section','KI-Funktionen der Testversion' in pg.locator('.dsbody').inner_text())
  pg.close()
  # 5 Einzelhandel
  pg=page('preview-vk',beruf='vk');pg.goto(U+'#start');pg.wait_for_timeout(700);clean(pg)
  log('vk start text',pg.locator('#app').inner_text()[:40].replace('\n',' '))
  pg.evaluate("location.hash='#lernfelder'");pg.wait_for_timeout(500);log('vk ask',pg.locator('.kibox').count())
  pg.close()
  # 6 Ohne claude (GitHub-Pages-Fall) in der Vorschau
  pg=page('preview-nomock',mock=False);pg.goto(U+'#wissen');pg.wait_for_timeout(700);log('no claude: ask',pg.locator('.kibox').count())
  pg.goto(U+'#mitmachen');pg.wait_for_timeout(500);log('no claude: upload',pg.locator('#kiup').count(),'mailform',pg.locator('#einsend').count());pg.close()
  # 7 Live
  pg=page('live',mock=True);pg.goto('file:///home/claude/out/index.html#gemeinsam');pg.wait_for_timeout(600)
  log('live gemeinsam ->',pg.evaluate("document.body.dataset.mode"),'kibox',pg.locator('.kibox').count())
  pg.goto('file:///home/claude/out/index.html#wissen');pg.wait_for_timeout(500);log('live wissen kibox',pg.locator('.kibox').count())
  pg.close()
  b.close()
print('errors',errs)
