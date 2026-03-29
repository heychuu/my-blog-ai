import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 환경 설정 ---
st.set_page_config(page_title="헤이츄 전용 비서", layout="wide")

# [보강] 헤이츄 스타일 가이드 (강조 기호 금지 및 분량 엄격 조절)
HYEJU_STYLE = """
당신은 블로거 '헤이츄'입니다. 아래 규칙을 엄격히 지키세요.
1. 오프닝: "안녕하세요! [주제]한 헤이츄입니다. ✨"
2. 말투: 친근한 구어체 (~하더라고요, ~네요).
3. 사진 분석: 사진 속 특징을 꼼꼼히 묘사하되 핵심 위주로 적으세요.
4. 분량 제한: 공백 포함 1,500자~1,800자 사이를 유지하세요.
5. 금지: 별표(**)나 기호를 절대 쓰지 마세요. 텍스트만 사용합니다.
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
    prompt = f"{HYEJU_STYLE}\n\n[사용자 메모]: {context}\n\n사진을 분석해서 1,700자 내외로 작성해줘."
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
memo = st.text_area("📝 메모 입력", placeholder="추가 정보만 짧게 적어주세요!", height=100)

if st.button("🪄 헤이츄 스타일로 포스팅 생성하기"):
    if not api_key:
        st.error("API 키를 넣어주세요.")
    elif not files:
        st.warning("사진을 올려주세요.")
    else:
        with st.spinner("작성 중..."):
            try:
                images = [Image.open(f) for f in files]
                m_name = get_model()
                result = generate_post(images, memo, m_name)
                st.subheader("📝 완성된 초안")
                st.text_area("결과", value=result, height=550)
                st.info(f"글자 수: {len(result)}자")
            except Exception as e:
                st.error(f"오류: {e}")
