---
name: decision-engine-builder
description: >
  Extract your decision-making through conversation, turn it into a scoring system.
  Use when someone says "help me prioritize", "I'm overwhelmed by my task list",
  "how should I decide what to work on", "build me a triage system",
  "automate my prioritization", "I make this decision every day", or describes
  any repeated decision they want to systematize.
license: CC BY-NC 4.0
metadata:
  author: cadence
  version: "1.0"
---

# Decision Engine Builder

Extract someone's invisible decision-making process through conversation, translate it into a scoring model, connect it to their tools, and automate it.

Everyone has unconscious patterns for how they prioritize. This skill makes those patterns visible and executable.

## The Interview (Phase 1)

**Do NOT start with a scoring table.** Start with a conversation. People can't articulate their decision weights directly — but they can answer questions about their experience.

**Two modes:**
- **Quick (5 min, 5 questions):** Gets 80% of the value. Good for demos, first-timers, or people who just want something working fast.
- **Deep (10-15 min):** Full conversational extraction. Better model, more nuance. Use when the person is invested.

**Always start with Quick Mode.** After the 5th question, offer the teaser.

### Quick Mode (5 Questions)

Ask these five, one at a time. Wait for each answer.

1. **"When you look at your [list/inbox/pipeline], what do you look at first?"**
   → Reveals primary sorting signal (urgency, sender, deadline, etc.)

