# Experiment design: LLM-judged readability of Australian insurance PDSs

## 0. The question
Which insurers write the most readable PDSs, does that differ by product line and by section,
and can LLM judges measure this more faithfully than classical formulas?

Formal hypotheses (pre-registered in this file before any scoring run):
- H1 Template effect: readability varies more between underwriting groups (IAG / Suncorp / A&G / Hollard ...)
  than between brands within a group.
- H2 Section effect: "General exclusions" and "Definitions" are the least readable sections industry-wide;
  "How to make a claim" is the most readable.
- H3 Judge validity: LLM pairwise judgments agree with human ratings better than Flesch-Kincaid does.
- H4 Brand bias: unblinded judges shift scores toward brand reputation; blinded judges do not.
- H5 (optional, longitudinal): post-2021 PDS versions are more readable than 2018-2020 versions of the same product.

## 1. Unit of analysis: matched sections, not whole documents
Whole-document scores confound length, structure and content mix. Instead, extract one passage per
*function* from every PDS so comparisons are like-for-like:

| Section key | What it covers | Why |
|---|---|---|
| `cover_summary` | The "what we cover" overview for the base cover | Core promise |
| `flood_storm` | Flood/storm/rainwater definitions and cover | Known pain point post-2022 floods |
| `general_exclusions` | General exclusions list | Densest legal text |
| `excess` | How excesses work | Numerical reasoning |
| `claims_process` | How to make a claim / how we settle | Procedural |
| `cancellation_cooling_off` | Cancelling, cooling-off, refunds | Consumer rights |
| `duty_disclosure` | Duty to take reasonable care / not misrepresent | Legally mandated wording, good control |
| `definitions_sample` | 10 defined terms sampled by fixed list (e.g. "accidental damage", "wear and tear", "market value") | Lexical complexity |

Rules: target 300-800 words; capture by heading match + LLM-assisted locator (Haiku 5.5 points to the page
range, human spot-check 10%). Store `passages.jsonl` with insurer, product, section, text, page range, word count.
Expect ~47 docs x 8 sections = ~350-380 passages.

### Blinding
Produce a `blinded_text` for every passage: replace brand names, group names, phone numbers, URLs and
ABNs with placeholders ("the insurer", "[phone]"). All primary judging uses blinded text; the unblinded
variant is used only for the H4 sub-experiment.

## 2. Three LLM measures (complementary, triangulated)

### 2a. Pairwise preference -> Bradley-Terry scale (primary measure)
Within each (product, section) cell, compare every pair of insurers' passages: "Which passage would a
typical Australian consumer find easier to understand and act on?" Output: winner + 1-sentence reason,
via structured output. Every pair is judged twice with positions swapped; a judgment that flips with
position is recorded as a tie. Fit Bradley-Terry per cell, then aggregate to insurer x product and
insurer overall with bootstrap CIs. Pairwise is used because absolute LLM scores compress and drift;
relative judgments are far more stable.

### 2b. Absolute rubric score (secondary, for interpretability)
1-7 on five dimensions, each with anchored descriptors in the prompt:
sentence clarity; vocabulary & jargon load; structure & navigability; transparency of what is NOT covered;
actionability (could the reader do the right thing after reading). Plus overall. Three repeats per passage
per model; report the mean and the within-passage SD (judge noise).

### 2c. Functional comprehension probe (does the text actually communicate?)
1. A strong model (Opus 5.5) writes 5 factual questions per passage with answers grounded in the passage
   (e.g. "Is damage from a slow leak covered?").
2. A weaker "simulated reader" (Haiku 5.5, effort low) answers those questions from the passage only.
3. Opus 5.5 grades the answers against the key.
Comprehension accuracy per passage is a behavioural readability measure independent of style judgments.
Caveat: questions are generated from the same passage, so this measures findability/clarity, not recall.

## 3. Judge validation (what makes this an experiment, not a vibe check)

