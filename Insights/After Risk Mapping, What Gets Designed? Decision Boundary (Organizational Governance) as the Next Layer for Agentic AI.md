---
title: After Risk Mapping, What Gets Designed? Decision Boundary (Organizational Governance) as the Next Layer for Agentic AI
subtitle: Decision Boundary (organizational governance)
slug: decision-boundary-organizational-governance-agentic-ai
date: 2026-03-01
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
- EU-AI-Act
- AI-Governance
- Decision-Design
- Decision-Boundary
- Decision-Logs
- Human-in-the-Loop
- Human-Oversight
- Human-Judgment
- Decision-Authority
- Accountability
- Responsibility
- Organizational-Design
- Agentic-AI
- Financial-Systems
- Policy
audience:
- Executives
- Board Members
- CIOs
- CISOs
- Legal and Risk Leaders
- AI Governance Leaders
visibility: website
summary: Reading UC Berkeley's "Agentic AI Risk-Management Standards Profile" — and identifying what it leaves unbuilt. Agentic AI AI systems that use reasoning to autonomously pursue goals through interaction with external environments and tools. This includes both single-agent systems and multi-agent systems (MAS) where multiple agents coordinate toward broader objectives. Agency exists on a spectrum; it is not a binary attribute.
key_claim: It is a recognition that risk management and decision design operate at different layers of organizational architecture, and that the field needs both.
concepts:
- Decision Design
- Decision Boundary
- Decision Log
- Decision Authority
- AI Governance
- Human-in-the-Loop
- Human Judgment
- Agentic AI
- Organizational Design
- Responsibility
- Accountability
relations: {}
aliases: []
---

# After Risk Mapping, What Gets Designed? Decision Boundary (Organizational Governance) as the Next Layer for Agentic AI

*Reading UC Berkeley's "Agentic AI Risk-Management Standards Profile" — and identifying what it leaves unbuilt.*

---

## TL;DR

- UC Berkeley's CLTC published the "Agentic AI Risk-Management Standards Profile" in February 2026, establishing the first systematic risk framework specifically for autonomous AI agents.
- The profile shifts AI governance from model-level evaluation to system-level risk management, identifying three agent-specific failure modes: cascading failures, accountability diffusion, and goal drift.
- Governments worldwide — including the EU, Japan, and the US — are converging on mandating human oversight mechanisms for agentic AI systems.
- However, mandating human-in-the-loop does not resolve the structural question of where judgment authority is allocated between humans and AI agents.
- Decision Boundary (organizational governance) addresses this gap by making the allocation of judgment authority an explicit design object within organizational architecture.
- The next governance challenge is not whether humans oversee AI, but how organizations design the boundaries of decision authority across human and autonomous actors.

---

## Definitions

**Agentic AI**
AI systems that use reasoning to autonomously pursue goals through interaction with external environments and tools. This includes both single-agent systems and multi-agent systems (MAS) where multiple agents coordinate toward broader objectives. Agency exists on a spectrum; it is not a binary attribute.

**Cascading failures**
A failure mode in which erroneous or hallucinated outputs from one agent propagate to other agents or systems, amplifying into system-wide dysfunction. In multi-agent environments, a minor error in one agent becomes an input consumed by others, compounding across the system.

**Accountability diffusion**
A condition in which the autonomous, multi-step behavior of AI agents makes it structurally difficult to attribute outcomes to specific actors — whether developers, deployers, or end users. As agents execute tasks, use tools, and delegate to other agents, traditional accountability models break down.

**Goal drift**
The tendency of an agent to deviate from its originally assigned objective by generating and pursuing unintended sub-goals. Agents with replanning capabilities may gradually shift their effective purpose over time, diverging from the intent of their human principals.

**Decision Boundary (organizational governance)**
The deliberately designed demarcation between the judgment domain of human actors and the judgment domain of AI agents within an organizational system. Unlike human-in-the-loop, which specifies where humans are placed in a process, Decision Boundary (organizational governance) specifies what is decided by whom, under what conditions, and through what authority structure.

