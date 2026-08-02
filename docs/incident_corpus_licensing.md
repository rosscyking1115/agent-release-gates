# Incident corpus licensing: what can actually be redistributed

Settled 2026-08-02, before any case is authored, because whether transformed cases can be
**redistributed** decides whether the
[gate mutation adequacy benchmark](gate_mutation_benchmark_design.md) can ship at all. If
nothing can be redistributed, kill criterion 1 applies and the programme ends cleanly.

Every licence below was read from the source's own licence file or terms page on
2026-08-02 and is cited. This is a documented reading of published licence terms, not
legal advice.

## Answer

**Redistribution is possible.** Kill criterion 1 does not fire.

MITRE ATLAS alone supplies 57 Apache-2.0 case studies, and the AI Incident Database
supplies thousands of structured records under CC BY-SA 4.0. Between them the 40–60 case
floor is reachable with attribution obligations that are ordinary and satisfiable.

Two conditions attach, and both change how the corpus must be built:

1. **AIID's share-alike is infectious.** Any case derived from AIID's licensed collections
   must itself be CC BY-SA 4.0. This repository is MIT. The corpus therefore cannot live
   under the repository's licence; it needs its own licensed directory, and cases must be
   segregated by source licence.
2. **AIID's report text is excluded from the licence.** The narrative journalism — the
   part that would make a case concrete — is not redistributable. AIID supplies the
   skeleton, not the story.

The question that may still kill the programme is not licensing. It is whether these
sources describe *agent* failures with checkable invariants, or only model-level attacks
and narrative summaries. That is kill criterion 2, it is unresolved, and §6 says what to do
about it.

## Source by source

| Source | Licence | Verified | Redistributable? |
| --- | --- | --- | --- |
| MITRE ATLAS `atlas-data` | Apache-2.0 | Licence file read 2026-08-02 | **Yes**, with notice |
| AI Incident Database | CC BY-SA 4.0, report text excluded | Terms of use read 2026-08-02 | **Yes**, share-alike |
| AVID `avid-db` | MIT | GitHub licence metadata, 2026-08-02 | **Yes**, with caveat |
| AVID `avidtools` | Apache-2.0 | GitHub licence metadata, 2026-08-02 | Yes (tooling, not data) |
| `awesome-ai-agent-incidents` | MIT | Repository read 2026-08-02 | Index only, see below |
| `butterflylabs/ai-incidents` (HF) | Labelled CC BY 4.0 | Dataset page read 2026-08-02 | **Do not rely on it** |
| OECD AIM | No open-data licence found | Terms page returned HTTP 403 | **No** |

### MITRE ATLAS — Apache-2.0, the cleanest source

`dist/ATLAS.yaml` at `mitre-atlas/atlas-data` contains **57** case studies,
`AML.CS0000`–`AML.CS0056`, counted from the distributed YAML on 2026-08-02. The licence
file is plain Apache-2.0 with a MITRE copyright line; the README carries "©2021-2026 The
MITRE Corporation. ALL RIGHTS RESERVED. Approved for Public Release; Distribution
Unlimited."

*The audit that prompted this work said 68 case studies. The current distribution has 57.*
Either the count moved or it was wrong; 57 is what the file says today.

Apache-2.0 is permissive: derivative cases may be released under any compatible licence,
including MIT, provided the licence text and attribution are preserved and modified files
are marked as changed. **This is the source to prefer**, because it is the only one that
does not constrain the corpus's own licence.

### AI Incident Database — CC BY-SA 4.0, with the interesting part carved out

The terms of use place these collections under CC BY-SA 4.0: incidents, quickadd,
duplicates, taxa, classifications, entities, and entity relationships. Weekly point-in-time
snapshots are published in JSON, MongoDB archive, and CSV.

Explicitly **not** under the licence:

- **the `text` field of the reports collection** — the report bodies themselves;
- submissions (pre-processed reports);
- images and video (though the URLs to them are licensed).

Two consequences, and the second is the one that matters for corpus design:

**Share-alike is infectious.** CC BY-SA 4.0 requires derivatives to carry the same
licence. A case built from an AIID incident record is CC BY-SA 4.0, and no amount of
transformation changes that unless the case retains nothing protectable.

