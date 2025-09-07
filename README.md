# Multilingual-Voice-Q-A-Chatbot
Multilingual Voice Q&amp;A Chatbot — Complete MVP Scaffold based
# Multilingual Voice Q&A Chatbot — Complete MVP Scaffold

यहाँ पूरा scaffold, रन-इन्स्ट्रक्शंस, और कोड स्निपेट्स दिए गए हैं ताकि आप तुरंत prototype चला सकें और बाद में इसे AI Studio (Google/Meta) पर adapt कर सकें।

---

## Overview
एक single-repo full-stack prototype जिसमें शामिल हैं:

- Frontend: Next.js (React) — microphone capture, language toggle, conversation UI
- Backend: FastAPI (Python) — endpoints: /stt, /query, /tts
- RAG: OpenAI embeddings + vector DB (Pinecone placeholder) for retrieval
- STT: OpenAI Whisper or Google Speech-to-Text (examples for both)
- TTS: Google Cloud TTS / ElevenLabs example
- Docker + docker-compose for local dev
- Env management (.env.example)
- Deployment notes for Google AI Studio (Gemini) and Meta AI Studio

---

## Repo structure

```
multilingual-chatbot-mvp/
├─ frontend/            # Next.js app
│  ├─ pages/
│  │  └─ index.js
│  ├─ components/
│  │  └─ ChatUI.jsx
│  └─ package.json
├─ backend/             # FastAPI app
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ routes.py
│  │  └─ utils/
│  │     ├─ stt.py
│  │     ├─ tts.py
│  │     └─ rag.py
│  ├─ requirements.txt
│  └─ Dockerfile
├─ docker-compose.yml
├─ .env.example
└─ README.md
```

---

## .env.example

```
# OpenAI
OPENAI_API_KEY=sk-...
# Pinecone
PINECONE_API_KEY=...
PINECONE_ENV=...
# Google TTS (optional)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-cred.json
# ElevenLabs
ELEVEN_API_KEY=...
# App
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

---

## Backend — FastAPI (app/main.py)

```python
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.routes import router

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
```


### Backend routes (app/routes.py)

```python
from fastapi import APIRouter, UploadFile, File
from app.utils.stt import speech_to_text
from app.utils.rag import answer_from_query
from app.utils.tts import text_to_speech

router = APIRouter()

@router.post('/stt')
async def stt_endpoint(audio: UploadFile = File(...)):
    # audio: bytes
    text, lang = await speech_to_text(audio)
    return {'text': text, 'language': lang}

@router.post('/query')
async def query_endpoint(payload: dict):
    q = payload.get('question')
    lang = payload.get('language', 'en')
    answer, sources = await answer_from_query(q, lang)
    return {'answer': answer, 'sources': sources}

@router.post('/tts')
async def tts_endpoint(payload: dict):
    text = payload.get('text')
    audio_bytes = await text_to_speech(text)
    return StreamingResponse(io.BytesIO(audio_bytes), media_type='audio/mpeg')
```


### STT helper (app/utils/stt.py)

```python
import aiofiles
import tempfile
from openai import OpenAI

async def speech_to_text(upload_file):
    # Save upload to temp file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    content = await upload_file.read()
    tmp.write(content)
    tmp.flush()
    tmp.close()

    # Option A: OpenAI Whisper (if using OpenAI's API)
    client = OpenAI()
    with open(tmp.name, 'rb') as f:
        res = client.audio.transcriptions.create(model='whisper-1', file=f)
    text = res.text
    # language detection: naive (could use langdetect)
    from langdetect import detect
    lang = detect(text)
    return text, lang

    # Option B: Google STT -> implement if preferred
```


### RAG helper (app/utils/rag.py)

```python
# pseudocode for retrieval + answer
from openai import OpenAI

client = OpenAI()

async def answer_from_query(question, lang='en'):
    # 1. create embedding for question
    emb = client.embeddings.create(model='text-embedding-3-large', input=question)
    vector = emb.data[0].embedding
    # 2. query Pinecone (or local vector DB) -> returned docs
    # placeholder: docs = query_vector_db(vector)
    docs = [
        {'title': 'Doc1', 'text': 'Example content from site', 'url': 'https://example.com'}
    ]
    # 3. call LLM with retrieved context
    prompt = f"Use the following docs to answer the question (language: {lang}):\n\nDocs:\n"
    for d in docs:
        prompt += f"- {d['title']}: {d['text']} (source: {d['url']})\n"
    prompt += f"\nQuestion: {question}\nAnswer concisely and include sources."
    resp = client.chat.completions.create(model='gpt-4o-mini', messages=[{"role":"user","content":prompt}])
    answer = resp.choices[0].message.content
    sources = [d['url'] for d in docs]
    return answer, sources
