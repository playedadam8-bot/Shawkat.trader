import base64
import json
from datetime import datetime, timedelta
import pytz
import requests
import streamlit as st
from PIL import Image

# Page Configuration
st.set_page_config(
    page_title="Shawkat Quotex AI Web Scanner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------


def get_pair_flag(asset_name: str) -> str:
    asset_upper = asset_name.upper()
    if "EUR" in asset_upper and "USD" in asset_upper:
        return "🇪🇺🇺🇸"
    if "GBP" in asset_upper and "USD" in asset_upper:
        return "🇬🇧🇺🇸"
    if "USD" in asset_upper and "JPY" in asset_upper:
        return "🇺🇸🇯🇵"
    if "AUD" in asset_upper and "CAD" in asset_upper:
        return "🇦🇺🇨🇦"
    if "EUR" in asset_upper and "GBP" in asset_upper:
        return "🇪🇺🇬🇧"
    if "GBP" in asset_upper and "JPY" in asset_upper:
        return "🇬🇧🇯🇵"
    if "EUR" in asset_upper and "JPY" in asset_upper:
        return "🇪🇺🇯🇵"
    if "CAD" in asset_upper and "JPY" in asset_upper:
        return "🇨🇦🇯🇵"
    if "AUD" in asset_upper and "JPY" in asset_upper:
        return "🇦🇺🇯🇵"
    if "EUR" in asset_upper and "CAD" in asset_upper:
        return "🇪🇺🇨🇦"
    if "AUD" in asset_upper and "CHF" in asset_upper:
        return "🇦🇺🇨🇭"
    if "GBP" in asset_upper and "AUD" in asset_upper:
        return "🇬🇧🇦🇺"
    if "EUR" in asset_upper and "AUD" in asset_upper:
        return "🇪🇺🇦🇺"
    if "CHF" in asset_upper and "JPY" in asset_upper:
        return "🇨🇭🇯🇵"
    if "GBP" in asset_upper and "CAD" in asset_upper:
        return "🇬🇧🇨🇦"
    if "GBP" in asset_upper and "CHF" in asset_upper:
        return "🇬🇧🇨🇭"
    if "USD" in asset_upper and "CHF" in asset_upper:
        return "🇺🇸🇨🇭"
    if "EUR" in asset_upper and "CHF" in asset_upper:
        return "🇪🇺🇨🇭"
    if "OTC" in asset_upper:
        return "🌐"
    return "📊"


def parse_json_response(raw_content: str) -> dict:
    content = raw_content.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    if "{" in content and "}" in content:
        start_idx = content.find("{")
        end_idx = content.rfind("}") + 1
        content = content[start_idx:end_idx]

    return json.loads(content)


def generate_text_signal(api_key: str, asset: str, timer: str, payout: int):
    local_tz = pytz.timezone("Asia/Karachi")
    now_local = datetime.now(local_tz)
    current_local_time = now_local.strftime("%H:%M:%S")
    future_entry = (now_local + timedelta(seconds=25)).strftime("%H:%M:%S")

    prompt = f"""
    You are an elite master binary options algorithmic trader. Current local time: {current_local_time}.
    Generate a high-probability technical trading signal for Quotex asset: {asset} with payout: {payout}%.

    CRITICAL INSTRUCTIONS:
    - Output ONLY valid raw JSON. Do NOT include markdown code blocks. 
    - Provide exact keys: "asset", "live_price", "signal", "accuracy", "reason", "mtg_advice".
    - "signal" must be strictly either "CALL" or "PUT".
    
    Example format:
    {{"asset": "{asset}", "live_price": "1.08520", "signal": "CALL", "accuracy": "95.2%", "reason": "Analyzed technical market structure.", "mtg_advice": "No MTG needed"}}
    """

    # Multi-model fallback chain (DeepSeek -> OpenAI GPT-4o-mini -> Google Gemini Flash -> Anthropic Claude Haiku)
    models = [
        "deepseek/deepseek-chat",
        "openai/gpt-4o-mini",
        "google/gemini-2.5-flash",
        "anthropic/claude-3-haiku",
    ]

    last_error = None
    for model in models:
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://streamlit.app",
                    "X-OpenRouter-Title": "Shawkat Quotex AI Web App",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 250,
                    "temperature": 0.3,
                },
                timeout=20,
            )

            if response.status_code == 200:
                raw_text = response.json()["choices"][0]["message"]["content"]
                data = parse_json_response(raw_text)
                data["execution_time"] = future_entry
                data["model_used"] = model
                return data
            else:
                last_error = f"Model {model} Error {response.status_code}: {response.text}"
        except Exception as e:
            last_error = f"Model {model} Exception: {str(e)}"
            continue

    raise Exception(f"All fallback text models failed. Last error: {last_error}")


