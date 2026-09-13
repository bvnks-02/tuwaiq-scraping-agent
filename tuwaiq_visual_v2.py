#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, pathlib, time, re, yaml, traceback
from scrapling.fetchers import StealthyFetcher

OUT = pathlib.Path("/home/bvnks/scraping_agent/output")
RAW = OUT / "raw"
OUT.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)

def log(m): print(m, flush=True)

def rgb_to_hex(rgb_str):
    m = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', rgb_str)
    if m:
        return f"#{int(m[1]):02x}{int(m[2]):02x}{int(m[3]):02x}"
    m = re.match(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d\.]+)\)', rgb_str)
    if m:
        return f"#{int(m[1]):02x}{int(m[2]):02x}{int(m[3]):02x}"
    return rgb_str

BASE = "https://tuwaiq.edu.sa"

def visual_action(page):
    try:
        page.wait_for_timeout(2500)
        js = r"""
        () => {
            const getStyle = (sel, props) => {
                const el = document.querySelector(sel);
                if (!el) return null;
                const cs = getComputedStyle(el);
                const o = {};
                props.forEach(p => o[p] = cs.getPropertyValue(p));
                o._selector = sel;
                o._text = (el.innerText || '').slice(0,120);
                const rect = el.getBoundingClientRect();
                o._rect = {width: Math.round(rect.width), height: Math.round(rect.height)};
                return o;
            };
            const typoProps = ['font-family','font-size','font-weight','line-height','letter-spacing','text-align','direction'];
            const colorProps = ['background-color','color','border-color','background-image','background'];
            const allProps = [...typoProps, ...colorProps, 'padding','margin','max-width','display','flex-direction','gap','border-radius','box-shadow','border','opacity'];
            const res = {};
            res.nav = getStyle('nav', allProps);
            res.header = getStyle('header', allProps);
            res.footer = getStyle('footer', allProps);
            res.body = getStyle('body', [...typoProps,'background-color','background-image']);
            res.html = {dir: document.documentElement.getAttribute('dir'), lang: document.documentElement.getAttribute('lang'), bodyDir: getComputedStyle(document.body).direction};
            res.h1 = getStyle('h1', [...typoProps, ...colorProps]);
            res.h2 = getStyle('h2', [...typoProps, ...colorProps]);
            res.h3 = getStyle('h3', [...typoProps, ...colorProps]);
            res.buttons = Array.from(document.querySelectorAll('a, button')).slice(0,14).map(el=>{
                const cs=getComputedStyle(el);
                const rect=el.getBoundingClientRect();
                const cls = el.getAttribute('class')||'';
                return {
                    text: (el.innerText||'').trim().slice(0,32),
                    href: el.getAttribute('href')||'',
                    className: cls.slice(0,150),
                    bg: cs.backgroundColor,
                    color: cs.color,
                    border: cs.borderColor,
                    fontFamily: cs.fontFamily,
                    fontSize: cs.fontSize,
                    fontWeight: cs.fontWeight,
                    lineHeight: cs.lineHeight,
                    padding: cs.padding,
                    borderRadius: cs.borderRadius,
                    boxShadow: cs.boxShadow,
                    display: cs.display,
                    width: Math.round(rect.width),
                    height: Math.round(rect.height)
                };
            }).filter(b=>b.text.length>0);
            const colorSet = new Set();
            const bgSet = new Set();
            const els = Array.from(document.querySelectorAll('*')).slice(0,600);
            els.forEach(el=>{
                const cs=getComputedStyle(el);
                if(cs.backgroundColor && cs.backgroundColor!=='rgba(0, 0, 0, 0)' && cs.backgroundColor!=='transparent') bgSet.add(cs.backgroundColor);
                if(cs.color) colorSet.add(cs.color);
                if(cs.borderColor && cs.borderColor!=='rgba(0, 0, 0, 0)' && cs.borderColor!=='transparent') colorSet.add(cs.borderColor);
            });
            res.palette_raw = Array.from(new Set([...bgSet, ...colorSet])).filter(c=>c.startsWith('rgb')).slice(0,70);
            res.gradients = Array.from(document.querySelectorAll('*')).slice(0,350).map(el=>getComputedStyle(el).backgroundImage).filter(v=>v && v!=='none' && v.includes('gradient')).slice(0,10);
            res.typography = {
                body: getStyle('body', typoProps),
                h1: getStyle('h1', typoProps),
                h2: getStyle('h2', typoProps),
                h3: getStyle('h3', typoProps),
                p: getStyle('p', typoProps),
                navLink: getStyle('nav a', typoProps),
                button: getStyle('a[href*="bootcamp"]', typoProps) || getStyle('button', typoProps),
                stat: (()=>{ const el=document.evaluate("//*[contains(text(),'2,474') or contains(text(),'2.474') or contains(text(),'1,654')]", document, null,9,null).singleNodeValue || document.querySelector('[class*="stat"]') || document.querySelector('[class*="number"]'); if(el){const cs=getComputedStyle(el.closest('div')||el); return {fontFamily: cs.fontFamily, fontSize: cs.fontSize, fontWeight: cs.fontWeight, lineHeight: cs.lineHeight, color: cs.color, text: (el.innerText||'').slice(0,50)} } return null;})()
            };
            res.fontFaces = [];
            try {
                const families = new Set();
                els.slice(0,250).forEach(el=>{
                    const cs=getComputedStyle(el);
                    if(cs.fontFamily) families.add(cs.fontFamily);
                });
                res.fontFamilies = Array.from(families);
            } catch(e){ res.fontFamilies=[]; }
            try {
                for(const ss of document.styleSheets){
                    try{
                        const rules = ss.cssRules || [];
                        for(const r of rules){
                            if(r.type===CSSRule.FONT_FACE_RULE){
                                res.fontFaces.push(r.cssText);
                            }
                        }
                    }catch(e){}
                    if(res.fontFaces.length>15) break;
                }
            }catch(e){}
            res.layout = {
                nav: getStyle('nav', ['display','flex-direction','justify-content','align-items','gap','padding','max-width','height']),
                container: getStyle('.container', ['max-width','padding','margin','display']) || getStyle('main', ['max-width','padding','display']) || getStyle('[class*="container"]', ['max-width','padding']),
                section: getStyle('section', ['padding','margin','max-width','display','gap']),
                cards: Array.from(document.querySelectorAll('[class*="card"], [class*="bootcamp"], section div[class*="bg-"]')).slice(0,4).map(el=>{ const cs=getComputedStyle(el); const rect=el.getBoundingClientRect(); const cls=el.getAttribute('class')||''; return {className: cls.slice(0,120), bg: cs.backgroundColor, radius: cs.borderRadius, padding: cs.padding, gap: cs.gap, display: cs.display, boxShadow: cs.boxShadow, width: Math.round(rect.width), height: Math.round(rect.height)};}),
                grid: (()=>{ const el=document.querySelector('[class*="grid"]'); if(el) {const cs=getComputedStyle(el); const cls=el.getAttribute('class')||''; return {display: cs.display, gridTemplateColumns: cs.gridTemplateColumns, gap: cs.gap, className: cls.slice(0,120)} } return null;})()
            };
            res.viewport = {width: window.innerWidth, height: window.innerHeight, devicePixelRatio: window.devicePixelRatio};
            res.breakpoints = (()=>{ const widths=['640px','768px','1024px','1280px']; const mqs=widths.map(w=>({query: `(min-width: ${w})`, matches: window.matchMedia(`(min-width: ${w})`).matches})); return mqs; })();
            res.components = {
                logos: Array.from(document.querySelectorAll('img[src*="logo"]')).slice(0,8).map(i=>({src: i.src, alt: i.alt, width: i.width, height: i.height, className: (i.getAttribute('class')||'').slice(0,80)})),
                icons: Array.from(document.querySelectorAll('img[src*="Arrow"], img[src*="arrow"], svg')).slice(0,10).map(el=>({src: el.src||el.outerHTML.slice(0,200), className: (el.getAttribute('class')||'').slice(0,80)})),
                artAssets: Array.from(document.querySelectorAll('img[src*="ART"], img[src*="art"], img[src*="Brands"], img[src*="numbers"], img[src*="founding"]')).slice(0,14).map(i=>({src: i.src, alt: i.alt})),
                partnerLogos: Array.from(document.querySelectorAll('img[src*="Brands"]')).slice(0,14).map(i=>i.src),
                backgroundImages: Array.from(document.querySelectorAll('*')).slice(0,350).map(el=>{ const bg=getComputedStyle(el).backgroundImage; if(bg && bg!=='none' && bg.includes('url')) return {selector: el.tagName+'.'+(el.getAttribute('class')||'').split(' ')[0].slice(0,25), bg: bg.slice(0,180)}; return null;}).filter(Boolean).slice(0,10)
            };
            res.allImages = Array.from(document.querySelectorAll('img')).slice(0,22).map(i=>({src: i.src, alt: (i.alt||'').slice(0,50), classes: (i.getAttribute('class')||'').slice(0,70)}));
            res.rtl = {
                htmlDir: document.documentElement.dir,
                htmlLang: document.documentElement.lang,
                bodyDirection: getComputedStyle(document.body).direction,
                bodyTextAlign: getComputedStyle(document.body).textAlign,
                navDirection: document.querySelector('nav') ? getComputedStyle(document.querySelector('nav')).direction : null,
                mirroredIcons: (()=>{ const arrows=Array.from(document.querySelectorAll('img[src*="Arrow"]')); return arrows.map(a=>({src: a.src, transform: getComputedStyle(a).transform, filter: getComputedStyle(a).filter}));})()
            };
            res.animations = Array.from(document.querySelectorAll('*')).slice(0,350).map(el=>{
                const cs=getComputedStyle(el);
                if(cs.transition && cs.transition!=='all 0s ease 0s') return {tag: el.tagName, className: (el.getAttribute('class')||'').slice(0,90), transition: cs.transition, animation: cs.animation};
                return null;
            }).filter(Boolean).slice(0,12);
            res.cssVariables = (()=>{ const vars={}; try{ const cs=getComputedStyle(document.documentElement); for(let i=0;i<cs.length;i++){const prop=cs[i]; if(prop.startsWith('--')) vars[prop]=cs.getPropertyValue(prop);} }catch(e){} return vars; })();
            return res;
        }
        """
        data = page.evaluate(js)
        import json, pathlib
        out = pathlib.Path("/tmp/tuwaiq_visual_raw.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Visual captured keys {list(data.keys())} palette {len(data.get('palette_raw',[]))}")
        return data
    except Exception as e:
        print(f"visual_action error: {e}")
        import traceback; traceback.print_exc()
        return None

