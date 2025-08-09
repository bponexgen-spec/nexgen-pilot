document.addEventListener('DOMContentLoaded', function(){
  // Rotating slogans
  const slogans = ["Your Complete Back Office — 24/7 Available.","Your Personal AI Assistant — Booking Appointments While You Work.","Never Miss a Call. Never Miss a Client."];
  let si = 0;
  setInterval(()=>{ document.getElementById('rotating').innerHTML = slogans[si++ % slogans.length]; }, 3500);

  // Play voice demo
  const playBtn = document.getElementById('play');
  const player = document.getElementById('player');
  const transcript = document.getElementById('transcript');
  playBtn.addEventListener('click', async ()=>{
    const scenario = document.getElementById('scenario').value;
    const lang = document.getElementById('lang').value;
    const fd = new FormData();
    fd.append('scenario', scenario);
    fd.append('language', lang);
    const res = await fetch('/voice_demo', {method:'POST', body:fd});
    const data = await res.json();
    if(data.audio_url){
      player.src = data.audio_url;
      player.play();
    } else {
      // fallback: use Web Speech API as local demo if no TTS key
      const text = data.transcript || 'Hello from NexGen demo';
      transcript.innerText = text;
      if('speechSynthesis' in window){
        const ut = new SpeechSynthesisUtterance(text);
        ut.lang = (lang==='nl') ? 'nl-NL' : 'en-US';
        window.speechSynthesis.cancel(); window.speechSynthesis.speak(ut);
      }
    }
    transcript.innerText = data.transcript || '';
  });

  // Calculator
  document.getElementById('calc').addEventListener('click', ()=>{
    const inbound = Number(document.getElementById('inbound').value||0);
    const outbound = Number(document.getElementById('outbound').value||0);
    const length = Number(document.getElementById('length').value||1);
    const minutes = Math.ceil((inbound + outbound) * length);
    let plan='Starter'; let price=49;
    if(minutes>1000){plan='Pro'; price=399}
    else if(minutes>200){plan='Growth'; price=99}
    document.getElementById('result').innerHTML = `<p>Total minutes: ${minutes} / month<br>Recommended: <strong>${plan}</strong> (€${price}/mo)</p>`;
  });

  // Contact form
  const form = document.getElementById('contactForm');
  form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const fd = new FormData(form);
    const res = await fetch('/contact', {method:'POST', body:fd});
    const data = await res.json();
    document.getElementById('formStatus').innerText = data.detail || 'Submitted';
    form.reset();
  });

  // share buttons
  document.getElementById('shareLinkedIn').addEventListener('click', ()=>{
    const url = encodeURIComponent(location.href);
    const text = encodeURIComponent("Check out NexGen BPO - AI voice agents");
    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`, '_blank');
  });
  document.getElementById('shareWA').addEventListener('click', ()=>{
    const url = encodeURIComponent(location.href);
    window.open(`https://wa.me/?text=${url}`, '_blank');
  });
});