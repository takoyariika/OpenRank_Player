/* OpenRank onboarding: Pages URL display and copy, no OAuth or secrets. */
(() => {
  const field = document.getElementById('pages-url');
  const copy = document.getElementById('copy-pages-url');
  const link = document.getElementById('visit-pages-url');
  const settings = document.getElementById('pages-settings-link');
  const status = document.getElementById('pages-setup-status');
  if (!field || !copy || !link || !settings || !status) return;

  fetch('manifest.json', {cache: 'no-store'}).then(response => {
    if (!response.ok) throw new Error('manifest.json を取得できません');
    return response.json();
  }).then(data => {
    if (!data.repository || !data.page_url) throw new Error('初期化が必要です');
    const [owner, repo] = data.repository.split('/');
    if (!owner || !repo) throw new Error('リポジトリが不正です');
    const url = new URL(data.page_url);
    if (url.protocol !== 'https:') throw new Error('URLが不正です');
    field.value = url.href;
    link.href = url.href;
    link.classList.remove('hidden');
    settings.href = `https://github.com/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/settings/pages`;
    settings.classList.remove('hidden');
    status.textContent = '公開前の場合は「Pagesの設定」を開き、main / (root) を公開元にしてください。';
    copy.disabled = false;
  }).catch(() => {
    status.textContent = '初期化前です。Actions → OpenRank - sync matches → Run workflow を実行してください。';
  });

  copy.addEventListener('click', async () => {
    if (!field.value) return;
    try {
      if (!navigator.clipboard?.writeText) throw new Error('clipboard unavailable');
      await navigator.clipboard.writeText(field.value);
      copy.textContent = 'コピーしました';
      status.textContent = 'URLをコピーしました。未公開の場合は先にPagesを有効化してください。';
    } catch (_) {
      field.focus();
      field.select();
      copy.textContent = 'URLを選択しました';
      status.textContent = '選択したURLを Ctrl+C でコピーしてください。';
    }
  });
})();
