"use strict";
const container=document.getElementById("release-list");
const repo="https://api.github.com/repos/BartekWiecek/mastering_PCI_DSS_Toolkit";
const history="https://github.com/BartekWiecek/mastering_PCI_DSS_Toolkit/releases";
function node(tag, text, cls) {const el=document.createElement(tag);el.textContent=text;if(cls)el.className=cls;return el;}
async function json(url){const r=await fetch(url,{cache:"no-store"});if(!r.ok)throw Error("unavailable");return r.json();}
function createCard(spec, release, fallback=false){
 const box=node("article","","release-card");
 box.append(node("h3",spec.tag),node("span",spec.channel.toUpperCase(),"badge"));
 box.append(node("p",spec.channel==="stable"?"Accepted educational companion release.":spec.channel==="candidate"?"Reviewed candidate. Not the final book-edition release.":"Earlier preview retained for evaluation."));
 if(spec.compatibility)box.append(node("p",spec.compatibility,"muted"));
 const button=node("button","Download and verify ZIP","button"),status=node("p","SHA-256 checked before saving.","muted");
 button.type="button";status.setAttribute("role","status");
 const detail=node("details","");detail.append(node("summary","SHA-256 checksum"),node("code",spec.sha256,"hash"));
 button.disabled=!globalThis.crypto?.subtle;
 button.onclick=async()=>{button.disabled=true;status.textContent="Checking archive…";try{
   const path="downloads/"+encodeURIComponent(spec.archive);const r=await fetch(path,{cache:"no-store"});if(!r.ok)throw Error();
   const bytes=await r.arrayBuffer();const h=Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",bytes)),x=>x.toString(16).padStart(2,"0")).join("");
   if(h!==spec.sha256)throw Error("checksum mismatch");
   const url=URL.createObjectURL(new Blob([bytes],{type:"application/zip"}));const link=document.createElement("a");link.href=url;link.download=spec.archive;link.click();setTimeout(()=>URL.revokeObjectURL(url),60000);status.textContent="Checksum verified. Download started.";
 }catch{status.textContent="Download not verified. Use the versioned release and check its checksum locally.";}finally{button.disabled=false;}};
 const link=node("a","Release notes and assets ↗");link.href=release?.html_url||history+"/tag/"+spec.tag;
 box.append(button,status,detail,link);container.append(box);
}
(async()=>{try{
 const m=await json("downloads/manifest.json");container.replaceChildren();
 if(m.next){try{const r=await json(repo+"/releases/tags/"+encodeURIComponent(m.next.tag));const asset=r.assets.find(a=>a.name===m.next.archive);
 if(!r.draft&&asset&&asset.digest==="sha256:"+m.next.sha256&&r.prerelease===(m.next.channel!=="stable"))createCard(m.next,r);
 else throw Error();}catch{container.append(node("p","The next release has not passed publication checks or its status could not be confirmed. It is not offered as an accepted release.","muted"));}}
 createCard(m.current,null,true);
}catch{container.replaceChildren();const a=node("a","Open verified release history ↗");a.href=history;container.append(node("p","Release status temporarily unavailable. Check the release assets and SHA-256 before use."),a);}})();
