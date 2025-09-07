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
