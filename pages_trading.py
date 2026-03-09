# -*- coding: utf-8 -*-
"""
模拟交易页面模块
"""

import streamlit as st
from trading_db import TradingDB
from datetime import datetime

def show_trading_page(db, user, get_stock_realtime_sina_func, stock_list):
    """显示模拟交易页面"""
    st.markdown("## 💰 买入股票")
    
    # 显示账户信息
    col1, col2 = st.columns(2)
    with col1:
        st.metric("可用资金", f"¥{user['cash']:,.2f}")
    with col2:
        st.metric("用户名", user['username'])
    
    st.markdown("---")
    
    # 交易表单
    st.markdown("### 📝 选择要买入的股票")
    
    # 初始化session state
    if 'trading_stock_code' not in st.session_state:
        st.session_state.trading_stock_code = ""
    if 'trading_stock_name' not in st.session_state:
        st.session_state.trading_stock_name = ""
    if 'trading_search_query' not in st.session_state:
        st.session_state.trading_search_query = ""
    
    # 股票搜索
    st.markdown("#### 🔍 选择股票")
    search_query = st.text_input(
        "输入股票代码或名称",
        value=st.session_state.trading_search_query,
        placeholder="如：茅台、600519",
        key="trading_search_input"
    )
    
    # 实时搜索并显示结果
    if search_query:
        st.session_state.trading_search_query = search_query
        
        # 搜索匹配的股票
        search_results = []
        for stock in stock_list:
            if search_query.upper() in stock['code'].upper() or search_query in stock['name']:
                search_results.append(stock)
                if len(search_results) >= 10:
                    break
        
        if search_results:
            st.markdown(f"**找到 {len(search_results)} 只股票，点击选择：**")
            
            # 使用按钮显示搜索结果
            for stock in search_results:
                if st.button(
                    f"📊 {stock['display']}", 
                    key=f"select_{stock['code']}",
                    use_container_width=True
                ):
                    st.session_state.trading_stock_code = stock['code']
                    st.session_state.trading_stock_name = stock['name']
                    st.session_state.trading_search_query = ""
                    st.rerun()
        else:
            st.warning("⚠️ 未找到匹配的股票")
    
    # 显示已选择的股票
    if st.session_state.trading_stock_code and st.session_state.trading_stock_name:
        st.success(f"✅ 已选择：{st.session_state.trading_stock_code} - {st.session_state.trading_stock_name}")
        
        # 显示当前价格
        symbol = f"{st.session_state.trading_stock_code}.SS" if st.session_state.trading_stock_code.startswith('6') or st.session_state.trading_stock_code.startswith('5') or st.session_state.trading_stock_code.startswith('688') else f"{st.session_state.trading_stock_code}.SZ"
        realtime_data, _ = get_stock_realtime_sina_func(symbol)
        
        default_price = 0.01
        if realtime_data and realtime_data['price'] > 0:
            current_price = realtime_data['price']
            st.info(f"💡 当前价格: ¥{current_price:.2f}")
            default_price = current_price
        
        st.markdown("---")
        
        # 交易参数
        col_a, col_b = st.columns(2)
        
        with col_a:
            quantity = st.number_input("数量（股，最小100股）", min_value=100, step=100, value=100)
        
        with col_b:
            price = st.number_input("价格（元）", min_value=0.01, step=0.01, value=default_price)
        
        # 计算金额
        if price > 0.01 and quantity > 0:
            total_amount = price * quantity
            st.markdown(f"**交易金额：** ¥{total_amount:,.2f}")
        
        st.markdown("---")
        
        # 买入按钮
        if st.button("🟢 买入", type="primary", use_container_width=True):
            if price <= 0.01:
                st.error("请输入有效价格")
            else:
                success, message = db.buy_stock(
                    user['user_id'],
                    st.session_state.trading_stock_code,
                    st.session_state.trading_stock_name,
                    quantity,
                    price
                )
                if success:
                    st.success(message)
                    # 清空搜索
                    st.session_state.trading_search_query = ""
                    st.session_state.trading_stock_code = ""
                    st.session_state.trading_stock_name = ""
                    st.rerun()
                else:
                    st.error(message)
        
        st.info("💡 提示：卖出操作请前往「我的持仓」页面")
    else:
        st.info("💡 请先搜索并选择要交易的股票")


