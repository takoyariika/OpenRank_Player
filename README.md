# OpenRank Player | 個人戦績テンプレート

GitHubアカウントごとに、対戦履歴・Eloレーティング（RP）・勝率を自分のリポジトリへ保存し、GitHub Pagesで公開します。**このリポジトリの管理者は運営者でも参加プレイヤーでもありません。** テンプレートから作ったリポジトリが各自のデータ保存先になります。

## 最初に行うこと（コピー後）

このリポジトリの **Use this template → Create a new repository** から、各自のGitHubアカウントに **Public** なリポジトリを作ってください。`.github/workflows` を含むファイル一式が複製されます。**GitHubのWebアップロードで `.github` を手動追加する必要はありません。**

1. 自分のリポジトリの **Settings → General → Features → Issues** を有効にする。
2. **Settings → Actions → General → Workflow permissions → Read and write permissions** を選んで **Save**。Actionsが停止していれば有効化する。
3. **Settings → Pages → Build and deployment** で **Deploy from a branch → main → /(root) → Save** を選ぶ。
4. 自分のリポジトリのトップ右側の **About（歯車） → Topics** に `openrank-player` を設定する（検索・ポータル自動発見用）。
5. `profile.json` の `display_name` と `games` を編集する。**対戦する2人のゲームIDは完全一致が必要**。
6. **Actions → OpenRank - sync matches → Run workflow** から、ブランチ `main` を選んで実行する。
7. 成功した実行結果の **Summary（概要）** に「OpenRank: あなたの戦績ページ 🌐」とURLが表示される。URLをコードブロック右のコピーアイコンからコピーする。

個人ページの上部にも「自分の戦績ページのURL → URLをコピー」ボタンがあります。URLは通常 `https://ユーザー名.github.io/リポジトリ名/` ですが、**初回Actionsで表示されるURLは候補であり、Pagesの公開が完了したことを意味しません**。

### Pagesが404になる場合

自分のリポジトリで **Settings → Pages** を開いて、公開元が **Deploy from a branch / main / (root)** であることを確認してください。GitHubに **Your site is live at ...** と表示されたら **Visit site** から開けます。公開に数分かかることがあります。トップに `index.html` があることも確認してください。カスタムドメインを設定している場合はPages設定のURLを優先します。

**`Run workflow` が表示されない場合** は、`.github/workflows/sync.yml` がリポジトリの一番上にあるか、Actionsが有効か、デフォルトブランチが `main` かを確認してください。

## 試合結果を記録する手順

1. Aが**自分の公開Pages**の「試合結果を報告する」に、自分とBのリポジトリ（`owner/repo`）、共通ゲームID、日付、勝者を入力する。
2. Aが「試合IDと申告リンクを作成」→「自分のIssueを作成」を押し、GitHubで **Submit new issue** する。Issueは**A本人のアカウント**で投稿する。
3. Aが「招待URLをコピー」を押してBへ送る。
4. BはURLを開き、勝者・ゲーム・RPを確認して「自分のIssueを作成」→ **Submit new issue** する。Issueは**B本人のアカウント**で投稿する。
5. 両方のIssuesが一致すればActionsで記録される。まだ更新されていなければ、両者が **Actions → OpenRank - sync matches → Run workflow** を再実行する。

確認ファイル：`manifest.json`（現在RP・勝率）、`data/matches.json`（確定履歴）、`data/pending.json`（保留理由）。

**注意：** 1ゲームで未確定の試合を複数同時に提出しないでください。RPが変わった場合、以前のRPを参照した試合は `stale-rating` になり、現在の試作版では新規試合IDでの再申告が必要です。GitHub Issuesは公開されるため本名や秘密情報を入力しないでください。このRPは自己申告・相互照合に基づく参考値です。

## 配布元の設定（メンテナー向け）

このリポジトリを初めて公開する際は、所有者が **Settings → General → Template repository** にチェックを入れてください。**この設定はファイルのPushだけでは自動的に有効になりません。** 参加者には **Fork** より **Use this template** を案内してください。

ソースコードの共通開発作業フォルダは `GPT/ranked/` です。配布用の `OpenRank_Player` はその `player/` の中身を独立させたものです。
