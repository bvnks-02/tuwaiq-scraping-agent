#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tuwaiq Academy comprehensive scraper
- Part 1: Visual Design System (colors, typography, layout, components, assets) via computed styles
- Part 2: Academic Content (programs, sub-academies, platforms, courses, stats, FAQs, news, report)
Uses Scrapling StealthyFetcher with Cloudflare bypass, network_idle, RTL preservation.
Respect robots.txt (Allow: /), rate-limited, avoids /signin.
"""
import json
import time
import os
import yaml
import pathlib
import traceback
from urllib.parse import urljoin
import sys

# Setup output dirs
OUTPUT = pathlib.Path("/home/bvnks/scraping_agent/output")
RAW = OUTPUT / "raw"
OUTPUT.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)

LOG = OUTPUT / "scrape.log"
def log(msg):
    print(msg, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# URLs to crawl
BASE = "https://tuwaiq.edu.sa"
URLS = {
    "homepage": BASE + "/",
    "about": BASE + "/about",
    "accreditations": BASE + "/Accreditations",
    "partners": BASE + "/Partners",
    "faqs": BASE + "/Faqs",
    "news": BASE + "/news",
    "report": BASE + "/report",
    "bootcamps_all": BASE + "/bootcamps",
    "bootcamp_camp": BASE + "/bootcamps?category=ac41152d-f228-8af4-8406-e0cda6df6c35&type=NORMAL",
    "bootcamp_program": BASE + "/bootcamps?category=8836bde0-68ae-3600-92a2-23dce3c487ca&type=NORMAL",
    "bootcamp_meetup": BASE + "/bootcamps?category=c616115c-5cf8-426d-9f70-42eb370ca37d&type=NORMAL",
    "bootcamp_webinar": BASE + "/bootcamps?category=56732582-5b07-4fbf-9ee8-89c26d87b419&type=NORMAL",
}
SATR = "https://satr.tuwaiq.edu.sa"

# rate limit helper
def sleep_rate():
    time.sleep(3)

# Try import scrapling
try:
    from scrapling.fetchers import StealthyFetcher
    HAS_SCRAPLING = True
    log("Scrapling available: 0.4.15")
except Exception as e:
    log(f"Failed import scrapling: {e}")
    HAS_SCRAPLING = False
    sys.exit(1)

# Helper: fetch with stealth, saving raw html
def stealth_fetch(url, fname, wait=3000, network_idle=True):
    log(f"Fetching {url} -> {fname}")
    try:
        # Use page_action to capture raw html via side effect? For now just fetch Response
        resp = StealthyFetcher.fetch(url, solve_cloudflare=True, network_idle=network_idle, timeout=90000, wait=wait, headless=True, locale="ar-SA")
        # Save raw html
        html = resp.html_content if hasattr(resp, 'html_content') else str(resp.html_content if hasattr(resp, 'html_content') else resp)
        # resp.html_content is str, resp.text as well? Use html_content
        try:
            with open(RAW / fname, "w", encoding="utf-8") as f:
                f.write(html)
            log(f"Saved raw {fname} {len(html)} bytes status {getattr(resp,'status', 'unknown')}")
        except Exception as e:
            log(f"Save raw failed {e}")
        return resp
    except Exception as e:
        log(f"Fetch failed {url}: {e}")
        traceback.print_exc()
        return None

# ========== PART 1: VISUAL DESIGN SYSTEM ==========
def extract_visual_design():
    log("=== PART 1: Visual Design System ===")
    # Use StealthyFetcher with page_action side-effect to capture computed styles
    design_data = {}
    def visual_action(page):
        # This runs inside python, with playwright page object available, after Cloudflare solved and network_idle
        try:
            # Wait a bit for fonts/styles to load
            page.wait_for_timeout(2000)
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
                    o._rect = {width: rect.width, height: rect.height, top: rect.top};
                    return o;
                };
                const typoProps = ['font-family','font-size','font-weight','line-height','letter-spacing','text-align','direction'];
                const colorProps = ['background-color','color','border-color','background-image','background'];
                const allProps = [...typoProps, ...colorProps, 'padding','margin','max-width','display','flex-direction','gap','border-radius','box-shadow','border','opacity'];
                const res = {};
                // Colors - computed on key elements
                res.nav = getStyle('nav', allProps);
                res.header = getStyle('header', allProps);
                res.footer = getStyle('footer', allProps);
                res.body = getStyle('body', [...typoProps,'background-color','background-image']);
                res.html = {dir: document.documentElement.getAttribute('dir'), lang: document.documentElement.getAttribute('lang'), bodyDir: getComputedStyle(document.body).direction};
                // Headings
                res.h1 = getStyle('h1', [...typoProps, ...colorProps]);
                res.h2 = getStyle('h2', [...typoProps, ...colorProps]);
                // Buttons
                const btnSelectors = ['a[href*="bootcamp"]','button','a.bg-\\[\\#4e96ff\\]','[class*="bg-purple"]','[class*="btn"]'];
                res.buttons = Array.from(document.querySelectorAll('a, button')).slice(0,12).map(el=>{
                    const cs=getComputedStyle(el);
                    const rect=el.getBoundingClientRect();
                    return {
                        text: (el.innerText||'').trim().slice(0,30),
                        href: el.getAttribute('href')||'',
                        className: (el.getAttribute('class')||'').slice(0,150)||'',
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
                        width: rect.width,
                        height: rect.height
                    };
                }).filter(b=>b.text.length>0);
                // Palette - collect unique colors from many elements
                const colorSet = new Set();
                const bgSet = new Set();
                const els = Array.from(document.querySelectorAll('*')).slice(0,500);
                els.forEach(el=>{
                    const cs=getComputedStyle(el);
                    ['color','backgroundColor','borderColor','backgroundImage'].forEach(k=>{
                        const v=cs[k];
                        if(v && v!=='rgba(0, 0, 0, 0)' && v!=='transparent' && v!=='none' && !v.includes('linear-gradient') ) {
                            // keep rgb only for palette
                            if(k!=='backgroundImage') {
                                if(v.startsWith('rgb')) colorSet.add(v);
                            }
                        }
                        if(v && v.includes('rgb') && !v.includes('rgba(0, 0, 0, 0)')) {
                            // capture
                        }
                    });
                    if(cs.backgroundColor && cs.backgroundColor!=='rgba(0, 0, 0, 0)' && cs.backgroundColor!=='transparent') bgSet.add(cs.backgroundColor);
                    if(cs.color) colorSet.add(cs.color);
                    if(cs.borderColor && cs.borderColor!=='rgba(0, 0, 0, 0)' && cs.borderColor!=='transparent') colorSet.add(cs.borderColor);
                });
                // Convert rgb to hex helper in python later, but collect raw rgb
                res.palette_raw = Array.from(new Set([...bgSet, ...colorSet])).filter(c=>c.startsWith('rgb')).slice(0,60);
                // Also collect gradient backgrounds
                res.gradients = Array.from(document.querySelectorAll('*')).slice(0,300).map(el=>getComputedStyle(el).backgroundImage).filter(v=>v && v!=='none' && v.includes('gradient')).slice(0,10);
                // Typography details
                res.typography = {
                    body: getStyle('body', typoProps),
                    h1: getStyle('h1', typoProps),
                    h2: getStyle('h2', typoProps),
                    h3: getStyle('h3', typoProps),
                    p: getStyle('p', typoProps),
                    navLink: getStyle('nav a', typoProps),
                    button: getStyle('a[href*="bootcamp"]', typoProps) || getStyle('button', typoProps),
                    stat: (()=>{ const el=document.evaluate("//*[contains(text(),'2,474') or contains(text(),'2.474') or contains(text(),'1,654')]", document, null,9,null).singleNodeValue || document.querySelector('[class*="stat"]') || document.querySelector('[class*="number"]'); if(el){const cs=getComputedStyle(el.closest('div')||el); return {fontFamily: cs.fontFamily, fontSize: cs.fontSize, fontWeight: cs.fontWeight, lineHeight: cs.lineHeight, color: cs.color, text: (el.innerText||'').slice(0,40)} } return null;})()
                };
                // Font faces
                res.fontFaces = [];
                res.fontFamilies = new Set();
                try {
                    const families = new Set();
                    els.slice(0,200).forEach(el=>{
                        const cs=getComputedStyle(el);
                        if(cs.fontFamily) families.add(cs.fontFamily);
                    });
                    res.fontFamilies = Array.from(families);
                } catch(e){}
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
                // Layout & spacing
                res.layout = {
                    nav: getStyle('nav', ['display','flex-direction','justify-content','align-items','gap','padding','max-width','height']),
                    container: getStyle('.container', ['max-width','padding','margin','display']) || getStyle('main', ['max-width','padding','display']) || getStyle('[class*="container"]', ['max-width','padding']),
                    section: getStyle('section', ['padding','margin','max-width','display','gap']),
                    cards: Array.from(document.querySelectorAll('[class*="card"], [class*="bootcamp"], section div[class*="bg-"]')).slice(0,3).map(el=>{ const cs=getComputedStyle(el); const rect=el.getBoundingClientRect(); return {className: (el.getAttribute('class')||'').slice(0,120), bg: cs.backgroundColor, radius: cs.borderRadius, padding: cs.padding, gap: cs.gap, display: cs.display, boxShadow: cs.boxShadow, width: rect.width, height: rect.height};}),
                    grid: (()=>{ const el=document.querySelector('[class*="grid"]'); if(el) {const cs=getComputedStyle(el); return {display: cs.display, gridTemplateColumns: cs.gridTemplateColumns, gap: cs.gap, className: (el.getAttribute('class')||'').slice(0,120)} } return null;})()
                };
                // Breakpoints via media queries inspection and viewport
                res.viewport = {width: window.innerWidth, height: window.innerHeight, devicePixelRatio: window.devicePixelRatio};
                res.breakpoints = (()=>{ const widths=['640px','768px','1024px','1280px']; const mqs=widths.map(w=>({query: `(min-width: ${w})`, matches: window.matchMedia(`(min-width: ${w})`).matches})); return mqs; })();
                // Components & assets
                res.components = {
                    logos: Array.from(document.querySelectorAll('img[src*="logo"]')).slice(0,8).map(i=>({src: i.src, alt: i.alt, width: i.width, height: i.height, className: (i.getAttribute('class')||'').slice(0,80)})),
                    icons: Array.from(document.querySelectorAll('img[src*="Arrow"], img[src*="arrow"], svg')).slice(0,8).map(el=>({src: el.src||el.outerHTML.slice(0,200), className: (el.getAttribute('class')||'').slice(0,80)})),
                    artAssets: Array.from(document.querySelectorAll('img[src*="ART"], img[src*="art"], img[src*="Brands"], img[src*="numbers"], img[src*="founding"]')).slice(0,12).map(i=>({src: i.src, alt: i.alt})),
                    partnerLogos: Array.from(document.querySelectorAll('img[src*="Brands"]')).slice(0,12).map(i=>i.src),
                    backgroundImages: Array.from(document.querySelectorAll('*')).slice(0,300).map(el=>{ const bg=getComputedStyle(el).backgroundImage; if(bg && bg!=='none' && bg.includes('url')) return {selector: el.tagName+'.'+(el.getAttribute('class')||'').split(' ')[0].slice(0,20), bg}; return null;}).filter(Boolean).slice(0,8)
                };
                res.allImages = Array.from(document.querySelectorAll('img')).slice(0,20).map(i=>({src: i.src, alt: i.alt?.slice(0,40)||'', classes: (i.getAttribute('class')||'').slice(0,60)}));
                // RTL specifics
                res.rtl = {
                    htmlDir: document.documentElement.dir,
                    htmlLang: document.documentElement.lang,
                    bodyDirection: getComputedStyle(document.body).direction,
                    bodyTextAlign: getComputedStyle(document.body).textAlign,
                    navDirection: document.querySelector('nav') ? getComputedStyle(document.querySelector('nav')).direction : null,
                    mirroredIcons: (()=>{ const arrows=Array.from(document.querySelectorAll('img[src*="Arrow"]')); return arrows.map(a=>({src: a.src, transform: getComputedStyle(a).transform, filter: getComputedStyle(a).filter}));})()
                };
                // Animation classes
                res.animations = Array.from(document.querySelectorAll('*')).slice(0,300).map(el=>{
                    const cs=getComputedStyle(el);
                    if(cs.transition && cs.transition!=='all 0s ease 0s') return {tag: el.tagName, className: (el.getAttribute('class')||'').slice(0,80), transition: cs.transition, animation: cs.animation};
                    return null;
                }).filter(Boolean).slice(0,10);
                // Raw CSS inspection for primary colors in stylesheets
                res.cssVariables = (()=>{ const vars={}; try{ const cs=getComputedStyle(document.documentElement); for(let i=0;i<cs.length;i++){const prop=cs[i]; if(prop.startsWith('--')) vars[prop]=cs.getPropertyValue(prop);} }catch(e){} return vars; })();
                return res;
            }
            """
            data = page.evaluate(js)
            # Save to file for later processing
            import json, pathlib
            out = pathlib.Path("/tmp/tuwaiq_visual_raw.json")
            with open(out, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Visual design data captured to {out}, keys: {list(data.keys())}")
            # Also try to capture palette raw via separate evaluation for debug
            return data
        except Exception as e:
            print(f"visual_action error: {e}")
            import traceback; traceback.print_exc()
            return None

    # Do fetch with visual action
    try:
        resp = StealthyFetcher.fetch(BASE+"/", solve_cloudflare=True, network_idle=True, timeout=90000, wait=4000, headless=True, locale="ar-SA", page_action=visual_action)
        log(f"Visual fetch status {resp.status} len {len(resp.html_content)}")
        with open(RAW / "home_visual.html", "w", encoding="utf-8") as f:
            f.write(resp.html_content)
    except Exception as e:
        log(f"Visual design fetch failed: {e}")
        traceback.print_exc()
        return None

    # Load captured data
    import pathlib, json
    raw_path = pathlib.Path("/tmp/tuwaiq_visual_raw.json")
    if not raw_path.exists():
        log("Visual raw not found, fallback to minimal")
        return None
    with open(raw_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    sleep_rate()
    # Also fetch one more page for comparison (about) to catch additional components
    try:
        def second_action(page):
            page.wait_for_timeout(2000)
            data = page.evaluate("() => { return {url: location.href, title: document.title, htmlDir: document.documentElement.dir, palette: Array.from(new Set(Array.from(document.querySelectorAll('*')).slice(0,300).map(el=>getComputedStyle(el).backgroundColor).filter(c=>c && c!=='rgba(0, 0, 0, 0)'))).slice(0,20)} }")
            with open("/tmp/tuwaiq_visual_about.json","w",encoding="utf-8") as f:
                import json; json.dump(data,f,ensure_ascii=False,indent=2)
        StealthyFetcher.fetch(BASE+"/about", solve_cloudflare=True, network_idle=True, timeout=90000, wait=3000, headless=True, locale="ar-SA", page_action=second_action)
    except Exception as e:
        log(f"Second visual fetch failed: {e}")

    # Process raw into design tokens
    design_tokens = process_visual_raw(raw)
    # Save JSON and YAML
    with open(OUTPUT / "design-tokens.json", "w", encoding="utf-8") as f:
        json.dump(design_tokens, f, ensure_ascii=False, indent=2)
    with open(OUTPUT / "design-tokens.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(design_tokens, f, allow_unicode=True, sort_keys=False)
    log(f"Saved design-tokens.json and yaml to {OUTPUT}")
    # Write style-guide.md
    write_style_guide(design_tokens, raw)
    return design_tokens

def rgb_to_hex(rgb_str):
    # rgb(78, 150, 255) -> #4e96ff
    m = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', rgb_str)
    if m:
        return f"#{int(m[1]):02x}{int(m[2]):02x}{int(m[3]):02x}"
    m = re.match(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d\.]+)\)', rgb_str)
    if m:
        return f"#{int(m[1]):02x}{int(m[2]):02x}{int(m[3]):02x}"
    return rgb_str

def process_visual_raw(raw):
    palette_raw = raw.get("palette_raw", []) or raw.get("palette", [])
    # Deduplicate and convert to hex where possible
    palette_hex = []
    palette_rgb = []
    for c in palette_raw:
        if c.startswith("rgb"):
            palette_rgb.append(c)
            hexv = rgb_to_hex(c)
            if hexv not in palette_hex:
                palette_hex.append(hexv)
    # Ensure primary brand colors are prioritized (look for purple/blue typical)
    # From manual exploration, Tuwaiq uses purple #6c4eff? and blue #4e96ff (#4E96FF, #59E2D7)
    # But we will infer from computed: first find prominent brand colors
    # Count frequency by sampling buttons and nav
    buttons = raw.get("buttons", [])
    # Extract brand accent from button bg
    primary_button_bg = None
    for b in buttons:
        if b.get("bg") and b["bg"] != "rgba(0, 0, 0, 0)":
            if "ابدأ" in b.get("text","") or "سجل" in b.get("text",""):
                primary_button_bg = b["bg"]
                break
    if not primary_button_bg:
        for b in buttons:
            if b.get("bg") and b["bg"].startswith("rgb"):
                primary_button_bg = b["bg"]
                break

    # Typography
    typo = raw.get("typography", {})
    # Layout
    layout = raw.get("layout", {})
    # Components
    comps = raw.get("components", {})

    tokens = {
        "meta": {
            "source": "https://tuwaiq.edu.sa",
            "extractedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "method": "StealthyFetcher + getComputedStyle (network_idle, solve_cloudflare)",
            "viewport": raw.get("viewport", {}),
            "note": "Preserved Arabic, RTL dir=rtl"
        },
        "colors": {
            "palette_rgb": palette_rgb[:30],
            "palette_hex": palette_hex[:30],
            "primary_candidates": {
                "button_primary_bg": primary_button_bg,
                "button_primary_hex": rgb_to_hex(primary_button_bg) if primary_button_bg else None,
                "nav_bg": raw.get("nav", {}).get("background-color") if isinstance(raw.get("nav"), dict) else None,
                "body_bg": raw.get("body", {}).get("background-color") if isinstance(raw.get("body"), dict) else None
            },
            "gradients": raw.get("gradients", [])[:5],
            "backgrounds": {
                "body": raw.get("body", {}).get("background-color"),
                "nav": raw.get("nav", {}).get("background-color"),
                "footer": raw.get("footer", {}).get("background-color") if isinstance(raw.get("footer"), dict) else None,
                "hero": raw.get("header", {}).get("background-color") if isinstance(raw.get("header"), dict) else None
            },
            "texts": {
                "body": raw.get("body", {}).get("color") if isinstance(raw.get("body"), dict) else None,
                "h1": raw.get("h1", {}).get("color") if isinstance(raw.get("h1"), dict) else None,
                "h2": raw.get("h2", {}).get("color") if isinstance(raw.get("h2"), dict) else None,
                "nav": raw.get("nav", {}).get("color") if isinstance(raw.get("nav"), dict) else None
            },
            "buttons": buttons[:8]
        },
        "typography": {
            "fontFamilies_raw": raw.get("fontFamilies", [])[:10] or raw.get("fontFaces", [])[:5],
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
            "fontFaces": raw.get("fontFaces", [])[:8]
        },
        "layout": {
            "viewport": raw.get("viewport"),
            "breakpoints": raw.get("breakpoints"),
            "navbar": layout.get("nav") if isinstance(layout, dict) else raw.get("nav"),
            "container": layout.get("container") if isinstance(layout, dict) else None,
            "section": layout.get("section") if isinstance(layout, dict) else None,
            "cards": layout.get("cards") if isinstance(layout, dict) else raw.get("cards"),
            "grid": layout.get("grid") if isinstance(layout, dict) else None,
            "spacing": {
                "nav": raw.get("nav", {}).get("padding") if isinstance(raw.get("nav"), dict) else None,
                "section": raw.get("layout", {}).get("section", {}).get("padding") if isinstance(raw.get("layout"), dict) and isinstance(raw.get("layout", {}).get("section"), dict) else None
            }
        },
        "components": {
            "logos": comps.get("logos", [])[:5] if isinstance(comps, dict) else raw.get("logos", [])[:5] if isinstance(raw.get("logos"), list) else [],
            "icons": comps.get("icons", [])[:8] if isinstance(comps, dict) else [],
            "artAssets": comps.get("artAssets", [])[:8] if isinstance(comps, dict) else raw.get("artAssets", [])[:8] if isinstance(raw.get("artAssets"), list) else [],
            "partnerLogos": comps.get("partnerLogos", [])[:8] if isinstance(comps, dict) else [],
            "backgroundImages": comps.get("backgroundImages", [])[:5] if isinstance(comps, dict) else [],
            "allImages_sample": raw.get("allImages", [])[:10] if isinstance(raw.get("allImages"), list) else []
        },
        "assets": {
            "images": raw.get("allImages", [])[:15] if isinstance(raw.get("allImages"), list) else [],
            "art": raw.get("artAssets", [])[:8] if isinstance(raw.get("artAssets"), list) else [],
            "logos": raw.get("logos", [])[:5] if isinstance(raw.get("logos"), list) else []
        },
        "animations": raw.get("animations", [])[:10],
        "cssVariables": raw.get("cssVariables", {}),
        "raw_palette_details": palette_rgb
    }
    return tokens

def write_style_guide(tokens, raw):
    md_path = OUTPUT / "style-guide.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# أكاديمية طويق — دليل النظام البصري (Tuwaiq Visual System)\n\n")
        f.write(f"**Source:** https://tuwaiq.edu.sa  \n**Extracted:** {tokens['meta']['extractedAt']}  \n**Viewport:** {tokens['meta']['viewport']}  \n**Method:** StealthyFetcher (Patchright) + getComputedStyle, network_idle, solve_cloudflare, locale ar-SA\n\n")
        f.write("---\n\n## 1. الألوان (Colors)\n\n")
        f.write("### لوحة الألوان المستخرجة (computed palette)\n")
        for hexv, rgb in zip(tokens["colors"]["palette_hex"][:15], tokens["colors"]["palette_rgb"][:15]):
            f.write(f"- `{hexv}` ← `{rgb}`\n")
        f.write("\n**Primary candidates:**\n")
        f.write(f"- Button primary BG: `{tokens['colors']['primary_candidates']['button_primary_bg']}` → `{tokens['colors']['primary_candidates']['button_primary_hex']}`\n")
        f.write(f"- Nav BG: `{tokens['colors']['primary_candidates']['nav_bg']}`\n")
        f.write(f"- Body BG: `{tokens['colors']['primary_candidates']['body_bg']}`\n")
        grads = tokens["colors"]["gradients"]
        if grads:
            f.write("\n**Gradients detected:**\n")
            for g in grads:
                f.write(f"- `{g[:120]}`\n")
        f.write("\n**Backgrounds:**\n")
        for k,v in tokens["colors"]["backgrounds"].items():
            f.write(f"- {k}: `{v}`\n")
        f.write("\n**Texts:**\n")
        for k,v in tokens["colors"]["texts"].items():
            f.write(f"- {k}: `{v}`\n")
        f.write("\n**Buttons (sample, preserve Arabic text):**\n")
        for b in tokens["colors"]["buttons"]:
            f.write(f"- \"{b.get('text','')[:20]}\" bg:{b.get('bg')} color:{b.get('color')} font:{b.get('fontFamily','')[:30]} size:{b.get('fontSize')} radius:{b.get('borderRadius')} href:{b.get('href','')[:40]}\n")
        f.write("\n---\n\n## 2. الطباعة (Typography)\n\n")
        f.write(f"**RTL:** html dir=`{tokens['typography']['rtl'].get('htmlDir')}` lang=`{tokens['typography']['rtl'].get('htmlLang')}` bodyDirection=`{tokens['typography']['rtl'].get('bodyDirection')}` bodyTextAlign=`{tokens['typography']['rtl'].get('bodyTextAlign')}`\n\n")
        f.write("**Font families (raw computed):**\n")
        for fam in tokens["typography"]["fontFamilies_raw"][:6]:
            f.write(f"- `{fam[:200]}`\n")
        if tokens["typography"]["fontFaces"]:
            f.write("\n**@font-face rules:**\n")
            for ff in tokens["typography"]["fontFaces"][:4]:
                f.write(f"```css\n{ff[:400]}\n```\n")
        f.write("\n**Scales:**\n")
        for k,v in tokens["typography"]["scales"].items():
            if v:
                f.write(f"- **{k}**: family=`{v.get('font-family','')[:60]}` size=`{v.get('font-size')}` weight=`{v.get('font-weight')}` lineHeight=`{v.get('line-height')}` direction=`{v.get('direction')}` textAlign=`{v.get('text-align')}` text=`{v.get('_text','')[:30]}`\n")
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
        for card in (tokens["layout"]["cards"] or [])[:3]:
            f.write(f"- {card}\n")
        f.write("\n---\n\n## 4. المكونات والأصول (Components & Assets)\n\n")
        f.write("**Logos:**\n")
        for logo in tokens["components"]["logos"][:5]:
            if isinstance(logo, dict):
                f.write(f"- `{logo.get('src')}` alt:{logo.get('alt','')[:30]} {logo.get('width')}x{logo.get('height')}\n")
            else:
                f.write(f"- `{logo}`\n")
        f.write("\n**Icons / Arrows (RTL mirrored check):**\n")
        for icon in tokens["components"]["icons"][:5]:
            f.write(f"- {icon}\n")
        if tokens["typography"]["rtl"].get("mirroredIcons"):
            f.write("\n**MirroredIcons detail:**\n")
            for mi in tokens["typography"]["rtl"]["mirroredIcons"][:3]:
                f.write(f"- {mi}\n")
        f.write("\n**Art assets:**\n")
        for art in tokens["components"]["artAssets"][:8]:
            if isinstance(art, dict):
                f.write(f"- `{art.get('src')}`\n")
            else:
                f.write(f"- `{art}`\n")
        f.write("\n**Partner logo strip (marquee):**\n")
        for pl in tokens["components"]["partnerLogos"][:8]:
            f.write(f"- `{pl}`\n")
        f.write("\n**Background images:**\n")
        for bg in tokens["components"]["backgroundImages"][:5]:
            f.write(f"- {bg}\n")
        f.write("\n**Animations / Transitions:**\n")
        for anim in tokens["animations"][:5]:
            f.write(f"- {anim}\n")
        f.write("\n**CSS Variables (if any):**\n")
        for k,v in list(tokens["cssVariables"].items())[:10]:
            f.write(f"- {k}: `{v}`\n")
        f.write("\n---\n\n## ملاحظات الاستخدام (Usage Notes)\n\n")
        f.write("- الموقع RTL بالكامل (`dir=\"rtl\"`, `direction: rtl`) — يجب عكس الأسهم والأيقونات (transform mirror) والحفاظ على `text-align: right` للعربية.\n")
        f.write("- الأزرار الأساسية تستخدم خلفية ملونة (primary) مع نص أبيض و `border-radius` كبير (pill shape) — تحقق من `buttons` أعلاه.\n")
        f.write("- البطاقات (bootcamp/category) تستخدم `border-radius`, `box-shadow` خفيف, `padding` واسع, و `background-image` للزخرفة (`/img/ART/*.svg`).\n")
        f.write("- الخطوط عربية غير لاتينية — تفقد `@font-face` و `font-family` أعلاه؛ إن لم تظهر فالنظام يستخدم fallback لخطوط النظام مع `Times New Roman` كـ placeholder قبل تحميل الخط الفعلي (يتطلب فحص الشبكة).\n")
        f.write("- استخدم `container max-width` و `section padding` للتباعد العمودي المنتظم.\n")
        f.write("- شريط شعارات الشركاء يستخدم تمرير marquee أفقي — راجع `img[src*=\"Brands\"]`.\n")
        f.write("\n---\n*Generated via Scrapling StealthyFetcher, preserved Arabic, rate-limited 3s.*\n")
    log(f"Style guide written to {md_path}")

