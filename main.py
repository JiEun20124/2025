# app.py
import streamlit as st
from datetime import datetime
import json
import io

# PIL은 이미지를 미리보기로 생성할 때 사용
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="꿈꾸는 공원 만들기", layout="wide")

# 닉네임 기본값: dlwldms00 (요청에 따라 자동 채움)
DEFAULT_NICK = "dlwldms00"

# st_canvas import 시도
HAS_CANVAS = False
try:
    from streamlit_drawable_canvas import st_canvas
    HAS_CANVAS = True
except Exception as e:
    # import 실패시 HAS_CANVAS=False로 처리
    st.sidebar.warning("streamlit-drawable-canvas를 찾을 수 없습니다. 설치하면 캔버스 모드 사용 가능해요.")
    st.sidebar.caption("설치: python -m pip install streamlit-drawable-canvas")

# 세션 상태 초기화
if "objects" not in st.session_state:
    st.session_state.objects = []

st.sidebar.title("프로젝트 설정")
title = st.sidebar.text_input("프로젝트 이름", "내 공원")
author = st.sidebar.text_input("닉네임", DEFAULT_NICK)

st.sidebar.markdown("### 요소 추가")
el_type = st.sidebar.selectbox("요소 종류", ["나무", "벤치", "분수", "텍스트"])
color = st.sidebar.color_picker("색상", "#228B22")
size = st.sidebar.slider("크기", 10, 200, 60)
x = st.sidebar.slider("X 좌표 (픽셀)", 0, 900, 100)
y = st.sidebar.slider("Y 좌표 (픽셀)", 0, 600, 100)
rotation = st.sidebar.slider("회전(도)", 0, 360, 0)
text_value = st.sidebar.text_input("텍스트 내용(선택)", "안녕 공원")

if st.sidebar.button("요소 추가"):
    obj = {
        "id": len(st.session_state.objects) + 1,
        "type": el_type,
        "color": color,
        "size": size,
        "x": x,
        "y": y,
        "rotation": rotation,
        "text": text_value
    }
    st.session_state.objects.append(obj)
    st.sidebar.success(f"{el_type} 요소 추가됨!")

st.sidebar.markdown("### 저장 / 내보내기")
proj = {
    "title": title,
    "author": author,
    "created": str(datetime.now()),
    "objects": st.session_state.objects
}
if st.sidebar.button("프로젝트 JSON 다운로드"):
    st.sidebar.download_button("다운로드(JSON)", data=json.dumps(proj, ensure_ascii=False).encode("utf-8"),
                                file_name=f"{title}.json", mime="application/json")

# PNG 생성 함수 (간단 렌더링)
def render_preview(objects, w=900, h=600, bg=(238,242,243)):
    img = Image.new("RGB", (w, h), color=bg)
    draw = ImageDraw.Draw(img)
    # 기본 폰트
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 14)
    except:
        font = ImageFont.load_default()
    for o in objects:
        cx = int(o.get("x", 100))
        cy = int(o.get("y", 100))
        s = int(o.get("size", 60))
        c = o.get("color", "#228B22")
        t = o.get("type", "나무")
        if t == "나무":
            # 원으로 나무 표현
            r = s // 2
            draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=c, outline="black")
        elif t == "벤치":
            # 사각형으로 벤치
            w_rect = s
            h_rect = max(10, s//3)
            draw.rectangle((cx, cy, cx + w_rect, cy + h_rect), fill=c, outline="black")
        elif t == "분수":
            # 작은 원 3개 쌓기
            for i in range(3):
                r = max(6, s//6) + i*4
                draw.ellipse((cx-r, cy-i*8-r, cx+r, cy-i*8+r), fill=c, outline="black")
        elif t == "텍스트":
            txt = o.get("text", "텍스트")
            draw.text((cx, cy), txt, fill=c, font=font)
        else:
            # 기본: 작은 점
            draw.ellipse((cx-3, cy-3, cx+3, cy+3), fill=c)
    return img

# 레이아웃: 캔버스(또는 미리보기) + 요소 목록
col1, col2 = st.columns([3,1])
with col1:
    st.header(title)
    if HAS_CANVAS:
        st.info("캔버스 모드(직접 그리기 가능). 요소는 하단 미리보기와 객체 목록에 반영됩니다.")
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2,
            background_color="#eef2f3",
            height=600,
            width=900,
            drawing_mode="freedraw",
            key="canvas",
        )
        # st_canvas에서 반환된 이미지가 있으면 보여주기
        if canvas_result.image_data is not None:
            st.image(canvas_result.image_data, caption="캔버스에 그린 결과")
        st.markdown("**프로젝트 미리보기**")
        preview_img = render_preview(st.session_state.objects)
        st.image(preview_img, use_column_width=True)
    else:
        st.warning("streamlit-drawable-canvas가 설치되어 있지 않아, 폼 기반 미리보기를 사용합니다.")
        preview_img = render_preview(st.session_state.objects)
        st.image(preview_img, use_column_width=True)

with col2:
    st.subheader("요소 목록")
    if len(st.session_state.objects) == 0:
        st.write("아직 요소가 없습니다. 사이드바에서 추가해봐!")
    else:
        for o in st.session_state.objects:
            st.write(o)
    if st.button("모든 요소 삭제"):
        st.session_state.objects = []
        st.success("요소 목록 초기화됨")

# PNG 다운로드
buf = io.BytesIO()
render_preview(st.session_state.objects).save(buf, format="PNG")
buf.seek(0)
st.download_button("미리보기 PNG 다운로드", data=buf, file_name=f"{title}.png", mime="image/png")

# 끝메시지
st.info("설치 문제 해결 후 st_canvas 기능을 다시 사용하려면 위 설치 명령을 실행하고 앱을 재시작하세요.")
