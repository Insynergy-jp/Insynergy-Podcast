---
title: 'The Architecture of Judgment: What a Japanese Deployment Reveals About the Missing Layer in Enterprise AI Agents'
subtitle: The console shows a draft message addressed to a customer whose Hokkaido itinerary has been disrupted by heavy snowfall.
slug: architecture-of-judgment-ai-agent-decision-design
date: 2026-02-16
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
- Human-in-the-Loop
- Human-Judgment
- Judgment-Architecture
- Accountability
- Responsibility
- Agentic-AI
- Automation
- Recruitment-AI
- Financial-Systems
- Physical-AI
- Leadership
audience:
- Executives
- Board Members
- CIOs
- CISOs
- Legal and Risk Leaders
- AI Governance Leaders
visibility: website
summary: The console shows a draft message addressed to a customer whose Hokkaido itinerary has been disrupted by heavy snowfall. The agent — not a person, but a software system — has already read the customer's inquiry, retrieved the booking record, checked the rail disruption status, applied cancellation-fee rules, and composed a reply explaining the refund terms. The message sits in a text box. Below it is a button labeled "Send."
key_claim: The console shows a draft message addressed to a customer whose Hokkaido itinerary has been disrupted by heavy snowfall. The agent — not a person, but a software system — has already read the customer's inquiry, retrieved the booking record, checked the rail disruption status, applied cancellation-fee rules, and...
concepts:
- Decision Design
- Decision Boundary
- Judgment Architecture
- Human-in-the-Loop
- Human Judgment
- Agentic AI
- Responsibility
- Accountability
- Automation
relations: {}
aliases: []
---

# The Architecture of Judgment: What a Japanese Deployment Reveals About the Missing Layer in Enterprise AI Agents

---

## The Send Button

The console shows a draft message addressed to a customer whose Hokkaido itinerary has been disrupted by heavy snowfall. The agent — not a person, but a software system — has already read the customer's inquiry, retrieved the booking record, checked the rail disruption status, applied cancellation-fee rules, and composed a reply explaining the refund terms.

The message sits in a text box. Below it is a button labeled "Send."

An operator — a person — is looking at the screen. The system has done the work. All that remains is a click.

It would be easy to treat this moment as trivial. The interesting engineering, one might assume, happened earlier: the language model parsing the customer's message, the system navigating multiple internal databases, the rule engine adjudicating cancellation eligibility. The button is a formality.

It is not. That button is the most deliberately designed component in the entire architecture. But explaining why requires stepping back to examine what is actually happening inside this system, and what it chose not to do.

---

## The Gap Between Capability and Accountability

The current discourse around AI agents is organized almost entirely around capability. Foundation models, tool use, multi-agent orchestration, autonomous workflows — these describe what AI systems can do. The trajectory is clear and the progress is real. Agents can parse language, navigate interfaces, retrieve data across systems, and compose coherent outputs in seconds.

What remains underdeveloped — and largely unnamed — is the architecture that governs where, within a real operational process, each type of judgment should reside. Not "what the model can do," but who decides, at which point, with what evidence, under what constraints, and with what accountability when the output is wrong.

This is not an abstract concern. During severe weather events, JTB's contact centers face inquiry volumes described as tens of times the normal rate. The operational case for automation is legitimate: every minute of human processing time costs real money, and customers waiting for resolution during a disruption are already dissatisfied. But customer-facing operations involving financial outcomes — refunds, cancellation fees, contractual obligations — are domains where a wrongly communicated fee waiver creates a binding expectation, a refund issued in error may be irrecoverable, and a message sent about the wrong booking compounds into a service failure costlier than the delay it was meant to prevent.

The question, then, is not whether to deploy an AI agent. It is how to design the judgment architecture around it. The JTB case offers a precise and instructive answer.

---

## The Structural Anatomy of JTB's Agent

The system was developed by JTB, Japan's largest travel company, as part of their submission to GENIAC-PRIZE, a program jointly administered by Japan's Ministry of Economy, Trade and Industry (METI) and the New Energy and Industrial Technology Development Organization (NEDO) to accelerate real-world deployment of generative AI applications. As reported by Nikkei xTECH, the agent handles customer inquiries submitted through JTB's "Contact Board," a web-based support channel for members, during weather disruptions.

