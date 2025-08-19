import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import os

# ---------------------------
# 데이터 불러오기 함수
# ---------------------------
@st.cache_data
def load_data():
    file_path = "전국문화축제표준데이터.csv"

    if not os.path.exists(file_path):
        st.error("❌ CSV 파일을 찾을 수 없습니다. GitHub 저장소에 파일을 올려주세요.")
        return pd.DataFrame()

    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8")

    # 날짜 컬럼 datetime 변환
    df["축제시작일자"] = pd.to_datetime(df["축제시작일자"], errors="coerce")
    df["축제종료일자"] = pd.to_datetime(df["축제종료일자"], errors="coerce")

    # 2025년 데이터만 사용
    df = df[df["축제시작일자"].dt.year == 2025].dropna(
        subset=["축제시작일자", "축제종료일자"]
    )
    return df


# ---------------------------
# 앱 시작
# ---------------------------
st.set_page_config(page_title="2025 전국 축제 캘린더", layout="wide")
st.title("🎉 2025 전국 축제 캘린더")

df = load_data()

if df.empty:
    st.stop()  # CSV가 없으면 앱 중지

# 월 선택
month = st.selectbox("월 선택", range(1, 13), index=datetime.now().month - 1)

# 선택한 월의 축제 필터링
festivals = df[df["축제시작일자"].dt.month == month]

# 캘린더 생성
cal = calendar.Calendar()
days = cal.itermonthdates(2025, month)

st.subheader(f"📅 2025년 {month}월 축제 일정")

# 달력을 테이블 형식으로 출력
calendar_table = """
<table border='1' style='border-collapse: collapse; text-align:center; width:100%;'>
<tr style='background-color:#f0f0f0;'>{}</tr>
""".format("".join([f"<th>{day}</th>" for day in ["월", "화", "수", "목", "금", "토", "일"]]))

week = []
for day in days:
    if day.month == month:
        # 시작일자 또는 기간 중 해당 날짜가 포함되는 축제 표시
        day_fests = festivals[
            (festivals["축제시작일자"].dt.date <= day) &
            (festivals["축제종료일자"].dt.date >= day)
        ]
        if not day_fests.empty:
            fest_list = "<br>".join(day_fests["축제명"].tolist())
            week.append(f"<td style='background-color:#e6f7ff;'><b>{day.day}</b><br>{fest_list}</td>")
        else:
            week.append(f"<td>{day.day}</td>")
    else:
        week.append("<td style='background-color:#f9f9f9;'></td>")

    if len(week) == 7:
        calendar_table += "<tr>" + "".join(week) + "</tr>"
        week = []

calendar_table += "</table>"

st.markdown(calendar_table, unsafe_allow_html=True)

# 축제 상세 정보 선택
if not festivals.empty:
    selected_festival = st.selectbox(
        "축제 선택 (상세정보 보기)",
        ["-- 선택 --"] + festivals["축제명"].tolist()
    )
    if selected_festival != "-- 선택 --":
        fest = festivals[festivals["축제명"] == selected_festival].iloc[0]
        st.write(f"📍 장소: {fest['개최장소']}")
        st.write(f"🗓️ 기간: {fest['축제시작일자'].date()} ~ {fest['축제종료일자'].date()}")
        st.write(f"ℹ️ 내용: {fest['축제내용'] if pd.notna(fest['축제내용']) else '내용 없음'}")
        if pd.notna(fest['홈페이지주소']):
            st.markdown(f"🔗 [홈페이지 바로가기]({fest['홈페이지주소']})")
