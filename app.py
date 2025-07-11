# training_dashboard/app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.formula.api import logit
import statsmodels.api as sm
import numpy as np

st.set_page_config(page_title="多维培训分析仪表板", layout="wide")
st.title("📊 培训学习行为多维分析")

uploaded_file = st.file_uploader("📤 上传包含完整字段的 Excel 文件", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    df.columns = df.columns.str.strip()

    # 预处理
    df.dropna(subset=["是否学习"], inplace=True)
    df["是否学习"] = df["是否学习"].astype(str)
    df["年龄"] = pd.to_numeric(df["年龄"], errors="coerce")
    df["年资"] = pd.to_numeric(df["年资"], errors="coerce")
    df["性别"] = df["性别"].astype(str)
    df["学历"] = df["学历"].astype(str)
    df["残疾类别"] = df["残疾类别"].fillna("未标注")

    st.success("✅ 数据读取成功！")

    # -----------------------------------
    # 基础概况面板
    # -----------------------------------
    st.subheader("👥 总体概况")
    col1, col2, col3 = st.columns(3)
    total = len(df)
    learned = len(df[df["是否学习"].str.contains("是")])
    female_pct = round((df["性别"].str.contains("女").sum() / total) * 100, 1)
    col1.metric("👥 总人数", total)
    col2.metric("📘 已学习人数", learned)
    col3.metric("♀️ 女性占比", f"{female_pct}%")

    st.divider()

    # -----------------------------------
    # 交叉分析模块
    # -----------------------------------
    st.subheader("🔁 多维交叉变量分析")
    cat_vars = ["性别", "学历", "事业群", "厂区", "管理职"]
    selected_x = st.selectbox("选择 X（横轴）变量", cat_vars)
    selected_hue = st.selectbox("选择颜色分组变量", cat_vars, index=1)

    fig1 = px.histogram(df, x=selected_x, color=selected_hue, barmode="group", facet_col="是否学习")
    st.plotly_chart(fig1, use_container_width=True)

    # -----------------------------------
    # 显著性差异分析（t检验 / 卡方检验）
    # -----------------------------------
    st.subheader("📐 显著性差异分析")

    st.markdown("#### 🎯 数值型变量 t 检验")
    for col in ["年龄", "年资"]:
        group1 = df[df["是否学习"].str.contains("是")][col].dropna()
        group2 = df[df["是否学习"].str.contains("否")][col].dropna()
        t_stat, p_val = stats.ttest_ind(group1, group2, equal_var=False)
        st.write(f"🔹 **{col}** 的 t 检验：学习者均值 = {group1.mean():.2f}，未学习者均值 = {group2.mean():.2f}，p = {p_val:.4f}")

    st.markdown("#### 🧪 分类变量 卡方检验")
    for cat in cat_vars:
        cross_tab = pd.crosstab(df[cat], df["是否学习"])
        chi2, p, dof, ex = stats.chi2_contingency(cross_tab)
        st.write(f"🔹 **{cat}** 与 是否学习：卡方统计量 = {chi2:.2f}，p = {p:.4f}")

    # -----------------------------------
    # Logistic 回归分析
    # -----------------------------------
    st.subheader("📈 回归分析：预测是否学习")

    df_reg = df[["是否学习", "年龄", "年资", "性别", "学历", "事业群", "厂区", "管理职"]].dropna()
    df_reg = df_reg[df_reg["是否学习"].isin(["是", "否"])]
    df_reg["是否学习"] = df_reg["是否学习"].map({"是": 1, "否": 0})
    df_reg = pd.get_dummies(df_reg, drop_first=True)

    X = df_reg.drop("是否学习", axis=1)
    y = df_reg["是否学习"]
    X = sm.add_constant(X)
    model = sm.Logit(y, X).fit(disp=0)

    st.markdown("#### 回归结果摘要")
    st.text(model.summary())

    st.markdown("#### 回归系数（影响方向与强度）")
    coef_df = model.params[1:].sort_values()
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    coef_df.plot(kind="barh", ax=ax2)
    st.pyplot(fig2)

else:
    st.info("请上传包含字段如：工号、姓名、是否学习、性别、年龄、年资、学历、事业群、厂区、管理职等的 Excel 文件。")