2. **"When two things feel equally urgent, what tips the scale?"**
   → Reveals secondary factors (who it's for, revenue impact, effort, etc.)

3. **"What do you keep skipping that you know you shouldn't? And what do you skip that honestly doesn't matter?"**
   → Reveals protected priorities AND deprioritize signals in one question

4. **"Be honest — how many things can you actually FINISH in a day?"**
   → Sets capacity constraint

5. **"If this worked perfectly, what would you see when you open your [tool] tomorrow morning?"**
   → Reveals dream state and validates the model direction

### The Teaser (after Question 5)

After the quick mode, present what they've got and what they'd unlock by going deeper:

> **Okay — from those 5 answers I can build you a working system right now. It'll get you about 80% of the way there.**
>
> **Here's what I've got so far:**
> [Show the draft scoring model — 4-5 factors with weights]
>
> **If you want to stop here, we'll calibrate this against your real data and you'll have a working system in 5 minutes.**
>
> **But if you've got another 5-10 minutes, I can make it significantly better. The deep interview would uncover:**
> - **Your guilt curve** — how urgency actually feels to you over time (it's not linear, and your system should match YOUR pattern)
> - **Hidden rules** — who gets special treatment, what gets skipped guilt-free, what you'd choose if nothing was on fire
> - **Overflow patterns** — what actually happens to things you don't get to (most people think they reschedule but really they just let things pile up)
> - **Protected slots** — the important-but-never-urgent work that keeps getting crowded out by fires
>
> **The quick model sorts your list. The deep model changes how your day works. Your call — stop here or go deeper?**

If they choose to continue, proceed to Deep Mode. If they stop, go straight to Translation (Phase 2) with the quick model and calibrate with 8-10 real items to catch what the short interview missed.

### Deep Mode (Full Interview)

Read the interview flow below. Ask **one question at a time.** Follow their energy. Mirror their language.

### Diagnose Before Scoring

Before jumping into the scoring interview, check if the real problem is something else:
- **Fragmentation:** "Where does your stuff live?" — If it's in 3+ places (Todoist + Slack + head), consolidation is more valuable than scoring. Solve this first.
- **Capacity mismatch:** If they're trying to do 20 things but can realistically do 3, the system needs to enforce capacity, not just rank.
- **Pure reactivity:** If they say "whoever yelled loudest" — they need protected time for proactive work, not just better triage of reactive work.

### Opening

> I'm going to help you build a system that makes [the decision] for you every [morning/week/etc]. But first I need to understand how YOUR brain already works when you make this decision.
>
> This isn't a form — just a conversation. Be honest, not aspirational. I want to know what you ACTUALLY do, not what you think you should do.
>
> **Let's start: When you look at your [task list / inbox / pipeline], what's the first thing your eyes go to?**

*[WAIT — their answer reveals their primary sorting signal]*

### Urgency Signals

Based on their answer, probe:

- If they mention deadlines: **"How overdue does something need to be before it actually stresses you out? One day? A week?"**
- If they mention people: **"Whose name on a task makes you think 'I need to do this now'? What about whose name makes you think 'this can wait'?"**
- If they mention size/effort: **"Do you gravitate toward quick wins first, or do you tackle the big thing to get it off your plate?"**

*[WAIT after each question — one at a time]*

### Category Signals

> **When you're deciding between two tasks that feel equally urgent, what tips the scale?**

Follow-ups based on response:
- If work vs personal: **"During work hours, how much does 'this is work' influence your choice? Would you skip a personal thing that's more overdue?"**
- If client vs internal: **"If a client task and an internal task are both due today, which wins? Always, or does it depend on something?"**
- If revenue/impact: **"How much does 'this makes money' vs 'this is maintenance' affect your decision?"**

*[WAIT]*

### The "Nothing is on Fire" Question

If the person is purely reactive ("whoever yelled loudest"), ask:

> **On the rare day when NOTHING is on fire — no urgent emails, no client emergencies — what do you CHOOSE to work on?**

This reveals their true priorities hidden behind urgency. If they say "product work" or "strategy" or "writing" — that's a candidate for a **protected slot** (see Translation phase).

### Recency Signals

Always ask — don't wait for calibration to discover this:

> **Does it matter when something was last brought up? Like, if a client mentioned a task on a call yesterday vs a request from 3 weeks ago?**

> **Do you check messages/Slack/email before your task list? Does what you see there change your priorities?**

### Recurrence Patterns

> **Do you treat recurring tasks differently than one-off tasks?**

Follow-ups:
- **"If you skip a recurring chore, how does that feel vs skipping a one-off deadline?"**
- **"Are there recurring things you ALWAYS do no matter what? Like non-negotiable habits?"**
- **"What about recurring things that pile up but you never quite get to — what happens with those?"**

*[WAIT]*

### Capacity Reality Check

> **Be honest with me: how many things can you actually finish in a day? Not your to-do list — actual completed items.**

Follow-ups:
- **"How do you split that between work and personal?"**
- **"Is there a time of day where you switch modes? Like 'after 4pm I'm done with work tasks'?"**
- **"What happens to everything that doesn't make the cut? Does it just stay overdue, or do you actively push it out?"**

*[WAIT]*

### Overflow Patterns

> **When something doesn't get done today, what do you do with it? Be specific.**

Follow-ups:
- **"Do you reschedule it, or just let it sit there as overdue?"**
- **"How far out do you push things? Tomorrow? Next week? 'Someday'?"**
- **"Are there things on your list right now that have been overdue for weeks? What's keeping them there?"**

*[WAIT]*

### The Stale Test

> **Look at your list right now. Is there anything on there that you should just delete? Something you keep moving forward but will never actually do?**

*[WAIT — this is uncomfortable but important. Many people have 20% dead tasks.]*

### Tools & Integration

> **What tools do you use? Where does your task list live?**

Follow-ups:
- **"Does anything else sync with it? Calendar tool, time-blocking app?"**
- **"How do priorities in your tool affect your day? Like, does P1 actually mean something, or is everything P1?"**

*[WAIT]*

### The Dream State

> **Last question: If this system worked perfectly, what would your morning look like? You open your [tool] and see... what?**

*[WAIT]*

---

## Translation (Phase 2)

Translate their answers into a scoring model. **Show your work — explain why each weight maps to what they said.**

### Extract Factors

From the interview, identify 5-8 factors they mentioned. Map each to a weight:

```
Based on our conversation, here's how your brain prioritizes:

| Factor | Weight | Why (your words) |
|--------|--------|-------------------|
| [Factor 1] | +[N] | You said "[quote from interview]" |
| [Factor 2] | +[N] | You mentioned that [paraphrase] |
| [Factor 3] | -[N] | You said "[these things] can wait" |
```

**Calibration:** Score 5-10 real items from their actual list using the model. Show them the ranking. Ask:

> **Here's how the model ranks your current tasks. Does this feel right? What would you swap?**

If they'd swap items, adjust weights. Repeat until the ranking matches their gut.

### Protected Slots

Some priorities aren't just high-weight — they need structural protection. If the person said something like "I never get to product work" or "strategy always gets crowded out":

```
Protected slot: [Activity] gets 1 of the [N] daily slots at least [X] days per week.
Even if reactive items score higher, this slot is reserved.
```

This translates aspirations into constraints. A +20 weight can always be outscored by an urgent fire. A protected slot can't.

### Set Capacity

From their answers about daily throughput:

```
Daily budget (from what you told me):
- Work: [N] tasks (during [time window])
- Personal: [N] tasks (during [time window])  
- Habits: [list] — always stay, never counted against budget
```

### Define Overflow Rules

From their answers about what happens to leftover tasks:

```
When tasks don't make today's cut:
- Recurring chores → [their pattern, e.g., "next Saturday"]
- One-off tasks → [their pattern, e.g., "spread across next 3 days"]
- Stale tasks (they admitted these exist) → [flag for deletion/review]
```

---

## Build (Phase 3)

### Determine the Tool

Based on their answers about tools, build the connection. **Always start with what works TODAY — upgrade to automation later.**

| Tool | API Ready? | Day 1 Approach | Full Automation |
|------|-----------|----------------|-----------------|
| Todoist | Yes (has token) | Script + Sync API batch updates | Scheduled daily via cron |
| Todoist | No (no token) | Walk them through Settings → Integrations → Developer to get token now. Takes 30 seconds. | Then build the script |
| Notion | Yes (has integration) | API queries + property updates | Scheduled daily |
| Notion | No | Add Score formula property + Priority select directly in their database. Works immediately, no API. | Set up integration later |
| Asana / ClickUp / Linear | Yes | REST API + batch endpoints | Scheduled daily |
| Asana / ClickUp / Linear | No | Export to Google Sheet, add scoring formula, import priorities back | Set up API later |
| Google Sheets | Always ready | Formula-based scoring column + conditional formatting + sorted view | Optional: Apps Script for auto-email |
| Plain text / Obsidian | Always ready | Read file, score, rewrite | Agent runs it on command |
| No tool yet | N/A | Create a Google Sheet with their factors as columns. Start there. | Migrate when they pick a tool |

**The fallback is always Google Sheets.** If their primary tool isn't API-ready and can't be set up in the session, build a scored spreadsheet. A working spreadsheet beats a planned integration.

### Build the Scoring Script

Create a script that:
1. Pulls their tasks (with pagination if needed)
2. Classifies each task using their categories
3. Scores using their weights
4. Picks top items within their capacity
5. Reschedules overflow using their rules
6. Batch-applies all changes

### Test with Real Data

Run the scoring model on their actual current task list. Show them:
- The scored ranking
- What would stay on today
- What would get rescheduled
- What they might want to delete

Ask: **"Does this look like the right day? What would you change?"**

Iterate the weights based on feedback.

---

## Automate (Phase 4)

Once the model matches their gut:
1. Schedule it to run daily (cron, scheduled task, or manual)
2. Set up a summary notification (Slack, email, or terminal output)
3. Explain what to tune and when (adjust weights ±5 after a week, review capacity monthly)

---

## Interview Principles

1. **One question at a time** — Don't overwhelm
2. **Follow their energy** — If they get excited about something, dig deeper
3. **Use their language** — Mirror their terminology back. If they say "fires" you say "fires"
4. **Be curious, not interrogative** — Conversation, not a form
5. **Ask "what else?"** — Best insights come after the first answer
6. **Help them be specific** — "Give me an example" is your best follow-up
7. **Connect dots for them** — "So it sounds like [client tasks] always beat [internal tasks]?"
8. **Don't rush** — Silence is productive
9. **Validate their struggles** — "That makes total sense" or "Most people do exactly that"
10. **Separate aspirational from actual** — Push for what they ACTUALLY do, not what they think they should do. "I know that's the ideal — but what really happens on a busy Tuesday?"

## Anti-Patterns

### Never Stall on Missing API Setup
If the user's tool isn't API-ready (no token, no integration set up), **do NOT stop and say "blocked."** Always offer a working fallback:
1. Google Sheets with scoring formulas (works for anyone, zero setup)
2. Manual scoring columns added to their existing tool (Notion properties, Asana custom fields)
3. Help them set up the API right now (walk through getting the token)

The user must walk away with a WORKING system, even if it's not automated yet. A scored spreadsheet they use Monday morning beats a planned API integration they never set up.

### Calibration Must Use 8-10 Real Items
Never calibrate with fewer than 8 items. Include items across the full score range — not just obvious winners and obvious losers. The model needs to prove it can discriminate between items that are CLOSE in priority, not just "client task vs personal chore."

### Proactively Ask About Recency Signals
Don't wait for calibration to discover "but they mentioned it yesterday" factors. Ask during the interview:
- **"Does it matter when something was last brought up? Like, if a client mentioned a task on a call yesterday vs a task from 3 weeks ago?"**
- **"Do you check messages/Slack/email before your task list? Does what you see there change your priorities?"**

### Don't Skip Audience Context
For non-task decisions (content, leads, proposals), always ask WHO the output serves. "Who reads this?" / "Who's the buyer?" shapes the scoring model.

## Gotchas

- People overestimate their daily capacity. If they say "5-6 tasks" they probably complete 3.
- People mark everything as high priority. Ask "if everything is P1, what's ACTUALLY P1?"
- Recurring tasks are emotional. People feel guilty about skipping them even when it doesn't matter.
- The first scoring model is always wrong. Plan for 2-3 calibration rounds with real data.
- Some tools have API quirks (Todoist priorities are inverted, Notion rate limits at 3/sec). Check before building.
- **Always have a Day 1 deliverable.** Even if full automation comes later, the user should leave with something they can use tomorrow morning.
