import streamlit as st
import pandas as pd
import random
import html
from pathlib import Path

# ページ設定
st.set_page_config(
    page_title="医学試験対策クイズ",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# パス設定
SCRIPT_DIR = Path(__file__).parent.resolve()
QUESTION_SETS_DIR = SCRIPT_DIR / "question_sets"
IMAGES_DIR = SCRIPT_DIR / "images"

# サポートする画像拡張子
SUPPORTED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

# カスタムCSS
st.markdown("""
<style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    
    .stButton > button {
        width: 100%;
        min-height: 80px;
        height: auto;
        font-size: 16px;
        font-weight: bold;
        margin: 8px 0;
        padding: 15px;
        border-radius: 12px;
        border: 2px solid #4CAF50;
        transition: all 0.3s;
        white-space: normal;
        word-wrap: break-word;
        text-align: left;
        line-height: 1.4;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
    }
    
    @media (max-width: 768px) {
        .stButton > button {
            font-size: 14px;
            min-height: 70px;
            padding: 12px;
        }
    }
    
    .correct-answer {
        background-color: #4CAF50;
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
    }
    
    .incorrect-answer {
        background-color: #f44336;
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
    }
    
    .pitfall-box {
        background-color: #fff3cd;
        color: #856404;
        border-left: 4px solid #ffc107;
        padding: 15px;
        margin: 15px 0;
        border-radius: 8px;
        line-height: 1.6;
    }
    
    [data-theme="dark"] .pitfall-box {
        background-color: #3d3d1a;
        color: #ffd54f;
        border-left: 4px solid #ffc107;
    }
    
    .progress-container {
        background-color: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        margin: 20px 0;
    }
    
    [data-theme="dark"] .progress-container {
        background-color: #424242;
    }
    
    .progress-bar {
        background-color: #4CAF50;
        height: 30px;
        border-radius: 10px;
        transition: width 0.3s;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
    }
    
    .question-set-card {
        background-color: #f8f9fa;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .question-set-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.2);
    }
    
    [data-theme="dark"] .question-set-card {
        background-color: #2d2d2d;
        border-color: #424242;
    }
    
    h1 {
        text-align: center;
        color: #2196F3;
        margin-bottom: 30px;
    }
    
    @media (max-width: 768px) {
        .correct-answer, .incorrect-answer {
            font-size: 18px;
            padding: 15px;
        }
    }
</style>
""", unsafe_allow_html=True)


def escape_html(text: str) -> str:
    """XSS対策のためのHTMLエスケープ"""
    return html.escape(str(text))


@st.cache_data
def build_image_index(images_dir: Path) -> dict[str, Path]:
    """画像フォルダをスキャンし、問題ID→画像パスのマッピングを作成"""
    image_map = {}
    if not images_dir.exists():
        return image_map
    
    for file_path in images_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
            question_id = file_path.stem.lower()
            image_map[question_id] = file_path
    
    return image_map


def get_question_image(question_id: str, image_map: dict[str, Path]) -> Path | None:
    """問題IDに対応する画像パスを取得"""
    normalized_id = question_id.lower()
    return image_map.get(normalized_id)


def display_question_image(question_id: str, image_map: dict[str, Path]):
    """問題に対応する画像があれば表示"""
    image_path = get_question_image(question_id, image_map)
    if image_path and image_path.exists():
        st.image(str(image_path), caption="📷 問題画像", use_container_width=True)


@st.cache_data
def get_available_question_sets() -> list[dict]:
    """利用可能な問題セットの一覧を取得"""
    question_sets = []
    
    if not QUESTION_SETS_DIR.exists():
        return question_sets
    
    for csv_file in QUESTION_SETS_DIR.glob("*.csv"):
        try:
            # ファイルを1回だけ開いて行数をカウント
            with open(csv_file, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f) - 1  # ヘッダーを除く
            
            if line_count > 0:  # 空ファイルを除外
                question_sets.append({
                    'name': csv_file.stem,
                    'path': csv_file,
                    'count': line_count,
                    'description': get_set_description(csv_file.stem)
                })
        except Exception:
            continue
    
    return sorted(question_sets, key=lambda x: x['name'])


def get_set_description(set_name: str) -> str:
    """問題セット名から説明文を生成"""
    descriptions = {
        '医学基礎問題_30問': '医学基礎問題（循環器・呼吸器・消化器など）',
        '総合予想問題_403問': '総合予想問題（物理・化学・生理学・統計など）',
    }
    return descriptions.get(set_name, '問題セット')


def init_session_state():
    """セッション状態の初期化"""
    defaults = {
        'selected_set': None,
        'all_questions': None,
        'questions': None,
        'current_question_idx': 0,
        'answered_questions': [],
        'correct_count': 0,
        'current_answer': None,
        'quiz_started': False,
        'selected_count': None,
        'uploaded_file_id': None,
        'pending_questions': None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


def validate_questions(csv_file) -> tuple[list | None, list[str]]:
    """CSVファイルを検証し、問題リストとエラーリストを返す"""
    errors = []
    valid_questions = []
    
    try:
        df = pd.read_csv(csv_file)
        required_columns = ['問題ID', '問題文', '選択肢A', '選択肢B', '選択肢C', 
                          '選択肢D', '選択肢E', '正解', '解説', '間違えやすいポイント']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"必要な列が不足: {', '.join(missing_columns)}")
            return None, errors
        
        if len(df) == 0:
            errors.append("CSVファイルに問題データが含まれていません")
            return None, errors
        
        for idx, row in df.iterrows():
            row_num = idx + 2
            
            if pd.isna(row['問題文']) or str(row['問題文']).strip() == '':
                errors.append(f"行{row_num}: 問題文が空です")
                continue
            
            has_all_choices = True
            for opt in ['A', 'B', 'C', 'D', 'E']:
                if pd.isna(row[f'選択肢{opt}']) or str(row[f'選択肢{opt}']).strip() == '':
                    errors.append(f"行{row_num}: 選択肢{opt}が空です")
                    has_all_choices = False
            
            if not has_all_choices:
                continue
            
            correct_answer = str(row['正解']).strip().upper()
            if correct_answer not in ['A', 'B', 'C', 'D', 'E']:
                errors.append(f"行{row_num}: 正解が不正（'{row['正解']}'）")
                continue
            
            if pd.isna(row['解説']) or str(row['解説']).strip() == '':
                errors.append(f"行{row_num}: 解説が空です")
                continue
            
            if pd.isna(row['間違えやすいポイント']) or str(row['間違えやすいポイント']).strip() == '':
                errors.append(f"行{row_num}: 間違えやすいポイントが空です")
                continue
            
            valid_questions.append({
                '問題ID': str(row['問題ID']).strip(),
                '問題文': str(row['問題文']).strip(),
                '選択肢A': str(row['選択肢A']).strip(),
                '選択肢B': str(row['選択肢B']).strip(),
                '選択肢C': str(row['選択肢C']).strip(),
                '選択肢D': str(row['選択肢D']).strip(),
                '選択肢E': str(row['選択肢E']).strip(),
                '正解': correct_answer,
                '解説': str(row['解説']).strip(),
                '間違えやすいポイント': str(row['間違えやすいポイント']).strip()
            })
        
        if len(valid_questions) == 0:
            errors.append("有効な問題データが1件もありません")
            return None, errors
        
        return valid_questions, errors
        
    except Exception as e:
        return None, [f"ファイル読み込み失敗: {str(e)}"]


def load_question_set(set_path: Path) -> list | None:
    """問題セットを読み込む"""
    try:
        with open(set_path, 'r', encoding='utf-8') as f:
            questions, _ = validate_questions(f)
            return questions
    except Exception:
        return None


def reset_and_load_questions(questions: list):
    """問題をリセットして新しい問題セットをロード"""
    st.session_state.all_questions = questions
    st.session_state.questions = None
    st.session_state.current_question_idx = 0
    st.session_state.answered_questions = []
    st.session_state.correct_count = 0
    st.session_state.current_answer = None
    st.session_state.pending_questions = None
    st.session_state.quiz_started = False
    st.session_state.selected_count = None


def start_quiz(num_questions: int):
    """指定された問題数でクイズを開始"""
    all_q = st.session_state.all_questions
    if all_q is None:
        return
    
    # ランダムに問題を選択（効率化: random.sampleを使用）
    actual_count = min(num_questions, len(all_q))
    selected_questions = random.sample(all_q, actual_count)
    
    st.session_state.questions = selected_questions
    st.session_state.current_question_idx = 0
    st.session_state.answered_questions = []
    st.session_state.correct_count = 0
    st.session_state.current_answer = None
    st.session_state.quiz_started = True
    st.session_state.selected_count = actual_count


def next_question():
    """次の問題へ進む"""
    st.session_state.current_answer = None
    st.session_state.current_question_idx += 1


def record_answer(selected_option: str, correct_answer: str):
    """回答を記録"""
    is_correct = (selected_option == correct_answer)
    st.session_state.answered_questions.append({
        'question_idx': st.session_state.current_question_idx,
        'selected': selected_option,
        'correct': correct_answer,
        'is_correct': is_correct
    })
    if is_correct:
        st.session_state.correct_count += 1
    st.session_state.current_answer = selected_option


def make_answer_callback(option: str, correct: str):
    """クロージャでコールバック関数を生成"""
    def callback():
        record_answer(option, correct)
    return callback


# ===== メインアプリ =====
st.title("🏥 医学試験対策クイズ")

# 画像インデックスを構築
image_map = build_image_index(IMAGES_DIR)

# 問題セット選択画面
if st.session_state.selected_set is None and st.session_state.all_questions is None:
    st.markdown("### 📚 問題セットを選択してください")
    
    # 利用可能な問題セットを取得
    available_sets = get_available_question_sets()
    
    if not available_sets:
        st.error("⚠️ 問題セットが見つかりません。`question_sets`フォルダにCSVファイルを配置してください。")
    else:
        for question_set in available_sets:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"#### 📋 {question_set['name']}")
                st.markdown(f"*{question_set['description']}*")
                st.markdown(f"**問題数: {question_set['count']}問**")
            
            with col2:
                if st.button("選択", key=f"select_{question_set['name']}", use_container_width=True):
                    questions = load_question_set(question_set['path'])
                    if questions:
                        st.session_state.selected_set = question_set['name']
                        reset_and_load_questions(questions)
                        st.rerun()
                    else:
                        st.error("問題セットの読み込みに失敗しました")
            
            st.markdown("---")
    
    # カスタムアップロード機能
    st.markdown("### 📤 または、独自の問題をアップロード")
    uploaded_file = st.file_uploader(
        "CSVファイルを選択",
        type=['csv'],
        help="独自の問題データが含まれるCSVファイルをアップロード"
    )
    
    if uploaded_file is not None:
        current_file_id = uploaded_file.file_id
        
        if st.session_state.uploaded_file_id != current_file_id:
            st.session_state.uploaded_file_id = current_file_id
            questions, errors = validate_questions(uploaded_file)
            
            if errors:
                st.warning(f"⚠️ エラーが見つかりました（{len(errors)}件）:")
                for error in errors[:10]:
                    st.warning(f"• {error}")
                if len(errors) > 10:
                    st.warning(f"...他{len(errors) - 10}件")
            
            if questions:
                st.session_state.pending_questions = questions
                st.success(f"✅ {len(questions)}問の問題を検証しました")
            else:
                st.session_state.pending_questions = None
        
        if st.session_state.pending_questions:
            if st.button("📝 この問題セットを使用", use_container_width=True, type="primary"):
                st.session_state.selected_set = "カスタム問題"
                reset_and_load_questions(st.session_state.pending_questions)
                st.success("✅ カスタム問題を読み込みました")
                st.rerun()

