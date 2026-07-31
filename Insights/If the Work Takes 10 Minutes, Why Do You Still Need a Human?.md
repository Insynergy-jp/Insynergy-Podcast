---
title: If the Work Takes 10 Minutes, Why Do You Still Need a Human?
subtitle: Novo Nordisk, the Danish pharmaceutical company behind Ozempic, has been applying AI to the production of clinical study reports since the autumn of 2023.
slug: if-work-takes-10-minutes-why-human-judgment-remains
date: 2026-02-26
timezone: Asia/Tokyo
language: en
type: insight
status: published
category: Decision Design
author: Ryoji Morii
role: Founder & CEO
organization: Insynergy Inc.
name: Insynergy Insights
origin: english_original
tags:
- Decision-Design
- Decision-Boundary
- Human-Oversight
- Human-Judgment
- Accountability
- Responsibility
- Agentic-AI
- AI-Ethics
- Automation
- Financial-Systems
- Physical-AI
- Policy
- Leadership
audience:
- Executives
- Board Members
- CIOs
- CISOs
- Legal and Risk Leaders
- AI Governance Leaders
visibility: website
summary: Novo Nordisk, the Danish pharmaceutical company behind Ozempic, has been applying AI to the production of clinical study reports since the autumn of 2023. A clinical study report, or CSR, is a regulatory document summarizing the results of a drug trial. A single CSR can run up to 300 pages. It must meet exacting standards for data accuracy, terminological consistency, and regulatory compliance. Historically, a team of roughly 50 specialist writers produced these documents over a period of 10 to 12 weeks. Each...
key_claim: Decision Design is the deliberate structuring of judgment processes, responsibility allocation, and human-AI boundaries within an organization.
concepts:
- Decision Design
- Decision Boundary
- Human Judgment
- Agentic AI
- Responsibility
- Accountability
- AI Ethics
- Automation
relations: {}
aliases: []
reddit:
  enabled: false
  post_type: discussion
  flair: Decision Boundary
  target_subreddit: DecisionDesign
  external_link: true
  publish_after: null
  approval_required: true
---

# If the Work Takes 10 Minutes, Why Do You Still Need a Human?

## A Pharmaceutical Company's 10 Minutes

Novo Nordisk, the Danish pharmaceutical company behind Ozempic, has been applying AI to the production of clinical study reports since the autumn of 2023. A clinical study report, or CSR, is a regulatory document summarizing the results of a drug trial. A single CSR can run up to 300 pages. It must meet exacting standards for data accuracy, terminological consistency, and regulatory compliance. Historically, a team of roughly 50 specialist writers produced these documents over a period of 10 to 12 weeks. Each writer could complete an average of 2.3 reports per year. For decades, CSR production has been one of the pharmaceutical industry's most persistent bottlenecks.

Novo Nordisk developed an internal platform called NovoScribe, built on Anthropic's Claude models, Amazon Bedrock, and MongoDB Atlas. The system uses retrieval-augmented generation grounded in expert-approved text, combined with case-specific clinical variables, to produce regulatory-grade documentation. After deployment, the time required to generate a CSR draft dropped to 10 minutes. A process that once required 50 people and over 10 weeks now runs with a team of three.

As an efficiency story, the numbers speak for themselves. But the more important observation lies in what happens after those 10 minutes. The AI-generated draft is not submitted directly to regulators. It passes through domain expert review and formal approval. The AI writes. Humans read, evaluate, and sign. That process has been compressed, but it has not been eliminated.

This distinction carries implications well beyond the pharmaceutical industry.


## What Does It Mean for AI to "Do the Work"?

In February 2026, Anthropic released a major expansion of Claude Cowork, its AI productivity platform for enterprise knowledge workers. Cowork goes considerably further than a conversational interface. It reads and writes files on the user's local system, executes multi-step tasks, coordinates parallel workstreams, and passes context between applications including Excel and PowerPoint. Industry-specific plugin templates now cover HR, financial analysis, legal, engineering, operations, investment banking, and wealth management. Enterprises can build private plugin marketplaces tailored to their own workflows and institutional knowledge.