### 3a. Synthetic manipulations with known direction
Take 40 passages. For each create: (i) a *degraded* version (merge sentences, add nominalisations and
passive voice, swap plain words for legalese, keep meaning identical) and (ii) an *improved* plain-English
rewrite (Opus 5.5 under a plain-language style guide, human-checked for meaning preservation).
A valid judge must rank improved > original > degraded. Report the hit rate per model. This is the
sensitivity test; a judge that fails it is dropped or down-weighted.

### 3b. Human anchor set
60 passage pairs rated by 3+ human reviewers with insurance domain knowledge in a simple web form, blinded.
Compute agreement of each LLM judge and of Flesch-Kincaid with the human majority (Cohen's kappa /
accuracy on pairs). This is the only true ground truth in the study; without it the LLM results are
uninterpretable as "readability".

### 3c. Consistency
- Position-swap consistency rate (2a).
- Repeat consistency (2b, three runs).
- Inter-model agreement: Krippendorff's alpha across judges.

### 3d. Brand-bias sub-experiment (H4)
Re-run 2b on 100 passages with unblinded text. Effect = unblinded minus blinded score, by insurer. If
AAMI/Budget Direct gain and smaller brands lose, that quantifies reputation leakage and justifies blinding.

## 4. Judge panel
| Role | Model | Notes |
|---|---|---|
| Primary judge | `claude-opus-5-5` | adaptive thinking, effort `medium` (set explicitly), structured outputs |
| Panel | `claude-sonnet-5-5`, `claude-haiku-5-5` | within-family capability gradient |
| Cross-vendor | one GPT and one Gemini model | are findings vendor-specific? |
| Simulated reader | `claude-haiku-5-5`, effort `low` | 2c only |

Fixed prompts, identical across models. Current Claude 5.5 models have no sampling controls, so repeat
runs measure inherent judge variance rather than temperature. Randomise passage order and pair order.

## 5. Controls and confounds
- Length: passages capped at 800 words; include word count as a covariate.
- Mandated wording: `duty_disclosure` is near-identical by law across insurers; it should show ~no spread
  and acts as a negative control.
- Combined PDS+FSG documents (RAC WA, RACQ travel, Everyday): exclude FSG pages before passage extraction.
- Product structure: AAMI splits building/contents; Budget Direct/Coles split car Part A/B; RACQ has one
  Household PDS. Passages are matched by function, so this is handled at extraction.
- Extraction noise: the current naive text has inflated sentence lengths (tables/bullets). Fix layout-aware
  extraction before any judging run.

## 6. Analysis plan
- Bradley-Terry ability per insurer per cell; aggregate with bootstrap CIs; league tables by product.
- Mixed model: rubric_score ~ group + product + section + words + (1|judge) + (1|passage) to test H1/H2.
- H3: pair-level accuracy vs human majority for each judge and for FK/Fog; McNemar test LLM vs FK.
- H4: paired difference unblinded - blinded by insurer.
- Convergent validity: Spearman between BT scale, rubric mean, comprehension accuracy, FK grade.
- Outputs: league tables, section heatmap (insurer x section), judge-validity table, brand-bias chart.

## 7. Phases and budget
| Phase | Work | Rough cost |
|---|---|---|
| P0 Pilot | 5 docs, Opus only, tune chunking and rubric anchors | < $10 |
| P1 Judge validation | 40 synthetic triplets + 60 human pairs; all judges | ~$20 |
| P2 Full pairwise | ~30 cells x ~100 pairs x 2 positions = ~6k calls x 5 judges, ~2k tokens each | Opus ~$50-60; panel ~$30; use Batches API (50% off) |
| P3 Rubric + comprehension | ~370 passages x 3 repeats x 5 judges; probes ~370 x 3 calls | ~$60-100 |
| P4 Brand bias | 100 passages x 2 conditions, Opus | ~$5 |
| P5 Longitudinal (optional) | older PDS versions for 6 brands | ~$20 |
Total likely $150-300. Cache the rubric/system prompt prefix; put passages after the cache breakpoint.

