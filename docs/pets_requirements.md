# PoPETs/PETS 2027 verified requirements

Verified: 2026-08-24. Recheck immediately before submission because venue rules can change.

## Authoritative sources

- PETS 2027 Call for Papers: https://petsymposium.org/cfp27.php
- PoPETs 2027 author/submission rules: https://www.petsymposium.org/authors-2027.php
- Official 2027 template archive: https://www.petsymposium.org/files/submission-template-2027.zip
- PETS 2027 submission server: https://submit.petsymposium.org/

## Scope and scientific positioning

- The work must be novel research into privacy-enhancing technologies and have strong ties to privacy in digital systems.
- The core contribution must be relevant to a real-world privacy application. That relevance must be explicit on page 1 and sustained through a substantial practical/applied portion of the paper.
- A theoretical cryptographic contribution must explain integration into a real application. An empirical paper must connect its evaluation to privacy and real-world use.
- If evidence relies on synthetic or otherwise non-privacy-specific datasets, the manuscript needs a clearly marked explanation of why the result can inform the real privacy application.
- Privacy cannot be a superficial label. For this project, protected storage/comparison, compromise resistance, leakage, and linkability must remain central—not merely the fact that authentication is security-related.

## Submission format and length

- Submission is PDF and must use the PoPETs 2027 LaTeX template without changing its look and feel. Nonconforming formatting can cause desk rejection.
- The initial submission/resubmission limit is 12 typeset main-body pages.
- The three mandatory template sections—Ethical Considerations, Open Science, and AI Use—plus acknowledgements, bibliography, and clearly marked appendices do not count toward those 12 pages.
- Appendices are supplementary; reviewers need not read them, and the paper must remain self-contained.
- A Revise submission and an accepted camera-ready paper may use 13 main-body pages.
- The introduction must give non-specialist background and summarize contributions; the first page must state real-world privacy relevance.

## Template verification

The official template ZIP downloaded on 2026-08-24 had SHA-256:

```text
B1ABBCC0832B7860F5FE8D9773088540B0456965A05FD14C3D47B3A8D85EA7D7
```

Every corresponding template file already in `paper/` matched the official archive byte-for-byte: `main.tex`, `popets.sty`, `acmart.cls`, `acmnumeric.bbx`, `acmnumeric.cbx`, `ACM-Reference-Format.bst`, `sample-base.bib`, `sample-franklin.png`, and `cc-by-4.pdf`.

`paper/draft.tex` remains a research-direction document. `paper/main.tex` and `sample-base.bib` remain official examples until P15 migrates the evidence-backed manuscript; sample authors/text/references must not become project content.

## Anonymisation and originality

- Review is double-blind. Remove author names/affiliations, identifying acknowledgements/funding, institution references, and identifying external repository links.
- Do not omit related work for anonymity; cite an author's prior work in the third person.
- PoPETs requires original, previously unpublished work. Substantial simultaneous overlap or double submission is prohibited.
- Public preprints are not forbidden, but the venue discourages posting while under review because of deanonymisation risk.
- A resubmission rejected by any reviewed venue must include prior reviews; PoPETs resubmissions/revisions require an anonymised change summary.

## Ethics, open science, and AI use

- Ethical Considerations is mandatory and must justify the work and state whether an external ethics panel reviewed it.
- This project has no human-subject study. Public prompt data and attack experiments still require privacy, harm, licence, and data-minimisation analysis.
- Open Science is mandatory. Authors indicate whether code/data will be released; a justified non-release is allowed. Artifact review is a separate post-acceptance process.
- AI Use is mandatory. Humans retain responsibility for the paper, work, and artifacts. AI tools cannot be authors. Hallucinated/fabricated references or results can cause desk rejection or misconduct action.
- Claims of benefit to a population require validation or an explicit limitation. This reinforces the contract's prohibition on memorability/usability claims without a human study.

## Process and dates

All deadlines are 23:59:59 Anywhere on Earth (UTC-12).

| Issue | Submission | Notification | Camera-ready for immediate acceptance/revision |
|---|---|---|---|
| 1 | 2026-05-31 | 2026-08-01 | 2026-09-15 |
| 2 | 2026-08-31 | 2026-11-01 | 2026-12-15 |
| 3 | 2026-11-30 | 2027-02-01 | 2027-03-15 |
| 4 | 2027-02-28 | 2027-05-01 | 2027-06-15 |

Papers receive Accept, Revise, or Reject decisions. A revision editor can guide a Revise for up to four months. Rejected papers must skip one full issue before PoPETs resubmission. Rebuttal allows a separate 250-word response to each review.

## Project consequence

Issue 2 is seven days after this verification date and is not a credible target for an unimplemented research project. Issue 3 is aggressive; Issue 4 is the first schedule with meaningful room for all scientific gates, but the target issue remains a user/project-management decision. Scientific gates must not be weakened to meet a deadline.

Before P15/P17, re-download the official template, recheck the CFP/author rules and deadlines, and record new hashes/access dates.

