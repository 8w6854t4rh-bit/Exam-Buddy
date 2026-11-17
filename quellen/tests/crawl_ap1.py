import json,re,sys
from playwright.sync_api import sync_playwright
U="file:///home/claude/out/index.html"
COLLECT=r"""(()=>{const out=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;
 while(n=w.nextNode()){const v=n.nodeValue.trim();if(v&&/[A-Za-zÄÖÜäöüß]/.test(v)&&!n.parentElement.closest('script,style'))out.push(v)}
 document.querySelectorAll('[aria-label],[placeholder],[title]').forEach(e=>['aria-label','placeholder','title'].forEach(a=>{const v=e.getAttribute(a);if(v&&/[A-Za-zÄÖÜäöüß]/.test(v))out.push(v.trim())}));
 out.push(document.title);return out})()"""
seen={}
def grab(pg,tag):
    for t in pg.evaluate(COLLECT):
        seen.setdefault(t,tag)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    pg=b.new_page(viewport={"width":390,"height":844}); pg.add_init_script("if(!sessionStorage.x){sessionStorage.x=1;localStorage.setItem('eb-track','ap1')}"); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.on("dialog",lambda d:(seen.setdefault(d.message.strip(),'dialog'),d.dismiss()))
    pg.goto(U); pg.wait_for_timeout(800); grab(pg,'welcome')
    pg.evaluate("tutGo(0)"); pg.wait_for_timeout(200); grab(pg,'tour'); pg.evaluate("tutClose()")
    G=lambda h:(pg.evaluate(f"go('{h}')"),pg.wait_for_timeout(120))
    for h in ["start","karten","quiz","rechnen","buchen","wissen","lernfelder","bilder","pruefung","einstellungen","plan"]:
        G(h); grab(pg,h)
    # settings variants
    pg.evaluate("setExam('2026-11-24','2026-11-25');go('einstellungen')"); pg.wait_for_timeout(100); grab(pg,'set')
    # wizard all steps
    pg.evaluate("S.plan=null;W=null;go('plan')"); pg.wait_for_timeout(100); grab(pg,'wiz0')
    pg.evaluate("W.step=1;vWizard()"); grab(pg,'wiz1')
    pg.evaluate("LFK.forEach(k=>W.a.r[k]=2);vWizard()"); grab(pg,'wiz1b')
    pg.evaluate("W.step=2;vWizard()"); grab(pg,'wiz2'); pg.evaluate("W.a.lt=['b','p','k','q'];vWizard()"); grab(pg,'wiz2b')
    pg.evaluate("W.step=3;vWizard()"); grab(pg,'wiz3')
    pg.click("button:has-text('Check starten')")
    for i in range(9):
        pg.locator("button.opt").first.click(); grab(pg,'chk'); pg.locator(".sheet .row button.primary").click()
    grab(pg,'chkres')
    for lt in [['b','b','b','p'],['p','p','p','k'],['k','k','k','q'],['q','q','q','b'],['b','p','b','p']]:
        pg.evaluate(f"W.a.lt={json.dumps(lt)};W.step=4;vWizard()"); grab(pg,'wiz4')
    pg.evaluate("W.a.days=[];W.step=4;vWizard()"); grab(pg,'wiz4none'); pg.evaluate("W.a.days=[1,2,3,4,5];vWizard()")
    pg.click("button:has-text('Lernplan starten')"); pg.wait_for_timeout(150); grab(pg,'plan')
    # many plan configurations to collect task texts
    tasks=set()
    for mins in [15,30,45,60,90]:
        for lt in [['b','b','b','b'],['p','p','p','p'],['k','k','k','k'],['q','q','q','q']]:
            for ex in ['2026-11-24','2027-01-20','2027-05-01']:
                t=pg.evaluate(f"(()=>{{const a=Object.assign({{}},S.plan.ans,{{min:{mins},lt:{json.dumps(lt)},exam:'{ex}',days:[0,1,2,3,4,5,6]}});return buildSessions(a,today(),{{}}).flatMap(s=>s.tasks.map(t=>t.t))}})()")
                tasks.update(t)
    for t in tasks: seen.setdefault(t,'task')
    # plan page states
    pg.evaluate("S.plan.sessions[0].tasks[0].done=true;S.plan.sessions[1].d='2026-11-01';S.plan.sessions[2].d='2026-11-02';S.plan.sessions.sort((a,b)=>a.d<b.d?-1:1);save();go('plan')"); grab(pg,'plan2')
    pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); grab(pg,'plan3')
    G('start'); grab(pg,'start2'); pg.evaluate("S.planOpen=true;vStart()"); grab(pg,'start3')
    for si,ti in [(0,0),(0,1),(0,2)]:
        pg.evaluate(f"goTask({si},{ti})"); pg.wait_for_timeout(120); grab(pg,'pbar')
        pg.evaluate("curTask().done=true;pbar(CURV)"); grab(pg,'pbar2')
    pg.evaluate("PT=null")
    # karten
    G('karten'); pg.evaluate("S.kType=true;cur={c:D.karten[37],i:37};shown=false;vKarten()"); grab(pg,'kt')
    pg.fill("#kans","Gewinn Umsatz"); pg.click("button.primary:has-text('Abgleichen')"); grab(pg,'kres')
    for v in ["Gewinn Eigenkapital Gesamtkapital Umsatz FK-Zinsen GK-Rent EK-Rent 100","x"]:
        pg.evaluate("shown=false;vKarten()"); pg.fill("#kans",v); pg.click("button.primary:has-text('Abgleichen')"); grab(pg,'kres')
    pg.evaluate("S.kType=false;shown=false;vKarten()"); pg.locator(".card").click(); grab(pg,'kshow')
    for a in ['KUP','WiSo','FF','T1']:
        pg.evaluate(f"F.area='{a}';cur=null;vKarten()"); grab(pg,'karea')
    # quiz
    G('quiz'); pg.evaluate("F.area='Alle';Q=null;startQuiz();vQuiz()")
    for i in range(10):
        pg.locator("button.opt").first.click(); grab(pg,'quiz'); pg.locator("main button.primary").last.click()
    grab(pg,'quizend')
    # rechnen all generators
    G('rechnen'); n=pg.evaluate("G.length")
    for i in range(n):
        for rep in range(3):
            pg.evaluate(f"F.area='Alle';F.topic=G[{i}][1];C=null;vRechnen()"); grab(pg,'calc')
            pg.click("button:has-text('Lösung zeigen')"); grab(pg,'calcsol')
        pg.evaluate(f"C=null;vRechnen()"); pg.fill("#ans","1"); pg.click("main button.primary:has-text('Prüfen')"); grab(pg,'calcno')
    # calc pad
    pg.evaluate("C=null;vRechnen()")
    for k in ["1","+","2","="]: pg.locator(f".cpad button[aria-label='{k}']").click()
    grab(pg,'pad'); pg.locator(".chead").click(); grab(pg,'padclosed'); pg.locator(".chead").click()
    for a in ['KUP','WiSo','FF','T1']:
        pg.evaluate(f"F.area='{a}';F.topic='Alle';C=null;vRechnen()"); grab(pg,'rarea')
    # buchen
    G('buchen'); nb=pg.evaluate("D.buchungen.length")
    for i in range(nb):
        pg.evaluate(f"B=null;newBuch();B.b=D.buchungen[{i}];vBuchen()") if pg.evaluate("typeof newBuch")=='function' else None
        grab(pg,'buch'); 
        if pg.locator("button:has-text('Lösung zeigen')").count(): pg.click("button:has-text('Lösung zeigen')"); grab(pg,'buchsol')
    pg.evaluate("newBuch();vBuchen()"); pg.locator("button.primary:has-text('Prüfen')").click(); grab(pg,'buchno')
    # wissen
    G('wissen'); pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); grab(pg,'wissen')
    for a in ['KUP','WiSo','FF','Alle']:
        pg.evaluate(f"F.area='{a}';vWissen();document.querySelectorAll('details').forEach(d=>d.open=true)"); grab(pg,'wissen')
    G('lernfelder'); pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); grab(pg,'lf')
    G('bilder'); grab(pg,'bilder')
    for i in range(pg.evaluate("STORIES.length")):
        pg.evaluate(f"BST={i};vWissen()"); grab(pg,'story')
    pg.evaluate("BST=null")
    # exams
    for k in ['T1','t1k']:
        pg.evaluate(f"E=null;go('pruefung');startExam('{k}');vExam()"); n=pg.evaluate("E.items.length")
        for i in range(n):
            pg.evaluate(f"E.i={i};vExam()"); grab(pg,'exam')
        pg.evaluate("finishExam();vExam()"); grab(pg,'examres')
        pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); grab(pg,'examres2')
        # rate open
        btn=pg.locator("main button:has-text('voll')")
        if btn.count(): btn.first.click(); grab(pg,'examrate')
    pg.evaluate("E=null;go('pruefung')"); grab(pg,'examhist')
    # timeout state
    pg.evaluate("startExam('t1k');E.end=Date.now()-1000;vExam()"); pg.wait_for_timeout(1200); grab(pg,'examtime')
    pg.evaluate("E=null;go('start')"); grab(pg,'start4')
    # home with exam running, endspurt
    pg.evaluate("startExam('T1');go('start')"); grab(pg,'startrun'); pg.evaluate("E=null;setExam('2026-11-19','');go('start')"); grab(pg,'startend')
    pg.evaluate("S.plan=null;go('start')"); grab(pg,'startnoplan')
    pg.evaluate("setExam('','');go('start')"); grab(pg,'startnoexam')
    # delete plan dialog
    pg.evaluate("const a={exam:'',days:[1,2,3],min:30,r:{LF3:3,LF4:2,LF5:1,WS:3},lt:['p','b','p','k'],sty:[],goal:'gut',chk:null};S.plan={ans:a,created:today(),sessions:buildSessions(a,today(),{})};go('plan')")
    pg.locator("button.danger").click(); pg.wait_for_timeout(100)
    print("errors",errs[:5])
    b.close()
json.dump(seen,open('/home/claude/i18n/seen_ap1.json','w'),ensure_ascii=False,indent=0)
print(len(seen))