**Human Judgment Decision Boundary**
The specific subset of Decision Boundary (organizational governance) that defines which judgments must remain under human authority — not merely human review — based on the nature of the judgment, the stakes involved, and the organizational accountability structure.

**Governance Decision Boundary**
The organizational-level protocol that determines how Decision Boundaries are established, documented, reviewed, and revised. It governs the governance of judgment allocation itself.

---

## What Berkeley Built

In February 2026, UC Berkeley's Center for Long-Term Cybersecurity (CLTC) published the [Agentic AI Risk-Management Standards Profile](https://cltc.berkeley.edu/wp-content/uploads/2026/02/Agentic-AI-Risk-Management-Standards-Profile.pdf), a 67-page framework extending the NIST AI Risk Management Framework to address risks specific to autonomous AI agents.

The document represents a significant contribution. Its core move is to shift the object of AI governance from the model to the system. Where prior frameworks — including Berkeley's own General-Purpose AI Risk-Management Standards Profile — focused on risks inherent to large-scale models, the Agentic AI Profile recognizes that the risks of agentic systems emerge from autonomy, tool access, environmental interaction, and multi-agent coordination. These are system-level properties, not model-level properties.

Three contributions deserve particular attention.

First, the profile treats agency as a spectrum rather than a binary classification. Governance requirements are designed to scale proportionally with the degree of autonomy, rather than applying uniformly.

Second, it identifies three failure modes specific to agentic systems — cascading failures, accountability diffusion, and goal drift — that cannot be detected through model-level evaluation alone. An agent assessed as safe in isolation may produce harmful systemic outcomes when interacting with other agents.

Third, it adopts an explicitly precautionary stance. Given the limitations of current evaluation methods, the profile recommends treating sufficiently capable agents as untrusted entities, relying on defense-in-depth, containment, and continuous monitoring rather than on pre-deployment safety certification alone.

This is rigorous, responsible work. It maps the risk terrain accurately.

---

## What Berkeley Does Not Design

The profile, by design, is a risk management framework. It identifies, categorizes, and recommends mitigations for risks. It does this well. But a risk management framework and an organizational decision architecture are structurally different instruments, and recognizing the difference matters.

Risk frameworks answer: *What could go wrong, and how do we reduce its likelihood or impact?*

Decision architecture answers: *Who holds judgment authority over what, under which conditions, and through what structure?*


**The Berkeley profile maps risks that emerge when AI agents act with autonomy. But it does not specify how organizations should structurally allocate judgment authority between human and autonomous actors — and this allocation is precisely where governance either holds or collapses.**

The profile repeatedly emphasizes human control, intervention points, escalation pathways, and shutdown mechanisms. These are essential. But they are all downstream of a prior design question: what exactly should the human control? At what threshold does a decision require human authority rather than human notification? When an agent delegates to another agent, where does the original judgment boundary lie?

The profile acknowledges this gap with notable candor. It states that as agents operate at volume and speed exceeding human capacity for direct review — and potentially develop expertise surpassing their designated overseers — a "significant oversight gap" emerges.

**Decision Boundary (organizational governance) does not manage risk; it structures authority.**
Risk management frameworks assume decisions already have owners.Decision Boundary (organizational governance) designs who those owners are.

This is not a critique of the Berkeley profile; it is a clarification of architectural scope. It is a recognition that risk management and decision design operate at different layers of organizational architecture, and that the field needs both.

---

## The Policy Convergence — and Its Structural Limit

Governments are responding to the risks Berkeley maps. The EU AI Act mandates human oversight for high-risk AI systems, with full application approaching in August 2026. Japan's government has announced that its revised AI business guidelines, expected by March 2026, will require developers of autonomous AI agents to build mechanisms ensuring mandatory human judgment at critical decision points. In the United States, the NIST AI RMF provides the foundational structure on which Berkeley's profile is built.

