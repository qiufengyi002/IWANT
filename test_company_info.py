# -*- coding: utf-8 -*-
import requests
import re

# 测试获取贵州茅台的公司信息
stock_code = "600519"

print("="*60)
print(f"测试获取 {stock_code} 的公司信息")
print("="*60)

# 1. 测试公司基本信息页面
url1 = f"http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/{stock_code}.phtml"
headers = {
    'Referer': 'http://finance.sina.com.cn',
    'User-Agent': 'Mozilla/5.0'
}

try:
    response = requests.get(url1, headers=headers, timeout=10)
    response.encoding = 'gbk'
    
    print(f"\n状态码: {response.status_code}")
    print(f"响应长度: {len(response.text)}")
    
    if response.status_code == 200:
        # 查找所有包含"："的行
        lines = response.text.split('\n')
        info_lines = [line for line in lines if '：' in line or ':' in line]
        
        print(f"\n找到 {len(info_lines)} 行包含信息")
        
        # 提取关键信息
        patterns = {
            '公司名称': r'公司名称[：:]\s*</td>\s*<td[^>]*>([^<]+)',
            '英文名称': r'英文名称[：:]\s*</td>\s*<td[^>]*>([^<]+)',
            '法人代表': r'法人代表[：:]\s*</td>\s*<td[^>]*>([^<]+)',
            '总经理': r'总\s*经\s*理[：:]\s*</td>\s*<td[^>]*>([^<]+)',
            '董秘': r'董事会秘书[：:]\s*</td>\s*<td[^>]*>([^<]+)',
            '注册地址': r'注册地址[：:]\s*</td>\s*<td[^>]*>([^<]+)',
            '所属行业': r'所属行业[：:]\s*</td>\s*<td[^>]*>([^<]+)',
            '上市日期': r'上市日期[：:]\s*</td>\s*<td[^>]*>([^<]+)',
        }
        
        print("\n提取的信息:")
        for name, pattern in patterns.items():
            match = re.search(pattern, response.text)
            if match:
                print(f"{name}: {match.group(1).strip()}")
            else:
                print(f"{name}: 未找到")
        
        # 查找公司简介
        intro_patterns = [
            r'公司简介[：:]\s*</td>\s*</tr>\s*<tr>\s*<td[^>]*>([^<]+)',
            r'公司简介[：:]\s*</td>\s*<td[^>]*>([^<]+)',
        ]
        
        print("\n公司简介:")
        found = False
        for pattern in intro_patterns:
            match = re.search(pattern, response.text)
            if match:
                print(match.group(1).strip()[:200] + "...")
                found = True
                break
        if not found:
            print("未找到")
            
except Exception as e:
    print(f"错误: {e}")

# 2. 测试财务指标API
print("\n" + "="*60)
print("测试财务指标API")
print("="*60)

url2 = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"
params = {
    'page': '1',
    'num': '1',
    'sort': 'symbol',
    'asc': '0',
    'node': 'sh_a',
    'symbol': stock_code,
}

try:
    response2 = requests.get(url2, params=params, headers=headers, timeout=10)
    print(f"状态码: {response2.status_code}")
    
    if response2.status_code == 200:
        import json
        data = response2.json()
        if data and len(data) > 0:
            print("\n返回的字段:")
            for key, value in data[0].items():
                print(f"  {key}: {value}")
        else:
            print("无数据")
            
except Exception as e:
    print(f"错误: {e}")
