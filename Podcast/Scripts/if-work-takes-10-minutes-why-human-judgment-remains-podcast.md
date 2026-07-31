---
title: "If the Work Takes 10 Minutes, Why Do You Still Need a Human?"
source: "Insights/If the Work Takes 10 Minutes, Why Do You Still Need a Human?.md"
type: "podcast_script"
language: "en"
estimated_duration_minutes: 10
generated_at: "2026-07-31T02:27:14.066062+00:00"
text_model: "gpt-5.4-mini"
tts_model: "tts-1-hd"
voice: "onyx"
---

This is the Decision Design Podcast from Insynergy, examining how judgment, authority, and accountability must be redesigned for the age of AI.

What does it really mean when AI can do in 10 minutes what used to take 10 weeks, and why, even then, do organizations still need a human?

That question is not hypothetical. Novo Nordisk, the Danish pharmaceutical company behind Ozempic, has been applying AI to the production of clinical study reports since the autumn of 2023. A clinical study report, or CSR, is a regulatory document summarizing the results of a drug trial. A single report can run up to 300 pages. It must meet exacting standards for data accuracy, terminological consistency, and regulatory compliance. Historically, a team of roughly 50 specialist writers produced these documents over 10 to 12 weeks, and each writer averaged 2.3 reports per year. For decades, this was one of the pharmaceutical industry’s most persistent bottlenecks.

Novo Nordisk developed an internal platform called NovoScribe, built on Anthropic’s Claude models, Amazon Bedrock, and MongoDB Atlas. It uses retrieval-augmented generation grounded in expert-approved text, combined with case-specific clinical variables, to produce regulatory-grade documentation. After deployment, the time required to generate a CSR draft dropped to 10 minutes. A process that once required 50 people and more than 10 weeks now runs with a team of three.

That is an efficiency story, and the numbers are striking. But the more important point is what happens after those 10 minutes. The AI-generated draft is not submitted directly to regulators. It passes through domain expert review and formal approval. The AI writes. Humans read, evaluate, and sign. The process has been compressed, but it has not been eliminated.

That distinction matters well beyond pharmaceuticals.

In February 2026, Anthropic released a major expansion of Claude Cowork, its AI productivity platform for enterprise knowledge workers. Cowork goes well beyond a conversational interface. It reads and writes files on the user’s local system, executes multi-step tasks, coordinates parallel workstreams, and passes context between applications including Excel and PowerPoint. Industry-specific plugin templates now cover HR, financial analysis, legal, engineering, operations, investment banking, and wealth management. Enterprises can also build private plugin marketplaces tailored to their own workflows and institutional knowledge.

Kate Jensen, Anthropic’s Head of Americas, described the ambition plainly: in 2025, Claude changed how developers work; in 2026, the same will happen across knowledge work as a whole. The framing is significant. AI is no longer positioned mainly as a tool that assists. It is positioned as an agent that executes.

Once that shift occurs, the central question is no longer capability. It is accountability. When an AI agent plans a task, decomposes it into subtasks, runs them in parallel, and delivers a finished output, the result carries consequences. Someone must own those consequences. In many organizations today, the question of who that someone is, and under what structure they exercise judgment, has not been deliberately answered.

Cowork makes the user’s level of involvement a matter of choice. Users can intervene at any point, or they can step away and return to completed work. That design embeds a judgment call: how much oversight is appropriate, and when does delegation become abdication? For individual users, that is a practical question. For organizations deploying AI agents at scale, it is a structural one.

Return to Novo Nordisk. Waheed Jowiya, the company’s Digitalization Strategy Director, described the impact of NovoScribe in specific terms: Claude helped cut writing times on CSRs by 90 percent, allowing documentation to move directly into human hands for review and approval. The wording matters. The AI output reaches human reviewers faster because intermediate steps have been removed. But the review itself remains intact: a qualified expert evaluates the document, decides whether it meets regulatory standards, and authorizes it for submission.

That is an intentional design choice. Novo Nordisk did not automate the production of clinical study reports. It relocated judgment. The AI handles generation. Humans handle evaluation and accountability. The boundary between those roles was drawn deliberately, not as an afterthought.

The reason is straightforward. A CSR helps determine whether a new drug can reach the market. Its accuracy is directly linked to patient safety. As Tobias Kröpelin of Novo Nordisk stated, report quality is critical because patient safety demands that errors are not tolerated. The line between what the AI produces and what a human approves exists because the stakes require it.

