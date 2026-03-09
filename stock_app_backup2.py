"""
股票行情展示系统 - Streamlit版本
功能：获取股票数据、展示K线图、实时价格、三大市场行情
支持Alpha Vantage、Yahoo Finance和akshare多数据源
作者：AI Assistant
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

# 自定义CSS样式 - 深色模式
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    /* 全局深色背景 */
    .stApp {
        background-color: #0e1117 !important;
        color: #fafafa !important;
    }
    
    .main {
        background: linear-gradient(135deg, #0e1117 0%, #1a1d23 50%, #0e1117 100%);
    }
    
    /* 标题样式 */
    .main-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00f5ff, #00d4ff, #00ff88, #00f5ff);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
        animation: gradient 3s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* 市场卡片 */
    .market-card {
        background: linear-gradient(135deg, rgba(30,33,40,0.9) 0%, rgba(20,23,28,0.95) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 245, 255, 0.2);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        transition: all 0.3s ease;
        margin-bottom: 12px;
    }
    
    .market-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px 0 rgba(0, 245, 255, 0.3);
        border-color: rgba(0, 245, 255, 0.5);
        background: linear-gradient(135deg, rgba(40,43,50,0.95) 0%, rgba(30,33,38,0.98) 100%);
    }
    
    /* 指数卡片头部 */
    .index-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    
    .index-header .index-name {
        font-size: 1.1rem;
        font-weight: bold;
        color: #fff;
    }
    
    .index-header .index-code {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.5);
    }
    
    /* 指数详细信息 */
    .index-detail {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        color: rgba(255,255,255,0.7);
        margin-top: 12px;
        padding-top: 10px;
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    
    .index-detail span {
        padding: 2px 8px;
        background: rgba(0, 245, 255, 0.1);
        border-radius: 4px;
    }
    
    /* 价格颜色 */
    .price-up {
        color: #00ff88;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }
    
    .price-down {
        color: #ff4757;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(255, 71, 87, 0.5);
    }
    
    /* 指标卡片 */
    .metric-card {
        background: linear-gradient(135deg, rgba(30,33,40,0.9) 0%, rgba(20,23,28,0.95) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 245, 255, 0.2);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.02);
        box-shadow: 0 12px 40px 0 rgba(0, 245, 255, 0.4);
        border-color: rgba(0, 245, 255, 0.4);
    }
    
    /* 按钮样式 */
    .stButton>button {
        background: linear-gradient(90deg, #00f5ff, #00ff88);
        color: #0e1117;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 245, 255, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 245, 255, 0.6);
    }
    
    /* 市场标题 */
    .market-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.2rem;
        color: #00f5ff;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .index-name {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.7);
        margin-bottom: 5px;
    }
    
    .index-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        font-weight: bold;
        color: #fff;
        margin-bottom: 5px;
    }
    
    .index-change {
        font-size: 1rem;
        font-weight: bold;
    }
    
    /* 股票卡片 */
    .stock-card {
        background: linear-gradient(135deg, rgba(30,33,40,0.8) 0%, rgba(20,23,28,0.9) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 245, 255, 0.15);
        border-radius: 12px;
        padding: 15px;
        transition: all 0.3s ease;
        color: #fff;
    }
    
    .stock-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0, 245, 255, 0.3);
        border-color: rgba(0, 245, 255, 0.4);
    }
    
    /* 侧边栏样式 - 强制深色背景 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0e1117 0%, #1a1d23 100%) !important;
        border-right: 1px solid rgba(0, 245, 255, 0.1) !important;
    }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0e1117 0%, #1a1d23 100%) !important;
        border-right: 1px solid rgba(0, 245, 255, 0.1) !important;
    }
    
    /* 侧边栏内容区域 */
    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }
    
    section[data-testid="stSidebar"] > div > div {
        background: transparent !important;
    }
    
    section[data-testid="stSidebar"] > div > div > div {
        background: transparent !important;
    }
    
    /* 侧边栏所有元素 */
    section[data-testid="stSidebar"] * {
        color: #fafafa !important;
        background-color: transparent !important;
    }
    
    /* 侧边栏标题 */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #00f5ff !important;
    }
    
    /* 侧边栏段落 */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #fafafa !important;
    }
    
    /* 侧边栏输入框 */
    section[data-testid="stSidebar"] input {
        background: rgba(30,33,40,0.8) !important;
        border: 1px solid rgba(0, 245, 255, 0.3) !important;
        color: #fafafa !important;
    }
    
    /* 侧边栏按钮 */
    section[data-testid="stSidebar"] button {
        background: rgba(30,33,40,0.8) !important;
        color: #fafafa !important;
        border: 1px solid rgba(0, 245, 255, 0.3) !important;
    }
    
    section[data-testid="stSidebar"] button:hover {
        background: rgba(0, 245, 255, 0.1) !important;
        border-color: rgba(0, 245, 255, 0.5) !important;
    }
    
    /* 侧边栏单选按钮 */
    section[data-testid="stSidebar"] .stRadio > div {
        background: rgba(30,33,40,0.5) !important;
        border-radius: 10px;
        padding: 10px;
    }
    
    section[data-testid="stSidebar"] .stRadio label {
        color: #fafafa !important;
    }
    
    section[data-testid="stSidebar"] .stRadio input[type="radio"] {
        filter: invert(1);
    }
    
    /* 侧边栏下拉框 */
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(30,33,40,0.8) !important;
        border: 1px solid rgba(0, 245, 255, 0.3) !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox div[role="listbox"] {
        background: #1a1d23 !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox div[role="option"] {
        background: #1a1d23 !important;
        color: #fafafa !important;
    }
    
    /* 侧边栏日期选择器 */
    section[data-testid="stSidebar"] .stDateInput > div > div {
        background: rgba(30,33,40,0.8) !important;
        border: 1px solid rgba(0, 245, 255, 0.3) !important;
    }
    
    section[data-testid="stSidebar"] .stDateInput input {
        background: rgba(30,33,40,0.8) !important;
        color: #fafafa !important;
    }
    
    /* 侧边栏分隔线 */
    section[data-testid="stSidebar"] hr {
        border-color: rgba(0, 245, 255, 0.2) !important;
    }
    
    /* 侧边栏图标 */
    section[data-testid="stSidebar"] svg {
        fill: #00f5ff !important;
    }
    
    /* 侧边栏消息提示 */
    section[data-testid="stSidebar"] .stSuccess {
        background: rgba(0, 255, 136, 0.1) !important;
        color: #00ff88 !important;
        border: 1px solid rgba(0, 255, 136, 0.3) !important;
    }
    
    section[data-testid="stSidebar"] .stError {
        background: rgba(255, 71, 87, 0.1) !important;
        color: #ff4757 !important;
        border: 1px solid rgba(255, 71, 87, 0.3) !important;
    }
    
    section[data-testid="stSidebar"] .stWarning {
        background: rgba(255, 193, 7, 0.1) !important;
        color: #ffc107 !important;
        border: 1px solid rgba(255, 193, 7, 0.3) !important;
    }
    
    section[data-testid="stSidebar"] .stInfo {
        background: rgba(0, 245, 255, 0.1) !important;
        color: #00f5ff !important;
        border: 1px solid rgba(0, 245, 255, 0.3) !important;
    }
    
    /* 强制侧边栏背景 - 使用多个选择器 */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebar"] > div > div,
    [data-testid="stSidebar"] > div > div > div,
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarContent"] > div,
    [data-testid="stSidebarContent"] > div > div {
        background: linear-gradient(180deg, #0e1117 0%, #1a1d23 100%) !important;
        background-color: #0e1117 !important;
    }
    
    /* 侧边栏所有div背景透明 */
    section[data-testid="stSidebar"] div:not([data-testid="stSidebar"]):not([data-testid="stSidebarContent"]) {
        background-color: transparent !important;
    }
    
    /* 侧边栏输入框容器 */
    div[data-testid="stSidebar"] .stTextInput,
    div[data-testid="stSidebar"] .stDateInput,
    div[data-testid="stSidebar"] .stSelectbox {
        background: transparent !important;
    }
    
    /* 侧边栏输入框 */
    div[data-testid="stSidebar"] input {
        background: rgba(30,33,40,0.8) !important;
        border: 1px solid rgba(0, 245, 255, 0.3) !important;
        color: #fafafa !important;
    }
    
    /* 侧边栏按钮 */
    div[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(90deg, #00f5ff, #00ff88) !important;
        color: #0e1117 !important;
        border: none !important;
    }
    
    /* 侧边栏单选按钮容器 */
    div[data-testid="stSidebar"] .stRadio > div {
        background: rgba(30,33,40,0.5) !important;
        border-radius: 10px;
        padding: 10px;
    }
    
    /* 侧边栏单选按钮 */
    div[data-testid="stSidebar"] .stRadio input[type="radio"] {
        filter: invert(1);
    }
    
    /* 侧边栏单选按钮标签 */
    div[data-testid="stSidebar"] .stRadio label {
        color: #fafafa !important;
    }
    
    /* 侧边栏下拉框 */
    div[data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(30,33,40,0.8) !important;
        border: 1px solid rgba(0, 245, 255, 0.3) !important;
    }
    
    /* 侧边栏下拉框选项 */
    div[data-testid="stSidebar"] .stSelectbox div[role="listbox"] {
        background: #1a1d23 !important;
    }
    
    div[data-testid="stSidebar"] .stSelectbox div[role="option"] {
        background: #1a1d23 !important;
        color: #fafafa !important;
    }
    
    div[data-testid="stSidebar"] .stSelectbox div[role="option"]:hover {
        background: rgba(0, 245, 255, 0.1) !important;
    }
    
    /* 侧边栏日期选择器 */
    div[data-testid="stSidebar"] .stDateInput > div > div {
        background: rgba(30,33,40,0.8) !important;
        border: 1px solid rgba(0, 245, 255, 0.3) !important;
    }
    
    /* 侧边栏日期选择器日历 */
    div[data-testid="stSidebar"] .stDateInput div[data-baseweb="calendar"] {
        background: #1a1d23 !important;
    }
    
    div[data-testid="stSidebar"] .stDateInput button {
        background: rgba(30,33,40,0.8) !important;
        color: #fafafa !important;
    }
    
    /* 侧边栏分隔线 */
    div[data-testid="stSidebar"] hr {
        border-color: rgba(0, 245, 255, 0.2) !important;
    }
    
    /* 侧边栏图标 */
    div[data-testid="stSidebar"] svg {
        fill: #00f5ff !important;
    }
    
    /* 侧边栏提示文本 */
    div[data-testid="stSidebar"] .stTooltipIcon {
        color: #00f5ff !important;
    }
    
    /* 侧边栏帮助文本 */
    div[data-testid="stSidebar"] .stHelp {
        color: rgba(250, 250, 250, 0.7) !important;
    }
    
    /* 侧边栏折叠面板 */
    div[data-testid="stSidebar"] .streamlit-expanderHeader {
        background: rgba(30,33,40,0.8) !important;
        border: 1px solid rgba(0, 245, 255, 0.2) !important;
        color: #fafafa !important;
    }
    
    div[data-testid="stSidebar"] .streamlit-expanderContent {
        background: rgba(30,33,40,0.5) !important;
        border: 1px solid rgba(0, 245, 255, 0.2) !important;
    }
    
    /* 侧边栏成功/错误/警告消息 */
    div[data-testid="stSidebar"] .stSuccess {
        background: rgba(0, 255, 136, 0.1) !important;
        color: #00ff88 !important;
        border: 1px solid rgba(0, 255, 136, 0.3) !important;
    }
    
    div[data-testid="stSidebar"] .stError {
        background: rgba(255, 71, 87, 0.1) !important;
        color: #ff4757 !important;
        border: 1px solid rgba(255, 71, 87, 0.3) !important;
    }
    
    div[data-testid="stSidebar"] .stWarning {
        background: rgba(255, 193, 7, 0.1) !important;
        color: #ffc107 !important;
        border: 1px solid rgba(255, 193, 7, 0.3) !important;
    }
    
    div[data-testid="stSidebar"] .stInfo {
        background: rgba(0, 245, 255, 0.1) !important;
        color: #00f5ff !important;
        border: 1px solid rgba(0, 245, 255, 0.3) !important;
    }
    
    /* 侧边栏所有div背景 */
    div[data-testid="stSidebar"] div {
        background-color: transparent !important;
    }
    
    /* 侧边栏特殊元素 */
    div[data-testid="stSidebar"] .element-container {
        background: transparent !important;
    }
    
    /* 侧边栏Markdown容器 */
    div[data-testid="stSidebar"] .stMarkdown {
        background: transparent !important;
        color: #fafafa !important;
    }
    
    /* 侧边栏文本容器 */
    div[data-testid="stSidebar"] .stText {
        background: transparent !important;
        color: #fafafa !important;
    }
    
    /* 强制侧边栏所有元素背景透明 */
    div[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        background: transparent !important;
    }
    
    div[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        background: transparent !important;
    }
    
    /* 侧边栏容器 */
    div[data-testid="stSidebar"] [data-testid="stSidebar"] {
        background: transparent !important;
    }
    
    /* 侧边栏表单 */
    div[data-testid="stSidebar"] form {
        background: transparent !important;
    }
    
    /* 侧边栏所有输入框 */
    div[data-testid="stSidebar"] input[type="text"],
    div[data-testid="stSidebar"] input[type="number"],
    div[data-testid="stSidebar"] input[type="date"],
    div[data-testid="stSidebar"] input[type="time"],
    div[data-testid="stSidebar"] textarea,
    div[data-testid="stSidebar"] select {
        background: rgba(30,33,40,0.8) !important;
        border: 1px solid rgba(0, 245, 255, 0.3) !important;
        color: #fafafa !important;
    }
    
    /* 侧边栏占位符 */
    div[data-testid="stSidebar"] input::placeholder,
    div[data-testid="stSidebar"] textarea::placeholder {
        color: rgba(250, 250, 250, 0.5) !important;
    }
    
    /* 侧边栏选择框 */
    div[data-testid="stSidebar"] select option {
        background: #1a1d23 !important;
        color: #fafafa !important;
    }
    
    /* 侧边栏复选框 */
    div[data-testid="stSidebar"] input[type="checkbox"] {
        filter: invert(1);
    }
    
    /* 侧边栏滑块 */
    div[data-testid="stSidebar"] input[type="range"] {
        background: rgba(30,33,40,0.8) !important;
    }
    
    /* 侧边栏所有按钮 */
    div[data-testid="stSidebar"] button {
        background: rgba(30,33,40,0.8) !important;
        color: #fafafa !important;
        border: 1px solid rgba(0, 245, 255, 0.3) !important;
    }
    
    div[data-testid="stSidebar"] button:hover {
        background: rgba(0, 245, 255, 0.1) !important;
        border-color: rgba(0, 245, 255, 0.5) !important;
    }
    
    /* 侧边栏主按钮 */
    div[data-testid="stSidebar"] button[kind="primary"] {
        background: linear-gradient(90deg, #00f5ff, #00ff88) !important;
        color: #0e1117 !important;
        border: none !important;
    }
    
    /* 侧边栏下拉菜单展开 */
    div[data-testid="stSidebar"] [data-baseweb="popover"] {
        background: #1a1d23 !important;
    }
    
    /* 侧边栏日历 */
    div[data-testid="stSidebar"] [data-baseweb="calendar"] {
        background: #1a1d23 !important;
    }
    
    div[data-testid="stSidebar"] [data-baseweb="calendar"] button {
        background: rgba(30,33,40,0.8) !important;
        color: #fafafa !important;
    }
    
    div[data-testid="stSidebar"] [data-baseweb="calendar"] button:hover {
        background: rgba(0, 245, 255, 0.2) !important;
    }
    
    /* 侧边栏时间选择器 */
    div[data-testid="stSidebar"] [data-baseweb="time-picker"] {
        background: #1a1d23 !important;
    }
    
    /* 侧边栏数字输入 */
    div[data-testid="stSidebar"] [data-baseweb="input"] {
        background: rgba(30,33,40,0.8) !important;
    }
    
    /* 侧边栏标签容器 */
    div[data-testid="stSidebar"] [data-baseweb="tag"] {
        background: rgba(0, 245, 255, 0.1) !important;
        color: #00f5ff !important;
    }
    
    /* 输入框样式 */
    .stTextInput>div>div>input {
        background: rgba(30,33,40,0.8);
        border: 1px solid rgba(0, 245, 255, 0.3);
        color: #fff;
        border-radius: 10px;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #00f5ff;
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.5);
    }
    
    /* 单选按钮 */
    .stRadio>label {
        color: #fafafa !important;
    }
    
    .stRadio>div>div>label {
        color: #fafafa !important;
    }
    
    /* 日期选择器 */
    .stDateInput>div>div>input {
        background: rgba(30,33,40,0.8);
        border: 1px solid rgba(0, 245, 255, 0.3);
        color: #fff;
    }
    
    /* 下拉选择框 */
    .stSelectbox>div>div>select {
        background: rgba(30,33,40,0.8);
        border: 1px solid rgba(0, 245, 255, 0.3);
        color: #fff;
    }
    
    /* 表格样式 */
    .stDataFrame {
        background: rgba(20,23,28,0.9);
        border: 1px solid rgba(0, 245, 255, 0.2);
        border-radius: 10px;
    }
    
    /* 信息提示框 */
    .stAlert {
        background: rgba(30,33,40,0.9);
        border: 1px solid rgba(0, 245, 255, 0.3);
        color: #fafafa;
    }
    
    /* 标题和文本 */
    h1, h2, h3, h4, h5, h6 {
        color: #fafafa !important;
    }
    
    p, span, div {
        color: #fafafa;
    }
    
    /* 链接 */
    a {
        color: #00f5ff;
    }
    
    /* 分隔线 */
    hr {
        border-color: rgba(0, 245, 255, 0.2);
    }
    
    /* 进度条 */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #00f5ff, #00ff88);
    }
    
    /* 滑块 */
    .stSlider > div > div > div {
        background: rgba(30,33,40,0.8);
    }
    
    /* 复选框 */
    .stCheckbox > label {
        color: #fafafa !important;
    }
    
    /* 多选框 */
    .stMultiSelect > div {
        background: rgba(30,33,40,0.8);
        border: 1px solid rgba(0, 245, 255, 0.3);
    }
    
    /* 数字输入 */
    .stNumberInput > div > div > input {
        background: rgba(30,33,40,0.8);
        border: 1px solid rgba(0, 245, 255, 0.3);
        color: #fff;
    }
    
    /* 文本区域 */
    .stTextArea > div > div > textarea {
        background: rgba(30,33,40,0.8);
        border: 1px solid rgba(0, 245, 255, 0.3);
        color: #fff;
    }
    
    /* 折叠面板 */
    .streamlit-expanderHeader {
        background: rgba(30,33,40,0.8);
        border: 1px solid rgba(0, 245, 255, 0.2);
        color: #fafafa;
    }
    
    /* 图表容器 */
    .plotly-graph-div {
        background: transparent !important;
    }
    
    /* 强制所有文本颜色 */
    .stMarkdown, .stText, .stCaption {
        color: #fafafa !important;
    }
    
    /* 强制所有标签颜色 */
    label, .st-emotion-cache-1gv3huu {
        color: #fafafa !important;
    }
    
    /* 强制所有输入框占位符 */
    input::placeholder, textarea::placeholder {
        color: rgba(250, 250, 250, 0.5) !important;
    }
    
    /* 强制所有选择框选项 */
    option {
        background: #1a1d23 !important;
        color: #fafafa !important;
    }
    
    /* 强制所有日期选择器 */
    input[type="date"] {
        background: rgba(30,33,40,0.8) !important;
        color: #fafafa !important;
    }
    
    /* 强制所有数字输入 */
    input[type="number"] {
        background: rgba(30,33,40,0.8) !important;
        color: #fafafa !important;
    }
    
    /* 强制所有复选框 */
    input[type="checkbox"] {
        filter: invert(1);
    }
    
    /* 强制所有滑块 */
    input[type="range"] {
        background: rgba(30,33,40,0.8) !important;
    }
    
    /* 强制所有下拉菜单 */
    .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(30,33,40,0.8) !important;
        border: 1px solid rgba(0, 245, 255, 0.3) !important;
    }
    
    /* 强制所有下拉菜单选项 */
    .stSelectbox div[role="listbox"] {
        background: #1a1d23 !important;
    }
    
    .stSelectbox div[role="option"] {
        color: #fafafa !important;
    }
    
    /* 强制所有提示框 */
    .stAlert > div {
        background: rgba(30,33,40,0.9) !important;
        color: #fafafa !important;
    }
    
    /* 强制所有成功消息 */
    .stSuccess {
        background: rgba(0, 255, 136, 0.1) !important;
        color: #00ff88 !important;
        border: 1px solid rgba(0, 255, 136, 0.3) !important;
    }
    
    /* 强制所有错误消息 */
    .stError {
        background: rgba(255, 71, 87, 0.1) !important;
        color: #ff4757 !important;
        border: 1px solid rgba(255, 71, 87, 0.3) !important;
    }
    
    /* 强制所有警告消息 */
    .stWarning {
        background: rgba(255, 193, 7, 0.1) !important;
        color: #ffc107 !important;
        border: 1px solid rgba(255, 193, 7, 0.3) !important;
    }
    
    /* 强制所有信息消息 */
    .stInfo {
        background: rgba(0, 245, 255, 0.1) !important;
        color: #00f5ff !important;
        border: 1px solid rgba(0, 245, 255, 0.3) !important;
    }
    
    /* 强制所有折叠面板内容 */
    .streamlit-expanderContent {
        background: rgba(30,33,40,0.5) !important;
        border: 1px solid rgba(0, 245, 255, 0.2) !important;
    }
    
    /* 强制所有代码块 */
    .stCodeBlock {
        background: rgba(30,33,40,0.8) !important;
        border: 1px solid rgba(0, 245, 255, 0.2) !important;
    }
    
    /* 强制所有表格 */
    .stDataFrame table {
        background: rgba(30,33,40,0.8) !important;
    }
    
    .stDataFrame th {
        background: rgba(0, 245, 255, 0.1) !important;
        color: #00f5ff !important;
    }
    
    .stDataFrame td {
        color: #fafafa !important;
    }
    
    /* 强制所有加载动画 */
    .stSpinner > div {
        border-color: #00f5ff transparent transparent transparent !important;
    }

</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<h1 class="main-header">📈 A股行情中心</h1>', unsafe_allow_html=True)

# 尝试导入配置文件
try:
    from config import ALPHA_VANTAGE_API_KEY, DATA_SOURCE
except:
    ALPHA_VANTAGE_API_KEY = None
    DATA_SOURCE = "yahoo_finance"

# Alpha Vantage API函数
@st.cache_data(ttl=300)
def get_stock_data_alpha_vantage(symbol, start, end):
    """使用Alpha Vantage获取股票历史数据"""
    if not ALPHA_VANTAGE_API_KEY or ALPHA_VANTAGE_API_KEY == "YOUR_API_KEY_HERE":
        return None, "未配置Alpha Vantage API密钥"
    
    try:
        # Alpha Vantage API endpoint
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY,
            "outputsize": "full"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "Error Message" in data:
            return None, f"未找到股票代码 '{symbol}'"
        
        if "Note" in data:
            return None, "API调用频率超限，请稍后再试"
        
        if "Time Series (Daily)" not in data:
            return None, "数据格式错误"
        
        # 转换数据为DataFrame
        time_series = data["Time Series (Daily)"]
        df_data = []
        
        for date, values in time_series.items():
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            if start <= date_obj <= end:
                df_data.append({
                    'Date': date_obj,
                    'Open': float(values['1. open']),
                    'High': float(values['2. high']),
                    'Low': float(values['3. low']),
                    'Close': float(values['4. close']),
                    'Volume': int(values['5. volume'])
                })
        
        if not df_data:
            return None, "指定日期范围内无数据"
        
        df = pd.DataFrame(df_data)
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        return df, None
        
    except requests.exceptions.Timeout:
        return None, "请求超时"
    except requests.exceptions.RequestException as e:
        return None, f"网络错误: {str(e)}"
    except Exception as e:
        return None, f"获取数据失败: {str(e)}"

@st.cache_data(ttl=300)
def get_stock_quote_alpha_vantage(symbol):
    """使用Alpha Vantage获取实时报价"""
    if not ALPHA_VANTAGE_API_KEY or ALPHA_VANTAGE_API_KEY == "YOUR_API_KEY_HERE":
        return None, "未配置Alpha Vantage API密钥"
    
    try:
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "Error Message" in data:
            return None, f"未找到股票代码 '{symbol}'"
        
        if "Note" in data:
            return None, "API调用频率超限"
        
        if "Global Quote" not in data or not data["Global Quote"]:
            return None, "无法获取报价数据"
        
        quote = data["Global Quote"]
        return {
            'price': float(quote.get('05. price', 0)),
            'change': float(quote.get('09. change', 0)),
            'change_percent': quote.get('10. change percent', '0%').replace('%', ''),
            'volume': int(quote.get('06. volume', 0)),
            'open': float(quote.get('02. open', 0)),
            'high': float(quote.get('03. high', 0)),
            'low': float(quote.get('04. low', 0)),
        }, None
        
    except Exception as e:
        return None, f"获取报价失败: {str(e)}"

# akshare 数据获取函数（A股专用）
@st.cache_data(ttl=300)
def get_stock_data_akshare(symbol, start, end):
    """使用akshare获取A股历史数据"""
    try:
        # 判断是否为A股
        if '.SS' in symbol or '.SZ' in symbol:
            # 提取股票代码（去掉后缀）
            code = symbol.replace('.SS', '').replace('.SZ', '')
            
            # 使用akshare获取A股日线数据
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start.strftime('%Y%m%d'),
                end_date=end.strftime('%Y%m%d'),
                adjust="qfq"  # 前复权
            )
            
            if df is None or df.empty:
                return None, "未找到A股数据"
            
            # 重命名列
            df = df.rename(columns={
                '日期': 'Date',
                '开盘': 'Open',
                '最高': 'High',
                '最低': 'Low',
                '收盘': 'Close',
                '成交量': 'Volume'
            })
            
            # 转换日期格式
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            
            # 只保留需要的列
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            
            return df, None
        
        return None, "不支持该股票类型"
        
    except Exception as e:
        return None, f"获取数据失败: {str(e)}"

@st.cache_data(ttl=300)
def get_stock_realtime_akshare(symbol):
    """使用akshare获取A股实时行情"""
    try:
        if '.SS' in symbol or '.SZ' in symbol:
            code = symbol.replace('.SS', '').replace('.SZ', '')
            
            # 获取实时行情
            df = ak.stock_zh_a_spot_em()
            stock_data = df[df['代码'] == code]
            
            if not stock_data.empty:
                row = stock_data.iloc[0]
                return {
                    'price': float(row['最新价']),
                    'change': float(row['涨跌额']),
                    'change_percent': float(row['涨跌幅']),
                    'volume': int(row['成交量']),
                    'open': float(row['今开']),
                    'high': float(row['最高']),
                    'low': float(row['最低']),
                }, None
        
        return None, "未找到股票数据"
        
    except Exception as e:
        return None, f"获取实时行情失败: {str(e)}"

# 新浪财经API数据获取函数（实时行情，与同花顺一致）
@st.cache_data(ttl=60)  # 缓存1分钟
def get_sina_data(codes):
    """
    使用新浪财经API获取实时行情
    codes: 列表格式，如 ['sh600519', 'sz000001', 'sh000001']
    返回: dict格式的数据
    """
    try:
        # 新浪财经API URL
        url = f"http://hq.sinajs.cn/list={','.join(codes)}"
        
        headers = {
            'Referer': 'http://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'
        
        result = {}
        lines = response.text.strip().split('\n')
        
        for line in lines:
            if not line or 'hq_str_' not in line:
                continue
                
            # 解析: var hq_str_sh600519="贵州茅台,1800.00,...";
            parts = line.split('="')
            if len(parts) < 2:
                continue
                
            code = parts[0].replace('var hq_str_', '')
            data_str = parts[1].rstrip('";')
            
            if not data_str:  # 空数据
                continue
                
            data_parts = data_str.split(',')
            
            # 判断是港股还是A股（港股代码以hk开头）
            if code.startswith('hk'):
                # 港股格式：英文名,中文名,昨收,今开,最高,最低,当前价,涨跌额,涨跌幅,...
                # 索引：0=英文名, 1=中文名, 2=昨收, 3=今开, 4=最高, 5=最低, 6=当前价, 7=涨跌额, 8=涨跌幅
                if len(data_parts) >= 9:
                    result[code] = {
                        'name': data_parts[1],  # 中文名
                        'prev_close': float(data_parts[2]) if data_parts[2] else 0,  # 昨收
                        'open': float(data_parts[3]) if data_parts[3] else 0,  # 今开
                        'high': float(data_parts[4]) if data_parts[4] else 0,  # 最高
                        'low': float(data_parts[5]) if data_parts[5] else 0,  # 最低
                        'price': float(data_parts[6]) if data_parts[6] else 0,  # 当前价
                        'change': float(data_parts[7]) if data_parts[7] else 0,  # 涨跌额
                        'change_percent': float(data_parts[8]) if data_parts[8] else 0,  # 涨跌幅
                        'volume': int(float(data_parts[12])) if len(data_parts) > 12 and data_parts[12] else 0,  # 成交量
                    }
            else:
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
    # 指数代码映射（新浪格式）
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
def get_hk_index_data_sina():
    """使用新浪财经获取港股主要指数实时行情"""
    # 港股指数代码（新浪格式）
    index_codes = {
        'hkHSI': {'name': '恒生指数', 'symbol': 'HSI'},
        'hkHSCEI': {'name': '国企指数', 'symbol': 'HSCEI'},
        'hkHSTECH': {'name': '恒生科技', 'symbol': 'HSTECH'},
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
            }
    
    return result

@st.cache_data(ttl=60)
def get_stock_realtime_sina(symbol):
    """使用新浪财经获取A股实时行情"""
    try:
        # 转换代码格式 - 只支持A股
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
        # 转换代码格式 - 只支持A股
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

# 获取指数数据的函数（保留akshare作为备选）
@st.cache_data(ttl=300)
def get_index_data_akshare():
    """使用akshare获取A股主要指数实时行情（备选方案）"""
    try:
        # 获取A股实时行情
        df = ak.stock_zh_index_spot_em()
        
        index_map = {
            '000001': {'name': '上证指数', 'suffix': '.SS'},
            '399001': {'name': '深证成指', 'suffix': '.SZ'},
            '399006': {'name': '创业板指', 'suffix': '.SZ'},
            '000688': {'name': '科创50', 'suffix': '.SS'},
            '000300': {'name': '沪深300', 'suffix': '.SS'},
            '000016': {'name': '上证50', 'suffix': '.SS'},
        }
        
        result = {}
        for code, info in index_map.items():
            index_data = df[df['代码'] == code]
            if not index_data.empty:
                row = index_data.iloc[0]
                symbol = f"{code}{info['suffix']}"
                result[symbol] = {
                    'price': float(row['最新价']),
                    'change': float(row['涨跌额']),
                    'change_percent': float(row['涨跌幅']),
                    'open': float(row['今开']),
                    'high': float(row['最高']),
                    'low': float(row['最低']),
                    'volume': int(row['成交量']) if '成交量' in row else 0,
                    'amount': float(row['成交额']) if '成交额' in row else 0,
                }
        
        return result
    except Exception as e:
        return None

# 获取港股指数数据（保留akshare作为备选）
@st.cache_data(ttl=300)
def get_hk_index_data_akshare():
    """使用akshare获取港股主要指数实时行情（备选方案）"""
    try:
        # 获取港股实时行情
        df = ak.stock_hk_index_spot_em()
        
        index_map = {
            'HSI': '恒生指数',
            'HSCEI': '国企指数',
            'HSTECH': '恒生科技指数',
        }
        
        result = {}
        for symbol, name in index_map.items():
            index_data = df[df['代码'] == symbol]
            if not index_data.empty:
                row = index_data.iloc[0]
                result[symbol] = {
                    'price': float(row['最新价']),
                    'change': float(row['涨跌额']),
                    'change_percent': float(row['涨跌幅']),
                    'open': float(row['今开']),
                    'high': float(row['最高']),
                    'low': float(row['最低']),
                    'volume': int(row['成交量']) if '成交量' in row else 0,
                }
        
        return result
    except Exception as e:
        return None

# 添加缓存装饰器，减少API调用
@st.cache_data(ttl=300)
def get_stock_data(symbol, start, end):
    """获取股票历史数据 - 只支持A股"""
    # A股优先使用新浪财经（最稳定）
    if '.SS' in symbol or '.SZ' in symbol:
        df, error = get_stock_history_sina(symbol, start, end)
        if df is not None:
            return df, None, "新浪财经 (A股数据)"
        # 新浪失败，尝试akshare
        df, error = get_stock_data_akshare(symbol, start, end)
        if df is not None:
            return df, None, "akshare (A股数据)"
        return None, error, None
    
    # 不支持的股票类型
    return None, "仅支持A股查询（代码格式：600519.SS 或 000001.SZ）", None
    
    # 美股使用Alpha Vantage或Yahoo Finance
    if DATA_SOURCE in ["alpha_vantage", "auto"] and ALPHA_VANTAGE_API_KEY and ALPHA_VANTAGE_API_KEY != "YOUR_API_KEY_HERE":
        df, error = get_stock_data_alpha_vantage(symbol, start, end)
        if df is not None:
            return df, None, "Alpha Vantage"
    
    # 使用Yahoo Finance作为备选
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(start=start, end=end)
        return df, None, "Yahoo Finance"
    except Exception as e:
        return None, str(e), None

@st.cache_data(ttl=300)
def get_stock_info(symbol):
    """获取股票基本信息"""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return info, None
    except Exception as e:
        return None, str(e)

def get_stock_data_with_retry(symbol, start, end, max_retries=3):
    """带重试机制的数据获取"""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # 港股添加延迟避免限流
            if '.HK' in symbol and attempt > 0:
                delay = random.uniform(3, 5)
                st.info(f"⏳ 第 {attempt + 1} 次尝试，等待 {delay:.1f} 秒...")
                time.sleep(delay)
            elif attempt > 0:
                delay = random.uniform(1, 3)
                time.sleep(delay)
            
            df, error, data_source = get_stock_data(symbol, start, end)
            
            if df is not None and not df.empty:
                return df, None, data_source
            
            if df is not None and df.empty:
                return None, f"未找到股票代码 '{symbol}' 的数据", None
            
            # 记录错误信息
            if error:
                last_error = error
                if attempt < max_retries - 1:
                    st.warning(f"⚠️ 尝试 {attempt + 1}/{max_retries} 失败: {error}")
                
        except Exception as e:
            last_error = str(e)
            if "Rate limited" in str(e) or "Too Many Requests" in str(e):
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3 + random.uniform(1, 3)
                    st.warning(f"⏳ API限流，等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    return None, "API请求次数过多，请稍后再试或清除缓存后重试", None
            else:
                if attempt < max_retries - 1:
                    st.warning(f"⚠️ 尝试 {attempt + 1}/{max_retries} 出错: {str(e)}")
    
    # 所有重试都失败
    return None, f"获取数据失败: {last_error}", None

# 三大市场配置
MARKETS = {
    "A股": {
        "indices": [
            {"symbol": "000001", "name": "上证指数", "code": "sh000001"},
            {"symbol": "399001", "name": "深证成指", "code": "sz399001"},
            {"symbol": "399006", "name": "创业板指", "code": "sz399006"},
        ]
    }
}

# 备用数据（当API不可用时使用）
FALLBACK_DATA = {
    # A股指数（与MARKETS配置的symbol一致）
    "000001": {"price": 4077.68, "change": -46.51, "change_percent": -1.13, "open": 4098.70, "high": 4099.25, "low": 4052.55},
    "399001": {"price": 13868.86, "change": -303.77, "change_percent": -2.14, "open": 13920.29, "high": 13920.29, "low": 13701.67},
    "399006": {"price": 3151.05, "change": -78.25, "change_percent": -2.42, "open": 3152.72, "high": 3158.14, "low": 3111.88},
    # A股热门股票
    "600519.SS": {"price": 1756.80, "change": 12.50, "change_percent": 0.72},
}

# 显示市场行情
st.markdown("## 🌍 A股市场概览")

# 添加数据来源提示
st.info("💡 提示：A股实时数据来自新浪财经（与同花顺一致）")

# 获取A股指数实时数据（优先使用新浪财经API）
a_stock_indices_data = None
a_stock_error = None
try:
    a_stock_indices_data = get_index_data_sina()
    if not a_stock_indices_data:
        # 新浪失败，尝试akshare
        a_stock_indices_data = get_index_data_akshare()
except Exception as e:
    a_stock_error = str(e)

# 显示错误信息
if a_stock_error:
    st.error(f"⚠️ A股指数数据获取失败: {a_stock_error[:100]}...")

# 显示A股市场
for idx, (market_name, market_data) in enumerate(MARKETS.items()):
    st.markdown(f'<div class="market-title">{market_name}</div>', unsafe_allow_html=True)
    
    # 显示指数
    for index in market_data["indices"]:
        try:
            # A股指数优先使用新浪实时数据
            if market_name == "A股" and a_stock_indices_data and index["symbol"] in a_stock_indices_data:
                    data = a_stock_indices_data[index["symbol"]]
                    change_class = "price-up" if data["change"] >= 0 else "price-down"
                    change_symbol = "▲" if data["change"] >= 0 else "▼"
                    
                    # 格式化成交量
                    volume_str = ""
                    if data.get('volume', 0) > 0:
                        vol = data['volume']
                        if vol >= 100000000:
                            volume_str = f"{vol/100000000:.2f}亿"
                        elif vol >= 10000:
                            volume_str = f"{vol/10000:.2f}万"
                    
                    st.markdown(f"""
                    <div class="market-card">
                        <div class="index-header">
                            <span class="index-name">{index['name']}</span>
                            <span class="index-code">{index['symbol']}</span>
                        </div>
                        <div class="index-value">{data['price']:,.2f}</div>
                        <div class="index-change {change_class}">
                            <span style="font-size: 1.1em;">{change_symbol}</span>
                            <span style="font-size: 1.3em; font-weight: bold;">{data['change']:+,.2f}</span>
                            <span style="font-size: 1.2em; margin-left: 8px;">{data['change_percent']:+.2f}%</span>
                        </div>
                        <div class="index-detail">
                            <span>开: {data.get('open', 0):.2f}</span>
                            <span>高: {data.get('high', 0):.2f}</span>
                            <span>低: {data.get('low', 0):.2f}</span>
                            {f'<span>量: {volume_str}</span>' if volume_str else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # 使用备用数据
                if index["symbol"] in FALLBACK_DATA:
                            data = FALLBACK_DATA[index["symbol"]]
                            change_class = "price-up" if data["change"] >= 0 else "price-down"
                            change_symbol = "📈" if data["change"] >= 0 else "📉"
                            st.markdown(f"""
                            <div class="market-card">
                                <div class="index-name">{index['name']}</div>
                                <div class="index-value">{data['price']:,.2f}</div>
                                <div class="index-change {change_class}">
                                    {change_symbol} {data['change']:+,.2f} ({data['change_percent']:+.2f}%)
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="market-card">
                                <div class="index-name">{index['name']}</div>
                                <div class="index-value">--</div>
                                <div class="index-change">数据加载中...</div>
                            </div>
                            """, unsafe_allow_html=True)
            except Exception as e:
                # 使用备用数据
                if index["symbol"] in FALLBACK_DATA:
                    data = FALLBACK_DATA[index["symbol"]]
                    change_class = "price-up" if data["change"] >= 0 else "price-down"
                    change_symbol = "📈" if data["change"] >= 0 else "📉"
                    st.markdown(f"""
                    <div class="market-card">
                        <div class="index-name">{index['name']}</div>
                        <div class="index-value">{data['price']:,.2f}</div>
                        <div class="index-change {change_class}">
                            {change_symbol} {data['change']:+,.2f} ({data['change_percent']:+.2f}%)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="market-card">
                    <div class="index-name">{index['name']}</div>
                    <div class="index-value">--</div>
                    <div class="index-change">数据加载中...</div>
                </div>
                """, unsafe_allow_html=True)

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
# 检查是否有选中的股票
if 'selected_stock' in st.session_state:
    stock_symbol = st.session_state['selected_stock']
    
if query_button or stock_symbol:
    try:
        with st.spinner(f"正在获取 {stock_symbol} 的数据..."):
            df, error, data_source = get_stock_data_with_retry(stock_symbol, start_date, end_date)
            
            if error:
                st.error(f"❌ {error}")
                st.info("💡 提示：\n- 请检查股票代码是否正确\n- 如果频繁查询，请等待1-2分钟后重试\n- 可以尝试其他股票代码")
            else:
                info, info_error = get_stock_info(stock_symbol)
                
        if df is None or df.empty:
            if not error:
                st.error(f"❌ 未找到股票代码 '{stock_symbol}' 的数据，请检查代码是否正确")
        else:
            # 显示数据来源
            if data_source:
                source_color = "#00ff88" if "新浪" in data_source else "#ffc107"
                st.markdown(f"**📊 数据来源：** <span style='color:{source_color}'>{data_source}</span>", unsafe_allow_html=True)
            
            # 获取实时价格（A股使用新浪财经实时行情）
            realtime_data = None
            if '.SS' in stock_symbol or '.SZ' in stock_symbol:
                realtime_data, _ = get_stock_realtime_sina(stock_symbol)
            
            if realtime_data:
                # 使用实时数据
                current_price = realtime_data['price']
                previous_close = df['Close'].iloc[-1]  # 历史数据的最后一条是昨收
                price_change = realtime_data['change']
                price_change_percent = realtime_data['change_percent']
            else:
                # 使用历史数据
                current_price = df['Close'].iloc[-1]
                previous_close = df['Close'].iloc[-2] if len(df) > 1 else current_price
                price_change = current_price - previous_close
                price_change_percent = (price_change / previous_close) * 100
            
            stock_name = info.get('longName', stock_symbol) if info else stock_symbol
            
            st.markdown(f"## {stock_name} ({stock_symbol})")
            
            # 显示实时价格信息
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <p style="font-size: 0.9rem; color: rgba(255,255,255,0.7); margin-bottom: 0.5rem;">💰 当前价格</p>
                    <p style="font-size: 2.5rem; font-weight: bold; margin: 0; color: #00f5ff;">${current_price:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                change_symbol = "📈" if price_change >= 0 else "📉"
                change_class = "price-up" if price_change >= 0 else "price-down"
                st.markdown(f"""
                <div class="metric-card">
                    <p style="font-size: 0.9rem; color: rgba(255,255,255,0.7); margin-bottom: 0.5rem;">{change_symbol} 涨跌额</p>
                    <p style="font-size: 2.5rem; font-weight: bold; margin: 0;" class="{change_class}">
                        {"+" if price_change >= 0 else ""}{price_change:,.2f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                change_class = "price-up" if price_change_percent >= 0 else "price-down"
                st.markdown(f"""
                <div class="metric-card">
                    <p style="font-size: 0.9rem; color: rgba(255,255,255,0.7); margin-bottom: 0.5rem;">📊 涨跌幅</p>
                    <p style="font-size: 2.5rem; font-weight: bold; margin: 0;" class="{change_class}">
                        {"+" if price_change_percent >= 0 else ""}{price_change_percent:.2f}%
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 将实时数据添加到历史数据中（用于K线图）
            chart_df = df.copy()
            if realtime_data:
                # 添加今天的实时数据
                today = pd.Timestamp.now().normalize()
                today_data = pd.DataFrame({
                    'Open': [realtime_data['open']],
                    'High': [realtime_data['high']],
                    'Low': [realtime_data['low']],
                    'Close': [realtime_data['price']],
                    'Volume': [realtime_data['volume']],
                }, index=[today])
                chart_df = pd.concat([chart_df, today_data])
            
            # 创建K线图和成交量图
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
                    x=chart_df.index,
                    open=chart_df['Open'],
                    high=chart_df['High'],
                    low=chart_df['Low'],
                    close=chart_df['Close'],
                    name="K线",
                    increasing_line_color='#00ff88',
                    decreasing_line_color='#ff4757',
                ),
                row=1, col=1
            )
            
            colors = ['#00ff88' if chart_df['Close'].iloc[i] >= chart_df['Open'].iloc[i] else '#ff4757' 
                     for i in range(len(chart_df))]
            
            fig.add_trace(
                go.Bar(
                    x=chart_df.index,
                    y=chart_df['Volume'],
                    name="成交量",
                    marker_color=colors,
                    opacity=0.7,
                ),
                row=2, col=1
            )
            
            # 添加移动平均线
            chart_df['MA5'] = chart_df['Close'].rolling(window=5).mean()
            chart_df['MA10'] = chart_df['Close'].rolling(window=10).mean()
            chart_df['MA20'] = chart_df['Close'].rolling(window=20).mean()
            
            fig.add_trace(
                go.Scatter(
                    x=chart_df.index,
                    y=chart_df['MA5'],
                    name="MA5",
                    line=dict(color='#ff6b6b', width=1),
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=chart_df.index,
                    y=chart_df['MA10'],
                    name="MA10",
                    line=dict(color='#ffd93d', width=1),
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=chart_df.index,
                    y=chart_df['MA20'],
                    name="MA20",
                    line=dict(color='#6bcb77', width=1),
                ),
                row=1, col=1
            )
            
            fig.update_layout(
                title=f"{stock_name} ({stock_symbol}) - K线图与成交量",
                yaxis_title="价格",
                yaxis2_title="成交量",
                xaxis_rangeslider_visible=False,
                height=800,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
            fig.update_xaxes(
                title_text="日期",
                gridcolor='rgba(255,255,255,0.1)',
                rangeslider_visible=False,
            )
            
            fig.update_yaxes(
                gridcolor='rgba(255,255,255,0.1)',
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 显示详细数据表格
            st.markdown("### 📊 详细数据")
            
            display_df = df.copy()
            display_df.index = display_df.index.strftime('%Y-%m-%d')
            display_df = display_df.round(2)
            
            # 根据实际列数设置列名
            if len(display_df.columns) == 5:
                display_df.columns = ['开盘价', '最高价', '最低价', '收盘价', '成交量']
            elif len(display_df.columns) == 7:
                display_df.columns = ['开盘价', '最高价', '最低价', '收盘价', '成交量', '分红', '股票拆分']
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400
            )
            
            # 显示股票基本信息
            if info:
                st.markdown("---")
                st.markdown("### 📋 公司简况")
                
                # 公司基本信息
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4 style="color: #00f5ff; margin-bottom: 15px;">🏢 基本信息</h4>
                        <p><strong>公司名称：</strong>{info.get('longName', 'N/A')}</p>
                        <p><strong>行业：</strong>{info.get('industry', 'N/A')}</p>
                        <p><strong>板块：</strong>{info.get('sector', 'N/A')}</p>
                        <p><strong>国家：</strong>{info.get('country', 'N/A')}</p>
                        <p><strong>员工数：</strong>{info.get('fullTimeEmployees', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4 style="color: #00f5ff; margin-bottom: 15px;">💰 财务数据</h4>
                        <p><strong>市值：</strong>{info.get('marketCap', 'N/A')}</p>
                        <p><strong>市盈率：</strong>{info.get('trailingPE', 'N/A')}</p>
                        <p><strong>市净率：</strong>{info.get('priceToBook', 'N/A')}</p>
                        <p><strong>营收：</strong>{info.get('totalRevenue', 'N/A')}</p>
                        <p><strong>净利润：</strong>{info.get('netIncomeToCommon', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 价格区间
                col3, col4 = st.columns(2)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4 style="color: #00f5ff; margin-bottom: 15px;">📈 价格区间</h4>
                        <p><strong>52周最高：</strong>{info.get('fiftyTwoWeekHigh', 'N/A')}</p>
                        <p><strong>52周最低：</strong>{info.get('fiftyTwoWeekLow', 'N/A')}</p>
                        <p><strong>50日均线：</strong>{info.get('fiftyDayAverage', 'N/A')}</p>
                        <p><strong>200日均线：</strong>{info.get('twoHundredDayAverage', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4 style="color: #00f5ff; margin-bottom: 15px;">📊 交易数据</h4>
                        <p><strong>平均成交量：</strong>{info.get('averageVolume', 'N/A')}</p>
                        <p><strong>股息收益率：</strong>{info.get('dividendYield', 'N/A')}</p>
                        <p><strong>Beta系数：</strong>{info.get('beta', 'N/A')}</p>
                        <p><strong>流通股：</strong>{info.get('floatShares', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 公司简介
                if info.get('longBusinessSummary'):
                    st.markdown("### 📝 公司简介")
                    st.markdown(f"""
                    <div class="metric-card">
                        <p style="line-height: 1.6;">{info.get('longBusinessSummary', '暂无简介')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 趋势分析
            st.markdown("---")
            st.markdown("### 📈 趋势分析")
            
            # 趋势判断（使用chart_df，包含实时数据）
            ma5 = chart_df['MA5'].iloc[-1]
            ma10 = chart_df['MA10'].iloc[-1]
            ma20 = chart_df['MA20'].iloc[-1]
            
            # 计算涨跌幅（相对于历史数据）
            price_change_5d = ((chart_df['Close'].iloc[-1] - chart_df['Close'].iloc[-5]) / chart_df['Close'].iloc[-5] * 100) if len(chart_df) >= 5 else 0
            price_change_10d = ((chart_df['Close'].iloc[-1] - chart_df['Close'].iloc[-10]) / chart_df['Close'].iloc[-10] * 100) if len(chart_df) >= 10 else 0
            price_change_20d = ((chart_df['Close'].iloc[-1] - chart_df['Close'].iloc[-20]) / chart_df['Close'].iloc[-20] * 100) if len(chart_df) >= 20 else 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                trend_5d = "📈 上涨" if price_change_5d > 0 else "📉 下跌"
                trend_class = "price-up" if price_change_5d > 0 else "price-down"
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #00f5ff; margin-bottom: 10px;">5日趋势</h4>
                    <p style="font-size: 1.5rem;" class="{trend_class}">{trend_5d}</p>
                    <p style="font-size: 2rem; font-weight: bold;" class="{trend_class}">{price_change_5d:+.2f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                trend_10d = "📈 上涨" if price_change_10d > 0 else "📉 下跌"
                trend_class = "price-up" if price_change_10d > 0 else "price-down"
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #00f5ff; margin-bottom: 10px;">10日趋势</h4>
                    <p style="font-size: 1.5rem;" class="{trend_class}">{trend_10d}</p>
                    <p style="font-size: 2rem; font-weight: bold;" class="{trend_class}">{price_change_10d:+.2f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                trend_20d = "📈 上涨" if price_change_20d > 0 else "📉 下跌"
                trend_class = "price-up" if price_change_20d > 0 else "price-down"
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #00f5ff; margin-bottom: 10px;">20日趋势</h4>
                    <p style="font-size: 1.5rem;" class="{trend_class}">{trend_20d}</p>
                    <p style="font-size: 2rem; font-weight: bold;" class="{trend_class}">{price_change_20d:+.2f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 均线分析
            st.markdown("### 📊 均线分析")
            
            ma_analysis = []
            if current_price > ma5:
                ma_analysis.append("✅ 当前价格高于5日均线")
            else:
                ma_analysis.append("❌ 当前价格低于5日均线")
            
            if current_price > ma10:
                ma_analysis.append("✅ 当前价格高于10日均线")
            else:
                ma_analysis.append("❌ 当前价格低于10日均线")
            
            if current_price > ma20:
                ma_analysis.append("✅ 当前价格高于20日均线")
            else:
                ma_analysis.append("❌ 当前价格低于20日均线")
            
            if ma5 > ma10 > ma20:
                ma_analysis.append("✅ 多头排列（看涨信号）")
            elif ma5 < ma10 < ma20:
                ma_analysis.append("❌ 空头排列（看跌信号）")
            
            for analysis in ma_analysis:
                st.markdown(f"- {analysis}")
            
            # 成交量分析
            st.markdown("### 📊 成交量分析")
            
            avg_volume = df['Volume'].mean()
            recent_volume = df['Volume'].iloc[-1]
            volume_ratio = recent_volume / avg_volume
            
            if volume_ratio > 1.5:
                volume_signal = "放量（交易活跃）"
                volume_color = "price-up"
            elif volume_ratio < 0.5:
                volume_signal = "缩量（交易清淡）"
                volume_color = "price-down"
            else:
                volume_signal = "量能正常"
                volume_color = ""
            
            st.markdown(f"""
            <div class="metric-card">
                <p><strong>今日成交量：</strong>{recent_volume:,.0f}</p>
                <p><strong>平均成交量：</strong>{avg_volume:,.0f}</p>
                <p><strong>量比：</strong>{volume_ratio:.2f}</p>
                <p><strong>信号：</strong><span class="{volume_color}">{volume_signal}</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**⏰ 最后更新时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
    except Exception as e:
        st.error(f"❌ 获取数据时出错：{str(e)}")
        st.info("💡 提示：请检查股票代码是否正确，或稍后重试")

# 页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.5); padding: 20px;">
    <p style="font-size: 1.1rem;">📊 A股行情中心 | 数据来源：新浪财经</p>
    <p>支持A股实时行情查询</p>
    <p style="font-size: 0.9rem; color: rgba(0, 245, 255, 0.7);">实时行情 · K线图表 · 技术分析</p>
</div>
""", unsafe_allow_html=True)

# 使用说明
with st.expander("📖 使用说明"):
    st.markdown("""
    ### 如何使用
    
    1. **查看市场行情**
       - 页面顶部自动显示美股、A股、港股三大市场的主要指数
       - 实时更新热门股票行情
    
    2. **点击查看股票详情**
       - 点击任意热门股票卡片，查看详细信息
       - 包含K线图、趋势分析、公司简况等
    
    3. **查询股票详情**
       - 在侧边栏输入股票代码
       - 或从"快速选择"下拉菜单选择热门股票
       - 选择日期范围后点击"查询股票"
    
    4. **股票代码格式**
       - A股：代码加后缀，如 `600519.SS`（贵州茅台）、`000001.SZ`（平安银行）
    
    ### 详细信息包含
    
    - **K线图**：包含MA5、MA10、MA20移动平均线
    - **趋势分析**：5日、10日、20日涨跌趋势
    - **均线分析**：价格与均线关系、多空排列判断
    - **成交量分析**：量比、交易活跃度
    - **公司简况**：基本信息、财务数据、公司简介
    
    ### 注意事项
    
    - 数据来源于 Yahoo Finance，可能有延迟
    - 避免频繁查询，建议每次查询间隔至少30秒
    - 使用缓存功能，相同查询会使用缓存数据
    - 如需最新数据，点击"清除缓存"按钮
    
    ### 常见问题
    
    **Q: 出现"Too Many Requests"错误怎么办？**
    - A: 这是API速率限制，请等待1-2分钟后重试
    
    **Q: 为什么有些股票信息显示不完整？**
    - A: 部分股票（特别是A股和港股）的信息可能不完整
    """)
