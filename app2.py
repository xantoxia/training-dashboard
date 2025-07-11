import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="人员培训多维分析", layout="wide")
st.title("📈 人员培训与多样性增强分析仪表板")

uploaded_file = st.file_uploader("📤 上传 Excel 文件", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        df.columns = df.columns.str.strip()

        # 数据预处理
        df["年龄"] = pd.to_numeric(df["年龄"], errors="coerce")
        df["年资"] = pd.to_numeric(df["年资"], errors="coerce")
        df["是否学习"] = df["是否学习"].astype(str)
        df["性别"] = df["性别"].astype(str)
        df["学历"] = df["学历"].astype(str)
        df["残疾类别"] = df["残疾类别"].fillna("未标注").astype(str)
        df["事业群"] = df["事业群"].astype(str)
        df["厂区"] = df["厂区"].astype(str)
        df["管理职"] = df["管理职"].astype(str)
        df["资位"] = df["资位"].astype(str)

        # 基本概况
        total = len(df)
        learned = len(df[df["是否学习"].str.contains("是")])
        female_pct = round((df["性别"].str.contains("女").sum() / total) * 100, 1)
        with st.container():
            col1, col2, col3 = st.columns(3)
            col1.metric("👥 总人数", total)
            col2.metric("📘 已学习人数", learned)
            col3.metric("♀️ 女性占比", f"{female_pct}%")

        st.divider()

        # 多维可视化
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 基础分布", 
            "🏢 事业群与厂区分析", 
            "🧑‍💼 管理职/资位分析", 
            "♿ 残疾类别与培训"
        ])

        # 基础分布图
        with tab1:
            st.subheader("📌 基本分布情况")
            col1, col2 = st.columns(2)
            with col1:
                fig1 = px.histogram(df, x="学历", color="是否学习", barmode="group", title="学历与是否学习")
                st.plotly_chart(fig1, use_container_width=True)
            with col2:
                fig2 = px.box(df, x="是否学习", y="年资", points="all", title="年资与是否学习")
                st.plotly_chart(fig2, use_container_width=True)

            col3, col4 = st.columns(2)
            with col3:
                fig3 = px.histogram(df, x="性别", color="是否学习", barmode="group", title="性别与是否学习")
                st.plotly_chart(fig3, use_container_width=True)
            with col4:
                fig4 = px.histogram(df, x="年龄", nbins=20, title="年龄分布")
                st.plotly_chart(fig4, use_container_width=True)

        # 事业群 & 厂区分析
        with tab2:
            st.subheader("🏭 各事业单位与厂区学习情况")
            fig5 = px.histogram(df, x="事业群", color="是否学习", barmode="group", title="事业群 vs 是否学习")
            st.plotly_chart(fig5, use_container_width=True)

            fig6 = px.histogram(df, x="厂区", color="是否学习", barmode="group", title="厂区 vs 是否学习")
            st.plotly_chart(fig6, use_container_width=True)

        # 管理职分析
        with tab3:
            st.subheader("👔 管理职与资位分析")
            col5, col6 = st.columns(2)
            with col5:
                fig7 = px.histogram(df, x="管理职", color="是否学习", barmode="group", title="管理职 vs 是否学习")
                st.plotly_chart(fig7, use_container_width=True)
            with col6:
                fig8 = px.histogram(df, x="资位", color="是否学习", barmode="group", title="资位 vs 是否学习")
                st.plotly_chart(fig8, use_container_width=True)

        # 残疾类别分析
        with tab4:
            st.subheader("♿ 残疾类别相关分析")
            fig9 = px.pie(df, names="残疾类别", title="残疾类别分布")
            st.plotly_chart(fig9, use_container_width=True)

            fig10 = px.histogram(df, x="残疾类别", color="是否学习", barmode="group", title="残疾类别 vs 是否学习")
            st.plotly_chart(fig10, use_container_width=True)

        st.divider()
        st.subheader("📄 原始数据预览")
        st.dataframe(df)

    except Exception as e:
        st.error(f"❌ 出错了：{e}")
else:
    st.info("请上传包含完整字段的 Excel 文件，如：工号、是否学习、性别、学历、年资、事业群、残疾类别等。")
