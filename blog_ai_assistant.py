import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 환경 설정 ---
st.set_page_config(page_title="헤이츄 전용 비서", layout="wide")

# [핵심] 분량 엄격 제한 가이드라인
HYEJU_STYLE = """
당신은 블로거 '헤이츄'입니다. 아래 규칙을 '칼같이' 지키세요.

1. 오프닝: "안녕하세요! [주제]한 헤이츄입니다. ✨"
2. 말투: 친근한 구어체 (~하더라고요, ~네요). 
3. 사진 분석: 사진 속 특징(색감, 메뉴, 분위기)을 묘사하되, 핵심 위주로 굵고 짧게 적으세요.
4. **분량 엄격 제한**: 공백 포함 '최대 1,700자'를 절대 넘기지 마세요. 
   - 설명이 너무 길어지면 과감하게 생략하고 다음 문단으로 넘어가세요.
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
    # AI에게 '요약해서 핵심만' 적으라고 한 번 더 강조
    prompt = f"""
    {HYEJU_STYLE}
    
    [작성 가이드]
    - 사진들을 분석하되 한 문단이 너무 길어지지 않게 주의하세요.
    - 전체 글자 수가 1,700자 내외가 되도록 요약해서 생동감 있게 적어주세요.
    - 메모 내용: {context}
    """
    res = model.generate_content([prompt] + images)
    
    # 텍스트 정제 (별표 제거)
    text = res.text.replace("**", "").replace("__", "")
    
    # 혹시나 AI가 너무 길게 썼을 경우, 마지막 인사 직전에서 자르는 처리는 하지 않고 
    # AI가 스스로 조절하도록 프롬프트를 강화했습니다.
    return text

# --- 화면 구성 ---
st.title("✨ 헤이츄 전용 AI 블로그 비서")

with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("연결 성공! 🚀")

files = st.file_uploader("📸 사진 업로드", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
memo = st.text_area("📝 메모 입력",
