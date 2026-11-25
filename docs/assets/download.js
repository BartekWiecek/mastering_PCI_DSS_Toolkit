"use strict";
const container=document.getElementById("release-list");
const repo="https://api.github.com/repos/BartekWiecek/mastering_PCI_DSS_Toolkit";
const releases="https://github.com/BartekWiecek/mastering_PCI_DSS_Toolkit/releases";
function node(tag,text,cls){const el=document.createElement(tag);el.textContent=text;if(cls)el.className=cls;return el;}
async function json(url){const r=await fetch(url,{cache:"no-store"});if(!r.ok)throw Error("unavailable");return r.json();}
function createCard(spec,release){
 const box=node("article","","release-card");
 box.append(node("h3",spec.tag),node("span","STABLE","badge"));
 box.append(node("p","The complete Toolkit for the Third Extended Edition. Includes the workbooks, editable implementation resources and all five practical labs."));
 const button=node("button","Download Toolkit ZIP","button"),status=node("p","SHA-256 integrity verified before saving.","muted");
 button.type="button";status.setAttribute("role","status");
 const detail=node("details","");detail.append(node("summary","Release checksum (SHA-256)"),node("code",spec.sha256,"hash"));
 button.disabled=!globalThis.crypto?.subtle;
 button.onclick=async()=>{button.disabled=true;status.textContent="Checking archive…";try{
   const r=await fetch("downloads/"+encodeURIComponent(spec.archive),{cache:"no-store"});if(!r.ok)throw Error("unavailable");
   const bytes=await r.arrayBuffer();const hash=Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",bytes)),x=>x.toString(16).padStart(2,"0")).join("");
   if(hash!==spec.sha256)throw Error("checksum mismatch");
   const url=URL.createObjectURL(new Blob([bytes],{type:"application/zip"}));const link=document.createElement("a");link.href=url;link.download=spec.archive;document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);status.textContent="Checksum verified. Download started.";
 }catch{status.textContent="Download not verified. Use the release page and check its checksum locally.";}finally{button.disabled=false;}};
 const link=node("a","Release notes and checksum ↗");link.href=release.html_url;
 box.append(button,status,detail,link);container.append(box);
}
(async()=>{try{
 const m=await json("downloads/manifest.json");
 const spec=m.current;
 if(m.schema!==2||!spec||spec.channel!=="stable"||spec.review!=="accepted"||!/^v\d+\.\d+\.\d+$/.test(spec.tag)||spec.archive!=="PCI_DSS_Implementation_Toolkit_"+spec.tag+".zip"||!(/^[a-f0-9]{64}$/).test(spec.sha256))throw Error("invalid release");
 const r=await json(repo+"/releases/tags/"+encodeURIComponent(spec.tag));
 const asset=r.assets.find(a=>a.name===spec.archive);
 if(r.draft||r.prerelease||!asset||asset.digest!=="sha256:"+spec.sha256)throw Error("unverified release");
 container.replaceChildren();createCard(spec,r);
}catch{container.replaceChildren();const a=node("a","Open the current stable release ↗");a.href=releases+"/latest";container.append(node("p","The download status could not be confirmed. Use the release page and verify its published SHA-256 checksum."),a);}})();
