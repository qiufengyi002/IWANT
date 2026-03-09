# -*- coding: utf-8 -*-
import requests
import json

# 测试新浪财经股票列表API
url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"
params = {
    'page': '1',
    'num': '100',  # 先测试100只
    'sort': 'symbol',
    'asc': '1',
    'node': 'hs_a',  # 沪深A股
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
    print(f"响应内容前500字符:\n{response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n数据类型: {type(data)}")
        print(f"数据长度: {len(data) if isinstance(data, list) else 'N/A'}")
        
        if isinstance(data, list) and len(data) > 0:
            print(f"\n第一条数据:")
            print(json.dumps(data[0], ensure_ascii=False, indent=2))
            
            print(f"\n前5只股票:")
            for i, item in enumerate(data[:5]):
                print(f"{i+1}. {item.get('code', 'N/A')} - {item.get('name', 'N/A')}")
                
except Exception as e:
    print(f"错误: {e}")
