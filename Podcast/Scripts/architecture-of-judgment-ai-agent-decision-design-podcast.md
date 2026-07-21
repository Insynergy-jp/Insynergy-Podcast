---
title: "The Architecture of Judgment: What a Japanese Deployment Reveals About the Missing Layer in Enterprise AI Agents"
source: "Insights/architecture-of-judgment-ai-agent-decision-design.md"
type: "podcast_script"
language: "en"
estimated_duration_minutes: 10
generated_at: "2026-07-21T04:09:32.984547+00:00"
text_model: "gpt-5.4-mini"
tts_model: "tts-1-hd"
voice: "onyx"
---

What is the missing layer in enterprise AI agents, and why does a single send button reveal it so clearly?

The console shows a draft message to a customer whose Hokkaido itinerary has been disrupted by heavy snowfall. The agent has already read the inquiry, retrieved the booking record, checked disruption status, applied cancellation-fee rules, and composed a reply explaining the refund terms. The message sits in a text box. Below it is a button labeled “Send.”

An operator is looking at the screen. The system has done the work. All that remains is a click.

It would be easy to dismiss that moment as trivial. The interesting engineering, one might assume, happened earlier: the language model parsing the message, the system navigating internal databases, the rule engine adjudicating eligibility. The button is just a formality. But that is not right. That button is the most deliberately designed component in the architecture. To understand why, we have to step back and ask what the system is actually doing, and what it chose not to do.

Most current discussion of AI agents is organized around capability. Foundation models, tool use, multi-agent orchestration, autonomous workflows: these describe what AI systems can do. That progress is real. Agents can parse language, navigate interfaces, retrieve data across systems, and compose coherent outputs in seconds. But what remains underdeveloped, and largely unnamed, is the architecture that governs where, within a real operational process, each type of judgment should reside. Not what the model can do, but who decides, at which point, with what evidence, under what constraints, and with what accountability when the output is wrong.

That question is not abstract. During severe weather events, JTB’s contact centers face inquiry volumes described as tens of times the normal rate. The operational case for automation is obvious enough. Every minute of human processing time costs money, and customers waiting for resolution during disruption are already dissatisfied. But customer-facing operations involving financial outcomes are domains where a wrongly communicated fee waiver creates a binding expectation, a refund issued in error may be irrecoverable, and a message sent about the wrong booking can compound into a service failure more costly than the delay it was meant to reduce.

So the question is not whether to deploy an AI agent. It is how to design the judgment architecture around it.

The JTB case offers a precise answer. JTB, Japan’s largest travel company, developed the system as part of its submission to GENIAC-PRIZE, a program jointly administered by Japan’s Ministry of Economy, Trade and Industry, METI, and the New Energy and Industrial Technology Development Organization, NEDO, to accelerate real-world deployment of generative AI applications. As reported by Nikkei xTECH, the agent handles customer inquiries submitted through JTB’s “Contact Board,” a web-based support channel for members, during weather disruptions.

JTB built the agent with KARAKURI, a Japanese AI company specializing in customer-support automation, using KARAKURI’s large language model “KARAKURI VL” as the system’s core LLM. The overall workflow was implemented in Python. But the structurally significant feature is not scope; it is internal differentiation. The agent operates across three distinct internal systems, each accessed differently and each assigned a different type of judgment authority.

The first is JTB’s back-office system for travel-product information, a web-based application the agent controls via Selenium. The second is the company intranet, where transportation disruption information, primarily airline cancellations, is published as PDF documents; the LLM reads and interprets those documents directly. The third is a separate, purpose-built system for adjudicating rail disruptions, which the agent queries via API.

That third system is especially important. JTB built a dedicated rule-based system, separate from the AI agent, to determine whether a customer’s booked rail segments are affected by reported disruptions. Rail networks in Japan involve complex route connections across multiple operators. Determining whether a specific ticket overlaps with a disrupted segment requires matching route data, station jurisdictions, and operator-specific cancellation policies. JTB judged that current AI cannot reliably prevent misjudgment in this domain. So the agent receives a definitive answer from the rule-based system via API rather than generating a probabilistic one.

The customer-facing message is then generated as a draft. The agent presents it for review alongside the evidence and reasoning that informed it. And the act of sending, the irreversible transmission of a message to a customer, remains with a human operator. As the Nikkei xTECH report states, the final confirmation of sending or executing is always performed by an operator.

Three design choices, then: a probabilistic AI for language interpretation and draft composition; a deterministic rule-based system, built independently, for rail adjudication; and a human operator holding authority at the irreversible action gate. These are not temporary limitations. They are the architecture.

