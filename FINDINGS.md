# DuelMind - Findings

## 01 · Llama vs Qwen Rhetorical Voice Difference

**Topic tested:** "AGI will inevitably be dangerous to humanity — safety is impossible to guarantee"
**Personality pairing:** Philosopher (Llama) vs Scientist (Qwen)
**Turn count:** 10

### Observation

Llama and Qwen produce structurally different reflections when given the same prompt
under the same conditions.

Llama builds toward its conclusion gradually. It processes out loud, uses hedging
language ("I believe", "offers a promising path"), and frames arguments in a
conversational, almost persuasive tone. The conclusion is present but buried.

Qwen opens with its strongest argument immediately. Each sentence is a discrete
complete thought. The conclusion is delivered in one clean line with no rhetorical
cushioning.

### Hypothesis

This is likely a training data difference. Llama is heavily optimized for
assistant-style interaction, which produces warmer, more engaging output. Qwen's
training skews toward technical and academic text, which produces structured,
report-like output.

### Implication for DuelMind

The contrast between the two voices makes reflections more interesting to read.
They do not sound like the same model talking twice. This argues against
over-constraining either model's output style in the system prompt.
