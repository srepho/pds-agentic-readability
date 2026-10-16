# Experimental design v4: paired tests of agentic PDS readability

Status: proposed protocol, updated 16 October 2026 (revision 4.1: adds the padded-evidence arm, a
schema-alignment control for the rewrite, a smaller pilot grid, and calibration diagnostics). This replaces designs v1-v3; their text remains
in Git history. No LLM evaluation has been run. The task bank, reference answers, model panel,
interventions and analysis settings must be frozen before the evaluation run. This document alone
is not a completed preregistration.

Four alternative small-study structures are recorded in [EXPERIMENT_OPTIONS.md](EXPERIMENT_OPTIONS.md)
for consideration. They do not replace or expand this active protocol unless explicitly adopted.

## 1. Research question and scope

**How much does the presentation of a PDS impede faithful extraction, and which changes reduce
that difficulty?**

The study measures whether models reconstruct policy rules correctly, including conditions and
exceptions. It does not reward generous cover, recommend an insurer, or establish human readability.
Classical readability formulas remain descriptive context; they are not the reference standard.

The core experiment compares three presentations of the same policy information using the same
model and task. Coverage therefore stays fixed within each comparison. Comparisons of raw accuracy
between insurers remain descriptive: their underlying coverage can differ in complexity.

Initial scope: home buildings, six complete policy bundles, twelve common extraction tasks (three per
category) and three models from different model families. Expansion to eight bundles and twenty tasks is
gated on measured annotation throughput (section 9), because reference records, evidence packets and
rewrites are the binding constraint, not API calls. This is a pilot for estimating effects and variability,
not a powered industry ranking. Use a separate development set to tune prompts and procedures.

## 2. Experimental unit and corpus

A policy bundle is the complete set of applicable documents for a specified product, version and
configuration, not necessarily one PDF. Record the base PDS, all required parts, and applicable
supplementary documents. Identify documents referenced but unavailable, including individual policy
schedules. Do not invent schedule-specific amounts or selected options.

For each bundle record:
- Stable bundle ID, brand, product, documented underwriter and assessed template family.
- Product configuration, applicability dates and corpus snapshot date.
- Component URLs, retrieval timestamps, SHA-256 hashes and document versions.
- Included page ranges, source page identifiers and any excluded non-PDS material.
- Missing dependencies, extraction method/version and extraction QA status.

Verify underwriting and template relationships for the selected documents; a brand-level group
label alone is not sufficient. Select for structural and template diversity before looking at model
performance. Keep all selected bundles and exclusion reasons in the selection record.

The local inventory on 16 October 2026 contains 49 base PDFs, including two separate car Part B files;
these counts do not imply 49 independent policies. `data/manifest.yaml` now also lists supplementary PDSs
(SPDS) per product where the insurer's public document page exposes them, and `download_pds.py` fetches
them as `<product>_spdsN.pdf`. Applicability of each SPDS to the listed base PDS version is flagged
"(verify ...)" where unconfirmed and must be checked against stated effective dates during bundle
assembly. The extraction and metrics scripts still operate per PDF and do not yet assemble bundles. Home buildings avoids initially mixing buildings,
contents and landlord cover, even when a source document contains several products.

### Extraction control

Use checked, page-labelled text for all primary conditions. Inspect reading order, tables, lists,
negation, numerical limits and cross-references against the source. Preserve coverage-bearing content;
remove non-PDS material only under documented rules. Preserve an immutable raw extraction alongside
the checked text. All B evidence must be traceable to A's checked text and the source PDF.

Native PDF input is a later, separate modality experiment. Do not attribute extraction defects to
writing style or assume that a PDF API necessarily exposes the same visual/text input across vendors.

## 3. Fixed task bank

Freeze twelve tasks for the pilot, reused across all six bundles, with three in each category (twenty
tasks, five per category, at expansion). A draft bank is in `tasks/home_buildings_task_bank_draft.yaml`;
it is a starting point for review, not a frozen artifact:

| Category | Target |
|---|---|
| Direct statements | Express cover and benefit rules |
| Limits and settlement | Amounts, units, caps, calculation bases and settlement rules |
| Qualifications | Conditions, exclusions and exceptions |
| Distributed evidence | Rules requiring multiple clauses or definitions |

