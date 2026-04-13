#!/usr/bin/env python3
"""
差异化CRM系统数据库初始化脚本
"""

import os
import sqlite3
import json

def init_database(recreate=False, insert_samples=True):
    """初始化增强版数据库"""
    db_path = os.path.join(os.path.dirname(__file__), 'crm_enhanced.db')
    schema_path = os.path.join(os.path.dirname(__file__), 'schema_enhanced.sql')
    
    print(f"差异化CRM数据库路径: {db_path}")
    print(f"架构文件: {schema_path}")
    
    # 如果数据库已存在且不需要重新创建，则跳过
    if os.path.exists(db_path) and not recreate:
        print("数据库已存在，跳过初始化")
        return True
    
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
        
        print("正在创建差异化CRM数据库表...")
        cursor.executescript(schema_sql)
        
        # 插入示例数据（如果指定）
        if insert_samples:
            print("正在插入示例数据...")
            insert_sample_data(conn)
        
        conn.commit()
        conn.close()
        
        print("差异化CRM数据库初始化成功！")
        print(f"数据库文件: {db_path}")
        return True
        
    except Exception as e:
        print(f"差异化CRM数据库初始化失败: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def insert_sample_data(conn):
    """插入示例数据"""
    cursor = conn.cursor()
    
    print("插入客户单位示例数据...")
    
    # 插入客户单位示例数据（网络安全公司专用）
    cursor.execute('''
        INSERT INTO customer_organizations 
        (name, type, industry, scale, security_level, address, phone, email, 
         invoice_info, tax_number, bank_account, 
         using_netshield, netshield_version, netshield_license_expiry,
         using_inoc, inoc_modules, inoc_license_expiry,
         potential_score, health_score, risk_level, classification, tags, created_by, notes)
        VALUES 
        -- 电网客户（高安全等级）
        ('国家电网华北分公司', 'final_customer', '电力能源', 'critical_infrastructure', 'enhanced',
         '北京市西城区', '010-12345678', 'contact@sgcc-north.com',
         '增值税专用发票', '911100001000123456', '中国银行北京分行 1234567890123456789',
         TRUE, 'v3.2', '2026-06-30',
         TRUE, '["智能发现", "根因分析", "配置仿真"]', '2026-12-31',
         95, 88, 'medium', '战略客户', '["电网", "关键基础设施", "已部署网盾", "已部署I-NOC"]', '韩晓晨', '国家电网重要客户，网盾+I-NOC全部署'),
        
        -- 金融客户
        ('中国银行信息安全部', 'final_customer', '金融', 'enterprise', 'enhanced',
         '北京市复兴门内大街1号', '010-12345679', 'security@bankofchina.com',
         '增值税专用发票', '911100001000123457', '工商银行北京分行 1234567890123456790',
         TRUE, 'v3.1', '2026-05-15',
         FALSE, NULL, NULL,
         90, 92, 'low', '重点客户', '["金融", "高安全要求", "已部署网盾"]', '韩晓晨', '银行客户，仅部署网盾'),
        
        -- 军工客户
        ('航天科工集团', 'final_customer', '军工', 'critical_infrastructure', 'classified',
         '北京市海淀区', '010-12345680', 'info@casic.com',
         '增值税专用发票', '911100001000123458', '建设银行北京分行 1234567890123456801',
         TRUE, 'v3.3', '2027-01-01',
         TRUE, '["智能发现", "凭据保险箱"]', '2027-06-30',
         98, 85, 'high', '保密客户', '["军工", "保密单位", "全产品部署"]', '韩晓晨', '军工单位，特殊安全要求'),
        
        -- 合作伙伴
        ('奇智科技（北京）有限公司', 'partner', '网络安全', 'medium', 'standard',
         '北京市海淀区', '010-87654321', 'partner@qizhitech.com',
         '增值税专用发票', '911100001000123459', '招商银行北京分行 1234567890123456902',
         FALSE, NULL, NULL,
         FALSE, NULL, NULL,
         85, 95, 'low', '战略合作伙伴', '["合作伙伴", "技术合作"]', '韩晓晨', '技术合作伙伴')
    ''')
    
    # 插入产品使用示例数据
    print("插入产品使用示例数据...")
    
    # 为国家电网插入使用记录
    for i in range(30):
        usage_date = f'2026-02-{10 + i:02d}' if i < 20 else f'2026-03-{i-19:02d}'
        cursor.execute('''
            INSERT INTO product_usage 
            (organization_id, product_type, module_name, usage_date, usage_count, 
             active_users, performance_score, issues_reported, support_tickets)
            VALUES 
            (1, 'netshield', '威胁检测', ?, 5, 12, 4, 0, 0),
            (1, 'inoc', '智能发现', ?, 8, 8, 5, 1, 0)
        ''', (usage_date, usage_date))
    
    # 为中国银行插入使用记录
    for i in range(15):
        usage_date = f'2026-02-{15 + i:02d}' if i < 10 else f'2026-03-{i-9:02d}'
        cursor.execute('''
            INSERT INTO product_usage 
            (organization_id, product_type, module_name, usage_date, usage_count, 
             active_users, performance_score, issues_reported, support_tickets)
            VALUES 
            (2, 'netshield', '访问控制', ?, 3, 6, 5, 0, 0)
        ''', (usage_date,))
    
    # 插入AI洞察示例数据
    print("插入AI洞察示例数据...")
    
    cursor.execute('''
        INSERT INTO ai_insights 
        (organization_id, insight_type, generated_date, confidence_score, 
         insight_text, recommended_actions, priority, status)
        VALUES 
        -- 国家电网的洞察
        (1, 'renewal_prediction', '2026-03-10', 0.8,
         '网盾许可证将在112天后到期，建议提前3个月开始续约沟通',
         '["准备续约报价", "安排客户拜访", "制定续约方案"]', 'medium', 'new'),
        
        (1, 'cross_sell', '2026-03-10', 0.7,
         '客户频繁使用智能发现模块，可推荐配置管理引擎',
         '["准备配置管理引擎介绍材料", "安排产品演示", "提供试用许可"]', 'medium', 'new'),
        
        -- 中国银行的洞察
        (2, 'churn_risk', '2026-03-10', 0.6,
         '客户近7天无产品使用记录，可能存在使用问题',
         '["联系客户了解使用情况", "提供在线培训", "收集反馈意见"]', 'high', 'new'),
        
        (2, 'upsell_opportunity', '2026-03-10', 0.75,
         '客户仅使用网盾，可推荐I-NOC智能运维平台',
         '["准备I-NOC产品介绍", "安排技术交流", "制定迁移方案"]', 'medium', 'reviewed')
    ''')
    
    # 插入安全日志示例数据
    print("插入安全日志示例数据...")
    
    cursor.execute('''
        INSERT INTO security_logs 
        (organization_id, log_type, event_time, user_id, action_description, 
         resource_type, resource_id, ip_address, user_agent, severity, details)
        VALUES 
        (1, 'access', '2026-03-10 08:30:00', 'api_key_system', '查看客户详情',
         'customer_organizations', 1, '192.168.1.100', 'Python-Requests/2.31', 'info',
         '{"method": "GET", "path": "/api/customer-organizations/1"}'),
        
        (2, 'modification', '2026-03-10 09:15:00', 'api_key_system', '更新产品使用记录',
         'product_usage', 1, '192.168.1.101', 'Python-Requests/2.31', 'info',
         '{"method": "POST", "path": "/api/product-usage"}'),
        
        (NULL, 'security_alert', '2026-03-10 10:00:00', 'system', '异常登录尝试',
         NULL, NULL, '203.0.113.1', 'Mozilla/5.0', 'warning',
         '{"attempts": 3, "blocked": true}')
    ''')
    
    # 插入自动化工作流示例数据
    print("插入自动化工作流示例数据...")
    
    cursor.execute('''
        INSERT INTO workflow_automations 
        (name, trigger_type, trigger_condition, actions, enabled, 
         last_executed, execution_count, success_count, failure_count)
        VALUES 
        ('每日客户健康检查', 'scheduled', 
         '{"schedule": "daily", "time": "09:00", "timezone": "Asia/Shanghai"}',
         '[{"type": "check_all_customers", "params": {}}, {"type": "generate_health_report", "params": {}}]',
         TRUE, '2026-03-10 09:00:00', 1, 1, 0),
        
        ('许可证到期自动提醒', 'condition_based',
         '{"condition": "days_until_expiry <= 60", "check_frequency": "daily"}',
         '[{"type": "send_email_reminder", "params": {"days_before": 60}}, {"type": "create_followup_task", "params": {}}]',
         TRUE, '2026-03-10 08:00:00', 5, 5, 0),
        
        ('低使用率客户跟进', 'condition_based',
         '{"condition": "usage_last_30_days < 5", "check_frequency": "weekly"}',
         '[{"type": "create_followup_task", "params": {"assignee": "韩晓晨"}}, {"type": "send_checkin_email", "params": {}}]',
         TRUE, '2026-03-09 10:00:00', 3, 2, 1)
    ''')
    
    print("示例数据插入完成")

if __name__ == '__main__':
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='初始化差异化CRM数据库')
    parser.add_argument('--recreate', action='store_true', help='重新创建数据库（删除现有数据）')
    parser.add_argument('--no-samples', action='store_true', help='不插入示例数据')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("差异化CRM数据库初始化工具")
    print("专为网络安全公司设计的智能CRM系统")
    print("=" * 60)
    
    success = init_database(
        recreate=args.recreate,
        insert_samples=not args.no_samples
    )
    
    if success:
        print("\n✅ 差异化CRM数据库初始化成功！")
        print("\n下一步:")
        print("1. 启动CRM服务: python app_enhanced.py")
        print("2. 默认端口: 5002")
        print("3. 默认API密钥: default-api-key-change-in-production")
        print("4. 访问 http://localhost:5002 查看系统")
        print("\n📊 包含的示例数据:")
        print("   - 4个客户单位（电网、金融、军工、合作伙伴）")
        print("   - 45条产品使用记录")
        print("   - 4个AI分析洞察")
        print("   - 3个自动化工作流")
        print("   - 3条安全日志")
    else:
        print("\n❌ 差异化CRM数据库初始化失败")
        sys.exit(1)