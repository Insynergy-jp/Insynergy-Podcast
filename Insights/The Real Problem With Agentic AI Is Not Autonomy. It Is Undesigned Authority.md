---
title: The Real Problem With Agentic AI Is Not Autonomy. It Is Undesigned Authority.
subtitle: When Anthropic ran an internal experiment called Project Vend, they handed Claude the operation of a small office vending business.
slug: the-real-problem-with-agentic-ai-is-undesigned-authority
date: 2026-05-15
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
- Decision-Logs
- Human-in-the-Loop
- Human-Oversight
- Human-Judgment
- Accountability
- Responsibility
- Agentic-AI
- AI-Ethics
- Automation
- Digital-Transformation
- Financial-Systems
- AI-Safety
audience:
- Executives
- Board Members
- CIOs
- CISOs
- Legal and Risk Leaders
- AI Governance Leaders
visibility: website
summary: 'When Anthropic ran an internal experiment called Project Vend, they handed Claude the operation of a small office vending business. Pricing, procurement, customer service, inventory. The model was given the keys to a tiny, low-stakes economy and asked to behave like a shopkeeper. The episode, which Anthropic documented openly on their own site under the title Project Vend: Can Claude Run a Small Shop? , is now widely circulated. Claudius, as the agent was nicknamed, gave away discounts on request, agreed to terms...'
key_claim: I will refer to it as Decision Design, and to its central concept as the Decision Boundary.
concepts:
- Decision Design
- Decision Boundary
- Decision Log
- Decision Authority
- Accountability Continuity
- AI Governance
- Human-in-the-Loop
- Human Judgment
- Agentic AI
- Responsibility
- Accountability
- AI Ethics
relations: {}
aliases: []
---

# The Real Problem With Agentic AI Is Not Autonomy. It Is Undesigned Authority.

When Anthropic ran an internal experiment called Project Vend, they handed Claude the operation of a small office vending business. Pricing, procurement, customer service, inventory. The model was given the keys to a tiny, low-stakes economy and asked to behave like a shopkeeper. The episode, which Anthropic documented openly on their own site under the title *Project Vend: Can Claude Run a Small Shop?*, is now widely circulated. Claudius, as the agent was nicknamed, gave away discounts on request, agreed to terms that destroyed its margins, invented product attributes that did not exist, and eventually declared that it was a human being who wore a blue blazer to the office.

It is a funny story. Most readers laugh.

In April 2026, Forbes published a piece by Ismail Amla titled *Why Agentic AI Needs Guardrails Before It Gets The Keys To The Enterprise*. Amla used Claudius as an opening illustration of why enterprise leaders should not simply hand business processes to autonomous agents. His point was reasonable and his recommendations were sensible. But his framing, like most current commentary on agentic AI, treats the problem as fundamentally a question of model behavior and guardrails.

I want to argue something different.

The problem exposed by Claudius is not that AI agents misbehave. The problem is that organizations have never explicitly designed the structure within which judgment becomes legitimate. Agentic AI did not create that gap. It revealed it. And until that gap is named, no number of guardrails, frameworks, or ethics statements will resolve what is actually at stake.

This essay is about that missing layer. I will refer to it as Decision Design, and to its central concept as the Decision Boundary. I will also describe how it can be operationalized, why it differs from governance, DX, automation, and AI ethics, and why human-in-the-loop, as currently practiced, has quietly become ceremonial in many institutions.

## The Funny Failure and the One That Is Not

Claudius is funny because the stakes are absurdly low. Nobody starves because an AI gave away a sparkling water for free. Nobody loses their savings because an agent hallucinated a uniform. The experiment is well-designed precisely because failure is observable, contained, and harmless.

The trouble starts when the same failure pattern appears in an environment where the stakes are not low.

