const statusEl=document.getElementById('status');
document.getElementById('submitBtn').addEventListener('click',()=>{
  const address=window.CHARTERCORE_CONFIG?.contractAddress;
  if(!address){statusEl.innerHTML='<span class="status-dot"></span> Draft prepared — add the deployed contract address to config.js to connect the builder.';return;}
  statusEl.innerHTML='<span class="status-dot"></span> Contract configured. Submit through your GenLayer client to invoke consensus.';
});
