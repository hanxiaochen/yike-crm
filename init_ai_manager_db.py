#!/usr/bin/env python3
"""
AI管理的CRM系统数据库初始化脚本
"""

import os
import sqlite3
import json
import random
from datetime import datetime, timedelta

def init_database(recreate=False):
    """初始化AI管理CRM数据库"""
    db_path = os.path.join(os.path.dirname(__file__), 'crm_ai_manager.db')
    schema_path = os.path.join(os.path.dirname(__file__), 'ai_manager_crm_schema.sql')
    
    print(f"🤖 AI管理的CRM数据库路径: {db_path}")
    
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
        
        print("正在创建AI管理的CRM数据库表...")
        cursor.executescript(schema_sql)
        
        # 插入AI代理
        print("初始化AI代理...")
        
        AI_AGENTS = [
            {
                'id': 1,
                'agent_name': 'AI销售经理',
                'role': 'sales_manager',
                'capabilities': json.dumps(['opportunity_identification', 'lead_qualification', 'deal_strategy', 'pricing_recommendation']),
                'authority_level': 'decision_maker',
                'description': '负责销售机会识别和转化，制定销售策略'
            },
            {
                'id': 2,
                'agent_name': 'AI客户成功经理',
                'role': 'customer_success',
                'capabilities': json.dumps(['health_monitoring', 'engagement_planning', 'issue_resolution', 'value_realization']),
                'authority_level': 'executor',
                'description': '负责客户健康度管理和价值实现'
            },
            {
                'id': 3,
                'agent_name': 'AI关系经理',
                'role': 'relationship_manager',
                'capabilities': json.dumps(['relationship_building', 'communication_planning', 'stakeholder_management', 'trust_development']),
                'authority_level': 'advisor',
                'description': '负责客户关系建设和维护'
            },
            {
                'id': 4,
                'agent_name': 'AI续约专家',
                'role': 'renewal_specialist',
                'capabilities': json.dumps(['renewal_prediction', 'renewal_strategy', 'risk_assessment', 'negotiation_support']),
                'authority_level': 'decision_maker',
                'description': '负责客户续约管理和风险控制'
            },
            {
                'id': 5,
                'agent_name': 'AI风险分析师',
                'role': 'risk_analyst',
                'capabilities': json.dumps(['risk_identification', 'impact_assessment', 'mitigation_planning', 'early_warning']),
                'authority_level': 'advisor',
                'description': '负责客户风险识别和预警'
            }
        ]
        
        for agent in AI_AGENTS:
            cursor.execute('''
                INSERT INTO ai_agents 
                (id, agent_name, role, capabilities, authority_level, is_active)
                VALUES (?, ?, ?, ?, ?, TRUE)
            ''', (
                agent['id'],
                agent['agent_name'],
                agent['role'],
                agent['capabilities'],
                agent['authority_level']
            ))
        
        # 插入示例客户（AI管理优化）
        print("插入示例客户数据...")
        
        # 首先插入客户组织
        customer_organizations = [
            {
                'id': 1,
                'name': '国家电网华北分公司',
                'type': 'final_customer',
                'industry': '电力能源',
                'scale': 'critical_infrastructure',
                'security_level': 'enhanced',
                'ai_managed_segment': '战略客户',
                'ai_engagement_score': 0.65,
                'ai_relationship_stage': 'established',
                'ai_management_priority': 9,
                'using_netshield': True,
                'netshield_version': 'v3.2',
                'netshield_license_expiry': '2026-06-30',
                'using_inoc': True,
                'inoc_modules': json.dumps(['智能发现', '根因分析']),
                'inoc_license_expiry': '2026-12-31',
                'health_score': 72,
                'potential_score': 95,
                'risk_level': 'medium',
                'created_by': 'ai_manager'
            },
            {
                'id': 2,
                'name': '中国银行信息安全部',
                'type': 'final_customer',
                'industry': '金融',
                'scale': 'enterprise',
                'security_level': 'enhanced',
                'ai_managed_segment': '活跃客户',
                'ai_engagement_score': 0.45,
                'ai_relationship_stage': 'developing',
                'ai_management_priority': 7,
                'using_netshield': True,
                'netshield_version': 'v3.1',
                'netshield_license_expiry': '2026-05-15',
                'using_inoc': False,
                'inoc_modules': None,
                'inoc_license_expiry': None,
                'health_score': 88,
                'potential_score': 90,
                'risk_level': 'low',
                'created_by': 'ai_manager'
            }
        ]
        
        for org in customer_organizations:
            cursor.execute('''
                INSERT INTO customer_organizations 
                (id, name, type, industry, scale, security_level, 
                 ai_managed_segment, ai_engagement_score, ai_relationship_stage, ai_management_priority,
                 using_netshield, netshield_version, netshield_license_expiry,
                 using_inoc, inoc_modules, inoc_license_expiry,
                 health_score, potential_score, risk_level, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                org['id'],
                org['name'],
                org['type'],
                org['industry'],
                org['scale'],
                org['security_level'],
                org['ai_managed_segment'],
                org['ai_engagement_score'],
                org['ai_relationship_stage'],
                org['ai_management_priority'],
                org['using_netshield'],
                org['netshield_version'],
                org['netshield_license_expiry'],
                org['using_inoc'],
                org['inoc_modules'],
                org['inoc_license_expiry'],
                org['health_score'],
                org['potential_score'],
                org['risk_level'],
                org['created_by']
            ))
        
        # 插入联系人
        print("插入示例联系人数据...")
        
        contacts = [
            {
                'organization_id': 1,
                'name': '王主任',
                'position': '信息化主任',
                'phone': '13800138000',
                'email': 'wang@sgcc-north.com',
                'ai_preferred_channel': 'meeting',
                'ai_interaction_frequency': 5,
                'last_ai_interaction': '2026-03-05',
                'next_ai_interaction': '2026-03-15',
                'ai_relationship_score': 0.7,
                'ai_communication_style': 'formal',
                'is_primary': True,
                'is_decision_maker': True
            },
            {
                'organization_id': 2,
                'name': '李经理',
                'position': '安全经理',
                'phone': '13900139000',
                'email': 'li@bankofchina.com',
                'ai_preferred_channel': 'email',
                'ai_interaction_frequency': 3,
                'last_ai_interaction': '2026-03-08',
                'next_ai_interaction': '2026-03-20',
                'ai_relationship_score': 0.6,
                'ai_communication_style': 'detailed',
                'is_primary': True,
                'is_decision_maker': False
            }
        ]
        
        for contact in contacts:
            cursor.execute('''
                INSERT INTO contacts 
                (organization_id, name, position, phone, email,
                 ai_preferred_channel, ai_interaction_frequency, last_ai_interaction, next_ai_interaction,
                 ai_relationship_score, ai_communication_style,
                 is_primary, is_decision_maker)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contact['organization_id'],
                contact['name'],
                contact['position'],
                contact['phone'],
                contact['email'],
                contact['ai_preferred_channel'],
                contact['ai_interaction_frequency'],
                contact['last_ai_interaction'],
                contact['next_ai_interaction'],
                contact['ai_relationship_score'],
                contact['ai_communication_style'],
                contact['is_primary'],
                contact['is_decision_maker']
            ))
        
        # 插入示例AI决策
        print("插入示例AI决策...")
        
        for i in range(1, 4):
            decision_id = f"decision_example_{i}"
            agent_id = random.randint(1, 5)
            decision_type = random.choice(['customer_segmentation', 'opportunity_priority', 'engagement_strategy'])
            target_entity_id = random.randint(1, 2)
            
            decision_data = {
                'segment': '战略客户' if target_entity_id == 1 else '活跃客户',
                'actions': ['高层会议', '定制方案'] if target_entity_id == 1 else ['定期沟通', '产品培训'],
                'confidence': random.uniform(0.7, 0.9)
            }
            
            cursor.execute('''
                INSERT INTO ai_decisions 
                (decision_id, agent_id, decision_type, target_entity_type, target_entity_id,
                 decision_data, rationale, confidence_score, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                decision_id,
                agent_id,
                decision_type,
                'customer',
                target_entity_id,
                json.dumps(decision_data, ensure_ascii=False),
                f'AI自动决策示例 {i}: {decision_type}',
                decision_data['confidence'],
                random.choice(['approved', 'completed'])
            ))
        
        # 插入示例AI任务
        print("插入示例AI任务...")
        
        for i in range(1, 4):
            task_id = f"task_example_{i}"
            agent_id = random.randint(1, 5)
            customer_id = random.randint(1, 2)
            
            cursor.execute('''
                INSERT INTO ai_managed_tasks 
                (task_id, agent_id, customer_id, task_type, task_description,
                 priority, status, scheduled_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_id,
                agent_id,
                customer_id,
                random.choice(['customer_outreach', 'opportunity_followup', 'renewal_reminder']),
                f'示例任务 {i}: 客户{customer_id}的{random.choice(["沟通", "跟进", "提醒"])}',
                random.choice(['low', 'medium', 'high']),
                random.choice(['pending', 'scheduled', 'completed']),
                (datetime.now() + timedelta(days=random.randint(1, 30))).isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        print("✅ AI管理的CRM数据库初始化成功！")
        print(f"📁 数据库文件: {db_path}")
        print("\n📊 初始化数据:")
        print("   • 5个AI代理（销售经理、客户成功、关系经理、续约专家、风险分析师）")
        print("   • 2个示例客户（国家电网、中国银行）")
        print("   • 2个示例联系人")
        print("   • 3个示例AI决策")
        print("   • 3个示例AI任务")
        
        return True
        
    except Exception as e:
        print(f"❌ AI管理的CRM数据库初始化失败: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def add_new_partner(name, department, phone, added_by='韩晓晨'):
    """添加新的合作伙伴信息"""
    db_path = os.path.join(os.path.dirname(__file__), 'crm_ai_manager.db')
    
    if not os.path.exists(db_path):
        print("❌ 数据库不存在，请先初始化")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 添加客户组织（合作伙伴）
        print(f"添加合作伙伴组织: {name} - {department}")
        
        # 生成组织名称
        org_name = f"{name} - {department}" if department else name
        
        cursor.execute('''
            INSERT INTO customer_organizations 
            (name, type, industry, scale, security_level,
             ai_managed_segment, ai_engagement_score, ai_relationship_stage, ai_management_priority,
             using_netshield, using_inoc,
             health_score, potential_score, risk_level, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            org_name,
            'partner',  # 合作伙伴类型
            '电力能源',  # 行业（根据部门判断）
            'medium',   # 规模（假设中等）
            'standard', # 安全等级
            '高潜力客户', # AI管理细分
            0.4,        # AI互动评分（初始值）
            'new',      # 关系阶段：新认识
            6,          # 管理优先级：中等偏高
            False,      # 未使用网盾
            False,      # 未使用I-NOC
            100,        # 健康度评分（初始满分）
            80,         # 潜力评分
            'low',      # 风险等级
            added_by    # 创建人
        ))
        
        org_id = cursor.lastrowid
        print(f"✅ 合作伙伴组织添加成功，ID: {org_id}")
        
        # 添加联系人（马强）
        print(f"添加联系人: {name}，电话: {phone}")
        
        cursor.execute('''
            INSERT INTO contacts 
            (organization_id, name, position, phone,
             ai_preferred_channel, ai_interaction_frequency, last_ai_interaction, next_ai_interaction,
             ai_relationship_score, ai_communication_style,
             is_primary, is_decision_maker)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            org_id,
            name,
            department,  # 职位使用部门信息
            phone,
            'phone',     # 偏好沟通渠道：电话
            0,           # 互动频率：初始0
            datetime.now().date().isoformat(),  # 最后互动：今天
            (datetime.now() + timedelta(days=7)).date().isoformat(),  # 下次互动：7天后
            0.5,         # AI关系评分：初始0.5
            'direct',    # 沟通风格：直接
            True,        # 主要联系人
            True         # 决策者
        ))
        
        contact_id = cursor.lastrowid
        print(f"✅ 联系人添加成功，ID: {contact_id}")
        
        # AI自动创建一个初始决策：客户细分
        decision_id = f"decision_new_partner_{org_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor.execute('''
            INSERT INTO ai_decisions 
            (decision_id, agent_id, decision_type, target_entity_type, target_entity_id,
             decision_data, rationale, confidence_score, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            decision_id,
            3,  # AI关系经理
            'customer_segmentation',
            'customer',
            org_id,
            json.dumps({
                'segment': '高潜力客户',
                'recommended_actions': ['建立初步关系', '了解业务需求', '探索合作机会'],
                'timeline': '30天'
            }, ensure_ascii=False),
            f'新合作伙伴{org_name}初始分析：电力行业合作伙伴，有合作潜力',
            0.8,
            'approved'
        ))
        
        # AI自动创建一个初始任务：建立联系
        task_id = f"task_new_partner_{org_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor.execute('''
            INSERT INTO ai_managed_tasks 
            (task_id, agent_id, customer_id, contact_id, task_type, task_description,
             priority, status, scheduled_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_id,
            3,  # AI关系经理
            org_id,
            contact_id,
            'customer_outreach',
            f'与新合作伙伴{name}建立联系，了解合作机会',
            'medium',
            'scheduled',
            (datetime.now() + timedelta(days=3)).isoformat()  # 3天后执行
        ))
        
        conn.commit()
        conn.close()
        
        print("\n🎯 AI管理已启动:")
        print(f"   • AI关系经理已制定客户细分决策 (ID: {decision_id})")
        print(f"   • AI已创建建立联系任务 (ID: {task_id})")
        print(f"   • 计划3天后自动执行首次联系")
        
        return {
            'organization_id': org_id,
            'contact_id': contact_id,
            'decision_id': decision_id,
            'task_id': task_id
        }
        
    except Exception as e:
        print(f"❌ 添加合作伙伴失败: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == '__main__':
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='AI管理的CRM数据库工具')
    parser.add_argument('--recreate', action='store_true', help='重新创建数据库')
    parser.add_argument('--add-partner', nargs=3, metavar=('NAME', 'DEPARTMENT', 'PHONE'), help='添加新的合作伙伴')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🤖 AI管理的CRM数据库工具")
    print("专为AI作为管理者的CRM系统设计")
    print("=" * 60)
    
    if args.add_partner:
        # 添加新合作伙伴
        name, department, phone = args.add_partner
        
        # 先确保数据库存在
        if not os.path.exists(os.path.join(os.path.dirname(__file__), 'crm_ai_manager.db')):
            print("数据库不存在，先初始化...")
            init_database()
        
        result = add_new_partner(name, department, phone)
        if result:
            print(f"\n✅ 合作伙伴 '{name}' 已成功添加到AI管理的CRM系统")
            print(f"   组织ID: {result['organization_id']}")
            print(f"   联系人ID: {result['contact_id']}")
            print(f"   AI决策ID: {result['decision_id']}")
            print(f"   AI任务ID: {result['task_id']}")
    else:
        # 初始化数据库
        success = init_database(recreate=args.recreate)
        
        if success:
            print("\n🚀 下一步:")
            print("1. 启动AI管理服务: python ai_manager_crm_app.py")
            print("2. 默认端口: 5003")
            print("3. 默认API密钥: ai-manager-api-key-change-me")
            print("4. 访问 http://localhost:5003 查看AI管理界面")
            print("\n📋 添加合作伙伴示例:")
            print("   python init_ai_manager_db.py --add-partner '马强' '中际联合电力事业部' '13910385263'")