Assign each task to one primary category before running models. Tasks may involve several skills;
the categories are sampling strata, not claims of independent cognitive mechanisms.

Example: "Extract the temporary-accommodation benefit, its maximum amount, duration and eligibility
conditions." Avoid reducing a conditional rule to an unconditional covered/not-covered label.

Specify atomic required elements and acceptable equivalents for every task. Include explicit tests
of qualifications and numerical units, rather than allowing a correct headline with a material
exception omitted to count as correct. Do not choose tasks based on errors observed in evaluation.
The task bank determines what the benchmark represents; using a schema does not remove selection bias.

Use a separate small development set, preferably from template families outside the evaluation set,
to refine instructions and annotation. If that separation is impossible, disclose the overlap.

## 4. Four paired presentations

| Arm | Model input | Interpretation |
|---|---|---|
| A: Full document | Complete checked policy bundle with page labels | Overall extraction performance |
| B: Relevant original evidence | All necessary original clauses, definitions, exceptions and cross-references, verbatim | Performance when evidence selection is supplied |
| B+: Padded evidence | The B packet embedded, in its original relative order, inside non-relevant checked text from the same bundle, padded to A's token length | Separates the cost of context length from the cost of finding evidence |
| C: Standardised presentation | The same evidence in a fixed plain-language structure, independently checked for meaning | Performance after a specified presentation intervention |

B+ is constructed mechanically from A and the B span list: keep the B spans at their original positions
and replace every other span with text drawn from the same bundle that the reference record marks as
irrelevant to the task. Then B+ minus B is the pure long-context cost, and A minus B+ is the cost of
evidence being surrounded by *relevant-looking* rather than irrelevant material, which is the closest
available proxy for a navigation cost. Where the padding rule cannot be applied cleanly (for example
when relevant spans are interleaved with table rows), record B+ as ineligible for that task.

Run each arm in a fresh session, with identical task wording and response schema, and no access to
other arms, reference answers, web search or previous responses. Randomise arm execution order and
interleave models/bundles to reduce time-related confounding. Neutral bundle IDs and consistent
metadata masking may be used, but must not change operative wording or break source references.
Do not claim that branding is completely blinded when the wording can identify a template.

### Evidence and rewrite construction

B is an expert-selected evidence packet, not a single convenient paragraph. Preserve source wording,
labels and original order; include the full dependency chain needed to answer the task. Record every
selected span and its source. An incomplete packet is an annotation defect.

C uses a frozen template, for example: scope; rule; limits and units; conditions; exclusions;
exceptions; dependencies. **Schema-alignment control:** the C template must not mirror the response
schema. If the response schema asks for rule, limits, conditions and exceptions as separate fields, a
C input organised under the same headings hands the model its output structure, and a C minus B lift
could reflect alignment rather than presentation. Either (i) write C as continuous plain prose that
contains every element in a fixed but non-schema order, or (ii) run two response schemas (field-wise
and free-text-then-extract) across all arms and report the C minus B effect under both; the effect
must survive the schema change to be attributed to presentation. Option (ii) is preferred when budget
allows because it also measures schema sensitivity in A and B. Preserve all material information in B,
including uncertainty. Do not add
an inferred answer, resolve genuine source ambiguity, supply absent facts, or copy the reference
answer into the input. Construct C from B under fixed instructions without access to evaluation
outputs; maintain a mapping from each rewritten rule to its original source spans.

A domain reviewer checks every reference answer and B packet. A second reviewer independently checks
C against B in both directions and reviews difficult reference cases. Models can help draft these
artifacts but model agreement cannot certify correctness. Report agreement, disagreements and their
resolution. Freeze accepted packets and rewrites before evaluation; never repair them selectively
because a model answered incorrectly.

If a faithful packet/rewrite cannot be prepared, retain the task in A and record why B/C are ineligible.
Report intervention eligibility and rewrite acceptance rates. Paired results apply only to the
prespecified eligible subset, not automatically to every policy rule.

### Missing information and ambiguity

Distinguish these reference states:
- An explicit policy rule, including explicit exclusion or conditional cover.
- Not stated after complete-bundle review.
- Requires a schedule, selected option or another unavailable document.
- Multiple defensible interpretations remain after adjudication.

