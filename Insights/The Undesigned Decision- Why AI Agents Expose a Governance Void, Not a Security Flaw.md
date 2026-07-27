---
title: 'The Undesigned Decision: Why AI Agents Expose a Governance Void, Not a Security Flaw'
subtitle: We are deploying systems that we cannot stop mid-execution, cannot trace after the fact, and did not explicitly authorize to decide.
slug: undesigned-decision-ai-agent-governance-void
date: 2026-02-22
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
- AI-Governance
- Decision-Design
- Decision-Boundary
- Judgment-Architecture
- Decision-Authority
- Accountability
- Agentic-AI
- Automation
- AI-Safety
- Policy
audience:
- Executives
- Board Members
- CIOs
- CISOs
- Legal and Risk Leaders
- AI Governance Leaders
visibility: website
summary: 'We are deploying systems that we cannot stop mid-execution, cannot trace after the fact, and did not explicitly authorize to decide. This is not a speculative concern. It is the empirical finding of the most comprehensive public audit of deployed AI agents to date. The instinct is to categorize this as a security problem. It is not. Security presupposes a defined perimeter—an inside and an outside, a permitted and a denied. What we are confronting is something prior to security: the absence of designed decision...'
key_claim: This is the domain of Decision Design —a governance architecture that treats the act of judgment itself as a design object.
concepts:
- Decision Design
- Decision Boundary
- Judgment Architecture
- Decision Authority
- AI Governance
- Agentic AI
- Accountability
- Automation
relations: {}
aliases: []
---

# The Undesigned Decision: Why AI Agents Expose a Governance Void, Not a Security Flaw

*RYOJI — Insynergy inc.*

We are deploying systems that we cannot stop mid-execution, cannot trace after the fact, and did not explicitly authorize to decide. This is not a speculative concern. It is the empirical finding of the most comprehensive public audit of deployed AI agents to date.

The instinct is to categorize this as a security problem. It is not. Security presupposes a defined perimeter—an inside and an outside, a permitted and a denied. What we are confronting is something prior to security: the absence of designed decision boundaries in systems that are already making consequential judgments across enterprise workflows.

The question is no longer whether AI agents can be hacked. It is whether anyone designed the scope of what they are authorized to decide in the first place.

## What the Data Shows

In February 2026, an international research team led by Leon Staufer of the University of Cambridge published the 2025 AI Agent Index through MIT CSAIL. The study, conducted in collaboration with researchers at Harvard Law School, Stanford, the University of Washington, the University of Pennsylvania, Concordia AI, and the Hebrew University of Jerusalem, systematically documented the safety, transparency, and governance characteristics of 30 prominent AI agents across chat, browser, and enterprise categories.

The findings are precise and unsettling.

Of the 30 agents examined, only four—ChatGPT Agent, OpenAI Codex, Claude Code, and Gemini 2.5 Computer Use—published agent-specific safety evaluations. Twenty-five out of thirty disclosed no internal safety testing results. Twenty-three had undergone no third-party evaluation. Among the 13 agents classified as operating at frontier levels of autonomy, only four provided any form of agentic safety disclosure.

The transparency gaps extend beyond safety testing. Twenty-one agents had no documented default behavior for disclosing their AI identity to end users or third parties. Only seven published stable User-Agent strings or IP address ranges for external verification. Six agents actively used Chrome-like UA strings and residential IP contexts—deliberately mimicking human web traffic.

Monitoring was thin to absent. Twelve of the 30 agents provided no usage monitoring, or only issued notifications when rate limits were reached. For many enterprise agents, the researchers could not confirm whether individual execution traces were logged at all.

These are not outlier findings from marginal products. The Index covers systems from OpenAI, Google, Anthropic, Microsoft, Salesforce, ServiceNow, and other major platforms. The agents examined are embedded in CRM workflows, browser automation, sales and support operations, and enterprise business processes across industries.

## This Is Not a Security Problem

Media coverage of the Index understandably framed these findings as security risks. And the security risks are real. Prompt injection attacks have been demonstrated against nearly every major AI agent. Research by Galileo AI in December 2025 showed that a single compromised agent could contaminate 87% of downstream decision-making within four hours through cascading multi-agent failures. Palo Alto Unit42 documented persistent prompt injection techniques that gradually shift agent behavior over extended conversation histories.