def generate_vision_signal(api_key: str, image_bytes: bytes):
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    local_tz = pytz.timezone("Asia/Karachi")
    now_local = datetime.now(local_tz)
    current_local_time = now_local.strftime("%H:%M:%S")
    future_entry = (now_local + timedelta(seconds=20)).strftime("%H:%M:%S")

    prompt = f"""
    You are an elite master binary options algorithmic trader. Current local time: {current_local_time}.
    Deeply analyze this Quotex chart screenshot where the candle timeframe is 1 minute.
    Based on the momentum, trend strength, and candle wicks, determine the optimal expiry duration (e.g., 1 Minute, 2 Minutes, 3 Minutes, 4 Minutes, or 5 Minutes) and the trade direction.

    CRITICAL INSTRUCTIONS:
    - Output ONLY valid raw JSON. Do NOT include markdown code blocks.
    - Provide exact keys: "asset", "live_price", "signal", "expiry", "accuracy", "wick_and_candle_analysis", "mtg_advice", "reason".
    - "signal" must be strictly either "CALL" or "PUT".
    - "expiry" must be specified clearly (e.g., "1 Minute", "2 Minutes", "3 Minutes", "5 Minutes").
    """

    # Multi-model vision fallback chain (Gemini Flash -> OpenAI GPT-4o -> Anthropic Claude 3.5 Sonnet)
    vision_models = [
        "google/gemini-2.5-flash",
        "openai/gpt-4o",
        "anthropic/claude-3.5-sonnet",
    ]

    last_error = None
    for model in vision_models:
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://streamlit.app",
                    "X-OpenRouter-Title": "Shawkat Quotex AI Web App",
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                    "max_tokens": 300,
                    "temperature": 0.3,
                },
                timeout=25,
            )

            if response.status_code == 200:
                raw_text = response.json()["choices"][0]["message"]["content"]
                data = parse_json_response(raw_text)
                data["execution_time"] = future_entry
                data["model_used"] = model
                return data
            else:
                last_error = f"Vision Model {model} Error {response.status_code}: {response.text}"
        except Exception as e:
            last_error = f"Vision Model {model} Exception: {str(e)}"
            continue

    raise Exception(f"All fallback vision models failed. Last error: {last_error}")


# ------------------------------------------------------------------------------
# Session State Initialization
# ------------------------------------------------------------------------------
if "session_active" not in st.session_state:
    st.session_state.session_active = False
if "balance" not in st.session_state:
    st.session_state.balance = 0.0
if "trade_size" not in st.session_state:
    st.session_state.trade_size = 0.0
if "tp" not in st.session_state:
    st.session_state.tp = 0.0
if "sl" not in st.session_state:
    st.session_state.sl = 0.0
if "current_pnl" not in st.session_state:
    st.session_state.current_pnl = 0.0
if "last_signal" not in st.session_state:
    st.session_state.last_signal = None

# ------------------------------------------------------------------------------
# Sidebar Configuration
# ------------------------------------------------------------------------------
st.sidebar.title("⚙️ Control Panel")

# OpenRouter Key Input
api_key = st.sidebar.text_input("OpenRouter API Key", type="password")

st.sidebar.markdown("---")

# Capital Management Session Setup
st.sidebar.subheader("💰 Capital & Risk Setup")
starting_balance_choice = st.sidebar.selectbox(
    "Select Session Capital ($)", [10, 20, 30, 50, 100], index=0
)

if st.sidebar.button("Initialize Capital Session"):
    amount = float(starting_balance_choice)
    st.session_state.balance = amount
    st.session_state.trade_size = amount * 0.1
    st.session_state.tp = amount * 0.4
    st.session_state.sl = amount * 0.2
    st.session_state.current_pnl = 0.0
    st.session_state.session_active = True
    st.sidebar.success(f"Session Initialized with ${amount:.2f}!")

