# Example using Google Cloud TTS (or ElevenLabs)
from google.cloud import texttospeech


async def text_to_speech(text, lang_code='hi-IN'):
client = texttospeech.TextToSpeechClient()
input_text = texttospeech.SynthesisInput(text=text)
voice = texttospeech.VoiceSelectionParams(language_code=lang_code, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
return response.audio_content