# サイドバー
with st.sidebar:
    st.header("📚 設定")
    
    # 現在の問題セット表示
    if st.session_state.selected_set:
        st.success(f"📋 {st.session_state.selected_set}")
    
    # 画像フォルダの状態表示
    if image_map:
        st.info(f"🖼️ 画像: {len(image_map)}件検出")
    
    st.markdown("---")
    
    # 問題セット選択に戻るボタン
    if st.session_state.all_questions is not None:
        if st.button("🔄 問題セットを変更", use_container_width=True, type="secondary"):
            st.session_state.selected_set = None
            st.session_state.all_questions = None
            st.session_state.questions = None
            st.session_state.quiz_started = False
            st.rerun()
        st.markdown("---")
    
    # 現在の状態表示
    if st.session_state.all_questions is not None:
        st.markdown("### 📊 現在の状態")
        total_available = len(st.session_state.all_questions)
        st.info(f"読込済み問題数: {total_available}問")
        
        if st.session_state.quiz_started and st.session_state.questions:
            st.info(f"出題数: {len(st.session_state.questions)}問")
            if len(st.session_state.answered_questions) > 0:
                accuracy = (st.session_state.correct_count / len(st.session_state.answered_questions) * 100)
                st.info(f"解答済み: {len(st.session_state.answered_questions)}問\n正答率: {accuracy:.1f}%")
    
    # キャッシュクリア機能（デバッグ用）
    st.markdown("---")
    if st.button("🗑️ キャッシュをクリア", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# メインコンテンツ
if st.session_state.all_questions is None:
    # 問題セット選択画面（上記で表示済み）
    pass

elif not st.session_state.quiz_started:
    # 出題数選択画面
    total_questions = len(st.session_state.all_questions)
    
    st.markdown("### 📝 クイズ設定")
    st.success(f"📚 読み込み済み: **{total_questions}問**")
    
    if image_map:
        questions_with_images = sum(
            1 for q in st.session_state.all_questions 
            if get_question_image(q['問題ID'], image_map)
        )
        st.info(f"🖼️ 画像付き問題: {questions_with_images}問")
    
    st.markdown("---")
    st.markdown("#### 出題数を選択してください")
    
    # プリセットボタン
    col1, col2, col3, col4 = st.columns(4)
    preset_counts = [5, 10, 20, total_questions]
    preset_labels = ["5問", "10問", "20問", f"全問（{total_questions}問）"]
    
    for col, count, label in zip([col1, col2, col3, col4], preset_counts, preset_labels):
        with col:
            if count <= total_questions:
                if st.button(label, use_container_width=True, key=f"preset_{count}"):
                    start_quiz(count)
                    st.rerun()
            else:
                st.button(label, use_container_width=True, disabled=True, key=f"preset_{count}")
    
    st.markdown("---")
    st.markdown("#### またはカスタム数を入力")
    custom_count = st.number_input(
        "出題数",
        min_value=1,
        max_value=total_questions,
        value=min(10, total_questions),
        step=1,
        help=f"1〜{total_questions}の範囲で指定できます"
    )
    
    if st.button("🚀 クイズを開始", use_container_width=True, type="primary"):
        start_quiz(custom_count)
        st.rerun()

else:
    # クイズ進行中
    if st.session_state.current_question_idx >= len(st.session_state.questions):
        # 全問題終了
        st.success("🎉 すべての問題が終了しました！")
        
        total = len(st.session_state.answered_questions)
        correct = st.session_state.correct_count
        accuracy = (correct / total * 100) if total > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("総問題数", f"{total}問")
        with col2:
            st.metric("正解数", f"{correct}問")
        with col3:
            st.metric("正答率", f"{accuracy:.1f}%")
        
        if accuracy >= 90:
            st.balloons()
            st.success("🌟 素晴らしい成績です！完璧な理解度です！")
        elif accuracy >= 70:
            st.success("👍 良い成績です！この調子で続けましょう！")
        elif accuracy >= 50:
            st.info("📚 まずまずの成績です。復習を重ねて理解を深めましょう。")
        else:
            st.warning("💪 もう一度復習して、再挑戦してみましょう！")
        
        if st.button("🔄 もう一度挑戦する", use_container_width=True, type="primary"):
            st.session_state.quiz_started = False
            st.session_state.questions = None
            st.session_state.current_question_idx = 0
            st.session_state.answered_questions = []
            st.session_state.correct_count = 0
            st.session_state.current_answer = None
            st.rerun()
    
    else:
        # 問題表示
        total_questions = len(st.session_state.questions)
        current_num = st.session_state.current_question_idx + 1
        progress = (current_num / total_questions) * 100
        answered = len(st.session_state.answered_questions)
        accuracy = (st.session_state.correct_count / answered * 100) if answered > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### 📊 進捗: {current_num} / {total_questions}問")
        with col2:
            if answered > 0:
                st.markdown(f"### ✅ 正答率: {accuracy:.1f}%")
            else:
                st.markdown("### ✅ 正答率: ---%")
        
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress}%;">
                {progress:.0f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 現在の問題を取得
        question = st.session_state.questions[st.session_state.current_question_idx]
        
        # 問題文表示
        st.markdown(f"### 問題 {current_num}")
        st.info(question['問題文'])
        
        # 画像があれば表示
        display_question_image(question['問題ID'], image_map)
        
        options = ['A', 'B', 'C', 'D', 'E']
        
        if st.session_state.current_answer is None:
            # 未回答
            for option in options:
                choice_text = question[f'選択肢{option}']
                st.button(
                    f"{option}. {choice_text}",
                    key=f"option_{option}",
                    use_container_width=True,
                    on_click=make_answer_callback(option, question['正解'])
                )
        
        else:
            # 回答済み
            selected = st.session_state.current_answer
            correct = question['正解']
            is_correct = (selected == correct)
            
            if is_correct:
                st.markdown("""
                <div class="correct-answer">
                    ✅ 正解です！
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="incorrect-answer">
                    ❌ 不正解です<br>
                    あなたの回答: {escape_html(selected)}<br>
                    正解: {escape_html(correct)}
                </div>
                """, unsafe_allow_html=True)
            
            for option in options:
                choice_text = question[f'選択肢{option}']
                if option == correct:
                    st.success(f"✅ **{option}. {choice_text}** （正解）")
                elif option == selected:
                    st.error(f"❌ **{option}. {choice_text}** （あなたの回答）")
                else:
                    st.info(f"{option}. {choice_text}")
            
            with st.expander("📖 解説を見る", expanded=True):
                st.markdown(question['解説'])
            
            st.markdown(f"""
            <div class="pitfall-box">
                <strong>⚠️ 間違えやすいポイント</strong><br>
                {escape_html(question['間違えやすいポイント'])}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.button(
                "➡️ 次の問題へ",
                use_container_width=True,
                type="primary",
                on_click=next_question
            )
