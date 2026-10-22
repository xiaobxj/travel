const fs = require('node:fs');
(async () => {
 const tabs=await (await fetch('http://127.0.0.1:9222/json/list')).json();
 const tab=tabs.find(t=>t.type==='page'&&t.url.includes('xiaohongshu.com'));
 if(!tab) throw Error('No Xiaohongshu tab');
 const ws=new WebSocket(tab.webSocketDebuggerUrl);
 await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
 let id=0; const pending=new Map();
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(pending.has(m.id)){pending.get(m.id)(m);pending.delete(m.id);}};
 const send=(method,params)=>new Promise(resolve=>{const n=++id;pending.set(n,resolve);ws.send(JSON.stringify({id:n,method,params}));});
 let out;
 if(process.argv[2]==='nav') out=await send('Page.navigate',{url:process.argv[3]});
 else out=await send('Runtime.evaluate',{expression:process.argv[3]||'document.body.innerText',returnByValue:true});
 console.log(JSON.stringify(out,null,2));ws.close();
})().catch(e=>{console.error(e);process.exitCode=1;});