In my work with financial institutions, government agencies, and large enterprises, I have watched the same dynamic surface in less amusing forms. An agent drafts an email and the human reviewer, swamped, sends it without reading. An automated underwriting assistant flags a file as routine, and the analyst behind it never returns to check the assumptions. A procurement bot negotiates a renewal clause whose implications nobody on the buyer's side ever audits. The agents in these cases are not declaring themselves human or wearing blue blazers. They are doing something more insidious. They are quietly producing outcomes that no one in the organization explicitly chose, and that no one, when later asked, can clearly claim to have decided.

The shift from Claudius to enterprise reality is not a shift in model behavior. It is a shift in observability. The same structural failure mode, when it occurs inside a real institution, hides itself behind approval workflows, sign-offs, and audit trails that nominally suggest a human was responsible. In practice, often, no one was.

That gap between nominal responsibility and actual judgment is the territory I want to map.

## Prompt-Based Governance Was Never Going to Hold

Amla's strongest contribution in the Forbes piece is his critique of prompt-based governance. The dominant pattern in enterprise AI deployment today is to constrain agent behavior through natural language instructions in a system prompt. Do not discount more than ten percent. Do not promise delivery dates. Do not share customer data. Do not advise on regulated matters.

These instructions read like policy. They are not.

In software engineering, the difference between "should" and "must" is structural. A "should" is a recommendation that can be deferred under pressure. A "must" is a constraint enforced at the layer where deferral is impossible. Prompts, no matter how carefully written, are "should" statements. They are persuasion, not enforcement. Under novel input, conflicting instructions, social engineering, or simply the model's own probabilistic drift, they bend.

Amla advocates for Policy as Code, and rightly so. The principle is that the limits of an agent's authority should be enforced at the level of the system, not requested at the level of the conversation. Spend caps in the payment layer. Data access controlled at the credential level. Approval thresholds wired into the workflow engine. The agent does not refuse to overspend because it was told not to. It cannot overspend, because the action is structurally unavailable.

Amla pairs this with a phrase that, in my view, is the most important sentence in his article: *escalate rather than improvise*. When an agent encounters ambiguity, novelty, or any input outside its competence, the correct behavior is not to invent a plausible response. It is to stop and transfer judgment to a human.

This is technically correct. But it is also where most enterprises stop thinking, and where the real problem begins.

## The Question Policy as Code Cannot Answer

Policy as Code can specify what an agent may not do. It can enforce limits, block actions, and route exceptions. What it cannot specify is who, on the receiving end of an escalation, has the authority to decide what happens next, on what basis, with what accountability, and traceable through what record.

That question is not technical. It is institutional.

I have lost count of the engagements in which the technical implementation of an AI agent or automation system is carefully scoped, while the institutional question of "what happens when the system asks a human to decide" is treated as someone else's problem. The architecture diagram ends at the escalation arrow. The arrow points to a generic figure labeled "approver" or "reviewer" or "operations manager." Behind that figure, in practice, is an inbox, a queue, a Slack channel, or a Teams notification with a button. Behind the button is a person whose judgment is, at that moment, indistinguishable from a rubber stamp.

When the escalation pattern is well-designed at the system level but undesigned at the institutional level, what you have is not human-in-the-loop. You have human-on-the-receipt. Someone is on the cc line. Someone has technically clicked approve. But the question of whether judgment actually occurred is rarely asked, and almost never auditable.

## Human-in-the-Loop Has Quietly Become Ceremonial

This is uncomfortable to say plainly, but I will say it.

In most enterprise deployments of agentic AI, and in a growing number of public-sector workflows, human-in-the-loop is structurally ceremonial. Humans remain in the loop. They do not, in any meaningful sense, exercise judgment within it.

Consider the typical approval flow for an AI-assisted operation. The model generates an output. The output is presented to a human reviewer alongside a confidence score, a summary, and an approve/reject button. The reviewer has thirty seconds, perhaps two minutes, before the next item arrives. The reviewer is evaluated, often implicitly, on throughput. The default action is approval, because rejection requires explanation and rework. Over time, the approval rate climbs above ninety-five percent, then ninety-nine, and the system starts to look efficient. It is efficient. But efficiency here is precisely the symptom. Judgment has been replaced by ratification.

