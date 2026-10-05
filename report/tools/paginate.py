"""Find the printed page label of every TOC / figure / table entry in a rendered PDF."""

import re
import subprocess

ROMAN = re.compile(r"^(?=[ivxlc]+$)c{0,3}(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$")


def _norm(text: str) -> str:
    text = text.replace("’", "'").replace("–", "-").replace("—", "-").replace(" ", " ")
    return re.sub(r"\s+", " ", text).strip()  # case-sensitive: chapter titles are upper case


def page_texts(pdf: str) -> list[str]:
    out = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
    return out.split("\f")[:-1] if out.endswith("\f") else out.split("\f")


def page_label(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return ""
    last = lines[-1]
    return last if last.isdigit() or ROMAN.match(last) else ""


def locate(pdf: str, entries: list[tuple[str, int, str]]) -> dict[str, list[str]]:
    texts = page_texts(pdf)
    normed = [_norm(t) for t in texts]
    labels = [page_label(t) for t in texts]
    # Pages that are themselves indexes (many dot leaders) must not match entries.
    skip = {i for i, t in enumerate(texts) if t.count("....") >= 4}

    result: dict[str, list[str]] = {"toc": [], "Figure": [], "Table": []}
    cursor = {"toc": 0, "Figure": 0, "Table": 0}
    for kind, _level, text in entries:
        needle = _norm(text)
        found = None
        for i in range(cursor[kind], len(texts)):
            if i in skip and not normed[i].startswith(needle):  # an index page may match its own title
                continue
            if needle in normed[i]:
                found = i
                break
        if found is None:
            result[kind].append("?")
            continue
        cursor[kind] = found
        result[kind].append(labels[found] or "?")
    return result
