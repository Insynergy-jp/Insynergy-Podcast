---
title: When Agents Act, Who Decided?
subtitle: A procurement manager asks an AI agent to draft a purchase request.
slug: when-agents-act-who-decided
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
- Shadow-AI
- EU-AI-Act
- AI-Governance
- Decision-Design
- Decision-Boundary
- Human-in-the-Loop
- Human-Oversight
- Human-Judgment
- Accountability
- Responsibility
- Organizational-Design
- Agentic-AI
- Automation
- Financial-Systems
- SaaS
audience:
- Executives
- Board Members
- CIOs
- CISOs
- Legal and Risk Leaders
- AI Governance Leaders
visibility: website
summary: A procurement manager asks an AI agent to draft a purchase request. The agent pulls data from past orders, applies standard terms, formats the document, and routes it for approval. A director reviews it, signs off, and the order goes through. It worked. It was faster. Nobody complained.
key_claim: This essay argues that the core challenge of the agent era is not how to deploy AI, but how to design the structure of judgment itself — who decides what, where the line is drawn, and how that line is maintained as agents multiply.
concepts:
- Decision Design
- Decision Boundary
- AI Governance
- Human-in-the-Loop
- Human Judgment
- Agentic AI
- Organizational Design
- Responsibility
- Accountability
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

# When Agents Act, Who Decided?

## The question no one is asking about AI in the enterprise

A procurement manager asks an AI agent to draft a purchase request. The agent pulls data from past orders, applies standard terms, formats the document, and routes it for approval. A director reviews it, signs off, and the order goes through.

It worked. It was faster. Nobody complained.

But who made that decision? The manager who prompted the agent? The director who approved a document she didn't draft? The agent that selected the vendor terms? If the terms turn out to be wrong, whose judgment failed?

This is not a hypothetical. It is happening across thousands of organizations, in processes far more consequential than procurement. And almost no one has a clear answer.

This essay argues that the core challenge of the agent era is not how to deploy AI, but how to design the structure of judgment itself — who decides what, where the line is drawn, and how that line is maintained as agents multiply.

---

## What "SaaS Is Dead" Actually Reveals

The claim that "SaaS is dead" has circulated widely since late 2024, sparked in part by comments from Microsoft CEO Satya Nadella and amplified by analysts at IDC, TechCrunch, and elsewhere. The argument: if AI agents can execute workflows autonomously, the UI-centric model of SaaS — dashboards, forms, click-through approvals — becomes redundant.

There is some truth here. When agents handle routine tasks end-to-end, the value of a human-operated interface diminishes. But this framing misses something important. SaaS did not only provide workflow execution. It also encoded accountability. Login IDs recorded who accessed what. Audit logs tracked who changed which field. Approval workflows documented who authorized each action. SaaS was simultaneously a productivity tool and an attribution system — a mechanism for recording whose judgment produced which outcome.

When agents replace SaaS workflows, the productivity function transfers. The attribution function does not. No one has designed the replacement.

This is the gap that matters. Not whether SaaS survives as a business model, but whether the accountability infrastructure it quietly provided will have a successor.

---

## Shadow Agents: The Accountability Problem Hiding in Plain Sight

Across enterprises today, a pattern is repeating itself. Employees adopt AI agents on their own initiative, without IT approval, without governance frameworks, and often without their managers' explicit knowledge.

They feed business data into ChatGPT. They use agents to summarize meeting transcripts, draft memos, generate analysis, and pre-fill reports. It works. Output quality improves. Turnaround times shrink. Management tolerates it — or doesn't notice.

The security community has begun calling this phenomenon "shadow AI," echoing the earlier "shadow IT" era. But the security framing, while valid, captures only part of the problem. The deeper issue is not data leakage. It is invisible delegation.

When an employee uses an unsanctioned agent to draft a recommendation that a senior leader then approves, an act of delegation has occurred — but it was never recorded, never authorized, and never made visible to the organization. The agent influenced a judgment. The organization does not know this happened.

This creates a specific structural failure: the output carries a human's name, but the judgment behind it was shaped by a system no one governs. Convenience and unattributed responsibility coexist comfortably — until something goes wrong.

The problem is not that people use agents. The problem is that no one has designed where the boundary sits between what the agent decides and what the human decides.

---

## Involvement Is Not Ownership

The instinctive response to this problem is familiar: "Keep the human in the loop." The phrase has become a governance reflex. If a human reviews the output, the reasoning goes, accountability is preserved.

This reasoning has three structural weaknesses.

**First, review depth is undefined.** When a human "reviews" an agent's output, what does that mean? A cursory glance? A line-by-line audit? A judgment call on the reasoning behind each recommendation? Almost no organization has defined the expected depth of human review for agent-assisted decisions. The word "review" is doing more work than it can bear.

