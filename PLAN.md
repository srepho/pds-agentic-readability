# PDS Agentic Readability — Project Plan

The active protocol is [EXPERIMENT.md](EXPERIMENT.md), design v4. The project measures faithful
reconstruction of policy rules and tests whether a standardised presentation improves it.

## 1. First study

Start with home buildings, eight complete policy bundles, twenty common extraction tasks and three
models from different families. Use a separate development set. Compare each policy-task-model in
three independent conditions:

- A: complete checked policy text.
- B: all relevant original evidence, including definitions and exceptions.
- C: the same evidence in a standardised, independently checked plain-language presentation.

Primary outcome: correct task answers including all material qualifications. Primary contrast: C-B.
B-A diagnoses the benefit of supplying evidence, including changes in context burden. Original-document
accuracy remains a descriptive benchmark. This pilot does not establish human readability or support
an industry-wide insurer ranking.

## 2. Existing collection pipeline

```
manifest.yaml -> download_pds.py -> raw PDFs
                               -> extract_text.py -> per-PDF text and metadata
                                                  -> metrics_classical.py -> first-pass metrics
```

The manifest spans car, home, landlord and travel. The local inventory on 16 October 2026 contains
49 PDFs, including separate car Part B files. Files, complete policy bundles and independent templates
are different units. The existing scripts do not yet assemble or validate complete bundles.

Classical metrics use naive extraction and remain provisional. They are descriptive context, not the
primary outcome or a validated measure of human comprehension. Fix reading order, tables, bullets and
page mapping before using text in the experiment.

## 3. Implementation milestones

1. **Corpus:** assemble complete versioned bundles, record applicable supplements and missing dependencies,
   verify product configurations and template families, and hash every source.
2. **Extraction QA:** create checked, page-labelled text with source mapping; retain raw extraction.
3. **Annotation:** freeze the twenty-task bank, reference answers, complete evidence packets and rewrite
   template. Review all keys and packets; independently review rewrites and difficult cases.
4. **Development:** test prompts, typed response validation, scoring, retry policy and token costs on a
   separate set. Decide and document exclusions before evaluation.
5. **Protocol freeze:** register model settings, input/reference hashes, eligibility, repeat selection,
   weights and analysis settings before evaluation outputs are inspected.
6. **Evaluation:** run fresh A/B/C sessions, preserve outputs and provenance, and score using the frozen key.
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
wording/organisation factorial, controlled policy changes, supplementary-document handling and single
versus joint policy extraction. These are candidates for consideration, not adopted milestones.
