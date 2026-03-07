from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path

from groq import Groq
import os
import re

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


@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")


@app.post("/turn")
def get_next_turn(req: TurnRequest):
    is_last_turn = req.current_turn >= req.total_turns
    if req.speaker == "llama":
        return llama_turn(req.topic, req.history, is_last_turn, req.llama_personality)
    else:
        return qwen_turn(req.topic, req.history, is_last_turn, req.qwen_personality)


@app.post("/reflect")
def get_reflection(req: TurnRequest):
    if req.speaker == "llama":
        return llama_reflect(req.topic, req.history, req.current_turn, req.total_turns)
    else:
        return qwen_reflect(req.topic, req.history, req.current_turn, req.total_turns)


def llama_turn(topic, history, is_last_turn, personality):
    system_prompt = f"""You are Llama, an AI by Meta. You are having a conversation with Qwen, an AI by Alibaba.
        {'Your personality for this conversation is: ' + personality + '. Embody this role fully in how you think and respond.' if personality != 'Default' else 'Be yourself — curious, thoughtful, and genuine.'}
        The starting topic is: '{topic}' — but let the conversation go wherever it naturally leads.
        Be curious, genuine, and engaging. Speak directly to Qwen. Keep responses to 3-4 sentences. No bullet points. No markdown formatting — plain text only."""

    if is_last_turn:
        system_prompt += " This is the final message. Summarize the key conclusions you both reached together."

    messages = [{"role": "system", "content": system_prompt}]

    for msg in history[-12:]:
        role = "assistant" if msg["speaker"] == "llama" else "user"
        messages.append({"role": role, "content": msg["content"]})

    if len(messages) == 1:
        messages.append({"role": "user", "content": f"Topic is: {topic}. Share your opening thought."})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=500,
        temperature=0.7)

    return {"speaker": "llama", "content": response.choices[0].message.content}


def qwen_turn(topic, history, is_last_turn, personality):
    system_prompt = f"""You are Qwen, an AI by Alibaba. You are having a conversation with Llama, an AI by Meta.
        {'Your personality for this conversation is: ' + personality + '. Embody this role fully in how you think and respond.' if personality != 'Default' else 'Be yourself — curious, thoughtful, and genuine.'}
        The starting topic is: '{topic}' — but let the conversation go wherever it naturally leads.
        Be curious, genuine, and engaging. Speak directly to Llama. Keep responses to 3-4 sentences. No bullet points. No markdown formatting — plain text only."""
    
    if is_last_turn:
        system_prompt += " This is the final message. Summarize the key conclusions you both reached together."

    messages = [{"role": "system", "content": system_prompt}]

    for msg in history[-12:]:
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

    return {"speaker": "qwen", "content": clean}


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

    for msg in history[-12:]:
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
        system_prompt = f"""You are Qwen, an AI by Alibaba. You just completed a full conversation with Llama about: '{topic}'.
    Give a final honest evaluation. What was your strongest argument? What was Llama's strongest point?
    What conclusion did you personally reach? Be reflective and honest. 2-3 sentences. Plain text only. No markdown."""
    else:
        system_prompt = f"""You are Qwen, an AI by Alibaba. You are mid-conversation with Llama about: '{topic}'.
    Pause and reflect on the reasoning so far. What was strong in your own arguments? What was weak?
    What did Llama raise that you haven't fully addressed? Be honest and self-critical. 3-4 sentences. Plain text only. No markdown. Do not use think tags. Respond directly."""

    messages = [{"role": "system", "content": system_prompt}]

    for msg in history[-12:]:
        role = "assistant" if msg["speaker"] == "qwen" else "user"
        messages.append({"role": role, "content": msg["content"]})

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

    return {"speaker": "qwen", "content": clean}