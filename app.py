import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="TF家族四代练习生寻艺数据看板", layout="wide")
st.title("📈 TF家族四代练习生寻艺数据看板")
st.caption("数据每日自动更新 | 基于寻艺小程序官方数据接口")

@st.cache_data(ttl=1800)   # 30分钟缓存，配合自动更新
def load_data():
    df = pd.read_csv("xunyi_likes_summary.csv")
    df['时间'] = pd.to_datetime(df['时间'])
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("未找到数据文件，请先运行数据采集脚本生成 xunyi_likes_summary.csv")
    st.stop()

st.sidebar.header("🔍 筛选练习生")
all_artists = df['练习生'].unique().tolist()
selected_artists = st.sidebar.multiselect("选择你想查看的练习生", all_artists, default=all_artists)
filtered_df = df[df['练习生'].isin(selected_artists)]

# 获取每个练习生的最新数据和上一次数据（用于计算增量）
latest_list = []
for artist in selected_artists:
    artist_df = filtered_df[filtered_df['练习生'] == artist].sort_values('时间')
    if len(artist_df) >= 2:
        latest = artist_df.iloc[-1]
        prev = artist_df.iloc[-2]
        diff = latest['总点赞量'] - prev['总点赞量']
    elif len(artist_df) == 1:
        latest = artist_df.iloc[-1]
        diff = 0
    else:
        continue
    latest_list.append((latest, diff))

# 卡片式布局
st.subheader("📊 练习生数据卡片（最新）")
cols = st.columns(3)
for idx, (row, diff) in enumerate(latest_list):
    with cols[idx % 3]:
        # 计算累计参与人数
        total_participants = row['点赞1次人数'] + row['点赞2次人数'] + row['点赞3次人数']
        diff_color = "green" if diff > 0 else "gray"
        diff_sign = "+" if diff > 0 else ""
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 1rem; margin-bottom: 1rem;">
            <h3 style="margin: 0;">{row['练习生']}</h3>
            <p style="font-size: 2rem; font-weight: bold; margin: 0;">{row['总点赞量']:,}</p>
            <p style="color: {diff_color};">较上次 {diff_sign}{diff}</p>
            <p>👍 总点赞量</p>
            <hr>
            <p>👥 粉丝数：{row['粉丝数']:,}</p>
            <p>⭐ 累计参与人数：{total_participants:,}</p>
            <p style="font-size: 0.8rem; color: gray;">（至少点赞1次的历史总人数）</p>
        </div>
        """, unsafe_allow_html=True)

# 趋势图
st.subheader("📈 总点赞量趋势")
fig_total = px.line(filtered_df, x='时间', y='总点赞量', color='练习生',
                    title='各练习生寻艺总点赞量变化趋势', markers=True,
                    labels={'总点赞量': '点赞量', '时间': '日期'})
st.plotly_chart(fig_total, use_container_width=True)

# 数据表格（增加累计参与人数列）
st.subheader("📋 详细数据表")
table_df = filtered_df.copy()
table_df['累计参与人数'] = table_df['点赞1次人数'] + table_df['点赞2次人数'] + table_df['点赞3次人数']
st.dataframe(table_df.sort_values('时间', ascending=False), use_container_width=True)