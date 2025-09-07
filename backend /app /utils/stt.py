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
