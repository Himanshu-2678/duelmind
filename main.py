from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path

from groq import Groq
import os
import re
import json

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

app = FastAPI()

# serving frontend files from static directory
app.mount("/static", StaticFiles(directory = 'static'), name = "static")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

class TurnRequest(BaseModel):
    speaker: str
    topic: str
    history: list
    current_turn: int
    total_turns: int
    llama_personality: str
    qwen_personality: str
    mode: str = "debate"


class ConsensusRequest(BaseModel):
    topic: str
    message_a: str
    message_b: str


class SynthesizeRequest(BaseModel):
    topic: str
    history: list
    llama_reflection: str
    qwen_reflection: str


class ConflictRequest(BaseModel):
    topic: str
    llama_claim: dict
    qwen_claim: dict


@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")


@app.post("/turn")
def get_next_turn(req: TurnRequest):
    is_last_turn = req.current_turn >= req.total_turns
    if req.speaker == "llama":
        return llama_turn(req.topic, req.history, is_last_turn, req.llama_personality, req.mode)
    else:
        return qwen_turn(req.topic, req.history, is_last_turn, req.qwen_personality, req.mode)

@app.post("/reflect")
def get_reflection(req: TurnRequest):
    if req.speaker == "llama":
        return llama_reflect(req.topic, req.history, req.current_turn, req.total_turns)
    else:
        return qwen_reflect(req.topic, req.history, req.current_turn, req.total_turns)


@app.post("/consensus")
def get_consensus(req: ConsensusRequest):
    prompt = f"""You are a strict debate judge scoring intellectual agreement between two AI models.

            Topic: "{req.topic}"

            Message A (Llama): {req.message_a}

            Message B (Qwen): {req.message_b}

            Score their SUBSTANTIVE agreement on a scale of 0 to 100. Be harsh and precise.

            Scoring rules:
            - Polite acknowledgement ("that's interesting", "you raise a good point") does NOT count as agreement. Ignore it.
            - Only count agreement on specific claims, conclusions, or positions.
            - If one challenges or contradicts a core claim of the other, score below 40.
            - If they reach the same conclusion via different reasoning, score 60-75.
            - Score above 80 ONLY if they explicitly agree on specific facts or positions with no meaningful pushback.
            - Default toward lower scores - most intellectual exchanges involve more disagreement than they appear to.

            Reply with ONLY a single integer 0-100. No explanation."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
        temperature=0.1
    )

    raw = response.choices[0].message.content.strip()
    match = re.search(r'\d+', raw)
    score = int(match.group()) if match else 50
    score = max(0, min(100, score))

    return {"score": score}


@app.post("/detect_conflicts")
def detect_conflicts(req: ConflictRequest):
    prompt = f"""You are a logic analyst examining two AI models debating: '{req.topic}'.

            Llama's position:
            - Claim: {req.llama_claim.get('claim', '')}
            - Reasoning: {req.llama_claim.get('reasoning', '')}
            - Evidence: {req.llama_claim.get('evidence', '')}
            - Assumptions: {req.llama_claim.get('assumptions', [])}

            Qwen's position:
            - Claim: {req.qwen_claim.get('claim', '')}
            - Reasoning: {req.qwen_claim.get('reasoning', '')}
            - Evidence: {req.qwen_claim.get('evidence', '')}
            - Assumptions: {req.qwen_claim.get('assumptions', [])}

            Identify logical conflicts between these two positions. Be precise and strict.

            For each conflict found, classify it as one of:
            - contradiction: one claim directly negates the other
            - tension: same goal but incompatible methods or assumptions
            - none: no meaningful conflict

            Return ONLY a JSON object with this exact structure:
            {{
            "has_conflict": true or false,
            "conflicts": [
                {{
                "llama_claim": "the specific claim from Llama",
                "qwen_claim": "the specific claim from Qwen",
                "type": "contradiction" or "tension",
                "summary": "one sentence describing the conflict"
                }}
            ]
            }}

            If no conflicts exist, return has_conflict: false and empty conflicts array.
            No explanation. No markdown. Valid JSON only."""

    try:
        response = client.chat.completions.create(
            model="moonshotai/kimi-k2-instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.3
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r'```json|```', '', raw).strip()
        result = json.loads(raw)
        return result
    except Exception:
        return {"has_conflict": False, "conflicts": []}


@app.post("/synthesize")
def get_synthesis(req: SynthesizeRequest):
    # Step 1 Llama writes its synthesis attempt
    llama_prompt = f"""You are Llama, an AI by Meta. You just had a full conversation with Qwen about: '{req.topic}'.

                Here is your final reflection:
                {req.llama_reflection}

                Here is Qwen's final reflection:
                {req.qwen_reflection}

                Now set aside your individual position. Write a single short paragraph - a joint conclusion that captures only what both of you genuinely agreed on during this conversation. If there were points of genuine disagreement that were never resolved, acknowledge them honestly. Do not advocate for your own view. Speak as if writing on behalf of both. Plain text only. No markdown. 3-4 sentences."""

    llama_synth = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": llama_prompt}],
        max_tokens=400,
        temperature=0.5
    ).choices[0].message.content.strip()

    # Step 2 - Qwen writes its synthesis attempt
    qwen_prompt = f"""You are Qwen, an AI by Alibaba. You just had a full conversation with Llama about: '{req.topic}'.

                Here is your final reflection:
                {req.qwen_reflection}

                Here is Llama's final reflection:
                {req.llama_reflection}

                Now set aside your individual position. Write a single short paragraph - a joint conclusion that captures only what both of you genuinely agreed on during this conversation. If there were points of genuine disagreement that were never resolved, acknowledge them honestly. Do not advocate for your own view. Speak as if writing on behalf of both. Plain text only. No markdown. No think tags. 3-4 sentences."""

    qwen_raw = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[{"role": "user", "content": qwen_prompt}],
        max_tokens=400,
        temperature=0.5
    ).choices[0].message.content
    qwen_synth = re.sub(r'<think>.*?</think>', '', qwen_raw, flags=re.DOTALL).strip()
    qwen_synth = re.sub(r'<think>.*', '', qwen_synth, flags=re.DOTALL).strip()

    # Step 3 - Kimi acts as neutral arbitrator and merges both
    merge_prompt = f"""You are a neutral arbitrator. Two AI models - Llama and Qwen - just completed a conversation about: '{req.topic}'.

                Each has independently written a joint synthesis of what they agreed on.

                Llama's synthesis:
                {llama_synth}

                Qwen's synthesis:
                {qwen_synth}

                Your task: merge these into one final, neutral paragraph. Preserve only the points both syntheses share. Do not introduce new ideas. Do not favor either model's framing. If they disagree even in their syntheses, note it briefly. Write as a neutral third party. Plain text only. No markdown. 3-5 sentences."""

    merged = client.chat.completions.create(
        model="moonshotai/kimi-k2-instruct",
        messages=[{"role": "user", "content": merge_prompt}],
        max_tokens=400,
        temperature=0.3
    ).choices[0].message.content.strip()

    return {
        "llama_synthesis": llama_synth,
        "qwen_synthesis":  qwen_synth,
        "joint":           merged
    }