log("Fetching visual design from homepage...")
try:
    resp = StealthyFetcher.fetch(BASE+"/", solve_cloudflare=True, network_idle=True, timeout=90000, wait=4000, headless=True, locale="ar-SA", page_action=visual_action)
    log(f"Fetched {resp.status} len {len(resp.html_content)}")
    with open(RAW / "home_visual_v2.html", "w", encoding="utf-8") as f:
        f.write(resp.html_content)
except Exception as e:
    log(f"Fetch failed: {e}")
    traceback.print_exc()

# Load and process
import pathlib, json
raw_path = pathlib.Path("/tmp/tuwaiq_visual_raw.json")
if not raw_path.exists():
    log("No visual raw, abort")
    exit(1)
raw = json.loads(raw_path.read_text(encoding="utf-8"))

# Process tokens
palette_raw = raw.get("palette_raw", [])
palette_hex = []
palette_rgb = []
for c in palette_raw:
    if c.startswith("rgb"):
        palette_rgb.append(c)
        hv = rgb_to_hex(c)
        if hv not in palette_hex:
            palette_hex.append(hv)

buttons = raw.get("buttons", [])
primary_bg = None
for b in buttons:
    if b.get("bg") and b["bg"] != "rgba(0, 0, 0, 0)":
        if "ابدأ" in b.get("text","") or "سجل" in b.get("text",""):
            primary_bg = b["bg"]; break