What makes that architecture legible, and portable, is the recognition that a single business process contains multiple judgment acts, each with distinct structural properties. Inside one cancellation-handling workflow, at least five are embedded.

There is interpretation: understanding what the customer is asking. The message may be informal, ambiguous, or written in frustration. Parsing intent from natural language tolerates moderate ambiguity, and misclassification at this stage is recoverable. A language model is well suited here.

There is fact determination: is the customer’s booked rail segment affected by a reported disruption? This is not interpretation. It requires deterministic matching of route data against disruption data, across operator boundaries and complex junction networks. That is why JTB built a separate rule-based system and why the AI agent queries it via API rather than attempting the determination itself.

There is contractual adjudication: does this specific booking, under these specific terms, qualify for a fee waiver? This requires matching facts against rules. The logic is complex but deterministic, and it needs to be traceable and auditable.

There is communication quality: is the draft accurate, appropriately scoped, and does it promise only what the company can deliver? That benefits from human review precisely because a poorly worded communication can carry reputational and potentially contractual consequences.

And there is execution authorization: should this message be sent? This is the irreversible action gate, the point at which internal processing becomes an external commitment.

Each of these judgment acts has a different tolerance for ambiguity, a different reversibility profile, and a different accountability requirement. Assigning all five uniformly to any single processing type, whether AI, rules, or human, is a design error. The structural insight is that judgment must be decomposed before it can be allocated.

That point was made explicitly by JTB’s development lead, Wataru Goda of JTB’s Data Intelligence Team, who said the most important thing was not to hold a worldview of solving everything cleanly with AI, but to meticulously decompose business flows and articulate them fully. KARAKURI’s Kensuke Muto reinforced the same point: the key was decomposing tasks into their smallest units and rigorously examining whether each step should be handled by AI or by programmatic logic. That examination, not the model selection, produced a viable operational agent.

This is also why “human-in-the-loop” is often an architectural claim that is formally true but operationally hollow. If the system is designed so that a human reviews AI output before an irreversible action, the claim is satisfied. But that says nothing about whether the human’s judgment is effective.

The failure mode is familiar from adjacent domains: automation complacency in aviation, automation bias in AI-assisted diagnostics. In enterprise AI-agent deployments, the equivalent is the rubber-stamp operator, a human who clicks approve reflexively because the system is usually right, the volume is high, and the time pressure is real.

The response is not to remove the human or to add more humans. It is to design the conditions under which human judgment at the irreversible action gate becomes real rather than ceremonial. The information necessary to evaluate the output must be presented alongside the output, not hidden in another system. The rationale must be surfaced. If the draft says the cancellation fee has been waived, the operator needs to see which rule was triggered, which disruption was referenced, and which booking terms applied. Exception routing must be explicit, so cases where the AI’s confidence is low or the rule engine cannot adjudicate do not simply appear as normal cases with a slightly different flag. And audit artifacts must record not only what the human did, but what information was presented at the time. Without that, post-incident analysis produces blame, not learning.

JTB’s design follows that logic. The message is a draft, not a fait accompli. The agent presents the draft response and the evidence underlying its judgments. The operator’s action, pressing “Send,” is genuine authorization whose preconditions are architecturally specified. This is not a safety measure bolted onto an autonomous system. It is the system’s judgment architecture expressing itself at the point of highest consequence.

This is what Decision Design names. Decision Design is the practice of treating judgment, not tasks, not workflows, not data flows, as the primary object of system architecture. It asks where the judgment acts are, what the nature of each is, what the risk profile of each is, and to which processing authority each should be assigned. The operational unit of Decision Design is the Decision Boundary: the explicitly defined line between one judgment authority and another.

Decision Boundaries are not guardrails. Guardrails constrain outputs. Decision Boundaries allocate authority. They determine which entity is responsible for which judgment, and they define the handoff protocol between entities.

They are not workflow steps. Workflow design organizes tasks in sequence. Decision Design organizes judgments by their nature, risk, and accountability requirements.

They are not RPA. Robotic process automation replicates human actions on existing interfaces. Decision Design asks whether the human action being replicated involves a judgment that should be replicated, preserved, restructured, or reassigned.

The absence of this layer explains a recurring pattern in enterprise AI: technically functional agents that create organizational liability. The agent works, it completes the process, generates the output, reaches the endpoint, but no one has designed where accountability sits when the output is wrong. The result is a system that operates without a judgment architecture, and when it fails, the failure cascades into a vacuum.

The JTB case matters