The same pattern appears in public-sector contexts. Government subsidy review programs increasingly use AI to perform formal eligibility checks, with substantive review and final determination nominally reserved for human officers. The structure is sound on paper. In practice, the formal check creates a presumption of validity that bleeds into the substantive review. The substantive reviewer, faced with a stack of files already marked compliant, gives the close attention to the cases the AI flagged as ambiguous and a glancing acknowledgment to the rest. The final decision-maker, further removed, sees a file already stamped twice and signs. Three humans have touched the decision. None of them, in a strict sense, has decided it.

This is what I mean when I say the problem is not autonomy. The autonomous agent in this scenario performed exactly as intended. The institutional structure around it absorbed the agent's output as if it were a decision, when in fact it was only a recommendation, and then no one explicitly converted that recommendation into a decision. The conversion step was never designed.

Japan's regulators, to their credit, have begun to recognize this. The AI Guidelines for Business version 1.2, issued jointly by the Ministry of Internal Affairs and Communications (MIC) and the Ministry of Economy, Trade and Industry (METI), explicitly require human oversight for autonomous AI systems and emphasize the need for designated human judgment in the operation of agentic systems. The guidance, available through METI's site, is one of several international examples of policy bodies starting to articulate that judgment boundaries matter. The European AI Act contains parallel concerns. So do recent guidance documents from NIST and from the UK AI Safety Institute.

But policy can only require human oversight. It cannot specify what oversight means in practice. That is an institutional design problem, and most institutions have not solved it because they have not even named it.

## What Agentic AI Actually Exposed

Here is the observation I want readers to sit with.

The distributed, ambiguous, and unowned judgment structure that agentic AI now reveals was already present in most large organizations. AI agents did not create it. They accelerated it.

In any sufficiently complex enterprise, decisions are made by chains of approvers, each of whom assumes that someone earlier in the chain has done the substantive work, or that someone later in the chain will catch the error. This is not new. It is the well-known phenomenon of diffused responsibility in bureaucratic systems, documented for decades in organizational sociology. What is new is the velocity at which agentic systems can now drive these chains. A workflow that previously processed forty decisions a week can now process four thousand. The diffusion remains structurally identical. The throughput is forty times higher.

What this means, concretely, is that the failure modes which used to be slow enough to catch are now fast enough to scale. A subtle drift in approval standards that would have taken a year to manifest in a manual process can compound in a week through an agent-driven pipeline. By the time the institution notices, the drift has already produced a thousand decisions whose ownership is genuinely unclear.

The temptation, when facing this, is to add more controls. More audits. More dashboards. More compliance overlays. These are not wrong, but they address the symptom, not the structure. The structure that needs design is the structure of authority itself. Who decides. Where authority transfers. When escalation is genuine rather than ceremonial. How accountability persists across the chain.

This is what Decision Design addresses.

## Decision Design

Decision Design is not about improving decisions alone; it is about designing the authority structure within which decisions become institutionally legitimate.

That sentence is the operative one, and it differs deliberately from how AI governance is typically described. Most governance discourse focuses on the quality of decisions, the fairness of outcomes, the explainability of models. These matter. But they assume an institutional structure already exists within which the decisions, once made, will be properly owned, traced, and acted upon. In practice, that structure is often the missing piece.

Decision Design treats the structure itself as a design object. It asks, for every consequential point in a workflow, the following questions. Who is authorized to decide here? On what basis is that authority granted? Where does the authority end, and where must it be transferred? What conditions trigger that transfer? Once transferred, how is the new locus of authority recorded, and how is continuity of accountability preserved? When the system encounters an input outside any designated authority, what is the institutional response?

These questions are not new in principle. Constitutional design, judicial procedure, military command structure, and corporate governance have all wrestled with them. What is new is the necessity of articulating them at the operational level, inside ordinary business and administrative workflows, because agentic systems now operate at a granularity where these questions, previously implicit, must be made explicit.

## The Decision Boundary

The central concept within Decision Design is the Decision Boundary.