Kate Jensen, Anthropic's Head of Americas, described the ambition plainly: in 2025, Claude changed how developers work; in 2026, the same will happen across knowledge work as a whole. The framing is significant. AI is no longer positioned as a tool that assists. It is positioned as an agent that executes.

The relevant question, then, is not about capability. It is about accountability. When an AI agent plans a task, decomposes it into subtasks, runs them in parallel, and delivers a finished output, the result carries consequences. Someone must own those consequences. In most organizations today, the question of who that someone is — and under what structure they exercise judgment — has not been deliberately answered.

Cowork makes the user's level of involvement a matter of choice. Users can intervene at any point, or they can step away and return to completed work. This design embeds a judgment call: how much oversight is appropriate, and when does delegation become abdication? For individual users, this is a practical question. For organizations deploying AI agents at scale, it is a structural one.


## The Space Between Delegation and Abandonment

Return to Novo Nordisk. Waheed Jowiya, the company's Digitalization Strategy Director, described the impact of NovoScribe in specific terms: Claude helped cut writing times on CSRs by 90 percent, allowing documentation to move directly into human hands for review and approval. The phrasing matters. The AI output reaches human reviewers faster because intermediate steps have been eliminated. But the review itself — the act of a qualified expert evaluating the document, deciding whether it meets regulatory standards, and authorizing it for submission — remains intact.

This structure reflects an intentional design choice. Novo Nordisk did not automate the production of clinical study reports. It relocated judgment. The AI handles generation. Humans handle evaluation and accountability. The boundary between these two roles was drawn deliberately, not as an afterthought.

The reason is straightforward. A CSR determines whether a new drug can reach the market. Its accuracy is directly linked to patient safety. As Tobias Kröpelin of Novo Nordisk stated: report quality is critical, because patient safety demands that errors are not tolerated. The line between what the AI produces and what a human approves exists because the stakes require it.

The more uncomfortable observation is that this kind of deliberate line-drawing tends to occur only where external regulatory pressure forces it. In industries without comparable oversight — which is to say, in most of the enterprise landscape where AI agents are now being deployed — the boundary between delegation and abandonment is left undefined.


## Regulation Is Arriving

The ambiguity is not going unnoticed by regulators.

The European Union's AI Act, the most comprehensive AI regulation enacted to date, began applying its provisions on general-purpose AI models in August 2025. The majority of its regulatory framework will take full effect in August 2026, with high-risk AI system requirements reaching complete applicability in 2027. The Act's risk-based classification system places particular emphasis on human oversight requirements for AI systems operating in high-stakes domains.

Japan's government is updating its AI Business Operator Guidelines, with a draft expected by March 2026 that explicitly requires developers and deployers of autonomous AI agents to build in mechanisms ensuring mandatory human judgment — citing risks of malfunction and privacy violation in agentic systems.

These regulatory moves are part of a broader pattern. Across jurisdictions, the direction of travel is consistent: organizations deploying AI that acts autonomously will be expected to demonstrate that human judgment remains structurally embedded in the process. This expectation applies not only to regulated industries like pharmaceuticals and financial services, but increasingly to any enterprise using agentic AI in consequential workflows.

However, regulation provides an external framework. It tells organizations that human judgment must be present. It does not tell them how to structure that judgment internally. If an organization lacks an internal architecture for human decision-making in AI-augmented processes, regulatory compliance will produce nothing more than additional checkboxes. The form will be satisfied. The substance will be absent.


## The Absent Design

As AI agents become more capable, the question that surfaces is not what AI can do, but what humans are supposed to do in response to what AI has done. When a 10-to-12-week process compresses to 10 minutes, the task that disappeared was drafting. The task that remained was judgment: evaluating the output, determining its fitness for purpose, and accepting responsibility for the decision to act on it.

In most organizations, these residual human responsibilities have not been designed. The conversations surrounding AI adoption tend to focus on tool selection, use case identification, and cost reduction estimates. Questions about where judgment resides, who bears responsibility for AI-assisted decisions, and what happens when exceptions arise are typically deferred — or never raised at all.

