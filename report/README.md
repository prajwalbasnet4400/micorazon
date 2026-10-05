# Project Report

Source for the final project report, `output/HFP_Final_Report.odt` (LibreOffice). It follows the
Project III guideline: the prescribed front matter, the five prescribed chapters, IEEE references,
A4 paper, margins of 1" (1.25" left), Times New Roman 12 pt, justified text at 1.5 spacing, and
bold 16/14/12 pt headings. Figure captions sit below figures and table captions above tables, and
pages are numbered in roman from the certificate page and in arabic from Chapter 1.

## Rebuild

```bash
uv sync --all-groups
uv run python report/tools/make_charts.py                              # charts + equations
plantuml -tpng -Sdpi=200 -o ../figures/generated report/diagrams/*.puml  # UML diagrams
uv run python report/build_report.py                                   # .odt + preview .pdf
```

Requires LibreOffice, PlantUML (`brew install plantuml`) and poppler (`pdftotext`). The build
renders the document, finds the page of every heading, figure and table, and writes them into
the table of contents and lists of figures and tables. These are real LibreOffice indexes, so
**Tools → Update → Update All** refreshes them after manual edits.

## Layout

| Path | Contents |
| --- | --- |
| `content/` | Report text, one module per part (front matter, chapters, back matter) |
| `diagrams/` | PlantUML sources for every UML diagram |
| `figures/screens/` | Application screenshots (Appendix A) |
| `figures/generated/` | Rendered diagrams and charts |
| `figures/original/` | College logo and algorithm figures reused from the earlier report |
| `tools/` | Document toolkit, pagination, chart generation |
| `system_test_results.json`, `latency.json` | Recorded system test and response time results |
