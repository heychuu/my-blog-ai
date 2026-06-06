import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io

# --- 환경 설정 ---
st.set_page_config(page_title="헤이츄 전용 비서", layout="wide")

# 헤이츄 스타일 가이드
HYEJU_STYLE = """
당신은 블로거 '헤이츄'입니다. 아래 규칙을 엄격히 지키세요.
1. 오프닝: 자연스럽고 친근하게 인사를 건네며 글을 시작하세요. 절대 "~한 헤이츄입니다"라는 정형화된 문구는 쓰지 마세요.
2. 말투: 친근한 구어체 (~하더라고요, ~네요, ~답니다).
3. 사진 분석: 사진 속 특징을 꼼꼼히 묘사하되 핵심 위주로 자연스럽게 녹여내세요.
4. 분량 제한: 본문 기준 공백 포함 1,500자~1,800자 사이를 유지하세요.
5. 금지: 별표(**)나 기호를 절대 쓰지 마세요. 본문은 부드러운 텍스트만 사용합니다.
6. 마무리: "그럼 또 다음 이야기로 돌아오도록 하겠습니다!! 다들 즐거운 하루 보내세요~!"로 마칩니다.

[중요 추가 요청]
글의 맨 마지막에 본문과 명확히 구분되도록 선을 긋고, 아래 양식으로 블로그 제목 제안과 해시태그를 추가해 주세요.
---
💡 [추천 블로그 제목]
1. (트렌디하고 클릭을 유도하는 제목 1)
2. (제목 2)
3. (제목 3)

🏷️ [추천 해시태그]
#태그1 #태그2 #태그3 ... (5개 이상)
"""

def generate_post(uploaded_files, context, api_key):
    client = genai.Client(api_key=api_key)
    
    prompt = f"{HYEJU_STYLE}\n\n[사용자 메모]: {context}\n\n사진을 분석해서 요구사항에 맞게 작성해줘."
    contents = [prompt]
    
    for f in uploaded_files:
        # 모바일 고용량 사진 자동 압축 처리
        img = Image.open(f)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        img.thumbnail((1280, 1280))
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=80)
        bytes_data = buffer.getvalue()
        
        contents.append(
            types.Part.from_bytes(
                data=bytes_data,
                mime_type="image/jpeg"
            )
        )
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contents
    )
    
    return response.text.replace("**", "").replace("__", "")

# --- 화면 구성 ---
st.title("✨ 헤이츄 전용 AI 블로그 비서 v2.0")

with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("Gemini API Key", type="password")
    if api_key:
        st.success("API 키 입력 완료! 🚀")

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
                result = generate_post(files, memo, api_key)
                st.session_state['generated_result'] = result
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")

# 결과 출력 및 복사 기능
if 'generated_result' in st.session_state:
    result_text = st.session_state['generated_result']
    
    st.subheader("📝 완성된 초안 (제목 & 태그 포함)")
    
    # [수정] 복사 버그 우회를 위해 Streamlit 내장 code 블록 사용
    # 이 상자의 우측 상단에 마우스를 올리거나 터치하면 [📋] 복사 버튼이 자동으로 나타납니다!
    st.code(result_text, language="text", wrap_lines=True)
    st.info(f"글자 수: {len(result_text)}자 (제목/태그 포함)")
