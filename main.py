import streamlit as st
from gtts import gTTS
from io import BytesIO
import base64
import requests

# ==================== CONFIGURATION ====================
APP_NAME = "Universal Voice Speaker Pro"
DEVELOPER_INFO = {
    "name": "Jahanzaib Javed",
    "company": "ZebyCoder & Co",
    "contact": "+92-300-5590321",
    "email": "zeb.innerartinteriors@gmail.com",
    "specialization": "AI/ML & Python Solutions"
}

# Enhanced language support
LANGUAGES = {
    "English": {"code": "en", "example": "Hello, welcome to our voice speaker!"},
    "Urdu": {"code": "ur", "example": "سلام، ہماری آواز اسپیکر میں خوش آمدید", "rtl": True},
    "Hindi": {"code": "hi", "example": "नमस्ते, हमारे वॉइस स्पीकर में आपका स्वागत है", "rtl": False},
    "Arabic": {"code": "ar", "example": "مرحبًا بكم في مكبر الصوت الخاص بنا!", "rtl": True},
    "Spanish": {"code": "es", "example": "¡Hola, bienvenido a nuestro altavoz de voz!", "rtl": False},
    "French": {"code": "fr", "example": "Bonjour, bienvenue sur notre haut-parleur vocal !", "rtl": False},
    "Chinese": {"code": "zh", "example": "您好，欢迎使用我们的语音扬声器！", "rtl": False},
    "Russian": {"code": "ru", "example": "Здравствуйте, добро пожаловать в наш голосовой динамик!", "rtl": False},
    "German": {"code": "de", "example": "Hallo, willkommen bei unserem Sprachlautsprecher!", "rtl": False},
    "Japanese": {"code": "ja", "example": "こんにちは、私たちの音声スピーカーへようこそ！", "rtl": False}
}

# Enhanced romanized to native mapping
TRANSLITERATION_MAP = {
    'ur': {
        'aap': 'آپ', 'kaise': 'کیسے', 'hain': 'ہیں', 'mein': 'میں', 'theek': 'ٹھیک',
        'shukriya': 'شکریہ', 'salaam': 'سلام', 'pyar': 'پیار', 'khuda': 'خدا',
        'kitna': 'کتنا', 'waqt': 'وقت', 'dost': 'دوست', 'acha': 'اچھا', 'nahi': 'نہیں',
        'hai': 'ہے', 'kyun': 'کیوں', 'kahan': 'کہاں', 'chai': 'چائے', 'pani': 'پانی'
    },
    'hi': {
        'aap': 'आप', 'kaise': 'कैसे', 'ho': 'हो', 'main': 'मैं', 'thik': 'ठीक',
        'dhanyavad': 'धन्यवाद', 'namaste': 'नमस्ते', 'pyaar': 'प्यार', 'bhagwan': 'भगवान',
        'kitna': 'कितना', 'samay': 'समय', 'mitr': 'मित्र', 'achha': 'अच्छा', 'nahi': 'नहीं',
        'hai': 'है', 'kyun': 'क्यों', 'kahan': 'कहाँ', 'chai': 'चाय', 'paani': 'पानी'
    }
}

# ==================== INITIAL SETUP ====================
# Mobile and RTL configuration must come first!
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None
)

