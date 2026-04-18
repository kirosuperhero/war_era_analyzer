import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time
import json
import os
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(
    page_title="War Era - Jet Market Analyzer", 
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

YOUR_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7Il9pZCI6IjY5Y2VlY2Y1MTk3Zjg0NWZjOWZlZGU1YyJ9LCJpYXQiOjE3NzUxNjg3NTcsImV4cCI6MTc3Nzc2MDc1N30.nIKi8ohQAYsAVXQL9_rlRUr93TDg-G-DVOCQOrRdOtY"

# ========== إعدادات الـ Theme ==========
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; }
    .stDataFrame tbody td, .stDataFrame thead th { color: #FFFFFF !important; }
    .stDataFrame tbody tr td { background-color: #1a1a2e !important; border-bottom: 1px solid #2a2a4a !important; }
    .stDataFrame tbody tr:nth-child(even) td { background-color: #222240 !important; }
    .stDataFrame thead tr th { background-color: #2a2a4a !important; color: #FFFFFF !important; }
    td:first-child { color: #00FF88 !important; font-weight: bold !important; }
    td:nth-child(2) { color: #FFB347 !important; font-weight: bold !important; }
    td:nth-child(3) { color: #FF6B6B !important; font-weight: bold !important; }
    td:nth-child(4) { color: #4ECDC4 !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] { background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%) !important; color: #00ff00 !important; }
    h1 { color: #ff6666 !important; text-align: center !important; }
    .stAlert { border-radius: 10px !important; }
    .stSuccess { background-color: #0a2a0a !important; border-left: 5px solid #00ff00 !important; }
    .stWarning { background-color: #2a2a0a !important; border-left: 5px solid #ffaa00 !important; }
    .stError { background-color: #2a0a0a !important; border-left: 5px solid #ff4444 !important; }
    .stInfo { background-color: #0a2a2a !important; border-left: 5px solid #44aaff !important; }
</style>
""", unsafe_allow_html=True)

# ========== دوال JSON الآمنة ==========
import numpy as np
import pandas as pd

PRICE_HISTORY_FILE = "data/price_history.json"
ALERTS_HISTORY_FILE = "data/alerts_history.json"

def convert_to_serializable(obj):
    """تحويل أي كائن غير JSONable إلى JSONable"""
    if isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.to_list()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    return obj

def load_price_history():
    """تحميل تاريخ الأسعار السابق"""
    os.makedirs("data", exist_ok=True)
    
    if not os.path.exists(PRICE_HISTORY_FILE):
        save_price_history({})
        return {}
    
    try:
        with open(PRICE_HISTORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except:
        save_price_history({})
        return {}

def save_price_history(history):
    """حفظ تاريخ الأسعار"""
    try:
        os.makedirs("data", exist_ok=True)
        with open(PRICE_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False, default=convert_to_serializable)
        return True
    except Exception as e:
        st.error(f"خطأ في حفظ الملف: {e}")
        return False

def load_alerts_history():
    """تحميل تاريخ التنبيهات"""
    os.makedirs("data", exist_ok=True)
    
    if not os.path.exists(ALERTS_HISTORY_FILE):
        save_alerts_history({"alerts_sent": []})
        return {"alerts_sent": []}
    
    try:
        with open(ALERTS_HISTORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {"alerts_sent": []}
            data = json.loads(content)
            if 'alerts_sent' not in data:
                data['alerts_sent'] = []
            return data
    except:
        save_alerts_history({"alerts_sent": []})
        return {"alerts_sent": []}

def save_alerts_history(alerts):
    """حفظ تاريخ التنبيهات"""
    try:
        os.makedirs("data", exist_ok=True)
        with open(ALERTS_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(alerts, f, indent=2, ensure_ascii=False, default=convert_to_serializable)
        return True
    except Exception as e:
        st.error(f"خطأ في حفظ ملف التنبيهات: {e}")
        return False

def categorize_jet(jet):
    attack_group = round(jet['attack'] / 5) * 5
    critical_group = round(jet['critical'] / 2) * 2
    return f"A{attack_group}_C{critical_group}"

def predict_price(history_prices):
    """توقع السعر القادم بناءً على الاتجاه"""
    if len(history_prices) < 3:
        return None, None
    
    X = np.array(range(len(history_prices))).reshape(-1, 1)
    y = np.array(history_prices)
    
    model = LinearRegression()
    model.fit(X, y)
    
    next_price = model.predict([[len(history_prices)]])[0]
    trend = "صاعد" if model.coef_[0] > 0 else "هابط"
    
    return next_price, trend

def check_price_alert(jet_category, current_price, price_history):
    """تنبيه تلقائي عند نزول السعر عن أقل سعر"""
    if jet_category in price_history and len(price_history[jet_category]) > 0:
        history = price_history[jet_category]
        min_price = min([h['price'] for h in history])
        
        if current_price < min_price:
            return True, min_price
    return False, None

def compare_sellers(jet_category, price_history, current_user=None):
    """مقارنة البائعين لنفس نوع الطائرة"""
    if jet_category not in price_history:
        return None
    
    sellers = {}
    for record in price_history[jet_category]:
        user = record.get('user', 'unknown')
        if user not in sellers:
            sellers[user] = {'prices': [], 'count': 0, 'last_seen': None}
        sellers[user]['prices'].append(record['price'])
        sellers[user]['count'] += 1
        sellers[user]['last_seen'] = record.get('time', '')
    
    # حساب المتوسط لكل بائع
    seller_stats = []
    for user, data in sellers.items():
        seller_stats.append({
            'user': user,
            'avg_price': sum(data['prices']) / len(data['prices']),
            'min_price': min(data['prices']),
            'max_price': max(data['prices']),
            'count': data['count']
        })
    
    return pd.DataFrame(seller_stats).sort_values('avg_price')

def time_ago(created_at_str):
    try:
        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
        now = datetime.now().astimezone()
        diff = now - created_at
        minutes = int(diff.total_seconds() / 60)
        seconds = int(diff.total_seconds())
        
        if minutes < 1:
            return f"{seconds} ثانية"
        elif minutes < 60:
            return f"{minutes} دقيقة"
        else:
            hours = minutes // 60
            return f"{hours} ساعة"
    except:
        return "غير معروف"

@st.cache_data(ttl=60, show_spinner=False)
def fetch_all_offers(max_pages=10):
    all_items = []
    cursor = None
    API_URL = "https://api4.warera.io/trpc/itemOffer.getItemOffers,transaction.getPaginatedTransactions?batch=1"
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for page in range(max_pages):
        status_text.text(f"جلب الصفحة {page + 1}/{max_pages}...")
        
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"jwt={YOUR_JWT}",
            "User-Agent": "Mozilla/5.0"
        }
        
        payload = {
            "0": {"itemCode": "jet", "limit": 50, "cursor": cursor} if cursor else {"itemCode": "jet", "limit": 50},
            "1": {"itemCode": "jet", "limit": 1, "transactionType": "itemMarket", "direction": "forward"}
        }
        
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                items = data[0].get('result', {}).get('data', {}).get('items', [])
                cursor = data[0].get('result', {}).get('data', {}).get('nextCursor')
                
                for item in items:
                    jet_info = item.get('item', {})
                    user_id = item.get('user', '')
                    attack = jet_info.get('skills', {}).get('attack', 0)
                    critical = jet_info.get('skills', {}).get('criticalChance', 0)
                    
                    attack_score = (attack - 221) / (300 - 221) if attack >= 221 else 0
                    critical_score = (critical - 41) / (50 - 41) if critical >= 41 else 0
                    attack_score = max(0, min(1, attack_score))
                    critical_score = max(0, min(1, critical_score))
                    quality_score = round(((attack_score + critical_score) / 2) * 100, 1)
                    
                    all_items.append({
                        'id': item.get('_id'),
                        'price': item.get('price'),
                        'user': user_id[:8] if user_id else 'unknown',
                        'attack': attack,
                        'critical': critical,
                        'quality_score': quality_score,
                        'attack_score': round(attack_score * 100, 1),
                        'critical_score': round(critical_score * 100, 1),
                        'createdAt': item.get('createdAt'),
                        'time_ago': time_ago(item.get('createdAt', ''))
                    })
                time.sleep(0.3)
            progress_bar.progress((page + 1) / max_pages)
        except Exception as e:
            break
    
    progress_bar.empty()
    status_text.empty()
    
    for jet in all_items:
        jet['value_for_money'] = (jet['quality_score'] / jet['price']) * 1000 if jet['price'] > 0 else 0
    
    return all_items

# تحديث تلقائي كل 30 ثانية
st_autorefresh(interval=30000, limit=100, key="auto_refresh")

st.title("✈️ War Era - Jet Market Analyzer")
st.markdown("تحليل متقدم لسوق الطائرات **JET** - اكتشف أفضل الصفقات")

# Sidebar
with st.sidebar:
    st.header("⚙️ إعدادات التحليل")
    max_pages = st.slider("عدد صفحات الجلب", 1, 20, 10)
    min_quality = st.slider("الحد الأدنى للجودة (%)", 0, 100, 0)
    max_price = st.number_input("الحد الأقصى للسعر", 0, 5000, 5000, step=500)
    
    st.divider()
    
    sort_by = st.selectbox("ترتيب حسب", 
                          ["القيمة مقابل السعر", "الجودة", "السعر (أقل سعر أولاً)", "السعر (أعلى سعر أولاً)", "الأحدث"])
    
    st.divider()
    
    if st.button("🔄 تحديث البيانات", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# جلب البيانات
with st.spinner("جاري تحليل السوق..."):
    all_offers = fetch_all_offers(max_pages=max_pages)

if not all_offers:
    st.error("❌ لا توجد عروض للطائرات حالياً")
    st.stop()

df = pd.DataFrame(all_offers)
df_filtered = df[(df['quality_score'] >= min_quality) & (df['price'] <= max_price)]

if sort_by == "القيمة مقابل السعر":
    df_sorted = df_filtered.sort_values('value_for_money', ascending=False)
elif sort_by == "الجودة":
    df_sorted = df_filtered.sort_values('quality_score', ascending=False)
elif sort_by == "السعر (أقل سعر أولاً)":
    df_sorted = df_filtered.sort_values('price', ascending=True)
elif sort_by == "السعر (أعلى سعر أولاً)":
    df_sorted = df_filtered.sort_values('price', ascending=False)
else:
    df_sorted = df_filtered.sort_values('createdAt', ascending=False)

# إحصائيات sidebar
with st.sidebar:
    st.divider()
    st.header("📊 إحصائيات سريعة")
    st.metric("إجمالي الطائرات", len(df_filtered))
    if len(df_filtered) > 0:
        st.metric("أقل سعر", f"${df_filtered['price'].min():,}")
        st.metric("أعلى جودة", f"{df_filtered['quality_score'].max():.1f}%")
        st.metric("متوسط السعر", f"${df_filtered['price'].mean():,.0f}")
    
    good_deals = df_filtered[df_filtered['quality_score'] >= 60]
    if len(good_deals) > 0:
        best = good_deals.loc[good_deals['value_for_money'].idxmax()]
        st.success(f"**أفضل صفقة:**\n💰 ${best['price']:,}\n⚔️ {best['attack']}\n🎯 {best['critical']}%\n📊 {best['quality_score']}%")

# ========== تبويبات ==========
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 جدول الطائرات", "🏆 أفضل الصفقات", "⭐ أفضل جودة", "📊 تحليل الأسعار", "🔔 التنبيهات"])

# TAB 1: جدول الطائرات
with tab1:
    st.subheader(f"📋 عرض {len(df_sorted)} طائرة")
    display_df = df_sorted[['price', 'attack', 'critical', 'quality_score', 'value_for_money', 'user', 'time_ago']].copy()
    display_df.columns = ['السعر', 'الهجوم', 'الكريتيكال%', 'الجودة%', 'القيمة/السعر', 'البائع', 'منذ']
    
    st.data_editor(
        display_df,
        column_config={
            "السعر": st.column_config.NumberColumn("💰 السعر", format="$ %d"),
            "الهجوم": st.column_config.NumberColumn("⚔️ الهجوم", format="%d / 300"),
            "الكريتيكال%": st.column_config.NumberColumn("🎯 الكريتيكال", format="%.1f %%"),
            "الجودة%": st.column_config.ProgressColumn("📊 الجودة", format="%.1f %%", min_value=0, max_value=100),
            "القيمة/السعر": st.column_config.NumberColumn("💎 القيمة", format="%.2f"),
        },
        use_container_width=True,
        height=500,
        hide_index=True,
        disabled=True
    )

# TAB 2: أفضل الصفقات
with tab2:
    st.subheader("🏆 أفضل 10 صفقات")
    best_value = df_sorted.nlargest(10, 'value_for_money')
    for i, row in best_value.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{i+1}. 💰 ${row['price']:,}** (منذ {row['time_ago']})")
                st.write(f"⚔️ Attack: {row['attack']} | 🎯 Critical: {row['critical']}%")
            with col2:
                st.metric("الجودة", f"{row['quality_score']}%")
            st.caption(f"👤 {row['user']}")

# TAB 3: أفضل جودة
with tab3:
    st.subheader("⭐ أفضل 10 طائرات جودة")
    best_quality = df_sorted.nlargest(10, 'quality_score')
    for i, row in best_quality.iterrows():
        with st.container(border=True):
            st.write(f"**{i+1}. ⚔️ {row['attack']} | 🎯 {row['critical']}%**")
            st.write(f"💰 ${row['price']:,} | 🕐 {row['time_ago']}")
            st.caption(f"👤 {row['user']}")
            
# TAB 4: تحليل الأسعار (التطويرات الثلاثة)
with tab4:
    st.subheader("📊 تحليل الأسعار التاريخي")
    
    # تحميل التاريخ
    price_history = load_price_history()
    alerts_history = load_alerts_history()
    
    # اختيار طائرة للتحليل - طريقة بسيطة ومضمونة
    temp_df = df_sorted.head(30).copy()
    temp_df['display'] = temp_df.apply(
        lambda x: f"💰 ${x['price']} | ⚔️ {x['attack']} | 🎯 {x['critical']}% | 👤 {x['user']}", 
        axis=1
    )
    
    selected_display = st.selectbox(
        "اختر طائرة لتحليل تاريخ أسعارها:",
        options=temp_df['display'].tolist()
    )
    
    if selected_display:
        jet = temp_df[temp_df['display'] == selected_display].iloc[0]
        jet_category = categorize_jet(jet)
        current_price = jet['price']
        current_time = datetime.now().isoformat()
        
        # تسجيل السعر الحالي
        if jet_category not in price_history:
            price_history[jet_category] = []
        
        # تجنب التكرار لنفس البائع والسعر
        is_duplicate = False
        for record in price_history[jet_category][-5:]:
            if record.get('user') == jet['user'] and record['price'] == current_price:
                is_duplicate = True
                break
        
        if not is_duplicate:
            price_history[jet_category].append({
                'price': current_price,
                'time': current_time,
                'user': jet['user'],
                'attack': jet['attack'],
                'critical': jet['critical']
            })
            price_history[jet_category] = price_history[jet_category][-50:]
            save_price_history(price_history)
        
        # ===== 1. تنبيه تلقائي =====
        is_alert, min_price = check_price_alert(jet_category, current_price, price_history)
        
        if is_alert:
            st.success(f"🔔 **تنبيه!** هذا أقل سعر شوهد لهذا النوع من الطائرات! (كان أقل سعر سابق ${min_price})")
            # تحديث سجل التنبيهات
            if 'alerts_sent' not in alerts_history:
                alerts_history['alerts_sent'] = []
            alert_id = f"{jet_category}_{current_price}_{jet['user']}"
            if alert_id not in alerts_history['alerts_sent']:
                alerts_history['alerts_sent'].append(alert_id)
                save_alerts_history(alerts_history)
        
        # عرض الإحصائيات الأساسية
        history = price_history[jet_category]
        prices = [h['price'] for h in history]
        
        min_price_hist = min(prices)
        max_price_hist = max(prices)
        avg_price_hist = sum(prices) / len(prices)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 السعر الحالي", f"${current_price}")
        with col2:
            delta = ((current_price - min_price_hist) / min_price_hist * 100) if current_price > min_price_hist else 0
            st.metric("📉 أقل سعر", f"${min_price_hist}", delta=f"-{delta:.1f}%" if delta > 0 else "أقل سعر!")
        with col3:
            st.metric("📈 أعلى سعر", f"${max_price_hist}")
        with col4:
            st.metric("📊 المتوسط", f"${avg_price_hist:.0f}")
        
        # ===== 2. توقعات الأسعار =====
        next_price, trend = predict_price(prices)
        if next_price:
            st.info(f"📈 **توقع السعر القادم:** ${next_price:.0f} (اتجاه {trend})")
            if trend == "هابط" and next_price < current_price:
                st.warning("⚠️ التوقعات تشير إلى انخفاض الأسعار قريباً - الأفضل الانتظار")
            elif trend == "صاعد" and next_price > current_price:
                st.success("✅ التوقعات تشير إلى ارتفاع الأسعار - السعر الحالي مناسب")
        
        # ===== 3. مقارنة البائعين =====
        st.subheader("🏪 مقارنة البائعين لهذا النوع من الطائرات")
        seller_comparison = compare_sellers(jet_category, price_history, jet['user'])
        
        if seller_comparison is not None and len(seller_comparison) > 0:
            st.dataframe(
                seller_comparison.head(10),
                column_config={
                    "user": "👤 البائع",
                    "avg_price": st.column_config.NumberColumn("💰 متوسط السعر", format="$ %.0f"),
                    "min_price": st.column_config.NumberColumn("📉 أقل سعر", format="$ %.0f"),
                    "max_price": st.column_config.NumberColumn("📈 أعلى سعر", format="$ %.0f"),
                    "count": "📊 عدد الصفقات"
                },
                use_container_width=True
            )
            
            # تمييز البائع الحالي
            current_seller = jet['user']
            seller_row = seller_comparison[seller_comparison['user'] == current_seller]
            if len(seller_row) > 0:
                avg_seller = seller_row.iloc[0]['avg_price']
                if current_price < avg_seller:
                    st.success(f"✅ البائع الحالي ({current_seller}) أرخص من متوسطه السابق (${avg_seller:.0f})")
                elif current_price > avg_seller:
                    st.warning(f"⚠️ البائع الحالي ({current_seller}) أغلى من متوسطه السابق (${avg_seller:.0f})")
        
        # تقييم الصفقة
        st.subheader("🎯 تقييم الصفقة")
        if current_price <= min_price_hist * 1.05:
            st.success("✅ **صفقة ممتازة!** هذا أقل سعر أو قريب جداً من أقل سعر شوهد")
        elif current_price <= avg_price_hist:
            st.info("👍 **صفقة جيدة** - السعر أقل من المتوسط التاريخي")
        elif current_price <= max_price_hist * 0.8:
            st.warning("⚠️ **سعر متوسط** - ممكن تلاقي أحسن لو استنيت")
        else:
            st.error("❌ **سعر مرتفع** - الأفضل تستنى")
        
        # رسم بياني لتاريخ الأسعار
        st.subheader("📈 تطور الأسعار")
        history_df = pd.DataFrame(sorted(history, key=lambda x: x['time']))
        history_df['time_dt'] = pd.to_datetime(history_df['time'])
        
        fig_history = px.line(
            history_df, 
            x='time_dt', 
            y='price',
            title=f'تاريخ أسعار الطائرات (Attack {jet["attack"]} - Critical {jet["critical"]}%)',
            markers=True
        )
        fig_history.add_hline(y=current_price, line_dash="dash", line_color="red", annotation_text="السعر الحالي")
        fig_history.add_hline(y=min_price_hist, line_dash="dash", line_color="green", annotation_text="أقل سعر")
        fig_history.add_hrect(y0=avg_price_hist*0.9, y1=avg_price_hist*1.1, line_width=0, fillcolor="gray", opacity=0.2, annotation_text="منطقة المتوسط")
        fig_history.update_layout(template='plotly_dark')
        st.plotly_chart(fig_history, use_container_width=True)
        
        # آخر 10 أسعار
        with st.expander("📜 آخر 10 أسعار شوهدت"):
            for h in sorted(history, key=lambda x: x['time'], reverse=True)[:10]:
                time_ago_str = time_ago(h['time'])
                emoji = "🟢" if h['price'] <= min_price_hist * 1.05 else "🟡" if h['price'] <= avg_price_hist else "🔴"
                st.write(f"{emoji} ${h['price']} - منذ {time_ago_str} - البائع: {h['user']}")

# TAB 5: التنبيهات
with tab5:
    st.subheader("🔔 التنبيهات المسجلة")
    
    price_history = load_price_history()
    
    # البحث عن صفقات ممتازة حالياً
    st.subheader("🎯 صفقات ممتازة حالياً")
    excellent_deals = df_filtered[
        (df_filtered['price'] < 600) & 
        (df_filtered['quality_score'] > 70)
    ].sort_values('value_for_money', ascending=False)
    
    if len(excellent_deals) > 0:
        for _, row in excellent_deals.head(10).iterrows():
            with st.container(border=True):
                st.write(f"**💰 ${row['price']:,}** - جودة {row['quality_score']}% - Attack {row['attack']} - Critical {row['critical']}%")
                st.caption(f"👤 {row['user']} | 🕐 {row['time_ago']}")
    else:
        st.info("لا توجد صفقات ممتازة حالياً")
    
    # تنبيهات تاريخية
    st.subheader("📋 تنبيهات سابقة")
    alerts_history = load_alerts_history()
    if alerts_history.get('alerts_sent'):
        st.write(f"عدد التنبيهات المسجلة: {len(alerts_history['alerts_sent'])}")
    else:
        st.write("لا توجد تنبيهات مسجلة بعد")