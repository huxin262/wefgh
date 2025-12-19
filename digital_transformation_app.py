import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 页面标题
st.title('上市公司数字化转型指数查询系统')

# 读取数据
df = pd.read_excel('两版合并后的年报数据_完整版.xlsx')

# 数据预处理
df['股票代码'] = df['股票代码'].astype(str)  # 将股票代码转为字符串类型

# 侧边栏：股票代码输入
stock_code = st.sidebar.text_input('请输入股票代码（如：600000）：')

# 侧边栏：年份选择
if not df.empty:
    years = sorted(df['年份'].unique(), reverse=True)
    selected_year = st.sidebar.selectbox('选择年份：', ['全部'] + years)

# 查询按钮
if st.sidebar.button('查询'):
    if stock_code:
        # 根据股票代码过滤数据
        filtered_df = df[df['股票代码'] == stock_code]
        
        if not filtered_df.empty:
            # 如果选择了特定年份
            if selected_year != '全部':
                filtered_df = filtered_df[filtered_df['年份'] == selected_year]
            
            if not filtered_df.empty:
                # 显示公司基本信息
                company_name = filtered_df['企业名称'].iloc[0]
                st.subheader(f'{company_name}（股票代码：{stock_code}）')
                
                # 显示数字化转型指数
                st.write('### 数字化转型指数')
                for idx, row in filtered_df.iterrows():
                    st.metric(
                        label=f'{row["年份"]}年',
                        value=round(row['数字化转型指数'], 4)
                    )
                
                # 显示详细数据
                st.write('### 详细数据')
                display_df = filtered_df[['年份', '人工智能词频数', '大数据词频数', '云计算词频数', 
                                          '区块链词频数', '数字技术运用词频数', '技术维度', '应用维度', 
                                          '词总', '数字化转型指数']]
                st.dataframe(display_df)
                
                # 可视化：数字化转型指数趋势
                if len(filtered_df) > 1:
                    st.write('### 数字化转型指数趋势')
                    fig, ax = plt.subplots(figsize=(10, 6))
                    filtered_df = filtered_df.sort_values('年份')
                    ax.plot(filtered_df['年份'], filtered_df['数字化转型指数'], marker='o', linewidth=2)
                    ax.set_title(f'{company_name}数字化转型指数趋势', fontsize=14)
                    ax.set_xlabel('年份', fontsize=12)
                    ax.set_ylabel('数字化转型指数', fontsize=12)
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)
                    
                    # 可视化：各技术维度对比
                    st.write('### 技术维度对比')
                    tech_columns = ['人工智能词频数', '大数据词频数', '云计算词频数', '区块链词频数']
                    tech_data = filtered_df.groupby('年份')[tech_columns].sum()
                    
                    fig, ax = plt.subplots(figsize=(12, 8))
                    tech_data.plot(kind='bar', ax=ax)
                    ax.set_title(f'{company_name}各技术维度词频数对比', fontsize=14)
                    ax.set_xlabel('年份', fontsize=12)
                    ax.set_ylabel('词频数', fontsize=12)
                    ax.legend(title='技术维度')
                    ax.grid(True, alpha=0.3, axis='y')
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
            else:
                st.warning(f'未找到{stock_code}在{selected_year}年的数据')
        else:
            st.error(f'未找到股票代码为{stock_code}的数据')
    else:
        st.warning('请输入股票代码')

# 显示所有股票代码列表（可选功能）
if st.checkbox('显示所有股票代码'):
    all_stocks = df[['股票代码', '企业名称']].drop_duplicates().sort_values('股票代码')
    st.write('### 所有股票代码列表')
    st.dataframe(all_stocks)

# 数据统计信息
st.sidebar.write('### 数据统计')
st.sidebar.write(f'总公司数：{df["股票代码"].nunique()}')
st.sidebar.write(f'年份范围：{df["年份"].min()} - {df["年份"].max()}')
st.sidebar.write(f'数据条目数：{len(df)}')