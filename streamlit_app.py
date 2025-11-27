import streamlit as st
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def split_into_sentences(text):
    """텍스트를 문장 단위로 분할"""
    import re
    # 마침표, 느낌표, 물음표 뒤에 공백이나 줄바꿈이 있는 경우 문장으로 분할
    sentences = re.split(r'([.!?]\s+)', text)
    result = []
    for i in range(0, len(sentences)-1, 2):
        if i+1 < len(sentences):
            result.append(sentences[i] + sentences[i+1].strip())
    if len(sentences) % 2 == 1:
        result.append(sentences[-1])
    return [s.strip() for s in result if s.strip()]

def proofread_sentence(sentence):
    """GPT API를 사용하여 문장 첨삭"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 전문 교정자입니다. 주어진 문장을 분석하고 문법, 맞춤법, 표현을 개선해주세요. 원문과 수정된 문장, 그리고 간단한 설명을 제공해주세요."},
                {"role": "user", "content": f"다음 문장을 첨삭해주세요:\n{sentence}"}
            ],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"오류 발생: {str(e)}"

# Streamlit UI 설정 - 밝은 테마
st.set_page_config(
    page_title="텍스트 첨삭 앱",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 밝은 테마 스타일 적용
st.markdown("""
    <style>
    .main {
        background-color: #FFFFFF;
    }
    .stApp {
        background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%);
    }
    h1 {
        color: #2C3E50;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F8F9FA;
        padding: 10px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF;
        border-radius: 8px;
        color: #495057;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4A90E2 !important;
        color: #FFFFFF !important;
    }
    .stButton button {
        background-color: #4A90E2;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(74, 144, 226, 0.2);
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: #357ABD;
        box-shadow: 0 4px 8px rgba(74, 144, 226, 0.3);
    }
    .stTextArea textarea {
        border: 2px solid #E9ECEF;
        border-radius: 8px;
        background-color: #FFFFFF;
        color: #000000 !important;
    }
    .stTextArea label {
        color: #2C3E50 !important;
    }
    textarea {
        color: #000000 !important;
    }
    input {
        color: #000000 !important;
    }
    .stExpander {
        background-color: #FFFFFF !important;
        border: 1px solid #E9ECEF;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .stExpander summary {
        background-color: #F8F9FA !important;
        color: #2C3E50 !important;
        font-weight: 500;
        padding: 12px;
        border-radius: 8px;
    }
    .stExpander p, .stExpander div {
        color: #2C3E50 !important;
    }
    .stExpander [data-testid="stMarkdownContainer"] {
        background-color: #FFFFFF !important;
    }
    .stExpander [data-testid="stMarkdownContainer"] p {
        color: #2C3E50 !important;
    }
    .stMarkdown {
        color: #2C3E50 !important;
    }
    .stMarkdown p, .stMarkdown div {
        color: #2C3E50 !important;
    }
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
        background-color: #FFFFFF !important;
        padding: 15px;
    }
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] * {
        color: #2C3E50 !important;
    }
    div[data-testid="stExpander"] [role="button"] {
        background-color: #F8F9FA !important;
        color: #2C3E50 !important;
    }
    .stProgress > div > div {
        background-color: #4A90E2;
    }
    .element-container {
        color: #2C3E50;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("✍️ 텍스트 첨삭 앱")
st.write("✨ 텍스트를 입력하거나 파일을 업로드하면 문장 단위로 첨삭해드립니다.")

# API 키 확인
if not openai.api_key or openai.api_key == "your-api-key-here":
    st.warning("⚠️ OpenAI API 키가 설정되지 않았습니다. .env 파일에 OPENAI_API_KEY를 설정해주세요.")
    st.stop()

# 탭 생성
tab1, tab2 = st.tabs(["📝 텍스트 입력", "📄 파일 업로드"])

text_to_process = None

with tab1:
    st.subheader("텍스트 직접 입력")
    text_input = st.text_area("첨삭할 텍스트를 입력하세요", height=200, key="text_input")
    if st.button("첨삭하기", key="text_button"):
        if text_input:
            text_to_process = text_input
        else:
            st.warning("텍스트를 입력해주세요.")

with tab2:
    st.subheader("파일 업로드")
    uploaded_file = st.file_uploader("텍스트 파일을 업로드하세요 (.txt)", type=['txt'])
    if uploaded_file is not None:
        text_from_file = uploaded_file.read().decode('utf-8')
        st.text_area("파일 내용 미리보기", text_from_file, height=200, disabled=True)
        if st.button("첨삭하기", key="file_button"):
            text_to_process = text_from_file

# 텍스트 처리
if text_to_process:
    st.divider()
    st.subheader("📋 첨삭 결과")
    
    sentences = split_into_sentences(text_to_process)
    
    if not sentences:
        st.warning("⚠️ 처리할 문장이 없습니다.")
    else:
        st.info(f"📊 총 {len(sentences)}개의 문장을 찾았습니다.")
        
        progress_bar = st.progress(0)
        
        for idx, sentence in enumerate(sentences):
            with st.expander(f"문장 {idx + 1}: {sentence[:50]}{'...' if len(sentence) > 50 else ''}"):
                st.markdown("**원문:**")
                st.write(sentence)
                
                st.markdown("**첨삭 결과:**")
                with st.spinner("첨삭 중..."):
                    result = proofread_sentence(sentence)
                    st.write(result)
            
            progress_bar.progress((idx + 1) / len(sentences))
        
        st.success("✅ 모든 문장 첨삭이 완료되었습니다!")
