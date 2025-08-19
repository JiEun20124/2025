import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import os

st.title("🎉 2025 전국 축제 캘린더 & 전남·전북 CSV 생성기")

# -----------------------------
# 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("전국문화축제표준데이터.csv", encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv("전국문화축제표준데이터.csv", encoding="utf-8")

    # 날짜 컬럼 datetime 변환
    df["축제시작일자"] = pd.to_datetime(df["축제시작일자"], errors="coerce")
    df["축제종료일자"] = pd.to_datetime(df["축제종료일자"], errors="coerce")

    # 2025년 데이터만 사용
    df = df[df["축제시작일자"].dt.year == 2025]
    return df

if not os.path.exists("전국문화축제표준데이터.csv"):
    st.error("❌ 원본 CSV 파일이 없습니다. 저장소에 '전국문화축제표준데이터.csv'를 올려주세요.")
    st.stop()

df = load_data()

# -----------------------------
# 캘린더 기능
# -----------------------------
st.header("📅 월별 축제 캘린더")

month = st.selectbox("월 선택", range(1, 13), index=datetime.now().month - 1)

festivals = df[df["축제시작일자"].dt.month == month]

cal = calendar.Calendar()
days = cal.itermonthdates(2025, month)

calendar_table = """
<table border='1' style='border-collapse: collapse; text-align:center; width:100%;'>
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

if not festivals.empty:
    selected_festival = st.selectbox("축제 선택 (상세정보 보기)", ["-- 선택 --"] + festivals["축제명"].tolist())
    if selected_festival != "-- 선택 --":
        fest = festivals[festivals["축제명"] == selected_festival].iloc[0]
        st.write(f"📍 장소: {fest['개최장소']}")
        st.write(f"🗓️ 기간: {fest['축제시작일자'].date()} ~ {fest['축제종료일자'].date()}")
        st.write(f"ℹ️ 내용: {fest['축제내용'] if pd.notna(fest['축제내용']) else '내용 없음'}")
        if pd.notna(fest['홈페이지주소']):
            st.markdown(f"🔗 [홈페이지 바로가기]({fest['홈페이지주소']})")

# -----------------------------
# 전남·전북 CSV 추출 + 다운로드
# -----------------------------
st.header("📥 전남·전북 축제 CSV 추출기")

# 주소 컬럼 보강
for col in ["소재지도로명주소", "소재지지번주소"]:
    if col not in df.columns:
        df[col] = ""

addr = df["소재지도로명주소"].fillna("").astype(str) + " " + df["소재지지번주소"].fillna("").astype(str)

pattern = r"(전라남도|전남|전라북도|전북특별자치도|전북)"
mask = addr.str.contains(pattern, na=False)

filtered = df[mask].copy()
count_before = len(filtered)

if len(filtered) > 300:
    filtered = filtered.sample(300, random_state=42)

st.write(f"전남·전북 필터 결과: 원본 {count_before}개 → 최종 {len(filtered)}개")

csv_bytes = filtered.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
st.download_button(
    label="📥 전남·전북 300개 CSV 다운로드",
    data=csv_bytes,
    file_name="전라남북도_축제_최대300개.csv",
    mime="text/csv",
)
