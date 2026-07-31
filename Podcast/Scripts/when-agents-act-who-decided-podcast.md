---
title: "When Agents Act, Who Decided?"
source: "Insights/When Agents Act, Who Decided?.md"
type: "podcast_script"
language: "en"
estimated_duration_minutes: 10
generated_at: "2026-07-31T02:13:47.663150+00:00"
text_model: "gpt-5.4-mini"
tts_model: "tts-1-hd"
voice: "onyx"
---

This is the Decision Design Podcast from Insynergy, examining how judgment, authority, and accountability must be redesigned for the age of AI.

What happens when an AI agent acts inside the enterprise: who, exactly, decided?

That is the central question, and it is the one many organizations are still avoiding. A procurement manager asks an AI agent to draft a purchase request. The agent pulls data from past orders, applies standard terms, formats the document, and routes it for approval. A director reviews it, signs off, and the order goes through.

It worked. It was faster. Nobody complained.

But the harder question remains: who made that decision? Was it the manager who prompted the agent? The director who approved a document she did not draft? The agent that selected the vendor terms? And if the terms turn out to be wrong, whose judgment failed?

This is not a hypothetical. It is happening across thousands of organizations, and often in processes far more consequential than procurement. The core challenge of the agent era is not simply how to deploy AI. It is how to design the structure of judgment itself: who decides what, where the line is drawn, and how that line is maintained as agents multiply.

The recent claim that “SaaS is dead” is useful precisely because it reveals what is at stake. Since late 2024, the argument has circulated widely, sparked in part by comments from Microsoft CEO Satya Nadella and amplified by analysts at IDC, TechCrunch, and elsewhere. The logic is straightforward: if AI agents can execute workflows autonomously, then the UI-centric model of SaaS — dashboards, forms, click-through approvals — becomes redundant.

There is some truth in that. When agents handle routine tasks end-to-end, the value of a human-operated interface declines. But this framing misses a more important point. SaaS did not only provide workflow execution. It also encoded accountability. Login IDs recorded who accessed what. Audit logs tracked who changed which field. Approval workflows documented who authorized each action. SaaS was, at once, a productivity tool and an attribution system — a mechanism for recording whose judgment produced which outcome.

When agents replace SaaS workflows, the productivity function transfers. The attribution function does not. No one has yet designed the replacement. That is the gap that matters.

You can see that gap already in the rise of shadow AI. Employees adopt AI agents on their own initiative, without IT approval, without governance frameworks, and often without their managers’ explicit knowledge. They feed business data into ChatGPT. They use agents to summarize meeting transcripts, draft memos, generate analysis, and pre-fill reports. It works. Output quality improves. Turnaround times shrink. Management tolerates it, or does not notice.

The security community has begun calling this “shadow AI,” echoing the earlier “shadow IT” era. But the security framing captures only part of the problem. The deeper issue is not just data leakage. It is invisible delegation.

When an employee uses an unsanctioned agent to draft a recommendation that a senior leader later approves, an act of delegation has occurred, but it was never recorded, never authorized, and never made visible to the organization. The agent influenced a judgment, and the organization does not know that happened. The output carries a human’s name, but the judgment behind it was shaped by a system no one governs.

That is the structural failure: convenience and unattributed responsibility coexist comfortably, until something goes wrong.

The familiar response is to say, “Keep the human in the loop.” It has become a governance reflex. If a human reviews the output, the reasoning goes, accountability is preserved. But that assumption is too simple.

First, review depth is undefined. When a human “reviews” an agent’s output, what does that mean? A cursory glance? A line-by-line audit? A judgment call on the reasoning behind every recommendation? Almost no organization has defined the expected depth of human review for agent-assisted decisions. The word “review” is doing more work than it can bear.

Second, review becomes performative at scale. A human can meaningfully review ten agent outputs per day, perhaps fifty. But when hundreds or thousands of agents produce outputs across an organization daily, exhaustive review becomes physically impossible. The human remains “in the loop” in name only.

Third, presence is not the same as ownership. Being present in a process does not mean accepting responsibility for its outcome. A human who rubber-stamps an agent’s recommendation has not exercised judgment. They have performed a ritual that resembles judgment.

Regulators are beginning to recognize this gap. In early 2026, Japan’s government signaled plans to update its AI governance guidelines to require mechanisms ensuring human judgment in autonomous agent operations, a direction consistent with broader regulatory trends in the EU and elsewhere. The instinct is sound. But requiring “human judgment” without specifying its depth, scope, and attribution risks creating a compliance checkbox rather than a genuine accountability structure.

The scale problem becomes clearer with McKinsey’s reported use of approximately 25,000 AI agents alongside 40,000 human employees, as cited by Business Insider. The figure was initially stated as 20,000 on Harvard Business Review’s IdeaCast and later revised upward at CES in Las Vegas. The precise number matters less than what it symbolizes.

