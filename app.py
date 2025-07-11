import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="培训情况分析", layout="wide")
st.title("👥 人员培训与多样性分析仪表板")

uploaded_file = st.file_uploader("📤 上传 Excel 文件", type=["xlsx"])
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.success("✅ 文件上传成功！")

        # 清洗 & 标准化字段
        df.columns = df.columns.str.strip()
        df["年龄"] = pd.to_numeric(df["年龄"], errors="coerce")
        df["年资"] = pd.to_numeric(df["年资"], errors="coerce")
        df["是否学习"] = df["是否学习"].astype(str)
        df["性别"] = df["性别"].astype(str)
        df["学历"] = df["学历"].astype(str)
        df["残疾类别"] = df["残疾类别"].fillna("未标注").astype(str)

        # 基本概况统计
        total = len(df)
        learned = len(df[df["是否学习"].str.contains("是")])
        female_pct = round((df["性别"].str.contains("女").sum() / total) * 100, 1)
        learn_rate = round((learned / total) * 100, 1)

        col1, col2, col3 = st.columns(3)
        col1.metric("👥 总人数", total)
        col2.metric("📘 已学习人数", learned)
        col3.metric("♀️ 女性占比", f"{female_pct}%")

        st.divider()

        # 🎯 分析摘要
        learn_rate_by_edu = df.groupby("学历")["是否学习"].apply(lambda x: (x.str.contains("是").sum() / len(x)) * 100)
        high_risk_group = learn_rate_by_edu.idxmin()
        low_rate = learn_rate_by_edu.min()

        st.markdown("### 📃 分析摘要报告")
        st.markdown(f"""
        - 本次数据共计 **{total}** 人，学习率为 **{learn_rate}%**。
        - 女性员工占比为 **{female_pct}%**。
        - 学历层级中，学习率最低的是 **{high_risk_group}**，仅为 **{low_rate:.1f}%**，建议重点关注。
        """)

        st.divider()

        # 📊 图表展示
        st.subheader("📊 数据可视化")
        tab1, tab2, tab3, tab4 = st.tabs(["性别与学习", "学历与年资", "残疾类别", "未学习画像"])

        with tab1:
            st.plotly_chart(px.histogram(df, x="性别", color="是否学习", barmode="group", title="性别与是否学习"), use_container_width=True)
            st.plotly_chart(px.histogram(df, x="是否学习", title="是否学习人数分布"), use_container_width=True)

        with tab2:
            st.plotly_chart(px.histogram(df, x="学历", color="是否学习", barmode="group", title="学历分布"), use_container_width=True)
            st.plotly_chart(px.histogram(df, x="年资", nbins=20, title="年资分布"), use_container_width=True)

        with tab3:
            st.plotly_chart(px.pie(df, names="残疾类别", title="残疾类别占比"), use_container_width=True)
            st.plotly_chart(px.histogram(df, x="残疾类别", color="是否学习", barmode="group", title="残疾类别与学习情况"), use_container_width=True)

        with tab4:
            st.markdown("#### 🎯 未学习人群学历分布")
            not_learned = df[df["是否学习"].str.contains("否")]
            edu_dist = not_learned["学历"].value_counts()
            st.bar_chart(edu_dist)

            st.markdown("#### 🎯 未学习人群按残疾类别")
            dis_dist = not_learned["残疾类别"].value_counts()
            st.bar_chart(dis_dist)

        st.divider()
        st.subheader("📄 原始数据预览")
        st.dataframe(df)

    except Exception as e:
        st.error(f"❌ 加载文件出错：{e}")
else:
    st.info("请上传包含完整字段的 Excel 文件，例如：工号、姓名、是否学习、性别、年龄、学历、年资、残疾类别等。")
