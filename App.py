import streamlit as st
import pandas as pd
import plotly.express as px

# --- تغيير لون خلفية الصفحة وخطوط عامة + ألوان الفلاتر ---
st.markdown(
    """
    <style>
    .stApp {background-color: #0D0D0D; color: #FFFFFF;}
    [data-testid="stSidebar"] {background-color: #2C2C2C; color: #FFFFFF; font-family: Arial, sans-serif;}
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] h2 {color: #A8D5BA; font-weight:bold;}
    div[role="listbox"] {background-color: #3A3A3A !important; color:#A8D5BA !important;}
    div[role="combobox"] > div > div > div {color:#A8D5BA !important;}
    .dataframe th {background-color:#1F3D2F; color:white; text-align:center;}
    .dataframe td {background-color:#262626; color:white; text-align:center;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- عنوان الداشبورد ---
st.markdown("<h2 style='text-align:center;color:#A8D5BA;font-family:Arial,sans-serif;'>تقرير بيانات تكاليف الصيانة</h2>", unsafe_allow_html=True)

# --- قراءة البيانات ---
file_path = r"C:\Users\vooxn\OneDrive\Desktop\Dashboard_Data\تكاليف الصيانة(2).xlsx"
df = pd.read_excel(file_path)

# --- تنظيف البيانات ---
df.columns = df.columns.str.strip()
for col in ["تكرار الاعطالي","2023","2024","2025"]:
    df[col] = df.groupby("موديل المركبة")[col].transform(lambda x: x.fillna(x.mean()))
df = df.dropna(subset=["الفرع","نوع المركبة","موديل المركبة","حرف اللوحة","رقم اللوحة"])

# --- Sidebar Filters مع خيار "الكل" ---
st.sidebar.header("📌 الفلاتر")
branches_options = ["الكل"] + list(df["الفرع"].unique())
selected_branches = st.sidebar.multiselect("اختر الفرع", options=branches_options, default="الكل")

models_options = ["الكل"] + list(df["موديل المركبة"].unique())
selected_models = st.sidebar.multiselect("اختر موديل المركبة", options=models_options, default="الكل")

years_options = ["الكل","2023","2024","2025"]
selected_years = st.sidebar.multiselect("اختر السنة", options=years_options, default="الكل")

# --- تحويل "الكل" إلى كل القيم قبل الفلترة ---
if "الكل" in selected_branches:
    selected_branches = df["الفرع"].unique()
if "الكل" in selected_models:
    selected_models = df["موديل المركبة"].unique()
if "الكل" in selected_years:
    selected_years = ["2023","2024","2025"]

# --- تحويل البيانات إلى long format لتسهيل فلترة السنوات ---
df_long = df.melt(
    id_vars=["الفرع","نوع المركبة","موديل المركبة","تكرار الاعطالي","رقم اللوحة","حرف اللوحة"],
    value_vars=["2023","2024","2025"],
    var_name="السنة",
    value_name="التكلفة"
)

# --- فلترة البيانات ---
filtered_df = df_long[
    (df_long["الفرع"].isin(selected_branches)) &
    (df_long["موديل المركبة"].isin(selected_models)) &
    (df_long["السنة"].isin(selected_years))
]

# --- KPIs ---
total_cost = filtered_df["التكلفة"].sum()
total_breakdowns = filtered_df["تكرار الاعطالي"].sum()
avg_breakdowns = filtered_df["تكرار الاعطالي"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("💰 إجمالي التكلفة", f"{total_cost:,.0f}")
col2.metric("🛠 إجمالي الأعطال", f"{total_breakdowns:,.0f}")
col3.metric("📊 متوسط الأعطال", f"{avg_breakdowns:,.1f}")

st.markdown("---")

# --- Charts ---
col1, col2 = st.columns(2)

# Bar Chart - تكلفة حسب الفرع
branch_cost = filtered_df.groupby("الفرع")["التكلفة"].sum().reset_index()
fig_bar = px.bar(branch_cost, x="الفرع", y="التكلفة", color="الفرع",
                 color_discrete_sequence=px.colors.sequential.Greens,
                 title="💰 تكلفة حسب الفرع")
fig_bar.update_layout(plot_bgcolor='#0D0D0D', paper_bgcolor='#0D0D0D',
                      font=dict(color='#A8D5BA'), title_font=dict(color='#A8D5BA'))

# Line Chart - تطور التكاليف
fig_line = px.line(filtered_df, x="السنة", y="التكلفة", color="الفرع", markers=True,
                   color_discrete_sequence=px.colors.sequential.Greens,
                   title="📈 تطور التكاليف")
fig_line.update_layout(plot_bgcolor='#0D0D0D', paper_bgcolor='#0D0D0D',
                       font=dict(color='#A8D5BA'), title_font=dict(color='#A8D5BA'))

# Pie Chart - توزيع الأعطال حسب نوع المركبة
breakdowns_type = filtered_df.groupby("نوع المركبة")["تكرار الاعطالي"].sum().reset_index()
fig_pie = px.pie(breakdowns_type, names="نوع المركبة", values="تكرار الاعطالي",
                 color_discrete_sequence=px.colors.sequential.Greens,
                 title="🛠 توزيع الأعطال حسب نوع المركبة")
fig_pie.update_layout(plot_bgcolor='#0D0D0D', paper_bgcolor='#0D0D0D',
                      font=dict(color='#A8D5BA'), title_font=dict(color='#A8D5BA'))

# Top 5 Vehicles
top_vehicles = filtered_df.groupby("نوع المركبة")["تكرار الاعطالي"].sum().sort_values(ascending=False).head(5).reset_index()
fig_top5 = px.bar(top_vehicles, x="نوع المركبة", y="تكرار الاعطالي", color="نوع المركبة",
                  color_discrete_sequence=px.colors.sequential.Greens,
                  title="🔥 أعلى 5 مركبات من حيث الأعطال")
fig_top5.update_layout(plot_bgcolor='#0D0D0D', paper_bgcolor='#0D0D0D',
                       font=dict(color='#A8D5BA'), title_font=dict(color='#A8D5BA'))

# Map
branch_locations = {
    "تبوك": [28.3838, 36.5662],
    "الجوف": [29.9539, 40.1970],
    "حائل": [27.5236, 41.6966],
    "جازان": [16.8833, 42.5500],
    "الشرقية": [26.4333, 50.1000],
    "القصيم": [26.3167, 43.9833],
    "عسير": [18.2208, 42.5053],
    "الحدود الشمالية": [30.9833, 41.0167],
    "الباحة": [20.0122, 41.4677],
    "الرياض": [24.7743, 46.7386],
    "مكة المكرمة": [21.4225, 39.8233],
    "المدينة المنورة": [24.4700, 39.6100],
    "نجران": [17.4931, 44.1596]
}
map_data = filtered_df.groupby("الفرع")["تكرار الاعطالي"].sum().reset_index()
map_data["lat"] = map_data["الفرع"].map(lambda x: branch_locations.get(x, [0,0])[0])
map_data["lon"] = map_data["الفرع"].map(lambda x: branch_locations.get(x, [0,0])[1])
fig_map = px.scatter_mapbox(
    map_data, lat="lat", lon="lon", size="تكرار الاعطالي", hover_name="الفرع",
    hover_data={"lat":False, "lon":False, "تكرار الاعطالي":True},
    color="تكرار الاعطالي", color_continuous_scale=px.colors.sequential.Greens,
    size_max=40, zoom=4, title="🗺️ توزيع الأعطال حسب الفرع"
)
fig_map.update_layout(mapbox_style="open-street-map", plot_bgcolor='#0D0D0D', paper_bgcolor='#0D0D0D',
                      font=dict(color='#A8D5BA'), title_font=dict(color='#A8D5BA'),
                      coloraxis_colorbar=dict(title="عدد الأعطال"))

# --- عرض الشارتات القديمة ---
with col1:
    st.plotly_chart(fig_bar, use_container_width=True)
    st.plotly_chart(fig_top5, use_container_width=True)
with col2:
    st.plotly_chart(fig_line, use_container_width=True)
    st.plotly_chart(fig_pie, use_container_width=True)

# Map منفصل أسفل
st.plotly_chart(fig_map, use_container_width=True)

# --- الرسوم الإضافية ---
st.markdown("---")
st.markdown("<h3 style='color:#A8D5BA'>📌 التحليلات الإضافية</h3>", unsafe_allow_html=True)
col3, col4 = st.columns(2)

# Top 10 أرقام اللوحات حسب الأعطال مع المدينة
top_plates = df.groupby(["رقم اللوحة","الفرع"])["تكرار الاعطالي"].sum().sort_values(ascending=False).reset_index().head(10)
fig_plate = px.bar(
    top_plates,
    x="رقم اللوحة",
    y="تكرار الاعطالي",
    color="رقم اللوحة",
    hover_data=["الفرع"],
    color_discrete_sequence=px.colors.sequential.Greens,
    title="🔢 أعلى 10 أرقام لوحات حسب الأعطال مع المدينة"
)
fig_plate.update_layout(plot_bgcolor='#0D0D0D', paper_bgcolor='#0D0D0D',
                        font=dict(color='#A8D5BA'), title_font=dict(color='#A8D5BA'))

# Top 3 موديلات المركبات حسب الأعطال - أخضر
top_models = df.groupby("موديل المركبة")["تكرار الاعطالي"].sum().sort_values(ascending=False).head(3).reset_index()
fig_model = px.bar(
    top_models,
    x="موديل المركبة",
    y="تكرار الاعطالي",
    color="موديل المركبة",
    color_discrete_sequence=px.colors.sequential.Greens,  # تعديل اللون ليكون أخضر
    title="🚗 أعلى 3 موديلات مركبات حسب الأعطال"
)
fig_model.update_layout(plot_bgcolor='#0D0D0D', paper_bgcolor='#0D0D0D',
                        font=dict(color='#A8D5BA'), title_font=dict(color='#A8D5BA'))

with col3:
    st.plotly_chart(fig_plate, use_container_width=True)
with col4:
    st.plotly_chart(fig_model, use_container_width=True)

# --- جدول البيانات كامل الأعمدة ---
st.markdown("---")
st.markdown(
    """
    <div style="
        background-color:#1F3D2F;
        color:white;
        padding:10px;
        border-radius:5px;
        text-align:center;
        font-size:20px;
        font-weight:bold;
        font-family: Arial, sans-serif;
    ">
        جدول البيانات الكامل
    </div>
    """, 
    unsafe_allow_html=True
)
st.dataframe(df.reset_index(drop=True), width=2200, height=600)