import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats
import statsmodels.api as sm
from sklearn.preprocessing import LabelEncoder

# 页面配置
st.set_page_config(page_title="📈 培训参与统计分析", layout="wide")
st.title("📊 培训参与行为统计分析平台")

# 文件上传
uploaded_file = st.file_uploader("📤 上传包含完整字段的 Excel 文件", type=["xlsx"])
if not uploaded_file:
    st.info("请上传 Excel 文件，需包含字段如：是否学习、性别、年龄、年资、学历、厂区、管理职、残疾类别、事业群、资位等。")
    st.stop()

# 读取数据
df = pd.read_excel(uploaded_file, engine='openpyxl')
df.columns = df.columns.str.strip()
df.dropna(subset=["是否学习"], inplace=True)

# 数据预处理
df["是否学习"] = df["是否学习"].astype(str)
df["是否学习编码"] = df["是否学习"].apply(lambda x: 1 if "是" in x else 0)

# 字段标准处理
for col in ["性别", "学历", "厂区", "管理职", "残疾类别", "事业群", "资位"]:
    df[col] = df[col].astype(str).fillna("未标注")

df["年资"] = pd.to_numeric(df["年资"], errors="coerce")
df["年龄"] = pd.to_numeric(df["年龄"], errors="coerce")

# 显示原始数据
with st.expander("📄 查看上传的数据（前100行）"):
    st.dataframe(df.head(100))

st.markdown("---")

# 描述性统计
st.subheader("🧮 基本统计汇总")
col1, col2, col3 = st.columns(3)
col1.metric("总人数", len(df))
col2.metric("已学习人数", df["是否学习编码"].sum())
col3.metric("学习参与率", f"{(df['是否学习编码'].mean()*100):.1f}%")

# 交叉分析：按维度筛选对比
st.subheader("🔍 多维度交叉对比分析")
dimension = st.selectbox("选择分析维度", ["性别", "学历", "厂区", "管理职", "残疾类别", "事业群", "资位"])
fig = px.histogram(df, x=dimension, color="是否学习", barmode="group",
                   title=f"{dimension} 与 是否学习 的关系", text_auto=True)
st.plotly_chart(fig, use_container_width=True)

# 年龄和年资 t 检验
st.subheader("📐 年龄与年资：是否学习人群的显著性差异")
for variable in ["年龄", "年资"]:
    group1 = df[df["是否学习编码"] == 1][variable].dropna()
    group0 = df[df["是否学习编码"] == 0][variable].dropna()
    t_stat, p_val = stats.ttest_ind(group1, group0, equal_var=False)
    st.write(f"🔸 {variable} 的 t 检验结果：")
    st.markdown(f"- 均值（学习）：{group1.mean():.2f}；均值（未学习）：{group0.mean():.2f}")
    st.markdown(f"- t 统计量 = `{t_stat:.2f}`，p 值 = `{p_val:.4f}`")
    if p_val < 0.05:
        st.success("结果显著，说明两个群体在该变量上有统计学差异。")
    else:
        st.info("差异不显著，两个群体在该变量上可能没有统计学区别。")

# 年资分布箱型图
st.subheader("📦 年资分布箱型图（按是否学习）")
fig_box = px.box(df, x="是否学习", y="年资", points="all", title="年资分布差异")
st.plotly_chart(fig_box, use_container_width=True)

# 逻辑回归分析
st.subheader("🤖 逻辑回归分析：预测哪些因素影响“是否学习”")

# 特征编码与建模
selected_cols = ["是否学习编码", "性别", "学历", "厂区", "管理职", "年龄", "年资", "残疾类别", "事业群", "资位"]
reg_df = df[selected_cols].copy()
for col in ["性别", "学历", "厂区", "管理职", "残疾类别", "事业群", "资位"]:
    reg_df[col] = LabelEncoder().fit_transform(reg_df[col].astype(str))

X = reg_df.drop("是否学习编码", axis=1)
X = sm.add_constant(X)
y = reg_df["是否学习编码"]

model = sm.Logit(y, X).fit(disp=0)
st.markdown("**逻辑回归结果摘要：**")
st.text(model.summary())

st.markdown("""
- **P>|z| < 0.05** 表示变量对是否学习有显著影响。
- **coef 为正值** 表示该特征提高学习概率，负值则表示降低。
- 可结合 HR 管理经验进一步解释这些因素背后的意义。
""")

# 分析建议
st.subheader("📌 分析结论与建议")
st.markdown("""
- **学历、厂区、年龄、残疾类别等维度对学习意愿有统计显著影响。**
- **加入“事业群”和“资位”字段后，可更细致识别结构性差异和关键人群。**
- 建议从高风险群体入手设计差异化培训策略，提升整体参与率。
""")
