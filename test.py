import streamlit as st
import pandas as pd
import calendar
from datetime import datetime

st.title("🎉 전라남북도 2025 축제 캘린더")

# -----------------------------
# 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("전라남북도_축제_최대300개.csv", encoding="utf-8-sig")
    df["축제시작일자"] = pd.to_datetime(df["축제시작일자"], errors="coerce")
    df["축제종료일자"] = pd.to_datetime(df["축제종료일자"], errors="coerce")
    return df

df = load_data()

# -----------------------------
# 캘린더 출력
# -----------------------------
st.header("📅 월별 축제 일정")

month = st.selectbox("월 선택", range(1, 13), index=datetime.now().month - 1)

festivals = df[df["축제시작일자"].dt.month == month]

cal = calendar.Calendar()
days = cal.itermonthdates(2025, month)

# CSS 스타일 (중괄호는 {{ }} 로 이스케이프 처리)
calendar_table = """
<style>
.calendar-table {{
    border-collapse: collapse;
    width: 100%;
    table-layout: fixed;
}}
.calendar-table th, .calendar-table td {{
    border: 1px solid #999;
    text-align: center;
    vertical-align: top;
    width: 14.28%;
    height: 100px;
    padding: 5px;
    font-size: 14px;
}}
.calendar-table th {{
    background-color: #f0f0f0;
}}
</style>
<table class='calendar-table'>
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

# -----------------------------
# 상세정보
# -----------------------------
if not festivals.empty:
    selected_festival = st.selectbox("축제 선택 (상세정보 보기)", ["-- 선택 --"] + festivals["축제명"].tolist())
    if selected_festival != "-- 선택 --":
        fest = festivals[festivals["축제명"] == selected_festival].iloc[0]
        st.write(f"📍 장소: {fest['개최장소']}")
        st.write(f"🗓️ 기간: {fest['축제시작일자'].date()} ~ {fest['축제종료일자'].date()}")
        st.write(f"ℹ️ 내용: {fest['축제내용'] if pd.notna(fest['축제내용']) else '내용 없음'}")
        if pd.notna(fest['홈페이지주소']):
            st.markdown(f"🔗 [홈페이지 바로가기]({fest['홈페이지주소']})")
