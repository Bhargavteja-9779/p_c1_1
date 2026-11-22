# Submission checklist — Advances in Applied Energy (Elsevier Editorial Manager)

Upload set: `Target_Journal_Submission/` (also zipped as `AAE_Submission_Package.zip`).

| File | Upload as (item type in Editorial Manager) |
|---|---|
| 01_Manuscript.docx | Manuscript (editable source; figures and tables embedded) |
| 01_Manuscript.pdf | Not required — for checking the layout only |
| 02_Title_page.docx | Title page (with author details) |
| 03_Highlights.docx | Highlights (5 bullets, each ≤ 85 characters) |
| 04_Cover_letter.docx | Cover letter |
| 05_Supplementary_Material.docx | Supplementary material (e-component) |
| 06_Graphical_abstract.pdf / .png | Graphical abstract (encouraged; 3984 × 1593 px at 300 dpi) |
| 07_Declaration_of_interest.docx | Declaration of interest (or regenerate with Elsevier's declarations tool during submission) |
| 08_Figures/Fig1–Fig8 (.pdf vector, .png 300 dpi) | Figures (separate files, numbered as in the manuscript) |

Fill in before uploading (placeholders in the manuscript front matter, title page and cover letter):
1. Second author's name (`[Second Author]`, CRediT role: Supervision) and both affiliations — or remove the second author.
2. Corresponding author's postal address and e-mail; date in the cover letter.
3. In Editorial Manager: enter the same title, abstract, keywords and author list; answer the generative-AI,
   data-availability and competing-interest questions consistently with the manuscript.
4. Suggested reviewers (if requested): choose active authors of cited conformal/load-forecasting work with no
   conflict of interest; verify their current e-mail addresses yourself.
5. Verify in Clarivate MJL/JCR that the journal's indexing and IF meet your institution's requirements.
6. To rebuild after editing manuscript/sections/*.md:
   `python manuscript/build_docx.py && python manuscript/build_supplementary.py && python manuscript/build_extras.py && python manuscript/build_cover_letter.py && python scripts/graphical_abstract.py && python scripts/package_submission.py`