But the deeper problem is structural, not defensive.

Security protects boundaries that have already been drawn. Firewalls presuppose an inside and an outside. Access controls presuppose a policy of permitted and denied actions. What the MIT Agent Index reveals is that for most deployed agents, no such boundaries exist to protect. The question of what an agent is authorized to decide—and where that authorization ends—has not been asked, let alone answered.

This is not a failure of implementation. It is a failure of design.

The researchers themselves make this point clearly. Many developers, they observe, treat the safety evaluation of the underlying large language model as sufficient evidence that the agent built on top of it is also safe. But as the report emphasizes, an agent's behavior is determined not by its model alone, but by the composite interaction of its planning layer, tool access, memory architecture, and policy configuration. Model safety and agent safety are fundamentally distinct problems.

The Index did not document a catalog of vulnerabilities. It documented a systematic absence: no defined decision scope, no boundary specification, no structured record of what was delegated and to what extent. For the majority of systems studied, the question "who authorized this agent to make this judgment?" has no traceable answer—because the question was never embedded in the system's architecture.

## The Structural Shift That Governance Has Not Absorbed

This gap becomes intelligible when we consider the architectural shift that AI agents represent.

Traditional enterprise software is deterministic. A given input produces a given output. The logic is written by humans, tested against specifications, and auditable against design. Judgment, in this paradigm, is not something the software performs—it is something the software executes on behalf of a human designer. The boundary between human decision and machine execution is implicit in the code itself.

AI agents break this assumption. An agent plans, selects tools, interprets context, and takes action probabilistically. The same input may produce different outputs across runs. The agent's behavior emerges from the interplay of its model, its tool integrations, its memory state, and its operational policies—none of which may be fully visible to the organization deploying it.

This means that the governance frameworks enterprises have relied on—access control lists, compliance checklists, model cards—were designed for a world in which machines did not exercise judgment. They enforce rules about what systems may access. They do not define what systems may decide.

The result is a governance vacuum: organizations are deploying judgment-bearing systems into workflows without having designed the scope, limits, or accountability structure of those judgments.

## Decision Design: The Missing Governance Layer

Addressing this vacuum requires a concept that existing frameworks do not provide: the explicit design of decision structures within and around AI agents.

This is the domain of **Decision Design**—a governance architecture that treats the act of judgment itself as a design object.

**What it designs.** Decision Design makes visible the implicit judgments that AI agents perform, and subjects them to intentional, pre-defined structure. It specifies who decides, within what scope, under what constraints, and with what mechanisms for verification and override. It addresses not only the agent's technical capabilities, but the organizational agreement about what the agent is permitted to judge.

**What it is not.** Decision Design is not an anti-AI framework. It does not seek to restrict adoption or slow deployment. Nor is it a replacement for existing compliance standards—SOC 2, GDPR, and ISO 27001 verify conformity to predefined requirements. Decision Design operates at a prior level: it asks what should be defined in the first place. It is also not an ethics framework. It does not prescribe what AI should or should not do. It structures who judges, within what boundaries, and with what accountability.

**What problem it addresses.** Decision Design responds to the specific condition the MIT Agent Index has documented: the proliferation of judgment-bearing systems without corresponding judgment architecture. When an agent's decision scope is undefined, there is no basis for evaluating whether its behavior is appropriate, no mechanism for meaningful oversight, and no traceable chain of authorization. Decision Design provides the structural layer that makes these evaluations possible.

At the center of this framework is the concept of the **Decision Boundary**—the explicit demarcation of who holds decision authority, over what domain, under what conditions, and where human override is retained. Decision Boundaries have always existed in organizations—in delegation-of-authority policies, in approval matrices, in separation-of-duties controls. What has changed is that a new class of decision-making entity has entered the organization, and no corresponding boundary has been drawn.

## From Framework to Implementation: The Agent Decision Ledger

Structural concepts require operational expression. One concrete implementation of Decision Design is the **Agent Decision Ledger**—a structured governance record that defines, tracks, and verifies the decision behavior of AI agents across their lifecycle.

