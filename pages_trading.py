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
    st.metric("💰 可用资金", f"¥{user['cash']:,.2f}")
    
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
    
    # 计算总资产和持仓数据
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
            'cost': cost,
            'profit': profit,
            'profit_percent': profit_percent
        })
    
    # 计算总盈亏（包括已实现盈亏和未实现盈亏）
    # 1. 未实现盈亏：当前持仓的盈亏
    total_cost = sum([p['cost'] for p in position_data])
    unrealized_profit = total_market_value - total_cost
    
    # 2. 已实现盈亏：通过交易记录计算
    all_transactions = db.get_all_transactions(user['user_id'])
    
    # 计算每只股票的已实现盈亏
    realized_profit = 0
    stock_buy_records = {}  # 记录每只股票的买入记录
    
    for trans in all_transactions:
        stock_code = trans['stock_code']
        
        if trans['type'] == 'BUY':
            # 记录买入
            if stock_code not in stock_buy_records:
                stock_buy_records[stock_code] = []
            stock_buy_records[stock_code].append({
                'quantity': trans['quantity'],
                'price': trans['price'],
                'amount': trans['amount']
            })
        
        elif trans['type'] == 'SELL':
            # 计算卖出盈亏
            if stock_code in stock_buy_records and stock_buy_records[stock_code]:
                # 计算平均买入成本
                total_buy_quantity = sum([r['quantity'] for r in stock_buy_records[stock_code]])
                total_buy_amount = sum([r['amount'] for r in stock_buy_records[stock_code]])
                avg_buy_price = total_buy_amount / total_buy_quantity if total_buy_quantity > 0 else 0
                
                # 计算这笔卖出的盈亏
                sell_amount = trans['amount']
                cost_amount = avg_buy_price * trans['quantity']
                profit = sell_amount - cost_amount
                realized_profit += profit
                
                # 更新买入记录（按比例减少）
                sell_quantity = trans['quantity']
                remaining_quantity = sell_quantity
                
                for record in stock_buy_records[stock_code][:]:
                    if remaining_quantity <= 0:
                        break
                    
                    if record['quantity'] <= remaining_quantity:
                        remaining_quantity -= record['quantity']
                        stock_buy_records[stock_code].remove(record)
                    else:
                        record['quantity'] -= remaining_quantity
                        record['amount'] = record['quantity'] * record['price']
                        remaining_quantity = 0
    
    # 总盈亏 = 已实现盈亏 + 未实现盈亏
    total_profit = realized_profit + unrealized_profit
    
    # 计算总投入（初始资金 - 当前总资产）
    initial_capital = 1000000  # 初始资金
    total_assets = user['cash'] + total_market_value
    total_invested = initial_capital  # 总投入就是初始资金
    total_profit_percent = (total_profit / total_invested * 100) if total_invested > 0 else 0
    
    # ==================== 数据统计面板 ====================
    st.markdown("### 📈 资产概览")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("总资产", f"¥{total_assets:,.2f}")
    with col2:
        st.metric("持仓市值", f"¥{total_market_value:,.2f}")
    with col3:
        st.metric("可用资金", f"¥{user['cash']:,.2f}")
    with col4:
        profit_color = "normal" if unrealized_profit >= 0 else "inverse"
        st.metric("未实现盈亏", f"¥{unrealized_profit:+,.2f}", delta_color=profit_color)
    with col5:
        total_profit_color = "normal" if total_profit >= 0 else "inverse"
        st.metric("总盈亏", f"¥{total_profit:+,.2f}", f"{total_profit_percent:+.2f}%", delta_color=total_profit_color)
    
    # 显示已实现盈亏
    if realized_profit != 0:
        st.info(f"💰 已实现盈亏: ¥{realized_profit:+,.2f}")
    
    if not positions:
        st.info("暂无持仓")
        return
    
    st.markdown("---")
    
    # ==================== 数据可视化 ====================
    st.markdown("### 📊 数据分析")
    
    # 创建两列布局
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        # 持仓分布饼图
        st.markdown("#### 持仓分布")
        import plotly.graph_objects as go
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=[f"{p['stock_name']}<br>({p['stock_code']})" for p in position_data],
            values=[p['market_value'] for p in position_data],
            hole=0.4,
            textinfo='label+percent',
            textposition='auto',
            marker=dict(
                colors=['#00ff88', '#00d4ff', '#ffd700', '#ff6b6b', '#a29bfe', '#fd79a8', '#fdcb6e', '#6c5ce7'],
                line=dict(color='#1e1e1e', width=2)
            )
        )])
        
        fig_pie.update_layout(
            showlegend=True,
            height=350,
            margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=10)
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with viz_col2:
        # 盈亏排行
        st.markdown("#### 盈亏排行")
        
        # 按盈亏排序
        sorted_positions = sorted(position_data, key=lambda x: x['profit'], reverse=True)
        
        for i, pos in enumerate(sorted_positions[:5]):  # 只显示前5名
            profit_color = "#00ff88" if pos['profit'] >= 0 else "#ff4757"
            rank_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
            
            st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.05);
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 8px;
                border-left: 3px solid {profit_color};
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 16px;">{rank_emoji}</span>
                        <span style="font-size: 14px; margin-left: 8px;">{pos['stock_name']}</span>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: {profit_color}; font-weight: bold;">
                            ¥{pos['profit']:+,.2f}
                        </div>
                        <div style="font-size: 12px; color: {profit_color};">
                            {pos['profit_percent']:+.2f}%
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ==================== 资产曲线图 ====================
    all_transactions = db.get_all_transactions(user['user_id'])
    if all_transactions:
        st.markdown("---")
        st.markdown("### 📈 资产变化曲线")
        
        # 计算每次交易后的资产
        import pandas as pd
        from datetime import datetime as dt
        
        asset_history = []
        current_cash = 1000000.0  # 初始资金
        holdings = {}  # 持仓 {stock_code: {'quantity': x, 'avg_cost': y}}
        
        for trans in all_transactions:
            stock_code = trans['stock_code']
            
            if trans['type'] == 'BUY':
                # 买入
                current_cash -= trans['amount']
                if stock_code in holdings:
                    old_qty = holdings[stock_code]['quantity']
                    old_cost = holdings[stock_code]['avg_cost']
                    new_qty = old_qty + trans['quantity']
                    new_cost = (old_qty * old_cost + trans['amount']) / new_qty
                    holdings[stock_code] = {'quantity': new_qty, 'avg_cost': new_cost}
                else:
                    holdings[stock_code] = {'quantity': trans['quantity'], 'avg_cost': trans['price']}
            else:
                # 卖出
                current_cash += trans['amount']
                if stock_code in holdings:
                    holdings[stock_code]['quantity'] -= trans['quantity']
                    if holdings[stock_code]['quantity'] <= 0:
                        del holdings[stock_code]
            
            # 计算当前持仓市值（使用当时的价格）
            holdings_value = sum([h['quantity'] * h['avg_cost'] for h in holdings.values()])
            total_asset = current_cash + holdings_value
            
            asset_history.append({
                'time': trans['time'],
                'total_asset': total_asset,
                'cash': current_cash,
                'holdings_value': holdings_value
            })
        
        # 创建资产曲线图
        df_asset = pd.DataFrame(asset_history)
        df_asset['time'] = pd.to_datetime(df_asset['time'])
        
        fig_asset = go.Figure()
        
        fig_asset.add_trace(go.Scatter(
            x=df_asset['time'],
            y=df_asset['total_asset'],
            mode='lines+markers',
            name='总资产',
            line=dict(color='#00ff88', width=3),
            fill='tozeroy',
            fillcolor='rgba(0, 255, 136, 0.1)'
        ))
        
        fig_asset.add_trace(go.Scatter(
            x=df_asset['time'],
            y=df_asset['cash'],
            mode='lines',
            name='现金',
            line=dict(color='#00d4ff', width=2, dash='dash')
        ))
        
        fig_asset.add_trace(go.Scatter(
            x=df_asset['time'],
            y=df_asset['holdings_value'],
            mode='lines',
            name='持仓市值',
            line=dict(color='#ffd700', width=2, dash='dot')
        ))
        
        # 添加初始资金参考线
        fig_asset.add_hline(
            y=1000000,
            line_dash="dash",
            line_color="rgba(255,255,255,0.3)",
            annotation_text="初始资金",
            annotation_position="right"
        )
        
        fig_asset.update_layout(
            title="资产变化趋势",
            xaxis_title="时间",
            yaxis_title="金额（元）",
            hovermode='x unified',
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        
        st.plotly_chart(fig_asset, use_container_width=True)
    
    st.markdown("---")
    
    # ==================== 持仓明细 ====================
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
                col_a, col_b = st.columns([1, 1])
                
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
                
                # 显示预计卖出金额（在列布局之后，按钮之前）
                if sell_quantity > 0 and sell_price > 0.01:
                    sell_amount = sell_quantity * sell_price
                    st.info(f"💰 预计卖出金额: ¥{sell_amount:,.2f}")
                
                # 确认卖出按钮
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


def show_transactions_page(db, user):
    """显示交易记录页面"""
    st.markdown("## 📜 交易记录")
    
    # 获取交易记录
    transactions = db.get_transactions(user['user_id'], limit=100)
    
    if not transactions:
        st.info("💡 暂无交易记录，开始您的第一笔交易吧！")
        return
    
    # 统计信息
    import pandas as pd
    from datetime import datetime, timedelta
    
    buy_count = sum(1 for t in transactions if t['type'] == 'BUY')
    sell_count = sum(1 for t in transactions if t['type'] == 'SELL')
    total_buy_amount = sum(t['amount'] for t in transactions if t['type'] == 'BUY')
    total_sell_amount = sum(t['amount'] for t in transactions if t['type'] == 'SELL')
    
    # 显示统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(255,255,255,0.05) 100%);
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(0, 255, 136, 0.3);
        ">
            <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-bottom: 5px;">买入次数</div>
            <div style="font-size: 24px; font-weight: bold; color: #00ff88;">{buy_count}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(255, 71, 87, 0.1) 0%, rgba(255,255,255,0.05) 100%);
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(255, 71, 87, 0.3);
        ">
            <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-bottom: 5px;">卖出次数</div>
            <div style="font-size: 24px; font-weight: bold; color: #ff4757;">{sell_count}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(255,255,255,0.05) 100%);
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(0, 255, 136, 0.3);
        ">
            <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-bottom: 5px;">买入总额</div>
            <div style="font-size: 20px; font-weight: bold; color: #00ff88;">¥{total_buy_amount:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(255, 71, 87, 0.1) 0%, rgba(255,255,255,0.05) 100%);
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(255, 71, 87, 0.3);
        ">
            <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-bottom: 5px;">卖出总额</div>
            <div style="font-size: 20px; font-weight: bold; color: #ff4757;">¥{total_sell_amount:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 筛选选项
    col_filter1, col_filter2 = st.columns([1, 3])
    
    with col_filter1:
        filter_type = st.selectbox(
            "交易类型",
            ["全部", "买入", "卖出"],
            key="trans_filter_type"
        )
    
    with col_filter2:
        filter_stock = st.text_input(
            "搜索股票",
            placeholder="输入股票代码或名称",
            key="trans_filter_stock"
        )
    
    # 转换为DataFrame并应用筛选
    trans_data = []
    for t in transactions:
        # 解析时间字符串并转换为本地时间
        try:
            time_str = t['time']
            if isinstance(time_str, str):
                utc_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                local_time = utc_time + timedelta(hours=8)
                time_display = local_time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                time_display = str(time_str)
        except:
            time_display = str(t['time'])
        
        trans_type = '买入' if t['type'] == 'BUY' else '卖出'
        
        # 应用筛选
        if filter_type != "全部" and trans_type != filter_type:
            continue
        
        if filter_stock and filter_stock not in t['stock_code'] and filter_stock not in t['stock_name']:
            continue
        
        trans_data.append({
            '时间': time_display,
            '股票代码': t['stock_code'],
            '股票名称': t['stock_name'],
            '类型': trans_type,
            '数量': t['quantity'],
            '价格': t['price'],
            '金额': t['amount'],
            '_type_raw': t['type']  # 用于样式判断
        })
    
    if not trans_data:
        st.info("💡 没有符合条件的交易记录")
        return
    
    # 使用卡片式展示
    st.markdown(f"### 📋 交易明细 ({len(trans_data)} 条记录)")
    
    for idx, trans in enumerate(trans_data):
        is_buy = trans['_type_raw'] == 'BUY'
        bg_color = "rgba(0, 255, 136, 0.05)" if is_buy else "rgba(255, 71, 87, 0.05)"
        border_color = "rgba(0, 255, 136, 0.3)" if is_buy else "rgba(255, 71, 87, 0.3)"
        type_color = "#00ff88" if is_buy else "#ff4757"
        type_icon = "🟢" if is_buy else "🔴"
        
        card_html = f"""
        <div style="
            background: {bg_color};
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            border: 1px solid {border_color};
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 18px; margin-right: 8px;">{type_icon}</span>
                        <span style="font-size: 16px; font-weight: bold; color: {type_color};">{trans['类型']}</span>
                        <span style="font-size: 16px; font-weight: bold; color: #fff; margin-left: 15px;">{trans['股票代码']} - {trans['股票名称']}</span>
                    </div>
                    <div style="display: flex; gap: 20px; font-size: 14px; color: rgba(255,255,255,0.7);">
                        <span>数量: <span style="color: #fff; font-weight: bold;">{trans['数量']}</span> 股</span>
                        <span>价格: <span style="color: #fff; font-weight: bold;">¥{trans['价格']:.2f}</span></span>
                        <span>金额: <span style="color: {type_color}; font-weight: bold;">¥{trans['金额']:,.2f}</span></span>
                    </div>
                </div>
                <div style="text-align: right; color: rgba(255,255,255,0.5); font-size: 12px;">
                    {trans['时间']}
                </div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)



def show_watchlist_page(db, user, get_stock_realtime_sina_func, stock_list):
    """显示自选股页面"""
    st.markdown("## ⭐ 我的自选股")
    
    # 获取自选股列表
    watchlist = db.get_watchlist(user['user_id'])
    
    # ==================== 添加自选股 ====================
    with st.expander("➕ 添加自选股", expanded=False):
        st.markdown("#### 搜索股票")
        
        # 初始化session state
        if 'watchlist_search_query' not in st.session_state:
            st.session_state.watchlist_search_query = ""
        
        search_query = st.text_input(
            "输入股票代码或名称",
            value=st.session_state.watchlist_search_query,
            placeholder="如：茅台、600519",
            key="watchlist_search_input"
        )
        
        # 实时搜索并显示结果
        if search_query:
            st.session_state.watchlist_search_query = search_query
            
            # 搜索匹配的股票
            search_results = []
            for stock in stock_list:
                if search_query.upper() in stock['code'].upper() or search_query in stock['name']:
                    search_results.append(stock)
                    if len(search_results) >= 10:
                        break
            
            if search_results:
                st.markdown(f"**找到 {len(search_results)} 只股票：**")
                
                # 使用按钮显示搜索结果
                for stock in search_results:
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(f"📊 {stock['display']}")
                    with col_b:
                        if st.button("添加", key=f"add_watch_{stock['code']}", use_container_width=True):
                            success, message = db.add_to_watchlist(
                                user['user_id'],
                                stock['code'],
                                stock['name']
                            )
                            if success:
                                st.session_state.watchlist_search_query = ""
                                st.rerun()
                            else:
                                st.error(message)
            else:
                st.warning("⚠️ 未找到匹配的股票")
    
    st.markdown("---")
    
    # ==================== 自选股列表 ====================
    if not watchlist:
        st.info("💡 暂无自选股，请添加关注的股票")
        return
    
    st.markdown(f"### 📋 自选股列表（共 {len(watchlist)} 只）")
    
    # 获取所有自选股的实时行情
    watchlist_data = []
    for stock in watchlist:
        stock_code = stock['stock_code']
        symbol = f"{stock_code}.SS" if stock_code.startswith('6') or stock_code.startswith('5') or stock_code.startswith('688') else f"{stock_code}.SZ"
        
        # 获取实时价格
        realtime_data, _ = get_stock_realtime_sina_func(symbol)
        
        if realtime_data:
            current_price = realtime_data['price']
            change = realtime_data['change']
            change_percent = realtime_data['change_percent']
            
            watchlist_data.append({
                'stock_code': stock_code,
                'stock_name': stock['stock_name'],
                'current_price': current_price,
                'change': change,
                'change_percent': change_percent,
                'symbol': symbol
            })
    
    # 显示自选股卡片
    for stock_data in watchlist_data:
        is_up = stock_data['change'] >= 0
        arrow = "▲" if is_up else "▼"
        
        # 使用 Streamlit 原生组件
        with st.container():
            # 使用列布局
            col_info, col_price, col_actions = st.columns([3, 2, 2])
            
            with col_info:
                # 股票名称和代码
                st.markdown(f"**{stock_data['stock_name']}** ({stock_data['stock_code']})")
                st.caption(f"当前价格: ¥{stock_data['current_price']:.2f}")
            
            with col_price:
                # 涨跌信息
                change_text = f"{arrow} {stock_data['change']:+.2f} ({stock_data['change_percent']:+.2f}%)"
                if is_up:
                    st.success(change_text)
                else:
                    st.error(change_text)
            
            with col_actions:
                # 操作按钮
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("📈 查看", key=f"view_{stock_data['stock_code']}", use_container_width=True):
                        # 设置要查看的股票信息
                        st.session_state['view_stock_code'] = stock_data['stock_code']
                        st.session_state['view_stock_name'] = stock_data['stock_name']
                        st.session_state['view_stock_symbol'] = stock_data['symbol']
                        # 切换到行情查询页面
                        st.session_state.current_page = "行情查询"
                        st.rerun()
                
                with col_btn2:
                    if st.button("🗑️ 移除", key=f"remove_{stock_data['stock_code']}", use_container_width=True):
                        success, message = db.remove_from_watchlist(
                            user['user_id'],
                            stock_data['stock_code']
                        )
                        if success:
                            st.rerun()
                        else:
                            st.error(message)
            
            st.markdown("---")