**Second, review becomes performative at scale.** A human can meaningfully review ten agent outputs per day. Perhaps fifty. But when hundreds or thousands of agents produce outputs across an organization daily, exhaustive review becomes physically impossible. The human remains "in the loop" in name only.

**Third, presence is not the same as ownership.** Being present in a process does not mean accepting responsibility for its outcome. A human who rubber-stamps an agent's recommendation has not exercised judgment. They have performed a ritual that resembles judgment.

Regulators are beginning to recognize this gap. In early 2026, Japan's government signaled plans to update its AI governance guidelines to require mechanisms ensuring human judgment in autonomous agent operations — a direction consistent with broader regulatory trends in the EU and elsewhere. The instinct is sound. But requiring "human judgment" without specifying its depth, scope, and attribution risks creating a compliance checkbox rather than a genuine accountability structure.

The gap between involvement and ownership is the central design problem of the agent era.

---

## What 25,000 Agents Actually Means

In January 2026, McKinsey Global Managing Partner Bob Sternfels reported that the firm operates with approximately 25,000 AI agents alongside 40,000 human employees, as cited by Business Insider. The figure was initially stated as 20,000 on Harvard Business Review's IdeaCast and later revised upward at CES in Las Vegas.

The precise number matters less than what it symbolizes.

At 25,000, the agent population approaches the human headcount. This is not a pilot program. It is not an experiment in one department. It is an operational reality in which non-human actors participate in judgment at a scale comparable to the human workforce.

Consider the implications. If each of those 25,000 agents produces outputs that inform decisions — analyses, summaries, recommendations, drafts — then the volume of agent-influenced judgment exceeds what any human review process can meaningfully audit. The "review everything" model collapses.

What the McKinsey number really exposes is not the ambition of one firm. It is the structural limit of human-in-the-loop as an accountability mechanism. When agent count reaches workforce scale, the gap between who executes judgment and who bears responsibility becomes impossible to manage through review alone.

Any organization can say it "uses" 25,000 agents. Far fewer can say who is responsible for the judgments those agents shape.

That gap — between deployment and accountability — is precisely the space that needs to be designed.

---

## Decision Design: Designing the Structure of Judgment

The framework proposed here is called **Decision Design**. Its core concept is the **Decision Boundary** — the deliberately drawn line between what is delegated to agents and what is retained by humans.

Decision Design is not a technology. It is a methodology for making the structure of judgment explicit, intentional, and maintainable.

### What Decision Design Designs

Decision Design addresses three elements:

**Decision ownership** — who accepts responsibility for a given judgment.

**Decision boundary** — what is delegated to agents or automation, and what remains with humans.

**Decision continuity** — how the structure is maintained and updated as conditions change.

The object of design is not the AI tool, the workflow, or the business process. It is the structure of judgment itself: who decides what, up to what point, and under whose accountability.

This distinction matters because the challenge most organizations face today is not "how to use AI" but "how to govern a state in which AI participates in judgment." Tool deployment is a means problem. Judgment structure is a governance problem. Conflating the two leaves accountability unresolved regardless of how sophisticated the tooling becomes.

### What Decision Design Is Not

**Decision Design is not decision support.** Decision support provides better information to decision-makers — BI dashboards, analytics, data visualization. Decision Design does not improve information quality. It designs the structure of who decides.

**Decision Design is not AI governance.** AI governance addresses ethical, safe, and transparent AI deployment. Decision Design is not limited to AI. It applies to human-to-human delegation, human-to-system delegation, and multi-agent chains. AI governance asks "how to use AI responsibly." Decision Design asks "how to structure judgment when AI participates in it."

**Decision Design is not organizational design.** Organizational design allocates authority among humans. When all decision-makers were human, organizational design and judgment design were equivalent. That equivalence no longer holds. Agents now execute judgment. Organizational design alone cannot define where accountability lands.

### What Problem Decision Design Addresses

Decision Design addresses situations in which **the attribution of judgment becomes ambiguous**.

Specifically: an agent substantively shapes a decision, but formal responsibility sits elsewhere. An individual deploys an agent that influences organizational decisions, but the delegation is invisible. Multiple agents process information in sequence, and no one can trace where a specific judgment was made or who owns it.

These situations share a common root: **decision boundaries are undefined, while operations proceed as if they were.**

---

## Decision Boundary: Where Agents End and Humans Begin

The Decision Boundary is the core operational concept within Decision Design. It defines the line: this far, the agent acts; from here, the human owns it.

Such boundaries have always existed implicitly. A manager delegates tasks to a subordinate but retains final approval. A company outsources analysis but makes strategy decisions internally. These are all forms of decision boundaries.

Agents change this in three ways.

**Boundaries become invisible.** Delegating to a human subordinate is a visible organizational act. Delegating to an agent often happens silently, on an individual's laptop, without organizational awareness. The boundary is drawn but no one sees it.

