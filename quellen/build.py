"""Baut Exam Buddy aus den Quellen in diesem Ordner.

Ergebnis:
  quellen/out/index.html    Live-Fassung (so auch auf claude.ai veröffentlicht)
  quellen/out/preview.html  Vorschau (PV=true, eigener Speicher mit Präfix pv-)
  index.html (Repo-Wurzel)  GitHub-Pages-Fassung als PWA (Manifest, Icons, Service Worker)
Aufruf: python3 quellen/build.py
"""
import os
Q=os.path.dirname(os.path.abspath(__file__)); REPO=os.path.dirname(Q); OUT=os.path.join(Q,'out')
os.makedirs(OUT,exist_ok=True)
rd=lambda n:open(os.path.join(Q,n),encoding='utf-8').read()
old=rd('generatoren.html')
a=old.index("const G=["); b=old.index("let C=null;",a)
G=old[a:b].rstrip()
FIXES=[("v2=ri(10,40)*1000,f=ri(60,200)*1000,a=e-v1-v2-f;","v2=ri(10,40)*1000,f=Math.round((e-v1-v2)*pick([.4,.6,.8])/1000)*1000,a=e-v1-v2-f;"),
       ("ab=ri(1,6),zu=ri(0,3),a=soll-(ist+zu-ab);","ab=ri(1,6),zu=ri(0,Math.min(3,ab-1)),a=soll-(ist+zu-ab);")]
for x,y in FIXES:
    assert x in G,x; G=G.replace(x,y)
s=rd('app.html')
esc=lambda t:t.replace('</','<\\/')
for k in ['/*GEN*/','/*DATA*/','/*DATAEN*/','/*UIEN*/']: assert k in s,k
s=s.replace('/*GEN*/',G).replace('/*DATAEN*/',esc(rd('data_en.json'))).replace('/*UIEN*/',esc(rd('ui_en.json'))).replace('/*DATA*/',esc(rd('data.json')))
open(os.path.join(OUT,'index.html'),'w',encoding='utf-8').write(s); print('live',len(s))
p=s.replace("const PV=false;/*PVFLAG*/","const PV=true;/*PVFLAG*/").replace("'ak-trainer-","'pv-ak-trainer-").replace("'eb-","'pv-eb-").replace("<title>Prüfungstrainer Automobilkaufleute</title>","<title>Exam Buddy (Vorschau)</title>")
assert "const PV=true;" in p
open(os.path.join(OUT,'preview.html'),'w',encoding='utf-8').write(p); print('preview',len(p))
old_head=('<meta name="viewport" content="width=device-width, initial-scale=1">\n'
 '<title>Prüfungstrainer Automobilkaufleute</title>\n'
 '<meta name="apple-mobile-web-app-capable" content="yes">\n'
 '<meta name="apple-mobile-web-app-title" content="Exam Buddy">')
new_head=('<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
 '<title>Exam Buddy</title>\n'
 '<link rel="manifest" href="manifest.webmanifest">\n'
 '<meta name="theme-color" content="#0f1120">\n'
 '<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">\n'
 '<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">\n'
 '<meta name="mobile-web-app-capable" content="yes">\n'
 '<meta name="apple-mobile-web-app-capable" content="yes">\n'
 '<meta name="apple-mobile-web-app-title" content="Exam Buddy">\n'
 '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">')
assert s.count(old_head)==1,'head not found'
w=s.replace(old_head,new_head)
assert w.count('</body>')==1
w=w.replace('</body>',"<script>\nif('serviceWorker' in navigator){addEventListener('load',()=>{navigator.serviceWorker.register('sw.js').catch(()=>{})})}\n</script></body>")
open(os.path.join(REPO,'index.html'),'w',encoding='utf-8').write(w); print('pwa',len(w))
