# app.py
import streamlit as st
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random
import json
from datetime import datetime

st.set_page_config(page_title="남자 연예인 16강 이상형 월드컵", layout="wide")

# 기본 참가자(남자 연예인 16명)
DEFAULT_PARTICIPANTS = [
    {"name":"박보검","img":""},
    {"name":"박서준","img":""},
    {"name":"송중기","img":""},
    {"name":"공유","img":""},
    {"name":"현빈","img":""},
    {"name":"정해인","img":""},
    {"name":"김수현","img":""},
    {"name":"류준열","img":""},
    {"name":"이민호","img":""},
    {"name":"이정재","img":""},
    {"name":"서강준","img":""},
    {"name":"유아인","img":""},
    {"name":"소지섭","img":""},
    {"name":"도경수(디오)","img":""},
    {"name":"차은우","img":""},
    {"name":"박형식","img":""},
]

# -- 유틸: 위키백과(한국어)에서 대표 썸네일 URL 가져오기 --
@st.cache_data(show_spinner=False)
def fetch_wiki_thumbnail(name, size=400):
    """
    이름을 받아 ko.wikipedia.org의 pageimages로 썸네일 URL을 조회.
    반환: image_url 혹은 None
    """
    S = requests.Session()
    API_URL = "https://ko.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": name,
        "prop": "pageimages",
        "pithumbsize": size,
        "redirects": 1,
    }
    try:
        r = S.get(API_URL, params=params, timeout=6)
        r.raise_for_status()
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        for pid, page in pages.items():
            thumb = page.get("thumbnail", {})
            if thumb:
                return thumb.get("source")
    except Exception:
        return None
    return None

@st.cache_data(show_spinner=False)
def load_image_from_url(url):
    try:
        resp = requests.get(url, timeout=6)
        resp.raise_for_status()
        return Image.open(BytesIO(resp.content)).convert("RGBA")
    except Exception:
        return None

def make_placeholder(name, size=(420,420), bg=(240,240,240)):
    img = Image.new("RGB", size, color=bg)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 30)
    except:
        font = ImageFont.load_default()
    text = name
    w,h = draw.textsize(text, font=font)
    draw.text(((size[0]-w)/2, (size[1]-h)/2), text, fill=(40,40,40), font=font)
    return img

# -- 참가자 준비: 만약 img 필드가 비어있으면 자동으로 위키썸네일 채움 --
def ensure_images(participants):
    updated = []
    for p in participants:
        if p.get("img"):
            updated.append(p)
            continue
        url = fetch_wiki_thumbnail(p["name"])
        p_new = p.copy()
        p_new["img"] = url or ""
        updated.append(p_new)
    return updated

# -- 토너먼트 관련 함수 --
def prepare_round(participants):
    random.shuffle(participants)
    pairs = []
    for i in range(0, len(participants), 2):
        a = participants[i]
        b = participants[i+1] if i+1 < len(participants) else None
        pairs.append((a,b))
    return pairs

# 세션 상태 초기화
if "participants" not in st.session_state:
    st.session_state.participants = ensure_images(DEFAULT_PARTICIPANTS.copy())
if "current_pairs" not in st.session_state:
    st.session_state.current_pairs = []
if "next_round" not in st.session_state:
    st.session_state.next_round = []
if "pair_index" not in st.session_state:
    st.session_state.pair_index = 0
if "round_num" not in st.session_state:
    st.session_state.round_num = 1
if "history" not in st.session_state:
    st.session_state.history = []

# 사이드바: 참가자 JSON 입력/업로드 및 설정
st.sidebar.header("설정 / 참가자")
st.sidebar.markdown("기본은 인기 남자 연예인 16명입니다. JSON으로 직접 참가자 목록을 넣을 수도 있어요.")
json_in = st.sidebar.text_area("참가자 JSON 입력 (예: [{\"name\":\"이름\",\"img\":\"URL\"}, ...])", height=160)
if st.sidebar.button("JSON으로 불러오기"):
    try:
        parsed = json.loads(json_in)
        if isinstance(parsed, list) and len(parsed) >= 2:
            st.session_state.participants = ensure_images(parsed)
            # 리셋
            st.session_state.current_pairs = []
            st.session_state.next_round = []
            st.session_state.pair_index = 0
            st.session_state.round_num = 1
            st.session_state.history = []
            st.sidebar.success("참가자 목록 적용(이미지 자동 보정 포함)")
        else:
            st.sidebar.error("리스트 형태의 JSON을 넣고, 최소 2명 이상이어야 합니다.")
    except Exception as e:
        st.sidebar.error(f"JSON 파싱 오류: {e}")

if st.sidebar.button("기본 16명으로 초기화"):
    st.session_state.participants = ensure_images(DEFAULT_PARTICIPANTS.copy())
    st.session_state.current_pairs = []
    st.session_state.next_round = []
    st.session_state.pair_index = 0
    st.session_state.round_num = 1
    st.session_state.history = []
    st.sidebar.success("기본 목록으로 초기화됨")

st.sidebar.markdown("참가자 개별 추가")
new_name = st.sidebar.text_input("이름 추가")
new_img = st.sidebar.text_input("이미지 URL (선택)")
if st.sidebar.button("참가자 추가"):
    if new_name:
        p = {"name": new_name, "img": new_img}
        if not new_img:
            p["img"] = fetch_wiki_thumbnail(new_name) or ""
        st.session_state.participants.append(p)
        st.sidebar.success(f"{new_name} 추가됨")
    else:
        st.sidebar.error("이름을 입력하세요.")

