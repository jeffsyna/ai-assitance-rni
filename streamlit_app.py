import urllib.request
import json
import os
import ssl
import streamlit as st
import time
from urllib.error import HTTPError

def allowSelfSignedHttps(allowed):
    """
    Bypass server certificate verification on client side
    """
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

def get_ai_response(user_input: str, api_key: str, query_type: str) -> str:
    """
    Get AI response from the endpoint with retry logic
    """
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            # Enable SSL bypass
            allowSelfSignedHttps(True)
            
            # Prepare the request
            url = 'https://aisolcopilot7010956395.openai.azure.com/openai/deployments/o1-mini/chat/completions'
            api_version = '2024-08-01-preview'
            
            # Set system message based on query type
            if query_type == "general":
                system_message = "당신은 R&I 부서를 위한 AI 어시스턴트입니다. 연구 및 혁신에 대한 일반적인 질문에 대해 한국어로 명확하고 간단한 답변을 제공해주세요."
            else:  # product
                system_message = """당신은 화장품 제품 기획 및 개발을 위한 전문 AI 어시스턴트입니다. 제품 기획, 시장 분석, 혁신 전략에 대해 한국어로 전문적인 인사이트를 제공해주세요.

화장품 개발을 위해 다음과 같은 성분과 그 함유량을 고려하세요:

각질개선:
- PURASAL SPF 60 (code: 6000285, content: 0.25%)
- PINK PLUM VINEGAR (code: 6026077, content: 0.1%)

미백:
- Niacinamide PC (code: 6000029, content: 2%)
- 트라넥사민산 (code: 6006650, content: 0.5%)
- Whitegen EX (code: 6008784, content: 0.01%)
- 삼백초추출물 (code: 6016434, content: 0.0001%)
- Ascorbic Acid Fine powder (code: 6018508, content: 0.7812%)
- New 닥나무뿌리추출물 (code: 6018603, content: 0.1%)
- COS-VCE-K (code: 6020206, content: 0.01%)
- AgelyticS (code: 6026723, content: 0.005%)
[Additional whitening ingredients omitted for brevity]

수분/보습:
- UREA(NEW) (code: 6006081, content: 1%)
- Ceramide PC-104 (code: 6010270, content: 0.0002%)
- Ceramide PC-102 (code: 6010271, content: 0.0002%)
- Glyacid 70 HP (code: 6010544, content: 0.0001%)
- Red Pine Needle (code: 6025370, content: 0.3%)
- VERI-ENT MOISTURIZING WATER_10 (code: 6026185, content: 0.01%)
- FERULIC ACID (code: 6026240, content: 0.01%)]
[Additional moisturizing ingredients omitted for brevity]

모공/피지/여드름:
- Houttuynia Powder (code: 6023106, content: 0.1%)
- Jade Sphere (code: 6023814, content: 0.01%)
- JM-MUD (code: 6023897, content: 0.1%)
- Volcanic Sphere (code: 6025074, content: 0.01%)
- JEJU VOLCANIC ASH 2 (code: 6025600, content: 0.01%)
- SALICYLIC ACID (code: 6000362, content: 0.4%)
[Additional pore/sebum ingredients omitted for brevity]

주름/탄력:
- L-ARGININE (code: 6005767, content: 0.0012%)
- New EGCG-200 (code: 6026318, content: 1%)
- HumaColl21® 2% Solution (code: 6026333, content: 0.02%)
- Adenosine (code: 6026519, content: 0.02%)
- CAMELLIA F (code: 6026553, content: 0.0001%)
- LactoPDRN (code: 6026575, content: 0.6%)
- SUPER COLLAGEN (code: 6026648, content: 0.0025%)
- AgeRefect (code: 6026649, content: 0.0003%)
- CYLASPHERE RETINOL 10S (code: 6026656, content: 0.0005%)
- CO2LLAGENEER (code: 6026684, content: 0.1%)
- Hi-Aqua™ FL (code: 6026745, content: 0.005%)
- Green Tea Infusion (code: 6026750, content: 0.1%)
- DOUBLE SQUEEZE GREEN TEA WATER (code: 6026848, content: 0.01%)]
[Additional wrinkle/elasticity ingredients omitted for brevity]

진정:
- ORGANIC ALOE VERA EXTRACT D (code: 6019146, content: 1%)
- JEJU GREEN CALMING COMPLEX (code: 6020894, content: 0.1%)
- New AP sprout complex (code: 6024707, content: 0.1%)
- Anasensyl-LS 9322 (code: 6024795, content: 0.01%)
- MATRICARIA LIQUID EXTRACT (code: 6026065, content: 0.02%)]
[Additional soothing ingredients omitted for brevity]

제품 기획안 작성 시 포함할 내용:
1. 제품명
2. 제품 컨셉
3. 타겟 소비자 (연령/성별/라이프스타일)
4. 소비자 페인포인트
5. 경쟁 상황
6. 주요 성분 및 특징 (코드 및 함량)
7. 제품 처방 (성분명, 함량, 기능을 표로 작성)
8. 디자인 컨셉
9. 향후 성장 가능성
10. 개선점
11. 차별화 전략

제품 처방은 다음 가이드를 따르세요:
- 토너/앰플/에센스: 정제수, 보습제, 효능 성분, 점도 조절제
- 로션/에멀젼: 정제수, 보습제, 효능 성분, 유화제, 점도 조절제
- 크림: 정제수, 보습제, 효능 성분, 유화제, 유화 안정제, 점도 조절제

제공된 리스트에서 최소 두 가지 성분을 사용하고, 용도에 따라 함유량을 조절하세요."""

            # Get conversation history from session state
            messages = []
            if 'chat_history' in st.session_state:
                for msg in st.session_state.chat_history[-5:]:  # 최근 5개 메시지만 포함
                    messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Add system message and current user input
            messages = [{"role": "assistant", "content": system_message}] + messages
            messages.append({"role": "user", "content": user_input})
            
            # Prepare request data
            data = {
                "messages": messages,
                "max_completion_tokens": 2000,
                "model": "o1-mini"
            }
            body = str.encode(json.dumps(data))
            
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'api-key': api_key
            }
            
            # Create and send request
            full_url = f"{url}?api-version={api_version}"
            req = urllib.request.Request(full_url, body, headers)
            
            # Get response
            with urllib.request.urlopen(req) as response:
                result = response.read()
                response_data = json.loads(result.decode('utf-8'))
                
                # Debug logging
                print("Response data:", response_data)
                
                if 'choices' not in response_data or not response_data['choices']:
                    return "죄송합니다. 응답을 받지 못했습니다. 다시 시도해주세요."
                
                message = response_data['choices'][0].get('message', {})
                content = message.get('content', '').strip()
                
                if not content:
                    return "죄송합니다. 응답 내용이 비어있습니다. 다시 시도해주세요."
                
                return content
                
        except urllib.error.HTTPError as error:
            if error.code == 500 and attempt < max_retries - 1:
                error_message = f"서버 오류 발생 - {attempt + 1}번째 시도 실패. {retry_delay}초 후 재시도합니다...\n"
                st.warning(error_message)
                time.sleep(retry_delay)
                retry_delay *= 2  # 지수 백오프
                continue
            error_message = f"요청 실패 - 상태 코드: {error.code}\n"
            error_message += f"오류 정보: {error.info()}\n"
            error_message += error.read().decode("utf8", 'ignore')
            return error_message
        except Exception as e:
            if attempt < max_retries - 1:
                error_message = f"오류 발생 - {attempt + 1}번째 시도 실패. {retry_delay}초 후 재시도합니다...\n"
                st.warning(error_message)
                time.sleep(retry_delay)
                retry_delay *= 2  # 지수 백오프
                continue
            return f"오류 발생: {str(e)}"
    
    return "최대 재시도 횟수를 초과했습니다. 잠시 후 다시 시도해주세요."

