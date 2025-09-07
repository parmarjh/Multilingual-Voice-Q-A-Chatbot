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
