# -*- coding: utf-8 -*-
"""
模拟交易数据库管理模块
"""

import sqlite3
from datetime import datetime
import os

class TradingDB:
    def __init__(self, db_path='trading.db'):
        """初始化数据库连接"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """初始化数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                cash REAL DEFAULT 1000000.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建持仓表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                position_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                stock_code TEXT NOT NULL,
                stock_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                avg_cost REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, stock_code)
            )
        ''')
        
        # 创建交易记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                stock_code TEXT NOT NULL,
                stock_name TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                amount REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, username, initial_cash=1000000.0):
        """创建用户"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO users (username, cash) VALUES (?, ?)',
                (username, initial_cash)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return user_id, None
        except sqlite3.IntegrityError:
            return None, "用户名已存在"
        finally:
            conn.close()
    
    def get_user(self, username):
        """获取用户信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT user_id, username, cash FROM users WHERE username = ?',
            (username,)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'cash': user[2]
            }
        return None
    
    def buy_stock(self, user_id, stock_code, stock_name, quantity, price):
        """买入股票"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 计算总金额
            amount = quantity * price
            
            # 检查资金是否足够
            cursor.execute('SELECT cash FROM users WHERE user_id = ?', (user_id,))
            cash = cursor.fetchone()[0]
            
            if cash < amount:
                return False, "资金不足"
            
            # 扣除资金
            cursor.execute(
                'UPDATE users SET cash = cash - ? WHERE user_id = ?',
                (amount, user_id)
            )
            
            # 更新持仓
            cursor.execute(
                'SELECT quantity, avg_cost FROM positions WHERE user_id = ? AND stock_code = ?',
                (user_id, stock_code)
            )
            position = cursor.fetchone()
            
            if position:
                # 已有持仓，更新数量和成本
                old_quantity = position[0]
                old_cost = position[1]
                new_quantity = old_quantity + quantity
                new_cost = (old_quantity * old_cost + amount) / new_quantity
                
                cursor.execute(
                    'UPDATE positions SET quantity = ?, avg_cost = ?, updated_at = ? WHERE user_id = ? AND stock_code = ?',
                    (new_quantity, new_cost, datetime.now(), user_id, stock_code)
                )
            else:
                # 新建持仓
                cursor.execute(
                    'INSERT INTO positions (user_id, stock_code, stock_name, quantity, avg_cost) VALUES (?, ?, ?, ?, ?)',
                    (user_id, stock_code, stock_name, quantity, price)
                )
            
            # 记录交易
            cursor.execute(
                'INSERT INTO transactions (user_id, stock_code, stock_name, transaction_type, quantity, price, amount) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (user_id, stock_code, stock_name, 'BUY', quantity, price, amount)
            )
            
            conn.commit()
            return True, "买入成功"
        
        except Exception as e:
            conn.rollback()
            return False, f"买入失败: {str(e)}"
        finally:
            conn.close()
    
    def sell_stock(self, user_id, stock_code, quantity, price):
        """卖出股票"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查持仓
            cursor.execute(
                'SELECT stock_name, quantity, avg_cost FROM positions WHERE user_id = ? AND stock_code = ?',
                (user_id, stock_code)
            )
            position = cursor.fetchone()
            
            if not position:
                return False, "没有该股票持仓"
            
            stock_name = position[0]
            current_quantity = position[1]
            
            if current_quantity < quantity:
                return False, f"持仓不足，当前持仓: {current_quantity}"
            
            # 计算卖出金额
            amount = quantity * price
            
            # 增加资金
            cursor.execute(
                'UPDATE users SET cash = cash + ? WHERE user_id = ?',
                (amount, user_id)
            )
            
            # 更新持仓
            new_quantity = current_quantity - quantity
            if new_quantity == 0:
                # 清空持仓
                cursor.execute(
                    'DELETE FROM positions WHERE user_id = ? AND stock_code = ?',
                    (user_id, stock_code)
                )
            else:
                # 减少持仓
                cursor.execute(
                    'UPDATE positions SET quantity = ?, updated_at = ? WHERE user_id = ? AND stock_code = ?',
                    (new_quantity, datetime.now(), user_id, stock_code)
                )
            
            # 记录交易
            cursor.execute(
                'INSERT INTO transactions (user_id, stock_code, stock_name, transaction_type, quantity, price, amount) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (user_id, stock_code, stock_name, 'SELL', quantity, price, amount)
            )
            
            conn.commit()
            return True, "卖出成功"
        
        except Exception as e:
            conn.rollback()
            return False, f"卖出失败: {str(e)}"
        finally:
            conn.close()
    
    def get_positions(self, user_id):
        """获取用户持仓"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT stock_code, stock_name, quantity, avg_cost FROM positions WHERE user_id = ? ORDER BY updated_at DESC',
            (user_id,)
        )
        positions = cursor.fetchall()
        conn.close()
        
        return [
            {
                'stock_code': p[0],
                'stock_name': p[1],
                'quantity': p[2],
                'avg_cost': p[3]
            }
            for p in positions
        ]
    
    def get_transactions(self, user_id, limit=50):
        """获取交易记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT stock_code, stock_name, transaction_type, quantity, price, amount, created_at FROM transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT ?',
            (user_id, limit)
        )
        transactions = cursor.fetchall()
        conn.close()
        
        return [
            {
                'stock_code': t[0],
                'stock_name': t[1],
                'type': t[2],
                'quantity': t[3],
                'price': t[4],
                'amount': t[5],
                'time': t[6]
            }
            for t in transactions
        ]