## 8. Implementation notes (Python, anthropic SDK)
- `scripts/segment_passages.py` -> `data/passages.jsonl` (+ blinded_text).
- `scripts/judge_pairwise.py`, `scripts/judge_rubric.py`, `scripts/judge_comprehension.py`: build requests,
  submit via `client.messages.batches.create`, key results by `custom_id`, write to `data/judgments/*.jsonl`.
- Structured outputs via `client.messages.parse()` with pydantic schemas for scores/choices.
- `scripts/analysis.py`: Bradley-Terry (choix or statsmodels), mixed model (statsmodels MixedLM), alpha
  (krippendorff), bootstrap.
- Log every request's model, prompt hash, passage id, usage; never overwrite judgments, append only.

---

# Design v2: separating substance from style

## The confound
A PDS passage has two things in it: **substance** (what is covered, limits, conditions) and **style**
(how that substance is written). Any judge, human or LLM, asked "which is easier to understand" will
partly answer "which cover do I like more" or "which one happened to answer my question". Price is not
in the PDS (it sits in the separate PED guide), so we strip any stray premium/discount text and ignore it.
Coverage must be controlled by design, not by instruction alone.

## Three mechanisms, in increasing elegance

### A. Measure the leakage (cheap, always do)
Extract a structured **coverage schema** per passage with a strong model: list of (event, covered?, limit,
conditions). From it derive a generosity index per passage. After judging, regress pairwise preference on
the generosity difference between the two passages. The coefficient is the judge's coverage-leakage; it
should be ~0 for a clean judge. Report it per model. Instructing judges to ignore generosity is necessary
but not sufficient; this measures whether it worked.

### B. Scenario comprehension with an expert key (the primary measure)
Readability as *information transmission*. Fix a bank of ~25 realistic claim scenarios per product line,
written once and reused across all insurers, e.g.
- Car: "A tree branch fell on my parked car in a storm." / "My car was stolen with the keys left inside." /
  "I lent the car to my unlisted 19-year-old nephew and he crashed it."
- Home: "A pipe leaked slowly inside a wall for six months." / "Floodwater from the river entered the house." /
  "My laptop was stolen from the car." / "A guest tripped on my stairs and broke an arm."
- Landlord: "Tenant stopped paying rent and left." / "Tenant's dog destroyed the carpet."
Each scenario is answered per PDS in two ways:
1. **Expert key**: a strong model (Opus 5.5, high effort) reads the *whole PDS* with care and returns
   covered / not covered / conditional, plus the clause citation. Human spot-check 20%.
2. **Consumer simulation**: a weaker reader (Haiku 5.5, effort low; also the small model from each other
   vendor) reads only the relevant passage, once, under a "you are an ordinary policyholder" prompt, and
   answers the same scenario with a confidence rating.
**Readability = agreement between consumer reading and expert key.** Coverage generosity cancels out
because both readings are scored against the same document's own truth. A PDS that says "not covered"
clearly scores just as well as one that says "covered" clearly. Add scoring for calibrated uncertainty:
the consumer saying "unclear from the text" when the expert also needed cross-references is a partial
credit, not an error.

**Reader-ability ladder.** Run the consumer simulation at three capability tiers (Haiku -> Sonnet -> Opus
at low effort). Plot accuracy vs reader tier per insurer. A readable PDS saturates early (weak readers
already get it right); an unreadable one needs a strong reader. The area under this curve is a single
interpretable readability number with a built-in sensitivity check.

### C. Content-style transplant (the factorial design that isolates style)
To attribute readability to *writing* rather than *what is written*:
1. From each insurer's passage take its coverage schema (content, C_i) and its passage as a style exemplar (S_j).
2. Have a strong model render content C_i in style S_j for all i != j in a Latin-square subset
   (e.g. 6 insurers -> 30 transplants per section cell instead of a full 15x15).
3. Verify meaning preservation with an entailment check (both directions, a different model from the
   writer) and discard failures.