# Display Metrics if Session Active
if st.session_state.session_active:
    st.sidebar.markdown("---")
    st.sidebar.metric("Current Balance", f"${st.session_state.balance:.2f}")
    st.sidebar.metric("Trade Size (10%)", f"${st.session_state.trade_size:.2f}")
    st.sidebar.metric("Target Profit (TP)", f"+${st.session_state.tp:.2f}")
    st.sidebar.metric("Stop Loss (SL)", f"-${st.session_state.sl:.2f}")
    st.sidebar.metric("Current PnL", f"${st.session_state.current_pnl:.2f}")

# ------------------------------------------------------------------------------
# Main App Layout
# ------------------------------------------------------------------------------
st.title("📈 Shawkat Quotex AI Web Scanner")

if not api_key:
    st.warning("⚠️ Please enter your OpenRouter API key in the sidebar to activate the web app.")
    st.stop()

if not st.session_state.session_active:
    st.info("👈 Please initialize your Session Balance from the sidebar to begin trading.")
    st.stop()

# Target Profit / Stop Loss Lock Check
if st.session_state.current_pnl >= st.session_state.tp:
    st.success(f"🎉 **TARGET PROFIT REACHED (+${st.session_state.tp:.2f})!** Stop trading for today.")
    st.stop()

if st.session_state.current_pnl <= -st.session_state.sl:
    st.error(f"🛑 **STOP LOSS HIT (-${st.session_state.sl:.2f})!** Trading locked for capital protection.")
    st.stop()

# Mode Selection
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "1️⃣ Manual Setup",
        "2️⃣ Screenshot Analyzer",
        "3️⃣ Manual & Sync Mode",
        "4️⃣ Auto 1-Min Intelligent Signal",
    ]
)

# ------------------------------------------------------------------------------
# Mode 1: Manual Setup
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("Mode 1: Manual Setup")
    col1, col2, col3 = st.columns(3)

    with col1:
        asset_m1 = st.selectbox(
            "Select Currency Pair",
            [
                "EUR/USD",
                "EUR/JPY",
                "CAD/JPY",
                "EUR/GBP",
                "AUD/JPY",
                "USD/JPY",
                "AUD/USD",
                "GBP/USD",
            ],
            key="m1_asset",
        )
    with col2:
        timer_m1 = st.selectbox(
            "Expiry Duration",
            [
                "1 Minute",
                "2 Minutes",
                "3 Minutes",
                "5 Minutes",
                "10 Minutes",
                "15 Minutes",
            ],
            key="m1_timer",
        )
    with col3:
        payout_m1 = st.slider("Broker Payout %", 80, 92, 85, key="m1_payout")

    if st.button("Generate Signal (Mode 1)", type="primary"):
        with st.spinner("Analyzing market structure across fallback engines..."):
            try:
                sig = generate_text_signal(api_key, asset_m1, timer_m1, payout_m1)
                st.session_state.last_signal = sig
                st.session_state.last_signal_timer = timer_m1
                st.session_state.last_signal_payout = payout_m1
            except Exception as e:
                st.error(str(e))

# ------------------------------------------------------------------------------
# Mode 2: Screenshot Analyzer Mode
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("Mode 2: Screenshot Analyzer")
    st.caption("Upload a 1-minute chart screenshot to detect trend strength, wicks, and dynamic expiry.")
    uploaded_file = st.file_uploader("Upload Quotex Chart Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Chart", use_container_width=True)

        if st.button("Analyze Chart & Generate Signal", type="primary"):
            with st.spinner("Analyzing candles and wicks using multi-model fallback..."):
                try:
                    img_bytes = uploaded_file.getvalue()
                    sig = generate_vision_signal(api_key, img_bytes)
                    st.session_state.last_signal = sig
                    st.session_state.last_signal_timer = sig.get("expiry", "1 Minute")
                    st.session_state.last_signal_payout = 90
                except Exception as e:
                    st.error(str(e))

