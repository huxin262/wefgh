import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 设置页面布局
st.set_page_config(
    page_title='企业数字化转型指数查询系统',
    layout='wide',
    initial_sidebar_state='expanded'
)

# 页面标题
st.title('企业数字化转型指数查询系统')

# 读取数据
df = pd.read_excel('两版合并后的年报数据_完整版.xlsx')

# 数据预处理
df['股票代码'] = df['股票代码'].astype(str)  # 将股票代码转为字符串类型

# 创建主布局：左侧查询面板，右侧内容
query_col, content_col = st.columns([1, 3])

# ---------------------- 左侧查询面板 ----------------------
with query_col:
    st.header('查询面板')
    st.write('请选择以下参数进行查询')
    
    # 股票代码选择（下拉框）
    if not df.empty:
        stock_codes = sorted(df['股票代码'].unique())
        stock_code = st.selectbox('股票代码', stock_codes)
    else:
        stock_code = st.selectbox('股票代码', ['无数据'])
    
    # 年份选择（下拉框）
    if not df.empty:
        years = sorted(df['年份'].unique(), reverse=True)
        selected_year = st.selectbox('年份', ['全部'] + years)
    else:
        selected_year = st.selectbox('年份', ['无数据'])
    
    # 查询按钮
    query_button = st.button('查询', type='primary')

# ---------------------- 右侧内容区域 ----------------------
with content_col:
    # 默认显示所有数据的统计信息，查询后显示筛选后的数据
    display_df = df.copy()
    query_executed = False
    
    # 处理查询
    if query_button:
        query_executed = True
        # 根据股票代码过滤数据
        display_df = df[df['股票代码'] == stock_code]
        
        # 如果选择了特定年份
        if selected_year != '全部':
            display_df = display_df[display_df['年份'] == selected_year]
    
    # ---------------------- 1. 统计概览 ----------------------
    st.header('统计概览')
    
    # 计算统计指标
    total_records = len(display_df)
    total_companies = display_df['股票代码'].nunique()
    if not display_df.empty:
        year_range = f"{display_df['年份'].min()}-{display_df['年份'].max()}"
        avg_index = display_df['数字化转型指数'].mean()
        max_index = display_df['数字化转型指数'].max()
        min_index = display_df['数字化转型指数'].min()
        median_index = display_df['数字化转型指数'].median()
        std_index = display_df['数字化转型指数'].std()
        
        # 显示统计卡片
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("总记录数", total_records)
        with col2:
            st.metric("企业数量", total_companies)
        with col3:
            st.metric("年份范围", year_range)
        with col4:
            st.metric("平均指数", round(avg_index, 4))
        with col5:
            st.metric("最高指数", round(max_index, 4))
        
        # 第二行统计卡片
        col6, col7, col8 = st.columns(3)
        with col6:
            st.metric("最低指数", round(min_index, 4))
        with col7:
            st.metric("指数中位数", round(median_index, 4))
        with col8:
            st.metric("指数标准差", round(std_index, 4))
    
    # ---------------------- 2. 数据概览 ----------------------
    st.header('数据概览')
    
    # 显示数据前几行
    st.dataframe(display_df.head(10), height=200)
    
    # ---------------------- 3. 数字化转型指数分布 ----------------------
    st.header('数字化转型指数分布')
    
    if not display_df.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(display_df['数字化转型指数'], kde=True, ax=ax)
        ax.set_title('数字化转型指数分布', fontsize=14)
        ax.set_xlabel('数字化转型指数', fontsize=12)
        ax.set_ylabel('频数', fontsize=12)
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    
    # ---------------------- 4. 数字化转型指数详细统计 ----------------------
    st.header('数字化转型指数详细统计')
    
    if not display_df.empty:
        # 按年份统计
        year_stats = display_df.groupby('年份')['数字化转型指数'].agg(['mean', 'median', 'max', 'min', 'std', 'count']).reset_index()
        year_stats.columns = ['年份', '平均值', '中位数', '最大值', '最小值', '标准差', '公司数量']
        st.dataframe(year_stats.style.format({
            '平均值': '{:.4f}',
            '中位数': '{:.4f}',
            '最大值': '{:.4f}',
            '最小值': '{:.4f}',
            '标准差': '{:.4f}'
        }))
    
    # ---------------------- 5. 数字化转型指数折线图 ----------------------
    st.header('数字化转型指数趋势')
    
    if not display_df.empty:
        # 如果是单个公司，按年份绘制趋势图
        if display_df['股票代码'].nunique() == 1:
            company_name = display_df['企业名称'].iloc[0]
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # 按年份排序
            trend_df = display_df.sort_values('年份')
            ax.plot(trend_df['年份'], trend_df['数字化转型指数'], marker='o', linewidth=2)
            ax.set_title(f'{company_name}数字化转型指数趋势', fontsize=14)
            ax.set_xlabel('年份', fontsize=12)
            ax.set_ylabel('数字化转型指数', fontsize=12)
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
        # 如果是多个公司，绘制平均趋势
        else:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # 按年份计算平均值
            avg_trend = display_df.groupby('年份')['数字化转型指数'].mean().reset_index()
            avg_trend = avg_trend.sort_values('年份')
            
            ax.plot(avg_trend['年份'], avg_trend['数字化转型指数'], marker='o', linewidth=2)
            ax.set_title('数字化转型指数平均趋势', fontsize=14)
            ax.set_xlabel('年份', fontsize=12)
            ax.set_ylabel('平均数字化转型指数', fontsize=12)
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
    
    # ---------------------- 6. 详细数据统计 ----------------------
    st.header('详细数据统计')
    
    if not display_df.empty:
        # 计算各技术维度的统计信息
        tech_cols = ['人工智能词频数', '大数据词频数', '云计算词频数', '区块链词频数', '数字技术运用词频数']
        tech_stats = display_df[tech_cols].agg(['sum', 'mean', 'max', 'min']).T
        tech_stats.columns = ['总计', '平均值', '最大值', '最小值']
        
        st.subheader('技术维度统计')
        st.dataframe(tech_stats.style.format('{:.4f}'))
        
        # 如果是单个公司，显示完整数据
        if display_df['股票代码'].nunique() == 1:
            st.subheader('完整数据')
            full_data_cols = ['年份', '企业名称', '股票代码', '人工智能词频数', '大数据词频数', 
                              '云计算词频数', '区块链词频数', '数字技术运用词频数', '技术维度', 
                              '应用维度', '词总', '数字化转型指数']
            st.dataframe(display_df[full_data_cols])