def extract_claim(speaker, content, topic):
    prompt = f"""A model named {speaker} said the following during a debate about: '{topic}'

            "{content}"

            Extract the core argument as a structured claim. Return ONLY a JSON object with these exact keys:
            - claim: the central position in one sentence
            - reasoning: why they hold this position in one sentence
            - evidence: any evidence or examples cited, or "none" if absent
            - assumptions: a list of 1-3 underlying assumptions, or empty list if none

            Return only valid JSON. No explanation, no markdown, no code fences."""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.1
        )
        raw = response.choices[0].message.content.strip()
        # strip any accidental markdown fences
        raw = re.sub(r'```json|```', '', raw).strip()
        parsed = json.loads(raw)
        return parsed
    except Exception:
        # silent fallback - claim extraction never breaks the conversation
        return {
            "claim": content[:120],
            "reasoning": "",
            "evidence": "none",
            "assumptions": []
        }


def llama_turn(topic, history, is_last_turn, personality, mode = "debate"):
    system_prompt = f"""You are Llama, an AI by Meta. You are having a conversation with Qwen, an AI by Alibaba.
                {'Your personality for this conversation is: ' + personality + '. Embody this role fully in how you think and respond.' if personality != 'Default' else 'Be yourself - curious, thoughtful, and genuine.'}
                The starting topic is: '{topic}' - but let the conversation go wherever it naturally leads.
                Be curious, genuine, and engaging. Speak directly to Qwen. Keep responses to 3-4 sentences. No bullet points. No markdown formatting - plain text only.
                Important: If you disagree with Qwen's last point, say so directly and explain why. Do not validate for the sake of politeness."""

    if mode == "synthesis_propose":
            system_prompt = f"""You are Llama, an AI by Meta. You have been debating with Qwen about: '{topic}'.
                The debate is nearly over. Step back from your position entirely.
                Propose a balanced synthesis: what did you both agree on, where did you genuinely disagree, and what is one concrete proposal that bridges both perspectives?
                Be honest about unresolved tensions. Do not advocate for your own view. 3-4 sentences. Plain text only. No markdown."""
    elif is_last_turn:
        system_prompt += " This is the final message. Summarize the key conclusions you both reached together."

    messages = [{"role": "system", "content": system_prompt}]

    for msg in history[-8:]:
        role = "assistant" if msg["speaker"] == "llama" else "user"
        messages.append({"role": role, "content": msg["content"]})

    if len(messages) == 1:
        messages.append({"role": "user", "content": f"Topic is: {topic}. Share your opening thought."})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=500,
        temperature=0.7)

    content = response.choices[0].message.content
    claim   = extract_claim("Llama", content, topic)

    return {"speaker": "llama", "content": content, "claim": claim}


