import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="TF家族四代练习生寻艺数据看板",
    layout="wide",
    page_icon="📊"
)

st.title("📈 寻艺数据")


@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv("xunyi_likes_summary.csv")
    df["时间"] = pd.to_datetime(df["时间"])
    return df


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

latest_data_time = df["时间"].max()
st.caption(f"数据最新时间：{latest_data_time.strftime('%Y-%m-%d %H:%M:%S')}")

st.sidebar.header("🔍 筛选练习生")
all_artists = sorted(df["练习生"].dropna().unique().tolist())
selected_artists = st.sidebar.multiselect("选择练习生", all_artists, default=all_artists)

filtered_df = df[df["练习生"].isin(selected_artists)]

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

latest_with_diff.sort(key=lambda x: x[0]["总点赞量"], reverse=True)

if not latest_with_diff:
    st.warning("当前没有可展示的练习生数据，请检查筛选条件。")
    st.stop()

for row, diff in latest_with_diff:
    today_participants = row["点赞1次人数"] + row["点赞2次人数"] + row["点赞3次人数"]

    p1 = row["点赞1次人数"] / today_participants if today_participants > 0 else 0
    p2 = row["点赞2次人数"] / today_participants if today_participants > 0 else 0
    p3 = row["点赞3次人数"] / today_participants if today_participants > 0 else 0

    with st.container(border=True):
        st.subheader(row["练习生"])

        col1, col2 = st.columns([3, 2])
        with col1:
            st.metric(
                label="总点赞量",
                value=f"{int(row['总点赞量']):,}",
                delta=f"{int(diff):,}"
            )
        with col2:
            st.metric(
                label="粉丝总数",
                value=f"{int(row['粉丝数']):,}"
            )

        st.metric(
            label="今日参与人数",
            value=f"{int(today_participants):,}"
        )

        st.write("**点赞次数分布**")
        st.write(f"1次：{int(row['点赞1次人数']):,}（{p1 * 100:.1f}%）")
        st.progress(float(p1))

        st.write(f"2次：{int(row['点赞2次人数']):,}（{p2 * 100:.1f}%）")
        st.progress(float(p2))

        st.write(f"3次：{int(row['点赞3次人数']):,}（{p3 * 100:.1f}%）")
        st.progress(float(p3))

        st.caption(f"数据时间：{row['时间'].strftime('%Y-%m-%d %H:%M')}")

st.markdown("---")
st.caption("注：今日参与人数 = 至少点赞1次的历史总人数（check1+check2+check3），实际为累计值。点赞次数分布展示不同深度点赞人数的占比。")
