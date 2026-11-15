#!/usr/bin/env python3
"""Publish a first-run GitHub Pages URL and setup hints to the Actions run summary.

Used after OpenRank's match-sync has committed manifest.json. Only the standard
library is needed, so it also runs in a fresh GitHub Actions Python environment.
"""
from __future__ import annotations

import json
import os
from pathlib import Path


def canonical_url(repo: str) -> str:
    owner, name = repo.split('/', 1)
    if name.lower() == f'{owner.lower()}.github.io':
        return f'https://{name.lower()}/'
    return f'https://{owner.lower()}.github.io/{name}/'


def build_summary(repo: str, url: str) -> str:
    settings = f'https://github.com/{repo}/settings/pages'
    return f'''## OpenRank: あなたの戦績ページ 🌐

**ページのURLはこちらです。** コード欄のコピーボタンでコピーできます。

```text
{url}
```

[戦績ページを開く]({url}) · [GitHub Pages の設定を開く]({settings})

> **注意:** 初回の Actions が成功しても、GitHub Pages が未公開なら上記URLはまだ開けません。
> `Settings → Pages → Build and deployment` で **Deploy from a branch**、**main**、**/(root)** を選び、**Save** してください。

### 公開の確認

1. 上の **GitHub Pages の設定を開く** をクリックします。
2. `Your site is live at ...` が出ていれば、そのURLの **Visit site** から開けます。
3. 表示されない場合はPagesの公開設定と `index.html` のルート配置を確認してください。公開には少し時間がかかります。
4. 個人ページ内にも **URLをコピー** ボタンが表示されます。

※ このURLはリポジトリ名から求めた標準のGitHub Pages URLです。カスタムドメインを使っている場合は Settings → Pages に表示されるURLを優先してください。
'''


def main() -> None:
    repo = os.environ['GITHUB_REPOSITORY']
    manifest_path = Path('manifest.json')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
    url = manifest.get('page_url') or canonical_url(repo)
    summary = build_summary(repo, url)
    out = os.environ.get('GITHUB_STEP_SUMMARY')
    if out:
        with open(out, 'a', encoding='utf-8') as f:
            f.write(summary)
    print(f'OpenRank Pages URL: {url}')
    print(f'Pages settings: https://github.com/{repo}/settings/pages')
    print(f'::notice title=OpenRank Pages URL::{url} (Pagesの公開設定が必要です)')
    if not out:
        print(summary)


if __name__ == '__main__':
    main()
