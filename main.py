# app.py (간단 골격)
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io, json, base64
from datetime import datetime

st.set_page_config(page_title="꿈꾸는 공원 만들기", layout="wide")

# 사이드바: 프로젝트 기본
st.sidebar.title("프로젝트")
title = st.sidebar.text_input("프로젝트 이름", "내 공원")
author = st.sidebar.text_input("닉네임", "dlwldms00")
if "objects" not in st.session_state:
    st.session_state.objects = []

# 툴(색상, 브러시)
st.sidebar.markdown("## 요소 추가")
element_type = st.sidebar.selectbox("추가할 요소", ["나무(도형)", "벤치(사각)", "텍스트"])
color = st.sidebar.color_picker("색상", "#228B22")
size = st.sidebar.slider("크기", 10, 200, 60)

# 캔버스: 기본 드로잉(유저는 캔버스에 직접 그리거나 요소 추가)
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=2,
    background_color="#eef2f3",
    height=600,
    width=900,
    drawing_mode="rectangle", # 또는 "polygon","freedraw"
    key="canvas",
)

# 간단한 '요소 추가' 버튼: 요소 리스트에 저장 (좌표 자동은 미구현, 예시용)
if st.sidebar.button("요소 추가"):
    st.session_state.objects.append({
        "id": len(st.session_state.objects)+1,
        "type": element_type,
        "color": color,
        "size": size,
        "x": 100, "y": 100, "rotation": 0, "layer": len(st.session_state.objects)
    })

# 오른쪽: 객체 리스트와 내보내기
st.sidebar.markdown("## 저장/내보내기")
if st.sidebar.button("프로젝트 JSON 다운로드"):
    proj = {"title": title, "author": author, "created": str(datetime.now()), "objects": st.session_state.objects}
    st.sidebar.download_button("다운로드(JSON)", data=json.dumps(proj, ensure_ascii=False).encode("utf-8"), file_name=f"{title}.json", mime="application/json")

# 메인: 작업 영역과 객체 목록
col1, col2 = st.columns([3,1])
with col1:
    st.header(title)
    st.write("캔버스(작업 영역)")
    st.image(canvas_result.image_data) if canvas_result.image_data is not None else st.write("캔버스에 그려보세요!")
with col2:
    st.write("요소 목록")
    for obj in st.session_state.objects:
        st.write(obj)