if not primary_bg:
    for b in buttons:
        if b.get("bg") and b["bg"].startswith("rgb"):
            primary_bg = b["bg"]; break

typo = raw.get("typography", {})
layout = raw.get("layout", {})
comps = raw.get("components", {})

tokens = {
    "meta": {
        "source": BASE+"/",
        "extractedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "method": "StealthyFetcher + getComputedStyle (network_idle, solve_cloudflare, locale ar-SA)",
        "viewport": raw.get("viewport", {}),
        "note": "Preserved Arabic, RTL dir=rtl, rate-limited"
    },
    "colors": {
        "palette_rgb": palette_rgb[:40],
        "palette_hex": palette_hex[:40],
        "primary_candidates": {
            "button_primary_bg": primary_bg,
            "button_primary_hex": rgb_to_hex(primary_bg) if primary_bg else None,
            "nav_bg": raw.get("nav", {}).get("background-color") if isinstance(raw.get("nav"), dict) else None,
            "body_bg": raw.get("body", {}).get("background-color") if isinstance(raw.get("body"), dict) else None
        },
        "gradients": raw.get("gradients", [])[:8],
        "backgrounds": {
            "body": raw.get("body", {}).get("background-color") if isinstance(raw.get("body"), dict) else None,
            "nav": raw.get("nav", {}).get("background-color") if isinstance(raw.get("nav"), dict) else None,
            "footer": raw.get("footer", {}).get("background-color") if isinstance(raw.get("footer"), dict) else None,
            "header": raw.get("header", {}).get("background-color") if isinstance(raw.get("header"), dict) else None
        },
        "texts": {
            "body": raw.get("body", {}).get("color") if isinstance(raw.get("body"), dict) else None,
            "h1": raw.get("h1", {}).get("color") if isinstance(raw.get("h1"), dict) else None,
            "h2": raw.get("h2", {}).get("color") if isinstance(raw.get("h2"), dict) else None,
            "nav": raw.get("nav", {}).get("color") if isinstance(raw.get("nav"), dict) else None
        },
        "buttons": buttons[:10]
    },
    "typography": {
        "fontFamilies_raw": raw.get("fontFamilies", [])[:12] or raw.get("fontFaces", [])[:5],
        "scales": {
            "h1": typo.get("h1") or raw.get("h1"),
            "h2": typo.get("h2") or raw.get("h2"),
            "h3": typo.get("h3"),
            "body": typo.get("body") or raw.get("body"),
            "p": typo.get("p"),
            "navLink": typo.get("navLink"),
            "button": typo.get("button"),
            "stat": typo.get("stat")
        },
        "rtl": raw.get("rtl", {}),
        "fontFaces": raw.get("fontFaces", [])[:10]
    },
    "layout": {
        "viewport": raw.get("viewport"),
        "breakpoints": raw.get("breakpoints"),
        "navbar": layout.get("nav") if isinstance(layout, dict) else raw.get("nav"),
        "container": layout.get("container") if isinstance(layout, dict) else None,
        "section": layout.get("section") if isinstance(layout, dict) else None,
        "cards": layout.get("cards") if isinstance(layout, dict) else None,
        "grid": layout.get("grid") if isinstance(layout, dict) else None,
        "spacing": {
            "nav": raw.get("nav", {}).get("padding") if isinstance(raw.get("nav"), dict) else None
        }
    },
    "components": {
        "logos": comps.get("logos", [])[:6] if isinstance(comps, dict) else [],
        "icons": comps.get("icons", [])[:10] if isinstance(comps, dict) else [],
        "artAssets": comps.get("artAssets", [])[:10] if isinstance(comps, dict) else [],
        "partnerLogos": comps.get("partnerLogos", [])[:12] if isinstance(comps, dict) else [],
        "backgroundImages": comps.get("backgroundImages", [])[:8] if isinstance(comps, dict) else [],
        "allImages_sample": raw.get("allImages", [])[:12] if isinstance(raw.get("allImages"), list) else []
    },
    "assets": {
        "images": raw.get("allImages", [])[:18] if isinstance(raw.get("allImages"), list) else [],
        "art": raw.get("artAssets", [])[:8] if isinstance(raw.get("artAssets"), list) else [],
        "logos": raw.get("logos", [])[:5] if isinstance(raw.get("logos"), list) else []
    },
    "animations": raw.get("animations", [])[:12],
    "cssVariables": raw.get("cssVariables", {}),
    "raw_palette_details": palette_rgb
}