```


### TTS helper (app/utils/tts.py)

```python
# Example using Google Cloud TTS (or ElevenLabs)
from google.cloud import texttospeech

async def text_to_speech(text, lang_code='hi-IN'):
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code=lang_code, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    return response.audio_content
```

---

## Frontend — Next.js (pages/index.js)

```jsx
import React, {useState, useRef} from 'react'

export default function Home(){
  const [messages, setMessages] = useState([])
  const [listening, setListening] = useState(false)
  const mediaRef = useRef(null)

  async function startRecording(){
    const stream = await navigator.mediaDevices.getUserMedia({audio:true})
    const mediaRecorder = new MediaRecorder(stream)
    const chunks = []
    mediaRecorder.ondataavailable = e => chunks.push(e.data)
    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunks, {type:'audio/wav'})
      const fd = new FormData()
      fd.append('audio', blob, 'input.wav')
      const res = await fetch(process.env.NEXT_PUBLIC_BACKEND_URL + '/stt', {method:'POST', body:fd})
      const data = await res.json()
      // show question
      setMessages(prev => [...prev, {role:'user', text:data.text}])
      // query backend
      const qres = await fetch(process.env.NEXT_PUBLIC_BACKEND_URL + '/query', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({question:data.text, language:data.language})})
      const qdata = await qres.json()
      setMessages(prev => [...prev, {role:'assistant', text:qdata.answer, sources:qdata.sources}])
    }
    mediaRecorder.start()
    setListening(true)
    setTimeout(()=>{ mediaRecorder.stop(); setListening(false)}, 4000)
  }

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold">Multilingual Voice Chatbot</h1>
      <button onClick={startRecording} className="mt-4">{listening? 'Listening...' : 'Speak'}</button>
      <div className="mt-6">
        {messages.map((m,i)=> (<div key={i}><b>{m.role}:</b> {m.text} {m.sources && <div>Sources: {m.sources.join(', ')}</div>}</div>))}
      </div>
    </div>
  )
}
```

---

## Docker

**backend/Dockerfile**

```
FROM python:3.11-slim
WORKDIR /app
COPY ./app /app
RUN pip install --upgrade pip && pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - '8000:8000'
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
  frontend:
    build: ./frontend
    ports:
      - '3000:3000'
    environment:
      - NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

---

## Local run (dev)

1. Copy `.env.example` → `.env` and fill keys.
2. From repo root: `docker-compose up --build`
3. Open `http://localhost:3000`

---

## Deploying to Google AI Studio / Gemini (notes)

1. Use Gemini/GMP for LLM calls instead of OpenAI if you want to host on Google AI Studio.
2. Google AI Studio lets you "Get code" snippets and deploy serverless endpoints; swap the OpenAI client calls to Gemini REST API using the API key from Google Cloud.
3. For STT/TTS you can use Google's Speech-to-Text and Text-to-Speech with service account credentials.
4. Ensure CORS and secure key storage.

---

## Deploying / Adapting to Meta AI Studio (notes)

1. Meta's AI Studio (ai.meta.com/ai-studio) is authoring & hosting for AI characters. It expects a prompt + personality; it's not a general-purpose app hosting like Vercel.
2. To use Meta's Llama/GPT-like models you can create a character and set webhooks or API backends to call your RAG pipeline. Use their developer docs to expose your backend to the character.
3. If your goal is to showcase a demo to Meta talent, mention in your application that you used Llama/GPT/Whisper-compatible stack and provide a live demo URL (Vercel + backend) and a short writeup.

---

## Hiring / Outreach support (quick package)

- I included a ready-to-use JD templates and 4-step outreach sequence in the `extras/outreach.md` file (Add your personalization tokens: {name}, {company}, {role}).
- Tip: For Meta applications, include a 2-min demo video showing: mic → speech → answer with sources → TTS playback. Attach the GitHub link and concise README showing architecture.

---

## Next steps I can do for you (pick any or all):
1. Push this scaffold to a GitHub repo and provide repo link.
2. Fill in Pinecone indexing script to ingest your selected websites for RAG.
3. Swap OpenAI calls to Google Gemini (if you prefer AI Studio) and provide exact code for Gemini API calls.
4. Create a 2-min demo video and a README tuned for Meta job applications.

---

*