In regulated industries, external forces compel organizations to confront these questions. But as AI agents penetrate knowledge work broadly, the same questions apply everywhere. The gap is not in AI performance. The gap is in the design of judgment itself.

One might argue that the Novo Nordisk case only works because it operates within a heavily regulated environment. But the causality runs the other way. Novo Nordisk did not design its judgment structure because regulation required it. It was able to deploy AI effectively within a regulated environment because it had designed the judgment structure first. The company can trust a 10-minute draft to move forward in the process because the questions of who reviews, by what criteria, and with what authority have already been answered.

This kind of design is needed everywhere AI agents operate — regardless of whether a regulator demands it. As agentic systems proliferate, the boundaries at which human judgment should engage will multiply, blur, and become invisible. What cannot be seen cannot be managed. What cannot be managed cannot be held accountable.

What is needed is not better AI literacy, nor a new governance committee. What is needed is a framework that treats judgment itself as a design object.


## Decision Design

Decision Design is the deliberate structuring of judgment processes, responsibility allocation, and human-AI boundaries within an organization. Its central structural element is the Decision Boundary: the explicitly defined line that determines what is delegated to AI and what is retained by humans, who holds authority at each point, and how that boundary is documented, maintained, and adapted over time.

**What Decision Design designs.** Decision Design addresses three layers. First, the judgment process: at which stage in a workflow does a human evaluate AI output, and at what level — interim review, final approval, or exception handling? Second, the allocation of responsibility: when an AI-assisted decision produces a consequence, who is accountable — the operator, the approver, or the executive who authorized the deployment? Third, the boundary itself: where the line sits between AI execution and human authority, whether that line is fixed or variable, and who has the authority to move it.

**What Decision Design is not.** Decision Design is not AI implementation consulting. It does not address which tools to select or which processes to automate. Tool selection is a prerequisite; Decision Design concerns the structure that follows. It is not generic corporate governance. Existing governance frameworks assume human-to-human decision chains. When an AI agent autonomously executes tasks within a business process, traditional governance structures cannot fully capture where judgment resides. Decision Design is also not AI ethics. Questions of fairness, bias, and transparency are important but distinct. Decision Design addresses a more operational concern: for a given AI output, who within the organization holds the authority, under what conditions, and with what accountability, to approve or reject it.

**What problems it addresses.** Decision Design responds to a set of structural problems that emerge when AI agents participate in organizational workflows. The first is responsibility diffusion — the growing difficulty of identifying, after the fact, who made a decision when AI proposed and a human approved. This is not merely a legal risk; it is an organizational learning problem, because an organization that cannot attribute decisions cannot learn from failures. The second is explainability risk — the inability to account for the rationale behind an AI-assisted decision when auditors, regulators, or counterparties ask. Novo Nordisk's use of retrieval-augmented generation grounded in pre-approved text exists partly to maintain output traceability. The third is review degradation — the tendency for human oversight to become ritualistic over time, as routine approval of AI outputs erodes the rigor of evaluation. When approval rates climb steadily, it may reflect improving AI accuracy, or it may reflect a review process that has quietly ceased to function. Without monitoring, the distinction is invisible. The fourth is boundary invisibility — the absence of any documented, maintained record of where human judgment is expected to engage. When boundaries are not explicit, they drift. When they drift, accountability becomes untraceable.


## Implementing Decision Boundaries

Moving from concept to practice, what does a Decision Boundary look like inside an organization? The following framework generalizes from cases like Novo Nordisk's CSR process into a structure applicable across enterprise functions.

**Structured human review workflow.** The foundational implementation is to classify all AI output as draft and to require human approval before it becomes a final deliverable or triggers a downstream action. To prevent this from becoming a rubber stamp, three elements must be specified. First, reviewer qualification: not anyone can approve. The reviewer must hold domain expertise relevant to the output. At Novo Nordisk, AI-generated clinical documents are monitored and adjusted by scientific domain experts in real time — not by general-purpose reviewers. Second, review granularity: approval should be defined at the appropriate level of specificity. A 300-page regulatory document may require section-level review where numerical accuracy and narrative interpretation demand different expertise. Defining granularity prevents the entire review from collapsing into a single, undifferentiated approval action. Third, rejection criteria: an approval process that lacks explicit grounds for rejection will, over time, degrade into a process that only approves. Documenting what constitutes a basis for rejection — and what workflow follows a rejection — is essential to maintaining the structural integrity of the review.

