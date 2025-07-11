import streamlit as st
import pandas as pd
import plotly.express as px

st.write("🚀 App is loading")

st.set_page_config(page_title="培训情况分析", layout="wide")
st.title("👥 人员培训与多样性分析仪表板")

uploaded_file = st.file_uploader("📤 上传 Excel 文件", type=["xlsx"])
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')

        st.success("✅ 文件上传成功！")

        # 字段标准化（可根据你的 Excel 表头修改）
        df.columns = df.columns.str.strip()

        # 主要字段处理
        df["年龄"] = pd.to_numeric(df["年龄"], errors="coerce")
        df["年资"] = pd.to_numeric(df["年资"], errors="coerce")
        df["是否学习"] = df["是否学习"].astype(str)
        df["性别"] = df["性别"].astype(str)
        df["学历"] = df["学历"].astype(str)
        df["残疾类别"] = df["残疾类别"].fillna("未标注").astype(str)

        # 概览
        total = len(df)
        learned = len(df[df["是否学习"].str.contains("是")])
        female_pct = round((df["性别"].str.contains("女").sum() / total) * 100, 1)

        col1, col2, col3 = st.columns(3)
        col1.metric("👥 总人数", total)
        col2.metric("📘 已学习人数", learned)
        col3.metric("♀️ 女性占比", f"{female_pct}%")

        st.divider()

        # 多图展示
        st.subheader("📊 数据分布可视化")

        tab1, tab2, tab3 = st.tabs(["性别与学习情况", "学历与年资", "残疾类别分布"])

        with tab1:
            fig1 = px.histogram(df, x="性别", color="是否学习", barmode="group", title="性别与是否学习")
            st.plotly_chart(fig1, use_container_width=True)

            fig2 = px.histogram(df, x="是否学习", title="是否学习人数分布")
            st.plotly_chart(fig2, use_container_width=True)

        with tab2:
            fig3 = px.histogram(df, x="学历", color="是否学习", barmode="group", title="学历分布")
            st.plotly_chart(fig3, use_container_width=True)

            fig4 = px.histogram(df, x="年资", nbins=20, title="年资分布")
            st.plotly_chart(fig4, use_container_width=True)

        with tab3:
            fig5 = px.pie(df, names="残疾类别", title="残疾类别占比")
            st.plotly_chart(fig5, use_container_width=True)

        st.divider()
        st.subheader("📄 原始数据预览")
        st.dataframe(df)

    except Exception as e:
        st.error(f"❌ 加载文件出错：{e}")
else:
    st.info("请上传包含完整字段的 Excel 文件，例如：工号、姓名、是否学习、性别、年龄、学历、残疾类别等。")

