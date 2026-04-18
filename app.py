import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="War Era - Jet Market Analyzer", 
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ========== تحسينات إضافية للوضوح ==========
st.markdown("""
<style>
    /* تحسين وضوح النصوص في الدارك مود */
    body, .stApp, .main, .stMarkdown, .stText, p, div, span, label {
        color: #FFFFFF !important;
        font-size: 14px !important;
    }
    
    /* تحسين الجداول - خلفية أفتح ونصوص بيضاء */
    .stDataFrame {
        background-color: #1e1e2e !important;
    }
    .stDataFrame table {
        background-color: #1e1e2e !important;
        color: #ffffff !important;
        font-size: 14px !important;
    }
    .stDataFrame th {
        background-color: #2d2d3d !important;
        color: #00ff88 !important;
        font-weight: bold !important;
        font-size: 15px !important;
        padding: 12px !important;
    }
    .stDataFrame td {
        background-color: #1e1e2e !important;
        color: #ffffff !important;
        padding: 10px !important;
        border-bottom: 1px solid #3d3d4d !important;
    }
    .stDataFrame tr:hover td {
        background-color: #2d2d3d !important;
    }
    
    /* تحسين الـ Metric Cards */
    div[data-testid="stMetricValue"] {
        color: #00ff88 !important;
        font-size: 2rem !important;
        font-weight: bold !important;
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d3d 100%);
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }
    div[data-testid="stMetricLabel"] {
        color: #aaaaaa !important;
        font-size: 0.9rem !important;
        font-weight: bold !important;
    }
    div[data-testid="stMetricDelta"] {
        color: #ff8888 !important;
        font-size: 0.8rem !important;
    }
    
    /* تحسين الـ Sidebar */
    .css-1d391kg, .stSidebar {
        background-color: #1a1a2a !important;
    }
    .stSidebar .stMarkdown, .stSidebar p, .stSidebar label {
        color: #ffffff !important;
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4 {
        color: #00ff88 !important;
    }
    
    /* تحسين الأزرار */
    .stButton button {
        background: linear-gradient(135deg, #ff4b4b 0%, #ff6b6b 100%) !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 14px !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        transition: all 0.3s ease !important;
    }
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(255,75,75,0.3) !important;
    }
    
    /* تحسين الـ Select Box */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #2d2d3d !important;
        border: 1px solid #4d4d5d !important;
        border-radius: 8px !important;
    }
    .stSelectbox label {
        color: #00ff88 !important;
    }
    
    /* تحسين الـ Slider */
    .stSlider label {
        color: #00ff88 !important;
    }
    
    /* تحسين الـ Number Input */
    .stNumberInput input {
        background-color: #2d2d3d !important;
        color: white !important;
        border: 1px solid #4d4d5d !important;
        border-radius: 8px !important;
    }
    
    /* تحسين التبويبات */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
        background-color: #1a1a2a;
        padding: 8px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2d2d3d !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 8px 20px !important;
        font-weight: bold !important;
        font-size: 14px !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ff4b4b 0%, #ff6b6b 100%) !important;
        color: white !important;
    }
    
    /* تحسين الـ Expander */
    .streamlit-expanderHeader {
        background-color: #2d2d3d !important;
        color: #00ff88 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    
    /* تحسين رسائل النجاح والتحذير */
    .stAlert {
        border-radius: 10px !important;
        font-weight: bold !important;
    }
    .stSuccess {
        background-color: #1e3a2e !important;
        border-left: 4px solid #00ff88 !important;
    }
    .stWarning {
        background-color: #3a2e1e !important;
        border-left: 4px solid #ffaa00 !important;
    }
    .stError {
        background-color: #3a1e1e !important;
        border-left: 4px solid #ff4b4b !important;
    }
    
    /* تحسين الكود والـ IDs */
    code {
        background-color: #2d2d3d !important;
        color: #00ff88 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-family: monospace !important;
        font-size: 13px !important;
    }
    
    /* تحسين الخطوط العربية */
    * {
        font-family: 'Segoe UI', 'Tahoma', 'Arial', sans-serif !important;
    }
    
    /* تحسين صناديق التنبيه */
    .alert-box {
        background: linear-gradient(135deg, #2d2d3d 0%, #1e1e2e 100%);
        border-left: 5px solid #ff4b4b;
        padding: 15px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .alert-box h3 {
        color: #ff6b6b !important;
        margin-top: 0 !important;
    }
    .alert-box p {
        color: #ffffff !important;
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

YOUR_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7Il9pZCI6IjY5Y2VlY2Y1MTk3Zjg0NWZjOWZlZGU1YyJ9LCJpYXQiOjE3NzUxNjg3NTcsImV4cCI6MTc3Nzc2MDc1N30.nIKi8ohQAYsAVXQL9_rlRUr93TDg-G-DVOCQOrRdOtY"

# ========== نظام التنبيهات ==========
ALERTS_FILE = "data/alerts.json"

def load_alerts():
    """تحميل التنبيهات السابقة"""
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, 'r') as f:
            return json.load(f)
    return {"last_scan": None, "best_deals": [], "notified_ids": []}

def save_alerts(alerts):
    """حفظ التنبيهات"""
    os.makedirs("data", exist_ok=True)
    with open(ALERTS_FILE, 'w') as f:
        json.dump(alerts, f, indent=2)

def check_new_deals(current_best, alerts):
    """التحقق من وجود صفقات جديدة"""
    new_deals = []
    for deal in current_best:
        deal_id = f"{deal['price']}_{deal['user']}"
        if deal_id not in alerts['notified_ids']:
            # تحقق إذا كانت الصفقة أفضل من آخر صفقة تم التنبيه عليها
            if len(alerts['best_deals']) > 0:
                old_best_price = min([d['price'] for d in alerts['best_deals']])
                if deal['price'] < old_best_price * 0.9:  # أرخص ب 10%
                    new_deals.append(deal)
            else:
                new_deals.append(deal)
    return new_deals

# دالة تحويل الوقت
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

@st.cache_data(ttl=60, show_spinner=False)  # خفضت الـ TTL عشان التنبيهات أسرع
def fetch_all_offers(max_pages=10):
    """جلب كل العروض من السوق"""
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

# ========== واجهة المستخدم ==========
st.title("✈️ War Era - Jet Market Analyzer")
st.markdown("تحليل متقدم لسوق الطائرات **JET** - اكتشف أفضل الصفقات بناءً على الجودة والسعر")

# ========== نظام التحديث التلقائي والتنبيهات ==========
# تحديث تلقائي كل 30 ثانية (للتنبيهات)
count = st_autorefresh(interval=30000, limit=100, key="auto_refresh")

# Sidebar
with st.sidebar:
    st.header("⚙️ إعدادات التحليل")
    max_pages = st.slider("عدد صفحات الجلب", min_value=1, max_value=20, value=10, 
                          help="كل صفحة = 50 طائرة")
    min_quality = st.slider("الحد الأدنى للجودة (%)", min_value=0, max_value=100, value=0)
    max_price = st.number_input("الحد الأقصى للسعر", min_value=0, value=5000, step=500)
    
    st.divider()
    
    # ========== إعدادات التنبيهات ==========
    st.header("🔔 نظام التنبيهات")
    
    enable_alerts = st.checkbox("تفعيل التنبيهات", value=True)
    alert_price_threshold = st.number_input("نبهني لو السعر أقل من", min_value=0, value=500, step=50)
    alert_quality_threshold = st.slider("وجودة أكبر من", 0, 100, 70)
    
    if st.button("🔕 مسح التنبيهات السابقة", use_container_width=True):
        alerts = load_alerts()
        alerts['notified_ids'] = []
        alerts['best_deals'] = []
        save_alerts(alerts)
        st.success("✅ تم مسح التنبيهات!")
    
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

# تحويل إلى DataFrame
df = pd.DataFrame(all_offers)

# تطبيق الفلاتر
df_filtered = df[(df['quality_score'] >= min_quality) & (df['price'] <= max_price)]

# ========== نظام التنبيهات ==========
if enable_alerts:
    alerts = load_alerts()
    
    # البحث عن صفقات ممتازة
    excellent_deals = df_filtered[
        (df_filtered['price'] < alert_price_threshold) & 
        (df_filtered['quality_score'] > alert_quality_threshold)
    ]
    
    if len(excellent_deals) > 0:
        # ترتيب حسب الأفضل
        excellent_deals = excellent_deals.sort_values('value_for_money', ascending=False)
        
        # التحقق من الصفقات الجديدة
        current_best = excellent_deals.head(5).to_dict('records')
        new_deals = check_new_deals(current_best, alerts)
        
        if new_deals:
            # عرض تنبيه في الصفحة
            for deal in new_deals:
                with st.container():
                    st.markdown(f"""
                    <div class="alert-box" style="border-left-color: #ff4b4b; background: linear-gradient(135deg, #2d2d2d 0%, #1e1e1e 100%);">
                        <h3 style="color: #ff4b4b; margin: 0;">🔔 صفقة جديدة ممتازة!</h3>
                        <hr style="margin: 10px 0;">
                        <p style="font-size: 1.2rem; margin: 5px 0;">💰 <strong style="color: #00ff00;">${deal['price']:,}</strong> - جودة <strong style="color: #ffa500;">{deal['quality_score']}%</strong></p>
                        <p style="margin: 5px 0;">⚔️ Attack: {deal['attack']} | 🎯 Critical: {deal['critical']}%</p>
                        <p style="margin: 5px 0;">👤 البائع: <code style="background: #000; padding: 2px 6px; border-radius: 4px;">{deal['user']}</code></p>
                        <p style="margin: 5px 0;">🕐 منذ {deal['time_ago']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # إضافة زر نسخ ID
                    if st.button(f"📋 نسخ ID البائع - {deal['user']}", key=f"copy_{deal['user']}_{deal['price']}"):
                        st.write(f"✅ تم نسخ: `{deal['user']}`")
                        st.balloons()
            
            # تحديث التنبيهات
            alerts['last_scan'] = datetime.now().isoformat()
            alerts['best_deals'] = current_best
            for deal in new_deals:
                alerts['notified_ids'].append(f"{deal['price']}_{deal['user']}")
            save_alerts(alerts)
    
    # عرض آخر تحديث للتنبيهات
    if alerts['last_scan']:
        st.info(f"🕐 آخر تحديث للتنبيهات: {datetime.fromisoformat(alerts['last_scan']).strftime('%H:%M:%S')}")

# الترتيب
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

# إحصائيات في الـ sidebar
with st.sidebar:
    st.divider()
    st.header("📊 إحصائيات سريعة")
    st.metric("إجمالي الطائرات", len(df_filtered))
    if len(df_filtered) > 0:
        st.metric("أقل سعر", f"${df_filtered['price'].min():,}")
        st.metric("أعلى جودة", f"{df_filtered['quality_score'].max():.1f}%")
        st.metric("متوسط السعر", f"${df_filtered['price'].mean():,.0f}")
        
        # تحذير إذا فيه صفقة ممتازة
        excellent = df_filtered[(df_filtered['price'] < 600) & (df_filtered['quality_score'] > 75)]
        if len(excellent) > 0:
            st.warning(f"⚠️ في {len(excellent)} صفقة ممتازة! راجع التبويبات")
    
    # توصية سريعة
    st.divider()
    st.header("🎯 التوصية")
    good_deals = df_filtered[df_filtered['quality_score'] >= 60]
    if len(good_deals) > 0:
        best = good_deals.loc[good_deals['value_for_money'].idxmax()]
        st.success(f"**أفضل صفقة:**\n\n💰 ${best['price']:,}\n⚔️ Attack: {best['attack']}\n🎯 Critical: {best['critical']}%\n📊 جودة: {best['quality_score']}%")
    else:
        st.warning("لا توجد طائرات بجودة عالية حالياً")

# ========== تبويبات ==========
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 جدول الطائرات", "🏆 أفضل الصفقات", "⭐ أفضل جودة", "🔔 التنبيهات", "📈 تحليلات"])

# ========== TAB 1: جدول الطائرات ==========
with tab1:
    st.subheader(f"📋 عرض {len(df_sorted)} طائرة")
    
    display_df = df_sorted[['price', 'attack', 'critical', 'quality_score', 'value_for_money', 'user', 'time_ago']].copy()
    display_df.columns = ['السعر', 'الهجوم', 'الكريتيكال%', 'الجودة%', 'القيمة/السعر', 'البائع', 'منذ']
    
    # استخدام data_editor بدل dataframe
    st.data_editor(
        display_df,
        column_config={
            "السعر": st.column_config.NumberColumn("💰 السعر", format="$ %d"),
            "الهجوم": st.column_config.NumberColumn("⚔️ الهجوم", format="%d / 300"),
            "الكريتيكال%": st.column_config.NumberColumn("🎯 الكريتيكال", format="%.1f %%"),
            "الجودة%": st.column_config.ProgressColumn("📊 الجودة", format="%.1f %%", min_value=0, max_value=100),
            "القيمة/السعر": st.column_config.NumberColumn("💎 القيمة", format="%.2f"),
            "البائع": st.column_config.TextColumn("👤 البائع"),
            "منذ": st.column_config.TextColumn("🕐 منذ"),
        },
        use_container_width=True,
        height=500,
        hide_index=True,
        disabled=True
    )

# ========== TAB 2: أفضل الصفقات ==========
with tab2:
    st.subheader("🏆 أفضل 10 صفقات (أعلى قيمة مقابل السعر)")
    
    best_value = df_sorted.nlargest(10, 'value_for_money')
    
    for i, row in best_value.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{i+1}. 💰 السعر: ${row['price']:,}** (منذ {row['time_ago']})")
                st.write(f"   ⚔️ Attack: {row['attack']} / 300 ({row['attack_score']}% من max)")
                st.write(f"   🎯 Critical: {row['critical']}% / 50% ({row['critical_score']}% من max)")
            with col2:
                st.metric("الجودة", f"{row['quality_score']}%")
                st.metric("القيمة", f"{row['value_for_money']:.2f}")
            st.caption(f"👤 البائع: {row['user']}")

# ========== TAB 3: أفضل جودة ==========
with tab3:
    st.subheader("⭐ أفضل 10 طائرات من حيث الجودة")
    
    best_quality = df_sorted.nlargest(10, 'quality_score')
    
    for i, row in best_quality.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{i+1}. ⚔️ Attack: {row['attack']} | 🎯 Critical: {row['critical']}%**")
                st.write(f"   💰 السعر: ${row['price']:,}")
                st.write(f"   🕐 منذ {row['time_ago']}")
            with col2:
                st.metric("الجودة", f"{row['quality_score']}%")
            st.caption(f"👤 البائع: {row['user']}")

# ========== TAB 4: التنبيهات النشطة ==========
with tab4:
    st.subheader("🔔 التنبيهات النشطة")
    
    st.info(f"""
    **إعدادات التنبيهات الحالية:**
    - ✅ التنبيه مفعل: {enable_alerts}
    - 💰 سعر أقل من: ${alert_price_threshold}
    - ⭐ جودة أكبر من: {alert_quality_threshold}%
    """)
    
    # عرض الصفقات التي تحقق التنبيهات
    active_alerts = df_filtered[
        (df_filtered['price'] < alert_price_threshold) & 
        (df_filtered['quality_score'] > alert_quality_threshold)
    ].sort_values('value_for_money', ascending=False)
    
    if len(active_alerts) > 0:
        st.success(f"🎯 يوجد {len(active_alerts)} صفقة تحقق شروط التنبيه!")
        for idx, row in active_alerts.head(10).iterrows():
            with st.container(border=True):
                st.write(f"**💰 ${row['price']:,}** - جودة {row['quality_score']}% - Attack {row['attack']} - Critical {row['critical']}%")
                st.caption(f"👤 البائع: {row['user']} | 🕐 {row['time_ago']}")
    else:
        st.warning("❌ لا توجد صفقات تحقق شروط التنبيه حالياً")

# ========== TAB 5: تحليلات ==========
with tab5:
    st.subheader("📈 تحليلات متقدمة")
    
    fig_scatter = px.scatter(
        df_filtered,
        x='price',
        y='quality_score',
        size='attack',
        color='critical',
        hover_data=['user', 'value_for_money'],
        title='العلاقة بين السعر وجودة الطائرة',
        labels={'price': 'السعر ($)', 'quality_score': 'الجودة (%)'}
    )
    fig_scatter.update_layout(template='plotly_dark')
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_hist_price = px.histogram(df_filtered, x='price', nbins=30, title='توزيع الأسعار')
        fig_hist_price.update_layout(template='plotly_dark')
        st.plotly_chart(fig_hist_price, use_container_width=True)
    
    with col2:
        fig_hist_quality = px.histogram(df_filtered, x='quality_score', nbins=20, title='توزيع الجودة')
        fig_hist_quality.update_layout(template='plotly_dark')
        st.plotly_chart(fig_hist_quality, use_container_width=True)

# ========== التوصية النهائية ==========
st.divider()
st.subheader("🎯 التوصية النهائية")

good_deals = df_filtered[df_filtered['quality_score'] >= 60]
if len(good_deals) > 0:
    best_recommendation = good_deals.loc[good_deals['value_for_money'].idxmax()]
    st.success(f"""
    ✅ **أفضل صفقة حالياً (جودة عالية + سعر مناسب):**
    - 💰 سعر الشراء: ${best_recommendation['price']:,} (منذ {best_recommendation['time_ago']})
    - ⚔️ Attack: {best_recommendation['attack']} / 300
    - 🎯 Critical: {best_recommendation['critical']}% / 50%
    - 📊 جودة الطائرة: {best_recommendation['quality_score']}%
    - 👤 البائع: {best_recommendation['user']}
    """)
else:
    st.warning("⚠️ لا توجد طائرات بجودة عالية حالياً (جودة ≥ 60%)")