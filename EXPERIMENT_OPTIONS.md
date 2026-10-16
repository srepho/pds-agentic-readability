# Alternative experimental designs for consideration

These nine candidate designs investigate different reasons why models misread insurance PDSs. They
are options for a small home-buildings study, not additions automatically required by the active
[v4 protocol](EXPERIMENT.md). No option has been selected or preregistered.

The leading candidates are the sibling-brand natural experiment, which needs no synthetic material and
can run first, and the wording-by-organisation factorial for deciding what to change in a document.
Controlled policy changes could provide a small complementary test of whether models follow the
supplied rules. Supplementary-document and multi-policy experiments answer separate operational
questions and are best considered as distinct studies.

## Comparison of the options

| Design | Main question | Practical use |
|---|---|---|
| Wording and organisation | Do simpler wording, bringing related rules together, or their combination improve extraction? | Identify useful document edits |
| Controlled policy changes | Does the answer change when the supplied rule changes? | Test responsiveness to policy evidence |
| Supplementary documents | Can models apply amendments and distinguish applicable versions? | Evaluate document consolidation and version handling |
| Single versus multiple policies | Does comparison cause omissions or facts to be assigned to the wrong insurer? | Evaluate the reliability of comparison workflows |
| Sibling brands (natural experiment) | When the same underwriter issues the same rule under different brand templates, which template is extracted most faithfully? | Rank templates within a group with no synthetic rewriting |
| Minimal-pair clause edits | Which single editing moves (inline a cross-reference, split a sentence, remove a double negative, ...) improve extraction? | Produce a ranked, evidence-based style guide for machine-readable drafting |
| Dependency distance | How far apart can a rule and its qualifying exception or definition be before models stop linking them? | Set a placement rule for exceptions and definitions |
| Navigating agent | Given page, search and contents tools instead of the full text, how many steps does a model need to reach the correct rule, and do headings help? | Evaluate the navigational apparatus of a PDS as agents actually use it |
| Paraphrase robustness | Does the extracted answer stay correct when the same task is asked in different ways? | Measure robustness to how consumers phrase questions, at low marginal cost |

## Shared scope and safeguards

An illustrative small sample is home buildings from NRMA, Suncorp, Allianz and Budget Direct. Selection
would depend on complete applicable bundles and verified document/template diversity, not a claim that
these are the four largest insurers. Fix the policy date, jurisdiction where relevant, owner-occupied
configuration, one cover tier per insurer and selected options before constructing reference answers.
Retain schedule-dependent values as dependencies rather than inventing them.

Use two models from different vendors with frozen versions and settings, a separate development set,
fresh sessions for every condition, and randomised execution order. Keep task wording and response
format constant within a comparison. No response or reference answer from one condition is supplied
to another. Human reviewers verify all reference answers and independently check transformations.

Preserve source files, hashes, transformation instructions, evidence mappings and reviewer decisions.
Label altered policies as synthetic research materials, including unchanged controls in a synthetic
experiment so the label itself does not reveal the treatment. Keep synthetic findings separate from
claims about an insurer's actual cover. Do not resolve source ambiguity through a rewrite.

Use the v4 definition of task correctness: all requested material rules and qualifications must be
correct. Report citation support separately. Predefine handling of missing information, invalid outputs,
failed transformations and exclusions; retain an accounting of every selected case. Freeze eligibility
before looking at model outputs. Repeat a prespecified random subset to assess stochastic variation.

Treat policy-task observations and their variants as paired. Repeated model calls, clauses and synthetic
variants are not independent insurers. With four selected brands, show individual cases, model-specific
effects and descriptive uncertainty; avoid industry rankings or strong population-level significance
claims. Shared templates further limit independence.

## Wording and organisation factorial

### Question and conditions

Can wording and information organisation be changed separately, and does their combination help more
than either intervention alone? A two-by-two factorial supplies four versions of the same information:

| | Original wording | Plain-language wording |
|---|---|---|
| Distributed rules | Original placement of relevant clauses | Rewritten clauses in their original locations |
| Rules brought together | Original clauses relocated together | Rewritten clauses relocated together |

