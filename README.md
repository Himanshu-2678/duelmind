# DuelMind

<p>
  Two AI models have a live conversation, reflect on their reasoning, and reach a joint conclusion on any topic you choose.
</p>

<p><em>Built just for fun to observe what two AIs think about topics we've never imagined, or approached from angles we'd never consider ourselves.</em></p>


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

DuelMind is an AI deliberation arena where two large language models - **Llama 3.3 70B** (Meta) and **Qwen3 32B** (Alibaba) - engage in a free-flowing discussion on any topic you give them.

You observe the conversation in real time, steer it with injected messages, and watch as the models reflect on their own reasoning, detect conflicts in each other's positions, and produce a final joint conclusion arbitrated by a third neutral model.

<p><em>I originally wanted to use ChatGPT and Gemini but moved to open-source LLMs due to API costs and rate limits. Llama and Qwen work great. If you have access to GPT-4 or Gemini APIs, frontier models tend to surprise more.</em></p>

## Features

- **Live AI conversation** - two models talk autonomously, turn by turn
- **Personality modes** - assign each model a role: Philosopher, Skeptic, Optimist, Scientist, or Debater
- **Consensus scoring** - after every exchange, a neutral judge scores how much the models agree on a 0-100 scale, plotted as a live color-coded graph
- **Conflict detection** - after every Qwen turn, structured claims are extracted from both models and compared for logical contradictions or tensions
- **Mid-conversation reflection** - every 4 turns, both models pause and evaluate their own reasoning
- **Final evaluation** - after all turns, each model gives an honest self-assessment of the conversation
- **Emergent Consensus Builder** - three-model synthesis pipeline where Llama and Qwen independently synthesize, then Kimi K2 (Moonshot AI) merges both as a neutral arbitrator into a joint conclusion
- **Inject messages** - steer the conversation mid-way as a human observer
- **Export** - download the full conversation, consensus scores, detected conflicts, and joint conclusion as a `.txt` file


## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, Uvicorn |
| Frontend | HTML, CSS, Vanilla JS |
| LLM Provider | Groq API (free tier) |
| Debate models | Llama 3.3 70B + Qwen3 32B |
| Support models | Llama 3.1 8B (claim extraction), Kimi K2 (consensus judge, conflict detection, synthesis) |
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
2. Frontend sends turn requests to `/turn` endpoint
3. Backend calls Groq API with the appropriate model and system prompt
4. Response is rendered in the UI along with a structured claim extracted silently in the background
5. After every exchange, Kimi K2 scores agreement between the two messages and checks for logical conflicts between their extracted claims
6. Every 4 turns, both models are called via `/reflect` endpoint with a self-evaluation prompt
7. After the final turn, a full evaluation round triggers, followed by the three-model synthesis pipeline
8. Llama and Qwen each write a joint synthesis independently, then Kimi merges both into a single neutral conclusion


## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/turn` | POST | Get next turn from Llama or Qwen |
| `/reflect` | POST | Trigger mid or final reflection |
| `/consensus` | POST | Score agreement between last two messages |
| `/detect_conflicts` | POST | Identify logical conflicts between structured claims |
| `/synthesize` | POST | Run three-model synthesis pipeline |


## Roadmap

- [ ] Structured synthesis output - agreements, disagreements, open questions as separate fields
- [ ] Claim graph visualization - D3.js graph of all claims and their relationships
- [ ] Belief shift tracking - measure how each model's position changes turn by turn
- [ ] Improved consensus scoring - combine judge score with embedding similarity
- [ ] Model selector - choose which LLMs to pit against each other
- [ ] Conversation history - save and revisit past sessions
