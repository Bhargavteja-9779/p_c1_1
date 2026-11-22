# Submission checklist (for the author; NOT part of the upload)

Upload folder: `Target_Journal_Submission/` (Advances in Applied Energy, Elsevier Editorial Manager)

| File | Upload as |
|---|---|
| 01_Manuscript.docx (+ 01_Manuscript.pdf for checking) | Manuscript |
| 02_Title_page.docx | Title page (with author details) |
| 03_Highlights.docx | Highlights |
| 04_Cover_letter.docx | Cover letter |
| 05_Supplementary_Material.docx | Supplementary material |
| 06_Code_and_data.zip | Supplementary data / code (or deposit on Zenodo and cite the DOI) |

Fill in before uploading (placeholders in the manuscript front matter, title page and cover letter):
1. Second author's name (currently `[Second Author]`, CRediT role: Supervision) and both affiliations.
2. Corresponding author's postal address and e-mail; date in the cover letter.
3. Repository URL / Zenodo DOI in "Data and code availability" (`[repository URL to be inserted upon acceptance]`).
4. A licence for the code archive (none is included; MIT or Apache-2.0 are common choices).
5. Verify in Clarivate MJL/JCR that the journal's indexing and IF meet your institution's requirements
   (see journal_selection/selected_journal.md: JIF 18.3 and Q1 come from aggregators, not JCR itself).
6. Edit sources in manuscript/sections/*.md and rebuild:
   `python manuscript/build_docx.py && python manuscript/build_supplementary.py && python manuscript/build_extras.py && python manuscript/build_cover_letter.py && python scripts/package_submission.py`