Absence cannot be established by an empty evidence packet. Score absence tasks using complete-bundle
review in A and report them separately from B/C comparisons. For other states, decide B/C eligibility
before evaluation: include them only when an evidence packet preserves everything needed to justify
the state. A correct response must identify the dependency or uncertainty, without inventing facts.

## 5. Reference records and response format

Each versioned reference record includes bundle ID, task ID/category, reference state, required answer
elements, material qualifications, acceptable alternatives, evidence spans, source pages, B/C
eligibility, reviewer decisions and adjudication history. An uncertainty label is not automatically
an error; score against the documented acceptable response set.

Each model response contains:
- Rule/value and reference-state assessment.
- Limits, units and material conditions/exceptions as applicable.
- Evidence locations and supporting quotations from its supplied input.
- A self-reported confidence on a fixed 0-100 scale (or a fixed ordinal scale where a vendor's
  structured-output support makes a number impractical). Confidence is never used for scoring
  correctness; it feeds the calibration diagnostics in section 6.

C citations refer to C spans, which map back to original sources. Do not require a verbatim original
quotation from a model that only received the rewrite. Keep the reference answer separate from all
model-visible artifacts.

Freeze and hash references and inputs. If a substantive reference defect is discovered later, issue
a new reference version, document the reason and rescore all affected outputs consistently. Preserve
the original results; never silently overwrite the key or selectively change a model's score.

## 6. Outcomes and estimands

### Primary outcome

**Task accuracy:** proportion of tasks answered correctly with all material qualifications.
Use prespecified exact/normalised checks for typed values, units and categories. Use blinded human
adjudication for remaining semantic equivalence, with model and arm identities hidden where feasible.
Count missing, truncated or invalid responses as failures under a fixed response-handling policy.

The primary intervention contrast is **C minus B** in percentage points on the same eligible
bundle-task-model observations. It estimates the effect of this standardised presentation package,
including any changes in length and organisation; it does not isolate sentence style alone.

The secondary contrasts are **B+ minus B** (long-context cost with evidence position preserved) and
**A minus B+** (cost of relevant-looking surroundings, the navigation proxy), both on the same eligible
observations. **B minus A** remains reportable as the total benefit of supplying relevant evidence.
Report A separately over all tasks and over the paired subset.

### Secondary diagnostics

- Overstatement: unsupported extension of cover, inflated limits or omitted restrictive qualifications.
- Understatement/omission: missing cover, understated limits or omitted requested information.
- Unsupported claims: assertions not supported by the supplied evidence.
- Citation validity and support: location/quotation exists, and the cited text actually supports the claim.

- Confidently-wrong rate: proportion of incorrect answers given with confidence at or above a
  prespecified threshold (default 80). This is the consumer-harm quadrant. A presentation that moves
  errors from confident to uncertain is an improvement even when headline accuracy does not move.
- Calibration: expected calibration error (or a reliability table at fixed bins) per arm and model.
  Report it as a diagnostic; small pilot counts make it noisy.

Predefine denominators and coding rules; error categories may overlap. A correct answer with a bad
citation should remain distinguishable from an incorrect answer. Quotes that occur in a document do
not by themselves establish support. Report reference-state and task-category breakdowns so easy or
absent fields cannot obscure failures on substantive rules.

Inter-model disagreement is an instability signal, not proof of textual ambiguity. Repeat agreement
is a reliability diagnostic, not correctness. Do not combine model tiers into an ability-curve area:
the tiers do not provide a calibrated numerical ability scale.

## 7. Model panel and execution

Select three models from different families, documenting practical availability and cost. Freeze exact
model identifiers/snapshots, prompts, reasoning settings, output limits, schema and client versions.
Verify supported settings and prices at run time; do not rely on earlier draft model names or prices.
Results describe these configured models, not the consumer products or agent platforms around them.

Use a common input format within supported context limits. Do not silently truncate bundles. No semantic
retry or corrective feedback is allowed. Log transport retries separately; an invalid completed response
counts as a failure. Preserve request IDs, timestamps, prompt/input hashes, raw outputs, usage, costs,
completion states and all retry attempts in append-only run records.

