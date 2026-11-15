/* OpenRank: client-side-only match link creation; no token is stored here. */
const $ = (id) => document.getElementById(id);
const repoPattern = /^[\w-]{1,39}\/[\w.-]{1,100}$/;
const gamePattern = /^[a-z0-9][a-z0-9-]{0,62}$/;
const PROTOCOL = 'openrank/1';
let manifest = null;
function text(id, value) { $(id).textContent = String(value); }
function showError(message) { text('report-error', message); $('report-error').classList.remove('hidden'); }
function validRepo(value) { return repoPattern.test(value) && !value.includes('..'); }
function safeDate() { const date = new Date(); return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`; }
function githubPageUrl(repo) { const [owner,name] = repo.split('/'); return name.toLowerCase() === `${owner.toLowerCase()}.github.io` ? `https://${name}/` : `https://${owner.toLowerCase()}.github.io/${name}/`; }
async function loadManifest(repo) {
  if (!validRepo(repo)) throw new Error('リポジトリ名は owner/repo の形式で指定してください。');
  if (manifest && manifest.repository.toLowerCase() === repo.toLowerCase()) return manifest;
  for (const branch of ['main','master']) {
    const url = `https://raw.githubusercontent.com/${repo}/${branch}/manifest.json`;
    try {
      const response = await fetch(url, {cache:'no-cache'});
      if (!response.ok) continue;
      const data = await response.json();
      if (data.protocol === PROTOCOL && data.repository.toLowerCase() === repo.toLowerCase() && data.games && typeof data.games === 'object') return data;
    } catch (_) { /* try other branch */ }
  }
  throw new Error(`${repo} のmanifest.jsonを読み込めません。Actionsを手動実行し、公開リポジトリを確認してください。`);
}
function makeIssue(match, repo) {
  const body = `OpenRank 対戦結果申告\n\n両者の同一内容のIssueが必要です。試合ID: ${match.id}\n\n\`\`\`openrank-match\n${JSON.stringify(match, null, 2)}\n\`\`\`\n`;
  return `https://github.com/${repo}/issues/new?title=${encodeURIComponent('[OpenRank] '+match.id)}&body=${encodeURIComponent(body)}`;
}
function renderGames(games) {
  const grid=$('game-grid'); grid.replaceChildren();
  const entries=Object.entries(games||{});
  if (!entries.length) { const p=document.createElement('p');p.className='muted';p.textContent='登録ゲームはまだありません。profile.jsonを編集してActionsを実行してください。';grid.append(p);return; }
  for(const [id,g] of entries) {
    const node=document.createElement('article');node.className='game';
    const genre=document.createElement('div');genre.className='genre';genre.textContent=g.genre||'GAME';
    const title=document.createElement('h3');title.textContent=g.name||id;
    const rp=document.createElement('div');rp.className='rp';rp.textContent=String(g.rp)+' ';
    const small=document.createElement('small');small.textContent='RP';rp.append(small);
    const score=document.createElement('div');score.className='score';
    const wl=document.createElement('span');wl.textContent=`${g.wins}勝 ${g.losses}敗`;
    const wr=document.createElement('span');wr.textContent=`勝率 ${Number(g.win_rate||0).toFixed(1)}%`;
    score.append(wl,wr);
    const bar=document.createElement('div');bar.className='bar';const filled=document.createElement('i');filled.style.width=`${Math.max(0,Math.min(100,Number(g.win_rate)||0))}%`;bar.append(filled);
    node.append(genre,title,rp,score,bar);grid.append(node);
  }
}
async function renderHistory() {
  const target=$('matches');target.replaceChildren();
  try {
    const response=await fetch('data/matches.json',{cache:'no-store'});
    if (!response.ok) throw new Error('履歴はまだありません');
    const matches=await response.json();
    if (!matches.length) throw new Error('確定した試合はまだありません');
    for (const m of matches.slice(-25).reverse()) {
      const row=document.createElement('div');row.className='match';
      const info=document.createElement('div');const heading=document.createElement('strong');heading.textContent=`${m.game} · ${m.won?'勝利':'敗北'}`;
      const sub=document.createElement('small');sub.textContent=`対戦相手 ${m.opponent} · ${m.played_at}`;info.append(heading,sub);
      const delta=document.createElement('strong');delta.textContent=`${m.delta>=0?'+':''}${m.delta} RP`;delta.className=m.delta>=0?'positive':'negative';row.append(info,delta);target.append(row);
    }
  } catch(e) { const p=document.createElement('p');p.className='muted';p.textContent=e.message;target.append(p); }
}
function showMatchPreview(m) {
  text('match-preview', `対象: ${m.game} / ${m.played_at}\n勝者: ${m.winner}\n対戦: ${m.repos[0]} (${m.before[m.repos[0]]} RP) vs ${m.repos[1]} (${m.before[m.repos[1]]} RP)\n試合ID: ${m.id}\n※勝者とレートを確認してからIssueを投稿してください。`);
}
function encodedInvite(match) { return `${location.origin}${location.pathname}?match=${encodeURIComponent(JSON.stringify(match))}`; }
function acceptInvite() {
  const params=new URLSearchParams(location.search);const encoded=params.get('match');if(!encoded)return;
  try {
    const m=JSON.parse(encoded);
    if(m.protocol!==PROTOCOL || !Array.isArray(m.repos) || m.repos.length!==2 || !m.repos.every(validRepo) || !m.repos.includes(m.winner) || !gamePattern.test(m.game)) throw Error();
    const host=manifest?.repository;
    const peer=m.repos.find(r=>r.toLowerCase()!==host?.toLowerCase()) || m.repos[0];
    $('self-repo').value=peer;
    $('other-repo').value=m.repos.find(r=>r!==peer)||'';
    $('game-id').value=m.game;
    $('played-at').value=m.played_at;
    $('winner').value=m.winner===peer?'self':'other';
    $('report-form').classList.add('hidden');
    $('report-output').classList.remove('hidden');
    $('own-issue').href=makeIssue(m,peer);
    $('invite-url').value=encodedInvite(m);
    showMatchPreview(m);
    text('report-output-title','対戦相手の申告リンク') ;
    $('report-panel').scrollIntoView({behavior:'smooth'});
  } catch (_) { showError('招待URLのデータが不正です。'); }
}
async function prepare(event) {
  event.preventDefault(); $('report-error').classList.add('hidden'); $('report-output').classList.add('hidden');
  const own=$('self-repo').value.trim(), other=$('other-repo').value.trim(), game=$('game-id').value.trim(), played=$('played-at').value;
  if (!validRepo(own)||!validRepo(other)||own.toLowerCase()===other.toLowerCase()||!gamePattern.test(game)) return showError('別々の正しいリポジトリ名とゲームIDを指定してください。');
  const btn=$('report-form').querySelector('button');btn.disabled=true;btn.textContent='双方のRPを取得中...';
  try {
    const [mine,theirs]=await Promise.all([loadManifest(own),loadManifest(other)]);
    if (!mine.games[game]||!theirs.games[game]) throw new Error('両者が参加しているゲームIDを指定してください。');
    const repos=[own,other].sort((a,b)=>a.toLowerCase()<b.toLowerCase()?-1:1);
    const winner=$('winner').value==='self'?own:other;
    const match={protocol:PROTOCOL,id:crypto.randomUUID(),game,repos,winner,before:{[own]:mine.games[game].rp,[other]:theirs.games[game].rp},played_at:played};
    $('own-issue').href=makeIssue(match,own);$('invite-url').value=encodedInvite(match);showMatchPreview(match);
    $('report-output').classList.remove('hidden');
    $('report-output').scrollIntoView({behavior:'smooth',block:'nearest'});
  } catch(e) { showError(e.message); }
  finally {btn.disabled=false;btn.textContent='試合IDと申告リンクを作成';}
}
async function init() {
  $('played-at').value=safeDate();
  try {
    const response=await fetch('manifest.json',{cache:'no-store'}); if(!response.ok) throw new Error('manifest.json が見つかりません');
    manifest=await response.json();
    text('display-name', manifest.display_name||'プレイヤー');
    text('owner-line',manifest.repository||'GitHubリポジトリ未設定');
    text('total-matches',manifest.confirmed_count||0);
    if(manifest.repository){$('self-repo').value=manifest.repository;$('github-link').href=`https://github.com/${manifest.repository}`;}
    renderGames(manifest.games);
    if(manifest.repository && manifest.games) $('game-id').value=Object.keys(manifest.games)[0]||'';
  } catch(e) {const box=$('notice');box.classList.remove('hidden');box.textContent=e.message;}
  await renderHistory();acceptInvite();
}
$('report-form').addEventListener('submit',prepare);
$('copy-invite').addEventListener('click',async()=>{try{await navigator.clipboard.writeText($('invite-url').value);text('copy-invite','コピーしました');}catch(_){$('invite-url').select();text('copy-invite','URLを選択しました');}});
init();