JTB developed the agent in collaboration with KARAKURI, a Japanese AI company specializing in customer-support automation, adopting KARAKURI's large language model "KARAKURI VL" as the system's core LLM. The overall agent workflow was implemented in Python.

The structurally significant feature of this system is not its scope but its internal differentiation. The agent operates across three distinct internal systems, each accessed through a different method and assigned a different type of judgment authority.

The first is JTB's back-office system for managing travel-product information — a web-based application that the agent controls via Selenium, the browser-automation library. The second is the company's intranet, where transportation disruption information — primarily airline cancellations — is published as PDF documents; the LLM reads and interprets these documents directly. The third is a separate, purpose-built system for adjudicating rail disruptions, which the agent queries via API.

This third system deserves particular attention. JTB built a dedicated rule-based system — separate from the AI agent itself — specifically for determining whether a customer's booked rail segments are affected by reported disruptions. Rail networks in Japan involve complex route connections across multiple operators; determining whether a specific ticket's itinerary overlaps with a disrupted segment requires matching route data, station jurisdictions, and operator-specific cancellation policies. JTB's assessment was that current AI cannot reliably prevent misjudgment in this domain. The agent therefore receives a definitive answer from the rule-based system via API rather than generating a probabilistic one.

The customer-facing message is generated as a draft. The agent presents it for review alongside the evidence and reasoning that informed it. And the act of sending — the irreversible transmission of a message to a customer — remains with a human operator. As the Nikkei xTECH report states, the final confirmation of sending or executing is always performed by an operator.

Three design choices, then: a probabilistic AI for language interpretation and draft composition; a deterministic rule-based system, built independently, for rail adjudication; and a human operator holding authority at the irreversible action gate. These choices are not limitations awaiting future improvement. They are the architecture.

---

## Judgment Is Not One Thing

What makes this architecture legible — and what makes it portable to other domains — is the recognition that a single business process contains multiple judgment acts, each with distinct structural properties.

Inside a single cancellation-handling workflow, at least five are embedded.

Interpretation: understanding what the customer is asking. The message may be informal, ambiguous, or written in frustration. Parsing intent from natural language tolerates moderate ambiguity — misclassification at this stage is recoverable, and the system can request clarification. A language model's probabilistic reasoning is well-suited here.

Fact determination: is the customer's booked rail segment affected by a reported disruption? This is not interpretation. It requires deterministic matching of route data against disruption data, across operator boundaries and complex junction networks. This is why JTB built a separate rule-based system and why the AI agent queries it via API rather than attempting the determination itself.

Contractual adjudication: does this specific booking, under these specific terms, qualify for a fee waiver? This requires matching facts against rules. The logic is complex but deterministic. It needs to be traceable and auditable, because disputes about refund eligibility are common and may have regulatory implications.

Communication quality: is the draft message accurate, appropriately scoped, and does it promise only what the company can deliver? This benefits from human review precisely because a poorly worded communication carries reputational and potentially contractual consequences.

Execution authorization: should this message be sent? This is the irreversible action gate — the point at which the organization's distributed internal processing becomes an external commitment. Once transmitted, the message shapes the customer's expectations and may constitute a binding obligation.

Each of these judgment acts has a different tolerance for ambiguity, a different reversibility profile, and a different accountability requirement. Assigning all five uniformly to any single processing type — whether AI, rules, or human — is a design error. The structural insight is that judgment must be decomposed before it can be allocated.

The development lead, Wataru Goda of JTB's Data Intelligence Team, captured this precisely: the most important thing, he said, was not to hold a worldview of solving everything cleanly with AI, but to meticulously decompose business flows and articulate them fully. KARAKURI's Kensuke Muto reinforced the point: the key was decomposing tasks into their smallest units and rigorously examining whether each step should be handled by AI or by programmatic logic. This examination — not the model selection, not the framework choice — is what produced a viable operational agent.

---

## What "Human-in-the-Loop" Actually Requires