**The narrative is off the table.** The structured record gives you a title, a date,
entities, classifications, and links. The account of what actually happened lives in the
report text, which is excluded. A case author working from AIID gets a skeleton and must
invent the flesh — which is precisely the condition kill criterion 2 describes, and
precisely why `divergence_from_real_event` is mandatory in the
[transformation record](gate_mutation_benchmark_design.md#9-the-transformation-record).

### AVID — MIT, with a caveat that is not cosmetic

`avidml/avid-db` is MIT-licensed. `avidml/avidtools` is **Apache-2.0**, not MIT as the
audit stated.

The caveat: a repository licence covers what the repository's authors can license.
Record-level content quoted or adapted from third-party advisories, papers, or vendor
disclosures carries its own rights, which the repository's MIT grant cannot extend. Each
record used must be checked individually against its own cited source. MIT on the
container is necessary and not sufficient.

### `awesome-ai-agent-incidents` — an index, not a corpus

MIT, actively maintained, roughly 26 documented incidents across real-world incidents,
supply-chain attacks, infrastructure compromise, agent misalignment, and AI-assisted
attacks, plus 8 CVEs — all cited to public sources including vendor disclosures and
academic venues. Contribution rules require verifiable sources.

Its value is the **citations**, and the citations point at publishers whose rights must
each be cleared separately. Treat it as a discovery index for finding agent-era incidents
that ATLAS and AIID have not yet catalogued. Do not treat the summaries as redistributable
case material.

*The audit described a "Community AI Agent Incident Database, CC BY 4.0, 34 sourced
incidents." No source matching that description was found. This repository is the closest
match and its licence and count are different. The audit's item should be treated as
unverified.*

### `butterflylabs/ai-incidents` — a licence label that cannot be right

A Hugging Face dataset of roughly 5,810 incident rows, labelled **CC BY 4.0**, drawing
from arXiv, the AI Incident Database, the AI Alignment Forum, and news outlets.

**CC BY 4.0 is not compatible with CC BY-SA 4.0's share-alike.** AIID-sourced rows cannot
be relicensed downward to plain CC BY. Either the dataset is mislabelled or those rows are
being redistributed outside their licence.

A downstream aggregator's label does not override the upstream grant. Relying on it would
be inheriting someone else's licensing error — and it is the same defect class this
project exists to catch: a claim stated more broadly than the evidence supports. **Do not
use it as a licence basis.** Use it, if at all, only to discover incidents, then go to the
upstream record and comply with the upstream licence.

### OECD AIM — unusable until someone reads the terms

The AIM methodology page states that use "is subject to the terms and conditions found at
www.oecd.org/termsandconditions" and that copyrights and trademarks included in AIM "are
the property of their respective owners." No Creative Commons or open-data licence is
granted on that page.

Both OECD terms-and-conditions URLs returned **HTTP 403** to automated retrieval on
2026-08-02, so the terms themselves were not read. **That is a gap, not a clearance.** AIM
additionally aggregates third-party news whose copyright stays with its owners, so even
permissive OECD terms would not settle the underlying content.

**Treat AIM as unusable for redistribution.** Reopening it requires a human to read the
terms page and record what it says.

## What this means for how the corpus is built

1. **Code stays MIT. The corpus gets its own licence file.** Repository code and the
   corpus are separately licensed, and the corpus directory carries its own `LICENSE` and
   `ATTRIBUTION` files.

2. **Segregate cases by source licence.** The transformation record already requires a
   `source_license` field; it becomes load-bearing. Apache-2.0-derived and CC BY-SA-derived
   cases are tracked distinctly, and no single case mixes sources with incompatible
   obligations.

3. **Do not mix upward into a permissive case.** Permissive material (Apache-2.0, MIT) can
   be incorporated into a CC BY-SA 4.0 work. The reverse is not permitted. A case that
   touches AIID licensed content is CC BY-SA 4.0 and stays that way.

4. **Prefer ATLAS.** It is permissive, already structured, and imposes no licence on the
   corpus. Reach for AIID where ATLAS lacks coverage, and accept share-alike on those
   cases knowingly rather than by accident.

5. **Attribution is published, not implied.** Each case names its source record, the
   licence it was used under, the required attribution string, and the retrieval date.
   ATLAS use additionally preserves the Apache-2.0 licence text and marks modifications.

## The check that has not been done

Licensing is settled. **Executability is not.**

ATLAS case studies document attacks on machine-learning systems — evasion, poisoning,
model extraction, and similar. Many are not agent-with-tools incidents at all, and a case
that cannot be expressed as an agent, a tool inventory, an initial state, and a checkable
invariant cannot be a benchmark case however well-licensed it is.

Before any case is authored, someone must audit the 57 ATLAS case studies and a sample of
AIID records against the twelve families in the design and count how many are executable.
If fewer than 40–60 survive that audit, **kill criterion 2 fires and the programme ends on
executability rather than on rights.**

That audit is the next step. It is a reading task over public data, it requires no spend,
and it should be done before a single case is written.
