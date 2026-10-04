const text=document.getElementById("text"), file=document.getElementById("file");
const counter=document.getElementById("counter"), btn=document.getElementById("summarize");
function update(){counter.textContent=(text.value.trim()?text.value.trim().split(/\s+/).length:0)+" words";}
text.addEventListener("input",update);
file.addEventListener("change",()=>{if(file.files[0]){const r=new FileReader();r.onload=e=>{text.value=e.target.result;update()};r.readAsText(file.files[0]);}});
btn.addEventListener("click",async()=>{
 if(text.value.trim().split(/\s+/).filter(Boolean).length<35){alert("Please enter at least 35 words.");return;}
 const fd=new FormData(); fd.append("text",text.value); fd.append("length",document.getElementById("length").value);
 document.getElementById("loading").classList.remove("hidden");document.getElementById("result").classList.add("hidden");btn.disabled=true;
 try{const res=await fetch("/summarize",{method:"POST",body:fd});const d=await res.json();if(!res.ok)throw new Error(d.error);
 document.getElementById("summary").textContent=d.summary;document.getElementById("downloadSummary").value=d.summary;
 document.getElementById("ow").textContent=d.original_words;document.getElementById("sw").textContent=d.summary_words;document.getElementById("cr").textContent=d.compression+"%";
 document.getElementById("keywords").innerHTML=d.keywords.map(k=>`<span>${k}</span>`).join("");
 document.getElementById("result").classList.remove("hidden");
 }catch(e){alert(e.message)}finally{document.getElementById("loading").classList.add("hidden");btn.disabled=false;}
});
