import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import plotly.express as px  # 그래프를 위한 도구

# 파일 설정
FILENAME = "my_reading_log.json"

def load_data():
    if not os.path.exists(FILENAME): return []
    try:
        with open(FILENAME, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except: return []

def save_data(book_list):
    with open(FILENAME, 'w', encoding='utf-8') as f:
        json.dump(book_list, f, ensure_ascii=False, indent=4)

# 앱 레이아웃 설정
st.set_page_config(page_title="나만의 서재 v2.0", layout="wide")
st.title("📚 나만의 독서 기록장 v2.0")

# 데이터 불러오기
book_list = load_data()

# --- 사이드바: 입력창 ---
with st.sidebar:
    st.header("➕ 새 책 등록")
    date_in = st.date_input("날짜", datetime.now())
    title_in = st.text_input("제목")
    author_in = st.text_input("작가")
    genre_in = st.selectbox("장르", ["소설", "자기계발", "경제/경영", "인문/사회", "과학", "기타"])
    pages_in = st.number_input("페이지", min_value=0, step=1)
    rating_in = st.slider("별점", 1, 5, 5)
    review_in = st.text_area("한 줄 감상평", placeholder="이 책은 나에게 어떤 의미였나요?")
    
    if st.button("기록 저장"):
        if title_in:
            book_list.append({
                "날짜": str(date_in),
                "제목": title_in,
                "작가": author_in,
                "장르": genre_in,
                "페이지": pages_in,
                "별점": rating_in,
                "감상평": review_in
            })
            save_data(book_list)
            st.success(f"'{title_in}' 저장 완료!")
            st.rerun()

# --- 메인 화면: 통계 및 그래프 ---
if book_list:
    df = pd.DataFrame(book_list)
    
    # 1. 상단 요약 바
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 권수", f"{len(df)}권")
    col2.metric("누적 페이지", f"{df['페이지'].sum()}p")
    col3.metric("평균 별점", f"{df['별점'].mean():.1f}점")
    col4.metric("최고 별점", f"{df['별점'].max()}점")
    
    st.divider()

    # 2. 그래프 영역
    st.subheader("📊 독서 데이터 분석")
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        # 장르별 분포 (원형 그래프)
        fig_pie = px.pie(df, names='장르', title='나의 독서 장르 분포', hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with g_col2:
        # 월별 독서량 (막대 그래프)
        df['월'] = df['날짜'].apply(lambda x: x[:7]) # YYYY-MM 추출
        monthly_count = df.groupby('월').size().reset_index(name='권수')
        fig_bar = px.bar(monthly_count, x='월', y='권수', title='월별 독서 흐름', color_discrete_sequence=['#FF4B4B'])
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # 3. 목록 및 감상평
    st.subheader("📖 나의 독서 서재")
    display_df = df.copy()
    display_df['별점'] = display_df['별점'].apply(lambda x: "⭐" * int(x))
    
    # 표로 보여주기
    st.dataframe(display_df[['날짜', '제목', '작가', '장르', '별점', '감상평']].sort_values(by='날짜', ascending=False), use_container_width=True)

    # 삭제 기능 (하단 배치)
    with st.expander("🗑️ 기록 삭제하기"):
        del_title = st.selectbox("삭제할 책을 선택하세요", df['제목'].tolist())
        if st.button("선택한 기록 삭제"):
            new_list = [b for b in book_list if b['제목'] != del_title]
            save_data(new_list)
            st.warning(f"'{del_title}' 기록이 삭제되었습니다.")
            st.rerun()
else:
    st.info("아직 등록된 책이 없습니다. 왼쪽 사이드바에서 첫 번째 기록을 남겨보세요!")
