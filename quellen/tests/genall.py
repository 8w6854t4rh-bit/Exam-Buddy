import asyncio,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        for tr in ['ap2','ap1']:
            pg=await b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.goto('file:///home/claude/exam-buddy/index.html'); await pg.wait_for_timeout(300)
            key='ak-trainer-v1' if tr=='ap2' else 'ak-trainer-ap1'
            await pg.evaluate(f"localStorage.setItem('eb-track','{tr}');localStorage.setItem('{key}',JSON.stringify({{tut:1,lang:'en'}}))"); await pg.reload(); await pg.wait_for_timeout(700)
            r=await pg.evaluate("""(()=>{const bad={},de=new Set();for(const g of G){if(!ina(g[0]))continue;for(let i=0;i<300;i++){let x;try{x=g[2]()}catch(e){bad[g[1]]='throw '+e.message;break}
              if(typeof x.a!=='number'||!isFinite(x.a)){bad[g[1]]='a='+x.a;break}if(/undefined|NaN|Infinity/.test(x.t+x.s)){bad[g[1]]='text has undefined/NaN';break}
              for(const l of (x.t+'\\n'+x.s).split('\\n')){const t=trS(l);if(/[äöüß]|\\b(und|der|die|das|ist|mit|für|von)\\b/.test(t)){let j=0;de.add(g[1]+' :: '+l.replace(/\\d+(?:[.,]\\d+)*/g,()=>'{'+(j++)+'}'))}}}}return [bad,[...de].slice(0,40),de.size]})()""")
            print(tr,'bad:',json.dumps(r[0],ensure_ascii=False)); print('untranslated count',r[2]); print('\n'.join(r[1]))
            print('errs',errs); await pg.close()
        await b.close()
asyncio.run(main())
