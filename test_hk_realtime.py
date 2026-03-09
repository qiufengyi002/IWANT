#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试港股实时行情解析
"""
import requests

def test_hk_realtime():
    """测试新浪财经港股实时行情解析"""
    hk_code = "hk00700"
    
    try:
        url = f"http://hq.sinajs.cn/list={hk_code}"
        headers = {
            'Referer': 'http://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'
        
        print("原始响应:")
        print(response.text)
        print("\n" + "="*50 + "\n")
        
        # 解析数据
        parts = response.text.split('="')
        if len(parts) >= 2:
            code = parts[0].replace('var hq_str_', '')
            data_str = parts[1].rstrip('";')
            data_parts = data_str.split(',')
            
            print(f"代码: {code}")
            print(f"字段数量: {len(data_parts)}")
            print("\n字段详情:")
            for i, field in enumerate(data_parts[:15]):
                print(f"  [{i}] = {field}")
            
            # 按新格式解析
            if len(data_parts) >= 9:
                result = {
                    'name': data_parts[1],  # 中文名
                    'prev_close': float(data_parts[2]),  # 昨收
                    'open': float(data_parts[3]),  # 今开
                    'high': float(data_parts[4]),  # 最高
                    'low': float(data_parts[5]),  # 最低
                    'price': float(data_parts[6]),  # 当前价
                    'change': float(data_parts[7]),  # 涨跌额
                    'change_percent': float(data_parts[8]),  # 涨跌幅
                }
                
                print("\n" + "="*50)
                print("解析结果:")
                print("="*50)
                for key, value in result.items():
                    print(f"{key}: {value}")
                
                return True
        
        return False
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("测试腾讯控股 (0700.HK) 实时行情解析\n")
    success = test_hk_realtime()
    print("\n" + "="*50)
    print(f"测试结果: {'✅ 成功' if success else '❌ 失败'}")