For a manageable pilot, start with a bounded document section or constructed text environment containing
the complete evidence chain and fixed surrounding material. Preserve all substantive content across
cells. Move clauses rather than duplicating them; duplication would introduce repetition as another
intervention. Keep unrelated material and its relative order fixed, and repair cross-references using
a consistent rule. Use stable source identifiers in every condition.

The same rewritten clauses must appear in both rewritten cells. The same relocation rule must apply
to both wording conditions. Otherwise the factors are not independently manipulated. Independently
verify every version for meaning preservation, numerical accuracy and intact exceptions.

### Outcomes and analysis

Let O_D and O_T be accuracy with original wording when rules are distributed or together, and P_D and
P_T the corresponding accuracies with plain wording. Calculate paired percentage-point differences:

- Wording effect: average of P_D minus O_D and P_T minus O_T.
- Organisation effect: average of O_T minus O_D and P_T minus P_D.
- Interaction: (P_T minus O_T) minus (P_D minus O_D).

A positive interaction would mean that the wording intervention helps more when related rules are
together. Retain negative effects and report both simple effects alongside averages. Freeze which
contrast is primary; a small pilot can treat the interaction as exploratory.

An illustrative grid is four bundles x six questions x two models x four conditions = **192 task
responses before repeats**, assuming one question per request and all cases eligible. This requires
24 reference cases and up to 96 reviewed input variants; annotation is more demanding than the call
count alone suggests.

### Interpretation and limitations

This is the strongest candidate for deciding what to change in a PDS. It can distinguish a useful
wording intervention from a useful organisation intervention. However, rewriting can change length
and relocating clauses changes position and context. The estimated effects belong to these specified
editing procedures, not to abstract linguistic simplicity or navigation in isolation. Record lengths
and positions rather than claiming those factors were held constant.

A bounded-section result does not establish full-document performance. Add an original full-bundle
baseline only as a separately labelled condition if that question is important; it is not one of the
four factorial cells.

## Controlled policy changes

### Question and conditions

Does a model track the actual supplied rule, including a rule that differs from familiar insurance
wording? Give each original passage or bundle a synthetic twin with one controlled substantive change.
Examples, purely illustrative, include changing a benefit from 12 months to 6 months, a limit from
10% to 5%, or a benefit from included to optional. Independently update the reference answer.

Check the entire supplied context for dependent statements. A nominally single-rule change may require
several consistent edits to definitions, tables or examples. Exclude cases where a coherent change
cannot be made, recording the reason before evaluation. Neither version should signal the expected
answer through an edit marker.

Include a separate meaning-preserving control, such as a checked paraphrase or harmless formatting
change. Predetermine which answers should change and which should remain invariant. Ask at least one
unaffected question where feasible to detect inappropriate spillover.

### Outcomes and analysis

Primary outcome: **both original and altered answers are correct under their respective keys**.
Simply producing different answers is insufficient. Report original accuracy, altered accuracy and
the rate at which an initially correct answer is correctly updated. The latter is conditional and
should not replace the all-pairs outcome.

For meaning-preserving controls, score correctness on both versions and report answer stability
separately: a model can be consistently wrong. Analyse limits, exclusions and optional-cover changes
separately when counts permit; do not pool semantically different edits without a fixed weighting rule.

### Interpretation and limitations

This is a compact test of responsiveness to evidence. Failure can reveal reliance on expectations,
missed details or difficulty interpreting the changed rule; it does not by itself prove memorisation.
Success does not establish complete understanding of the policy. Synthetic cases establish behaviour
under controlled edits, not error rates on unmodified insurer documents.

