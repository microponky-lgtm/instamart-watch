import json
from urllib.parse import quote
from playwright.sync_api import sync_playwright

LAT, LNG = 28.4595, 77.0266  # rough Gurgaon centre, test only
QUERY = "POCO M8 Power"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        geolocation={"latitude": LAT, "longitude": LNG},
        permissions=["geolocation"],
        locale="en-IN",
        timezone_id="Asia/Kolkata",
        viewport={"width": 1280, "height": 900},
    )
    loc = json.dumps({"lat": LAT, "lng": LNG, "address": "",
                      "area": "", "showUserDefaultAddressHint": False})
    base = "https://www.swiggy.com"
    ctx.add_cookies([
        {"name": "lat", "value": str(LAT), "url": base},
        {"name": "lng", "value": str(LNG), "url": base},
        {"name": "userLocation", "value": quote(loc), "url": base},
    ])
    page = ctx.new_page()
    seen = []
    page.on("response", lambda r: seen.append(r)
            if "/api/instamart/" in r.url else None)

    page.goto(base + "/instamart", wait_until="domcontentloaded",
              timeout=60000)
    page.wait_for_timeout(8000)
    page.goto(base + "/instamart/search?custom_back=true&query="
              + quote(QUERY), wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(8000)

    print("TITLE:", page.title())
    print("URL:", page.url)
    for r in seen:
        print("API", r.status, r.url[:140])
        if "search" in r.url:
            try:
                print("BODY:", r.text()[:1200])
            except Exception as e:
                print("BODY ERROR:", e)
    print("PAGE TEXT:", page.inner_text("body")[:1200])
    browser.close()
