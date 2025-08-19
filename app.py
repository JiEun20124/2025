import streamlit as st
import pandas as pd
import calendar
from datetime import datetime

# -------------------------
# 🎯 데이터 불러오기
# -------------------------
def load_data():
    try:
        df = pd.read_csv("전라남북도_축제_최대300개.csv", encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv("전라남북도_축제_최대300개.csv", encoding="utf-8-sig")

    # 날짜 변환
    df["축제시작일자"] = pd.to_datetime(df["축제시작일자"], errors="coerce")
    df["축제종료일자"] = pd.to_datetime(df["축제종료일자"], errors="coerce")

    # 2025년 데이터만
    df = df[df["축제시작일자"].dt.year == 2025]
    return df

df = load_data()

# -------------------------
# 🎨 계절별 배경 이미지 설정
# -------------------------
def get_background_image(month):
    if month in [12, 1, 2]:
        return "https://images.unsplash.com/photo-1608889175123-7b2c1f6a5c51"  # 겨울
    elif month in [3, 4, 5]:
        return "https://images.unsplash.com/photo-1529070538774-1843cb3265df"  # 봄
    elif month in [6, 7, 8]:
        return "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"  # 여름
    else:
        return "https://images.unsplash.com/photo-1501973801540-537f08ccae7b"  # 가을

month = st.sidebar.selectbox("월 선택", range(1, 13), index=datetime.now().month - 1)

bg_url = get_background_image(month)
page_bg = f"""
<style>
.stApp {{
  background: url("{bg_url}") no-repeat center center fixed;
  background-size: cover;
}}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# -------------------------
# 🎉 앱 제목
# -------------------------
st.title("🎉 2025 전라남북도 축제 캘린더")

# 선택한 월 데이터 필터링
festivals = df[df["축제시작일자"].dt.month == month]

# -------------------------
# 📅 캘린더 UI
# -------------------------
cal = calendar.Calendar()
days = cal.itermonthdates(2025, month)

st.subheader(f"📅 2025년 {month}월 축제 일정")

calendar_table = """
<table border='1' style='border-collapse: collapse; text-align:center; table-layout: fixed; width:100%;'>
<tr>{}</tr>
""".format("".join([f"<th>{day}</th>" for day in ["월", "화", "수", "목", "금", "토", "일"]]))

week = []
for day in days:
    if day.month == month:
        day_fests = festivals[festivals["축제시작일자"].dt.day == day.day]
        if not day_fests.empty:
            fest_list = "<br>".join(day_fests["축제명"].tolist())
            week.append(f"<td><b>{day.day}</b><br>{fest_list}</td>")
        else:
            week.append(f"<td>{day.day}</td>")
    else:
        week.append("<td></td>")

    if len(week) == 7:
        calendar_table += "<tr>" + "".join(week) + "</tr>"
        week = []

calendar_table += "</table>"
st.markdown(calendar_table, unsafe_allow_html=True)

# -------------------------
# ⭐ 즐겨찾기 기능
# -------------------------
if "favorites" not in st.session_state:
    st.session_state.favorites = []

if not festivals.empty:
    selected_festival = st.selectbox("축제 선택 (상세정보 보기)", ["-- 선택 --"] + festivals["축제명"].tolist())
    if selected_festival != "-- 선택 --":
        fest = festivals[festivals["축제명"] == selected_festival].iloc[0]
        st.write(f"📍 장소: {fest['개최장소']}")
        st.write(f"🗓️ 기간: {fest['축제시작일자'].date()} ~ {fest['축제종료일자'].date()}")
        st.write(f"ℹ️ 내용: {fest['축제내용'] if pd.notna(fest['축제내용']) else '내용 없음'}")
        if pd.notna(fest['홈페이지주소']):
            st.markdown(f"🔗 [홈페이지 바로가기]({fest['홈페이지주소']})")

        # 즐겨찾기 버튼
        if st.button("⭐ 즐겨찾기 추가"):
            if selected_festival not in st.session_state.favorites:
                st.session_state.favorites.append(selected_festival)
                st.success(f"'{selected_festival}'이(가) 즐겨찾기에 추가되었습니다!")

# 즐겨찾기 목록 표시
if st.session_state.favorites:
    st.subheader("⭐ 나의 즐겨찾기 축제")
    for fav in st.session_state.favorites:
        st.write(f"- {fav}")