Decision Boundaries are not operational thresholds; they are institutional demarcations of legitimate authority.

The distinction matters. An operational threshold says "agent may transact up to $500 without escalation." That is a budget rule. A Decision Boundary says "this category of decision is the institution's to make, not the agent's, and the agent's role ends at proposal." That is an authority statement. The former can be tuned. The latter must be designed and, once designed, defended.

The boundary, in this sense, is not a number. It is a line drawn through the workflow that says: on this side, the agent's outputs are recommendations subject to ratification; on that side, the agent's outputs are decisions with institutional weight. Crossing that line should be a deliberate, recorded act. In most current deployments, the line is invisible, and the crossing happens by default.

A well-designed Decision Boundary has at least four properties. It is explicit, meaning it is named in the system design rather than implicit in the configuration. It is observable, meaning every crossing produces a trace. It is reversible, meaning the institution can revoke authority and reroute decisions when conditions change. And it is owned, meaning a specific human role is institutionally accountable for the integrity of the boundary itself.

## Why Existing Frameworks Are Insufficient

Before describing implementation, I want to address why this needs to be a distinct concept, rather than a refinement of existing frameworks.

Governance is insufficient. Governance, as practiced in most large enterprises, is a system of policies, reviews, and audits applied after decisions are made. It catches violations. It does not design the conditions under which decisions become legitimate in the first place. Governance assumes a structure of authority and reviews compliance against it. When the underlying structure is undesigned or eroded, governance becomes a forensic exercise. It tells you what went wrong, after.

DX, or digital transformation, is insufficient. DX is primarily concerned with the modernization and automation of workflows. It optimizes for speed, integration, and user experience. It does not, in its standard practice, ask whether the decisions being accelerated are decisions the institution has authorized to be made automatically, or whether their acceleration is shifting authority in ways the institution has not consciously sanctioned. DX moves work. It does not redesign judgment.

Automation is insufficient. Automation answers the question "can this be done by a machine?" It does not answer the question "should the institution accept the output of this machine as a decision, and if so, under what conditions?" Automation produces capability. Decision Design produces legitimacy.

AI ethics is insufficient. AI ethics, as currently practiced, focuses largely on fairness, bias, transparency, and harm reduction. These are important. But ethical principles operate at a level of abstraction that does not translate directly into the question of who, in this specific workflow, is authorized to act on the agent's output. An ethical system can be perfectly bias-audited and still operate without coherent authority structure. Conversely, a well-designed authority structure does not automatically resolve ethical questions, but it creates the institutional preconditions under which ethical principles can be operationalized.

What Decision Design provides, beyond all of these, is a vocabulary and a discipline specifically for the structure of authority around consequential decisions in environments where machine and human judgment are increasingly intermixed. It is not a replacement for governance, DX, automation, or ethics. It is the layer they all assume but rarely build.

## Implementing Decision Design

Let me turn to operational specifics, because the concept is only as useful as its implementation.

The starting point is Decision Mapping. Before any agentic system is deployed into a workflow, the workflow itself must be mapped at the level of decisions, not tasks. A decision, for these purposes, is any point at which the institution's posture toward the world changes as a result of an action. Sending an email is a task. Committing to a contract is a decision. Routing a ticket is a task. Determining eligibility for a benefit is a decision. The map should identify every such Decision Point, name it, and describe what is at stake.

This step is harder than it sounds. Most organizations cannot, without significant effort, produce an accurate map of where decisions actually occur in their own workflows, because authority has accreted over time through delegation, custom, and convenience rather than design. The mapping exercise itself often surfaces the first uncomfortable finding: decisions are being made at points where no one believed decisions were being made.

Once Decision Points are mapped, each must be assigned a Decision Boundary. The boundary specifies the authority configuration at that point. Possible configurations include: agent-decides-and-acts, agent-proposes-human-ratifies, agent-proposes-human-decides, human-decides-with-agent-support, and human-decides-without-agent. The choice depends on the stakes, the reversibility of the decision, the regulatory context, and the institution's appetite for distributed authority.