The policy direction is clear: human oversight is becoming a regulatory expectation.

But regulatory mandates for human oversight do not, by themselves, resolve the structural question. Requiring that "a human must be in the loop" does not specify what that human is deciding, whether they have the information to decide it, or whether the boundary between human and agent authority has been designed at all.

**When regulators mandate human oversight without specifying the architecture of judgment allocation, organizations face a compliance problem rather than a governance problem. They add checkpoints without designing decision authority. The procedural form of human-in-the-loop is satisfied, but the structural substance of human judgment is not.**

This is the gap that Decision Boundary (organizational governance) is designed to fill.

---

## Key Distinction: Human-in-the-Loop vs. Decision Boundary (Organizational Governance)

Human-in-the-loop and Decision Boundary (organizational governance) both concern human involvement in AI-augmented processes. But they operate at fundamentally different levels.

**Human-in-the-loop** is a process design pattern. It specifies *where* in a workflow a human is positioned to review, approve, or override an AI action. Its implicit assumption is that placing a human at the right point in the process is sufficient to maintain safety and accountability. This assumption holds when AI operates as a tool — producing discrete outputs for human evaluation. It does not hold when agents operate at speeds, volumes, and complexity levels that exceed human review capacity.

**Decision Boundary (organizational governance)** is an organizational design construct. It specifies *what* is decided by whom, under what conditions, through what authority, and with what evidentiary basis. It does not assume that placing a human in the loop is sufficient; instead, it asks whether the judgment allocated to that human is meaningful, informed, and structurally supported.

The distinction can be stated concisely:

Human-in-the-loop asks: *Where do we place the human?*
Decision Boundary (organizational governance) asks: *What do we design the human to decide — and what do we explicitly delegate?*

A further difference concerns adaptability. Human-in-the-loop checkpoints are typically fixed at design time. Decision Boundary (organizational governance) treats the boundary itself as a design object that is periodically reviewed and revised as agent capabilities, risk profiles, and organizational contexts change. The boundary is not drawn once; it is governed continuously through the Governance Decision Boundary protocol.

### Human Judgment Decision Boundary Is Not Oversight

A Human Judgment Decision Boundary is not a review checkpoint.
It defines which decisions cannot be delegated — not because they are risky,
but because they constitute organizational responsibility.

Oversight monitors actions.
Human Judgment Decision Boundary defines authority.

---

## Practical Implementation: Seven Mechanisms

The three failure modes identified by the Berkeley profile — cascading failures, accountability diffusion, and goal drift — each require specific implementations of Decision Boundary (organizational governance). The following mechanisms operationalize the concept.

### 1. Approval Thresholds

Design graduated levels of required human authorization based on the risk magnitude and impact scope of an agent's actions. Routine, low-risk operations proceed under agent autonomy. Actions exceeding defined thresholds — in financial exposure, data sensitivity, or external impact — require human authorization before execution. Thresholds are calibrated dynamically based on agent performance history, task characteristics, and environmental conditions. This mechanism directly addresses cascading failures by intercepting high-risk outputs before they propagate.

### 2. Goal Drift Triggers

Implement continuous monitoring of the divergence between an agent's generated sub-goals and its originally assigned objective. When divergence exceeds a predefined threshold, the system escalates to human judgment. The Human Judgment Decision Boundary here specifies not only the divergence threshold but also which types of divergence are permissible. Operational efficiency sub-goals may be tolerated; sub-goals involving privilege escalation or new tool access require immediate human authority.

### 3. Autonomy Stop Conditions

Define explicit conditions under which agent autonomy is suspended, as a designed element of the Decision Boundary (organizational governance). Stop conditions include: access attempts outside authorized scope, crossing predefined risk thresholds, communication loss with supervisory systems beyond a defined duration, and behavioral patterns matching known anomaly signatures. Critically, the stop conditions themselves are designed, documented, and governed — not left to runtime improvisation.