This design is compatible with the behavioural-testing distinction between changes that should preserve
an answer and changes that should alter it predictably; see [CheckList](https://aclanthology.org/2020.acl-main.442/).
[Context-faithful Prompting](https://aclanthology.org/2023.findings-emnlp.968/) provides related work on
following supplied context when it conflicts with prior model knowledge.

## Supplementary documents and amendments

### Question and conditions

Can a model apply an amendment to a base PDS and recognise when an amendment does not apply?

| Condition | Input | Reference answer |
|---|---|---|
| Base | Base PDS alone | Rule in the base document |
| Amended bundle | Base PDS plus an applicable supplement | Rule after applying the supplement |
| Consolidated | Checked text incorporating the applicable amendment | Same operative rule as the amended bundle |

For the base condition, explicitly ask what the supplied base document states, not what a current policy
covers. For the amended and consolidated conditions, specify the applicable policy date and configuration.
This prevents omission of a required supplement from being mistaken for a valid current-policy answer.

Include questions about both changed and unchanged provisions. An optional fourth condition supplies
a supplement outside its applicability period; the expected answer must follow the explicitly stated
dates. Freeze an applicability/precedence table, including commencement versus renewal rules where
relevant, before evaluation. Use synthetic amendments only where clearly labelled and independently
checked. Consolidation must preserve the effective meaning without adding explanatory answers.

### Outcomes and analysis

Measure correct application of changed provisions, preservation of unchanged provisions and correct
handling of inapplicable amendments. Compare amended-bundle accuracy with consolidated-text accuracy
against the same operative key. Use the base condition to test correct answer updating; do not interpret
its raw accuracy difference from the amended condition as a pure presentation effect, since substance
also changes.

### Interpretation and limitations

This design can show whether consolidation reduces version-handling errors. It evaluates evidence
integration and applicability reasoning as well as reading. Real amendments may be sparse or uneven
across insurers, so define eligibility before sampling and avoid a forced brand ranking. A supplemental
PDF is not automatically applicable merely because it is available on the insurer's website.

## Single policy versus multiple policies

### Question and conditions

Does joint comparison degrade extraction or cause a fact from one policy to be attributed to another?
Use the same four bundles and field questions in two settings: one policy per fresh request, or all
four policies in one fresh request with an explicit field-by-policy response structure. Keep per-policy
instructions and scoring criteria equivalent, allowing sufficient output space for four answers.

For the joint condition, use a balanced set of four orders so every bundle appears in each position
once. For example, ABCD, BCDA, CDAB and DABC balance position but not all neighbour or carryover effects.
Select and freeze the order scheme before outputs are seen; randomise execution order separately.
Ensure the full combined input fits each model's context window without truncation.

### Outcomes and analysis

Compare per-policy task correctness in the single condition with correctness averaged across the
prespecified joint orders. Report omissions, unsupported claims and confirmed attribution errors,
where an incorrect value matches a different supplied policy and its context supports that diagnosis.
Do not assume every shared number proves that information was transferred between policies.

Report position sensitivity separately. Joint answers share a request and must not be treated as
independent observations. Request counts also differ from scored-answer counts: one joint response
can contain four policy answers. Log both counts and retain the paired structure in analysis.

### Interpretation and limitations

This tests comparison workflows without requiring a subjective recommendation or utility function.
The intervention changes context length, information competition and output workload together. Describe
it as the effect of joint extraction, not a pure measure of writing quality or cross-policy interference.
A four-order design is a small position check, not exhaustive testing of all 24 document permutations.

## Sibling brands as a natural experiment

### Question and conditions

Several groups issue the same underlying policy under different brand templates. The Suncorp group home
PDSs for Suncorp, GIO and AAMI in the local collection were all prepared on 31 January 2025 by the same
manufacturer; Apia's home PDS is a further variant. IAG issues NRMA, CGU and RACV (via IMA) documents of
very different length and layout. Where the substantive rule for a task is verified identical across
sibling brands, the brands form a natural content-style transplant: same rule, different wording, layout,
ordering and length, with no synthetic rewriting and no meaning-preservation review of a constructed
artifact.

Conditions are the sibling brands themselves, using arm A (full checked bundle) and optionally arm B
(evidence packet) from the v4 protocol. Eligibility is per task: a task is eligible for a sibling set
only when the reference answers, including all material qualifications, are identical across every
sibling in the set after adjudication. Record and report the ineligible tasks; they are themselves
informative about where sibling products genuinely diverge.

### Outcomes and analysis

Primary outcome: task accuracy per sibling brand on the eligible task set, paired within task and model.
Report pairwise brand differences in percentage points inside each group, and the within-group spread.
Because the rule is fixed by construction, any accuracy difference is attributable to the document and
its surrounding material, not to coverage. Secondary: confidently-wrong rate and citation support per
brand; whether the same tasks fail across all siblings (a rule problem) or only in some (a template
problem).

### Interpretation and limitations

This is the cheapest design available: it requires only the existing bundles, the v4 reference records
and a sibling-identity check per task. Its result is directly actionable inside a group, which is where
document templates are actually decided. Limitations: the number of sibling sets is small (two groups
with three or four brands each in the current collection), brands within a group may differ in more than
template (for example target demographic or optional covers), and identical rules may be embedded in
different amounts of surrounding material, so length is a covariate rather than a controlled factor.
Results describe these templates, not plain language in general.

## Minimal-pair clause edits

### Question and conditions

Which individual editing moves make a clause easier for models to extract correctly? Rather than a whole
rewrite, each clause receives exactly one edit from a frozen catalogue, producing a minimal pair with the
original. Candidate moves, each defined operationally before any run:

- Inline a cross-reference (replace "see Section 12" with the referenced sentence).
- Expand a defined term in place (replace "we" or "accidental damage" with its definition once).
- Split one sentence of more than 40 words into two or three without changing content.
- Convert a double negative or "unless ... not" construction into a positive statement.
- Move an exception from a separate list to the sentence that states the rule it qualifies.
- Convert a prose list of conditions into a bulleted list, or the reverse.
- Replace a passive construction with an active one naming the actor.

Apply each move only where it is applicable; record applicability per clause. Each pair is checked for
meaning preservation, which is far simpler for a single edit than for a whole rewrite. The task and
response format are fixed; the model receives a short context containing the clause and its immediate
dependencies, identical across the pair except for the edit.

### Outcomes and analysis

Primary outcome: paired accuracy difference (edited minus original) per editing move, averaged over
clauses and models with equal weights. Report the number of eligible clauses per move. Secondary:
confidently-wrong rate per move, and whether moves interact when two are applied together on a small
subset (exploratory only). The output is a ranked table of editing moves with effect sizes and
denominators: an evidence-based style guide for machine-readable drafting.

### Interpretation and limitations

Short contexts make this design cheap to run and easy to review, and the per-move attribution is more
useful to a drafting team than knowing that a complete rewrite helps. Limitations: single edits may have
small effects that need many clauses to detect; effects in a short context may not transfer to a full
document where finding the clause is the harder problem; and the catalogue itself is a choice that
determines what the study can find. Use v4 arm B material as the clause source so results connect to the
main protocol.

## Dependency distance

### Question and conditions

Many extraction errors involve a rule and a qualifier (exception, definition, limit) that sit far apart.
How does accuracy decay with the distance between them? Take rule-qualifier pairs from the v4 evidence
packets and construct inputs in which the rule stays fixed and the qualifier is placed at controlled
distances: adjacent; roughly one page later; five pages; twenty pages; in a separately labelled
supplementary document appended after the main text. Fill the intervening space with checked, irrelevant
text from the same bundle so register and vocabulary are held constant. Include a condition with the
qualifier absent, whose correct answer is the unqualified rule, so models that invent qualifiers are
detected.

### Outcomes and analysis

Primary outcome: accuracy as a function of distance, per model, with the correct answer requiring the
qualifier. Fit a simple monotone curve per model and report the distance at which accuracy falls below a
prespecified level; report the absent-qualifier condition separately as a false-qualification rate.
Secondary: whether failures are omissions (qualifier ignored) or substitutions (a different qualifier
from the padding applied), which the padding text should be chosen to make detectable.

### Interpretation and limitations

The deliverable is a placement rule that a document designer can use: how close an exception must sit to
the rule it qualifies for agents to link them reliably. The construction is mechanical and cheap once the
evidence packets exist. Limitations: distance in tokens is not the only variable moved (intervening
material also changes), the padding is drawn from the same document and may contain competing rules, and
the result is specific to the context lengths and models tested. It is a controlled probe of one failure
mechanism, not a measure of a whole document.

## Navigating agent

### Question and conditions

Real agents rarely receive a whole PDS as context. They open a PDF, read the contents page, search for
terms and jump between pages. How navigable is a PDS for a tool-using agent? Give the model no document
text up front but three tools over the checked, page-labelled bundle: `contents()` returning the table of
contents and headings with page numbers; `search(term)` returning page numbers and short snippets; and
`read_page(n)` returning one page. Fix a step budget (for example twelve tool calls) and the same task
wording and response format as v4. Compare against arm A on the same tasks.

Two variants isolate the navigational apparatus: one where `contents()` returns the insurer's own table of
contents and headings, and one where it returns a neutral, uniform list of page numbers only. The
difference measures how much the insurer's own structure helps or hinders.

### Outcomes and analysis

Primary outcome: task accuracy within the step budget, paired with arm A. Secondary: number of tool calls
to a correct answer, pages read, whether the first `search` term matches the insurer's terminology (a
proxy for vocabulary alignment), and the rate of giving up or answering without reading the governing
clause. Report trajectories for a sample of tasks as qualitative evidence.

### Interpretation and limitations

This is agentic readability in the literal sense and the condition closest to how shopping agents will
operate. Its cost is moderate (several short calls per task rather than one long one) and it uses the
existing bundles directly. Limitations: results depend on the tool design and step budget, which are
choices; models differ in tool-use skill independent of the document; and the simulated tools are a
simplification of real PDF viewers and retrieval stacks. Freeze the tool definitions and budget before
the run and treat tool-use skill as a model property that the paired comparison with arm A partially
controls.

## Paraphrase robustness

### Question and conditions

Does a model's extraction stay correct when the same task is asked in different ways? For each v4 task,
freeze five phrasings: the protocol wording; a consumer's informal question; a scenario ("my pipe leaked
for months, am I covered?"); a negated form ("is gradual water damage excluded?"); and a vague form that
names the topic without specifying the detail. All five are answered against the same input (arm A or
B), with the reference answer unchanged. Because the long document prefix is identical across phrasings,
prompt caching makes the marginal cost of the extra four phrasings small.

### Outcomes and analysis

Primary outcome: the proportion of tasks answered correctly under all five phrasings (strict consistency),
alongside mean accuracy per phrasing. Secondary: which phrasing types fail most, whether negated phrasing
flips answers, and whether robustness differs by arm (does supplying evidence or a standardised rewrite
make answers more stable, not just more accurate?). Report per model.

### Interpretation and limitations

Consumers do not ask in protocol wording. A document whose rules survive paraphrase is more robustly
readable than one that yields the right answer only to the right question. The design is almost free to
add to v4 and needs no new reference material beyond checking that each phrasing targets the same
reference answer. Limitations: phrasings are a small sample of how people ask; negated and vague forms
may have legitimately different acceptable answers that the reference set must anticipate; and
inconsistency is a model property as well as a document property, so compare across documents within
model rather than across models.

## Decisions before adopting a design

Choose the research question first, then select one core design. For a first result with no construction
work, the sibling-brand natural experiment can run as soon as v4 reference records exist. For presentation
improvement, the factorial and the minimal-pair catalogue are the leading candidates, with minimal pairs
giving finer attribution and the factorial testing interaction. For document faithfulness, choose
controlled policy changes. For version handling or comparison reliability, choose the corresponding
operational experiment. The navigating agent is the design closest to real agent behaviour and is the
natural second study once v4 establishes baseline extraction performance. Paraphrase robustness is an
add-on to any of them.

Before replacing or extending v4, settle the exact bundles and tasks, intervention rules, human-review
arrangements, primary contrast, repeat schedule, output budget and analysis plan. Measure token usage
and annotation time on development cases. API cost alone understates the effort: constructing valid
variants and reference answers is the central preparation task.

If an option is adopted, update EXPERIMENT.md and PLAN.md explicitly and freeze the evaluation package
before running it. Until then, these remain candidate designs and v4 remains the active protocol.
