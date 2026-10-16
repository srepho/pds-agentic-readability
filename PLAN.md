# PDS Agentic Readability — Project Plan

The active protocol is [EXPERIMENT.md](EXPERIMENT.md), design v4. The project measures faithful
reconstruction of policy rules and tests whether a standardised presentation improves it.

## 1. First study

Start with home buildings, six complete policy bundles, twelve common extraction tasks and three
models from different families, expanding to eight bundles and twenty tasks once annotation throughput
is measured. Use a separate development set. Compare each policy-task-model in four independent conditions:

- A: complete checked policy text.
- B: all relevant original evidence, including definitions and exceptions.
- B+: the B evidence at its original positions, padded with irrelevant text from the same bundle to A's length.
- C: the same evidence in a standardised, independently checked plain-language presentation whose
  structure does not mirror the response schema.

Primary outcome: correct task answers including all material qualifications. Primary contrast: C-B.
B+-B isolates the cost of context length; A-B+ isolates the cost of relevant-looking surroundings;
B-A remains the total benefit of supplying evidence. Confidently-wrong rate and calibration are
secondary diagnostics. Original-document
accuracy remains a descriptive benchmark. This pilot does not establish human readability or support
an industry-wide insurer ranking.

## 2. Existing collection pipeline

```
manifest.yaml -> download_pds.py -> raw PDFs
                               -> extract_text.py -> per-PDF text and metadata
                                                  -> metrics_classical.py -> first-pass metrics
```

The manifest spans car, home, landlord and travel and now lists supplementary PDSs where the insurer
publishes them. The local inventory on 16 October 2026 contains 49 base PDFs, including separate car
Part B files, plus 44 supplements. Files, complete policy bundles and independent templates are different
units. The existing scripts download and extract per file; they do not yet assemble or validate bundles,
and supplement applicability must be verified against effective dates.

Classical metrics use naive extraction and remain provisional. They are descriptive context, not the
primary outcome or a validated measure of human comprehension. Fix reading order, tables, bullets and
page mapping before using text in the experiment.

## 3. Implementation milestones

1. **Corpus:** assemble complete versioned bundles, record applicable supplements and missing dependencies,
   verify product configurations and template families, and hash every source.
2. **Extraction QA:** create checked, page-labelled text with source mapping; retain raw extraction.
3. **Annotation:** review and freeze the task bank (draft in `tasks/`), reference answers, complete
   evidence packets, padding constructions and rewrite template. Review all keys and packets;
   independently review rewrites and difficult cases. Record minutes per artifact to size the study.
4. **Development:** test prompts, typed response validation, scoring, retry policy and token costs on a
   separate set. Decide and document exclusions before evaluation.
5. **Protocol freeze:** register model settings, input/reference hashes, eligibility, repeat selection,
   weights and analysis settings before evaluation outputs are inspected.
6. **Evaluation:** run fresh A/B/B+/C sessions, preserve outputs and provenance, and score using the frozen key.
7. **Report:** show per-policy paired performance, model-specific differences, uncertainty, error examples,
   intervention eligibility and rewrite acceptance. Use pilot variability to size a larger study.

Likely new components: a bundle manifest/validator, checked-text preparation, task/reference records,
evidence/rewrite preparation, an evaluation runner, scoring/adjudication tools and an analysis report.
These are planned components, not implemented commands.

## 4. Later extensions

After validating the pilot, consider more product lines, a broader model panel, native-PDF inputs,
larger extraction schemas and explicit-utility comparisons. A consumer study is required for claims
about human comprehension. See EXPERIMENT.md for limitations and the deferred experiments.

Alternative small-study structures are documented in [EXPERIMENT_OPTIONS.md](EXPERIMENT_OPTIONS.md):
wording/organisation factorial, controlled policy changes, supplementary-document handling, single versus
joint policy extraction, sibling brands as a natural experiment, minimal-pair clause edits, dependency
distance, a navigating agent, and paraphrase robustness. These are candidates for consideration, not
adopted milestones. The sibling-brand design can run first because it needs no synthetic material.
