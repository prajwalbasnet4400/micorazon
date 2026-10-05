"""Build the final project report (LibreOffice .odt) in the prescribed Project III format.

    uv run python report/tools/make_charts.py      # charts + equations (after retraining)
    plantuml -tpng -Sdpi=200 -o ../figures/generated report/diagrams/*.puml
    uv run python report/build_report.py

Pipeline: python-docx builds the document; LibreOffice renders it to PDF to find the page of every
heading, figure and table; the document is rebuilt with those page numbers in its (live) index fields
until pagination is stable; LibreOffice then converts it to native .odt.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "tools"))
sys.path.insert(0, str(HERE))

from content.chapter3 import chapter3  # noqa: E402
from content.chapters_1_2 import chapter1, chapter2  # noqa: E402
from content.chapters_4_5 import back_matter, chapter4, chapter5  # noqa: E402
from content.common import Citations  # noqa: E402
from content.front import front_matter  # noqa: E402
from docx_kit import Report  # noqa: E402
from paginate import locate  # noqa: E402

SOFFICE = shutil.which("soffice") or "/Applications/LibreOffice.app/Contents/MacOS/soffice"
OUT = HERE / "output"
NAME = "HFP_Final_Report"


def build(index_pages, labels):
    cite = Citations(labels)
    R = Report(index_pages)
    front_matter(R, cite)
    chapter1(R, cite)
    chapter2(R, cite)
    chapter3(R, cite)
    chapter4(R, cite)
    chapter5(R, cite)
    back_matter(R, cite)
    return R


def convert(src: Path, fmt: str, outdir: Path) -> Path:
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run(
            [SOFFICE, "--headless", "--norestore", f"-env:UserInstallation=file://{profile}",
             "--convert-to", fmt, "--outdir", str(outdir), str(src)],
            check=True, capture_output=True,
            env={**os.environ, "FONTCONFIG_FILE": str(HERE / "tools" / "fonts.conf")},
        )
    return outdir / f"{src.stem}.{fmt.split(':')[0]}"


def main():
    OUT.mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="hfp_report_"))
    docx = work / f"{NAME}.docx"

    pages, labels = None, {}
    for attempt in range(1, 6):
        R = build(pages, labels)
        R.save(docx)
        found = locate(str(convert(docx, "pdf", work)), R.entries)
        missing = [e[2] for e, p in zip(R.entries, found["toc"] + found["Figure"] + found["Table"]) if p == "?"]
        print(f"pass {attempt}: {len(R.entries)} entries, {R.figure_no} figures, {R.table_no} tables")
        if found == pages and R.labels == labels:
            break
        pages, labels = found, dict(R.labels)
    else:
        print("warning: pagination did not stabilize")
    unresolved = [k for kind in ("toc", "Figure", "Table") for k, v in zip([e for e in R.entries if e[0] == kind], found[kind]) if v == "?"]
    if unresolved:
        print("warning: entries not located:", unresolved)

    final_docx = OUT / f"{NAME}.docx"
    shutil.copy(docx, final_docx)
    odt = convert(final_docx, "odt", OUT)
    pdf = convert(odt, "pdf", OUT)  # render from the .odt itself to verify it
    print(f"wrote {odt.relative_to(HERE.parent)} and preview {pdf.relative_to(HERE.parent)}")
    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
