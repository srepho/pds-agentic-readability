# Experiments overview

Every experiment proposed for this project, in one place. The active protocol is
[EXPERIMENT.md](EXPERIMENT.md) (v4.1). Candidate designs are specified in full in
[EXPERIMENT_OPTIONS.md](EXPERIMENT_OPTIONS.md). Designs v1 to v3 are superseded; their full text is in
Git history at commit `5f658eb` and in the history of `EXPERIMENT.md`.

## At a glance

| # | Experiment | Question | Status | Synthetic material needed | Relative cost |
|---|---|---|---|---|---|
| 0 | Classical readability metrics | How do PDSs score on Flesch, Fog, SMOG and density measures? | Built, provisional | None | Negligible |
| 1 | LLM-judge readability (v1) | Can LLM judges rate readability like humans do? | Superseded | Degraded and improved rewrites | Medium |
| 2 | Scenario comprehension and style transplant (v2) | Does a weak reader reach the same claim decision as an expert reader? | Superseded | Scenario bank, transplants | Medium-high |
| 3 | Agentic coverage extraction (v3) | How faithfully do agents extract and compare full coverage? | Superseded, ideas carried into v4 | Coverage ontology | High |
| 4 | **Paired presentations A/B/B+/C (v4.1)** | How much does presentation impede extraction, and does a standardised rewrite help? | **Active protocol** | Evidence packets, padding, rewrites | Medium |
| 5 | Wording by organisation factorial | Do plain wording and co-locating rules help separately or together? | Candidate | Four variants per section | Medium |
| 6 | Controlled policy changes | Does the answer follow the supplied rule when the rule changes? | Candidate | Synthetic policy twins | Low-medium |
| 7 | Supplementary documents | Can models apply amendments and ignore inapplicable ones? | Candidate | Consolidated texts | Medium |
| 8 | Single versus multiple policies | Does joint comparison cause omissions or misattribution? | Candidate | None | Low |
| 9 | Sibling brands natural experiment | Same rule, different brand template: which template reads best? | Candidate, recommended first | None | Low |
| 10 | Minimal-pair clause edits | Which single drafting moves improve extraction? | Candidate | One edit per pair | Low-medium |
| 11 | Dependency distance | How far apart can a rule and its exception be? | Candidate | Mechanical padding | Low |
| 12 | Navigating agent | Can a tool-using agent find the governing clause, and do headings help? | Candidate | None | Medium |
| 13 | Paraphrase robustness | Does the answer survive different ways of asking? | Candidate, add-on | Phrasing variants | Very low with caching |
| 14 | Agent retrieval in the wild | Can real agent products find and fetch the current PDS at all? | New proposal | None | Low |

## 0. Classical readability metrics

Built in `scripts/metrics_classical.py`: Flesch Reading Ease, Flesch-Kincaid grade, Gunning Fog, SMOG,
Coleman-Liau, ARI, Dale-Chall, sentence length, share of long sentences, polysyllable share, and densities
of hedges ("unless", "subject to"), negations and cross-references. Results for 47 documents are in
`data/metrics_classical.csv`. They are provisional: naive extraction lets tables and bullet lists inflate
sentence length. In the active design they are descriptive context only, not a measure of comprehension.

## 1. LLM-judge readability (v1, superseded)

Matched sections across insurers (cover summary, flood, exclusions, excess, claims, cancellation, duty of
disclosure, definitions), blinded for brand. Three measures:

- **Pairwise preference** within each product-section cell, judged twice with positions swapped, fitted
  with a Bradley-Terry model.
- **Anchored rubric** on five dimensions, three repeats per passage to measure judge noise.
- **Comprehension probe**: a strong model writes questions, a weak model answers from the passage, the
  strong model grades.

Validation: synthetic degraded and improved versions of 40 passages that a valid judge must rank
correctly; a human-rated anchor set of 60 pairs; position, repeat and inter-model consistency; and a
brand-bias test comparing blinded with unblinded scores. Optional longitudinal comparison of 2018 to 2026
PDS versions. Superseded because judge preferences leak coverage generosity into "readability".

## 2. Scenario comprehension and style transplant (v2, superseded)

- **Scenario comprehension with an expert key**: about 25 claim scenarios per product line. A strong model
  reads the whole PDS to produce the key; a weak "consumer" model reads only the relevant passage.
  Readability is agreement with the key, so generosity cancels out.
- **Reader-ability ladder**: repeat at small, mid and flagship tiers. Readable documents saturate early.
- **Content-style transplant**: render insurer A's coverage in insurer B's house style across a Latin
  square, then fit comprehension against content source and style source.
- **Generosity leakage test**: regress judge preferences on the generosity difference between passages.

Superseded because a shopping agent extracts and compares whole coverage, not single scenarios.

## 3. Agentic coverage extraction (v3, superseded)

A frozen coverage ontology per product line (insured events, settlement basis, benefits and limits,
sub-limits, exclusions, excess structure, optional covers, conditions), each field allowing `not_stated`.

- **T1 extraction**: fill the schema from one full PDS with quotes and pages, as text and as native PDF.
- **T2 comparison**: rank four or five PDSs for a consumer profile with a field-by-field table.
- **T3 scenarios**: a small validation layer for the key.

