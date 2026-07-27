---
title: "The Undesigned Decision: Why AI Agents Expose a Governance Void, Not a Security Flaw"
source: "Insights/The Undesigned Decision- Why AI Agents Expose a Governance Void, Not a Security Flaw.md"
type: "podcast_script"
language: "en"
estimated_duration_minutes: 10
generated_at: "2026-07-27T10:16:05.265830+00:00"
text_model: "gpt-5.4-mini"
tts_model: "tts-1-hd"
voice: "onyx"
---

What is the central governance question posed by AI agents: are they a security problem, or do they expose a deeper absence of designed decision boundaries?

We are deploying systems that we cannot stop mid-execution, cannot trace after the fact, and did not explicitly authorize to decide. That is not a speculative concern. It is the empirical finding of the most comprehensive public audit of deployed AI agents to date. The instinct is to classify this as a security issue, because security is the familiar language of risk. But security presupposes something already in place: a defined perimeter, an inside and an outside, a permitted and a denied. What we are confronting is prior to security. It is the absence of designed decision boundaries in systems that are already making consequential judgments across enterprise workflows.

So the question is no longer whether AI agents can be hacked. It is whether anyone designed the scope of what they are authorized to decide in the first place.

In February 2026, an international research team led by Leon Staufer of the University of Cambridge published the 2025 AI Agent Index through MIT CSAIL. The study, conducted with researchers at Harvard Law School, Stanford, the University of Washington, the University of Pennsylvania, Concordia AI, and the Hebrew University of Jerusalem, systematically documented the safety, transparency, and governance characteristics of 30 prominent AI agents across chat, browser, and enterprise categories.

The findings are precise and unsettling. Of the 30 agents examined, only four—ChatGPT Agent, OpenAI Codex, Claude Code, and Gemini 2.5 Computer Use—published agent-specific safety evaluations. Twenty-five out of thirty disclosed no internal safety testing results. Twenty-three had undergone no third-party evaluation. Among the 13 agents classified as operating at frontier levels of autonomy, only four provided any form of agentic safety disclosure.

The transparency gaps extend beyond safety testing. Twenty-one agents had no documented default behavior for disclosing their AI identity to end users or third parties. Only seven published stable User-Agent strings or IP address ranges for external verification. Six agents actively used Chrome-like UA strings and residential IP contexts, deliberately mimicking human web traffic.

Monitoring was thin to absent. Twelve of the 30 agents provided no usage monitoring, or only issued notifications when rate limits were reached. For many enterprise agents, the researchers could not confirm whether individual execution traces were logged at all.

These are not marginal products. The Index covers systems from OpenAI, Google, Anthropic, Microsoft, Salesforce, ServiceNow, and other major platforms. The agents examined are embedded in CRM workflows, browser automation, sales and support operations, and enterprise business processes across industries. The scale matters because it shows this is not an edge case. It is becoming a normal feature of enterprise operations.

Media coverage understandably framed these findings as security risks. And the security risks are real. Prompt injection attacks have been demonstrated against nearly every major AI agent. Research by Galileo AI in December 2025 showed that a single compromised agent could contaminate 87% of downstream decision-making within four hours through cascading multi-agent failures. Palo Alto Unit42 documented persistent prompt injection techniques that gradually shift agent behavior over extended conversation histories.

But the deeper problem is structural, not defensive. Security protects boundaries that have already been drawn. Firewalls presuppose an inside and an outside. Access controls presuppose a policy of permitted and denied actions. What the MIT Agent Index reveals is that for most deployed agents, no such boundaries exist to protect. The question of what an agent is authorized to decide, and where that authorization ends, has not been asked, let alone answered.

This is not a failure of implementation. It is a failure of design.

The researchers make an important point here. Many developers treat safety evaluation of the underlying large language model as sufficient evidence that the agent built on top of it is also safe. But an agent’s behavior is determined not by its model alone, but by the composite interaction of its planning layer, tool access, memory architecture, and policy configuration. Model safety and agent safety are fundamentally distinct problems.

The Index did not document a catalog of vulnerabilities. It documented a systematic absence: no defined decision scope, no boundary specification, no structured record of what was delegated and to what extent. For the majority of systems studied, the question “who authorized this agent to make this judgment?” has no traceable answer, because the question was never embedded in the system’s architecture.

