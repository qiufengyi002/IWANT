# -*- coding: utf-8 -*-
import requests
import json

# 测试获取沪市股票
markets = [
    ('hs_a', 'sh'),  # 沪市A股
    ('sz_a', 'sz'),  # 深市A股
]

for market_code, prefix in markets:
    print(f"\n{'='*50}")
    print(f"测试市场: {market_code}")
    print('='*50)
    
    url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"
    params = {
        'page': '1',
        'num': '50',
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
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"获取到 {len(data)} 只股票")
            
            # 查找贵州茅台
            found = False
            for item in data:
                if '茅台' in item.get('name', ''):
                    print(f"\n找到茅台: {item['code']} - {item['name']}")
                    found = True
            
            if not found:
                print("\n前10只股票:")
                for i, item in enumerate(data[:10]):
                    print(f"{i+1}. {item.get('code', 'N/A')} - {item.get('name', 'N/A')}")
                    
    except Exception as e:
        print(f"错误: {e}")
