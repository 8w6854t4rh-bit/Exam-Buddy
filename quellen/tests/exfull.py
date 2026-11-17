import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        for lang in ['de','en']:
          for tr,ks,key in [('ap2',['KUP','FF','WiSo','mix'],'ak-trainer-v1'),('ap1',['T1','t1k'],'ak-trainer-ap1')]:
            pg=await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.goto('file:///home/claude/exam-buddy/index.html'); await pg.wait_for_timeout(300)
            await pg.evaluate(f"localStorage.setItem('eb-track','{tr}');localStorage.setItem('{key}',JSON.stringify({{tut:1,lang:'{lang}'}}))"); await pg.reload(); await pg.wait_for_timeout(700)
            for k in ks:
                for rep in range(3):
                    await pg.evaluate(f"startExam('{k}');location.hash='#pruefung'"); await pg.wait_for_timeout(150)
                    n=await pg.evaluate("E.items.length")
                    for i in range(n):
                        await pg.evaluate(f"E.i={i};vExam()")
                    await pg.evaluate("E.items.forEach(it=>{if(it.type==='q')it.sel=1;if(it.type==='c')it.val='12,5';if(it.type==='z')it.sel=it.z.rows.map(()=>0);if(it.type==='b'){it.place={}}});finishExam()"); await pg.wait_for_timeout(150)
                    await pg.evaluate("vExam()"); await pg.wait_for_timeout(100)
                    txt=await pg.inner_text('#scr')
                    if 'undefined' in txt or 'NaN' in txt: errs.append(f'{k}: undefined/NaN in result')
            print(lang,tr,'errors',errs[:5]); await pg.close()
        await b.close()
asyncio.run(main())
