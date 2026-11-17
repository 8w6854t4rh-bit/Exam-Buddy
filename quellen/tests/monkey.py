import asyncio,random
from playwright.async_api import async_playwright
async def main():
    random.seed(7)
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        for tr,key in [('ap2','ak-trainer-v1'),('ap1','ak-trainer-ap1')]:
          for lang in ['de','en']:
            pg=await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:160]))
            pg.on('dialog',lambda d:asyncio.ensure_future(d.dismiss()))
            await pg.goto('file:///home/claude/exam-buddy/index.html'); await pg.wait_for_timeout(300)
            await pg.evaluate(f"localStorage.setItem('eb-track','{tr}');localStorage.setItem('{key}',JSON.stringify({{tut:1,lang:'{lang}'}}))"); await pg.reload(); await pg.wait_for_timeout(700)
            await pg.evaluate("window.open=()=>null;document.addEventListener('click',e=>{const a=e.target.closest('a');if(a&&/^(mailto|http)/.test(a.getAttribute('href')||''))e.preventDefault()},true);Object.defineProperty(window,'onbeforeunload',{value:null})")
            await pg.evaluate("const _a=Location.prototype;")
            for step in range(350):
                els=await pg.query_selector_all('button:not([disabled]),a[href^="#"],summary,select,input[type=checkbox]')
                vis=[e for e in els if await e.is_visible()]
                if not vis: continue
                e=random.choice(vis)
                try:
                    tag=await e.evaluate('x=>x.tagName')
                    txt=(await e.inner_text())[:30] if tag!='SELECT' else ''
                    if any(w in txt for w in ['löschen','zurücksetzen','Delete','Reset','E-Mail vorbereiten','Problem melden','Prepare email','Report a problem','English','Deutsch']): continue
                    if tag=='SELECT':
                        opts=await e.evaluate('x=>[...x.options].map(o=>o.value)'); await e.select_option(random.choice(opts))
                    else: await e.click(timeout=800)
                except Exception: pass
                await pg.wait_for_timeout(40)
            print(tr,lang,'errors',sorted(set(errs))[:6], 'url',pg.url[-20:]); await pg.close()
        await b.close()
asyncio.run(main())
