# EuroS&P 2027 manuscript

> **Active v4 planning narrative:** reconstruction, semantic distinctions and attacker acceptance. Private verification is deferred; no v4 result is claimed. See [paper plan](../docs/eurosp2027_paper_plan.md). P18-v4 and every later phase require an explained proposal and explicit authorization.

- `main.tex`: canonical build entry; inputs the active manuscript.
- `draft.tex`: active anonymous **planning draft**, not a submission-ready paper.
- `IEEEtran.cls`: exact class distributed by EuroS&P 2027.
- `references.bib`: existing verified research bibliography; no sample references are imported.
- `templates/eurosp2027/`: unmodified official template files.
- `templates/popets-2027/`: preserved old sample and pre-migration draft source/PDF. Root ACM/PoPETs support files are legacy material and are not loaded by the active entry.

Build from this directory:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The same sequence with `draft` builds `draft.pdf`. Never upload the archived PoPETs PDF. Verify A4 geometry, at most 13 body pages, resolved references, anonymous metadata and anonymous artifact links. A successful build establishes formatting only. Results and submission blockers are documented in `../docs/eurosp2027_paper_plan.md`; official requirements and dates are in `../docs/eurosp2027_requirements.md`.