**Judgment log architecture.** Decision Boundaries require a record of the judgments made at each boundary. This means structured logging of what the AI produced, what inputs it operated on, who reviewed the output, when, and what action they took — approval, modification, or rejection. Where modifications were made, the log should capture what was changed and why. These records serve a dual purpose. They provide an audit trail for external compliance. They also function as a monitoring dataset: if approval rates trend upward over time, the log provides the evidence base to determine whether AI accuracy has improved or whether review discipline has eroded.

**Exception escalation protocol.** Not every AI output fits a standard approval workflow. Cases where the AI flags uncertainty, where the reviewer cannot reach a clear judgment, or where the output falls outside the scope of existing policy require a predefined escalation path. Without such a path, exceptions are handled ad hoc. Ad hoc decisions are rarely documented. Undocumented decisions cannot be reviewed, and recurring exceptions cannot be identified as systemic patterns requiring structural response.

**Explicit final responsible owner.** Each workflow involving AI output should identify a specific role — not a committee, not a department, but a defined position — as the final responsible owner of the decision to act on that output. This can be implemented by extending existing delegation of authority matrices to include AI-generated output categories. For each output type — documents, analytical results, client-facing communications, internal recommendations — the matrix specifies which role carries final sign-off authority. This documentation must be maintained as a referenceable record for internal audit, external regulatory review, and organizational accountability.


## What 10 Minutes Did Not Eliminate

Return to where this began. Novo Nordisk compressed the production of clinical study reports from over 10 weeks to 10 minutes. But when the work took 10 minutes, something remained that 10 minutes could not compress.

That something is the act of taking responsibility for what the document says. No matter how quickly an AI generates a draft, the decision to judge it adequate, to sign it, and to submit it to a regulatory authority rests with a human. That act does not take 10 minutes. It should not.

As platforms like Claude Cowork extend AI agency across the full spectrum of knowledge work, the number of tasks that can be completed in minutes will continue to grow. The question for every organization is whether the judgment and accountability structures surrounding those tasks will grow with them — or whether they will be left undesigned, assumed to exist simply because someone, somewhere, clicks "approve."

AI adoption is not the automation of work. It is the relocation of judgment. Where that judgment lands, within what structure, and in whose hands — these are design decisions. They are the decisions that Decision Design exists to address, and that the concept of the Decision Boundary makes visible, manageable, and accountable.

What accelerated was the task. What did not accelerate was the judgment. Embedding that distinction into organizational structure is the work that the age of AI agents requires.

---

## Sources

**Novo Nordisk / NovoScribe**

- Anthropic, "Novo Nordisk Customer Story"
  https://claude.com/customers/novo-nordisk
- MongoDB, "Novo Nordisk & MongoDB Atlas: Groundbreaking Time To Value Acceleration With A Clinical Study Report In Minutes"
  https://www.mongodb.com/solutions/customer-case-studies/novo-nordisk

**Claude Cowork**

- Anthropic, "Introducing Cowork" (January 12, 2026)
  https://claude.com/blog/cowork-research-preview
- Anthropic, "Get started with Cowork" — Claude Help Center
  https://support.claude.com/en/articles/13345190-get-started-with-cowork

**Regulatory Context**

- Nikkei, "Government to require 'mandatory human judgment mechanisms' for AI agents and physical AI" (February 15, 2026)
  https://www.nikkei.com/article/DGXZQOUA136YP0T10C26A2000000/
- Cabinet Office of Japan, "AI Basic Plan" (December 23, 2025, Cabinet Decision)
  https://www8.cao.go.jp/cstp/ai/ai_plan/aiplan_20251223.pdf
