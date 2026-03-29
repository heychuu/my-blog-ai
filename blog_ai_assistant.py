import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 환경 설정 ---
st.set_page_config(page_title="헤이츄 전용 비서", layout="wide")

# [보강된] 헤이츄 스타일 가이드
HYEJU_STYLE = """
당신은 블로거 '헤이츄'입니다. 아래 규칙을 '반드시' 지키세요.

1. 사진 분석 우선주의: 
   - 업로드된 모든 사진을 하나하나 아주 꼼꼼하게 묘사하세요. 
   - 사진 속 음식의 질감, 인테리어의 색감, 메뉴판의 글씨, 창밖의 뷰 등을 눈으로 보는 것처럼 상세히 적어야 합니다. 
   - 메모에 없는 내용이라도 사진에 보인다면 무조건 본문에 녹여내세요.

2. 오프닝: "안녕하세요! [주제]한 헤이츄입니다. ✨"
3. 말투: 친근한 구어체 (~하더라고요, ~네요). 
4. 금지: 별표(**)나 기호를 절대 쓰지 마세요. 텍스트만 사용합니다.
5. 분량: 1,700자 내외로 아주 풍성하게 작성하세요.
6. 마무리: "그럼 또 다음 이야기로 돌아오도록 하겠습니다!! 다들 즐거운 하루 보내세요~!"
"""

def get_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        flash = [m for m in models if 'gemini-1.5-flash' in m]
        return flash[0] if flash else models[0]
    except:
        return "models/gemini-1.5-flash"

def generate_post(images, context, model_name):
    model = genai.GenerativeModel(model_name)
    # 사진을 먼저 분석하고 메모를 참고하라는 강력한 지시문
    prompt = f"""
    {HYEJU_STYLE}
    
    [작성 지시]
    1. 먼저 업로드된 사진들을 순서대로 분석하여 각 사진의 특징을 본문에 상세히 적으세요.
    2. 그 다음 아래 [사용자 메모] 내용을 자연스럽게 버무려주세요.
    3. 사진 설명이 빠지면 절대로 안 됩니다! 
    
    [사용자 메모]: {context}
    
    자, 이제 사진을 보고 헤이츄의 말투로 생생한 포스팅을 시작해줘!
    """
    res = model.generate_content([prompt] + images)
    return res.text.replace("**", "").replace("__", "")

# --- 화면 구성 ---
st.title("✨ 헤이츄 전용 AI 블로그 비서")

with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("연결 성공! 🚀")

files = st.file_uploader("📸 사진 업로드", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
memo = st.text_area("📝 메모 입력 (장소, 특징 등)", placeholder="사진에 없는 추가 정보만 적어주셔도 돼요!", height=150)

if st.button("🪄 헤이츄 스타일로 포스팅 생성하기"):
    if not api_key:
        st.error("API 키를 넣어주세요.")
    elif not files:
        st.warning("사진을 올려주세요.")
    else:
        with st.spinner("사진 속 디테일을 하나하나 분석하며 작성 중..."):
            try:
                images = [Image.open(f) for f in files]
                m_name = get_model()
                result = generate_post(images, memo, m_name)
                st.subheader("📝 완성된 헤이츄톤 초안")
                st.text_area("결과 (복사해서 사용)", value=result, height=600)
                st.info(f"글자 수: {len(result)}자")
            except Exception as e:
                st.error(f"오류: {e}")
