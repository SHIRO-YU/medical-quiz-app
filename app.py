import streamlit as st
import pandas as pd
import random
import os
import html  # XSS対策用

# ページ設定
st.set_page_config(
    page_title="医学試験対策クイズ",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# デフォルトのCSVファイルパス
DEFAULT_CSV_PATH = "sample_medical_questions.csv"

# カスタムCSS（モバイルファースト、ダークモード対応）
st.markdown("""
<style>
    /* 全体のスタイル */
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    
    /* 選択肢ボタンのスタイル */
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
    
    /* モバイル対応 */
    @media (max-width: 768px) {
        .stButton > button {
            font-size: 14px;
            min-height: 70px;
            padding: 12px;
        }
    }
    
    /* 正解・不正解の表示 */
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
    
    /* 間違えやすいポイントの強調 */
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
    
    /* 進捗バー */
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
    
    /* 問題文のスタイル */
    .question-box {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        border-left: 4px solid #2196F3;
        line-height: 1.8;
    }
    
    [data-theme="dark"] .question-box {
        background-color: #2d2d2d;
        color: #e0e0e0;
    }
    
    .question-box h3 {
        margin-top: 0;
        color: #2196F3;
    }
    
    [data-theme="dark"] .question-box h3 {
        color: #64b5f6;
    }
    
    .question-box p {
        margin-bottom: 0;
        font-size: 16px;
    }
    
    /* タイトル */
    h1 {
        text-align: center;
        color: #2196F3;
        margin-bottom: 30px;
    }
    
    /* エクスパンダーのスタイル改善 */
    .streamlit-expanderHeader {
        font-size: 16px;
        font-weight: bold;
    }
    
    /* モバイルでのパディング調整 */
    @media (max-width: 768px) {
        .question-box {
            padding: 15px;
        }
        
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


# セッション状態の初期化
def init_session_state():
    defaults = {
        'questions': None,
        'current_question_idx': 0,
        'answered_questions': [],
        'correct_count': 0,
        'question_order': [],
        'current_answer': None,
        'is_default_csv': False,
        'default_load_attempted': False,  # 名前を変更: 試行済みフラグ
        'uploaded_file_id': None,  # アップロードファイルの追跡用
        'pending_questions': None,  # 検証済みの問題を一時保存
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# サンプルデータの生成
def generate_sample_csv():
    sample_data = """問題ID,問題文,選択肢A,選択肢B,選択肢C,選択肢D,選択肢E,正解,解説,間違えやすいポイント
Q001,心筋梗塞の初期対応として最も適切なものはどれか。,アスピリン300mg内服,ヘパリン静注,ワルファリン内服,ジピリダモール内服,チクロピジン内服,A,急性心筋梗塞の初期対応では抗血小板薬としてアスピリン300mgの投与が推奨される。血小板凝集を抑制し、血栓の進展を防ぐ。,ヘパリンは抗凝固薬であり初期対応としては推奨されない。ワルファリンは作用発現が遅く急性期には不適切。
Q002,肺血栓塞栓症の診断に最も有用な検査はどれか。,胸部X線,心電図,造影CT,D-ダイマー,動脈血ガス,C,肺血栓塞栓症の確定診断には造影CT（特にCTPA: CT肺動脈造影）が最も有用。肺動脈内の血栓を直接描出できる。,D-ダイマーは除外診断に有用だが、陽性でも特異度が低い。心電図のS1Q3T3パターンは感度が低い。
Q003,慢性心不全患者に禁忌の薬剤はどれか。,ACE阻害薬,β遮断薬,ループ利尿薬,NSAIDs,スピロノラクトン,D,NSAIDsは腎血流量を低下させ、体液貯留を引き起こすため慢性心不全では禁忌。また利尿薬の効果を減弱させる。,β遮断薬は過去には禁忌とされたが、現在は慢性心不全の標準治療。急性増悪時には注意が必要。
Q004,COPD急性増悪時の酸素投与目標SpO2はどれか。,88-92%,93-95%,96-98%,99-100%,85%以下,A,COPD患者では高濃度酸素投与によりCO2ナルコーシスのリスクがあるため、SpO2 88-92%を目標とする。,健常者の目標SpO2（96%以上）を適用すると高CO2血症を招く危険がある。Ⅱ型呼吸不全の理解が重要。
Q005,気管支喘息の長期管理において第一選択となる薬剤はどれか。,吸入ステロイド,長時間作用性β2刺激薬,ロイコトリエン受容体拮抗薬,テオフィリン,短時間作用性β2刺激薬,A,気管支喘息の長期管理では気道炎症を抑制する吸入ステロイド（ICS）が第一選択。コントロール不良時にLABAを追加する。,短時間作用性β2刺激薬は発作時の頓用であり長期管理薬ではない。LABAは単独使用せず必ずICSと併用する。"""
    return sample_data


# CSVファイルの読み込みと検証（UIメッセージなし版）
def validate_questions(csv_file) -> tuple[list | None, list[str]]:
    """
    CSVファイルを検証し、問題リストとエラーリストを返す。
    UIへの出力は行わない。
    """
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
            row_errors = []
            
            if pd.isna(row['問題文']) or str(row['問題文']).strip() == '':
                row_errors.append(f"行{row_num}: 問題文が空です")
                continue
            
            has_all_choices = True
            for opt in ['A', 'B', 'C', 'D', 'E']:
                if pd.isna(row[f'選択肢{opt}']) or str(row[f'選択肢{opt}']).strip() == '':
                    row_errors.append(f"行{row_num}: 選択肢{opt}が空です")
                    has_all_choices = False
            
            if not has_all_choices:
                errors.extend(row_errors)
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
                '問題ID': str(row['問題ID']),
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
        
    except pd.errors.EmptyDataError:
        return None, ["CSVファイルが空です"]
    except pd.errors.ParserError as e:
        return None, [f"CSVファイルの解析に失敗: {str(e)}"]
    except Exception as e:
        return None, [f"ファイル読み込み失敗: {str(e)}"]


def load_default_csv() -> list | None:
    """デフォルトCSVファイルを読み込む（UIメッセージなし）"""
    if not os.path.exists(DEFAULT_CSV_PATH):
        return None
    
    try:
        with open(DEFAULT_CSV_PATH, 'r', encoding='utf-8') as f:
            questions, _ = validate_questions(f)
            return questions
    except Exception:
        return None


def reset_and_load_questions(questions: list, is_default: bool = False):
    """問題をリセットして新しい問題セットをロード"""
    st.session_state.questions = questions
    st.session_state.question_order = list(range(len(questions)))
    random.shuffle(st.session_state.question_order)
    st.session_state.current_question_idx = 0
    st.session_state.answered_questions = []
    st.session_state.correct_count = 0
    st.session_state.current_answer = None
    st.session_state.is_default_csv = is_default
    st.session_state.pending_questions = None  # クリア


def next_question():
    """次の問題へ進む"""
    st.session_state.current_answer = None
    st.session_state.current_question_idx += 1


def record_answer(selected_option: str, correct_answer: str):
    """回答を記録"""
    is_correct = (selected_option == correct_answer)
    st.session_state.answered_questions.append({
        'question_idx': st.session_state.question_order[st.session_state.current_question_idx],
        'selected': selected_option,
        'correct': correct_answer,
        'is_correct': is_correct
    })
    if is_correct:
        st.session_state.correct_count += 1
    st.session_state.current_answer = selected_option


# ===== メインアプリ =====
st.title("🏥 医学試験対策クイズ")

# 初回起動時にデフォルトCSVを自動読み込み（一度だけ試行）
if not st.session_state.default_load_attempted:
    st.session_state.default_load_attempted = True
    default_questions = load_default_csv()
    if default_questions:
        reset_and_load_questions(default_questions, is_default=True)
        st.rerun()

# サイドバー
with st.sidebar:
    st.header("📚 設定")
    
    # 現在使用中の問題セット表示
    if st.session_state.questions is not None:
        if st.session_state.is_default_csv:
            st.success("📋 デフォルト問題を使用中")
        else:
            st.info("📤 カスタム問題を使用中")
    
    st.markdown("---")
    
    # デフォルト問題に戻るボタン
    if st.session_state.questions is not None and not st.session_state.is_default_csv:
        if st.button("🔄 デフォルト問題に戻る", use_container_width=True, type="secondary"):
            default_questions = load_default_csv()
            if default_questions:
                reset_and_load_questions(default_questions, is_default=True)
                st.success("✅ デフォルト問題に戻りました")
                st.rerun()
            else:
                st.error("❌ デフォルト問題ファイルが見つかりません")
        st.markdown("---")
    
    # サンプルデータのダウンロード
    sample_csv = generate_sample_csv()
    st.download_button(
        label="📥 簡易サンプルCSV（5問）",
        data=sample_csv,
        file_name="simple_sample_quiz.csv",
        mime="text/csv",
        help="動作確認用の簡易サンプルCSVファイル（5問）"
    )
    
    st.markdown("---")
    
    # ファイルアップロード
    st.markdown("### 📤 カスタム問題をアップロード")
    uploaded_file = st.file_uploader(
        "CSVファイルを選択",
        type=['csv'],
        help="独自の問題データが含まれるCSVファイルをアップロード"
    )
    
    # アップロードファイルの処理（変更時のみ検証）
    if uploaded_file is not None:
        current_file_id = uploaded_file.file_id
        
        # 新しいファイルがアップロードされた場合のみ検証
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
        
        # 検証済みの問題がある場合、使用ボタンを表示
        if st.session_state.pending_questions:
            if st.button("📝 この問題セットを使用", use_container_width=True, type="primary"):
                reset_and_load_questions(st.session_state.pending_questions, is_default=False)
                st.success("✅ カスタム問題を読み込みました")
                st.rerun()
    else:
        # ファイルがクリアされた場合
        st.session_state.uploaded_file_id = None
        st.session_state.pending_questions = None
    
    # 現在の状態表示
    if st.session_state.questions is not None:
        st.markdown("---")
        st.markdown("### 📊 現在の状態")
        st.info(f"総問題数: {len(st.session_state.questions)}問")
        if len(st.session_state.answered_questions) > 0:
            accuracy = (st.session_state.correct_count / len(st.session_state.answered_questions) * 100)
            st.info(f"解答済み: {len(st.session_state.answered_questions)}問\n正答率: {accuracy:.1f}%")

# メインコンテンツ
if st.session_state.questions is None:
    st.info("⚠️ デフォルト問題ファイル（sample_medical_questions.csv）が見つかりません")
    st.markdown("### 📤 問題ファイルをアップロードしてください")
    
    st.markdown("### 📋 CSVフォーマット例")
    st.code("""問題ID,問題文,選択肢A,選択肢B,選択肢C,選択肢D,選択肢E,正解,解説,間違えやすいポイント
Q001,心筋梗塞の初期対応として最も適切なものはどれか。,アスピリン300mg内服,ヘパリン静注,...,A,解説文,注意点""", language="csv")
    
    st.markdown("### ✅ 必須項目")
    st.markdown("""
    - **問題ID**: 問題を識別するID（例: Q001）
    - **問題文**: 出題する問題文
    - **選択肢A〜E**: 5つの選択肢すべて必須
    - **正解**: A, B, C, D, Eのいずれか
    - **解説**: 正解の理由や詳細説明
    - **間違えやすいポイント**: 受験生が注意すべき点
    """)
    
else:
    # 全問題終了チェック
    if st.session_state.current_question_idx >= len(st.session_state.questions):
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
            st.session_state.question_order = list(range(len(st.session_state.questions)))
            random.shuffle(st.session_state.question_order)
            st.session_state.current_question_idx = 0
            st.session_state.answered_questions = []
            st.session_state.correct_count = 0
            st.session_state.current_answer = None
            st.rerun()
    
    else:
        # 進捗表示
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
        current_q_idx = st.session_state.question_order[st.session_state.current_question_idx]
        question = st.session_state.questions[current_q_idx]
        
        # 問題文表示（XSSエスケープ適用）
        st.markdown(f"""
        <div class="question-box">
            <h3>問題 {current_num}</h3>
            <p>{escape_html(question['問題文'])}</p>
        </div>
        """, unsafe_allow_html=True)
        
        options = ['A', 'B', 'C', 'D', 'E']
        
        if st.session_state.current_answer is None:
            for option in options:
                choice_text = question[f'選択肢{option}']
                if st.button(f"{option}. {choice_text}", key=f"option_{option}", use_container_width=True):
                    record_answer(option, question['正解'])
                    st.rerun()
        
        else:
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
            
            # 間違えやすいポイント（XSSエスケープ適用）
            st.markdown(f"""
            <div class="pitfall-box">
                <strong>⚠️ 間違えやすいポイント</strong><br>
                {escape_html(question['間違えやすいポイント'])}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            if st.button("➡️ 次の問題へ", use_container_width=True, type="primary"):
                next_question()
                st.rerun()
