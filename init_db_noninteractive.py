#!/usr/bin/env python3
"""
CRM系统数据库初始化脚本（非交互式版本）
"""

import os
import sqlite3

def init_database(recreate=False, insert_samples=False):
    """初始化数据库"""
    db_path = os.path.join(os.path.dirname(__file__), 'crm.db')
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    print(f"数据库路径: {db_path}")
    
    # 如果数据库已存在且不需要重新创建，则跳过
    if os.path.exists(db_path) and not recreate:
        print("数据库已存在，跳过初始化")
        return
    
    try:
        # 如果存在且需要重新创建，先删除
        if os.path.exists(db_path) and recreate:
            os.remove(db_path)
            print("已删除现有数据库")
        
        # 读取schema文件
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # 连接数据库并执行schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("正在创建数据库表...")
        cursor.executescript(schema_sql)
        
        # 插入示例数据（如果指定）
        if insert_samples:
            print("正在插入示例数据...")
            insert_sample_data_sql(conn)
        
        conn.commit()
        conn.close()
        
        print("数据库初始化成功！")
        print(f"数据库文件: {db_path}")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        if 'conn' in locals():
            conn.close()

def insert_sample_data_sql(conn):
    """插入示例数据"""
    cursor = conn.cursor()
    
    # 插入客户单位示例数据
    cursor.execute('''
        INSERT INTO customer_organizations 
        (name, type, industry, scale, address, phone, email, 
         invoice_info, potential_score, classification, created_by, notes)
        VALUES 
        ('奇智科技（北京）有限公司', 'partner', '网络安全', 'medium', 
         '北京市海淀区', '010-12345678', 'contact@qizhitech.com',
         '增值税专用发票', 85, '战略合作伙伴', '韩晓晨', '重要合作伙伴'),
        
        ('沁北电厂', 'final_customer', '电力能源', 'large',
         '河南省济源市', '0391-1234567', 'contact@qinbei-power.com',
         '增值税普通发票', 90, '重点客户', '韩晓晨', '发电企业客户'),
        
        ('首信云技术有限公司', 'partner', '云计算', 'medium',
         '北京市朝阳区', '010-87654321', 'info@shouxincloud.com',
         '增值税专用发票', 75, '技术合作伙伴', '韩晓晨', '云计算服务商')
    ''')
    
    # 插入联系人示例数据
    cursor.execute('''
        INSERT INTO contacts 
        (organization_id, name, position, phone, email, is_alumni, is_primary)
        VALUES 
        (1, '王博士', '技术总监', '13800138000', 'wang@qizhitech.com', TRUE, TRUE),
        (1, '张老师', '销售总监', '13900139000', 'zhang@qizhitech.com', FALSE, FALSE),
        (2, '李主任', '信息化主任', '13700137000', 'li@qinbei-power.com', FALSE, TRUE)
    ''')
    
    # 插入销售机会示例数据
    cursor.execute('''
        INSERT INTO sales_opportunities 
        (organization_id, opportunity_name, source, stage, estimated_amount, 
         estimated_close_date, probability, priority, assigned_to, description)
        VALUES 
        (2, '沁北电厂智能运维平台项目', '客户主动咨询', 'proposal', 1500000.00,
         '2026-06-30', 70, 'high', '韩晓晨', '智能运维平台整体解决方案'),
        
        (3, '首信云安全防护项目', '合作伙伴推荐', 'qualification', 800000.00,
         '2026-05-15', 60, 'medium', '韩晓晨', '云安全防护系统部署')
    ''')
    
    # 插入合同示例数据
    cursor.execute('''
        INSERT INTO contracts 
        (organization_id, contract_number, contract_name, contract_amount, 
         start_date, end_date, status, signed_date)
        VALUES 
        (1, 'HT20260309001', '网盾系统年度维护合同', 500000.00,
         '2026-01-01', '2026-12-31', 'active', '2026-01-15')
    ''')
    
    # 插入发票示例数据
    cursor.execute('''
        INSERT INTO invoices 
        (contract_id, organization_id, invoice_number, invoice_date, 
         amount, total_amount, status, due_date)
        VALUES 
        (1, 1, 'FP20260309001', '2026-03-01', 41666.67, 41666.67, 'paid', '2026-03-31')
    ''')
    
    # 插入应收应付示例数据
    cursor.execute('''
        INSERT INTO financial_transactions 
        (type, organization_id, invoice_id, contract_id, transaction_date, 
         due_date, amount, status)
        VALUES 
        ('receivable', 1, 1, 1, '2026-03-01', '2026-03-31', 41666.67, 'paid')
    ''')
    
    print("示例数据插入完成")

if __name__ == '__main__':
    import sys
    recreate = '--recreate' in sys.argv
    insert_samples = '--insert-samples' in sys.argv
    
    print("CRM数据库初始化（非交互式）")
    print(f"重新创建: {recreate}")
    print(f"插入示例数据: {insert_samples}")
    
    init_database(recreate=recreate, insert_samples=insert_samples)