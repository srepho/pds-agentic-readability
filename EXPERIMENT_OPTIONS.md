# Alternative experimental designs for consideration

These four candidate designs investigate different reasons why models misread insurance PDSs. They
are options for a small home-buildings study, not additions automatically required by the active
[v4 protocol](EXPERIMENT.md). No option has been selected or preregistered.

The leading candidate for improving document presentation is the wording-by-organisation factorial.
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

## Decisions before adopting a design

Choose the research question first, then select one core design. For presentation improvement, the
factorial is the leading candidate; for document faithfulness, choose controlled policy changes; for
version handling or comparison reliability, choose the corresponding operational experiment.

Before replacing or extending v4, settle the exact bundles and tasks, intervention rules, human-review
arrangements, primary contrast, repeat schedule, output budget and analysis plan. Measure token usage
and annotation time on development cases. API cost alone understates the effort: constructing valid
variants and reference answers is the central preparation task.

If an option is adopted, update EXPERIMENT.md and PLAN.md explicitly and freeze the evaluation package
before running it. Until then, these remain candidate designs and v4 remains the active protocol.