The structural analysis above reveals why "human-in-the-loop" is often an architectural claim that is formally true and operationally hollow. If the system is designed so that a human reviews AI output before an irreversible action, the claim is satisfied. But the claim says nothing about whether the human's judgment is effective.

The failure mode is well-documented in adjacent domains: automation complacency in aviation, automation bias in AI-assisted diagnostics. In enterprise AI-agent deployments, the equivalent is the rubber-stamp operator — a human who clicks "approve" reflexively because the system is usually right, the volume is high, and the time pressure is real.

The structural response is not to remove the human or to add more humans. It is to design the conditions under which human judgment at the irreversible action gate becomes real rather than ceremonial.

The information necessary to evaluate the AI's output must be presented alongside the output, not stored in a separate system the operator must navigate to. The rationale must be surfaced: if the draft says "your cancellation fee has been waived," the operator needs to see, at a glance, which rule was triggered, which disruption was referenced, which booking terms applied. Exception routing must be explicit — cases where the AI's confidence is low or the rule engine cannot adjudicate must enter a different workflow, not appear as normal cases with a slightly different flag. And audit artifacts must record not only what the human did but what information was presented to the human at the time. Without this, post-incident analysis produces blame, not learning.

JTB's design addresses these requirements. The message is a draft, not a fait accompli. The agent presents not only the draft response but also the evidence underlying its judgments. The operator's action — pressing "Send" — is a genuine authorization whose preconditions are architecturally specified.

This is not a "safety measure" bolted onto an autonomous system. It is the system's judgment architecture expressing itself at the point of highest consequence. HITL is not a person in the loop. It is evidence in front of a person at the moment of commitment.

---

## Decision Design and Decision Boundary

The structural pattern visible in the JTB case — judgment decomposition, differential authority assignment, irreversible action gating — is not ad hoc. It reflects a coherent architectural layer that is currently missing from the mainstream AI-agent discourse.

We call this layer Decision Design. Decision Design is the practice of treating judgment — not tasks, not workflows, not data flows — as the primary object of system architecture. It asks: within a given process, where are the judgment acts? What is the nature of each (probabilistic, deterministic, evaluative, authoritative)? What is the risk profile of each (reversible, irreversible, auditable, opaque)? And to which processing authority — AI, rule engine, human operator, escalation path — should each be assigned?

The operational unit of Decision Design is the Decision Boundary: the explicitly defined line between one judgment authority and another. A Decision Boundary specifies where the language model's responsibility ends and the rule engine's begins; where the rule engine's output is handed to a human for authorization; where a human's approval triggers an irreversible external action; and where an exception exits the normal flow and enters an escalation path.

Decision Boundaries are not guardrails. Guardrails constrain outputs — they filter, redact, or block certain responses. Decision Boundaries allocate authority — they determine which entity is responsible for which judgment, and they define the handoff protocol between entities.

Decision Boundaries are not workflow steps. Workflow design organizes tasks in sequence. Decision Design organizes judgments by their nature, risk, and accountability requirements. A workflow can proceed through five tasks, each containing a different type of judgment, all assigned to the same performer. Decision Design would examine whether each judgment is correctly assigned given its specific properties.

Decision Boundaries are not RPA. Robotic process automation replicates human actions on existing interfaces. Decision Design asks whether the human action being replicated involves a judgment that should be replicated, or one that should be preserved, restructured, or reassigned.

The absence of this layer explains a recurring pattern in enterprise AI deployments: technically functional agents that create organizational liability. The agent works — it completes the process, generates the output, reaches the endpoint — but no one has designed where accountability sits when the output is wrong. The result is a system that operates without a judgment architecture, and when it fails, the failure cascades into a vacuum.

---

## A Portable Architecture: From Structure to Method

The JTB case is instructive not because it is unique, but because its structure can be extracted as a repeatable method. Any organization deploying AI agents in consequential domains — customer service, claims processing, financial operations, regulatory compliance, procurement — faces the same architectural question: where should judgment reside?

The method has three phases: decomposition, allocation, and gate design.