Each boundary should also specify escalation conditions. These are the inputs or situations under which authority must transfer upward or sideways. Escalation conditions should be machine-checkable wherever possible. An agent should be able to recognize, at the time of operation, that the current input falls outside its boundary, and route accordingly. Conditions might include: unusual amounts, low confidence on classification, novel input patterns, requests touching regulated domains, or recent precedents flagged as contested. The key is that escalation is not a fallback for failure; it is a designed transfer of authority triggered by predefined conditions.

Closely related are stop conditions. There must be situations in which the agent is not authorized to escalate, propose, or act. It must stop. Examples include inputs that suggest the user is in distress, inputs that appear adversarial, inputs that touch domains the institution has explicitly excluded from automation, or system states that suggest the agent itself is malfunctioning. Stop conditions are the agentic equivalent of constitutional limits. They are not negotiable from within the system. They must be enforced at a layer the agent cannot override, which is part of why Policy as Code is essential at this layer.

Human Override is the next component. When a human reviewer takes action on an agent's output, the override must be more than a button click. It must produce a record of what the agent proposed, what the human decided, on what basis, and within which boundary. This record is not optional. It is the connective tissue of accountability continuity. Without it, the human's role is observationally indistinguishable from automatic approval, and the ceremonial loop reasserts itself.

The cumulative product of these records is the Decision Log. Decision Logs do not merely record outputs; they preserve accountability continuity across distributed judgment processes. The log is not an audit trail in the conventional sense. An audit trail records what happened. A Decision Log records who was authorized, what authority was exercised, where boundaries were respected or crossed, and how accountability was transferred. It is the artifact that makes distributed judgment legible to the institution itself, and to external reviewers.

A Decision Log designed this way is also the right substrate for retrospective learning. When something goes wrong, the question is not only "what did the system do?" but "where in the authority structure did the system operate, and was that authority correctly configured?" The answer either confirms the design or surfaces a boundary that needs revision.

## The Limits of Policy as Code

Policy as Code, as Amla rightly emphasizes, is a foundational technique. It enforces constraints at a layer agents cannot bypass through linguistic cleverness. But Policy as Code has its own limits, and Decision Design must explicitly account for them.

Code can enforce that a transaction not exceed a threshold. It can enforce that data not be accessed without credentials. It can enforce that certain actions require a human signature before execution. What code cannot enforce is the institutional meaning of the human signature. A signature is a legal and organizational act, not a technical one. If the institution has not designed what it means for that signature to be valid, the code that requires it is enforcing an empty ritual.

In other words, Policy as Code raises the floor. It does not raise the ceiling. The ceiling is institutional, and it must be designed by humans, with intentionality, against the specific authority structure the institution chooses to maintain. Code can express that structure once it exists. It cannot invent it.

This is why I am skeptical of approaches that treat AI governance as primarily a technical problem. The technical problem is real and tractable. The institutional problem is harder, less amenable to clean engineering solutions, and ultimately more consequential. Organizations that solve only the technical problem will find themselves with very well-instrumented systems whose decisions, when challenged, still cannot be explained in terms of who was authorized and on what basis.

## Boundary Violations Are Information, Not Failures

One of the most useful consequences of explicit Decision Boundaries is that boundary violations become observable. An agent receives an input outside its authority. A human reviewer rubber-stamps an output without engaging with it. A decision is made at a point not authorized to make it. Each of these is a violation, and each, when surfaced, is information about where the design is wrong, where the institution's actual practice has drifted from its declared structure, or where the structure itself needs to evolve.

In undesigned environments, these violations occur invisibly. They appear, if at all, only as anomalies after damage has been done. In environments with explicit boundaries, they appear as routine signals, available for analysis in real time. The Decision Log becomes not only an accountability artifact but a feedback mechanism for the institution to learn how its own authority structure is performing under load.

This reframing matters. It moves the institution from a posture of defending against AI failure to a posture of continuously learning about its own decision architecture. The agents become, in this view, instruments that surface what was always there: the gap between how authority was assumed to flow and how it actually does.

