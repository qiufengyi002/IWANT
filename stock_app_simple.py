"""
A股行情展示系统 - 简化版
只支持A股，使用新浪财经API
"""

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import time
import random
import requests
import json
import akshare as ak

# 页面配置
st.set_page_config(
    page_title="A股行情中心",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 标题
st.markdown('<h1 style="text-align: center; color: #00f5ff;">📈 A股行情中心</h1>', unsafe_allow_html=True)

# 尝试导入配置文件
try:
    from config import ALPHA_VANTAGE_API_KEY, DATA_SOURCE
except:
    ALPHA_VANTAGE_API_KEY = None
    DATA_SOURCE = "yahoo_finance"

# 新浪财经API数据获取函数
@st.cache_data(ttl=60)
def get_sina_data(codes):
    """使用新浪财经API获取实时行情"""
    try:
        url = f"http://hq.sinajs.cn/list={','.join(codes)}"
        headers = {
            'Referer': 'http://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'
        
        result = {}
        lines = response.text.strip().split('\n')
        
        for line in lines:
            if not line or 'hq_str_' not in line:
                continue
                
            parts = line.split('="')
            if len(parts) < 2:
                continue
                
            code = parts[0].replace('var hq_str_', '')
            data_str = parts[1].rstrip('";')
            
            if not data_str:
                continue
                
            data_parts = data_str.split(',')
            
            # A股格式：名称,今开,昨收,当前价,最高,最低,买一,卖一,成交量,成交额
            if len(data_parts) >= 10:
                result[code] = {
                    'name': data_parts[0],
                    'open': float(data_parts[1]) if data_parts[1] else 0,
                    'prev_close': float(data_parts[2]) if data_parts[2] else 0,
                    'price': float(data_parts[3]) if data_parts[3] else 0,
                    'high': float(data_parts[4]) if data_parts[4] else 0,
                    'low': float(data_parts[5]) if data_parts[5] else 0,
                    'volume': int(float(data_parts[8])) if data_parts[8] else 0,
                    'amount': float(data_parts[9]) if data_parts[9] else 0,
                }
                # 计算涨跌
                if result[code]['prev_close'] > 0:
                    result[code]['change'] = result[code]['price'] - result[code]['prev_close']
                    result[code]['change_percent'] = (result[code]['change'] / result[code]['prev_close']) * 100
                else:
                    result[code]['change'] = 0
                    result[code]['change_percent'] = 0
        
        return result
        
    except Exception as e:
        return None

@st.cache_data(ttl=60)
def get_index_data_sina():
    """使用新浪财经获取A股主要指数实时行情"""
    index_codes = {
        'sh000001': {'name': '上证指数', 'symbol': '000001'},
        'sz399001': {'name': '深证成指', 'symbol': '399001'},
        'sz399006': {'name': '创业板指', 'symbol': '399006'},
    }
    
    data = get_sina_data(list(index_codes.keys()))
    
    if not data:
        return None
    
    result = {}
    for code, info in index_codes.items():
        if code in data:
            d = data[code]
            result[info['symbol']] = {
                'price': d['price'],
                'change': d['change'],
                'change_percent': d['change_percent'],
                'open': d['open'],
                'high': d['high'],
                'low': d['low'],
                'volume': d['volume'],
                'amount': d.get('amount', 0),
            }
    
    return result

@st.cache_data(ttl=60)
def get_stock_realtime_sina(symbol):
    """使用新浪财经获取A股实时行情"""
    try:
        if '.SS' in symbol:
            sina_code = f"sh{symbol.replace('.SS', '')}"
        elif '.SZ' in symbol:
            sina_code = f"sz{symbol.replace('.SZ', '')}"
        else:
            return None, "仅支持A股实时行情"
        
        data = get_sina_data([sina_code])
        
        if data and sina_code in data:
            d = data[sina_code]
            return {
                'price': d['price'],
                'change': d['change'],
                'change_percent': d['change_percent'],
                'volume': d['volume'],
                'open': d['open'],
                'high': d['high'],
                'low': d['low'],
            }, None
        
        return None, "未找到股票数据"
        
    except Exception as e:
        return None, f"获取实时行情失败: {str(e)}"

@st.cache_data(ttl=300)
def get_stock_data(symbol, start, end):
    """获取股票历史数据 - 只支持A股"""
    if '.SS' in symbol or '.SZ' in symbol:
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(start=start, end=end)
            if df is not None and not df.empty:
                return df, None, "Yahoo Finance (A股数据)"
        except Exception as e:
            pass
    
    return None, "仅支持A股查询（代码格式：600519.SS 或 000001.SZ）", None

# 市场配置
MARKETS = {
    "A股": {
        "indices": [
            {"symbol": "000001", "name": "上证指数"},
            {"symbol": "399001", "name": "深证成指"},
            {"symbol": "399006", "name": "创业板指"},
        ]
    }
}

# 显示市场行情
st.markdown("## 🌍 A股市场概览")
st.info("💡 提示：A股实时数据来自新浪财经（与同花顺一致）")

# 获取A股指数实时数据
a_stock_indices_data = None
try:
    a_stock_indices_data = get_index_data_sina()
except Exception as e:
    st.error(f"⚠️ A股指数数据获取失败: {str(e)[:100]}...")

# 显示A股指数
if a_stock_indices_data:
    for index in MARKETS["A股"]["indices"]:
        if index["symbol"] in a_stock_indices_data:
            data = a_stock_indices_data[index["symbol"]]
            change_class = "🔴" if data["change"] < 0 else "🟢"
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(index['name'], f"{data['price']:,.2f}")
            with col2:
                st.metric("涨跌额", f"{data['change']:+,.2f}")
            with col3:
                st.metric("涨跌幅", f"{data['change_percent']:+.2f}%")
            with col4:
                st.metric("成交量", f"{data['volume']:,}")

st.markdown("---")

# 侧边栏 - 输入区域
st.sidebar.header("📊 股票查询")

# 股票代码输入
stock_symbol = st.sidebar.text_input(
    "股票代码",
    value="600519.SS",
    help="输入股票代码，例如：600519.SS（贵州茅台）、000001.SZ（平安银行）"
)

# 日期范围选择
st.sidebar.subheader("📅 日期范围")
date_option = st.sidebar.radio(
    "选择时间范围",
    ["1个月", "3个月", "6个月", "1年", "自定义"],
    index=0
)

# 根据选择设置日期范围
if date_option == "自定义":
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("开始日期", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("结束日期", datetime.now())
else:
    days_map = {"1个月": 30, "3个月": 90, "6个月": 180, "1年": 365}
    days = days_map[date_option]
    start_date = datetime.now() - timedelta(days=days)
    end_date = datetime.now()

# 添加查询按钮
query_button = st.sidebar.button("🔍 查询股票", type="primary")

# 添加清除缓存按钮
if st.sidebar.button("🗑️ 清除缓存"):
    st.cache_data.clear()
    st.success("✅ 缓存已清除！")
    st.rerun()

# 快速选择热门股票
st.sidebar.markdown("### 🚀 快速选择")
quick_stocks = st.sidebar.selectbox(
    "热门股票",
    ["", "600519.SS - 贵州茅台", "000001.SZ - 平安银行", "000858.SZ - 五粮液", "601318.SS - 中国平安", "000333.SZ - 美的集团"]
)

if quick_stocks:
    stock_symbol = quick_stocks.split(" - ")[0]

# 主内容区域 - 股票详情
if query_button or stock_symbol:
    try:
        with st.spinner(f"正在获取 {stock_symbol} 的数据..."):
            df, error, data_source = get_stock_data(stock_symbol, start_date, end_date)
            
            if error:
                st.error(f"❌ {error}")
                st.info("💡 提示：\n- 请检查股票代码是否正确\n- 仅支持A股查询")
            else:
                # 获取股票基本信息
                try:
                    stock = yf.Ticker(stock_symbol)
                    info = stock.info
                except:
                    info = None
                
        if df is None or df.empty:
            if not error:
                st.error(f"❌ 未找到股票代码 '{stock_symbol}' 的数据，请检查代码是否正确")
        else:
            # 显示数据来源
            if data_source:
                st.markdown(f"**📊 数据来源：** {data_source}")
            
            # 获取实时价格
            realtime_data = None
            if '.SS' in stock_symbol or '.SZ' in stock_symbol:
                realtime_data, _ = get_stock_realtime_sina(stock_symbol)
            
            if realtime_data:
                current_price = realtime_data['price']
                price_change = realtime_data['change']
                price_change_percent = realtime_data['change_percent']
            else:
                current_price = df['Close'].iloc[-1]
                previous_close = df['Close'].iloc[-2] if len(df) > 1 else current_price
                price_change = current_price - previous_close
                price_change_percent = (price_change / previous_close) * 100
            
            stock_name = info.get('longName', stock_symbol) if info else stock_symbol
            
            st.markdown(f"## {stock_name} ({stock_symbol})")
            
            # 显示实时价格信息
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("💰 当前价格", f"¥{current_price:,.2f}")
            
            with col2:
                st.metric("📊 涨跌额", f"{price_change:+,.2f}")
            
            with col3:
                st.metric("📈 涨跌幅", f"{price_change_percent:+.2f}%")
            
            st.markdown("---")
            
            # 创建K线图
            fig = make_subplots(
                rows=2, 
                cols=1, 
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.7, 0.3],
                subplot_titles=('K线图', '成交量')
            )
            
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name="K线",
                    increasing_line_color='#00ff88',
                    decreasing_line_color='#ff4757',
                ),
                row=1, col=1
            )
            
            colors = ['#00ff88' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ff4757' 
                     for i in range(len(df))]
            
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df['Volume'],
                    name="成交量",
                    marker_color=colors,
                    opacity=0.7,
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title=f"{stock_name} ({stock_symbol}) - K线图与成交量",
                yaxis_title="价格",
                yaxis2_title="成交量",
                xaxis_rangeslider_visible=False,
                height=600,
                showlegend=True,
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 显示详细数据表格
            st.markdown("### 📊 详细数据")
            
            display_df = df.copy()
            display_df.index = display_df.index.strftime('%Y-%m-%d')
            display_df = display_df.round(2)
            display_df.columns = ['开盘价', '最高价', '最低价', '收盘价', '成交量']
            
            st.dataframe(display_df, use_container_width=True, height=400)
            
            st.markdown(f"**⏰ 最后更新时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
    except Exception as e:
        st.error(f"❌ 获取数据时出错：{str(e)}")
        st.info("💡 提示：请检查股票代码是否正确，或稍后重试")

# 页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.5); padding: 20px;">
    <p>📊 A股行情中心 | 数据来源：新浪财经</p>
    <p>支持A股实时行情查询</p>
</div>
""", unsafe_allow_html=True)