# ------------------------------------------------------------------------------
# Mode 3: Manual Setup with Exact Sync Execution
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("Mode 3: Setup with Generate & Sync")
    col1, col2, col3 = st.columns(3)

    with col1:
        asset_m3 = st.selectbox(
            "Select Currency Pair",
            [
                "EUR/USD",
                "EUR/JPY",
                "CAD/JPY",
                "EUR/GBP",
                "AUD/JPY",
                "USD/JPY",
                "AUD/USD",
                "GBP/USD",
            ],
            key="m3_asset",
        )
    with col2:
        timer_m3 = st.selectbox(
            "Expiry Duration",
            ["1 Minute", "2 Minutes", "3 Minutes", "5 Minutes"],
            key="m3_timer",
        )
    with col3:
        payout_m3 = st.slider("Broker Payout %", 80, 92, 88, key="m3_payout")

    if st.button("🟢 Generate Live Signal Now", type="primary"):
        with st.spinner("Generating synchronized live signal..."):
            try:
                sig = generate_text_signal(api_key, asset_m3, timer_m3, payout_m3)
                st.session_state.last_signal = sig
                st.session_state.last_signal_timer = timer_m3
                st.session_state.last_signal_payout = payout_m3
            except Exception as e:
                st.error(str(e))

# ------------------------------------------------------------------------------
# Mode 4: Auto 1-Min Intelligent Signal Mode
# ------------------------------------------------------------------------------
with tab4:
    st.subheader("Mode 4: Auto 1-Min Intelligent Signal Mode")
    st.caption("Automatic fast execution signal for EUR/USD OTC (90% Payout / 1-Min Expiry).")

    if st.button("⚡ Run Auto 1-Min Scan", type="primary"):
        with st.spinner("Scanning OTC market action with AI fallback rotation..."):
            try:
                sig = generate_text_signal(api_key, "EUR/USD OTC", "1 Minute", 90)
                st.session_state.last_signal = sig
                st.session_state.last_signal_timer = "1 Minute"
                st.session_state.last_signal_payout = 90
            except Exception as e:
                st.error(str(e))

# ------------------------------------------------------------------------------
# Display Active Signal & Results Execution Area
# ------------------------------------------------------------------------------
if st.session_state.last_signal:
    st.markdown("---")
    sig_data = st.session_state.last_signal
    asset_flag = get_pair_flag(sig_data.get("asset", ""))
    signal_dir = sig_data.get("signal", "CALL").upper()

    signal_color = "green" if signal_dir == "CALL" else "red"
    signal_icon = "🟢 🚀 CALL" if signal_dir == "CALL" else "🔴 📉 PUT"

    st.markdown(f"## {asset_flag} **Asset:** `{sig_data.get('asset')}`")
    if "model_used" in sig_data:
        st.caption(f"⚡ *Executed successfully via fallback engine:* `{sig_data.get('model_used')}`")

    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.markdown(f"### Direction: :{signal_color}[{signal_icon}]")
        st.write(f"**Estimated Price:** `{sig_data.get('live_price')}`")
        st.write(f"**Expiry Timer:** `{st.session_state.get('last_signal_timer', '1 Minute')}`")
        st.write(f"**Sync Execution Time:** `{sig_data.get('execution_time')}`")

    with res_col2:
        st.write(f"**Win Accuracy:** `{sig_data.get('accuracy')}`")
        st.write(f"**Recommended Trade Size:** `${st.session_state.trade_size:.2f}`")
        st.write(f"**MTG Advice:** `{sig_data.get('mtg_advice')}`")

    if "wick_and_candle_analysis" in sig_data:
        st.info(f"**Wick Analysis:** {sig_data.get('wick_and_candle_analysis')}")

    st.caption(f"**Technical Reason:** {sig_data.get('reason')}")

    # Result Logging Controls
    st.markdown("### Select Trade Result")
    btn_win, btn_loss = st.columns(2)

    payout_pct = float(st.session_state.get("last_signal_payout", 90)) / 100.0

    if btn_win.button("✅ WIN", type="secondary", use_container_width=True):
        profit = st.session_state.trade_size * payout_pct
        st.session_state.balance += profit
        st.session_state.current_pnl += profit
        st.session_state.last_signal = None
        st.success(f"Added +${profit:.2f} to account balance!")
        st.rerun()

    if btn_loss.button("❌ LOSS", type="secondary", use_container_width=True):
        loss = st.session_state.trade_size
        st.session_state.balance -= loss
        st.session_state.current_pnl -= loss
        st.session_state.last_signal = None
        st.error(f"Deducted -${loss:.2f} from account balance.")
        st.rerun()
