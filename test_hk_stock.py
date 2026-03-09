#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试港股数据获取
"""
import requests
import pandas as pd
from datetime import datetime, timedelta

def test_sina_hk_realtime():
    """测试新浪财经港股实时行情"""
    print("=" * 50)
    print("测试1: 新浪财经港股实时行情")
    print("=" * 50)
    
    # 腾讯控股 0700.HK -> hk00700
    hk_code = "hk00700"
    
    try:
        url = f"http://hq.sinajs.cn/list={hk_code}"
        headers = {
            'Referer': 'http://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容:\n{response.text[:500]}")
        
        if 'hq_str_' in response.text:
            parts = response.text.split('="')
            if len(parts) >= 2:
                data_str = parts[1].rstrip('";')
                data_parts = data_str.split(',')
                print(f"\n数据字段数量: {len(data_parts)}")
                print(f"前10个字段: {data_parts[:10]}")
                
                if len(data_parts) >= 6:
                    print("\n解析结果:")
                    print(f"名称: {data_parts[1]}")
                    print(f"昨收: {data_parts[2]}")
                    print(f"当前价: {data_parts[3]}")
                    print(f"最高: {data_parts[4]}")
                    print(f"最低: {data_parts[5]}")
                    return True
        
        print("❌ 未找到有效数据")
        return False
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False

def test_sina_hk_history():
    """测试新浪财经港股历史数据"""
    print("\n" + "=" * 50)
    print("测试2: 新浪财经港股历史K线")
    print("=" * 50)
    
    # 腾讯控股
    sina_code = "hk00700"
    
    try:
        url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData'
        params = {
            'symbol': sina_code,
            'scale': '240',  # 日线
            'datalen': '30',  # 30天
        }
        
        headers = {
            'Referer': 'http://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容:\n{response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                print(f"\n✅ 获取到 {len(data)} 条数据")
                print(f"第一条数据: {data[0]}")
                print(f"最后一条数据: {data[-1]}")
                return True
            else:
                print("❌ 数据为空或格式错误")
                return False
        else:
            print(f"❌ 请求失败")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_yfinance_hk():
    """测试Yahoo Finance港股数据"""
    print("\n" + "=" * 50)
    print("测试3: Yahoo Finance港股数据")
    print("=" * 50)
    
    try:
        import yfinance as yf
        
        symbol = "0700.HK"
        stock = yf.Ticker(symbol)
        
        end = datetime.now()
        start = end - timedelta(days=30)
        
        df = stock.history(start=start, end=end)
        
        if df is not None and not df.empty:
            print(f"✅ 获取到 {len(df)} 条数据")
            print(f"\n数据预览:")
            print(df.head())
            print(f"\n最新数据:")
            print(df.tail(1))
            return True
        else:
            print("❌ 未获取到数据")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_akshare_hk():
    """测试akshare港股数据"""
    print("\n" + "=" * 50)
    print("测试4: akshare港股数据")
    print("=" * 50)
    
    try:
        import akshare as ak
        
        code = "00700"
        end = datetime.now()
        start = end - timedelta(days=30)
        
        df = ak.stock_hk_hist(
            symbol=code,
            period="daily",
            start_date=start.strftime('%Y%m%d'),
            end_date=end.strftime('%Y%m%d'),
            adjust="qfq"
        )
        
        if df is not None and not df.empty:
            print(f"✅ 获取到 {len(df)} 条数据")
            print(f"\n数据预览:")
            print(df.head())
            return True
        else:
            print("❌ 未获取到数据")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试港股数据获取 - 腾讯控股 (0700.HK)")
    print()
    
    results = {
        "新浪实时行情": test_sina_hk_realtime(),
        "新浪历史K线": test_sina_hk_history(),
        "Yahoo Finance": test_yfinance_hk(),
        "akshare": test_akshare_hk(),
    }
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    for name, result in results.items():
        status = "✅ 成功" if result else "❌ 失败"
        print(f"{name}: {status}")
