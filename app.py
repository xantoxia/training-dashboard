import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="培训情况分析", layout="wide")
st.title("👥 人员培训与多样性分析仪表板（增强版）")

uploaded_file = st.file_uploader("📤 上传 Excel 文件", type=["xlsx"])
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.success("✅ 文件上传成功！")

        df.columns = df.columns.str.strip()

        # 类型转换
        df["年龄"] = pd.to_numeric(df["年龄"], errors="coerce")
        df["年资"] = pd.to_numeric(df["年资"], errors="coerce")
        df["是否学习"] = df["是否学习"].astype(str)
        df["性别"] = df["性别"].astype(str)
        df["学历"] = df["学历"].astype(str)
        df["残疾类别"] = df["残疾类别"].fillna("未标注").astype(str)
        df["管理职"] = df["管理职"].fillna("无").astype(str)
        df["事业群"] = df["事业群"].astype(str)
        df["厂区"] = df["厂区"].astype(str)

        # 概览
        total = len(df)
        learned = len(df[df["是否学习"].str.contains("是")])
        female_pct = round((df["性别"].str.contains("女").sum() / total) * 100, 1)

        col1, col2, col3 = st.columns(3)
        col1.metric("👥 总人数", total)
        col2.metric("📘 已学习人数", learned)
        col3.metric("♀️ 女性占比", f"{female_pct}%")

        st.divider()

        # 可视化分析
        st.subheader("📊 数据分布分析")
        tab1, tab2, tab3, tab4 = st.tabs(["性别与学习", "学历与年资", "残疾类别", "事业群与管理层"])

        with tab1:
            fig1 = px.histogram(df, x="性别", color="是否学习", barmode="group", title="性别与是否学习")
            st.plotly_chart(fig1, use_container_width=True)
            
            st.markdown("""
            **📌 解读：**
            - 比较男女员工的学习参与率，发现性别是否影响培训参与。
            - 可观察某一性别是否存在明显的学习缺口，推动有针对性的提升策略。
            """)

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                fig2 = px.histogram(df, x="学历", color="是否学习", barmode="group", title="学历分布")
                st.plotly_chart(fig2, use_container_width=True)
            with col2:
                fig3 = px.box(df, x="是否学习", y="年资", points="all", title="年资与是否学习")
                st.plotly_chart(fig3, use_container_width=True)
                st.markdown("""
                **🔍 年资箱型图解读：**
                - 箱体位置越高，说明年资越高。
                - 若“已学习”群体中位数更高，表示资深员工更愿意参加培训。
                - 可见离群点（小圆点）表示年资极高或极低但与主趋势不同的群体。
                - 有助于发现：是否存在高年资未培训、或新人积极参与培训的群体。
                """)

        with tab3:
            fig4 = px.pie(df, names="残疾类别", title="残疾类别占比")
            st.plotly_chart(fig4, use_container_width=True)

            st.markdown("""
            **🧩 残疾类别分布说明：**
            - 帮助识别企业内部多样性情况。
            - 若某类别占比高，需评估是否获得合理的培训资源与辅助工具。
            """)

        with tab4:
            fig5 = px.histogram(df, x="事业群", color="是否学习", barmode="group", title="各事业群学习参与情况")
            st.plotly_chart(fig5, use_container_width=True)

            fig6 = px.histogram(df, x="管理职", color="是否学习", barmode="group", title="管理职是否学习")
            st.plotly_chart(fig6, use_container_width=True)

            st.markdown("""
            **🏢 部门与管理层分析说明：**
            - 事业群间存在培训参与差异，便于发现需重点推动区域。
            - 管理职参与度是衡量企业学习文化传导是否到位的重要参考。
            """)

        st.divider()

        # 原始数据
        st.subheader("📄 原始数据预览")
        st.dataframe(df)

    except Exception as e:
        st.error(f"❌ 加载文件出错：{e}")
else:
    st.info("请上传包含完整字段的 Excel 文件，例如：工号、姓名、是否学习、性别、年龄、学历、残疾类别、事业群、厂区、管理职、年资等。")