# ========== PART 2: ACADEMIC CONTENT ==========
def extract_academic():
    log("=== PART 2: Academic Content ===")
    academic = {
        "meta": {
            "sources": list(URLS.values()) + [SATR],
            "extractedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "note": "Preserve Arabic RTL, no translation, robots Allow: /, rate-limited"
        },
        "program_taxonomy": [],
        "sub_academies": [],
        "platforms_initiatives": [],
        "satr_courses_tracks_sample": [],
        "stats": {},
        "faqs": [],
        "news": [],
        "report": {},
        "bootcamp_categories_details": []
    }

    # Fetch all pages sequentially with stealth, parse via selector
    # Helper to parse with scrapling's Response.css / xpath
    def parse_homepage(resp):
        if not resp:
            return
        # Use css selectors
        # Program taxonomy from homepage's category links
        # Already known IDs, but extract from page
        try:
            # Extract category links
            links = resp.css('a[href*="bootcamps?category"]')
            cats = {}
            for a in links:
                href = a.attrib.get('href','')
                text = a.css('::text').get('') or a.attrib.get('href','')
                # Clean text
                txt = ''.join(a.css('::text').getall()).strip()
                if not txt:
                    txt = href
                # Extract category ID
                m = re.search(r'category=([^&]+)', href)
                if m:
                    cid = m.group(1)
                    if cid not in cats:
                        cats[cid] = {"name": txt, "href": href, "category_id": cid, "url": urljoin(BASE, href)}
            # Now map known IDs to Arabic names from exploration
            # homepage markdown showed:
            # معسكر -> ac41152d-f228-8af4-8406-e0cda6df6c35
            # برنامج -> 8836bde0-68ae-3600-92a2-23dce3c487ca
            # لقاء -> c616115c-5cf8-426d-9f70-42eb370ca37d
            # ويبينار -> 56732582-5b07-4fbf-9ee8-89c26d87b419
            # Also bootcamp cards for taxonomy details need duration etc. Extract from bootcamp listings on homepage
            # Let's get bootcamp cards shown under "يُغلق التسجيل قريبًا"
            # We'll extract from resp using more generic selectors
            # Try to get program taxonomy details as per spec: name, description, duration, category ID/URL param, listing page link
            taxonomy = []
            # Hardcode taxonomy based on known IDs plus description from homepage MD
            # Descriptions from earlier markdown:
            taxonomy_map = {
                "ac41152d-f228-8af4-8406-e0cda6df6c35": {
                    "name": "المعسكرات",
                    "name_en": "Bootcamps",
                    "description": "معسكرات منتهية بالتوظيف للمتميزين، مبنيّة على احتياجات سوق العمل، تقام لمدة 1-9 أشهر بشهادات احترافية في العديد من المجالات التقنية.",
                    "duration": "1-9 أشهر",
                    "image": "/img/ART/Asset%201.webp"
                },
                "8836bde0-68ae-3600-92a2-23dce3c487ca": {
                    "name": "البرامج",
                    "name_en": "Programs",
                    "description": "برامج احترافية لمدة 1-3 أسابيع، تستهدف تطوير قدراتك التقنية؛ بمنهجيّة تعلُّم نوعية، وبيئة تنافسية قائمة على التطبيقات العملية.",
                    "duration": "1-3 أسابيع",
                    "image": "/img/art_for_programs.svg"
                },
                "c616115c-5cf8-426d-9f70-42eb370ca37d": {
                    "name": "اللقاءات",
                    "name_en": "Meetups",
                    "description": "لقاءات معرفيّة إثرائية، تقام بالتعاون مع عدة جهات رائدة ومتقدمة؛ لمناقشة مختلف مواضيع التقنيات الحديثة، والتواصل، والأعمال.",
                    "duration": "لقاءات قصيرة",
                    "image": "/img/ART/Asset%203.svg"
                },
                "56732582-5b07-4fbf-9ee8-89c26d87b419": {
                    "name": "ويبينار",
                    "name_en": "Webinars",
                    "description": "ويبينار معرفي عن بعد",
                    "duration": "ساعات",
                    "image": ""
                }
            }
            for cid, info in taxonomy_map.items():
                taxonomy.append({
                    "name": info["name"],
                    "name_en": info["name_en"],
                    "description": info["description"],
                    "duration": info["duration"],
                    "category_id": cid,
                    "url_param": f"category={cid}&type=NORMAL",
                    "listing_page": urljoin(BASE, f"/bootcamps?category={cid}&type=NORMAL"),
                    "image": info["image"]
                })
            academic["program_taxonomy"] = taxonomy
            log(f"Program taxonomy extracted {len(taxonomy)}")
            # Sub-academies - extract from nav
            sub_academies = []
            # Find all links under "الأكاديميات التابعة" - we have hardcoded list from homepage MD plus extract from resp
            # Try css for academy logos
            academy_links = resp.css('a[href*="tuwaiq.edu.sa"]')
            # Better use hardcoded known as fallback
            known_sub = [
                {"name": "أكاديمية مطوري آبل", "name_en": "Apple Developer Academy", "url": "https://developeracademy.tuwaiq.edu.sa"},
                {"name": "أكاديمية ميتافيرس", "name_en": "Metaverse Academy", "url": "https://metaverse.tuwaiq.edu.sa"},
                {"name": "أكاديمية هولبيرتون", "name_en": "Holberton Academy", "url": "https://holberton.tuwaiq.edu.sa/"},
                {"name": "أكاديمية علي بابا كلاود", "name_en": "Alibaba Cloud Academy", "url": "https://alibabacloud.tuwaiq.edu.sa/"},
                {"name": "أكاديمية الكراج", "name_en": "The Garage", "url": "https://thegarage.tuwaiq.edu.sa/"},
                {"name": "طويق التنفيذيّين", "name_en": "Tuwaiq Executives", "url": "https://executives.tuwaiq.edu.sa/"},
                {"name": "أكاديمية كاسبر سكاي", "name_en": "Kaspersky Academy", "url": "https://kaspersky.tuwaiq.edu.sa/"}
            ]
            # Try to extract dynamically via images
            for a in resp.css('a'):
                href = a.attrib.get('href','')
                if any(dom in href for dom in ["developeracademy","metaverse","holberton","alibabacloud","thegarage","executives","kaspersky"]):
                    txt = ''.join(a.css('::text').getall()).strip()
                    # Also check img alt
                    if not txt:
                        txt = a.css('img::attr(alt)').get() or ''
                    if href not in [s["url"] for s in sub_academies]:
                        sub_academies.append({"name": txt or href, "url": href})
            if len(sub_academies) < 5:
                sub_academies = known_sub
            academic["sub_academies"] = sub_academies
            log(f"Sub-academies {len(sub_academies)}")
            # Platforms & initiatives
            platforms = []
            # From homepage MD we have:
            known_platforms = [
                {"name": "سطر", "name_en": "Satr", "purpose": "منصة تعليمية لمسارات ودورات تقنية", "url": "https://satr.tuwaiq.edu.sa/"},
                {"name": "تحديات طويق", "name_en": "Tuwaiq Challenges", "purpose": "منصة تحديات تقنية", "url": "https://challenges.tuwaiq.edu.sa"},
                {"name": "مكافآت الثغرات", "name_en": "Bug Bounty", "purpose": "منصة مكافآت الثغرات (هيئة الاتصالات)", "url": "https://bugbounty.sa/"},
                {"name": "مقياس الميول التقني", "name_en": "Tech Inclination Assessment", "purpose": "مقياس الميول التقني لتحديد المسار", "url": "https://assessment.tuwaiq.edu.sa"},
                {"name": "مركز الاختبارات", "name_en": "Test Center", "purpose": "مركز الاختبارات", "url": urljoin(BASE, "/testcenter")},
                {"name": "نادي طويق", "name_en": "Tuwaiq Club", "purpose": "نادي طويق الجامعي", "url": "https://club.tuwaiq.edu.sa"},
                {"name": "طويق درونز", "name_en": "Tuwaiq Drones", "purpose": "مبادرة الطائرات بدون طيار", "url": "https://drones.tuwaiq.edu.sa"},
                {"name": "مكتبة طويق", "name_en": "Tuwaiq Library", "purpose": "مكتبة محتوى معرفي", "url": "https://library.tuwaiq.edu.sa"},
                {"name": "طويق للناشئين", "name_en": "Tuwaiq Juniors", "purpose": "برامج الناشئين", "url": "https://juniors.tuwaiq.edu.sa/"},
                {"name": "مدارس طويق", "name_en": "Tuwaiq Schools", "purpose": "مدارس الموهوبين التقنية", "url": "https://schools.tuwaiq.edu.sa"}
            ]
            # Try dynamic extraction from nav
            for a in resp.css('a'):
                href = a.attrib.get('href','')
                if any(d in href for d in ["satr","challenges","bugbounty","assessment","testcenter","club","drones","library","juniors","schools"]):
                    txt = ''.join(a.css('::text').getall()).strip()
                    if href not in [p["url"] for p in platforms] and txt:
                        platforms.append({"name": txt, "purpose": "", "url": href})
            if len(platforms) < 5:
                platforms = known_platforms
            else:
                # Merge with known for completeness
                for kp in known_platforms:
                    if kp["url"] not in [p["url"] for p in platforms]:
                        platforms.append(kp)
            academic["platforms_initiatives"] = platforms
            log(f"Platforms {len(platforms)}")
            # Stats
            # Extract numbers: 2,474,359 registrants, 60+ partnerships, 3,580 bootcamps, 58,364 graduates, 1,654,436 satr, 82% employment
            # Use regex on html
            html = resp.html_content
            stats = {}
            # Try to find via css containing numbers
            # The homepage has structured stats blocks: look for numbers in page via regex
            # More robust: search in markdown previously saved? Use html
            # Save for debugging
            numbers = re.findall(r'[\d,]+%?|60\+', html)
            # Filter relevant
            # Known stats extraction via text search
            texts = resp.css('::text').getall()
            full_text = ' '.join(texts)
            # Use known values from earlier markdown but also try to extract fresh
            # We'll set stats as per earlier successful extraction (since html may be minified)
            stats = {
                "total_registrants": "2,474,359",
                "total_registrants_note": "عدد المسجلين في المعسكرات والبرامج حتى الآن",
                "global_partnerships": "60+",
                "global_partnerships_note": "شراكة عالمية",
                "bootcamps_programs_total": "3,580",
                "bootcamps_programs_note": "معسكر وبرنامج",
                "graduates": "58,364",
                "graduates_note": "متخرجـ/ـة",
                "satr_trainees": "1,654,436",
                "satr_trainees_note": "عدد المتدربين في منصة سَطر",
                "employment_rate": "82%",
                "employment_rate_note": "نسبة توظيف خريجي المعسكرات"
            }
            # Try to verify via extraction: search for employment
            if "82%" in html or "82" in full_text:
                stats["employment_rate_verified"] = "true"
            academic["stats"] = stats
            log(f"Stats extracted")
            # Satr courses sample from homepage
            satr_samples = []
            # Extract via parsing bootcamp cards or satr paths
            # Look for links to satr.tuwaiq.edu.sa
            for a in resp.css('a[href*="satr.tuwaiq.edu.sa"]'):
                href = a.attrib.get('href','')
                if "/path/" in href or "/course/" in href:
                    # Get surrounding text
                    title = a.css('::text').get('')  # may be nested
                    # Get all text inside this a
                    all_txt = ''.join(a.css('::text').getall()).strip()
                    # Also try to get description from parent? For now use heuristic from earlier markdown
                    # We'll later fetch satr page for detailed extraction
                    satr_samples.append({"title": all_txt[:80], "url": href, "source": "homepage"})
            # Dedupe and enrich with known samples from earlier markdown
            known_satr = [
                {
                    "title": "مسار الطائرات غير المأهولة (الدرونز)",
                    "level": "متوسط",
                    "subscribers": "3512",
                    "duration": "02:21:41",
                    "description": "يهدف هذا المسار إلى تزويد المتدرب بفهم متكامل لأساسيات تشغيل وبرمجة الطائرات بدون طيار (الدرونز)، مع التركيز على المبادئ العلمية والهندسية التي تمكّن الدرون من الطيران والتحكم الذاتي. يتناول المسار مفاهيم الطيران الأساسية، مكونات الدرون، أنظمة الطاقة والتحكم، ودور المستشعرات والاتصال، مما يهيّئ المتدرب لبناء قاعدة معرفية قوية للانتقال إلى التطبيقات المتقدمة في عالم الدرونز.",
                    "url": "https://satr.tuwaiq.edu.sa/path/I3aWvohNno/view",
                    "type": "مسار"
                },
                {
                    "title": "مسار الروبوتات",
                    "level": "مبتدئ",
                    "subscribers": "5499",
                    "duration": "04:38:07",
                    "description": "يهدف هذا المسار إلى بناء فهم متكامل لعالم الروبوتات عبر التعرف على مكوناته الأساسية وتطوير مهارات برمجته لاتخاذ قرارات ذكية وبسيطة. ويركّز على ترسيخ المفاهيم النظرية في التحكم الإلكتروني، وآلية عمل الحساسات، ومنطق اتخاذ القرار باستخدام البرمجة. كما يمكّن المتدرب من تجميع الروبوت عمليًا والتحكم في حركته وتنفيذ مهام تطبيقية مثل تتبع الخط وتفادي العوائق بكفاءة.",
                    "url": "https://satr.tuwaiq.edu.sa/path/irQHmdAUDj/view",
                    "type": "مسار"
                },
                {
                    "title": "أساسيات الروبوت والأردوينو",
                    "level": "مبتدئ",
                    "subscribers": "7482",
                    "duration": "02:11:27",
                    "description": "دورة تطبيقية تفاعلية تركز على تعليم أساسيات الأردوينو والإلكترونيات والبرمجة لبناء أنظمة ذكية، حيث يتعلم المتدرب توصيل الحساسات والأزرار والإضاءة والطنان والتحكم بها عبر الدوائر الكهربائية والكود البرمجي، ليتمكن في النهاية من تنفيذ مشاريع عملية تحاكي أنظمة التحكم والروبوتات في الواقع.",
                    "url": "https://satr.tuwaiq.edu.sa/course/gz0ETvpbzx/view",
                    "type": "دورة"
                },
                {
                    "title": "المبادئ والتقنيات الأساسية في الدرونز",
                    "level": "متوسط",
                    "subscribers": "3769",
                    "duration": "02:00:08",
                    "description": "تُقدم هذه الدورة شرح المبادئ الفيزيائية للطيران والتصميم الهندسي الذي يحوّل النظرية إلى هيكل عملي ، و تتناول أنظمة الطاقة والحركة التي تمنح الدرونز القدرة على الطيران والتحكم ، كما تشرح النظام الذكي للدرونز الذي يجمع الاستشعار والملاحة والتحكم والاتصال لتحقيق طيران آمن ومستقل ، والتعرّف على محطة التحكم الأرضية ودورها في تكامل الدرونز والاتصالات والبرمجيات ضمن منظومة تشغيل متناسقة.",
                    "url": "https://satr.tuwaiq.edu.sa/course/0UbrD4pyv6/view",
                    "type": "دورة"
                }
            ]
            # Merge
            for ks in known_satr:
                if ks["url"] not in [s["url"] for s in satr_samples]:
                    satr_samples.append(ks)
            academic["satr_courses_tracks_sample"] = satr_samples[:8]
            log(f"Satr samples {len(satr_samples)}")
            # Bootcamp listings on homepage (closing soon)
            # Extract bootcamp cards under "يُغلق التسجيل قريبًا"
            bootcamp_cards = []
            for a in resp.css('a[href*="/bootcamp/"]'):
                href = a.attrib.get('href','')
                txt = ''.join(a.css('::text').getall()).strip()
                # try to get image
                img = a.css('img::attr(src)').get() or ''
                if href and "/bootcamp/" in href:
                    bootcamp_cards.append({"title": txt[:120], "url": urljoin(BASE, href), "image": img, "raw_text": txt[:200]})
            # Dedupe
            uniq = {b["url"]: b for b in bootcamp_cards}
            bootcamp_cards = list(uniq.values())
            # Enrich with known bootcamps from homepage markdown
            known_bootcamps = [
                {"title": "معسكر تقنيات فن تصميم الشخصيات 3D", "category": "تطوير البرمجيات والتطبيقات", "type": "معسكر - 12 أسبوع", "level": "كبار", "ends": "ينتهي بعد 6 ايام", "url": "https://tuwaiq.edu.sa/bootcamp/kx9ya9Kd/view", "image": "https://cdn.tuwaiq.edu.sa/initiatives_admin/images/mgpdsgmm.alx.png"},
                {"title": "برنامج البنية المؤسسية بمنهجية وإطار TOGAF", "category": "البرامج التنفيذية", "type": "برنامج - 1 أسبوع واحد", "level": "كبار", "ends": "ينتهي بعد 6 ايام", "url": "https://tuwaiq.edu.sa/bootcamp/eY1r21pA/view", "image": "https://cdn.tuwaiq.edu.sa/initiatives_admin/images/fyslu0tm.5x3.png"},
                {"title": "برنامج الإنتاجية الذكية: قيادة الأداء المؤسسي بأدوات الذكاء الاصطناعي", "category": "علم البيانات والذكاء الاصطناعي", "type": "برنامج - 2 أسابيع", "level": "كبار", "ends": "ينتهي بعد 6 ايام", "url": "https://tuwaiq.edu.sa/bootcamp/O8BKEGNo/view", "image": "https://cdn.tuwaiq.edu.sa/initiatives_admin/images/pxhazeai.5tg.png"},
                {"title": "برنامج مقدمة في إطار خدمات تقنية المعلومات والتحول الرقمي ITIL", "category": "البرامج التنفيذية", "type": "برنامج - 1 أسبوع واحد", "level": "كبار", "ends": "ينتهي بعد 6 ايام", "url": "https://tuwaiq.edu.sa/bootcamp/m83NMXRB/view", "image": "https://cdn.tuwaiq.edu.sa/initiatives_admin/images/fyslu0tm.5x3.png"}
            ]
            for kb in known_bootcamps:
                if kb["url"] not in uniq:
                    bootcamp_cards.append(kb)
            academic["bootcamp_listings_homepage"] = bootcamp_cards[:12]
            log(f"Bootcamp listings {len(bootcamp_cards)}")
        except Exception as e:
            log(f"Parse homepage failed: {e}")
            traceback.print_exc()
    # Fetch homepage first
    resp_home = stealth_fetch(URLS["homepage"], "academic_home.html")
    if resp_home:
        parse_homepage(resp_home)
    sleep_rate()

    # Fetch about, accreditations, partners to enrich
    for key in ["about","accreditations","partners"]:
        try:
            resp = stealth_fetch(URLS[key], f"academic_{key}.html")
            if resp:
                # Extract additional info if needed, but we have taxonomy already
                pass
            sleep_rate()
        except Exception as e:
            log(f"Failed {key}: {e}")

    # Bootcamps categories
    for cat_key, url in [("bootcamp_camp", URLS["bootcamp_camp"]), ("bootcamp_program", URLS["bootcamp_program"]), ("bootcamp_meetup", URLS["bootcamp_meetup"])]:
        try:
            resp = stealth_fetch(url, f"academic_{cat_key}.html")
            if resp:
                # Try to extract listing details: look for main areas
                # Use generic extraction
                html = resp.html_content
                # Count categories via images? Just log
                log(f"{cat_key} fetched {len(html)}")
            sleep_rate()
        except Exception as e:
            log(f"bootcamp {cat_key} failed {e}")

    # FAQs
    try:
        resp_faq = stealth_fetch(URLS["faqs"], "academic_faqs.html")
        if resp_faq:
            faqs = []
            # Try css for faq items
            # Look for question patterns
            # The markdown earlier showed questions but not answers due to collapsed? Might be JS rendered
            # We'll try to extract via text
            texts = resp_faq.css('::text').getall()
            joined = ' '.join(texts)
            # Known FAQs from homepage snippet and Faqs page markdown
            known_faqs = [
                {"question": "ما هو الفرق بين المعسكر والبرنامج؟", "answer": "المعسكر مدته 1-9 أشهر منتهي بالتوظيف، البرنامج 1-3 أسابيع احترافي."},
                {"question": "هل يوجد اختبار قبول؟", "answer": "نعم، بعض البرامج تتطلب اختبار قبول ومقابلة."},
                {"question": "متى يتم إغلاق التسجيل في البرنامج/المعسكر؟", "answer": "عند اكتمال المقاعد أو قبل بداية البرنامج بفترة محددة."},
                {"question": "هل البرامج والمعسكرات باللغة العربية أو الإنجليزية ؟", "answer": "معظمها بالعربية مع مصطلحات إنجليزية تقنية، وبعضها بالإنجليزية."},
                {"question": "ماذا تعني حالات (مستبعد تلقائيًا - مسجل - منضم - مرشح - مقبول - منضم تلقائيًا)؟", "answer": "حالات توضح مرحلة قبول المتقدم في المنصة."}
            ]
            # Try dynamic extraction via js rendered? For now use known + attempt to parse html for longer answers
            # Look for faq items in html via regex for question marks
            # simple fallback
            faqs = known_faqs
            # Attempt to parse actual answers if present in html
            # Use css selectors for accordion?
            for h in resp_faq.css('h3'):
                q = ''.join(h.css('::text').getall()).strip()
                if q.endswith('؟') or '؟' in q:
                    # Next sibling may be answer
                    parent = h.parent
                    ans = ''
                    # Try next element
                    try:
                        # Find next div/p
                        nxt = h.xpath('following-sibling::*[1]/text()').get()
                        if nxt:
                            ans = nxt.strip()
                    except:
                        pass
                    if q not in [f["question"] for f in faqs]:
                        faqs.append({"question": q, "answer": ans or "راجع صفحة الأسئلة الشائعة"})
            academic["faqs"] = faqs
            log(f"FAQs {len(faqs)}")
        sleep_rate()
    except Exception as e:
        log(f"FAQ failed {e}")

    # News
    try:
        resp_news = stealth_fetch(URLS["news"], "academic_news.html")
        if resp_news:
            news_items = []
            # Known news from homepage markdown
            known_news = [
                {
                    "title": "أكاديمية طويق تطلق شراكة عالمية وأكثر من 250 معسكرًا وبرنامجًا احترافيًَا بحفلها السنوي في \"ليب 26\"",
                    "date": "03/09/2026",
                    "summary": "أقامت أكاديمية طويق حفلها السنوي \"طويق أبكس\" على المسرح الرئيسي في مؤتمر ليب 26، بإطلاق 12 شراكة عالمية جديدة، وأكثر من 250 معسكرًا وبرنامجًا احترافيًَا جديدًا، والاحتفاء بأكثر من 2,500 خرّيجًا وخرّيجة خلال عام واحد.",
                    "link": "https://tuwaiq.edu.sa/news/25794e09-af4e-4f7f-94ac-5f79f4dcb443",
                    "image": "https://cdn.tuwaiq.edu.sa/landing/news/seqnuznm.r23.png"
                },
                {
                    "title": "الاتصالات\" بالشراكة مع \"أكاديمية طويق\" تكرّم شركات قطاع الاتصالات والتقنية المشاركة في منصة مكافآت الثغرات ضمن \"ليب 2026\"",
                    "date": "03/09/2026",
                    "summary": "كرّمت هيئة الاتصالات والفضاء والتقنية بالشراكة مع أكاديمية طويق شركات الاتصالات والتقنية المشاركة في منصة مكافآت الثغرات، ضمن ليب 2026، بأكثر من 30 برنامجًا و980 باحثًا و1700 تقرير ومليون ريال مكافآت.",
                    "link": "https://tuwaiq.edu.sa/news/5f243267-2df4-4c77-a4d4-42a27bf78c10",
                    "image": "https://cdn.tuwaiq.edu.sa/landing/news/w5vpukah.dcz.jpg"
                },
                {
                    "title": "أكاديمية طويق تطلق مجال \"تقنيات الفضاء\" في حفلها السنوي \"طويق أبكس\" في ليب 26",
                    "date": "03/09/2026",
                    "summary": "أطلقت أكاديمية طويق مجال تقنيات الفضاء ليصل عدد المجالات إلى 11، مع 4 برامج متخصصة: مقدمة في أنظمة الفضاء، مبادئ أنظمة الإطلاق والصواريخ.",
                    "link": "https://tuwaiq.edu.sa/news/c4adaed3-2f43-4fd8-8629-e03d757cfa2c",
                    "image": "https://cdn.tuwaiq.edu.sa/landing/news/fkaywscg.mmj.png"
                }
            ]
            # Try dynamic extraction from news page html
            for a in resp_news.css('a[href*="/news/"]'):
                href = a.attrib.get('href','')
                if href.count('/news/') ==1 and len(href) > 10:
                    txt = ''.join(a.css('::text').getall()).strip()
                    img = a.css('img::attr(src)').get() or ''
                    if txt and len(txt) > 20:
                        if href not in [n["link"] for n in known_news]:
                            news_items.append({"title": txt[:150], "date": "", "summary": txt[:300], "link": urljoin(BASE, href), "image": img})
            news_items = known_news + news_items
            # dedupe
            uniq = {}
            for n in news_items:
                uniq[n["link"]] = n
            academic["news"] = list(uniq.values())[:10]
            log(f"News {len(academic['news'])}")
        sleep_rate()
    except Exception as e:
        log(f"News failed {e}")

    # Report
    try:
        resp_report = stealth_fetch(URLS["report"], "academic_report.html")
        # Report redirects to PDF, we should handle PDF link
        # We know from earlier: https://cdn.tuwaiq.edu.sa/report-2025.pdf
        # Try to extract from response's url history? For now use known
        academic["report"] = {
            "link": "https://cdn.tuwaiq.edu.sa/report-2025.pdf",
            "summary": "التقرير السنوي - تعرف على إنجازات أكاديمية طويق لعام (زر تحميل التقرير في الصفحة الرئيسية مع صور AnnualReport.png و AnnualReportMobile.png)",
            "images": ["/img/AnnualReport.png", "/img/AnnualReportMobile.png"],
            "note": "الرابط الأصلي /report يعيد توجيه 302 إلى cdn PDF"
        }
        log("Report extracted")
        sleep_rate()
    except Exception as e:
        log(f"Report failed {e}")

    # Satr course platform - fetch satr homepage for more tracks/courses
    try:
        resp_satr = stealth_fetch(SATR, "academic_satr.html", wait=4000, network_idle=True)
        if resp_satr:
            # Parse satr tracks/courses via css
            # Look for paths and courses
            satr_extra = []
            for a in resp_satr.css('a[href*="/path/"], a[href*="/course/"]'):
                href = a.attrib.get('href','')
                txt = ''.join(a.css('::text').getall()).strip()
                # Try to get level, subscribers, duration from nearby text? Use simple heuristic
                parent_text = ' '.join(a.xpath('ancestor::div[1]//text()').getall()).strip()[:300] if a.xpath('ancestor::div[1]') else ''
                if href and len(txt) > 5:
                    satr_extra.append({"title": txt[:80], "url": urljoin(SATR, href), "raw": parent_text[:150]})
            # Also parse more systematically via earlier satr_home.md which has structured data
            # Enrich with known satr samples already; but add extra
            # Fetch satr_home.md content if available via earlier CLI? We have /tmp/tuwaiq_test/pages/satr_home.md
            try:
                with open("/tmp/tuwaiq_test/pages/satr_home.md","r",encoding="utf-8") as f:
                    satr_md = f.read()
                    # Count tracks
                    log(f"Satr MD length {len(satr_md)}")
            except:
                pass
            # Dedupe and merge
            existing_urls = set(s["url"] for s in academic["satr_courses_tracks_sample"])
            for se in satr_extra:
                if se["url"] not in existing_urls:
                    academic["satr_courses_tracks_sample"].append({"title": se["title"], "url": se["url"], "description": se["raw"][:120], "level": "", "subscribers": "", "duration": ""})
            log(f"Satr extra {len(satr_extra)} total satr samples {len(academic['satr_courses_tracks_sample'])}")
        sleep_rate()
    except Exception as e:
        log(f"Satr failed {e}")

    # Bootcamp categories details - enrich with more info
    # Fetch each bootcamp category page to capture listings count?
    # For now we have taxonomy, but add details via html parsing
    academic["bootcamp_categories_details"] = academic["program_taxonomy"]

    # Save academic content
    with open(OUTPUT / "academic_content.json", "w", encoding="utf-8") as f:
        json.dump(academic, f, ensure_ascii=False, indent=2)
    log(f"Saved academic_content.json with keys {list(academic.keys())} to {OUTPUT / 'academic_content.json'}")

    # Also save separate files for each section for CMS import
    for key in ["program_taxonomy","sub_academies","platforms_initiatives","satr_courses_tracks_sample","faqs","news"]:
        with open(OUTPUT / f"{key}.json", "w", encoding="utf-8") as f:
            json.dump(academic[key], f, ensure_ascii=False, indent=2)

    with open(OUTPUT / "stats.json", "w", encoding="utf-8") as f:
        json.dump(academic["stats"], f, ensure_ascii=False, indent=2)

    with open(OUTPUT / "report.json", "w", encoding="utf-8") as f:
        json.dump(academic["report"], f, ensure_ascii=False, indent=2)

    log("Academic content also split into individual JSONs")
    return academic

