# EuroS&P 2027 submission requirements

Active venue: **12th IEEE European Symposium on Security and Privacy**, Madrid, 5–9 July 2027. Verified against the [official CFP](https://eurosp2027.ieee-security.org/cfp.html) on **26 October 2026**. Machine-readable dates and downloaded-template hashes are in `eurosp2027_submission.json`.

## Dates and registration

| Event | Official date, AoE (UTC−12) |
|---|---|
| Mandatory abstract registration | **25 November 2026** |
| Full paper | **2 December 2026** |
| Early rejection notification | 28 January 2027 |
| Rebuttal | 24 February–1 March 2027 |
| Decision | 18 March 2027 |
| Camera-ready, tentative | 15 April 2027 |

Register at [HotCRP](https://hotcrp.eurosp2027.ieee-security.org), scheduled to open in November. Registration requires title, abstract, authors, conflicts, primary area, and relevant topics. It is mandatory even if the PDF is uploaded later. The CFP supplies AoE dates but no explicit cutoff clock time; confirm the clock time in HotCRP. Luxembourg is UTC+1 on these November/December dates, 13 hours ahead of AoE. Use the internal targets in `PLAN.md` rather than relying on a last-minute timezone conversion.

## Format and integrity

- Use the [venue-supplied archive](https://eurosp2027.ieee-security.org/eurosp2027-template.zip), not another IEEE template. Original files are in `paper/templates/eurosp2027/`; `paper/IEEEtran.cls` is an identical copy.
- Preserve its exact class options: `compsoc,conference,a4paper,10pt,times`. Keep the prescribed layout. Submit PDF with at most **13 body pages**. References and appendices are additional; submission acknowledgments are also excluded. Do not assume ethics or data-availability text is exempt. Essential evidence belongs in the body because appendices need not be reviewed.
- Review is anonymous. Omit author names, affiliations, identifying thanks/funding and PDF metadata. Cite prior work in the third person. Review artifacts must use anonymous hosting; the CFP excludes ordinary GitHub and Google Drive links. The public development repository is not a reviewer artifact URL.
- No substantially overlapping concurrent submission. Declare relevant prior overlap. Check each author's seven-paper limit, verify all author/PC conflicts, and finalize authors before full submission: the author list cannot change afterward. Withdrawal is restricted once reviews are sent.
- Address research and publication harms **in the body**. Plan public reproducibility materials under appropriate open-source/data terms, or explain justified restrictions in a Data Availability statement. Release only material the project may redistribute.
- Disclose substantive AI-generated text, code and imagery in anonymous acknowledgments, identifying tools, affected sections and extent of use. Grammar-only assistance has a narrower disclosure exception. The CFP's AI rule takes precedence over the downloaded example's generic instruction to remove acknowledgments.
- Accepted work requires a short talk and poster. Retain these as post-acceptance obligations, not completed outputs.

## Project positioning and readiness

This is an original research-paper target, not a SoK submission. Lead with the security of fuzzy acceptance under independent reconstruction and budgeted attacks. Treat private verification as a separate, conditional contribution. Existing hypotheses, local-secret boundaries, baselines, freezes and gates remain binding; venue fit supplies no evidence of security or privacy.

The supplied example contains legacy 2025 links. Preserve those files as downloaded provenance; the **2027 CFP** above controls policy and dates. The old `pets_requirements.md` and `paper/templates/popets-2027/` are historical records. There is no active PoPETs issue schedule.

Recheck the CFP and HotCRP before registration and upload. Record changes prospectively without altering experimental evidence.
