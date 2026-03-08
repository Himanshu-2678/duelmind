# DuelMind - Findings

## 01 · Llama vs Qwen Rhetorical Voice Difference

**Topic tested:** "AGI will inevitably be dangerous to humanity  - safety is impossible to guarantee" <br>
**Personality pairing:** Philosopher (Llama) vs Scientist (Qwen) <br>
**Turn count:** 10

### What I noticed

When both models were given the same reflection prompt, they responded in completely
different ways  - not just in what they said, but in how they said it.

Llama takes its time. It builds up to its point slowly, uses phrases like "I believe"
and "I've come to realize", and sounds like it's thinking out loud. The actual conclusion
shows up at the end after a lot of setup.

Qwen gets to the point immediately. First sentence is the argument. Each sentence after
that adds one thing and stops. No warm-up, no filler.

### Why I think this happens

Llama is trained heavily on conversational data  - it's built to feel like a helpful
assistant, so it naturally sounds like one. Qwen's training seems to lean more toward
technical and academic writing, which shows in how clean and direct its output is.

### What this means for DuelMind

This difference is actually a good thing. The reflections don't sound like the same
model talking twice, which makes them more interesting to read. I decided not to
constrain either model's writing style in the system prompt because the contrast
itself is part of what makes the feature work.

 

## 02 · Emergent Consensus Builder  - Synthesis Pipeline Behavior

**Feature:** Three-model synthesis phase that runs automatically after the final reflection <br>
**Models involved:** Llama 3.3 70B (synthesis), Qwen3 32B (synthesis), Kimi K2 (merge) <br>
**Trigger:** Fires after final evaluation, does not block the conversation

### What I noticed

When both models write their own version of a joint conclusion independently, the
merged result is more honest. Each model naturally favors its own framing when
summarizing  - having a third model merge them cuts that bias out and keeps only
what both actually agreed on.

### Why Kimi and not one of the two

Asking Llama or Qwen to merge their own outputs would just give one of them the
last word. Kimi is from Moonshot AI  - a completely different company from Meta and
Alibaba  - so it has no stake in either side. That's the only reason it's there.

Stack: Meta + Alibaba + Moonshot.

### What this means

The three-step approach  - each model synthesizes, then a neutral model merges  -
gives a cleaner result than a single summarization call would. I want to keep this
pattern for anything multi-model I build later.

 

## 03 · Conflict Detection Behavior

**Feature:** Detects logical conflicts between model positions after each exchange <br>
**Model used:** Kimi K2 (classifier) <br>
**Trigger:** After every Qwen turn, does not block the conversation

### What I noticed

On hard topics with a clear yes/no split  - like free will or AI regulation  - conflict
tags showed up consistently below Qwen's responses. Kimi was able to tell the
difference between a direct contradiction (one model says X, the other says not X)
and a tension (both want the same thing but disagree on how to get there).

On open-ended topics where both models could comfortably agree, fewer or no conflicts
were flagged. That's correct behavior, not a bug.

### A note on temperature

At temperature 0.1, Kimi was too strict and missed real conflicts. Bumping it to 0.3
fixed that  - it flags genuine tensions without being sloppy about it.

### What this means

Conflict detection works best on topics with a real binary split. When you combine it
with the consensus score, you get a clearer picture  - low consensus plus a conflict
tag means the models are actually disagreeing, not just being politely different.