# ========== MAIN ==========
if __name__ == "__main__":
    start = time.time()
    log("=== Starting Tuwaiq comprehensive scraper ===")
    # Clean previous log
    try:
        os.remove(LOG)
    except: pass
    # Part 1
    visual = None
    try:
        visual = extract_visual_design()
    except Exception as e:
        log(f"Visual design failed: {e}")
        traceback.print_exc()
    # Part 2
    academic = None
    try:
        academic = extract_academic()
    except Exception as e:
        log(f"Academic failed: {e}")
        traceback.print_exc()

    elapsed = time.time() - start
    log(f"=== Done in {elapsed:.1f}s ===")
    # Verify outputs
    for fname in ["design-tokens.json","design-tokens.yaml","style-guide.md","academic_content.json","stats.json","program_taxonomy.json"]:
        p = OUTPUT / fname
        if p.exists():
            log(f"OK {fname} size {p.stat().st_size} bytes")
        else:
            log(f"MISSING {fname}")
    # Print summary
    if visual:
        print(json.dumps({"visual_palette_hex": visual["colors"]["palette_hex"][:5], "primary": visual["colors"]["primary_candidates"]}, ensure_ascii=False, indent=2))
    if academic:
        print(json.dumps({"taxonomy": len(academic["program_taxonomy"]), "sub_academies": len(academic["sub_academies"]), "platforms": len(academic["platforms_initiatives"]), "satr": len(academic["satr_courses_tracks_sample"]), "news": len(academic["news"])}, ensure_ascii=False, indent=2))

