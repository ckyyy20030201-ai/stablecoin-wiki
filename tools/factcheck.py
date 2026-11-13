"""簡報事實檢查：每張投影片的 data-src 必須是存在的 wiki 頁；投影片上的每個數字／日期都必須出現在它引用的 wiki 頁中。
用法：python tools/factcheck.py"""
import re, pathlib, html
base = pathlib.Path(__file__).resolve().parent.parent
wiki = base / "wiki"
src = (base / "slides/index.html").read_text(encoding="utf-8")
sections = re.findall(r'<section class="slide[^"]*" data-src="([^"]+)">(.*?)</section>', src, re.S)
problems = []
for n, (refs, body) in enumerate(sections, 1):
    pages = []
    for r in refs.split():
        f = wiki / f"{r}.md"
        if not f.exists():
            problems.append(f"[第{n}頁] 引用不存在的 wiki 頁：{r}")
        else:
            pages.append(f.read_text(encoding="utf-8"))
    ref_text = "\n".join(pages).replace(",", "")
    text = html.unescape(re.sub(r"<[^>]+>", " ", body))
    text = re.sub(r'class="[^"]*"', "", text).replace(",", "")
    # 抓數字（含日期、百分比、小數）；排除投影片自身的編號用字
    for num in set(re.findall(r"\d+(?:[.\-]\d+)*%?", text)):
        if num in {"1", "2", "3"} and n in (4, 5, 15):   # 步驟／題號編號
            continue
        if num not in ref_text:
            problems.append(f"[第{n}頁] 數字「{num}」在引用的 wiki 頁找不到（引用：{refs}）")
print("\n".join(problems) if problems else "事實檢查通過：所有數字都能對回 wiki")
print(f"共檢查 {len(sections)} 張投影片")