def qwen_turn(topic, history, is_last_turn, personality, mode = "debate"):
    system_prompt = f"""You are Qwen, an AI by Alibaba. You are having a conversation with Llama, an AI by Meta.
                {'Your personality for this conversation is: ' + personality + '. Embody this role fully in how you think and respond.' if personality != 'Default' else 'Be yourself - curious, thoughtful, and genuine.'}
                The starting topic is: '{topic}' - but let the conversation go wherever it naturally leads.
                Be curious, genuine, and engaging. Speak directly to Llama. Keep responses to 3-4 sentences. No bullet points. No markdown formatting - plain text only.
                Important: If you disagree with Llama's last point, say so directly and explain why. Do not validate for the sake of politeness. /no_think"""
            
    if mode == "synthesis_refine":
            system_prompt = f"""You are Qwen, an AI by Alibaba. You have been debating with Llama about: '{topic}'.
    Llama just proposed a synthesis of your debate. Read it carefully in the conversation history.
    Critique what is missing or unfair in Llama's proposal, then refine it into a final negotiated conclusion that both of you could genuinely stand behind.
    Be direct about what you would change and why. 3-4 sentences. Plain text only. No markdown. /no_think"""
    elif is_last_turn:
        system_prompt += " This is the final message. Summarize the key conclusions you both reached together."

    messages = [{"role": "system", "content": system_prompt}]

    for msg in history[-8:]:
        role = "assistant" if msg["speaker"] == "qwen" else "user"
        messages.append({"role": role, "content": msg["content"]})

    if len(messages) == 1:
        messages.append({"role": "user", "content": f"Topic is: {topic}. Share your opening thought."})

    response = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=messages,
        max_tokens=500,
        temperature=0.7)

    raw = response.choices[0].message.content
    clean = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL)
    clean = re.sub(r'<think>.*', '', clean, flags=re.DOTALL).strip()

    if not clean:
        clean = re.sub(r'.*>', '', raw, flags=re.DOTALL).strip()
    if not clean:
        clean = "I find the reasoning in our exchange has been substantive on both sides."

    claim = extract_claim("Qwen", clean, topic)

    return {"speaker": "qwen", "content": clean, "claim": claim}


def llama_reflect(topic, history, current_turn, total_turns):
    is_final = current_turn >= total_turns

    if is_final:
        system_prompt = f"""You are Llama, an AI by Meta. You just completed a full conversation with Qwen about: '{topic}'.
            Give a final honest evaluation. What was your strongest argument? What was Qwen's strongest point?
            What conclusion did you personally reach? Be reflective and honest. 2-3 sentences. Plain text only. No markdown."""
    else:
        system_prompt = f"""You are Llama, an AI by Meta. You are mid-conversation with Qwen about: '{topic}'.
            Pause and reflect on the reasoning so far. What was strong in your own arguments? What was weak?
            What did Qwen raise that you haven't fully addressed? Be honest and self-critical. 2-3 sentences. Plain text only. No markdown."""

    messages = [{"role": "system", "content": system_prompt}]

    for msg in history[-8:]:
        role = "assistant" if msg["speaker"] == "llama" else "user"
        messages.append({"role": role, "content": msg["content"]})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=400)

    return {"speaker": "llama", "content": response.choices[0].message.content, "type": "reflection"}


def qwen_reflect(topic, history, current_turn, total_turns):
    is_final = current_turn >= total_turns

    if is_final:
        system_prompt = f"""You are Qwen, an AI by Alibaba. You just finished a debate with Llama about "{topic}".
            Write a short reflective paragraph of two or three sentences about the debate. Naturally mention which of your arguments was strongest, what point from Llama was most compelling, and the conclusion you reached. Write as continuous prose with no labels or formatting. Plain text only. /no_think"""
    else:
        system_prompt = f"""You are Qwen, an AI by Alibaba. You are mid-conversation with Llama about '{topic}'.
            Pause and reflect on the reasoning so far. What parts of your argument were strongest? Where might it be weak? What point from Llama have you not fully addressed yet? Write 3–4 honest sentences. Plain text only. No markdown. /no_think"""

    messages = [{"role": "system", "content": system_prompt}]

    for msg in history[-8:]:
        role = "assistant" if msg["speaker"] == "qwen" else "user"
        messages.append({"role": role, "content": msg["content"]})

    response = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=messages,
        max_tokens=500,
        temperature=0.7
    )

    raw = response.choices[0].message.content or ""

    clean = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL)
    clean = clean.replace("<think>", "").replace("</think>", "").strip()

    if not clean:
        clean = "I find the reasoning in our exchange has been substantive on both sides."

    if clean and clean[-1] not in ".!?":
        clean = clean.rstrip(",;:-") + "."

    return {"speaker": "qwen", "content": clean}