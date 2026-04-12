import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="TF家族四代练习生寻艺数据看板",
    layout="wide",
    page_icon="📊"
)

# 自定义 CSS：手机纵向卡片样式
st.markdown("""
<style>
    /* 全局适配手机 */
    .main .block-container {
        padding-left: 0.8rem;
        padding-right: 0.8rem;
        max-width: 100%;
    }

    /* 卡片纵向排列 */
    .vertical-card {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        transition: 0.2s;
    }

    .card-header {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #212529;
    }

    .big-number {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0.2rem 0;
        color: #1f77b4;
        display: inline-block;
    }

    .diff {
        font-size: 0.9rem;
        margin-left: 0.8rem;
        font-weight: 500;
    }

    .diff-positive {
        color: #28a745;
    }

    .diff-negative {
        color: #dc3545;
    }

    .diff-zero {
        color: #6c757d;
    }

    .info-row {
        display: flex;
        justify-content: space-between;
        margin-top: 0.5rem;
        font-size: 0.85rem;
        color: #495057;
        border-top: 1px solid #e9ecef;
        padding-top: 0.5rem;
    }

    .info-item {
        text-align: center;
        flex: 1;
    }

    .info-label {
        font-size: 0.7rem;
        color: #6c757d;
    }

    .info-value {
        font-weight: 600;
        font-size: 0.9rem;
    }

    .percent-bar {
        background-color: #e9ecef;
        border-radius: 10px;
        overflow: hidden;
        margin: 6px 0;
    }

    .bar1 { background-color: #1f77b4; height: 6px; }
    .bar2 { background-color: #ff7f0e; height: 6px; }
    .bar3 { background-color: #2ca02c; height: 6px; }

    .stat-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        margin-top: 4px;
        color: #495057;
    }

    hr {
        margin: 0.6rem 0;
    }

    .timestamp {
        font-size: 0.65rem;
        color: #adb5bd;
        text-align: right;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 寻艺数据")

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv("xunyi_likes_summary.csv")
    df["时间"] = pd.to_datetime(df["时间"])
    return df

# 手动刷新按钮
if st.button("🔄 立即刷新数据"):
    load_data.clear()
    st.rerun()

try:
    df = load_data()
except FileNotFoundError:
    st.error("未找到数据文件，请先运行采集脚本生成 xunyi_likes_summary.csv")
    st.stop()
except Exception as e:
    st.error(f"读取数据失败：{e}")
    st.stop()

# 显示真实数据最新时间，而不是页面运行时间
latest_data_time = df["时间"].max()
st.caption(f"数据最新时间：{latest_data_time.strftime('%Y-%m-%d %H:%M:%S')}")

# 侧边栏筛选
st.sidebar.header("🔍 筛选练习生")
all_artists = sorted(df["练习生"].dropna().unique().tolist())
selected_artists = st.sidebar.multiselect("选择练习生", all_artists, default=all_artists)

filtered_df = df[df["练习生"].isin(selected_artists)]

# 获取每个练习生的最新数据和上一次数据
latest_with_diff = []
for artist in selected_artists:
    artist_df = filtered_df[filtered_df["练习生"] == artist].sort_values("时间")
    if len(artist_df) >= 2:
        latest = artist_df.iloc[-1]
        prev = artist_df.iloc[-2]
        diff = latest["总点赞量"] - prev["总点赞量"]
    elif len(artist_df) == 1:
        latest = artist_df.iloc[-1]
        diff = 0
    else:
        continue
    latest_with_diff.append((latest, diff))

# 按总点赞量排序
latest_with_diff.sort(key=lambda x: x[0]["总点赞量"], reverse=True)

if not latest_with_diff:
    st.warning("当前没有可展示的练习生数据，请检查筛选条件。")
    st.stop()

# 渲染卡片
for row, diff in latest_with_diff:
    today_participants = row["点赞1次人数"] + row["点赞2次人数"] + row["点赞3次人数"]

    p1 = row["点赞1次人数"] / today_participants * 100 if today_participants > 0 else 0
    p2 = row["点赞2次人数"] / today_participants * 100 if today_participants > 0 else 0
    p3 = row["点赞3次人数"] / today_participants * 100 if today_participants > 0 else 0

    if diff > 0:
        diff_html = f'<span class="diff diff-positive">▲ +{diff:,}</span>'
    elif diff < 0:
        diff_html = f'<span class="diff diff-negative">▼ {diff:,}</span>'
    else:
        diff_html = '<span class="diff diff-zero">→ 0</span>'

    st.markdown(f"""
<div class="vertical-card">
    <div class="card-header">{row['练习生']}</div>
    <div>
        <span class="big-number">{row['总点赞量']:,}</span>
        {diff_html}
    </div>

    <div class="info-row">
        <div class="info-item">
            <div class="info-label">粉丝总数</div>
            <div class="info-value">{row['粉丝数']:,}</div>
        </div>
        <div class="info-item">
            <div class="info-label">今日参与人数</div>
            <div class="info-value">{today_participants:,}</div>
        </div>
    </div>

    <hr>

    <div style="font-weight:500; font-size:0.8rem;">点赞次数分布</div>

    <div class="percent-bar">
        <div class="bar1" style="width:{p1:.1f}%;"></div>
    </div>
    <div class="stat-row">
        <span>🔹 1次：{row['点赞1次人数']:,} ({p1:.1f}%)</span>
    </div>

    <div class="percent-bar">
        <div class="bar2" style="width:{p2:.1f}%;"></div>
    </div>
    <div class="stat-row">
        <span>🔸 2次：{row['点赞2次人数']:,} ({p2:.1f}%)</span>
    </div>

    <div class="percent-bar">
        <div class="bar3" style="width:{p3:.1f}%;"></div>
    </div>
    <div class="stat-row">
        <span>🔹 3次：{row['点赞3次人数']:,} ({p3:.1f}%)</span>
    </div>

    <div class="timestamp">数据时间：{row['时间'].strftime('%Y-%m-%d %H:%M')}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("注：今日参与人数 = 至少点赞1次的历史总人数（check1+check2+check3），实际为累计值。点赞次数分布展示不同深度点赞人数的占比。")