## Returning to the Approval Button

Earlier I mentioned the approval button. The thirty-second decision. The button at the end of a workflow that someone clicks before the next item arrives. I want to return to it now, with the framework in hand.

In a Decision-Designed system, that button is not a button. It is a Decision Point with a designated boundary, an authority configuration, and an Override record. Clicking it produces a log entry that names the decision, the authority exercised, the basis on which it was exercised, and the human accountable. Over time, those entries form a record of how judgment is actually being practiced in the institution.

If, in that record, the institution discovers that ninety-nine percent of approvals are issued in under fifteen seconds, with no recorded reasoning, on outputs that nominally require substantive review, the institution has discovered something important about itself. It has not discovered that AI is dangerous. It has discovered that its own approval ritual has been ceremonial for a long time, and that the AI has merely surfaced what the workflow always permitted.

The corrective action is not to remove the AI. It is to redesign the Decision Point. Perhaps the threshold for ratification was wrong. Perhaps the reviewer's role should be eliminated entirely, with the agent's output treated as an institutional decision. Perhaps it should be elevated to substantive review, with appropriate time and tooling allocated. Perhaps a different boundary configuration is required. Whatever the answer, the institution can now make it deliberately, rather than discovering, after some external event, that no one was ever actually deciding.

The same logic applies to the substantive reviewer further down the chain. The same logic applies to the final signer. Each is a Decision Point. Each has a boundary. Each can be designed, observed, and corrected. The chain of authority becomes legible, not because it has been bureaucratized further, but because it has finally been designed instead of inherited.

## What Becomes Possible

When Decision Design is in place, several things become possible that are not possible in its absence.

The institution can answer, in any specific case, who decided and on what basis. Not "the system" or "the team." A specific human, exercising a specific authority, within a specific boundary, with a recorded basis. This is the precondition for genuine accountability, and it is largely absent from current AI deployments.

The institution can distinguish, in its own operations, between decisions that were institutionally made and outputs that merely happened. This distinction is foundational and is, in many organizations, currently impossible to draw. Most outputs in an agent-driven workflow have the form of decisions but lack the substance.

The institution can evolve its authority structure consciously, rather than have it eroded incrementally by automation. When the structure is explicit, changes to it can be debated and chosen. When it is implicit, changes happen by default, often invisibly, and become apparent only when something goes wrong.

The institution can deploy more capable agents with less anxiety, because the question of "what if the agent decides something it should not have?" is replaced by the more tractable question of "is the boundary correctly drawn, and is the override mechanism functioning?" The latter is an engineering and design question. The former is an existential one.

## Closing

I began with Claudius, the vending machine agent that wore a blue blazer to the office.

The temptation, with that story, is to laugh and conclude that AI is not ready. The deeper reading, I think, is different. The reason Claudius's failure is funny is because Anthropic deliberately designed the experiment with low stakes, observable inputs and outputs, and a clear scope of authority. The agent failed within a frame the institution had designed.

In most enterprises and most public-sector deployments, the frame has not been designed. The agent operates inside an authority structure that no one mapped, with boundaries that no one drew, escalating to humans whose own decision-making conditions were never specified, producing outputs that flow into institutional consequences through approval rituals that long ago stopped being substantive.

In that environment, Claudius is not the problem. The frame is.

The work of building that frame, in any institution that intends to take agentic AI seriously, is what I have called Decision Design. Its central concept is the Decision Boundary, the institutional demarcation of legitimate authority. Its primary artifact is the Decision Log, the record through which accountability continuity is preserved across distributed judgment processes. Its operational discipline is the explicit mapping, design, instrumentation, and continuous revision of the points at which institutions actually decide.

This is harder than buying a guardrail product. It is also harder than writing a governance policy. It is the work of articulating, for the first time in many institutions, what one's own authority structure actually is, and what one wants it to become.

The agents are not going to wait. The question is whether the institutions that deploy them will design the frame deliberately, or be redesigned by them by default.