4. Run measure B (comprehension) and the pairwise judge on the transplanted passages.
Fit comprehension ~ content_source + style_source + reader + (1|section). The style_source effect is the
readability of each insurer's *house style* with substance held constant; content_source captures how
inherently complex each insurer's cover is. If NRMA content in Youi style reads better than NRMA content
in NRMA style, that is an actionable finding for a plain-language programme.

## Judge panel: a range of LLMs
Use the current flagship and a mid/small tier from each vendor so capability is crossed with vendor:
| Vendor | Strong | Mid / small | Role |
|---|---|---|---|
| Anthropic | claude-opus-5-5 | claude-sonnet-5-5, claude-haiku-5-5 | expert key, judge, consumer tiers |
| OpenAI | current GPT flagship | current GPT mini | judge, consumer tiers |
| Google | current Gemini Pro | current Gemini Flash | judge, consumer tiers |
| Open-weights (via a hosted API) | e.g. current Llama / Qwen / DeepSeek flagship | a 7-9B model | consumer tiers; the small open model is the most "ordinary reader" proxy we can get |
Rules: one shared prompt per task; vendor-specific defaults left alone except reasoning effort set to the
vendor's "low" for consumer runs and "high" for expert key; never let the same model write the expert key
and act as consumer for the same passage without also running a cross-vendor key (the key itself is
checked for cross-vendor agreement; disagreements go to human adjudication).

## What "elegant" buys us
- Every number is anchored to the document's own truth (expert key), not to taste.
- Style and substance are separable via the transplant factorial.
- Leakage is measured, not assumed away.
- The reader-ability ladder turns "readability" into a curve with an obvious interpretation.
- Human effort is concentrated where it matters: spot-checking expert keys and rating a small pair set.

## Revised phase order
P0 pilot (5 PDSs, 10 scenarios, Anthropic only) -> P1 expert keys for all docs + cross-vendor check ->
P2 consumer simulation across the reader ladder and all vendors -> P3 pairwise judging + leakage test ->
P4 transplant factorial on 6 insurers x 3 sections -> P5 human anchor set -> analysis.

---

# Design v3: agentic readability (extraction and comparison, not scenarios)

## Reframe
The consumer of the future hands a personal agent five PDSs and asks "which covers me best?". The agent
must extract the coverage picture from each document and compare them. A PDS is *agent-readable* to the
extent that agents reconstruct what it says faithfully, completely and consistently. Readability is then a
property we can measure per document as **fidelity of machine reconstruction**, with coverage generosity
fully in scope for the agent but irrelevant to the score (the score is agreement with the document's own
truth, not preference).

## 1. Canonical coverage ontology (built once per product line, then frozen)
Union of what any PDS in the set addresses, normalised to one schema. Illustrative for Home:
- Insured events (~20): fire, storm, flood, rainwater run-off, escape of liquid (sudden / gradual), theft,
  burglary attempt, malicious damage, impact, earthquake, tsunami, landslide, lightning, explosion, riot,
  animal damage, accidental breakage of glass, motor burnout, power surge, trees falling.
- Settlement basis: sum insured vs total replacement vs safety-net %, new-for-old, matching materials.
- Additional benefits with limits: temporary accommodation (% / months), debris removal, rebuilding fees,
  locks & keys, food spoilage, mortgage discharge, environmental upgrades.
- Contents sub-limits: jewellery per item / aggregate, cash, collections, bicycles, items away from home.
- Exclusions: wear & tear, gradual deterioration, actions of the sea, unoccupied > N days, business use,
  tenant damage (for home), defects, pest damage, mould.
- Excess structure: basic, imposed, voluntary, special (earthquake, unoccupied).
- Optional covers: motor burnout, accidental damage, portable contents, flood opt-out, pet damage.
- Conditions: maintenance, security, notification periods, cooling-off days, cancellation refund basis.
Each field has a type: boolean / enum / number with unit / free text, plus allowed value `not_stated`.
Car and Landlord get their own ontologies (~60-90 fields each). A domain reviewer signs off the
ontology before any run.

