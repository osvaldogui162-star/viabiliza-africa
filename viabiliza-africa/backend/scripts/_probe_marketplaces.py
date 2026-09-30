from app.infrastructure.scraping.http_utils import fetch_html
import re

html = fetch_html("https://kikoloonline.com/?s=gerador", timeout=20)
open("scripts/_kikolo.html", "w", encoding="utf-8").write(html[:100000])
for pat in [
    r"product/[a-f0-9]{10,}",
    r"\d[\d.,]*\s*KZ",
    r'href="(/product[^"]+)"',
    r'"price"\s*:\s*(\d+)',
    r'"name"\s*:\s*"([^"]{5,80})"',
]:
    ms = re.findall(pat, html, re.I)
    print(pat, "=>", len(ms), ms[:8])

# socia
try:
    s = fetch_html("https://socia.ao/busca?q=cimento", timeout=15)
    open("scripts/_socia.html", "w", encoding="utf-8").write(s[:50000])
    print("socia len", len(s))
    print("socia api hints", re.findall(r"/api/[^\"'\s]+", s)[:10])
except Exception as e:
    print("socia fail", e)
