# 🚀 セットアップガイド

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

4. **完了！** GitHubにアップロード完了です

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
git commit -m "医学試験対策クイズアプリ（問題セット選択機能付き）"

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

- `app.py` - メインアプリケーション
- `requirements.txt` - 必要なライブラリ
- `README.md` - プロジェクト説明
- `.gitignore` - Git設定
- `SETUP_GUIDE.md` - このファイル
- `question_sets/` - 問題セットフォルダ
  - `医学基礎問題_30問.csv` - 医学基礎問題
  - `総合予想問題_403問.csv` - 総合予想問題
- `images/` - 画像フォルダ（空の場合あり）

---

## 🎯 問題セットの追加方法

1. `question_sets/` フォルダに新しいCSVファイルを追加
2. ファイル名は自由（例: `過去問2024.csv`）
3. アプリを再起動すると自動的に認識されます

### CSVフォーマット

```csv
問題ID,問題文,選択肢A,選択肢B,選択肢C,選択肢D,選択肢E,正解,解説,間違えやすいポイント
Q001,問題文,選択肢A,選択肢B,選択肢C,選択肢D,選択肢E,A,解説文,注意点
```

---

## 🖼️ 画像の追加方法

1. `images/` フォルダを作成（まだない場合）
2. 画像ファイル名を問題IDと同じにする
   - 例: `Q001.png`, `PHY_001.jpg`
3. 対応形式: PNG, JPG, JPEG, GIF, WEBP

---

## ❓ 困ったときは

- GitHub Desktop が「repository not found」と言われる
  → フォルダを正しく選択していますか？

- Streamlit Cloud でエラーが出る
  → requirements.txt が正しくアップロードされていますか？

- アプリが起動しない
  → Python 3.8以上がインストールされていますか？
  → `pip install -r requirements.txt` を実行しましたか？

- 問題セットが表示されない
  → `question_sets/` フォルダにCSVファイルがありますか？
  → CSVの形式は正しいですか？
