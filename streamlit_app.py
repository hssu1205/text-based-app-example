import streamlit as st
import openai

# Set up OpenAI API key from Streamlit secrets
openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

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

# Streamlit UI
st.title("✍️ 텍스트 첨삭 앱")
st.write("텍스트를 입력하거나 파일을 업로드하면 문장 단위로 첨삭해드립니다.")

# API 키 확인
if not openai.api_key or openai.api_key == "your-api-key-here":
    st.error("⚠️ OpenAI API 키가 설정되지 않았습니다. .streamlit/secrets.toml 파일에 OPENAI_API_KEY를 설정해주세요.")
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
        st.warning("처리할 문장이 없습니다.")
    else:
        st.info(f"총 {len(sentences)}개의 문장을 찾았습니다.")
        
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