That becomes intelligible when we consider the architectural shift AI agents represent. Traditional enterprise software is deterministic. A given input produces a given output. The logic is written by humans, tested against specifications, and auditable against design. Judgment, in that paradigm, is not something the software performs. It is something the software executes on behalf of a human designer. The boundary between human decision and machine execution is implicit in the code itself.

AI agents break this assumption. An agent plans, selects tools, interprets context, and takes action probabilistically. The same input may produce different outputs across runs. The agent’s behavior emerges from the interplay of its model, its tool integrations, its memory state, and its operational policies, none of which may be fully visible to the organization deploying it.

This means that the governance frameworks enterprises have relied on—access control lists, compliance checklists, model cards—were designed for a world in which machines did not exercise judgment. They enforce rules about what systems may access. They do not define what systems may decide.

The result is a governance vacuum: organizations are deploying judgment-bearing systems into workflows without having designed the scope, limits, or accountability structure of those judgments.

Decision Design is a judgment architecture framework proposed by Ryoji Morii, founder of Insynergy Inc., for structuring authority, accountability, and decision boundaries in AI-augmented organizations.

That is the missing layer. Decision Design treats the act of judgment itself as a design object.

It makes visible the implicit judgments that AI agents perform, and subjects them to intentional, pre-defined structure. It specifies who decides, within what scope, under what constraints, and with what mechanisms for verification and override. It addresses not only the agent’s technical capabilities, but the organizational agreement about what the agent is permitted to judge.

It is not an anti-AI framework. It does not seek to restrict adoption or slow deployment. Nor is it a replacement for existing compliance standards. SOC 2, GDPR, and ISO 27001 verify conformity to predefined requirements. Decision Design operates at a prior level: it asks what should be defined in the first place. It is also not an ethics framework. It does not prescribe what AI should or should not do. It structures who judges, within what boundaries, and with what accountability.

At the center of this framework is the concept of the Decision Boundary: the explicit demarcation of who holds decision authority, over what domain, under what conditions, and where human override is retained. Decision Boundaries have always existed in organizations, in delegation-of-authority policies, approval matrices, and separation-of-duties controls. What has changed is that a new class of decision-making entity has entered the organization, and no corresponding boundary has been drawn.

Structural concepts require operational expression. One concrete implementation of Decision Design is the Agent Decision Ledger, a structured governance record that defines, tracks, and verifies the decision behavior of AI agents across their lifecycle.

The Ledger is not a logging tool. It is a decision architecture artifact that connects pre-deployment design to post-deployment auditability.

For each deployed agent, the Ledger specifies what the agent is authorized to decide, the extent of impact those decisions may have, the conditions under which human approval is required, and the time horizon within which the authorization remains valid. This shifts the unit of evaluation from the model to the decision boundary.

It also embeds explicit checkpoints in the agent’s execution flow where human authorization is required before proceeding. Not every decision requires human intervention. The design challenge is determining which decisions do, based on irreversibility, external exposure, and potential for cascading impact.

Each action the agent takes is tagged with the Decision Scope under which it was authorized. This enables post-hoc audit not merely of what the agent did, but whether it acted within its defined decision boundaries and passed through required approval points.

Over time, an agent’s behavior may shift from its designed parameters, either through probabilistic variation or through adversarial manipulation such as persistent prompt injection. A Decision Drift Monitor continuously measures actual decision patterns against the defined scope and raises alerts when divergence exceeds acceptable thresholds.

The MIT AI Agent Index did not describe a security crisis. It described something more fundamental: the rapid proliferation of judgment-bearing systems in the absence of judgment architecture. Most of the 30 agents studied disclosed neither what they decide nor how their decisions are recorded. Several agents, particularly browser-based systems, could not be clearly stopped or steered mid-execution. Most did not identify themselves as AI to the parties they interacted with. This is not technical immaturity alone. It is the consequence of an industry that has not yet treated decision structure as a design requirement.

The practical implication is straightforward. If an organization is deploying AI agents into real workflows, it must define decision scope before deployment, not after incident response. It must distinguish model safety from agent safety. It must require traceability for authorization, approval, and override. It must treat monitoring as structural, not merely observational. And it must recognize that governance is no longer only about access to systems; it is about authority to decide within them.

The capabilities of AI agents will continue to expand. That trajectory is neither avoidable nor undesirable. But expanding the population of systems that exercise judgment without designing the structure of that judgment is an organizational failure that compounds with each deployment. The question remains straightforward: who decides, within what boundaries, and who retains the authority to override?

That is the governance work ahead, and it is the work that connects Insynergy with Decision Design.