The more uncomfortable observation is that this sort of line-drawing usually happens only where external regulatory pressure forces it. In industries without comparable oversight, which is to say in much of the enterprise landscape where AI agents are now being deployed, the boundary between delegation and abandonment is left undefined.

Regulation is beginning to close that gap. The European Union’s AI Act, the most comprehensive AI regulation enacted to date, began applying its provisions on general-purpose AI models in August 2025. Most of its framework will take full effect in August 2026, with high-risk AI system requirements reaching complete applicability in 2027. Its risk-based classification system places particular emphasis on human oversight in high-stakes domains.

Japan’s government is also updating its AI Business Operator Guidelines, with a draft expected by March 2026 that explicitly requires developers and deployers of autonomous AI agents to build in mechanisms ensuring mandatory human judgment, citing risks of malfunction and privacy violation in agentic systems.

These moves point in the same direction. Organizations deploying AI that acts autonomously will increasingly be expected to show that human judgment remains structurally embedded in the process. That expectation will not be limited to regulated sectors like pharmaceuticals and financial services. It will extend to any enterprise using agentic AI in consequential workflows.

But regulation is only an external frame. It says human judgment must be present. It does not say how to design that judgment internally. If an organization lacks an internal architecture for human decision-making in AI-augmented processes, compliance will produce little more than checkboxes. The form will be satisfied. The substance will be absent.

As AI agents become more capable, the practical question is not what AI can do, but what humans are supposed to do in response to what AI has done. When a 10-to-12-week process compresses to 10 minutes, the vanished task is drafting. The remaining task is judgment: evaluating the output, determining its fitness for purpose, and accepting responsibility for the decision to act on it.

In most organizations, those residual human responsibilities have not been designed. Discussions about AI adoption usually focus on tool selection, use case identification, and cost reduction. Questions about where judgment resides, who bears responsibility for AI-assisted decisions, and what happens when exceptions arise are often deferred or never raised at all.

In regulated industries, external forces compel organizations to confront these issues. But as AI agents spread through knowledge work more broadly, the same issues apply everywhere. The gap is not in AI performance. The gap is in the design of judgment itself.

One might say that the Novo Nordisk case works only because it sits inside a heavily regulated environment. But the causality runs the other way. Novo Nordisk did not design its judgment structure because regulation required it. It was able to deploy AI effectively within a regulated environment because it had designed the judgment structure first. It can trust a 10-minute draft to move forward because the questions of who reviews, by what criteria, and with what authority have already been answered.

That kind of design is needed wherever AI agents operate, whether or not a regulator demands it. As these systems proliferate, the points at which human judgment should engage will multiply, blur, and become less visible. What cannot be seen cannot be managed. What cannot be managed cannot be held accountable.

Decision Design is the deliberate structuring of judgment processes, responsibility allocation, and human-AI boundaries within an organization. Its central structural element is the Decision Boundary: the explicitly defined line that determines what is delegated to AI and what is retained by humans, who holds authority at each point, and how that boundary is documented, maintained, and adapted over time.

Decision Design addresses three layers. First, the judgment process: at which stage in a workflow does a human evaluate AI output, and at what level — interim review, final approval, or exception handling? Second, the allocation of responsibility: when an AI-assisted decision produces a consequence, who is accountable — the operator, the approver, or the executive who authorized the deployment? Third, the boundary itself: where the line sits between AI execution and human authority, whether that line is fixed or variable, and who has the authority to move it.

It is not AI implementation consulting. It is not generic corporate governance. Existing governance frameworks assume human-to-human decision chains. When an AI agent autonomously executes tasks within a business process, traditional governance structures cannot fully capture where judgment resides. Decision Design is also not AI ethics. Fairness, bias, and transparency matter, but they are distinct from the operational question of who has authority to approve or reject a given AI output.

The practical implications are clear. Organizations need structured human review workflows, with qualified reviewers, defined review granularity, and explicit rejection criteria. They need judgment logs that record what the AI produced, what inputs it used, who reviewed it, when, and what action was taken. They need exception escalation protocols for outputs that do not fit standard approval paths. And they need an explicit final responsible owner for each workflow involving AI output, not a committee, but a defined role with sign-off authority.

That is the core lesson from the Novo Nordisk example. What accelerated was the task. What did not accelerate was the judgment. AI adoption is not the automation of work. It is the relocation of judgment. The work of this era is to make that relocation visible, governed, and accountable.

That is where Insynergy comes in, and it is why Decision Design matters.

If you want to keep exploring how organizations can preserve judgment in the age of AI, subscribe to the Decision Design Podcast.
