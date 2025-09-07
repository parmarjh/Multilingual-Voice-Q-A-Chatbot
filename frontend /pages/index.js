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