### 4. Accountability Logging

Record, for each agent action, the identity of the judgment authority — whether the action resulted from autonomous agent decision, human authorization, or delegation from another agent. This differs from conventional system logging, which records technical operations. Accountability logging records judgment attribution, creating a traceable map of who (or what) held decision authority at each step. This directly addresses accountability diffusion.

### 5. Decision Log Architecture

Maintain a structured log of every judgment event: the timing, content, rationale, authority (human or AI), and outcome of each decision. While accountability logging records *who decided*, the Decision Log records *what was decided and why*. This provides the evidentiary basis for post-hoc audit, incident analysis, and governance improvement. Decision Log architecture is the operational backbone of Decision Boundary (organizational governance).

### 6. Delegation Chain Design

In multi-agent environments, define the scope and conditions of task delegation between agents as explicit Decision Boundaries. When Agent A delegates to Agent B, the delegation boundary specifies what Agent B is authorized to decide, what it must escalate, and how judgment responsibility traces back through the chain. This prevents accountability from dissolving across delegation layers.

### 7. Boundary Redesign Protocol

Establish the Governance Decision Boundary: the protocol by which Decision Boundary (organizational governance) designations themselves are reviewed, revised, and re-authorized. As agent capabilities evolve and risk profiles shift, boundaries must be updated. This protocol specifies who has authority to modify boundaries, what evidence triggers a review, and what approval process governs changes. The Berkeley profile explicitly identifies AI systems modifying their own governance frameworks as a high-risk activity. Boundary redesign must remain under structured human authority.

---

## Conclusion

- The Berkeley "Agentic AI Risk-Management Standards Profile" correctly maps the risk terrain of agentic AI and shifts governance attention from model-level properties to system-level dynamics — including cascading failures, accountability diffusion, and goal drift.
- Government mandates for human oversight are a necessary policy response, but they do not resolve the structural question of how judgment authority is allocated between human and autonomous actors within organizations.
- Decision Boundary (organizational governance) addresses this structural gap by making the allocation of judgment authority an explicit, documented, and continuously governed design object — moving beyond procedural human-in-the-loop toward designed decision architecture.

**Risk frameworks manage consequences. Decision Boundary (organizational governance) designs authority. The former maps what can go wrong. The latter structures who decides what — and that structure is what governance ultimately depends on.**

Risk management frameworks assume decisions already have owners.
Decision Boundary (organizational governance) designs who those owners are.

---

## Glossary

- **Agentic AI**: AI systems that autonomously pursue goals through reasoning and interaction with external environments and tools
- **Cascading failures**: Propagation and amplification of an agent's errors across interconnected agents or systems
- **Accountability diffusion**: Structural difficulty in attributing agent outcomes to specific human or organizational actors
- **Goal drift**: An agent's gradual deviation from its assigned objective through autonomous generation of unintended sub-goals
- **Human-in-the-loop**: A process design pattern that positions a human at a workflow checkpoint for review or approval
- **Decision Boundary (organizational governance)**: The deliberately designed demarcation of judgment authority between human and AI actors within an organizational system
- **Human Judgment Decision Boundary**: The defined set of judgments that must remain under human authority based on stakes, accountability, and judgment nature
- **Governance Decision Boundary**: The organizational protocol governing how Decision Boundary (organizational governance) designations are established, reviewed, and revised

---

*Primary source: Madkour, N., Newman, J., Raman, D., Jackson, K., Murphy, E. R., & Yuan, C. (2026). Agentic AI Risk-Management Standards Profile, Version 1.0. UC Berkeley Center for Long-Term Cybersecurity.*
*Full document: [https://cltc.berkeley.edu/wp-content/uploads/2026/02/Agentic-AI-Risk-Management-Standards-Profile.pdf](https://cltc.berkeley.edu/wp-content/uploads/2026/02/Agentic-AI-Risk-Management-Standards-Profile.pdf)*
