#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试新浪财经港股历史数据的不同API
"""
import requests
import json

def test_method_1():
    """方法1: CN_MarketData.getKLineData"""
    print("="*50)
    print("方法1: CN_MarketData.getKLineData")
    print("="*50)
    
    url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData'
    params = {
        'symbol': 'hk00700',
        'scale': '240',
        'datalen': '30',
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:200]}")
        return response.text != 'null'
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_method_2():
    """方法2: HK_MarketData.getKLineData"""
    print("\n" + "="*50)
    print("方法2: HK_MarketData.getKLineData")
    print("="*50)
    
    url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/HK_MarketData.getKLineData'
    params = {
        'symbol': 'hk00700',
        'scale': '240',
        'datalen': '30',
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")
        
        if response.text and response.text != 'null':
            data = json.loads(response.text)
            if data and len(data) > 0:
                print(f"\n✅ 成功获取 {len(data)} 条数据")
                print(f"第一条: {data[0]}")
                print(f"最后一条: {data[-1]}")
                return True
        return False
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_method_3():
    """方法3: 港股通用历史数据API"""
    print("\n" + "="*50)
    print("方法3: 港股通用历史数据API")
    print("="*50)
    
    # 尝试不同的symbol格式
    symbols = ['hk00700', 'rt_hk00700', '00700']
    
    for symbol in symbols:
        print(f"\n尝试代码: {symbol}")
        url = f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHKStockData'
        params = {
            'page': '1',
            'num': '1',
            'sort': 'symbol',
            'asc': '0',
            'node': 'qbgg_hk',
            'symbol': symbol,
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            print(f"  状态码: {response.status_code}")
            print(f"  响应: {response.text[:200]}")
        except Exception as e:
            print(f"  错误: {e}")
    
    return False

if __name__ == "__main__":
    print("测试新浪财经港股历史数据API\n")
    
    results = {
        "方法1 (CN_MarketData)": test_method_1(),
        "方法2 (HK_MarketData)": test_method_2(),
        "方法3 (通用API)": test_method_3(),
    }
    
    print("\n" + "="*50)
    print("测试结果")
    print("="*50)
    for name, result in results.items():
        status = "✅ 成功" if result else "❌ 失败"
        print(f"{name}: {status}")
