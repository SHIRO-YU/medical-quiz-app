# 🚀 GitHubへのアップロード手順

## 📦 このフォルダをダウンロードしたら...

### 方法1: GitHub Desktop を使う（最も簡単！）

1. **GitHub Desktop をインストール**
   - https://desktop.github.com/ からダウンロード
   - インストールしてGitHubアカウントでサインイン

2. **リポジトリを作成**
   - GitHub Desktop で「File」→「Add Local Repository」
   - 「Choose...」をクリックしてこのフォルダを選択
   - 「create a repository」をクリック
   - 「Create Repository」をクリック

3. **GitHubに公開**
   - 左下の「Commit to main」をクリック
   - 上の「Publish repository」をクリック
   - 「Publish repository」を再度クリック

4. **完了！**
   - GitHubにアップロード完了です

---

### 方法2: コマンドライン

```bash
# このフォルダに移動
cd medical-quiz-app

# Gitリポジトリを初期化
git init

# ファイルを追加
git add .

# コミット
git commit -m "医学試験対策クイズアプリを追加"

# GitHubでリポジトリを作成後、以下を実行
git remote add origin https://github.com/あなたのユーザー名/medical-quiz-app.git
git branch -M main
git push -u origin main
```

---

## 🌐 Streamlit Cloudでの公開手順

1. **Streamlit Cloud にアクセス**
   - https://share.streamlit.io/

2. **GitHubでログイン**
   - 「Sign in with GitHub」をクリック

3. **アプリをデプロイ**
   - 「New app」をクリック
   - Repository: `あなたのユーザー名/medical-quiz-app`
   - Branch: `main`
   - Main file path: `app.py`
   - 「Deploy!」をクリック

4. **3〜5分待つ**
   - デプロイ完了すると公開URLが表示されます！

---

## 📝 含まれているファイル

- `app.py` - メインのアプリケーション
- `requirements.txt` - 必要なライブラリ一覧
- `README.md` - プロジェクトの説明
- `.gitignore` - Git管理対象外のファイル設定
- `SETUP_GUIDE.md` - このファイル

---

## ❓ 困ったときは

- GitHub Desktop が「repository not found」と言われる
  → フォルダを正しく選択していますか？

- Streamlit Cloud でエラーが出る
  → requirements.txt が正しくアップロードされていますか？

- アプリが起動しない
  → Python 3.8以上がインストールされていますか？
