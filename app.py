import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

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

# 앱 제목
st.title("📚 나만의 독서 기록장")

# 입력창 (사이드바에 배치하면 깔끔해!)
with st.sidebar:
    st.header("➕ 새 책 등록")
    date_in = st.date_input("날짜", datetime.now())
    title_in = st.text_input("제목")
    author_in = st.text_input("작가")
    genre_in = st.text_input("장르")
    pages_in = st.number_input("페이지", min_value=0, step=1)
    rating_in = st.selectbox("별점", [5, 4, 3, 2, 1], format_func=lambda x: "⭐" * x)
    
    if st.button("기록 저장"):
        if title_in:
            blist = load_data()
            blist.append({
                "날짜": str(date_in),
                "제목": title_in,
                "작가": author_in,
                "장르": genre_in,
                "페이지": pages_in,
                "별점": rating_in
            })
            save_data(blist)
            st.success(f"'{title_in}' 저장 완료!")
            st.rerun()

# 메인 화면: 통계 및 목록
book_list = load_data()
if book_list:
    df = pd.DataFrame(book_list)
    
    # 상단 요약
    col1, col2, col3 = st.columns(3)
    col1.metric("총 권수", f"{len(df)}권")
    col2.metric("누적 페이지", f"{df['페이지'].sum()}p")
    col3.metric("평균 별점", f"{df['별점'].mean():.1f}점")
    
    st.divider()

    # 목록 출력
    st.subheader("📖 나의 독서 목록")
    display_df = df.copy()
    display_df['별점'] = display_df['별점'].apply(lambda x: "⭐" * int(x))
    st.dataframe(display_df.sort_values(by='날짜', ascending=False), use_container_width=True)

    # 삭제 기능
    st.divider()
    st.subheader("🗑️ 기록 삭제")
    del_title = st.text_input("삭제할 책 제목을 입력하세요")
    if st.button("선택 삭제"):
        new_list = [b for b in book_list if b['제목'] != del_title]
        save_data(new_list)
        st.warning(f"'{del_title}' 삭제됨")
        st.rerun()
else:
    st.info("아직 등록된 책이 없습니다. 왼쪽 사이드바에서 첫 번째 책을 등록해 보세요!")
