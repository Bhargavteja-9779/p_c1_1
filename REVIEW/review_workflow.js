export const meta = {
  name: 'paper-review-cycle',
  description: 'Ten independent reviewer agents (distinct scientific perspectives) review manuscript, code and results for one improvement cycle',
  phases: [{ title: 'Review', detail: '10 reviewer agents in parallel' }],
}

const CYCLE = (args && args.cycle) || 1
const LEAD = (args && args.lead) || ''
const ROOT = '/home/user/p_c1_1'

const ROLES = [
  { name: 'R1-novelty-prior-art', text: 'NOVELTY AND PRIOR-ART REVIEWER. Investigate whether the contribution is genuinely different from existing research (conformal prediction for groups/hierarchies/few-shot, Mondrian/clustered conformal, ACI, Bayesian/Dirichlet conformal, transfer learning and zero-shot building load forecasting). Use WebSearch to look for similar publications, methods or patents published up to 2026. Attempt to invalidate the novelty claims; report any close prior work with full bibliographic details you actually found.' },
  { name: 'R2-methodology', text: 'METHODOLOGY REVIEWER. Check mathematical correctness of Eq. (scale, scores, interval, prior, HSC mixture, tuning), assumptions (exchangeability, Dirichlet-process interpretation), the claimed limits, the stage-bin and kNN design, and whether the code in src/models/calibration.py, src/training/pipeline.py and src/preprocessing/features.py implements exactly what the manuscript states. Report contradictions with file:line evidence.' },
  { name: 'R3-experimental-design', text: 'EXPERIMENTAL DESIGN REVIEWER. Check fairness of baselines (same forecaster/scores/tuning budget), dataset choice, hyper-parameter selection (only on calibration buildings?), evaluation protocol, reproducibility, and whether every claim maps to an executed experiment. Check results/run_info.json and tables/*.md.' },
  { name: 'R4-statistics', text: 'STATISTICAL REVIEWER. Check confidence intervals, seeds, unit of analysis, Wilcoxon/Holm/rank-biserial usage, cluster bootstrap, multiple comparisons, effect sizes, and whether text claims of significance match results/statistics.csv and tables/T_tests.md. Recompute a few numbers from results/raw_results.csv with python if needed.' },
  { name: 'R5-data-leakage', text: 'DATASET AND LEAKAGE REVIEWER. Check data quality rules, licensing, duplicate buildings/meters, building/site/temporal leakage between training, calibration and target sets, leakage through features (inspect src/preprocessing/features.py and tests/test_core.py), weather (observed vs forecast), distribution bias from the quality filter, and target-period selection (80 % valid windows).' },
  { name: 'R6-robustness-generalisation', text: 'ROBUSTNESS AND GENERALISATION REVIEWER. Try to show that the method fails under distribution shift, noise, missing data, level shifts, unseen sites, another country, small calibration pools, weak forecasters, or other plausible deployment conditions not yet tested. Inspect tables/T_robustness.md, tables/T_gen_*.md and propose decisive missing experiments.' },
  { name: 'R7-computational', text: 'COMPUTATIONAL EFFICIENCY REVIEWER. Check complexity, memory, latency, scalability to large portfolios, deployment feasibility, and whether reported costs (tables/T_efficiency.md, results/run_info.json) are measured fairly and described correctly. Question whether improvements justify any cost.' },
  { name: 'R8-literature-citations', text: 'LITERATURE AND CITATION REVIEWER. Verify references in manuscript/references.py (authors, year, venue, DOI) — spot-check at least 8 via WebSearch/WebFetch or crossref API (curl https://api.crossref.org/works/<doi>), check that each citation supports the sentence where it is used in manuscript/Final_Manuscript.md, and identify important missing competing studies.' },
  { name: 'R9-associate-editor', text: 'ASSOCIATE EDITOR of Advances in Applied Energy (Elsevier). Evaluate scope fit (applied energy innovation), novelty relative to the journal standard (see literature/aae_benchmark.md), manuscript quality, length, structure, highlights/abstract/keywords, declarations, data availability, figure/table quality (look at figures/*.png), and likely desk-rejection risks.' },
  { name: 'R10-hostile-competitor', text: 'HOSTILE COMPETING RESEARCHER who built a similar method. Try to demonstrate the work is incremental, incorrectly evaluated, unfairly compared or unnecessary; look for a simpler existing method (e.g. self-only conformal, ACI, CQR, Mondrian, a simple blend) that gives equivalent results according to the reported tables; check whether improvements are driven by something other than the claimed components.' },
]

const SCHEMA = {
  type: 'object',
  properties: {
    recommendation: { type: 'string', enum: ['Acceptable', 'Minor revision', 'Major revision', 'Reject'] },
    summary: { type: 'string' },
    issues: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          severity: { type: 'string', enum: ['Fatal', 'Critical', 'Major', 'Moderate', 'Minor'] },
          title: { type: 'string' },
          evidence: { type: 'string' },
          action: { type: 'string' },
          experiment: { type: 'string' },
        },
        required: ['severity', 'title', 'evidence', 'action'],
      },
    },
  },
  required: ['recommendation', 'summary', 'issues'],
}

function prompt(r) {
  const packet = (args && args.packet) || `${ROOT}/REVIEW/packet_cycle01.md`
  return `You are an independent peer reviewer (review cycle ${CYCLE} of 10) for a manuscript targeted at the Elsevier journal "Advances in Applied Energy" (applied energy innovation; full-length research articles ~10-15 printed pages; abstract <= 250 words).
Your perspective: ${r.text}
${LEAD ? 'Lead emphasis of this cycle (in addition to your own perspective): ' + LEAD : ''}

START by reading the review packet ${packet}. It contains the complete built manuscript (all numbers are machine-filled from result files), all generated tables, a code map and the review history. Then verify anything suspicious with TARGETED reads/greps in the repository ${ROOT} (results/*.csv|json, src/*, tests/*, figures/*.png). Read-only: do not modify the repository (scratch only under /tmp/claude-0/review_scratch_${CYCLE}/). Do not run experiments; small checks with "nice -n 19 python3" on results files are fine.
The review history lists issues already raised and how they were resolved: find NEW weaknesses or issues that were NOT adequately resolved; do not repeat resolved items.
Be hostile but scientifically fair. Every issue needs concrete evidence (quote numbers, table rows, file:line). Do not invent problems to reach a count. Classify each as Fatal, Critical, Major, Moderate or Minor; give a specific corrective action and the experiment (if any) required; give a final recommendation. Keep the review under ~900 words.`
}

phase('Review')
const res = await parallel(ROLES.map(r => () => agent(prompt(r), { label: r.name, schema: SCHEMA, phase: 'Review' })))
return res.map((x, i) => (x ? { role: ROLES[i].name, ...x } : { role: ROLES[i].name, failed: true }))