The Ledger is not a logging tool. It is a decision architecture artifact that connects pre-deployment design to post-deployment auditability.

**Decision Scope Definition.** For each deployed agent, the Ledger specifies what the agent is authorized to decide (Scope), the extent of impact those decisions may have (Impact Radius), the conditions under which human approval is required (Escalation Trigger), and the time horizon within which the authorization remains valid (Decision TTL). This directly addresses the Index's finding that most agents lack agent-specific safety evaluations—by shifting the unit of evaluation from the model to the decision boundary.

**Human Approval Points.** The Ledger embeds explicit checkpoints in the agent's execution flow where human authorization is required before proceeding. Not every decision requires human intervention—the design challenge is determining which decisions do, based on their irreversibility, external exposure, and potential for cascading impact. The Index's finding that monitoring is "thin to nonexistent" for most agents reflects the absence of this design step.

**Boundary-Tagged Execution Trace.** Each action the agent takes is tagged with the Decision Scope under which it was authorized. This enables post-hoc audit not merely of what the agent did, but whether it acted within its defined decision boundaries and passed through required approval points. This goes beyond conventional logging by recording the structural relationship between action and authorization.

**Decision Drift Monitor.** Over time, an agent's behavior may shift from its designed parameters—either through probabilistic variation or through adversarial manipulation such as persistent prompt injection. The Drift Monitor continuously measures the agent's actual decision patterns against its defined scope and raises alerts when divergence exceeds acceptable thresholds.

## The Persistent Question

The MIT AI Agent Index did not describe a security crisis. It described something more fundamental: the rapid proliferation of judgment-bearing systems in the absence of judgment architecture.

Most of the 30 agents studied disclosed neither what they decide nor how their decisions are recorded. Several agents—particularly browser-based systems—could not be clearly stopped or steered mid-execution. Most did not identify themselves as AI to the parties they interacted with. This is not technical immaturity. It is the consequence of an industry that has not yet treated decision structure as a design requirement.

Decision Design offers a name for the missing layer. Decision Boundary offers its operational unit. Neither eliminates risk. But they make a specific and necessary contribution: they convert the question of AI governance from an abstract aspiration into a designable, auditable, and enforceable structure.

The capabilities of AI agents will continue to expand. That trajectory is neither avoidable nor undesirable. But expanding the population of systems that exercise judgment, without designing the structure of that judgment, is an organizational failure that compounds with each deployment.

The question remains straightforward: Who decides? Within what boundaries? And who retains the authority to override?

Designing the answer—deliberately, structurally, before the next agent is deployed—is the most basic governance obligation of the agentic era.

---

*RYOJI is the Representative Director of Insynergy Inc., a consulting firm specializing in Decision Design—governance architecture for defining who holds judgment authority, where boundaries sit, and how override works in agentic systems.*

---

### References

1. Leon Staufer, Kevin Feng, Kevin Wei, Luke Bailey, Yawen Duan, Mick Yang, A. Pinar Ozisik, Stephen Casper, and Noam Kolt. "The 2025 AI Agent Index." MIT CSAIL, February 2026. Paper: https://aiagentindex.mit.edu/data/2025-AI-Agent-Index.pdf / Index: https://aiagentindex.mit.edu/

2. Stephen Casper, Luke Bailey, et al. "The AI Agent Index." arXiv:2502.01635, February 2025.

3. Galileo AI Research, December 2025. Cascading failure in multi-agent systems. Cited via: Stellarcyber, "Top Agentic AI Security Threats in 2026." https://stellarcyber.ai/learn/agentic-ai-securiry-threats/

4. Palo Alto Unit42. "Persistent Prompt Injection Research." October 2025. Cited via: Stellarcyber (ibid.).

5. The Register. "AI agents abound, unbound by rules or safety disclosures." February 20, 2026. https://www.theregister.com/2026/02/20/ai_agents_abound_unbound_by

6. Gizmodo. "New Research Shows AI Agents Are Running Wild Online, With Few Guardrails in Place." February 2026. https://gizmodo.com/new-research-shows-ai-agents-are-running-wild-online-with-few-guardrails-in-place-2000724181
