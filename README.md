# OpenRank Player | 個人戦績テンプレート

GitHubアカウントごとに、対戦履歴・Eloレーティング（RP）・勝率を自分のリポジトリへ保存し、GitHub Pagesで公開します。**このリポジトリの管理者は運営者でも参加プレイヤーでもありません。** テンプレートから作ったリポジトリが各自のデータ保存先になります。

## 0. 配布元をテンプレートとして有効化する（配布元の管理者が最初に1回だけ）

**重要：先にこの設定が必要です。** 配布元の管理者が [OpenRank_Player](https://github.com/takoyariika/OpenRank_Player) で **Settings → General → Template repository** のチェックをオンにしてください（通常は General のリポジトリ名などの設定付近）。設定されていないと、下記の **Use this template** ボタンが表示されません。

この設定は **配布元の管理者だけ** が行います。一般のプレイヤーは自分のアカウントにコピーするだけでよく、配布元の設定を変更する必要はありません。

## 1. OpenRank Player を自分のGitHubへコピーする（参加者向け）

**ZIPのダウンロードや `.github` の手動アップロードは不要**です。次の順に操作します。

1. GitHubで、自分が戦績を管理するアカウントにログインします。
2. 配布元の **[OpenRank_Player](https://github.com/takoyariika/OpenRank_Player)** を開きます。
3. リポジトリの上部にある **Use this template** をクリックし、**Create a new repository** を選びます。**Fork** や **Code → Download ZIP** ではありません。
4. **Owner** には自分のGitHubアカウントを選びます（配布元の `takoyariika` を選ぶわけではありません）。
5. **Repository name** に `ranked-data` など好きな名前を入力します。**Visibility は Public** を選びます。**Include all branches** が表示されても通常はチェック不要です。
6. **Create repository** を押します。自分のアカウントに、コード一式を持つ新しいリポジトリができます。
7. 新しいリポジトリの **Code** タブで、`index.html`、`profile.json`、`scripts/sync.py` が見えることを確認し、`.github/workflows/sync.yml` も確認してください。

たとえば `alice` が `ranked-data` という名前でコピーすると、作成先は `https://github.com/alice/ranked-data` です。**配布元のフォルダを自分で移動する必要はありません**。ドットで始まる `.github` もまとめてコピーされるため、以前の **This file is hidden.** も発生しません。

**Use this template が見つからない場合：** 配布元リポジトリの管理者が上記「0」の **Template repository** をまだ有効にしていない可能性があります。まず管理者側で設定してください。プレイヤーが自分のリポジトリの Template repository をオンにする必要はありません。

## 2. コピー後の初期設定（自分のリポジトリで行う）

**以下の操作は配布元ではなく、今コピーして作った自分のリポジトリで行います。**

1. 自分のリポジトリの **Settings → General → Features → Issues** を有効にする。
2. **Settings → Actions → General → Workflow permissions → Read and write permissions** を選んで **Save**。Actionsが停止していれば有効化する。
3. **Settings → Pages → Build and deployment** で **Deploy from a branch → main → /(root) → Save** を選ぶ。
4. 自分のリポジトリのトップ右側の **About（歯車） → Topics** に `openrank-player` を設定する（検索・ポータル自動発見用）。
5. `profile.json` の `display_name` と `games` を編集する。**対戦する2人のゲームIDは完全一致が必要**。
6. **Actions → OpenRank - sync matches → Run workflow** から、ブランチ `main` を選んで実行する。
7. 成功した実行結果の **Summary（概要）** に「OpenRank: あなたの戦績ページ 🌐」とURLが表示される。URLをコードブロック右のコピーアイコンからコピーする。

### 初回起動で表示されたPages URLをコピーする

1. **Actions → OpenRank - sync matches** を開き、成功した実行履歴をクリックします。
2. 実行結果の **Summary（概要）** へ戻ります。**「OpenRank: あなたの戦績ページ 🌐」** に公開予定のURLがコードブロックで表示されています。
3. URLの右側にある**コピーアイコン**が使えれば、それを押します。見つからなければURLの文字列を選択して **Ctrl+C** でコピーします。
4. コピーしたURLをブラウザのアドレス欄に貼り付けて開きます（Ctrl+V）。**404が表示されるときは、下のPages設定を確認**してください。

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

配布元リポジトリの管理者は、ページ冒頭の「0. 配布元をテンプレートとして有効化する」を参照してください。**Template repository はファイルのPushだけではオンになりません。** 参加者には **Fork** より **Use this template** を案内してください。

ソースコードの共通開発作業フォルダは `GPT/ranked/` です。配布用の `OpenRank_Player` はその `player/` の中身を独立させたものです。
