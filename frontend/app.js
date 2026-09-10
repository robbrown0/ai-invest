'use strict';
const notice=document.getElementById('notice');
const form=document.getElementById('connect-form');
const key=document.getElementById('api-key');
const secret=document.getElementById('api-secret');
const selector=document.getElementById('connection');
const connect=document.getElementById('connect-button');
let busy=false;
function clearKeys(){key.value='';secret.value='';}
window.addEventListener('pagehide',clearKeys);
window.addEventListener('pageshow',clearKeys);
document.addEventListener('visibilitychange',()=>{if(document.hidden)clearKeys();});
function say(value){notice.textContent=value;}
async function request(path,body){
 const options={cache:'no-store',credentials:'same-origin',redirect:'error',signal:AbortSignal.timeout(35000)};
 if(body!==undefined){
  const auth=await fetch('/api/session',{...options}).then(r=>{if(!r.ok)throw new Error();return r.json();});
  options.method='POST';options.headers={'Content-Type':'application/json','X-CSRF-Token':auth.csrf};
  options.body=JSON.stringify(body);
 }
 try{const response=await fetch(path,options);if(!response.ok)throw new Error();return await response.json();}
 finally{delete options.body;}
}
function element(tag,text){const node=document.createElement(tag);if(text!==undefined)node.textContent=String(text);return node;}
function details(parent,values){const list=element('dl');for(const [label,value]of values){list.append(element('dt',label),element('dd',value??'Unavailable'));}parent.append(list);}
function table(parent,title,rows,columns){parent.append(element('h3',title));if(!rows?.length){parent.append(element('p','No rows in this observation.'));return;}
 const wrap=element('div');wrap.className='table-scroll';const grid=element('table');const head=element('tr');for(const column of columns)head.append(element('th',column[0]));grid.append(head);
 for(const row of rows){const tr=element('tr');for(const column of columns)tr.append(element('td',row[column[1]]??'—'));grid.append(tr);}wrap.append(grid);parent.append(wrap);}
async function action(path,message){if(busy)return;busy=true;say(message);try{await request(path,{});await load();say('Updated.');}catch{say('Could not confirm the operation. Refresh to check its current state; credentials are never redisplayed.');}finally{busy=false;}}
async function load(){
 const result=await request('/api/connections');const accounts=document.getElementById('accounts');accounts.replaceChildren();
 const selected=selector.value;selector.replaceChildren(new Option('Add a PAPER connection',''));
 for(const connection of result.connections){
  selector.append(new Option('PAPER '+connection.account_id,connection.id));
  const card=element('article');card.className='account';card.append(element('h3',connection.state==='CONNECTED'?'Connected · PAPER':'Disconnected · PAPER'));
  details(card,[['Account',connection.account_id],['Last stored observation',connection.updated_at]]);
  if(connection.state==='CONNECTED'){
   const snapshot=connection.snapshot;const account=snapshot.account||{};
   details(card,[['Cash (USD)',account.cash],['Equity (USD)',account.equity],['Account status',account.status],['Trading blocked',account.trading_blocked],['Account observed',account.observed_at]]);
   table(card,'Positions',snapshot.positions,[['Symbol','symbol'],['Quantity','quantity'],['Market value (USD)','market_value']]);
   table(card,'Recent orders (not complete reconciliation)',snapshot.orders,[['Symbol','symbol'],['Side','side'],['Quantity','quantity'],['Filled','filled_quantity'],['Status','status']]);
   if(snapshot.market)details(card,[['SPY IEX bid / ask',snapshot.market.bid+' / '+snapshot.market.ask],['Quote observed',snapshot.market.observed_at]]);
   else card.append(element('p','Market quote unavailable or not yet refreshed.'));
   const refresh=element('button','Refresh real PAPER data');refresh.type='button';refresh.onclick=()=>action('/api/connections/'+connection.id+'/refresh','Fetching PAPER account data…');
   const disconnect=element('button','Disconnect');disconnect.type='button';disconnect.onclick=()=>{if(window.confirm('Disconnect ai-invest? This removes local credentials, but does NOT revoke the key at Alpaca or cancel orders.'))action('/api/connections/'+connection.id+'/disconnect','Disconnecting…');};
   card.append(refresh,disconnect);
  }accounts.append(card);
 }
 if(!result.connections.length)accounts.append(element('p','No PAPER connection yet. Use the setup form above.'));
 selector.value=selected;connect.disabled=false;
}
selector.addEventListener('change',()=>{clearKeys();connect.textContent=selector.value?'Replace PAPER credentials':'Connect Alpaca PAPER';});
form.addEventListener('submit',async event=>{
 event.preventDefault();if(busy)return;busy=true;connect.disabled=true;
 const body={key:key.value,secret:secret.value};const id=selector.value;clearKeys();
 say('Saving securely and validating against Alpaca PAPER…');
 try{const result=await request(id?'/api/connections/'+id+'/credentials':'/api/connections',body);
  body.key='';body.secret='';await load();say('Connected to Alpaca PAPER. Loading account data…');
  await new Promise(resolve=>setTimeout(resolve,1100));await request('/api/connections/'+result.id+'/refresh',{});await load();say('Connected. Real PAPER data loaded. No order execution is enabled.');
 }catch{say('Connection or refresh could not be confirmed. Existing credentials are preserved when validation fails. Check status, verify PAPER keys and retry.');}
 finally{body.key='';body.secret='';clearKeys();busy=false;connect.disabled=false;}
});
load().then(()=>say('Secure PAPER workspace ready.')).catch(()=>say('Access unavailable. A trusted client certificate and configured private TLS connection are required.'));