Metrics: fidelity, over- and under-statement, findability failure, hallucination, self-consistency,
interpretive entropy across models (a key-free ambiguity signal), fidelity against model tier and effort,
and misrepresentation inside comparisons. Superseded by v4's tighter paired design; the ontology, the
over-statement metric and T2 survive as options 8 and later extensions.

## 4. Paired presentations A/B/B+/C (v4.1, active)

Home buildings, six bundles by twelve tasks by three models from different families, expanding to eight by
twenty once annotation throughput is measured. Each bundle-task-model is run in four fresh conditions:

| Arm | Input |
|---|---|
| A | Complete checked policy bundle, including applicable supplementary PDSs |
| B | All relevant original clauses, definitions and exceptions, verbatim |
| B+ | B at its original positions, padded with irrelevant text from the same bundle to A's length |
| C | The same evidence in a checked plain-language presentation whose structure does not mirror the response schema |

Primary outcome: correct answers with every material qualification. Primary contrast C minus B. B+ minus B
is the cost of context length, A minus B+ the cost of relevant-looking surroundings. Secondary: over- and
under-statement, unsupported claims, citation support, confidently-wrong rate and calibration. Uncertainty
by paired cluster bootstrap at template-family level. A draft task bank is in `tasks/`.

## 5 to 13. Candidate designs

Full specifications are in [EXPERIMENT_OPTIONS.md](EXPERIMENT_OPTIONS.md). In brief:

- **5. Wording by organisation factorial.** Two by two: original or plain wording, rules distributed or
  brought together. Estimates the wording effect, the organisation effect and their interaction.
- **6. Controlled policy changes.** A synthetic twin with one substantive change, such as 12 months to 6.
  Both answers must be right under their own keys. Includes meaning-preserving controls.
- **7. Supplementary documents.** Base PDS alone, base plus applicable supplement, and a consolidated text.
  Tests applying amendments, preserving unchanged rules and ignoring inapplicable supplements.
- **8. Single versus multiple policies.** One policy per request against four in one request with balanced
  orders. Measures omissions and facts attributed to the wrong insurer.
- **9. Sibling brands natural experiment.** Suncorp, GIO, AAMI and Apia, and the IAG brands, issue
  identical rules under different templates. Where the reference answer is verified identical, accuracy
  differences are attributable to the document alone. Needs no synthetic material, so it can run first.
- **10. Minimal-pair clause edits.** One edit per pair from a frozen catalogue: inline a cross-reference,
  expand a defined term, split a long sentence, remove a double negative, move an exception next to its
  rule, change list format, activate a passive. Output is a ranked, evidence-based drafting guide.
- **11. Dependency distance.** Place a qualifier adjacent to its rule, one page, five pages, twenty pages
  away, or in a supplement. Includes an absent-qualifier control. Output is a placement rule.
- **12. Navigating agent.** No text up front; tools for contents, search and reading one page, with a fixed
  step budget. Compare the insurer's own headings against a neutral page list. Agentic readability in the
  literal sense.
- **13. Paraphrase robustness.** Five phrasings per task (protocol, informal, scenario, negated, vague)
  against one cached context. Strict consistency across all five is the outcome.

## 14. Agent retrieval in the wild (new proposal)

Every design above starts with the document already in hand. A real agent first has to find and fetch it,
and [AGENT_READINESS.md](AGENT_READINESS.md) shows that this step fails for several insurers: NRMA and CGU
block agent user agents, Budget Direct and Coles block anything without a browser fingerprint, QBE hides its
document links behind pages that refuse scripted clients, and Real Insurance was down.

**Question.** Given "find the current home insurance PDS for insurer X", do real agent products return the
right document?

**Conditions.** Each of the 16 brands for home and car, run through real agent products rather than
simulated user agents: a ChatGPT agent mode, a Claude agent with web tools, a Perplexity or Comet agent, a
Gemini agent, and a self-hosted agent framework running a cheap open-weights model. Fresh session per
request, identical prompt, three repeats.

**Outcomes.**
- Retrieved the correct current base PDS.
- Also identified the applicable supplementary PDSs.
- Wrong document: superseded version, a target market determination, key facts sheet or another brand.
- Answered from a third-party summary or from memory without retrieving any document.
- Failed or refused, with the blocking response recorded where visible.

**Analysis.** Success rate by insurer and by agent, cross-tabulated against the access verdicts in
AGENT_READINESS.md. The key comparison is whether sites that block simulated agent user agents also defeat
real agents, or whether browser-driving agents get through regardless.

**Why it matters.** It measures the first point of failure in the consumer journey and is directly
actionable for insurers: a PDS that agents cannot retrieve gets summarised from somewhere else. It needs no
annotation beyond a list of current document versions, which the manifest already holds.

**Limitations.** Agent products change weekly and do not expose their full retrieval traces. Results are a
dated snapshot of named products, not of the underlying models.

## Recommended sequence

1. Sibling brands (9) and agent retrieval (14): cheapest, no synthetic material, publishable early.
2. Active v4.1 protocol (4) with paraphrase robustness (13) as an add-on.
3. Minimal-pair edits (10) and dependency distance (11) to explain the mechanism behind v4 results.
4. Navigating agent (12), then comparison (8) and supplements (7) as operational follow-ups.