Prefer one task per fresh request for the pilot. If batching tasks is necessary, freeze identical task
blocks across arms on the development set; B/C must contain the union of required evidence, and results
must be described as block-based. Never compare a single-task evidence packet with a differently
prompted multi-task baseline without explicitly changing the protocol.

The maximum pilot grid is 6 bundles x 12 tasks x 3 models x 4 arms = 864 task responses before repeats
(1,920 at the 8 x 20 expansion). B/B+/C ineligibility reduces the realised grid. The matching annotation
load at pilot scale is 72 reference records, 72 evidence packets, 72 padding constructions and 72
rewrites, each with the review steps in section 4; this, not the call count, is what to budget. Request counts depend on task batching; full-bundle
reads can dominate token cost. Measure tokens and cost on the development set before approving a run.
Repeat a prespecified random 10% of eligible bundle-task-model triplets across all three arms, selected
before outputs are inspected, to estimate repeat variability. Repeats are not new independent policies.

## 8. Analysis

1. Report A accuracy for each model, with task-category and reference-state breakdowns.
2. Calculate paired C-B, B+-B, A-B+ and B-A differences within bundle, task and model. Average tasks within the
   fixed categories and bundles with equal prespecified weights; do not let document length or repeated
   runs determine weight. Report eligible counts and missing categories rather than imputing them.
3. Show per-bundle effects and model-specific averages before an optional equally weighted panel mean.
   Keep the panel fixed; do not down-weight models because their results are inconvenient.
4. Account for repeated tasks and shared templates. For uncertainty conditional on this fixed task bank
   and panel, use a paired cluster bootstrap at the assessed template-family level, preserving all arms
   and nested observations. With few families, treat intervals as exploratory, show individual-family
   effects and leave-one-family-out sensitivity, and avoid strong population claims.
5. Generalisation to new task types requires a broader task sample and an analysis that also accounts
   for task dependence. Do not present the pilot's many field responses as a large independent sample.
6. Use pilot effect sizes and between-family variability to simulate sample-size needs for a larger,
   separately frozen study. Set the target precision or minimum meaningful improvement before sizing it.

Report absolute percentage-point differences, denominators and uncertainty, including negative effects.
Do not force results into an insurer league table. No confirmatory significance claims are planned for
this pilot. Secondary diagnostics and subgroup comparisons are exploratory.

## 9. Delivery sequence and expansion gates

1. Audit complete bundles (base PDS + parts + applicable SPDS, see `data/manifest.yaml`) and checked
   extraction; select the development and evaluation sets.
2. Draft the common task bank, references, evidence packets and rewrite template; complete human review.
3. Test the workflow on development data. Measure API cost **and annotation minutes per reference record,
   packet, padding construction and rewrite**. Use those throughput numbers, not API cost, to decide
   whether the evaluation runs at 6 x 12 or 8 x 20, and to settle response handling and analysis rules.
4. Freeze and hash the evaluation package and register the protocol before any evaluation output is seen.
5. Run A/B/C with the fixed panel; score, adjudicate and audit all denominators and exclusions.
6. Publish paired performance charts, error examples, eligibility/rewrite-quality information and a
   reproducibility manifest. Respect source-document ownership when selecting public excerpts.

The first deliverable is a per-policy A/B/C performance chart with examples of errors corrected or
introduced by the intervention. It should support specific recommendations about evidence organisation
and rule presentation, with clear limits on generalisation.

Defer native-PDF comparisons, full extraction ontologies, large model panels, brand-bias experiments,
insurer-to-insurer style transplants and recommendation rankings until this design is validated.
Recommendation ranking would additionally require an explicit preference/utility rule and sufficient
profile information; coverage extraction alone does not supply a uniquely correct recommendation.
Human readability requires a separate consumer comprehension study, not a small-model proxy.

## 10. Methodological references

- Liu et al., [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172):
  evidence that relevant-information position can affect long-context performance; motivates separating
  full-document performance from performance with relevant evidence supplied.
- Gao et al., [Enabling Large Language Models to Generate Text with Citations](https://aclanthology.org/2023.emnlp-main.398/):
  separates answer correctness from citation quality; motivates reporting citation support separately.

These sources motivate controls; they do not establish how the selected models will perform on PDSs.
