import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import base64

# アプリの設定
st.set_page_config(page_title="Enhanced English Vocabulary Test システム英単語バージョン", page_icon='sisutannaikonn.png')


# カスタムCSSでUIを改善
st.markdown(
    """
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #9c944f; /* メインテーマカラー */
        color: #9c944f; /* テキストの色 */
    }
    .header, .choices-container button {
        color: #9c944f; /* テキストの色 */
    }
    .choices-container button {
        background-color: #5d79ba;
        color: #9c944f; /* ボタンの文字色 */
        border: 2px solid #9c944f;
        margin: 5px;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        cursor: pointer;
    }
    .choices-container button:hover {
        background-color: #ffffff;
        color: #9c944f; /* ホバー時のボタン文字色 */
    }
    .test-container {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        margin: 20px auto;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .results-table {
        margin: 20px auto;
        border-collapse: collapse;
        width: 100%;
        background-color: #ffffff;
        color: #9c944f; /* テーブルの文字色 */
    }
    .results-table th {
        background-color: #5d79ba;
        color: #9c944f; /* テーブルヘッダーの文字色 */
        padding: 10px;
    }
    .results-table td {
        border: 1px solid #5d79ba;
        padding: 8px;
        text-align: center;
    }
    .stProgress > div > div > div > div {
        background-color: #9c944f; /* プログレスバーの色 */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Excelデータを読み込む関数
@st.cache_data
def load_data():
    data = pd.read_excel("シスタン.xlsx", sheet_name="Sheet1")
    data.columns = ["No.", "単語", "語の意味"]  # カラム名を設定
    return data

words_df = load_data()

# サイドバー設定
st.sidebar.title("テスト設定")
test_type = st.sidebar.radio("テスト形式を選択", ['英語→日本語', '日本語→英語'])
ranges = [f"{i*100+1}-{(i+1)*100}" for i in range(len(words_df) // 100 + 1)]
selected_range = st.sidebar.selectbox("出題範囲を選択", ranges)

# 選択した範囲のデータを抽出
range_start, range_end = map(int, selected_range.split('-'))
filtered_words_df = words_df[(words_df['No.'] >= range_start) & (words_df['No.'] <= range_end)].sort_values(by='No.')

# カスタムCSSで画像の角を丸めるスタイルを追加
st.markdown(
    """
    <style>
    .rounded-image {
        border-radius: 15px;  /* 画像の角を丸くする */
        width: 100%;  /* 画像の幅を調整 */
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# 画像を表示（CSSクラス「rounded-image」を適用）
st.markdown('<img src="test.png" class="rounded-image">', unsafe_allow_html=True)

# テスト開始ボタン
if st.button('テストを開始する'):
    st.session_state.update({
        'test_started': True,
        'correct_answers': 0,
        'current_question': 0,
        'finished': False,
        'wrong_answers': [],
    })

    selected_questions = filtered_words_df.sample(min(50, len(filtered_words_df))).reset_index(drop=True)
    st.session_state.update({
        'selected_questions': selected_questions,
        'total_questions': len(selected_questions),
        'current_question_data': selected_questions.iloc[0],
    })

    # 初回の選択肢を生成
    if test_type == '英語→日本語':
        options = list(selected_questions['語の意味'].sample(3))
        options.append(st.session_state.current_question_data['語の意味'])
    else:
        options = list(selected_questions['単語'].sample(3))
        options.append(st.session_state.current_question_data['単語'])
    
    np.random.shuffle(options)
    st.session_state.options = options
    st.session_state.answer = None

# 質問を進める関数
def update_question(answer):
    if test_type == '英語→日本語':
        correct_answer = st.session_state.current_question_data['語の意味']
        question_word = st.session_state.current_question_data['単語']
    else:
        correct_answer = st.session_state.current_question_data['単語']
        question_word = st.session_state.current_question_data['語の意味']

    if answer == correct_answer:
        st.session_state.correct_answers += 1
    else:
        st.session_state.wrong_answers.append((
            st.session_state.current_question_data['No.'],
            question_word,
            correct_answer
        ))

    st.session_state.current_question += 1
    if st.session_state.current_question < st.session_state.total_questions:
        st.session_state.current_question_data = st.session_state.selected_questions.iloc[st.session_state.current_question]
        if test_type == '英語→日本語':
            options = list(st.session_state.selected_questions['語の意味'].sample(3))
            options.append(st.session_state.current_question_data['語の意味'])
        else:
            options = list(st.session_state.selected_questions['単語'].sample(3))
            options.append(st.session_state.current_question_data['単語'])
        np.random.shuffle(options)
        st.session_state.options = options
        st.session_state.answer = None
    else:
        st.session_state.finished = True

# 結果を表示する関数
def display_results():
    correct_answers = st.session_state.correct_answers
    total_questions = st.session_state.total_questions
    wrong_answers = [wa for wa in st.session_state.wrong_answers if wa[0] in st.session_state.selected_questions['No.'].values]
    accuracy = correct_answers / total_questions

    st.write(f"テスト終了！正解数: {correct_answers}/{total_questions}")
    st.progress(accuracy)
    
    st.write("正解数と不正解数")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("正解数", correct_answers)
    with col2:
        st.metric("不正解数", total_questions - correct_answers)

    st.write(f"正答率: {accuracy:.0%}")
    st.progress(accuracy)
    
    if wrong_answers:
        df_wrong_answers = pd.DataFrame(wrong_answers, columns=["問題番号", "単語", "語の意味"])
        df_wrong_answers = df_wrong_answers.sort_values(by="問題番号")
        st.markdown(df_wrong_answers.to_html(classes='results-table'), unsafe_allow_html=True)
    else:
        st.write("間違えた問題はありません。")

# 問題表示ロジック
if 'test_started' in st.session_state and not st.session_state.finished:
    st.subheader(f"問題 {st.session_state.current_question + 1} / {st.session_state.total_questions} (問題番号: {st.session_state.current_question_data['No.']})")
    st.subheader(f"{st.session_state.current_question_data['単語']}" if test_type == '英語→日本語' else f"{st.session_state.current_question_data['語の意味']}")
    st.markdown('<div class="choices-container">', unsafe_allow_html=True)
    for idx, option in enumerate(st.session_state.options):
        st.button(option, key=f"button_{st.session_state.current_question}_{idx}", on_click=update_question, args=(option,))
    st.markdown('</div>', unsafe_allow_html=True)
else:
    if 'test_started' in st.session_state and st.session_state.finished:
        display_results()