def show_positions_page(db, user, get_stock_realtime_sina_func):
    """显示持仓页面"""
    st.markdown("## 📊 我的持仓")
    
    # 获取持仓
    positions = db.get_positions(user['user_id'])
    
    if not positions:
        st.info("暂无持仓")
        return
    
    # 计算总资产
    total_market_value = 0
    position_data = []
    
    for pos in positions:
        stock_code = pos['stock_code']
        symbol = f"{stock_code}.SS" if stock_code.startswith('6') or stock_code.startswith('5') or stock_code.startswith('688') else f"{stock_code}.SZ"
        
        # 获取当前价格
        realtime_data, _ = get_stock_realtime_sina_func(symbol)
        current_price = realtime_data['price'] if realtime_data else pos['avg_cost']
        
        # 计算盈亏
        market_value = current_price * pos['quantity']
        cost = pos['avg_cost'] * pos['quantity']
        profit = market_value - cost
        profit_percent = (profit / cost) * 100 if cost > 0 else 0
        
        total_market_value += market_value
        
        position_data.append({
            'stock_code': stock_code,
            'stock_name': pos['stock_name'],
            'quantity': pos['quantity'],
            'avg_cost': pos['avg_cost'],
            'current_price': current_price,
            'market_value': market_value,
            'profit': profit,
            'profit_percent': profit_percent
        })
    
    # 显示总资产
    total_assets = user['cash'] + total_market_value
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总资产", f"¥{total_assets:,.2f}")
    with col2:
        st.metric("持仓市值", f"¥{total_market_value:,.2f}")
    with col3:
        st.metric("可用资金", f"¥{user['cash']:,.2f}")
    
    st.markdown("---")
    
    # 显示持仓列表 - 使用卡片形式，每个持仓一个卡片
    st.markdown("### 📋 持仓明细")
    
    for pos_data in position_data:
        # 判断盈亏颜色
        is_profit = pos_data['profit'] >= 0
        profit_color = "#00ff88" if is_profit else "#ff4757"
        bg_color = "rgba(0, 255, 136, 0.05)" if is_profit else "rgba(255, 71, 87, 0.05)"
        
        # 创建持仓卡片
        with st.container():
            st.markdown(f"""
            <div style="
                background: {bg_color};
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                border: 1px solid rgba(255,255,255,0.1);
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 18px; font-weight: bold; color: #fff;">
                            {pos_data['stock_name']} ({pos_data['stock_code']})
                        </div>
                        <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-top: 5px;">
                            持仓: {pos_data['quantity']} 股 | 成本: ¥{pos_data['avg_cost']:.2f} | 现价: ¥{pos_data['current_price']:.2f}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 16px; color: {profit_color}; font-weight: bold;">
                            {pos_data['profit']:+,.2f} ({pos_data['profit_percent']:+.2f}%)
                        </div>
                        <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-top: 5px;">
                            市值: ¥{pos_data['market_value']:,.2f}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 卖出操作区域
            with st.expander(f"🔴 卖出 {pos_data['stock_name']}", expanded=False):
                col_a, col_b, col_c = st.columns([2, 2, 1])
                
                with col_a:
                    # A股规则：卖出最小100股，但如果持仓不足100股可以全部卖出
                    if pos_data['quantity'] < 100:
                        # 持仓不足100股，只能全部卖出
                        sell_quantity = st.number_input(
                            f"卖出数量（股，不足100股只能全部卖出）",
                            min_value=pos_data['quantity'],
                            max_value=pos_data['quantity'],
                            step=pos_data['quantity'],
                            value=pos_data['quantity'],
                            key=f"sell_qty_{pos_data['stock_code']}",
                            disabled=True
                        )
                        st.info(f"💡 持仓不足100股，只能全部卖出")
                    else:
                        # 持仓大于等于100股，按100股倍数卖出
                        # 默认值为持仓数量（向下取整到100的倍数）
                        default_sell_qty = (pos_data['quantity'] // 100) * 100
                        if default_sell_qty == 0:
                            default_sell_qty = 100
                        
                        sell_quantity = st.number_input(
                            f"卖出数量（股，100股的倍数，最多{pos_data['quantity']}股）",
                            min_value=100,
                            max_value=pos_data['quantity'],
                            step=100,
                            value=default_sell_qty,
                            key=f"sell_qty_{pos_data['stock_code']}"
                        )
                
                with col_b:
                    sell_price = st.number_input(
                        "卖出价格（元）",
                        min_value=0.01,
                        step=0.01,
                        value=pos_data['current_price'],
                        key=f"sell_price_{pos_data['stock_code']}"
                    )
                
                with col_c:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button(
                        "确认卖出",
                        type="primary",
                        key=f"sell_btn_{pos_data['stock_code']}",
                        use_container_width=True
                    ):
                        # 验证卖出数量
                        if sell_quantity > pos_data['quantity']:
                            st.error(f"卖出数量不能超过持仓数量 {pos_data['quantity']}")
                        elif pos_data['quantity'] >= 100 and sell_quantity % 100 != 0:
                            st.error("卖出数量必须是100股的倍数")
                        elif sell_price <= 0.01:
                            st.error("请输入有效价格")
                        else:
                            success, message = db.sell_stock(
                                user['user_id'],
                                pos_data['stock_code'],
                                sell_quantity,
                                sell_price
                            )
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                
                # 显示预计卖出金额
                if sell_quantity > 0 and sell_price > 0.01:
                    sell_amount = sell_quantity * sell_price
                    st.info(f"💰 预计卖出金额: ¥{sell_amount:,.2f}")


def show_transactions_page(db, user):
    """显示交易记录页面"""
    st.markdown("## 📜 交易记录")
    
    # 获取交易记录
    transactions = db.get_transactions(user['user_id'], limit=100)
    
    if not transactions:
        st.info("暂无交易记录")
        return
    
    # 转换为DataFrame
    import pandas as pd
    trans_data = []
    for t in transactions:
        trans_data.append({
            '时间': t['time'],
            '股票代码': t['stock_code'],
            '股票名称': t['stock_name'],
            '类型': '买入' if t['type'] == 'BUY' else '卖出',
            '数量': t['quantity'],
            '价格': f"¥{t['price']:.2f}",
            '金额': f"¥{t['amount']:,.2f}"
        })
    
    df = pd.DataFrame(trans_data)
    st.dataframe(df, use_container_width=True, height=600)