# 초기 라운드 준비
if not st.session_state.current_pairs:
    st.session_state.participants = ensure_images(st.session_state.participants)
    # 참가자 수가 2^n이 아니면 가장 가까운 상위 2^n으로 맞출 수 있지만 여기선 16 고정 권장
    if len(st.session_state.participants) not in (8,16,32):
        # 자동으로 16명으로 맞추기 (중복 허용)
        base = st.session_state.participants.copy()
        while len(base) < 16:
            base.extend(st.session_state.participants)
        st.session_state.participants = base[:16]
    st.session_state.current_pairs = prepare_round(st.session_state.participants)
    st.session_state.next_round = []
    st.session_state.pair_index = 0
    st.session_state.round_num = 1
    st.session_state.history = []

# 메인 UI
st.title("남자 연예인 16강 이상형 월드컵 🌟")
st.caption(f"진행자: {st.session_state.get('user','guest')} — 라운드 {st.session_state.round_num} / 참가자 {len(st.session_state.participants)}")

# 현재 매치 표시
if st.session_state.pair_index < len(st.session_state.current_pairs):
    a,b = st.session_state.current_pairs[st.session_state.pair_index]
    col1, col_mid, col2 = st.columns([1,0.15,1])
    with col1:
        if a:
            img_a = load_image_from_url(a["img"]) if a.get("img") else None
            if img_a is None:
                img_a = make_placeholder(a["name"])
            st.image(img_a, use_column_width=True)
            st.markdown(f"**{a['name']}**")
            if st.button(f"선택 → {a['name']}", key=f"chooseA_{st.session_state.pair_index}"):
                st.session_state.next_round.append(a)
                st.session_state.history.append({"round":st.session_state.round_num, "pair_index":st.session_state.pair_index, "winner":a})
                st.session_state.pair_index += 1
                st.experimental_rerun()
    with col2:
        if b:
            img_b = load_image_from_url(b["img"]) if b.get("img") else None
            if img_b is None:
                img_b = make_placeholder(b["name"])
            st.image(img_b, use_column_width=True)
            st.markdown(f"**{b['name']}**")
            if st.button(f"{b['name']} ← 선택", key=f"chooseB_{st.session_state.pair_index}"):
                st.session_state.next_round.append(b)
                st.session_state.history.append({"round":st.session_state.round_num, "pair_index":st.session_state.pair_index, "winner":b})
                st.session_state.pair_index += 1
                st.experimental_rerun()
        else:
            st.info("부전승: 자동으로 다음 라운드로 올라갑니다.")
            st.button("확인 (부전승)", key=f"bye_{st.session_state.pair_index}")
            st.session_state.next_round.append(a)
            st.session_state.history.append({"round":st.session_state.round_num, "pair_index":st.session_state.pair_index, "winner":a})
            st.session_state.pair_index += 1
            st.experimental_rerun()
else:
    # 라운드 종료
    if len(st.session_state.next_round) == 0:
        st.warning("다음 라운드 진출자가 없습니다. 참가자 목록을 확인하세요.")
    elif len(st.session_state.next_round) == 1:
        winner = st.session_state.next_round[0]
        st.success(f"우승자: {winner['name']} 🏆")
        img_w = load_image_from_url(winner.get("img","")) or make_placeholder(winner["name"], size=(600,600))
        st.image(img_w, use_column_width=False)
        result = {
            "title": f"이상형월드컵_{datetime.now().isoformat()}",
            "participants": st.session_state.participants,
            "history": st.session_state.history,
            "winner": winner
        }
        st.download_button("결과 JSON 다운로드", data=json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8"),
                           file_name="match_result.json", mime="application/json")
        if st.button("다시하기 (처음부터)"):
            st.session_state.current_pairs = []
            st.session_state.next_round = []
            st.session_state.pair_index = 0
            st.session_state.round_num = 1
            st.session_state.history = []
            st.experimental_rerun()
    else:
        st.info(f"라운드 {st.session_state.round_num} 종료 — 다음 라운드로 이동합니다.")
        if st.button("다음 라운드 시작"):
            st.session_state.current_pairs = prepare_round(st.session_state.next_round)
            st.session_state.participants = st.session_state.next_round.copy()
            st.session_state.next_round = []
            st.session_state.pair_index = 0
            st.session_state.round_num += 1
            st.experimental_rerun()

# 사이드바: 진행 기록
st.sidebar.header("진행 기록")
st.sidebar.write(f"현재 라운드: {st.session_state.round_num}")
st.sidebar.write("진행된 매치 수:", len(st.session_state.history))
if st.sidebar.button("히스토리 보기"):
    st.sidebar.json(st.session_state.history)

# 하단 도움말 및 저작권 안내
st.markdown("---")
st.markdown("이미지는 한국 위키백과(ko.wikipedia.org)에서 가능한 경우 자동으로 가져옵니다. 위키미디어에 있는 이미지는 각각 다른 라이선스(저작권)가 적용될 수 있으니, 상업적 사용이나 재배포가 필요하면 원 출처의 라이선스를 확인하세요.") 앱을 재시작하세요.")