**Decomposition** begins by identifying judgment nodes within the process — not tasks. A task is "draft a customer response." A judgment node is "determine whether this customer's booking qualifies for a fee waiver under the severe-weather exception clause." The distinction matters because automation planning typically operates at the task level, which obscures the judgment acts embedded within tasks. This is what Goda meant by decomposing business flows and articulating them fully — the decomposition target is not the workflow, but the judgments within it.

Each identified node is then classified by three properties. Tolerance for ambiguity: can this judgment tolerate probabilistic reasoning, or does it require deterministic resolution? Reversibility: if this judgment is wrong, can the outcome be corrected without external consequences, or does it create an irreversible commitment? Audit requirements: must the reasoning be reconstructable after the fact?

**Allocation** assigns each node to the appropriate judgment authority based on these properties. Nodes with high ambiguity tolerance and high reversibility are candidates for AI processing. Nodes with low ambiguity tolerance and high audit requirements are candidates for rule-based deterministic systems. Nodes that gate irreversible actions or require accountability assignment are candidates for human authority. Nodes that fall outside the designed coverage of any authority require explicit escalation routing.

In the JTB case, this allocation produced a three-layer architecture: the LLM handles message interpretation and draft composition; a separate rule-based system handles rail-disruption adjudication via API; and a human operator holds authority at the irreversible action gate. The critical design act was not choosing which AI model to use — it was deciding which judgments the AI model should not make.

Allocation also requires defining escalation paths. For each AI-assigned node, a confidence threshold below which cases route to human review. For each rule-based node, the conditions under which the rule engine cannot adjudicate — ambiguous inputs, missing data, novel scenarios — and the path those cases take. For each human-authority node, the conditions for escalation to a supervisor or specialist.

**Gate design** is the specification of the irreversible action gate itself — the point at which internal processing becomes an external commitment. This gate requires its own design artifact, distinct from the judgment nodes that precede it.

The gate specification defines what must be visible to the approver before execution: the AI-generated output in full; the key facts the system relied upon, with source attribution; the specific rules or conditions that were applied; any upstream flags or exception conditions; and confirmation that all upstream judgment nodes completed within their designed parameters. It defines the rejection path: rejection routes to exception handling, preserving the system's reasoning for review while enabling a human to compose or modify the response independently. And it defines the audit artifact: the approval action, including timestamp, approver identity, and the information state presented at the time of approval, logged immutably.

Two prose templates illustrate these artifacts at the node and gate level.

A **judgment node specification** defines: the node's identifier and plain-language description; inputs received (data, context, upstream outputs); expected output (classification, determination, draft, recommendation, authorization); certainty requirement — probabilistic or deterministic, with applicable thresholds; allowable actions (accept, flag, escalate, reject); escalation conditions; evidence requirements — supporting data that must be present, and what must be surfaced for downstream review; and the log artifact produced. In the JTB case, the rail-adjudication node would be specified as: "Determine whether the customer's booked rail segment is affected by a reported disruption. Input: booking record (rail segment details, operator, route), disruption data feed (affected lines, operators, segments). Output: binary determination (affected / not affected). Certainty requirement: deterministic — handled by dedicated rule-based system via API. Escalation: if segment data is ambiguous or disruption data is incomplete. Evidence: disruption source, operator, and timestamp recorded. Log: determination result, input snapshot, source reference, timestamp."

An **irreversible action gate checklist** confirms: the draft output is fully displayed and readable; the factual basis is visible alongside the draft, not in a separate system; the specific rules or exceptions applied are identified; upstream flags or exception conditions are prominently displayed; the approver has had sufficient time to review — the system does not auto-advance or time out into execution; a rejection path exists and routes to exception handling; and the approval action is logged with timestamp, approver identity, and information state.

---

## Why This Implementation Discipline Is Portable

The current generation of AI-agent frameworks — from LangChain and CrewAI to Anthropic's computer-use capabilities and Google's agent-building tools — provides increasingly powerful machinery for constructing autonomous workflows. The capability curve is steep. What lags behind is the accountability architecture.