# Custom CSS for RTL and mobile
st.markdown("""
<style>
    /* RTL Support */
    .rtl-text {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, sans-serif;
        line-height: 1.8;
        font-size: 1.1rem;
    }

    /* Mobile Optimization */
    @media screen and (max-width: 600px) {
        .sidebar .sidebar-content {
            width: 85px;
            transition: width 0.2s;
        }
        .sidebar:hover .sidebar-content {
            width: 300px;
        }
        .stTextArea textarea {
            min-height: 120px !important;
        }
        button {
            padding: 14px !important;
            margin: 8px 0 !important;
        }
        /* Better mobile header */
        .header h1 {
            font-size: 1.8rem !important;
        }
    }

    /* General UI Improvements */
    .header {
        background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .feature-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
        color: white;
        font-weight: bold;
    }
    .developer-credit {
        font-size: 0.9rem;
        margin-top: -1rem;
        margin-bottom: 1.5rem;
        color: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)


# ==================== CORE FUNCTIONS ====================
def romanized_to_native(text, language):
    """Enhanced romanized text converter with context handling"""
    lang_code = LANGUAGES[language]["code"]
    if lang_code not in ['ur', 'hi']:
        return text

    words = text.lower().split()
    converted_words = []

    for word in words:
        # Handle punctuation and common suffixes
        clean_word = word.strip('.,?!')
        if clean_word in TRANSLITERATION_MAP[lang_code]:
            converted_word = TRANSLITERATION_MAP[lang_code][clean_word]
            # Preserve original punctuation
            if word.endswith(('.', ',', '?', '!')):
                converted_word += word[-1]
            converted_words.append(converted_word)
        else:
            converted_words.append(word)

    return ' '.join(converted_words)


def text_to_speech(text, language, speed=1.0):
    """Enhanced TTS with better Urdu/Hindi handling"""
    lang_code = LANGUAGES[language]["code"]

    # Convert romanized text if needed
    if lang_code in ['ur', 'hi']:
        text = romanized_to_native(text, language)

    try:
        # Use slower speed for better Urdu/Hindi clarity
        slow = True if lang_code in ['ur', 'hi', 'ar'] else False
        tts = gTTS(text=text, lang=lang_code, slow=slow)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return None


# ==================== STREAMLIT UI ====================
def main():
    # Header with developer credit
    st.markdown(f"""
    <div class="header">
        <h1>🌍 {APP_NAME}</h1>
        <p>Advanced Multilingual Text-to-Speech Solution</p>
        <p class="developer-credit">Created and Developed by {DEVELOPER_INFO['name']} • {DEVELOPER_INFO['email']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar with developer info
    with st.sidebar:
        st.markdown(f"""
        ### Developer Information
        **{DEVELOPER_INFO['name']}**  
        Founder @ {DEVELOPER_INFO['company']}  
        📞 {DEVELOPER_INFO['contact']}  
        ✉️ {DEVELOPER_INFO['email']}  
        Specializing in {DEVELOPER_INFO['specialization']}
        """)

        st.markdown("### Quick Phrases")
        if st.button("Hello (English)"):
            st.session_state.text_input = "Hello, how are you today?"
        if st.button("آداب (Urdu)"):
            st.session_state.text_input = "آپ کیسے ہیں؟"
        if st.button("नमस्ते (Hindi)"):
            st.session_state.text_input = "आप कैसे हैं?"

    # Main content
    col1, col2 = st.columns([3, 1])

    with col1:
        # Initialize session state for text input
        if 'text_input' not in st.session_state:
            st.session_state.text_input = ""

        text_input = st.text_area(
            "Enter your text:",
            height=150,
            value=st.session_state.text_input,
            placeholder="Type or paste your text here in any language..."
        )

        # Language selection
        selected_lang = st.selectbox(
            "Select Language:",
            list(LANGUAGES.keys()),
            index=0
        )

        # Action buttons
        col1a, col1b = st.columns(2)
        with col1a:
            if st.button("🔊 Speak Now"):
                if text_input:
                    with st.spinner("Generating speech..."):
                        audio_bytes = text_to_speech(text_input, selected_lang)
                        if audio_bytes:
                            st.audio(audio_bytes, format='audio/mp3')
                            # Show formatted text
                            if LANGUAGES[selected_lang].get('rtl', False):
                                st.markdown(
                                    f"<div class='rtl-text'>{romanized_to_native(text_input, selected_lang)}</div>",
                                    unsafe_allow_html=True)
                            else:
                                st.write(romanized_to_native(text_input, selected_lang))
                else:
                    st.warning("Please enter some text first")

        with col1b:
            if st.button("💾 Download Audio"):
                if text_input:
                    with st.spinner("Preparing download..."):
                        audio_bytes = text_to_speech(text_input, selected_lang)
                        if audio_bytes:
                            st.audio(audio_bytes, format='audio/mp3')
                            b64 = base64.b64encode(audio_bytes.read()).decode()
                            href = f'<a href="data:audio/mp3;base64,{b64}" download="{selected_lang}_speech.mp3">Download Audio File</a>'
                            st.markdown(href, unsafe_allow_html=True)
                else:
                    st.warning("Please enter some text first")

    with col2:
        st.markdown("### Language Examples")
        for lang in ["Urdu", "Hindi", "Arabic", "English"]:
            with st.expander(lang):
                example = LANGUAGES[lang]["example"]
                if LANGUAGES[lang].get('rtl', False):
                    st.markdown(f"<div class='rtl-text'>{example}</div>", unsafe_allow_html=True)
                else:
                    st.write(example)
                if st.button(f"Speak {lang}", key=f"ex_{lang}"):
                    audio_bytes = text_to_speech(example, lang)
                    st.audio(audio_bytes, format='audio/mp3')

    # Features section
    st.markdown("## ✨ Key Features")
    features = [
        {
            "icon": "🌐",
            "title": "10+ Languages",
            "description": "High-quality speech in English, Urdu, Hindi, Arabic, Spanish, French, Chinese, Russian, German, and Japanese"
        },
        {
            "icon": "⌨️",
            "title": "Romanized Input",
            "description": "Type Urdu/Hindi in English letters (like 'aap kaise hain') and get perfect native pronunciation"
        },
        {
            "icon": "📱",
            "title": "Mobile Optimized",
            "description": "Works perfectly on all devices with touch-friendly controls"
        },
        {
            "icon": "🔄",
            "title": "RTL Support",
            "description": "Proper right-to-left display for Urdu and Arabic with correct text alignment"
        }
    ]

    cols = st.columns(len(features))
    for i, feature in enumerate(features):
        with cols[i]:
            st.markdown(f"""
            <div class="feature-card">
                <h3>{feature['icon']} {feature['title']}</h3>
                <p>{feature['description']}</p>
            </div>
            """, unsafe_allow_html=True)

    # Footer
    st.markdown(f"""
    <div style="text-align: center; margin-top: 3rem; color: #666;">
        <p>© 2023 {DEVELOPER_INFO['company']} | All Rights Reserved</p>
        <p>Developed by {DEVELOPER_INFO['name']} | Contact: {DEVELOPER_INFO['contact']}</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()