**Boundaries become fluid.** Agent capabilities update continuously. An agent that could only summarize last month can draft proposals this month. The scope of what can be delegated shifts, but the boundary is rarely redrawn intentionally. Drift accumulates between what the organization thinks is delegated and what actually is.

**Boundaries become layered.** Agent A's output feeds Agent B, whose output a human references. The boundary is no longer a single line. It is a stack of layers, and tracing which layer produced which judgment — and who owns the final output — becomes difficult.

In the SaaS era, boundaries were relatively clear. Software executed human instructions. Audit logs recorded attribution. In the agent era, that infrastructure is gone. Decision Boundary is the design discipline that replaces it.

---

## Implementation: From Concept to Practice

Decision Boundary is not only a conceptual framework. It requires concrete mechanisms to function inside an organization. Two implementation patterns are outlined here — each designed to be pilotable within 30 to 60 days using existing governance infrastructure.

### Delegation Map

A Delegation Map visualizes, for each business process, which judgments are delegated to which actors — human, agent, or automated system. It resembles an extended RACI chart with one critical modification: agents can be "Responsible" (they execute) but never "Accountable" (they cannot own the outcome). This asymmetry is the entire point.

**How it works.** Select a business process — say, quarterly financial reporting. Map each judgment point: data collection, anomaly flagging, narrative drafting, sign-off. For each point, record the current actor (human or agent), the intended delegation scope, and the human who holds accountability. The output is a single-page visual that makes invisible delegation visible.

**Who owns it.** The process owner, with input from IT governance and risk management.

**Artifacts.** One Delegation Map per critical process. Updated when agent capabilities or process scope change.

The value is not the document itself. It is the act of making delegation explicit — surfacing the shadow agents and the unnamed boundaries that already exist.

### Boundary Review

Decision boundaries are not static. Agent capabilities evolve. Regulations change. Business contexts shift. A boundary that was appropriate six months ago may be misaligned today.

A Boundary Review is a recurring governance checkpoint — quarterly or semi-annually — that audits the alignment between documented Decision Boundaries and actual practice.

**Review agenda.** Current agent usage versus documented Delegation Maps. Whether accountability structures are functioning or have become ceremonial. Newly emerged shadow agents not yet captured in governance. Changes in agent capabilities that have implicitly shifted delegation scope.

**How it fits.** This is not a new committee. It is an agenda item added to existing IT governance, risk management, or internal audit cycles. The overhead is minimal. The value is preventing the slow drift from intentional delegation to unaccountable automation.

**Cadence.** Quarterly for high-stakes processes (finance, compliance, client-facing decisions). Semi-annually for others.

---

## What 25,000 Really Meant

Return to McKinsey's reported 25,000 agents. The number drew attention because of its scale. But the real significance is what it implies about the limits of human oversight.

Ten agents can be reviewed. A hundred, perhaps. At 25,000, the premise that every agent output receives meaningful human scrutiny collapses. The model of accountability-through-review fails not because humans are negligent, but because the math no longer works.

What the number actually revealed was this: **human-in-the-loop, as traditionally conceived, does not scale to workforce-level agent deployment.**

Any firm can report how many agents it deploys. Fewer can explain who is accountable for the judgments those agents shape. The distance between those two statements is the territory of Decision Design.

---

## Back to the Procurement Request

The procurement manager prompted an agent. The director approved the output. The order went through.

Who decided?

Without a Decision Boundary, the answer is: nobody, clearly. The agent shaped the judgment. The director performed a review of uncertain depth. The organization bears the consequences of a decision whose ownership was never defined.

With a Decision Boundary, the answer is explicit. The Delegation Map specifies that the agent drafts terms within predefined parameters, but vendor selection and pricing approval remain with the director, who accepts accountability by signing not as a reviewer but as the decision-maker of record.

The difference is not technological. It is structural. One organization has designed its judgment. The other has not.

Agents will keep multiplying. The organizations that thrive will not be those that deploy the most agents — but those that know, at every point, where the agent ends and the human begins, because they designed that boundary on purpose.

---

## References

- Bob Sternfels on McKinsey's AI agent deployment: Harvard Business Review IdeaCast and CES 2026 "All-In" podcast (January 2026). Confirmed by McKinsey spokesperson. Reported by Business Insider, January 7 and 12, 2026.
- "SaaS is dead" discourse: Originated with Satya Nadella's remarks on the BG2 podcast (December 2024). Subsequent analysis by IDC, "Is SaaS Dead? Rethinking the Future of Software in the Age of AI" (December 2025).
- Shadow AI and rogue agents in the enterprise: TechCrunch, "Rogue agents and shadow AI: Why VCs are betting big on AI security" (January 2026). CIO.com, "Shadow AI practices: A wakeup call for enterprises" (February 2026).
- Japan's updated AI governance guidelines requiring human judgment mechanisms for autonomous agents: Nikkei (February 15, 2026). Consistent with broader regulatory direction in the EU AI Act and related frameworks.
