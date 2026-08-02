# ATLAS executability audit: the incident corpus cannot be sourced

**Verdict: kill criterion 2 fires. The 12-family incident corpus in the
[gate mutation benchmark design](gate_mutation_benchmark_design.md) is not buildable from
the sources available, and the design is suspended.**

Audited 2026-08-02 against `dist/ATLAS.yaml` from
[`mitre-atlas/atlas-data`](https://github.com/mitre-atlas/atlas-data), Apache-2.0, all 57
case studies `AML.CS0000`–`AML.CS0056`. Per-study judgements are tabulated below so the
count is auditable rather than asserted.

## What was asked of each study

The [licensing answer](incident_corpus_licensing.md) established that redistribution is
possible. It left open the harder question: does a well-licensed incident description
contain enough to *execute*? Each of the 57 was judged on three things:

1. **Is it an agent-with-tools failure, or a model-level attack?** The gate under test
   decides whether an agent that holds tools may ship. An attack on a classifier has no
   agent, no tool inventory, and no action to gate.
2. **Can an environment, initial state, permitted actions and an oracle be reconstructed
   from what the study actually states** — not from what a reader could plausibly imagine?
3. **What would have to be invented, and does provenance still constrain the replay
   afterwards?** If every load-bearing detail is invented, the case is constructed and
   calling it incident-derived is the overclaim this project
   [corrected on 2026-08-02](../CHANGELOG.md) wearing a new coat.

## Result

| Judgement | Count |
| --- | --- |
| Total case studies | 57 |
| Agent-with-tools failures | 24 |
| Model-level attacks | 18 |
| Infrastructure, supply-chain or credential compromise | 12 |
| Human-in-the-loop fraud | 3 |
| **Executable — strict** | **19** |
| **Executable — including marginals** | **24** |

**Nineteen strict, twenty-four generous. The preregistered floor was 40–60.** The verdict
does not turn on where the marginal line is drawn: the generous count misses the floor by
sixteen.

Two further problems make it worse rather than better.

**Two of the twelve families have no source case at all.** Family coverage across the 24
executable and marginal studies:

| Family | Studies | | Family | Studies |
| --- | --- | --- | --- | --- |
| F01 Indirect prompt injection | 11 | | F07 System-prompt disclosure | 1 |
| F02 Direct instruction override | **0** | | F08 Memory poisoning | 3 |
| F03 Approval-gate bypass | 3 | | F09 Tool outside declared scope | 10 |
| F04 Irreversible action | 2 | | F10 Exfiltration to external sink | 7 |
| F05 Bulk automation at scale | **0** | | F11 Confused deputy | 2 |
| F06 Credential exfiltration | 3 | | F12 Invented action, weak evidence | 1 |

F02 and F05 cannot be populated from ATLAS at any threshold, and four more families rest
on one or two studies, some of them marginal. A 12-family design needs twelve families.

**The distribution is lopsided.** Eleven of twenty-four are indirect prompt injection and
ten involve a tool used outside its declared scope. A benchmark built from this would
measure two failure modes thoroughly and ten barely — the same shape of defect as the
current eight-case pack, at greater expense.

## Why the other sources do not rescue it

The instinct is to make up the shortfall from the AI Incident Database, which has
thousands of records under CC BY-SA 4.0. That does not work, and the reason is structural
rather than a matter of effort.

**AIID excludes report text from its licence.** The licensed collections give a title, a
date, entities, classifications and links. The account of *what actually happened* lives in
the `text` field of the reports collection, which is
[explicitly outside the grant](incident_corpus_licensing.md#ai-incident-database--cc-by-sa-40-with-the-interesting-part-carved-out).

So the source with the mechanism detail is the one that yields nineteen cases, and the
source with the volume withholds precisely the text needed to reconstruct an environment.
Building from AIID's structured records would mean inventing the environment, the tool
inventory, the initial state and the oracle from a title and a classification — which is
kill criterion 2 stated in its original words: *the only available incidents are narrative
taxonomies needing so much invention that provenance stops constraining the replay.*

The community index examined during the licensing check is a citation list of roughly 26
incidents pointing at publishers whose rights would each need clearing individually. It is
a discovery aid, not a supply.

## What this kills, and what it does not

**Killed:** the 12-family, 36-case corpus, and with it the three-way comparison against
`release-gate` and an eval-in-CI framework as designed. The design document stands as a
preregistration that reached its stopping condition before any case was authored, which is
what preregistration is for.

**Not killed:** the mutation-adequacy *method*. The
[pilot](gate_mutation_adequacy.md) already showed the metric discriminates — nine of
nineteen mutants changed the release decision, so kill criterion 6 does not fire — and the
finding it produced is about gate design, not about corpus size. What dies is the claim
that the method can be demonstrated across *sourced* incidents at the scale a comparative
study needs.

**Not killed:** the specific defects the pilot found in this project's own gate. Those are
real, they are in this repository, and repairing them is now ordinary engineering rather
than a research prerequisite.

## What would reopen it

Recorded so the decision is revisitable rather than final by default.

- **Agent incidents are accumulating fast.** Of the 24 agent-with-tools studies, the large
  majority are dated 2024 or later, and ATLAS added agent-specific techniques
  (`AML.T0053`, `AML.T0085`, `AML.T0086`, `AML.T0101`) to describe them. Re-running this
  audit against a later ATLAS release is cheap and the count is rising.
- **A smaller study is still possible now.** Nineteen executable cases will not support
  twelve families with holdouts, but they would support a narrower question over the two
  families ATLAS covers deeply. That is a different study and would need its own
  preregistration, not an amendment to this one.
- **If AIID ever licenses report text**, or a corpus emerges with mechanism-level detail
  under a redistributable licence, the volume problem disappears.

## Per-study judgement

Source: `dist/ATLAS.yaml`, `mitre-atlas/atlas-data`, retrieved 2026-08-02. Case names are
MITRE's; the class, executability and judgement columns are this audit's.

| Case | Name | Class | Executable | Family | Judgement |
| --- | --- | --- | --- | --- | --- |
| `AML.CS0000` | Evasion of Deep Learning Detector for Malware C&C Traffic | model | no | — | Adversarial samples against a malware classifier. No agent, no tools, no action to gate. |
| `AML.CS0001` | Botnet Domain Generation Algorithm (DGA) Detection Evasion | model | no | — | Domain-name mutation against a DGA classifier. Classifier evasion only. |
| `AML.CS0002` | VirusTotal Poisoning | model | no | — | Training-data poisoning of a sharing platform. No agent runtime. |
| `AML.CS0003` | Bypassing Cylance's AI Malware Detection | model | no | — | Universal bypass string appended to a file. Classifier evasion only. |
| `AML.CS0004` | Camera Hijack Attack on Facial Recognition System | fraud | no | — | Physical camera hijack against face authentication. No agent, no tool inventory. |
| `AML.CS0005` | Attack on Machine Translation Services | model | no | — | Model extraction plus transferred adversarial examples via an inference API. |
| `AML.CS0006` | ClearviewAI Misconfiguration | infra | no | — | Misconfigured repository exposing credentials. Ordinary infrastructure failure. |
| `AML.CS0007` | GPT-2 Model Replication | model | no | — | Model replication from published artifacts. |
| `AML.CS0008` | ProofPoint Evasion | model | no | — | Copy-cat model used to craft evasive email. Classifier evasion only. |
| `AML.CS0009` | Tay Poisoning | model | no | — | Conversational retraining, not tool use. The invariant concerns learned outputs, not an action. |
| `AML.CS0010` | Microsoft Azure Service Disruption | infra | no | — | Red-team exercise combining account discovery and model evasion. No agent decision to gate. |
| `AML.CS0011` | Microsoft Edge AI Evasion | model | no | — | Automated image manipulation to force misclassification. |
| `AML.CS0012` | Face Identification System Evasion via Physical Countermeasures | model | no | — | Physical-domain evasion of a face identification service. |
| `AML.CS0013` | Backdoor Attack on Deep Learning Models in Mobile Apps | model | no | — | Backdoor injected into models shipped inside mobile apps. |
| `AML.CS0014` | Confusing Antimalware Neural Networks | model | no | — | Gray-box adversarial attack on an antimalware model. |
| `AML.CS0015` | Compromised PyTorch Dependency Chain | infra | no | — | Dependency-confusion supply-chain compromise. No agent. |
| `AML.CS0016` | Achieving Code Execution in MathGPT via Prompt Injection | agent | **yes** | F06/F09 | Agent converts a question to Python and executes it; injection reaches environment variables and an API key. Tool inventory is stated; invariant and oracle follow directly. |
| `AML.CS0017` | Bypassing ID.me Identity Verification | fraud | no | — | Human identity fraud against an automated verification process. |
| `AML.CS0018` | Arbitrary Code Execution with Google Colab | infra | no | — | A human executes a shared notebook. No agent makes the decision. |
| `AML.CS0019` | PoisonGPT | model | no | — | Poisoned model published to a public hub. |
| `AML.CS0020` | Indirect Prompt Injection Threats: Bing Chat Data Pirate | agent | **yes** | F01/F10 | Browsing-enabled assistant reads an attacker-controlled page and exfiltrates user information. Environment, permitted actions and oracle all derivable. |
| `AML.CS0021` | ChatGPT Conversation Exfiltration | agent | **yes** | F01/F10 | Indirect injection makes the assistant embed conversation text in an outbound image URL. Oracle is an outbound request carrying conversation content. |
| `AML.CS0022` | ChatGPT Package Hallucination | agent | marginal | F12 | Hallucinated package name acted on by an install step. Executable only if an install tool is invented; the study describes the hallucination, not an agent's tool inventory. |
| `AML.CS0023` | ShadowRay | infra | no | — | Unauthenticated remote execution in a compute framework. |
| `AML.CS0024` | Morris II Worm: RAG-Based Attack | agent | **yes** | F01/F08/F10 | RAG email assistant ingests a self-replicating prompt and leaks user data in a generated reply. Mechanism fully stated. |
| `AML.CS0025` | Web-Scale Data Poisoning: Split-View Attack | model | no | — | Web-scale dataset poisoning via expired domains. |
| `AML.CS0026` | Financial Transaction Hijacking with M365 Copilot as an Insider | agent | **yes** | F01/F11 | RAG-poisoning email overrides enterprise search and forges a citation to steer a wire transfer. The payload is published verbatim, so the oracle is unusually well constrained. |
| `AML.CS0027` | Organization Confusion on Hugging Face | infra | no | — | Impersonated organization accounts on a model hub. |
| `AML.CS0028` | AI Model Tampering via Supply Chain Attack | infra | no | — | Exposed container registries permitting model tampering. |
| `AML.CS0029` | Google Bard Conversation Exfiltration | agent | **yes** | F01/F10 | Shared document carries an injection; assistant renders an image URL embedding the conversation. |
| `AML.CS0030` | LLM Jacking | infra | no | — | Stolen cloud credentials resold as model access. |
| `AML.CS0031` | Malicious Models on Hugging Face | infra | no | — | Malware embedded in published model files. |
| `AML.CS0032` | Attempted Evasion of ML Phishing Webpage Detection System | model | no | — | Modified brand logos evading an image-classifier ensemble. |
| `AML.CS0033` | Live Deepfake Image Injection to Evade Mobile KYC Verification | model | no | — | Deepfake injection against liveness verification. |
| `AML.CS0034` | ProKYC: Deepfake Tool for Account Fraud Attacks | fraud | no | — | Commercial deepfake tooling for KYC bypass. |
| `AML.CS0035` | Data Exfiltration from Slack AI via Indirect Prompt Injection | agent | **yes** | F01/F10 | Public-channel post poisons the assistant's retrieval; a private-channel secret is rendered into a clickable outbound link. Payload published. |
| `AML.CS0036` | AIKatz: Attacking LLM Desktop Applications | infra | no | — | Authentication tokens dumped from desktop application memory. |
| `AML.CS0037` | Data Exfiltration via Agent Tools in Copilot Studio | agent | **yes** | F01/F10 | Customer-service agent with a mail tool and CRM access is induced to exfiltrate customer records. Tool inventory explicitly enumerated. |
| `AML.CS0038` | Planting Instructions for Delayed Automatic AI Agent Tool Invocation | agent | **yes** | F01/F09 | Injection defers tool invocation to a later turn, defeating a same-turn restriction. A named control being bypassed is exactly this benchmark's subject. |
| `AML.CS0039` | Living Off AI: Prompt Injection via Jira Service Management | agent | **yes** | F11 | External support ticket processed by an internal agent holding elevated privileges. Textbook confused deputy; environment and privilege boundary are stated. |
| `AML.CS0040` | Hacking ChatGPT’s Memories with Prompt Injection | agent | **yes** | F08 | Injection in a shared document is written into persistent memory and survives across sessions. Oracle is persistence of an untrusted instruction. |
| `AML.CS0041` | Rules File Backdoor: Supply Chain Attack on AI Coding Assistants | agent | marginal | F09 | Poisoned assistant configuration steers generated code. Executable, but the oracle is 'the emitted code contains a backdoor', which needs an invented judgement step. |
| `AML.CS0042` | SesameOp: Novel backdoor uses OpenAI Assistants API for command and control | infra | no | — | Malware using a model API as a command-and-control channel. |
| `AML.CS0043` | Malware Prototype with Embedded Prompt Injection | model | no | — | Injection embedded in malware to fool an LLM analysis tool. Target is a classifier, not an agent. |
| `AML.CS0044` | LAMEHUG: Malware Leveraging Dynamic AI-Generated Commands | infra | no | — | Malware calling a model endpoint to generate host commands. |
| `AML.CS0045` | Data Exfiltration via an MCP Server used by Cursor | agent | **yes** | F01/F03/F06 | Scraping tool returns an injection; the agent runs a shell command exfiltrating credential files. The study records a user confirmation prompt in front of it, so the approval boundary is stated rather than invented. |
| `AML.CS0046` | Data Destruction via Indirect Prompt Injection Targeting Claude Computer-Use | agent | **yes** | F04 | Injection in a PDF drives a destructive filesystem command through the agent's shell tool. The clearest available instance of an irreversible action taken without confirmation. |
| `AML.CS0047` | Code to Deploy Destructive AI Agent Discovered in Amazon Q VS Code Extension | agent | **yes** | F03/F04 | An agent deployed with all tools trusted and prompted to delete local and cloud resources. The deployment command and the prompt are both published. |
| `AML.CS0048` | Exposed ClawdBot Control Interfaces Leads to Credential Access and Execution | agent | marginal | F07/F09 | Agent discloses its system prompt and executes shell via a skill. Executable, but initial access is an infrastructure exposure that would have to be invented away. |
| `AML.CS0049` | Supply Chain Compromise via Poisoned ClawdBot Skill | agent | **yes** | F09 | A poisoned third-party skill from a registry causes outbound shell execution. Tool provenance is the invariant. |
| `AML.CS0050` | OpenClaw 1-Click Remote Code Execution | agent | marginal | F03 | Agent configuration is modified to disable user confirmation. Directly on topic, but the attack is a web-session hijack; the agent-side property is config integrity rather than agent behavior. |
| `AML.CS0051` | OpenClaw Command & Control via Prompt Injection | agent | **yes** | F08/F09 | Web content causes a script to plant persistent instructions into future system prompts, turning the agent into a controlled implant. |
| `AML.CS0052` | LLMSmith: RCE Vulnerabilities in LLM-Integrated Applications | agent | marginal | F09 | Injection reaching a code interpreter across 11 frameworks. The mechanism is stated but no single environment is; every concrete case would be invented. |
| `AML.CS0053` | Poisoned Postmark MCP Server Email Exfiltration | agent | **yes** | F09/F10 | A tool's behavior changes under the agent: the poisoned package silently adds a BCC recipient. A tool-route change in the wild, which is one of the mutation operators. |
| `AML.CS0054` | Data Exfiltration via Remote Poisoned MCP Tool | agent | **yes** | F01/F06/F09 | A tool's own description carries instructions; the agent reads credential files and passes them as arguments. Tool metadata as instruction authority. |
| `AML.CS0055` | AI ClickFix: Hijacking Computer-Use Agents Using ClickFix | agent | **yes** | F01/F09 | Computer-use agent is socially engineered into pasting and executing a clipboard command. |
| `AML.CS0056` | Model Distillation Campaigns Targeting Anthropic Claude | model | no | — | Distillation campaign against a frontier model API. |

©2021-2026 The MITRE Corporation. ATLAS case-study identifiers and names are used under the
Apache License 2.0. This audit reproduces no ATLAS case-study text.
