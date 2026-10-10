import json
from urllib.parse import quote
from playwright.sync_api import sync_playwright

LAT, LNG = 28.4595, 77.0266
QUERY = "POCO M8 Power"
BASE = "https://www.swiggy.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")


def variant(p, name, url, use_ua, use_cookies):
    print("\n===== VARIANT:", name, "=====")
    browser = p.chromium.launch(headless=True)
    opts = dict(locale="en-IN", timezone_id="Asia/Kolkata",
                viewport={"width": 1280, "height": 900})
    if use_ua:
        opts["user_agent"] = UA
    ctx = browser.new_context(**opts)
    if use_cookies:
        loc = json.dumps({"lat": LAT, "lng": LNG, "address": "",
                          "area": "", "showUserDefaultAddressHint": False})
        ctx.add_cookies([
            {"name": "lat", "value": str(LAT), "url": BASE},
            {"name": "lng", "value": str(LNG), "url": BASE},
            {"name": "userLocation", "value": quote(loc), "url": BASE},
        ])
    page = ctx.new_page()
    seen = []
    page.on("response", lambda r: seen.append(r)
            if "swiggy.com" in r.url and
            ("/api/" in r.url or r.status >= 400) else None)
    try:
        resp = page.goto(url, wait_until="domcontentloaded",
                         timeout=60000)
        print("MAIN STATUS:", resp.status if resp else None)
    except Exception as e:
        print("GOTO ERROR:", e)
    page.wait_for_timeout(8000)
    print("TITLE:", page.title())
    for r in seen[:15]:
        print("  ", r.status, r.url[:120])
    txt = page.inner_text("body")[:300].replace("\n", " | ")
    print("TEXT:", txt)
    browser.close()


with sync_playwright() as p:
    try:
        b = p.chromium.launch(headless=True)
        r = b.new_context().request.get("https://ipinfo.io/json")
        print("RUNNER IP INFO:", r.text()[:300])
        b.close()
    except Exception as e:
        print("IP CHECK ERROR:", e)

    home = BASE + "/instamart"
    search = BASE + "/instamart/search?custom_back=true&query=" + quote(QUERY)
    variant(p, "1 plain", home, False, False)
    variant(p, "2 normal-browser-name", home, True, False)
    variant(p, "3 normal-browser-name + location", search, True, True)