## 2. Tasks
### T1 Extraction (primary)
Agent receives one full PDS and the schema; returns a filled schema with, per field: value, confidence,
verbatim quote, page. Run per (PDS x model x 3 repeats). Both input modalities: extracted text and the
native PDF (vision), to test whether layout helps or hurts machines.

### T2 Comparison (end-to-end realism)
Agent receives 4-5 PDSs for one product line plus a consumer profile ("I own a $900k house in a flood-prone
suburb, $20k of jewellery, two bicycles, work from home") and must produce a ranked recommendation with a
field-by-field comparison table. Scored against a key derived from the expert schemas plus the profile.

### T3 Scenario adjudication (validation layer, small)
~10 scenarios per product line to check that the expert schema key is right and to catch fields the
ontology missed. Not a primary metric.

## 3. Ground truth
Expert key per PDS: strong model at high effort fills the schema with citations; a second vendor's strong
model does the same; disagreements plus a 15% random sample go to human adjudication by a domain reviewer. The key
is the only place where human time is spent at scale. Keys are versioned and never edited after a run.

## 4. Metrics (per insurer x product, aggregated across agents)
- **Fidelity**: field-level accuracy vs key, weighted by field importance (consumer-harm weights set once).
- **Over-statement rate**: agent says covered / higher limit than the key (the harmful direction).
- **Under-statement rate**: the opposite; penalises conservative but wrong reading.
- **Findability failure**: agent returns `not_stated` when the key has a cited value.
- **Hallucination rate**: value with no supporting quote, or a quote not found in the document.
- **Self-consistency**: agreement across the 3 repeats of the same model.
- **Interpretive entropy**: disagreement across *different* models on the same field. This needs no key:
  if five capable models read the same clause five ways, the clause is ambiguous. A document-level
  ambiguity score independent of any judge's taste.
- **Reader-ability curve**: fidelity vs model capability tier (small -> flagship). Readable PDSs saturate
  early. Also fidelity vs reasoning effort: how much "thinking" does this document demand?
- **T2 misrepresentation**: how often is insurer X's cover misstated inside a comparison, and does the
  wrong ranking follow from it. This is the number an insurer should care about: "agents get us wrong".

## 5. Why this is clean
- Coverage generosity is what the agent is *supposed* to compare; the score never rewards it, only
  rewards getting it right. No leakage problem to control.
- Scenarios are no longer load-bearing, so no scenario-selection bias.
- The ontology makes every PDS answer the same questions, which is exactly how an agent would compare them.
- Interpretive entropy gives a key-free measure as a cross-check on the key-based one.
- The style/substance separation falls out naturally: fields where the key says `not_stated` across all
  insurers are substance gaps; fields where entropy is high only for some insurers are style problems.

## 6. Model range
Flagship + small tier from Anthropic, OpenAI, Google, and one open-weights family via a hosted API. Each
acts as agent in T1/T2 and as consumer-tier reader in the ability curve. Expert keys use two vendors'
flagships at high effort. One shared system prompt and schema across all vendors; structured output where
the vendor supports it, otherwise JSON-in-text with a validator and one retry.

## 7. Cost shape
T1 is the bulk: ~47 PDSs x 8 models x 3 repeats x 2 modalities = ~2,250 full-document reads at 20-40k
tokens each = ~60M input tokens across vendors, output ~5k each. Roughly $300-600 total at list prices,
about half with batch APIs. Reduce by running the PDF modality on 2 models only and repeats on 3.
T2: ~15 profiles x 3 product lines x 8 models = ~360 multi-document calls at ~120k tokens; ~$150.
Keys: ~47 x 2 vendors at high effort; ~$40.

## 8. Phases
P0 ontology drafts (model-assisted, user-approved) -> P1 expert keys + adjudication -> P2 T1 across all
models, text modality -> P3 PDF-modality ablation on 2 models -> P4 T2 comparison -> P5 scenarios +
human spot checks -> analysis and report. The v2 transplant factorial becomes an optional P6 to attribute
style effects once we know which fields are fragile.

## Note on model panel (market evidence, Oct 2026)
Consumer assistants: ChatGPT ~45-55% share, Gemini ~28%, Claude ~10% (Sensor Tower / Similarweb, mid-2026).
Agent users skew to Claude (Menlo/Morning Consult, n=5,067 US adults, Jul 2026: 48% of Claude users run agents).
Self-hosted personal agents (OpenClaw etc.) are model-agnostic and, by OpenRouter token volume, mostly run
cheap Chinese/open-weights models (MiniMax, DeepSeek Flash, GLM Flash). Implication: the panel must include
(a) the three consumer flagships, (b) their small tiers, and (c) at least two cheap open-weights models,
because that is what a real "find me the best cover" agent is most likely running.

## Agent platforms and the models underneath them (as at Oct 2026; third-party sourced, verify before publishing)
| Agent platform | Channel | Share of agent users (Menlo, Jul 2026) | Underlying model(s) | Confidence |
|---|---|---|---|---|
| ChatGPT Work (ex "Agent Mode"), Atlas browser | Consumer, OpenAI | n/a (ChatGPT ~46-55% of all assistant users) | GPT-5.6 at launch (Jul 2026); GPT-6 family rolling in | Medium |
| Codex (app / CLI / cloud) | Developer, OpenAI | 35% | GPT-6.1 Sol default (Oct 2026); GPT-6 Astra flagship, GPT-6 Luna fast | High (official changelog) |
| Claude Code / Cowork | Developer + knowledge-worker, Anthropic | 32% | Claude Opus 5.5 default; Sonnet 5.5 / Haiku 5.5 for subagents and fast paths | High |
| Perplexity Comet / Computer | Consumer browser agent | 24% | Claude Opus 4.6 default for the agent (Max tier, since Mar-Apr 2026); user-selectable Sonar, Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, Kimi K2.5 | Medium |
| Gemini app agent / Chrome Gemini | Consumer, Google | n/a (Gemini ~28% of assistant users) | Gemini 3.5 Flash is the app default; agent features on 3.5 / 3.6 Flash; new "Gemini agent" (Oct 2026) routes between Gemini and Claude | Medium-low |
| OpenClaw (self-hosted) | Prosumer, open source | 10-16% | Model-agnostic. Fresh-install default GPT-5.6 Sol (mid-2026); by token volume users mostly run MiniMax M3, DeepSeek V4 Flash, GLM Flash via OpenRouter | Medium (vendor blogs) |
| Hermes Agent (Nous) | Prosumer, open source | 10-16% | Model-agnostic; free Nous trial model on first run, then Nous Portal / OpenRouter; Hermes 4.x and Claude via OpenRouter common | Medium |
| Manus | Consumer/prosumer, hosted | 10-16% | Orchestration over Claude (Sonnet-class) plus fine-tuned Qwen; 2026 lineup not disclosed | Low (2025 sources) |
| Browser-use / custom LangGraph-style agents | Developer, DIY | not measured | Whatever the developer picks; OpenRouter volume says cheap Chinese/open-weights models dominate automated traffic | Medium |

Implied experimental panel (one row per "agent persona"):
1. Consumer-OpenAI: current GPT flagship + GPT mini
2. Consumer-Google: Gemini 3.5 Pro + Gemini 3.5 Flash
3. Consumer/Dev-Anthropic: claude-opus-5-5 + claude-sonnet-5-5 + claude-haiku-5-5
4. Perplexity-style: Claude Opus 4.6 (still the Comet default) - a useful "one generation back" point
5. Self-hosted cheap: DeepSeek V4 Flash, MiniMax M3, GLM Flash (via OpenRouter)
6. Open-weights mid: Qwen 3.x or Llama 4 class, as the Manus/DIY proxy
