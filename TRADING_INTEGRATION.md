# 模拟交易系统集成说明

## 📦 已创建的文件

1. **trading_db.py** - 数据库管理模块
   - SQLite数据库操作
   - 用户管理、持仓管理、交易记录

2. **pages_trading.py** - 交易页面模块
   - 模拟交易页面
   - 持仓查看页面
   - 交易记录页面

## 🗄️ 数据库设计

### 表结构

**users表** - 用户信息
- user_id: 用户ID（主键）
- username: 用户名（唯一）
- cash: 可用资金
- created_at: 创建时间

**positions表** - 持仓信息
- position_id: 持仓ID（主键）
- user_id: 用户ID
- stock_code: 股票代码
- stock_name: 股票名称
- quantity: 持仓数量
- avg_cost: 平均成本
- created_at/updated_at: 时间戳

**transactions表** - 交易记录
- transaction_id: 交易ID（主键）
- user_id: 用户ID
- stock_code: 股票代码
- stock_name: 股票名称
- transaction_type: 交易类型（BUY/SELL）
- quantity: 数量
- price: 价格
- amount: 金额
- created_at: 交易时间

## 🔧 集成步骤

### 1. 在stock_app.py中添加用户登录

```python
# 初始化数据库
db = TradingDB()

# 用户登录/注册
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    # 显示登录界面
    username = st.sidebar.text_input("用户名")
    if st.sidebar.button("登录/注册"):
        user = db.get_user(username)
        if user is None:
            # 创建新用户，初始资金100万
            user_id, error = db.create_user(username, 1000000.0)
            if user_id:
                user = db.get_user(username)
                st.session_state.user = user
                st.rerun()
        else:
            st.session_state.user = user
            st.rerun()
else:
    # 已登录，显示用户信息
    st.sidebar.success(f"👤 {st.session_state.user['username']}")
    if st.sidebar.button("退出登录"):
        st.session_state.user = None
        st.rerun()
```

### 2. 根据页面选择显示不同内容

```python
from pages_trading import show_trading_page, show_positions_page, show_transactions_page

if st.session_state.user:
    if page == "行情查询":
        # 原有的行情查询代码
        pass
    elif page == "模拟交易":
        show_trading_page(db, st.session_state.user, get_stock_realtime_sina)
    elif page == "我的持仓":
        show_positions_page(db, st.session_state.user, get_stock_realtime_sina)
    elif page == "交易记录":
        show_transactions_page(db, st.session_state.user)
else:
    st.info("请先登录")
```

## 💡 功能特点

### 模拟交易
- ✅ 买入股票（检查资金是否足够）
- ✅ 卖出股票（检查持仓是否足够）
- ✅ 自动获取当前价格
- ✅ 计算交易金额
- ✅ 更新持仓和资金

### 持仓管理
- ✅ 查看所有持仓
- ✅ 实时计算盈亏
- ✅ 显示总资产、持仓市值、可用资金
- ✅ 成本价、当前价对比

### 交易记录
- ✅ 查看所有交易历史
- ✅ 按时间倒序排列
- ✅ 显示买入/卖出类型

## 🎯 使用流程

1. **用户注册/登录**
   - 输入用户名
   - 新用户自动创建，初始资金100万

2. **查看行情**
   - 搜索股票
   - 查看实时价格和K线图

3. **模拟交易**
   - 输入股票代码和名称
   - 输入数量和价格（可自动获取当前价）
   - 点击买入或卖出

4. **查看持仓**
   - 查看所有持仓股票
   - 实时盈亏计算
   - 总资产统计

5. **查看记录**
   - 查看所有交易历史
   - 分析交易行为

## 📝 注意事项

1. **数据持久化**
   - 使用SQLite数据库，数据保存在`trading.db`文件中
   - 重启应用数据不会丢失

2. **资金管理**
   - 初始资金：100万元
   - 买入时检查资金是否足够
   - 卖出时检查持仓是否足够

3. **价格获取**
   - 使用新浪财经API获取实时价格
   - 也可以手动输入价格

4. **交易规则**
   - 最小交易单位：100股
   - 支持A股所有股票

## 🚀 扩展功能建议

1. **止盈止损**
   - 设置目标价位自动卖出
   - 设置止损价位自动卖出

2. **收益统计**
   - 总收益率
   - 日收益曲线
   - 最佳/最差交易

3. **策略回测**
   - 历史数据回测
   - 策略效果评估

4. **多用户支持**
   - 用户权限管理
   - 排行榜功能

5. **实时提醒**
   - 价格提醒
   - 持仓预警
