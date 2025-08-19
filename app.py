import streamlit as st
import pandas as pd
import calendar
from datetime import datetime

# 데이터 불러오기
def load_data():
    df = pd.read_csv("전라남북도_축제_최대300개.csv", encoding="cp949")
    df["축제시작일자"] = pd.to_datetime(df["축제시작일자"], errors="coerce")
    df["축제종료일자"] = pd.to_datetime(df["축제종료일자"], errors="coerce")
    df = df[df["축제시작일자"].dt.year == 2025]
    return df

# 앱 시작
df = load_data()
st.set_page_config(page_title="2025 전국 축제 캘린더", layout="wide")
st.title("🎉 2025 전라남·북도 축제 캘린더")

# 월 선택
month = st.selectbox("월 선택", range(1, 13), index=datetime.now().month - 1)

# ✅ 계절별 배경 이미지 매핑
season_backgrounds = {
    "spring": "https://images.unsplash.com/photo-1523413651479-597eb2da0ad6?auto=format&fit=crop&w=1600&q=80",
    "summer": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1600&q=80",
    "autumn": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1600&q=80",
    "winter": "https://images.unsplash.com/photo-1608889175123-8c6c53d3aaf4?auto=format&fit=crop&w=1600&q=80"
}

def get_season(month):
    if 3 <= month <= 5:
        return "spring"
    elif 6 <= month <= 8:
        return "summer"
    elif 9 <= month <= 11:
        return "autumn"
    else:
        return "winter"

season = get_season(month)
bg_url = season_backgrounds[season]

# ✅ CSS로 배경 적용
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{bg_url}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}
    table {{
        width: 100%;
        table-layout: fixed;
        border-collapse: collapse;
        background-color: rgba(255, 255, 255, 0.8);
    }}
    td, th {{
        width: 14%;
        padding: 10px;
        border: 1px solid #ccc;
        text-align: center;
        vertical-align: top;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# 선택한 월의 축제 필터링
festivals = df[df["축제시작일자"].dt.month == month]

# 캘린더 생성
cal = calendar.Calendar()
days = cal.itermonthdates(2025, month)

st.subheader(f"📅 2025년 {month}월 축제 일정")

calendar_table = """
<table>
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

# 축제 상세 정보 + 즐겨찾기
if not festivals.empty:
    selected_festival = st.selectbox("축제 선택 (상세정보 보기)", ["-- 선택 --"] + festivals["축제명"].tolist())
    if "favorites" not in st.session_state:
        st.session_state["favorites"] = []

    if selected_festival != "-- 선택 --":
        fest = festivals[festivals["축제명"] == selected_festival].iloc[0]
        st.write(f"📍 장소: {fest['개최장소']}")
        st.write(f"🗓️ 기간: {fest['축제시작일자'].date()} ~ {fest['축제종료일자'].date()}")
        st.write(f"ℹ️ 내용: {fest['축제내용'] if pd.notna(fest['축제내용']) else '내용 없음'}")

        if pd.notna(fest['홈페이지주소']):
            st.markdown(f"🔗 [홈페이지 바로가기]({fest['홈페이지주소']})")

        if fest["축제명"] not in st.session_state["favorites"]:
            if st.button("⭐ 즐겨찾기 추가"):
                st.session_state["favorites"].append(fest["축제명"])
        else:
            if st.button("❌ 즐겨찾기 해제"):
                st.session_state["favorites"].remove(fest["축제명"])

    # 즐겨찾기 출력
    st.sidebar.subheader("⭐ 나의 즐겨찾기 축제")
    if st.session_state["favorites"]:
        for f in st.session_state["favorites"]:
            st.sidebar.write(f"- {f}")
    else:
        st.sidebar.write("아직 추가한 축제가 없어요.")
