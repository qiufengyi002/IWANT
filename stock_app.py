"""
A股行情展示系统 - 简化版
只支持A股，使用新浪财经API
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import requests
import json
from trading_db import TradingDB
from pages_trading import show_trading_page, show_positions_page, show_transactions_page, show_watchlist_page

# 初始化数据库
db = TradingDB()

# 页面配置
st.set_page_config(
    page_title="A股行情中心",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加CSS样式 - 禁用输入框自动填充
st.markdown("""
<style>
    /* 禁用输入框的自动填充 */
    input[type="text"] {
        -webkit-autocomplete: off !important;
        autocomplete: off !important;
    }
    
    /* 隐藏浏览器自动填充的下拉提示 */
    input:-webkit-autofill,
    input:-webkit-autofill:hover,
    input:-webkit-autofill:focus,
    input:-webkit-autofill:active {
        -webkit-box-shadow: 0 0 0 30px transparent inset !important;
        transition: background-color 5000s ease-in-out 0s;
    }
</style>
<script>
    // 禁用所有输入框的自动完成
    document.addEventListener('DOMContentLoaded', function() {
        const inputs = document.querySelectorAll('input[type="text"]');
        inputs.forEach(input => {
            input.setAttribute('autocomplete', 'off');
            input.setAttribute('autocorrect', 'off');
            input.setAttribute('autocapitalize', 'off');
            input.setAttribute('spellcheck', 'false');
        });
    });
    
    // 监听新添加的输入框
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) {
                    const inputs = node.querySelectorAll('input[type="text"]');
                    inputs.forEach(input => {
                        input.setAttribute('autocomplete', 'off');
                        input.setAttribute('autocorrect', 'off');
                        input.setAttribute('autocapitalize', 'off');
                        input.setAttribute('spellcheck', 'false');
                    });
                }
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
</script>
""", unsafe_allow_html=True)

# 标题
st.markdown('<h1 style="text-align: center; color: #00f5ff;">📈 A股行情中心</h1>', unsafe_allow_html=True)

# 初始化用户session - 使用query params保持登录状态
if 'user' not in st.session_state:
    st.session_state.user = None

# 从URL参数中恢复登录状态
query_params = st.query_params
if st.session_state.user is None and 'username' in query_params:
    username = query_params['username']
    user = db.get_user(username)
    if user:
        st.session_state.user = user

# 用户登录/注册
if st.session_state.user is None:
    st.sidebar.markdown("### 👤 用户登录")
    username = st.sidebar.text_input("用户名", placeholder="输入用户名登录或注册")
    
    if st.sidebar.button("登录/注册", type="primary"):
        if username:
            user = db.get_user(username)
            if user is None:
                # 创建新用户，初始资金100万
                user_id, error = db.create_user(username, 1000000.0)
                if user_id:
                    user = db.get_user(username)
                    st.session_state.user = user
                    # 保存用户名到URL参数
                    st.query_params['username'] = username
                    st.success(f"欢迎新用户 {username}! 初始资金: 1,000,000元")
                    st.rerun()
                else:
                    st.error(f"❌ {error}")
            else:
                st.session_state.user = user
                # 保存用户名到URL参数
                st.query_params['username'] = username
                st.success(f"欢迎回来, {username}!")
                st.rerun()
        else:
            st.warning("请输入用户名")
    
    st.sidebar.info("💡 首次登录将自动注册，初始资金100万元")
    st.sidebar.markdown("---")
    
    # 未登录时只显示行情查询
    page = "行情查询"
else:
    # 已登录，显示用户信息和完整导航
    # 用户信息卡片
    st.sidebar.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.1) 0%, rgba(255,255,255,0.05) 100%);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid rgba(0, 245, 255, 0.3);
    ">
        <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-bottom: 5px;">👤 当前用户</div>
        <div style="font-size: 18px; font-weight: bold; color: #00f5ff; margin-bottom: 10px;">{st.session_state.user['username']}</div>
        <div style="font-size: 12px; color: rgba(255,255,255,0.6);">💰 可用资金</div>
        <div style="font-size: 20px; font-weight: bold; color: #00ff88;">¥{st.session_state.user['cash']:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 退出登录", use_container_width=True, type="secondary"):
        st.session_state.user = None
        # 清除URL参数
        if 'username' in st.query_params:
            del st.query_params['username']
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📑 功能导航")
    
    # 初始化current_page
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "行情查询"
    
    # 导航选项配置
    nav_options = [
        {"name": "行情查询", "icon": "📈"},
        {"name": "买入股票", "icon": "💰"},
        {"name": "我的自选", "icon": "⭐"},
        {"name": "我的持仓", "icon": "📊"},
        {"name": "交易记录", "icon": "📜"}
    ]
    
    # 创建导航按钮
    for option in nav_options:
        is_active = st.session_state.current_page == option["name"]
        button_type = "primary" if is_active else "secondary"
        button_label = f"{option['icon']} {option['name']}"
        
        if st.sidebar.button(
            button_label,
            key=f"nav_{option['name']}",
            use_container_width=True,
            type=button_type
        ):
            if st.session_state.current_page != option["name"]:
                # 页面切换逻辑
                if option["name"] == "买入股票":
                    if 'trading_search_query' in st.session_state:
                        st.session_state.trading_search_query = ""
                    if 'trading_stock_code' in st.session_state:
                        st.session_state.trading_stock_code = ""
                    if 'trading_stock_name' in st.session_state:
                        st.session_state.trading_stock_name = ""
                elif option["name"] == "我的自选":
                    if 'watchlist_search_query' in st.session_state:
                        st.session_state.watchlist_search_query = ""
                
                st.session_state.current_page = option["name"]
                st.rerun()
    
    page = st.session_state.current_page

st.sidebar.markdown("---")

# 获取A股股票列表
@st.cache_data(ttl=3600)
def get_stock_list():
    """获取A股股票列表，使用新浪财经API（分页获取）"""
    try:
        stock_list = []
        
        # 分别获取沪市和深市的股票
        markets = [
            ('sh_a', 'sh'),  # 沪市A股
            ('sz_a', 'sz'),  # 深市A股
        ]
        
        for market_code, prefix in markets:
            page = 1
            max_pages = 30  # 最多获取30页，每页100条，共3000条
            
            while page <= max_pages:
                url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"
                params = {
                    'page': str(page),
                    'num': '100',  # 每页100条
                    'sort': 'symbol',
                    'asc': '1',
                    'node': market_code,
                    'symbol': '',
                    '_s_r_a': 'page'
                }
                
                headers = {
                    'Referer': 'http://vip.stock.finance.sina.com.cn/',
                    'User-Agent': 'Mozilla/5.0'
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                
                if not data or not isinstance(data, list) or len(data) == 0:
                    break  # 没有更多数据了
                
                for item in data:
                    try:
                        code = item['code']
                        name = item['name']
                        
                        # 判断是上海还是深圳
                        if code.startswith('6') or code.startswith('5') or code.startswith('688'):
                            symbol = f"{code}.SS"
                        else:
                            symbol = f"{code}.SZ"
                        
                        stock_list.append({
                            'code': code,
                            'name': name,
                            'symbol': symbol,
                            'display': f"{code} - {name}"
                        })
                    except:
                        continue
                
                # 如果返回的数据少于100条，说明已经是最后一页了
                if len(data) < 100:
                    break
                    
                page += 1
        
        if len(stock_list) > 0:
            return stock_list
        else:
            raise Exception("未获取到股票数据")
        
    except Exception as e:
        # 如果获取失败，返回常用股票列表作为备选
        st.warning(f"⚠️ 获取完整股票列表失败，使用常用股票列表: {str(e)[:50]}")
        return get_fallback_stock_list()

def get_fallback_stock_list():
    """备用的常用股票列表"""
    stock_list = [
        # 上证主板
        {'code': '600519', 'name': '贵州茅台', 'symbol': '600519.SS'},
        {'code': '600036', 'name': '招商银行', 'symbol': '600036.SS'},
        {'code': '601318', 'name': '中国平安', 'symbol': '601318.SS'},
        {'code': '600276', 'name': '恒瑞医药', 'symbol': '600276.SS'},
        {'code': '601012', 'name': '隆基绿能', 'symbol': '601012.SS'},
        {'code': '600900', 'name': '长江电力', 'symbol': '600900.SS'},
        {'code': '601888', 'name': '中国中免', 'symbol': '601888.SS'},
        {'code': '600887', 'name': '伊利股份', 'symbol': '600887.SS'},
        {'code': '601166', 'name': '兴业银行', 'symbol': '601166.SS'},
        {'code': '600030', 'name': '中信证券', 'symbol': '600030.SS'},
        {'code': '601398', 'name': '工商银行', 'symbol': '601398.SS'},
        {'code': '601288', 'name': '农业银行', 'symbol': '601288.SS'},
        {'code': '601939', 'name': '建设银行', 'symbol': '601939.SS'},
        {'code': '601988', 'name': '中国银行', 'symbol': '601988.SS'},
        {'code': '600000', 'name': '浦发银行', 'symbol': '600000.SS'},
        {'code': '601328', 'name': '交通银行', 'symbol': '601328.SS'},
        {'code': '600016', 'name': '民生银行', 'symbol': '600016.SS'},
        {'code': '601601', 'name': '中国太保', 'symbol': '601601.SS'},
        {'code': '601688', 'name': '华泰证券', 'symbol': '601688.SS'},
        {'code': '600309', 'name': '万华化学', 'symbol': '600309.SS'},
        {'code': '603259', 'name': '药明康德', 'symbol': '603259.SS'},
        {'code': '600585', 'name': '海螺水泥', 'symbol': '600585.SS'},
        {'code': '601899', 'name': '紫金矿业', 'symbol': '601899.SS'},
        {'code': '600031', 'name': '三一重工', 'symbol': '600031.SS'},
        {'code': '601857', 'name': '中国石油', 'symbol': '601857.SS'},
        {'code': '600028', 'name': '中国石化', 'symbol': '600028.SS'},
        {'code': '601668', 'name': '中国建筑', 'symbol': '601668.SS'},
        {'code': '601390', 'name': '中国中铁', 'symbol': '601390.SS'},
        {'code': '600050', 'name': '中国联通', 'symbol': '600050.SS'},
        {'code': '601728', 'name': '中国电信', 'symbol': '601728.SS'},
        
        # 深证主板
        {'code': '000001', 'name': '平安银行', 'symbol': '000001.SZ'},
        {'code': '000002', 'name': '万科A', 'symbol': '000002.SZ'},
        {'code': '000333', 'name': '美的集团', 'symbol': '000333.SZ'},
        {'code': '000858', 'name': '五粮液', 'symbol': '000858.SZ'},
        {'code': '000651', 'name': '格力电器', 'symbol': '000651.SZ'},
        {'code': '000725', 'name': '京东方A', 'symbol': '000725.SZ'},
        {'code': '000568', 'name': '泸州老窖', 'symbol': '000568.SZ'},
        {'code': '000596', 'name': '古井贡酒', 'symbol': '000596.SZ'},
        {'code': '000661', 'name': '长春高新', 'symbol': '000661.SZ'},
        {'code': '000063', 'name': '中兴通讯', 'symbol': '000063.SZ'},
        {'code': '000100', 'name': 'TCL科技', 'symbol': '000100.SZ'},
        {'code': '000876', 'name': '新希望', 'symbol': '000876.SZ'},
        
        # 创业板
        {'code': '300750', 'name': '宁德时代', 'symbol': '300750.SZ'},
        {'code': '300059', 'name': '东方财富', 'symbol': '300059.SZ'},
        {'code': '300760', 'name': '迈瑞医疗', 'symbol': '300760.SZ'},
        {'code': '300015', 'name': '爱尔眼科', 'symbol': '300015.SZ'},
        {'code': '300142', 'name': '沃森生物', 'symbol': '300142.SZ'},
        {'code': '300122', 'name': '智飞生物', 'symbol': '300122.SZ'},
        {'code': '300274', 'name': '阳光电源', 'symbol': '300274.SZ'},
        {'code': '300124', 'name': '汇川技术', 'symbol': '300124.SZ'},
        {'code': '300014', 'name': '亿纬锂能', 'symbol': '300014.SZ'},
    ]
    
    # 添加display字段
    for stock in stock_list:
        stock['display'] = f"{stock['code']} - {stock['name']}"
    
    return stock_list

def search_stock_by_name(query, stock_list):
    """根据中文名称或代码搜索股票"""
    if not query:
        return []
    
    query = query.strip()
    results = []
    
    for stock in stock_list:
        # 支持代码或名称匹配（代码不区分大小写，名称直接匹配）
        if query.upper() in stock['code'].upper() or query in stock['name']:
            results.append(stock)
            if len(results) >= 20:  # 最多返回20个结果
                break
    
    return results

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

@st.cache_data(ttl=3600)
def get_company_info_sina(symbol):
    """获取公司基本信息"""
    try:
        stock_code = symbol.replace('.SS', '').replace('.SZ', '')
        
        # 获取公司基本信息
        url = f"http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/{stock_code}.phtml"
        headers = {
            'Referer': 'http://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'
        
        if response.status_code == 200:
            import re
            text = response.text
            
            # 提取基本信息
            info = {}
            patterns = {
                'company_name': r'公司名称[：:]\s*</td>\s*<td[^>]*>([^<]+)',
                'english_name': r'英文名称[：:]\s*</td>\s*<td[^>]*>([^<]+)',
                'address': r'注册地址[：:]\s*</td>\s*<td[^>]*>([^<]+)',
                'legal_person': r'法人代表[：:]\s*</td>\s*<td[^>]*>([^<]+)',
                'general_manager': r'总\s*经\s*理[：:]\s*</td>\s*<td[^>]*>([^<]+)',
                'secretary': r'董事会秘书[：:]\s*</td>\s*<td[^>]*>([^<]+)',
                'phone': r'公司电话[：:]\s*</td>\s*<td[^>]*>([^<]+)',
                'email': r'电子信箱[：:]\s*</td>\s*<td[^>]*>([^<]+)',
                'website': r'公司网址[：:]\s*</td>\s*<td[^>]*>([^<]+)',
                'industry': r'所属行业[：:]\s*</td>\s*<td[^>]*>([^<]+)',
                'listing_date': r'上市日期[：:]\s*</td>\s*<td[^>]*>([^<]+)',
                'registered_capital': r'注册资本[：:]\s*</td>\s*<td[^>]*>([^<]+)',
                'employees': r'员工人数[：:]\s*</td>\s*<td[^>]*>([^<]+)',
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, text)
                info[key] = match.group(1).strip() if match else "暂无"
            
            # 提取公司简介
            intro_patterns = [
                r'公司简介[：:]\s*</td>\s*</tr>\s*<tr>\s*<td[^>]*>([^<]+)',
                r'公司简介[：:]\s*</td>\s*<td[^>]*>([^<]+)',
            ]
            
            for pattern in intro_patterns:
                match = re.search(pattern, text)
                if match:
                    info['introduction'] = match.group(1).strip()
                    break
            else:
                info['introduction'] = "暂无"
            
            # 提取主营业务
            business_patterns = [
                r'主营业务[：:]\s*</td>\s*</tr>\s*<tr>\s*<td[^>]*>([^<]+)',
                r'主营业务[：:]\s*</td>\s*<td[^>]*>([^<]+)',
            ]
            
            for pattern in business_patterns:
                match = re.search(pattern, text)
                if match:
                    info['business'] = match.group(1).strip()
                    break
            else:
                info['business'] = "暂无"
            
            return info
        
        return None
        
    except Exception as e:
        return None

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
def get_stock_history_sina(symbol, start, end):
    """使用新浪财经获取A股历史K线数据"""
    try:
        # 转换代码格式
        if '.SS' in symbol:
            sina_code = f"sh{symbol.replace('.SS', '')}"
        elif '.SZ' in symbol:
            sina_code = f"sz{symbol.replace('.SZ', '')}"
        else:
            return None, "仅支持A股历史数据"
        
        # 计算天数
        days = (end - start).days + 1
        
        # 新浪历史K线API
        url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData'
        params = {
            'symbol': sina_code,
            'scale': '240',  # 日线
            'datalen': str(min(days, 500)),  # 最多500天
        }
        
        headers = {
            'Referer': 'http://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None, f"API请求失败: {response.status_code}"
        
        data = response.json()
        
        if not data or not isinstance(data, list):
            return None, "未获取到数据"
        
        # 转换为DataFrame
        df_data = []
        for item in data:
            try:
                date = pd.to_datetime(item['day'])
                if start <= date <= end:
                    df_data.append({
                        'Date': date,
                        'Open': float(item['open']),
                        'High': float(item['high']),
                        'Low': float(item['low']),
                        'Close': float(item['close']),
                        'Volume': int(float(item['volume'])),
                    })
            except:
                continue
        
        if not df_data:
            return None, "指定日期范围内无数据"
        
        df = pd.DataFrame(df_data)
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        return df, None
        
    except Exception as e:
        return None, f"获取历史数据失败: {str(e)}"

@st.cache_data(ttl=300)
def get_stock_data(symbol, start, end):
    """获取股票历史数据 - 使用新浪财经API"""
    if '.SS' in symbol or '.SZ' in symbol:
        df, error = get_stock_history_sina(symbol, start, end)
        if df is not None:
            return df, None, "新浪财经 (A股数据)"
        else:
            return None, error, None
    
    return None, f"仅支持A股查询（代码格式：600519.SS 或 000001.SZ）", None

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

# ==================== 页面路由 ====================
if page == "行情查询":
    # ==================== 行情查询页面 ====================
    # 显示市场行情
    st.markdown("## 🌍 A股市场概览")

    # 获取A股指数实时数据
    a_stock_indices_data = None
    try:
        a_stock_indices_data = get_index_data_sina()
    except Exception as e:
        st.error(f"⚠️ A股指数数据获取失败: {str(e)[:100]}...")
    
    # 显示A股指数 - 卡片形式
    if a_stock_indices_data:
        cols = st.columns(3)
        
        for idx, index in enumerate(MARKETS["A股"]["indices"]):
            if index["symbol"] in a_stock_indices_data:
                data = a_stock_indices_data[index["symbol"]]
                
                # 判断涨跌
                is_up = data["change"] >= 0
                color = "#ff4757" if not is_up else "#00ff88"
                bg_color = "rgba(255, 71, 87, 0.1)" if not is_up else "rgba(0, 255, 136, 0.1)"
                arrow = "▲" if is_up else "▼"
                
                with cols[idx]:
                    # 使用HTML创建卡片样式
                    card_html = f"""
                    <div style="
                        background: linear-gradient(135deg, {bg_color} 0%, rgba(255,255,255,0.05) 100%);
                        border-radius: 15px;
                        padding: 20px;
                        border: 1px solid rgba(255,255,255,0.1);
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        margin-bottom: 10px;
                    ">
                        <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-bottom: 8px;">
                            {index['name']}
                        </div>
                        <div style="font-size: 28px; font-weight: bold; color: #fff; margin-bottom: 10px;">
                            {data['price']:,.2f}
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="font-size: 16px; color: {color}; font-weight: bold;">
                                {arrow} {data['change']:+,.2f}
                            </div>
                            <div style="font-size: 16px; color: {color}; font-weight: bold;">
                                {data['change_percent']:+.2f}%
                            </div>
                        </div>
                        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.1);">
                            <div style="font-size: 12px; color: rgba(255,255,255,0.5);">
                                成交量: {data['volume']:,}
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 侧边栏 - 输入区域
    st.sidebar.header("📊 股票查询")
    
    # 获取股票列表
    stock_list = get_stock_list()
    
    # 初始化session state
    if 'last_search_query' not in st.session_state:
        st.session_state.last_search_query = ""
    if 'last_quick_select' not in st.session_state:
        st.session_state.last_quick_select = ""
    
    # 处理从自选股页面跳转过来的快速选择
    quick_select_value = ""
    auto_select_symbol = None
    
    # 检查是否有从自选股传来的查看请求
    if 'view_stock_code' in st.session_state and st.session_state.get('view_stock_code'):
        quick_select_value = f"{st.session_state['view_stock_code']} - {st.session_state['view_stock_name']}"
        auto_select_symbol = st.session_state['view_stock_symbol']
    
    # 搜索输入框（使用唯一key防止浏览器自动填充）
    search_query = st.sidebar.text_input(
        "输入股票代码或名称",
        value=quick_select_value,
        placeholder="如：茅台、600519",
        help="💡 输入关键词后，下方会显示匹配的股票列表",
        key="stock_search_input"
    )
    
    # 如果用户修改了搜索框内容，清空自选股跳转标记
    if search_query != quick_select_value and st.session_state.get('view_stock_code'):
        st.session_state['view_stock_code'] = None
        st.session_state['view_stock_name'] = None
        st.session_state['view_stock_symbol'] = None
        auto_select_symbol = None
    
    # 实时搜索并显示结果
    stock_symbol_from_search = None
    search_selected = False
    
    # 如果是从自选股跳转过来的，直接使用传入的symbol
    if auto_select_symbol:
        stock_symbol_from_search = auto_select_symbol
        search_selected = True
        # 显示选中的股票信息
        st.sidebar.success(f"✅ 已选择: {quick_select_value}")
    elif search_query:
        search_results = search_stock_by_name(search_query, stock_list)
        
        if search_results:
            # 使用radio按钮显示搜索结果（更紧凑）
            st.sidebar.markdown(f"**找到 {len(search_results)} 只股票：**")
            
            # 只显示前10个结果，避免列表太长
            display_results = search_results[:10]
            
            selected_display = st.sidebar.radio(
                "选择股票",
                options=[s['display'] for s in display_results],
                index=0,
                key="search_results",
                label_visibility="collapsed"
            )
            
            if selected_display:
                for stock in display_results:
                    if stock['display'] == selected_display:
                        stock_symbol_from_search = stock['symbol']
                        search_selected = True
                        break
            
            if len(search_results) > 10:
                st.sidebar.info(f"💡 还有 {len(search_results) - 10} 个结果，请输入更精确的关键词")
        else:
            st.sidebar.warning("⚠️ 未找到匹配的股票")
    else:
        st.sidebar.info("💡 请输入股票名称或代码")
    
    # 快速选择热门股票
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔥 快速选择热门股票")
    quick_stocks = st.sidebar.selectbox(
        "快速选择热门股票",
        ["", "600519 - 贵州茅台", "000001 - 平安银行", "000858 - 五粮液", "601318 - 中国平安", "000333 - 美的集团", "300750 - 宁德时代", "600036 - 招商银行"],
        key="quick_select",
        label_visibility="collapsed"
    )
    
    # 日期范围选择
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 日期范围")
    date_option = st.sidebar.radio(
        "选择时间范围",
        ["1个月", "3个月", "6个月", "1年"],
        index=0
    )
    
    # 根据选择设置日期范围
    days_map = {"1个月": 30, "3个月": 90, "6个月": 180, "1年": 365}
    days = days_map[date_option]
    start_date = datetime.now() - timedelta(days=days)
    end_date = datetime.now()
    
    # 检测用户操作：判断是搜索还是快速选择
    search_changed = search_query != st.session_state.last_search_query
    quick_changed = quick_stocks != st.session_state.last_quick_select
    
    # 更新session state
    st.session_state.last_search_query = search_query
    st.session_state.last_quick_select = quick_stocks
    
    # 确定最终使用哪个股票
    stock_symbol = None
    query_button = False
    
    # 如果搜索框有变化且有选择，使用搜索结果
    if search_changed and search_selected and stock_symbol_from_search:
        stock_symbol = stock_symbol_from_search
        query_button = True
    # 如果快速选择有变化且有选择，使用快速选择
    elif quick_changed and quick_stocks:
        code = quick_stocks.split(" - ")[0]
        if code.startswith('6') or code.startswith('5') or code.startswith('688'):
            stock_symbol = f"{code}.SS"
        else:
            stock_symbol = f"{code}.SZ"
        query_button = True
    # 否则，使用当前有效的选择（搜索优先）
    elif search_selected and stock_symbol_from_search:
        stock_symbol = stock_symbol_from_search
        query_button = True
    elif quick_stocks:
        code = quick_stocks.split(" - ")[0]
        if code.startswith('6') or code.startswith('5') or code.startswith('688'):
            stock_symbol = f"{code}.SS"
        else:
            stock_symbol = f"{code}.SZ"
        query_button = True
    
    # 添加清除缓存按钮
    st.sidebar.markdown("---")
    if st.sidebar.button("�️ 清除缓存"):
        st.cache_data.clear()
        st.success("✅ 缓存已清除！")
        st.rerun()
    
    # 主内容区域 - 股票详情
    if query_button and stock_symbol:
        try:
            with st.spinner(f"正在获取 {stock_symbol} 的数据..."):
                df, error, data_source = get_stock_data(stock_symbol, start_date, end_date)
                
                if error:
                    st.error(f"❌ {error}")
                    st.info("💡 提示：\n- 请检查股票代码是否正确\n- 仅支持A股查询")
                else:
                    # 从股票列表中获取中文名称
                    stock_code = stock_symbol.replace('.SS', '').replace('.SZ', '')
                    stock_name = stock_code
                    for stock in stock_list:
                        if stock['code'] == stock_code:
                            stock_name = stock['name']
                            break
                    
                    if df is None or df.empty:
                        if not error:
                            st.error(f"❌ 未找到股票代码 '{stock_symbol}' 的数据，请检查代码是否正确")
                    else:
                        # 获取实时价格
                        realtime_data = None
                        if '.SS' in stock_symbol or '.SZ' in stock_symbol:
                            realtime_data, _ = get_stock_realtime_sina(stock_symbol)
                        
                        if realtime_data:
                            current_price = realtime_data['price']
                            price_change = realtime_data['change']
                            price_change_percent = realtime_data['change_percent']
                            open_price = realtime_data['open']
                            high_price = realtime_data['high']
                            low_price = realtime_data['low']
                            volume = realtime_data['volume']
                            prev_close = realtime_data.get('prev_close', 0)
                            amount = realtime_data.get('amount', 0)
                            
                            # 计算振幅
                            if prev_close > 0:
                                amplitude = ((high_price - low_price) / prev_close) * 100
                            else:
                                amplitude = 0
                        else:
                            current_price = df['Close'].iloc[-1]
                            previous_close = df['Close'].iloc[-2] if len(df) > 1 else current_price
                            price_change = current_price - previous_close
                            price_change_percent = (price_change / previous_close) * 100
                            open_price = df['Open'].iloc[-1]
                            high_price = df['High'].iloc[-1]
                            low_price = df['Low'].iloc[-1]
                            volume = df['Volume'].iloc[-1]
                            prev_close = previous_close
                            amount = 0
                            
                            # 计算振幅
                            if previous_close > 0:
                                amplitude = ((high_price - low_price) / previous_close) * 100
                            else:
                                amplitude = 0
                        
                                # 显示股票标题卡片
                        is_up = price_change >= 0
                        color = "#00ff88" if is_up else "#ff4757"
                        bg_color = "rgba(0, 255, 136, 0.1)" if is_up else "rgba(255, 71, 87, 0.1)"
                        arrow = "▲" if is_up else "▼"
                        
                        header_html = f"""
                <div style="
                    background: linear-gradient(135deg, {bg_color} 0%, rgba(255,255,255,0.05) 100%);
                    border-radius: 15px;
                    padding: 25px;
                    margin-bottom: 20px;
                    border: 1px solid rgba(255,255,255,0.1);
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 28px; font-weight: bold; color: #fff; margin-bottom: 8px;">
                                {stock_name} <span style="font-size: 20px; color: rgba(255,255,255,0.7);">({stock_code})</span>
                            </div>
                            <div style="font-size: 13px; color: rgba(255,255,255,0.5);">
                                数据来源：{data_source if data_source else '新浪财经'}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 36px; font-weight: bold; color: {color};">
                                ¥{current_price:,.2f}
                            </div>
                            <div style="font-size: 18px; color: {color}; font-weight: bold;">
                                {arrow} {price_change:+,.2f} ({price_change_percent:+.2f}%)
                            </div>
                        </div>
                    </div>
                        </div>
                        """
                        st.markdown(header_html, unsafe_allow_html=True)
                        
                        # 公司简况入口
                        with st.expander("📋 查看公司简况", expanded=False):
                            with st.spinner("正在加载公司信息..."):
                                company_info = get_company_info_sina(stock_symbol)
                                
                                if company_info:
                                    # 基本信息
                                    st.markdown("### 📌 基本信息")
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.markdown(f"**公司名称：** {company_info.get('company_name', '暂无')}")
                                        st.markdown(f"**英文名称：** {company_info.get('english_name', '暂无')}")
                                        st.markdown(f"**法人代表：** {company_info.get('legal_person', '暂无')}")
                                        st.markdown(f"**总经理：** {company_info.get('general_manager', '暂无')}")
                                        st.markdown(f"**董事会秘书：** {company_info.get('secretary', '暂无')}")
                                        st.markdown(f"**注册资本：** {company_info.get('registered_capital', '暂无')}")
                                    with col_b:
                                        st.markdown(f"**所属行业：** {company_info.get('industry', '暂无')}")
                                        st.markdown(f"**上市日期：** {company_info.get('listing_date', '暂无')}")
                                        st.markdown(f"**员工人数：** {company_info.get('employees', '暂无')}")
                                        st.markdown(f"**公司电话：** {company_info.get('phone', '暂无')}")
                                        st.markdown(f"**电子信箱：** {company_info.get('email', '暂无')}")
                                        st.markdown(f"**公司网址：** {company_info.get('website', '暂无')}")
                                    
                                    st.markdown(f"**注册地址：** {company_info.get('address', '暂无')}")
                                    
                                    # 主营业务
                                    st.markdown("---")
                                    st.markdown("### 🏢 主营业务")
                                    st.write(company_info.get('business', '暂无'))
                                    
                                    # 公司简介
                                    st.markdown("---")
                                    st.markdown("### 📝 公司简介")
                                    st.write(company_info.get('introduction', '暂无'))
                                else:
                                    st.info("暂无公司简况信息")
                        
                        # 显示详细行情信息
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("昨收", f"¥{prev_close:,.2f}")
                        
                        with col2:
                            st.metric("今开", f"¥{open_price:,.2f}")
                        
                        with col3:
                            st.metric("最高", f"¥{high_price:,.2f}")
                        
                        with col4:
                            st.metric("最低", f"¥{low_price:,.2f}")
                        
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
    
    
elif page == "买入股票":
    # ==================== 买入股票页面 ====================
    if st.session_state.user:
        # 刷新用户资金信息
        user = db.get_user(st.session_state.user['username'])
        st.session_state.user = user
        # 获取股票列表
        stock_list = get_stock_list()
        show_trading_page(db, user, get_stock_realtime_sina, stock_list)
    else:
        st.warning("请先登录")

elif page == "我的自选":
    # ==================== 自选股页面 ====================
    if st.session_state.user:
        # 获取股票列表
        stock_list = get_stock_list()
        show_watchlist_page(db, st.session_state.user, get_stock_realtime_sina, stock_list)
    else:
        st.warning("请先登录")

elif page == "我的持仓":
    # ==================== 持仓页面 ====================
    if st.session_state.user:
        # 刷新用户资金信息
        user = db.get_user(st.session_state.user['username'])
        st.session_state.user = user
        show_positions_page(db, user, get_stock_realtime_sina)
    else:
        st.warning("请先登录")

elif page == "交易记录":
    # ==================== 交易记录页面 ====================
    if st.session_state.user:
        show_transactions_page(db, st.session_state.user)
    else:
        st.warning("请先登录")

# 页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.5); padding: 20px;">
    <p>📊 A股行情中心 | 数据来源：新浪财经</p>
    <p>支持A股实时行情查询和模拟交易</p>
</div>
""", unsafe_allow_html=True)