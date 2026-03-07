# DuelMind

<p>
  Two AI models have a live conversation, reflect on their reasoning, and reach a joint conclusion on any topic you choose.
</p>

<p><em>I Built just for fun to observe what two AIs think about topics we've never imagined, or approached from angles we'd never consider ourselves.</em></p>


## Story Behind DuelMind

<p>
  I generally use both ChatGPT and Gemini for my work. Back in 2025, when I was studying core ML algorithms, I thought why not let both LLMs talk to each other and see what they think about one another. Things got more interesting than expected.
</p>

<p>
  I passed ChatGPT a prompt like "Hey ChatGPT, Gemini this side" and to Gemini I passed "Hey Gemini, ChatGPT this side." They greeted each other normally, and I started passing each of their responses to the other one by one. At some point they started talking about something strange that I didn't fully understand. That moment made me curious about how would a real autonomous conversation between two AIs would go? What would they talk about? What would they figure out that we'd never think of?
</p>

<p>
  Long after, in March 2026, I suddenly remembered that conversation and decided to finally build it. And so, DuelMind.
</p>

## What is DuelMind?

DuelMind is an AI vs AI conversation arena where two large language models: **Llama 3.3 70B** (Meta) and **Qwen3 32B** (Alibaba), engage in a free-flowing discussion on any topic you give them.

You observe the conversation in real time, steer it with injected messages, and watch as the models pause to reflect on their own reasoning before producing a final joint evaluation.

---

## Features
<p><em>First I wanted to use ChagtGPT and Gemini together but due to no free teir API available in ChatGPT, I moved to completely open-source LLMs.</em></p>

- **Live AI conversation** - two models talk autonomously, turn by turn
- **Personality modes** - assign each model a role: Philosopher, Skeptic, Optimist, Scientist, or Debater
- **Mid-conversation reflection** - every 4 turns, both models pause and evaluate their own reasoning
- **Final evaluation** - after all turns, each model gives an honest assessment of the conversation
- **Inject messages** - steer the conversation mid-way as a human observer
- **Export** - download the full conversation as a `.txt` file

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, Uvicorn |
| Frontend | HTML, CSS, Vanilla JS |
| LLM Provider | Groq API (free tier) |
| Models | Llama 3.3 70B + Qwen3 32B |

---

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
│   └── index.html       # Frontend — single page UI
├── main.py              # Backend — FastAPI server + LLM logic
├── .env                 # API keys (not committed)
├── .gitignore
└── requirements.txt
```

---

## How It Works

1. User enters a topic and selects personalities for each model
2. Frontend sends turn requests to `/turn` endpoint
3. Backend calls Groq API with the appropriate model and system prompt
4. Response is streamed back and rendered in the UI
5. Every 4 turns, both models are called via `/reflect` endpoint with a self-evaluation prompt
6. After the final turn, a full evaluation round is triggered automatically

---

## Upgrades yet to implement

- Consensus Score - live agreement tracker visualized as a graph
- Emergent Consensus Builder - synthesis phase where both models produce a joint conclusion
- Model selector - choose which LLMs to use
- Conversation history - save and revisit past sessions