This gap is not theoretical. As agentic AI moves from controlled demonstrations to live enterprise operations, the consequences of architectural neglect scale rapidly. A misclassified customer inquiry in a demo is a data point. A misclassified inquiry in production, processed through multiple systems, resulting in an incorrect financial communication sent to a real customer, is a liability event. When that event occurs across thousands of cases during a weather emergency, it becomes a systemic failure.

The implementation discipline visible in the JTB case — and in the broader GENIAC-PRIZE ecosystem, which explicitly targets real-world deployment and operational viability rather than model benchmarking — offers a distinctive orientation. KARAKURI's role is illustrative: the company developed "KARAKURI VL," a vision-language model designed specifically for computer-using agents in Japanese enterprise environments, through the GENIAC program. In the JTB case, KARAKURI VL served as the foundational LLM — but what made the system operational was not the model alone. It was the judgment architecture layered around it.

This orientation is not cultural essentialism. It is a practical, engineering-level discipline: when deploying autonomous systems in consequential domains, design the judgment architecture before scaling the capability.

There is, however, a structural reason why this discipline emerged where it did. Many Japanese enterprises have spent decades building and integrating complex back-office systems under a systems-integration (SI) culture that treats coherence with existing infrastructure as a non-negotiable design constraint. The JTB agent does not replace the booking system, the intranet, or the rail-adjudication engine. It operates across them — controlling one via Selenium, reading another's PDFs, querying a third through an API — because the design premise is coexistence, not substitution. In much of the global AI discourse, legacy systems are framed as obstacles to be bypassed or replaced. In the SI-informed engineering tradition common in Japanese enterprise IT, they are the operating environment into which new capabilities must be woven. This habit of designing for integration rather than displacement produces, almost as a byproduct, exactly the kind of boundary-aware architecture that Decision Design formalizes. What was once regarded as conservatism — the reluctance to rip and replace — turns out to be a structural advantage in an era where AI agents must coexist with deterministic systems, human authority, and organizational accountability.

The practices that characterize this discipline are portable. Pragmatic hybridization: combining probabilistic AI with deterministic rule systems within a single workflow — as JTB did by building a dedicated rail-adjudication system alongside its LLM-powered agent. Careful boundary placement: explicitly deciding, at each judgment node, which type of authority is appropriate and defining the handoff conditions. Operational safety as a design constraint: treating the irreversible action gate as a structural safeguard to be designed well, not a bottleneck to be eliminated. Accountability as architecture: ensuring that every judgment act produces a log artifact sufficient for post-incident reconstruction.

These practices do not slow deployment. They make deployment sustainable. An agent that processes ten thousand cancellation inquiries during a typhoon is only as valuable as the organization's ability to stand behind every communication it sends. That ability is not a product of model quality. It is a product of judgment architecture.

---

## Return to the Send Button

Consider the console again. The draft message. The button.

The operator has reviewed the AI-composed text. The system has surfaced the disruption data, the booking terms, the applied rules. The operator sees why this message says what it says. The operator decides: this is correct; this should be sent.

The click is not a formality. It is the moment at which the distributed judgment of the system — the language model's interpretation, the rule engine's determination, the human's evaluation — converges into an irreversible external action. The message leaves the organization's boundary. It reaches the customer. It creates an expectation, possibly a commitment, certainly a record.

This is the true agent boundary. Not the boundary between what AI can and cannot do — that boundary moves with every model release. The boundary that matters is the one between the system's internal processing and the organization's external commitments. The boundary between "we believe this is correct" and "we have told the customer this is correct."

Designing that boundary — specifying what must happen before the button can be pressed, what the person pressing it must see, what the system must log when they press it, and what happens when they choose not to — is Decision Design. The boundary itself is the Decision Boundary.

The agent's most important capability is not autonomy. It is knowing where to stop and who takes over.

The most valuable export from cases like this one will not be a model. It will be this architecture of judgment.

---

## References

- METI press release on GENIAC-PRIZE (May 2025)
- NEDO GENIAC-PRIZE official site
- Nikkei xTECH, "JTB develops itinerary-disruption AI agent that operates business systems" (February 16, 2026, by Tadao Gen; paywalled)
- KARAKURI press release on KARAKURI VL (July 2025)
- JTB Contact Board public guidance
