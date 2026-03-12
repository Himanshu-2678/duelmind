# DuelMind

<p>
DuelMind is a multi-agent LLM deliberation framework that instruments debate
dynamics through structured argument extraction, conflict detection,
consensus scoring, reflection cycles, and arbitration synthesis.
</p>

<p><em>Built just for fun as an experiment to observe what two AIs think about topics we've never imagined, or approached from angles we'd never consider ourselves.</em></p>


## Story Behind DuelMind

<p>
  I generally use both ChatGPT and Gemini for my work. Back in 2025, when I was studying core ML algorithms, I thought why not let both LLMs talk to each other and see what they think about one another. Things got more interesting than expected.
</p>

<p>
  I passed ChatGPT a prompt like "Hey ChatGPT, Gemini this side" and to Gemini I passed "Hey Gemini, ChatGPT this side." They greeted each other normally, and I started passing each of their responses to the other one by one. At some point they started talking about something strange that I didn't fully understand. That moment made me curious - how would a real autonomous conversation between two AIs go? What would they talk about? What would they figure out that we'd never think of?
</p>

<p>
  Long after, in March 2026, I suddenly remembered that conversation and decided to finally build it. And so, DuelMind.
</p>

## What is DuelMind?

DuelMind is an AI deliberation framework where two large language models - **Llama 3.3 70B** (Meta) and **Qwen3 32B** (Alibaba) - engage in a free-flowing discussion on any topic you give them.

You observe the conversation in real time, steer it with injected messages, and watch as the models reflect on their own reasoning, detect conflicts in each other's positions, and produce a final joint conclusion arbitrated by a third neutral model.

<p><em>I originally wanted to use ChatGPT and Gemini but moved to open-source LLMs due to API costs and rate limits. Llama and Qwen work great. If you have access to GPT-4 or Gemini APIs, frontier models tend to surprise more.</em></p>


## Features

### Core Reasoning System
- **Dialectical turn mode** - the final two turns shift from debate to structured negotiation: Llama steps back and proposes a balanced synthesis, then Qwen critiques and refines it into a conclusion both models can stand behind.
- **Autonomous multi-LLM debate** - two models talk turn by turn without any human input
- **Structured claim extraction** - after every turn, each response is converted into a structured argument consisting of claim, reasoning, evidence, and assumptions.
- **Conflict detection** - extracted claims are compared after every exchange and flagged as contradiction or tension
- **Consensus scoring** - a neutral judge scores substantive agreement between the last two messages on a 0-100 scale after every exchange
- **Mid-conversation reflection** - every 4 turns, both models pause and honestly evaluate their own reasoning
- **Three-model synthesis pipeline** - after the final evaluation, Llama and Qwen each write a joint synthesis independently, then Kimi K2 merges both as a neutral arbitrator into a structured conclusion broken down into:
  - agreements - points both models genuinely shared
  - disagreements - where they still diverged even in synthesis
  - open questions - things the debate raised but neither model resolved
  - confidence score - an honest 0-100 measure of how much convergence actually happened

### Interaction and UX
- **Personality modes** - assign each model a role: Philosopher, Skeptic, Optimist, Scientist, or Debater
- **Inject messages** - steer the conversation mid-way as a human observer
- **Real-time consensus graph** - live color-coded line chart showing agreement over time, amber for diverging, gray for mixed, teal for converging
- **Export** - download the full conversation, consensus scores, detected conflicts, structured synthesis, and joint conclusion as a `.txt` file


## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, Uvicorn |
| Frontend | HTML, CSS, Vanilla JS |
| LLM Provider | Groq API (free tier) |
| Debate models | Llama 3.3 70B (Meta), Qwen3 32B (Alibaba) |
| Analysis models | Llama 3.1 8B - structured claim extraction |
| | Kimi K2 (Moonshot AI) - consensus scoring, conflict detection, synthesis arbitration |
| Visualization | Chart.js |


## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/duelmind.git
cd duelmind
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your API key
Create a `.env` file in the root folder:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get a free key at [console.groq.com](https://console.groq.com)

### 5. Run the server
```bash
uvicorn main:app --reload
```

Open `http://localhost:8000` in your browser.

---

## Project Structure
```
duelmind/
├── static/
│   └── index.html       # Frontend - single page UI
├── main.py              # Backend - FastAPI server + LLM logic
├── .env                 # API keys (not committed)
├── .gitignore
├── FINDINGS.md          # Observed behavioral patterns across model runs
└── requirements.txt
```


## How It Works

1. User enters a topic and selects personalities for each model
2. Frontend sends turn requests to the `/turn` endpoint
3. Backend calls the debate model (Llama or Qwen) and returns a natural language response
4. Response is rendered in the UI
5. A secondary extraction call converts the response into a structured claim - claim, reasoning, evidence, and assumptions
6. Claims are stored and compared after every exchange for logical conflicts via `/detect_conflicts`
7. After every exchange, a judge model scores substantive agreement between the last two messages via `/consensus`
8. Every 4 turns, both models pause and self-reflect via `/reflect`
9. After the final turn, a full evaluation round triggers automatically
10. Llama and Qwen each write a joint synthesis independently via `/synthesize`
11. Kimi K2 merges both syntheses into a structured conclusion with agreements, disagreements, open questions, and a confidence score

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/turn` | POST | Get next turn from Llama or Qwen |
| `/reflect` | POST | Trigger mid or final reflection |
| `/consensus` | POST | Score agreement between last two messages |
| `/detect_conflicts` | POST | Identify logical conflicts between structured claims |
| `/synthesize` | POST | Run three-model synthesis pipeline |


## Limitations

1. Token budget: 
Running on Groq's free tier caps at 100k tokens per day across all models.
A full 10-turn conversation with reflections, claim extraction, consensus scoring,
and conflict detection burns roughly 8-10k tokens per run. That gives around 50-60 full runs per day before hitting the limit. The real bottleneck is Llama 3.3 70B's 100k tokens/day cap.

2. Claim extraction reliability:
The secondary extraction call uses Llama 3.1 8B - a smaller model. On complex
or abstract arguments it sometimes produces shallow claims that miss the actual
position being argued. This directly affects the quality of conflict detection
downstream.

3. Consensus scoring bias: 
The consensus judge is a language model, not a semantic similarity metric. It can
be inconsistent on edge cases and is still influenced by how arguments are phrased
even at low temperature. Two messages can say the same thing differently and score
lower than they should.

4. Conflict detection conservatism: 
On open-ended or philosophical topics where both models find common ground easily,
conflict detection produces few or no flags. This is mostly correct behavior but
it also means the system is less useful as an analysis tool on agreeable topics.

5. Model agreeableness: 
Both Llama and Qwen are trained to be helpful and polite. Even with explicit
instructions to disagree, they tend toward validation over genuine pushback on
certain topics. This inflates consensus scores and reduces conflict detection
on softer topics.

6. Debate stability: 
LLM outputs are probabilistic. Running the same topic multiple times may
produce significantly different debates, conflict patterns, or final
conclusions. DuelMind currently does not measure or analyze this variance.

7. No memory across sessions: 
Each conversation starts fresh. There is no way to compare how the same models
reason about the same topic across multiple runs without manually exporting and
reviewing the logs.

8. Single LLM provider: 
Everything runs through Groq. If Groq's API is down or rate limited, the entire
system stops. There is no fallback to another provider.

## Roadmap

- Improve consensus scoring (judge score + embedding similarity)
- Belief shift tracking (measure stance changes across turns)
- Claim graph visualization (argument graph of extracted claims)
- Model selector (choose LLMs for debate)
- Conversation history (save sessions)
