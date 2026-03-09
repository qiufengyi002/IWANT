# -*- coding: utf-8 -*-
import requests

# 测试不同的node参数
nodes = ['sh_a', 'shzb', 'shmb', 'sz_a', 'szzb']

for node in nodes:
    print(f"\n{'='*50}")
    print(f"测试node: {node}")
    print('='*50)
    
    url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"
    params = {
        'page': '1',
        'num': '10',
        'sort': 'symbol',
        'asc': '1',
        'node': node,
        'symbol': '',
        '_s_r_a': 'page'
    }
    
    headers = {
        'Referer': 'http://vip.stock.finance.sina.com.cn/',
        'User-Agent': 'Mozilla/5.0'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                print(f"成功! 获取到 {len(data)} 只股票")
                print("前3只:")
                for i, item in enumerate(data[:3]):
                    print(f"  {item.get('code', 'N/A')} - {item.get('name', 'N/A')}")
            else:
                print("无数据")
        else:
            print(f"失败: {response.status_code}")
                    
    except Exception as e:
        print(f"错误: {e}")
