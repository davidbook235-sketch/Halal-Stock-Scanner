import streamlit as st
from halalterminal import Client

# --- पेज कॉन्फ़िगरेशन ---
st.set_page_config(page_title="Halal Stock Scanner - India", page_icon="🕌")
st.title("🕌 हलाल स्टॉक स्कैनर - भारतीय बाज़ार")
st.markdown("NSE/BSE स्टॉक्स की शरिया अनुपालन स्थिति जांचें।")

# --- API क्लाइंट (Streamlit Secrets से key लें) ---
# Streamlit Cloud पर API key को Secrets में डालें।
# लोकल पर: export HALAL_TERMINAL_API_KEY="ht_..."
try:
    ht = Client()  # यह env var से key उठा लेगा
except Exception:
    st.error("API key सेट नहीं है। कृपया HALAL_TERMINAL_API_KEY environment variable सेट करें।")
    st.stop()

# --- साइडबार ---
st.sidebar.header("सेटिंग्स")
methodology = st.sidebar.selectbox(
    "स्क्रीनिंग मेथडोलॉजी चुनें",
    ["AAOIFI", "DJIM", "FTSE", "MSCI", "S&P"]
)

# --- मुख्य इनपुट ---
ticker_input = st.text_input(
    "स्टॉक सिंबल डालें (कॉमा से अलग करें)",
    "RELIANCE.NS, TCS.NS, HDFCBANK.NS"
)

if st.button("स्कैन करें"):
    symbols = [s.strip().upper() for s in ticker_input.split(",") if s.strip()]
    
    if not symbols:
        st.warning("कृपया कम से कम एक सिंबल डालें।")
    else:
        results = []
        progress_bar = st.progress(0)
        
        for i, symbol in enumerate(symbols):
            try:
                # Halal Terminal API से स्क्रीन करें
                result = ht.screen(symbol)
                
                results.append({
                    "सिंबल": symbol,
                    "स्थिति": "✅ हलाल" if result.is_compliant else "❌ हराम",
                    "कारण": result.compliance_explanation,
                    "व्यवसाय": result.business_screen_status,
                    "वित्तीय": result.financial_screen_status,
                })
            except Exception as e:
                results.append({
                    "सिंबल": symbol,
                    "स्थिति": "⚠️ त्रुटि",
                    "कारण": str(e),
                    "व्यवसाय": "N/A",
                    "वित्तीय": "N/A",
                })
            
            progress_bar.progress((i + 1) / len(symbols))
        
        # --- रिजल्ट टेबल ---
        if results:
            st.subheader("स्कैनिंग परिणाम")
            st.dataframe(results, use_container_width=True)
            
            # हराम स्टॉक्स के लिए अलर्ट
            haram = [r for r in results if "हराम" in r["स्थिति"]]
            if haram:
                st.warning(f"⚠️ {len(haram)} स्टॉक्स हराम पाए गए।")