At 25,000, the agent population approaches the human headcount. This is no longer a pilot program. It is an operational reality in which non-human actors participate in judgment at a scale comparable to the workforce itself.

If those agents produce analyses, summaries, recommendations, and drafts that inform decisions, then the volume of agent-influenced judgment exceeds what any human review process can meaningfully audit. The “review everything” model collapses. The limit is not human diligence. It is arithmetic.

That is why the framework I am discussing matters. It is called Decision Design, and its core concept is the Decision Boundary — the deliberately drawn line between what is delegated to agents and what is retained by humans. Decision Design is not a technology. It is a methodology for making the structure of judgment explicit, intentional, and maintainable.

“Decision Design is a judgment architecture framework proposed by Ryoji Morii, founder of Insynergy Inc., for structuring authority, accountability, and decision boundaries in AI-augmented organizations.”

Decision Design addresses three elements: decision ownership, meaning who accepts responsibility for a given judgment; decision boundary, meaning what is delegated to agents or automation and what remains with humans; and decision continuity, meaning how the structure is maintained and updated as conditions change.

The object of design is not the AI tool, the workflow, or the business process. It is the structure of judgment itself: who decides what, up to what point, and under whose accountability.

This distinction is important because the challenge most organizations face today is not “how to use AI,” but “how to govern a state in which AI participates in judgment.” Tool deployment is a means problem. Judgment structure is a governance problem. If you conflate the two, accountability remains unresolved no matter how sophisticated the tooling becomes.

Decision Design is not decision support. It does not primarily improve the quality of information. It is not AI governance in the narrow sense, either. It is broader than AI, applying to human-to-human delegation, human-to-system delegation, and multi-agent chains. And it is not organizational design in the traditional sense, because when all decision-makers were human, organizational design and judgment design were effectively the same. That equivalence no longer holds. Agents now execute judgment, and organizational design alone cannot define where accountability lands.

The practical concept at the center of this framework is the Decision Boundary. That boundary defines the line: this far, the agent acts; from here, the human owns it.

Such boundaries have always existed implicitly. A manager delegates tasks to a subordinate but retains final approval. A company outsources analysis but keeps strategy decisions internal. But agents change the nature of boundaries in three ways.

First, boundaries become invisible. Delegating to a human subordinate is a visible organizational act. Delegating to an agent often happens silently, on an individual’s laptop, without organizational awareness.

Second, boundaries become fluid. Agent capabilities update continuously. An agent that could only summarize last month can draft proposals this month. The scope of what can be delegated shifts, but the boundary is rarely redrawn intentionally.

Third, boundaries become layered. Agent A’s output feeds Agent B, whose output a human references. The boundary is no longer a single line. It is a stack of layers, and tracing which layer produced which judgment becomes difficult.

To make Decision Boundary operational, the source proposes two implementation patterns that can be piloted within 30 to 60 days using existing governance infrastructure.

The first is a Delegation Map. This visualizes, for each business process, which judgments are delegated to which actors — human, agent, or automated system. It resembles an extended RACI chart, with one critical modification: agents can be Responsible, meaning they execute, but never Accountable, meaning they cannot own the outcome. The point is to make invisible delegation visible.

The second is Boundary Review, a recurring governance checkpoint — quarterly or semi-annually — that audits the alignment between documented Decision Boundaries and actual practice. It checks current agent usage against the Delegation Maps, whether accountability structures are functioning or have become ceremonial, whether new shadow agents have emerged, and whether changes in agent capability have implicitly shifted delegation scope. This does not require a new committee. It can be added to existing IT governance, risk management, or internal audit cycles.

The practical implication is straightforward. Organizations should stop treating agent adoption as only a deployment question and start treating it as a judgment question. They should document where agents may draft, summarize, recommend, or pre-fill, and where humans must still decide. They should define what “review” actually means. They should expect boundaries to drift and inspect them on a recurring basis. And they should not confuse visible approval with true ownership.

Return, then, to the procurement request. The manager prompted an agent. The director approved the output. The order went through.

Without a Decision Boundary, the answer to who decided is unclear. The agent shaped the judgment. The director performed a review of uncertain depth. The organization bears the consequences of a decision whose ownership was never defined.

With a Decision Boundary, the answer is explicit. The Delegation Map specifies that the agent drafts terms within predefined parameters, while vendor selection and pricing approval remain with the director, who accepts accountability as the decision-maker of record.

The difference is not technological. It is structural.

And that is why this conversation matters for executives, CIOs, AI governance leaders, and researchers alike: agents will keep multiplying, but the organizations that thrive will not be those that deploy the most agents. They will be the ones that know, at every point, where the agent ends and the human begins, because they designed that boundary on purpose. That is the work Insynergy is advancing through Decision Design.

If you want to keep exploring how organizations can preserve judgment in the age of AI, subscribe to the Decision Design Podcast.