with open(OUT / "design-tokens.json", "w", encoding="utf-8") as f:
    json.dump(tokens, f, ensure_ascii=False, indent=2)
with open(OUT / "design-tokens.yaml", "w", encoding="utf-8") as f:
    yaml.safe_dump(tokens, f, allow_unicode=True, sort_keys=False)
log(f"Saved design-tokens.json/yaml")

# Write style-guide.md
md = OUT / "style-guide.md"
with open(md, "w", encoding="utf-8") as f:
    f.write("# أكاديمية طويق — دليل النظام البصري (Tuwaiq Visual System)\n\n")
    f.write(f"**Source:** {BASE}/  \n**Extracted:** {tokens['meta']['extractedAt']}  \n**Viewport:** {tokens['meta']['viewport']}  \n**Method:** StealthyFetcher (Patchright) + getComputedStyle, network_idle, solve_cloudflare, locale ar-SA\n\n---\n\n## 1. الألوان (Colors)\n\n### لوحة الألوان المستخرجة (computed palette)\n")
    for hv, rgb in zip(tokens["colors"]["palette_hex"][:20], tokens["colors"]["palette_rgb"][:20]):
        f.write(f"- `{hv}` ← `{rgb}`\n")
    f.write("\n**Primary candidates:**\n")
    f.write(f"- Button primary BG: `{tokens['colors']['primary_candidates']['button_primary_bg']}` → `{tokens['colors']['primary_candidates']['button_primary_hex']}`\n")
    f.write(f"- Nav BG: `{tokens['colors']['primary_candidates']['nav_bg']}`\n")
    f.write(f"- Body BG: `{tokens['colors']['primary_candidates']['body_bg']}`\n")
    grads = tokens["colors"]["gradients"]
    if grads:
        f.write("\n**Gradients detected:**\n")
        for g in grads:
            f.write(f"- `{g[:160]}`\n")
    f.write("\n**Backgrounds:**\n")
    for k,v in tokens["colors"]["backgrounds"].items():
        f.write(f"- {k}: `{v}`\n")
    f.write("\n**Texts:**\n")
    for k,v in tokens["colors"]["texts"].items():
        f.write(f"- {k}: `{v}`\n")
    f.write("\n**Buttons (sample, preserve Arabic):**\n")
    for b in tokens["colors"]["buttons"]:
        f.write(f"- \"{b.get('text','')[:28]}\" bg:{b.get('bg')} color:{b.get('color')} font:{b.get('fontFamily','')[:40]} size:{b.get('fontSize')} radius:{b.get('borderRadius')} href:{b.get('href','')[:50]}\n")
    f.write("\n---\n\n## 2. الطباعة (Typography)\n\n")
    f.write(f"**RTL:** html dir=`{tokens['typography']['rtl'].get('htmlDir')}` lang=`{tokens['typography']['rtl'].get('htmlLang')}` bodyDirection=`{tokens['typography']['rtl'].get('bodyDirection')}` bodyTextAlign=`{tokens['typography']['rtl'].get('bodyTextAlign')}`\n\n")
    f.write("**Font families (raw computed):**\n")
    for fam in tokens["typography"]["fontFamilies_raw"][:8]:
        f.write(f"- `{str(fam)[:220]}`\n")
    if tokens["typography"]["fontFaces"]:
        f.write("\n**@font-face rules:**\n")
        for ff in tokens["typography"]["fontFaces"][:4]:
            f.write(f"```css\n{ff[:500]}\n```\n")
    f.write("\n**Scales:**\n")
    for k,v in tokens["typography"]["scales"].items():
        if v:
            f.write(f"- **{k}**: family=`{str(v.get('font-family',''))[:70]}` size=`{v.get('font-size')}` weight=`{v.get('font-weight')}` lineHeight=`{v.get('line-height')}` direction=`{v.get('direction')}` textAlign=`{v.get('text-align')}` text=`{str(v.get('_text',''))[:40]}`\n")
    f.write("\n---\n\n## 3. التخطيط والمسافات (Layout & Spacing)\n\n")
    f.write(f"**Viewport:** {tokens['layout']['viewport']}\n\n")
    f.write("**Breakpoints (matchMedia):**\n")
    for bp in tokens["layout"]["breakpoints"] or []:
        f.write(f"- {bp.get('query')}: {bp.get('matches')}\n")
    f.write("\n**Navbar computed:**\n")
    nav = tokens["layout"]["navbar"]
    if isinstance(nav, dict):
        for k in ['display','flex-direction','justify-content','align-items','gap','padding','max-width','height','background-color']:
            if k in nav:
                f.write(f"- {k}: `{nav[k]}`\n")
    f.write("\n**Container:**\n")
    cont = tokens["layout"]["container"]
    if isinstance(cont, dict):
        for k,v in cont.items():
            if not k.startswith('_'):
                f.write(f"- {k}: `{v}`\n")
    f.write("\n**Cards (sample):**\n")
    for card in (tokens["layout"]["cards"] or [])[:4]:
        f.write(f"- {card}\n")
    f.write("\n---\n\n## 4. المكونات والأصول (Components & Assets)\n\n")
    f.write("**Logos:**\n")
    for logo in tokens["components"]["logos"][:6]:
        if isinstance(logo, dict):
            f.write(f"- `{logo.get('src')}` alt:{logo.get('alt','')[:40]} {logo.get('width')}x{logo.get('height')}\n")
        else:
            f.write(f"- `{logo}`\n")
    f.write("\n**Icons / Arrows (RTL mirrored check):**\n")
    for icon in tokens["components"]["icons"][:6]:
        f.write(f"- {icon}\n")
    if tokens["typography"]["rtl"].get("mirroredIcons"):
        f.write("\n**MirroredIcons detail:**\n")
        for mi in tokens["typography"]["rtl"]["mirroredIcons"][:4]:
            f.write(f"- {mi}\n")
    f.write("\n**Art assets:**\n")
    for art in tokens["components"]["artAssets"][:10]:
        if isinstance(art, dict):
            f.write(f"- `{art.get('src')}`\n")
        else:
            f.write(f"- `{art}`\n")
    f.write("\n**Partner logo strip (marquee):**\n")
    for pl in tokens["components"]["partnerLogos"][:10]:
        f.write(f"- `{pl}`\n")
    f.write("\n**Background images:**\n")
    for bg in tokens["components"]["backgroundImages"][:6]:
        f.write(f"- {bg}\n")
    f.write("\n**Animations / Transitions:**\n")
    for anim in tokens["animations"][:6]:
        f.write(f"- {anim}\n")
    f.write("\n**CSS Variables (if any):**\n")
    for k,v in list(tokens["cssVariables"].items())[:12]:
        f.write(f"- {k}: `{v}`\n")
    f.write("\n---\n\n## ملاحظات الاستخدام (Usage Notes)\n\n")
    f.write("- الموقع RTL بالكامل (`dir=\"rtl\"`, `direction: rtl`) — يجب عكس الأسهم والأيقونات (transform mirror) والحفاظ على `text-align: right` للعربية.\n")
    f.write("- الأزرار الأساسية تستخدم خلفية ملونة (primary) مع نص أبيض و `border-radius` كبير (pill shape) — تحقق من `buttons` أعلاه.\n")
    f.write("- البطاقات (bootcamp/category) تستخدم `border-radius`, `box-shadow` خفيف, `padding` واسع, و `background-image` للزخرفة (`/img/ART/*.svg`).\n")
    f.write("- الخطوط عربية غير لاتينية — تفقد `@font-face` و `font-family` أعلاه؛ إن لم تظهر فالنظام يستخدم fallback لخطوط النظام مع `Times New Roman` كـ placeholder قبل تحميل الخط الفعلي (يتطلب فحص الشبكة).\n")
    f.write("- استخدم `container max-width` و `section padding` للتباعد العمودي المنتظم.\n")
    f.write("- شريط شعارات الشركاء يستخدم تمرير marquee أفقي — راجع `img[src*=\"Brands\"]`.\n")
    f.write("\n---\n*Generated via Scrapling StealthyFetcher, preserved Arabic, rate-limited 3s.*\n")

log(f"Style guide written to {md}")
print(json.dumps({"palette_hex": tokens["colors"]["palette_hex"][:6], "primary": tokens["colors"]["primary_candidates"], "fonts": tokens["typography"]["fontFamilies_raw"][:2]}, ensure_ascii=False, indent=2))
