# -*- coding: utf-8 -*-
import requests

markets = [
    ('sh_a', '上海A股'),
    ('sz_a', '深圳A股'),
]

for market_code, market_name in markets:
    print(f"\n{'='*60}")
    print(f"{market_name} ({market_code})")
    print('='*60)
    
    url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"
    params = {
        'page': '1',
        'num': '3000',
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
        
        if response.status_code == 200:
            data = response.json()
            print(f"总共获取: {len(data)} 只股票")
            
            # 统计不同类型的股票
            sh_main = []  # 上海主板 60开头
            sh_sci = []   # 科创板 688开头
            sz_main = []  # 深圳主板 000开头
            sz_sme = []   # 中小板 002开头
            sz_gem = []   # 创业板 300开头
            
            for item in data:
                code = item['code']
                if code.startswith('60'):
                    sh_main.append(f"{code} - {item['name']}")
                elif code.startswith('688'):
                    sh_sci.append(f"{code} - {item['name']}")
                elif code.startswith('000'):
                    sz_main.append(f"{code} - {item['name']}")
                elif code.startswith('002'):
                    sz_sme.append(f"{code} - {item['name']}")
                elif code.startswith('300'):
                    sz_gem.append(f"{code} - {item['name']}")
            
            if sh_main:
                print(f"\n上海主板(60): {len(sh_main)}只")
                print("  示例:", sh_main[:3])
            if sh_sci:
                print(f"\n科创板(688): {len(sh_sci)}只")
                print("  示例:", sh_sci[:3])
            if sz_main:
                print(f"\n深圳主板(000): {len(sz_main)}只")
                print("  示例:", sz_main[:3])
            if sz_sme:
                print(f"\n中小板(002): {len(sz_sme)}只")
                print("  示例:", sz_sme[:3])
            if sz_gem:
                print(f"\n创业板(300): {len(sz_gem)}只")
                print("  示例:", sz_gem[:3])
            
            # 查找特定股票
            test_stocks = ['600519', '688981', '000001', '002594', '300750']
            print(f"\n查找测试股票:")
            for test_code in test_stocks:
                found = [item for item in data if item['code'] == test_code]
                if found:
                    print(f"  ✓ {found[0]['code']} - {found[0]['name']}")
                else:
                    print(f"  ✗ {test_code} 未找到")
                    
    except Exception as e:
        print(f"错误: {e}")