def main():
    # Page config
    st.set_page_config(page_title="R&I AI assistance", page_icon="🤖", layout="wide")
    
    # Custom CSS for layout
    st.markdown("""
        <style>
        /* Global background fix */
        .st-emotion-cache-1y4p8pa {
            background-color: transparent !important;
        }
        
        .st-emotion-cache-1v0mbdj > div {
            background-color: transparent !important;
        }
        
        /* Main container styling */
        .main-container {
            position: fixed;
            top: 0;
            left: 15rem;
            right: 0;
            bottom: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            background-color: transparent !important;
        }
        
        /* Notice and Tip styling */
        .notice-box {
            background-color: #fff2f0;
            padding: 10px;
            border-radius: 8px;
            margin: 10px auto;
            border: 1px solid #ffccc7;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            width: 600px;
        }
        
        .tip-box {
            background-color: #f0f5ff;
            padding: 10px;
            border-radius: 8px;
            margin: 10px auto;
            border: 1px solid #d6e4ff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            width: 600px;
        }
        
        /* Chat history container */
        .chat-history-container {
            flex-grow: 1;
            overflow-y: auto;
            margin-bottom: 80px;
            padding: 20px;
            background-color: transparent !important;
        }
        
        /* Chat input container */
        .chat-input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 70px;
            padding: 10px;
            background: transparent;
            z-index: 1000;
            width: 600px;
            margin: 0 auto;
        }
        
        /* Chat input styling */
        .stChatInput {
            width: 600px !important;
            margin: 0 auto;
        }
        
        /* Remove default streamlit styles */
        .stChatInput > div {
            background: transparent !important;
            border: none !important;
            width: 600px !important;
        }
        
        /* Style the actual input element */
        .stChatInput input {
            border: 1px solid #e0e0e0 !important;
            border-radius: 8px !important;
            background: white !important;
            padding: 8px 12px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
            width: 600px !important;
        }
        
        /* Remove any additional backgrounds */
        div[data-testid="stChatInput"] {
            background: transparent !important;
            width: 600px !important;
        }
        
        /* Message styling */
        .stChatMessage {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-bottom: 15px;
            padding: 15px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        [data-testid="user-message"] {
            background-color: #e3f2fd !important;
            border-color: #90caf9;
        }
        
        [data-testid="assistant-message"] {
            background-color: #f5f5f5 !important;
            border-color: #e0e0e0;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            width: 15rem;
            padding: 2rem 1rem;
        }
        
        /* Hide unnecessary elements */
        .stDeployButton, footer {
            display: none;
        }
        
        /* Force transparent background on all containers */
        .element-container, .stMarkdown, .stChatMessageContent {
            background-color: transparent !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "general"
    
    # Sidebar for API key and query type selection
    with st.sidebar:
        st.title("설정")
        
        # API Key input
        if 'api_key' not in st.session_state:
            api_key = st.text_input("API Key", type="password")
            if st.button("설정 저장"):
                st.session_state.api_key = api_key
                st.rerun()
        else:
            st.success("API 키가 설정되었습니다.")
            if st.button("API 키 재설정"):
                del st.session_state.api_key
                st.rerun()
        
        st.markdown("---")  # Divider
        
        # Query type selection
        st.subheader("문의 유형 선택")
        selected_tab = st.radio("", ["일반 문의", "제품 기획"], key="query_type", 
                              help="문의 유형을 선택해주세요")
        
        if selected_tab == "일반 문의":
            st.session_state.current_tab = "general"
        else:
            st.session_state.current_tab = "product"
            st.markdown("""
                <div style='background-color: #fff3e0; padding: 10px; border-radius: 5px; border: 1px solid #ffe0b2;'>
                ⚠️ 제품기획안 생성만 가능합니다.
                </div>
                """, unsafe_allow_html=True)
    
    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Notice section
    st.markdown("""
        <div class='notice-box'>
        <h3 style='color: #cf1322; margin-top: 0;'>⚠️ Notice</h3>
        <p style='color: #cf1322; margin-bottom: 0;'>등록된 DB 기반으로 최대한 충실하게 답변드리지만 반드시 정확하지는 않습니다.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tip section
    st.markdown("""
        <div class='tip-box'>
        <h3 style='color: #1890ff; margin-top: 0;'>💡 TIP</h3>
        <p style='color: #1890ff; margin-bottom: 0;'>질의 전 반드시 왼쪽 설정에서 일반 질문인지 제품기획인지 선택해주세요.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat history container
    st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input container
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    if st.session_state.current_tab == "general":
        placeholder = "일반적인 문의사항에 대해 질문해주세요:"
    else:
        placeholder = "제품 기획과 관련된 문의사항에 대해 질문해주세요:"
    user_input = st.chat_input(placeholder)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Handle chat input
    if user_input and 'api_key' in st.session_state:
        try:
            with st.chat_message("user"):
                st.write(user_input)
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            response = get_ai_response(user_input, st.session_state.api_key, st.session_state.current_tab)
            
            with st.chat_message("assistant"):
                st.write(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"오류 발생: {str(e)}")
    elif user_input and 'api_key' not in st.session_state:
        st.warning("API 키를 먼저 설정해주세요.")

if __name__ == "__main__":
    main()
