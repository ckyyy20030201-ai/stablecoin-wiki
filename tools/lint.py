"""Wiki Lint：檢查斷鏈、缺來源、index 漏列。用法：python tools/lint.py"""
import re, pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent / "wiki"
pages = {p.relative_to(root).with_suffix("").as_posix() for p in root.rglob("*.md")}
problems = []
for p in sorted(root.rglob("*.md")):
    name = p.relative_to(root).with_suffix("").as_posix()
    text = p.read_text(encoding="utf-8")
    for link in re.findall(r"\[\[([^\]]+)\]\]", text):
        if link not in pages:
            problems.append(f"[斷鏈] {name} → [[{link}]]")
    if name == "index" or name.startswith("sources/"):
        continue
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        is_fact = s.startswith(("- ", "1.", "2.", "3.", "4.", "5.", "6.", "**一句話")) and len(s) > 25
        # v3：只有「→ 見 [[」或「→ [[」這種導覽句才豁免，單純含「→」不再豁免；白話句須標「（白話說明）」
        is_nav = "→ 見 [[" in s or "→ [[" in s or "見 [[" in s
        if is_fact and "來源：" not in s and not is_nav and "（白話說明" not in s:
            problems.append(f"[缺來源] {name}:{i} {s[:40]}")
    # v2：表格列不會被上面的規則檢查到 → 規定有表格的頁面，表格後 3 行內必須有來源標註
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("|") and (i + 1 == len(lines) or not lines[i + 1].startswith("|")):
            after = "\n".join(lines[i + 1:i + 4])
            if "來源：" not in after:
                problems.append(f"[表格缺來源] {name}:{i+1}")
    # v4：表格每列欄數必須和表頭一致
    header_cols = None
    for i, line in enumerate(lines):
        if line.startswith("|"):
            n = line.strip().strip("|").count("|") + 1
            if header_cols is None:
                header_cols = n
            elif n != header_cols:
                problems.append(f"[表格欄數不符] {name}:{i+1} 應為 {header_cols} 欄，實際 {n} 欄")
        else:
            header_cols = None
index = (root / "index.md").read_text(encoding="utf-8")
for pg in pages - {"index"}:
    if f"[[{pg}]]" not in index:
        problems.append(f"[index 漏列] {pg}")
print("\n".join(problems) if problems else "Lint 通過：0 個問題")
print(f"共檢查 {len(pages)} 頁")
