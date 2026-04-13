#!/usr/bin/env python3
"""
AI管理的CRM系统
核心：AI作为管理者，负责客户关系的决策和执行
版本：3.0
端口：5003
"""

import os
import sqlite3
import json
import uuid
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, g, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'crm_ai_manager.db')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ai-manager-secret-key-change-me')
app.config['API_KEY'] = os.environ.get('CRM_AI_MANAGER_KEY', 'ai-manager-api-key-change-me')

# ==================== AI代理配置 ====================

AI_AGENTS = [
    {
        'id': 1,
        'agent_name': 'AI销售经理',
        'role': 'sales_manager',
        'capabilities': ['opportunity_identification', 'lead_qualification', 'deal_strategy', 'pricing_recommendation'],
        'authority_level': 'decision_maker',
        'description': '负责销售机会识别和转化，制定销售策略'
    },
    {
        'id': 2,
        'agent_name': 'AI客户成功经理',
        'role': 'customer_success',
        'capabilities': ['health_monitoring', 'engagement_planning', 'issue_resolution', 'value_realization'],
        'authority_level': 'executor',
        'description': '负责客户健康度管理和价值实现'
    },
    {
        'id': 3,
        'agent_name': 'AI关系经理',
        'role': 'relationship_manager',
        'capabilities': ['relationship_building', 'communication_planning', 'stakeholder_management', 'trust_development'],
        'authority_level': 'advisor',
        'description': '负责客户关系建设和维护'
    },
    {
        'id': 4,
        'agent_name': 'AI续约专家',
        'role': 'renewal_specialist',
        'capabilities': ['renewal_prediction', 'renewal_strategy', 'risk_assessment', 'negotiation_support'],
        'authority_level': 'decision_maker',
        'description': '负责客户续约管理和风险控制'
    },
    {
        'id': 5,
        'agent_name': 'AI风险分析师',
        'role': 'risk_analyst',
        'capabilities': ['risk_identification', 'impact_assessment', 'mitigation_planning', 'early_warning'],
        'authority_level': 'advisor',
        'description': '负责客户风险识别和预警'
    }
]

# ==================== 数据库工具函数 ====================

def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    """关闭数据库连接"""
    if hasattr(g, 'db'):
        g.db.close()

def dict_from_row(row):
    """将SQLite行转换为字典"""
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}

def require_api_key(f):
    """API密钥验证装饰器"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('X-API-Key'):
            return jsonify({'error': 'API key required'}), 401
        
        api_key = request.headers.get('X-API-Key')
        if api_key != app.config['API_KEY']:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# ==================== AI决策引擎 ====================

def make_ai_decision(agent_id, decision_type, target_entity_type, target_entity_id, context_data):
    """
    AI做出决策
    返回决策ID和决策详情
    """
    decision_id = f"decision_{uuid.uuid4().hex[:16]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 根据决策类型和上下文数据生成决策
    decision_data = {}
    rationale = ""
    confidence_score = random.uniform(0.7, 0.95)  # 模拟AI置信度
    
    if decision_type == 'customer_segmentation':
        # 客户细分决策
        segment = determine_customer_segment(context_data)
        decision_data = {'segment': segment, 'recommended_actions': get_segment_actions(segment)}
        rationale = f"根据客户行业{context_data.get('industry', '未知')}、规模{context_data.get('scale', '未知')}和产品使用情况{context_data.get('product_usage', '未知')}，将客户划分到{segment}细分"
    
    elif decision_type == 'opportunity_priority':
        # 销售机会优先级决策
        priority_score = calculate_opportunity_priority(context_data)
        priority_level = 'high' if priority_score >= 0.8 else 'medium' if priority_score >= 0.5 else 'low'
        decision_data = {'priority_score': priority_score, 'priority_level': priority_level, 'next_steps': get_opportunity_next_steps(priority_level)}
        rationale = f"机会评估得分{priority_score:.2f}，确定为{priority_level}优先级。主要因素：预计金额{context_data.get('estimated_amount', 0)}、成交概率{context_data.get('probability', 0)}%、客户健康度{context_data.get('health_score', 0)}"
    
    elif decision_type == 'engagement_strategy':
        # 客户互动策略决策
        strategy = determine_engagement_strategy(context_data)
        decision_data = {'strategy': strategy, 'channels': get_engagement_channels(strategy), 'frequency': get_engagement_frequency(strategy)}
        rationale = f"基于客户关系阶段{context_data.get('relationship_stage', 'new')}和互动历史{context_data.get('interaction_count', 0)}次，制定{strategy}互动策略"
    
    elif decision_type == 'renewal_action':
        # 续约行动决策
        action_plan = create_renewal_action_plan(context_data)
        decision_data = action_plan
        days_until_expiry = context_data.get('days_until_expiry', 0)
        rationale = f"许可证{days_until_expiry}天后到期，制定{len(action_plan.get('actions', []))}步续约行动计划"
    
    elif decision_type == 'risk_mitigation':
        # 风险缓解决策
        risk_assessment = assess_risk_level(context_data)
        mitigation_plan = create_mitigation_plan(risk_assessment)
        decision_data = {'risk_level': risk_assessment['level'], 'mitigation_plan': mitigation_plan}
        rationale = f"识别到{risk_assessment['risk_type']}风险，等级{risk_assessment['level']}，制定{len(mitigation_plan)}项缓解措施"
    
    # 保存决策到数据库
    db = get_db()
    cursor = db.execute('''
        INSERT INTO ai_decisions 
        (decision_id, agent_id, decision_type, target_entity_type, target_entity_id, 
         decision_data, rationale, confidence_score, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'approved')
    ''', (
        decision_id,
        agent_id,
        decision_type,
        target_entity_type,
        target_entity_id,
        json.dumps(decision_data, ensure_ascii=False),
        rationale,
        confidence_score
    ))
    
    db.commit()
    
    # 记录决策历史
    db.execute('''
        INSERT INTO ai_decision_history 
        (decision_id, agent_id, decision_type, action_taken)
        VALUES (?, ?, ?, ?)
    ''', (cursor.lastrowid, agent_id, decision_type, json.dumps({'decision_made': decision_type, 'data': decision_data})))
    
    db.commit()
    
    return {
        'decision_id': decision_id,
        'agent_id': agent_id,
        'decision_type': decision_type,
        'decision_data': decision_data,
        'rationale': rationale,
        'confidence_score': confidence_score,
        'status': 'approved'
    }

# ==================== AI决策辅助函数 ====================

def determine_customer_segment(context_data):
    """确定客户细分"""
    industry = context_data.get('industry', '')
    scale = context_data.get('scale', '')
    product_usage = context_data.get('product_usage', 0)
    
    if industry in ['电力能源', '金融', '军工'] and scale in ['large', 'enterprise', 'critical_infrastructure']:
        return '战略客户'
    elif product_usage > 20:
        return '活跃客户'
    elif context_data.get('health_score', 100) < 60:
        return '风险客户'
    elif context_data.get('potential_score', 0) > 80:
        return '高潜力客户'
    else:
        return '一般客户'

def get_segment_actions(segment):
    """获取细分对应的行动建议"""
    actions_map = {
        '战略客户': ['定期高层会议', '定制化解决方案', '专属客户成功经理', '优先技术支持'],
        '活跃客户': ['产品使用培训', '最佳实践分享', '新功能介绍', '满意度调查'],
        '风险客户': ['问题诊断会议', '使用情况分析', '改进计划制定', '客户回访'],
        '高潜力客户': ['需求深度挖掘', '解决方案演示', '成功案例分享', '试用扩展'],
        '一般客户': ['定期产品通讯', '在线培训邀请', '使用情况报告', '续约提醒']
    }
    return actions_map.get(segment, ['定期沟通', '产品支持'])

def calculate_opportunity_priority(context_data):
    """计算销售机会优先级得分"""
    estimated_amount = context_data.get('estimated_amount', 0) or 0
    probability = context_data.get('probability', 0) or 0
    health_score = context_data.get('health_score', 100) or 100
    urgency = context_data.get('urgency', 0) or 0
    
    # 标准化计算
    amount_score = min(estimated_amount / 1000000, 1.0)  # 百万级归一化
    probability_score = probability / 100.0
    health_score_norm = health_score / 100.0
    urgency_score = min(urgency / 30.0, 1.0)  # 30天内归一化
    
    # 加权综合得分
    priority_score = (
        amount_score * 0.3 +
        probability_score * 0.4 +
        health_score_norm * 0.2 +
        urgency_score * 0.1
    )
    
    return round(priority_score, 2)

def get_opportunity_next_steps(priority_level):
    """获取机会下一步行动"""
    steps_map = {
        'high': ['24小时内联系决策人', '一周内安排解决方案演示', '两周内提交正式方案', '一个月内完成技术验证'],
        'medium': ['一周内安排需求沟通', '两周内提供初步方案', '一个月内安排产品演示', '跟进客户反馈'],
        'low': ['发送产品资料', '邀请参加线上研讨会', '定期跟进需求变化', '保持联系']
    }
    return steps_map.get(priority_level, ['定期跟进', '发送更新'])

def determine_engagement_strategy(context_data):
    """确定客户互动策略"""
    relationship_stage = context_data.get('relationship_stage', 'new')
    interaction_count = context_data.get('interaction_count', 0)
    health_score = context_data.get('health_score', 100)
    
    if relationship_stage == 'new' and interaction_count < 3:
        return '建立关系'
    elif relationship_stage == 'strategic' and health_score >= 80:
        return '深化合作'
    elif health_score < 60:
        return '风险干预'
    elif interaction_count > 10:
        return '价值提升'
    else:
        return '常规维护'

def get_engagement_channels(strategy):
    """获取互动渠道"""
    channels_map = {
        '建立关系': ['会议', '电话', '微信'],
        '深化合作': ['高层会议', '联合方案', '客户活动'],
        '风险干预': ['紧急会议', '现场支持', '每日跟进'],
        '价值提升': ['培训', '最佳实践分享', '客户案例'],
        '常规维护': ['邮件', '产品通讯', '季度回顾']
    }
    return channels_map.get(strategy, ['邮件', '电话'])

def get_engagement_frequency(strategy):
    """获取互动频率"""
    frequency_map = {
        '建立关系': '每周',
        '深化合作': '每月',
        '风险干预': '每日',
        '价值提升': '每季度',
        '常规维护': '每季度'
    }
    return frequency_map.get(strategy, '每月')

def create_renewal_action_plan(context_data):
    """创建续约行动计划"""
    days_until_expiry = context_data.get('days_until_expiry', 0)
    renewal_history = context_data.get('renewal_history', [])
    
    if days_until_expiry <= 30:
        return {
            'urgency': '紧急',
            'actions': [
                {'step': 1, 'action': '立即联系客户决策人', 'timeline': '24小时内', 'owner': 'AI续约专家'},
                {'step': 2, 'action': '准备续约方案和报价', 'timeline': '3天内', 'owner': 'AI销售经理'},
                {'step': 3, 'action': '安排续约谈判会议', 'timeline': '7天内', 'owner': 'AI关系经理'},
                {'step': 4, 'action': '完成续约合同签署', 'timeline': '14天内', 'owner': 'AI客户成功经理'}
            ]
        }
    elif days_until_expiry <= 90:
        return {
            'urgency': '重要',
            'actions': [
                {'step': 1, 'action': '发送续约提醒邮件', 'timeline': '1周内', 'owner': 'AI续约专家'},
                {'step': 2, 'action': '安排续约预沟通', 'timeline': '2周内', 'owner': 'AI关系经理'},
                {'step': 3, 'action': '提供年度价值报告', 'timeline': '1个月内', 'owner': 'AI客户成功经理'},
                {'step': 4, 'action': '正式启动续约流程', 'timeline': '2个月内', 'owner': 'AI销售经理'}
            ]
        }
    else:
        return {
            'urgency': '规划中',
            'actions': [
                {'step': 1, 'action': '记录续约时间节点', 'timeline': '立即', 'owner': '系统'},
                {'step': 2, 'action': '准备客户价值分析', 'timeline': '到期前3个月', 'owner': 'AI客户成功经理'},
                {'step': 3, 'action': '制定续约策略', 'timeline': '到期前2个月', 'owner': 'AI续约专家'},
                {'step': 4, 'action': '启动续约沟通', 'timeline': '到期前1个月', 'owner': 'AI关系经理'}
            ]
        }

def assess_risk_level(context_data):
    """评估风险等级"""
    health_score = context_data.get('health_score', 100)
    usage_trend = context_data.get('usage_trend', 'stable')
    payment_history = context_data.get('payment_history', 'good')
    support_tickets = context_data.get('support_tickets', 0)
    
    risk_score = 0
    risk_type = []
    
    if health_score < 60:
        risk_score += 30
        risk_type.append('健康度低')
    if usage_trend == 'declining':
        risk_score += 25
        risk_type.append('使用下降')
    if payment_history == 'delayed':
        risk_score += 20
        risk_type.append('付款延迟')
    if support_tickets > 5:
        risk_score += 15
        risk_type.append('支持问题多')
    if context_data.get('last_interaction_days', 0) > 90:
        risk_score += 10
        risk_type.append('长期无互动')
    
    if risk_score >= 60:
        level = 'critical'
    elif risk_score >= 40:
        level = 'high'
    elif risk_score >= 20:
        level = 'medium'
    else:
        level = 'low'
    
    return {
        'risk_score': risk_score,
        'risk_level': level,
        'risk_type': risk_type,
        'assessment_time': datetime.now().isoformat()
    }

def create_mitigation_plan(risk_assessment):
    """创建风险缓解计划"""
    level = risk_assessment['risk_level']
    risk_type = risk_assessment['risk_type']
    
    base_actions = []
    
    if 'critical' in level:
        base_actions = [
            '成立应急小组',
            '制定紧急应对方案',
            '每日进度跟踪',
            '高层直接介入'
        ]
    elif 'high' in level:
        base_actions = [
            '指定专人负责',
            '制定详细改进计划',
            '每周进度汇报',
            '客户高层沟通'
        ]
    elif 'medium' in level:
        base_actions = [
            '制定改进措施',
            '定期客户沟通',
            '月度进展评估',
            '资源调配支持'
        ]
    else:
        base_actions = [
            '持续关注',
            '定期检查',
            '预防措施',
            '文档记录'
        ]
    
    # 根据风险类型添加具体措施
    specific_actions = []
    for r_type in risk_type:
        if '健康度低' in r_type:
            specific_actions.append('健康度专项提升计划')
        if '使用下降' in r_type:
            specific_actions.append('使用情况深度分析')
        if '付款延迟' in r_type:
            specific_actions.append('付款流程优化')
        if '支持问题多' in r_type:
            specific_actions.append('技术支持增强')
        if '长期无互动' in r_type:
            specific_actions.append('重新建立联系计划')
    
    return {
        'base_actions': base_actions,
        'specific_actions': specific_actions,
        'timeline': '30天' if level in ['critical', 'high'] else '60天',
        'success_criteria': ['风险等级降低', '客户满意度提升', '问题解决率达标']
    }

# ==================== AI管理API ====================

@app.route('/api/ai-agents', methods=['GET'])
@require_api_key
def get_ai_agents():
    """获取AI代理列表"""
    db = get_db()
    cursor = db.execute('SELECT * FROM ai_agents WHERE is_active = TRUE ORDER BY role')
    agents = [dict_from_row(row) for row in cursor.fetchall()]
    
    return jsonify({
        'agents': agents,
        'total': len(agents),
        'retrieved_at': datetime.now().isoformat()
    })

@app.route('/api/ai-decisions/make', methods=['POST'])
@require_api_key
def make_decision():
    """AI做出决策"""
    data = request.get_json()
    
    required_fields = ['agent_id', 'decision_type', 'target_entity_type', 'target_entity_id', 'context_data']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        decision = make_ai_decision(
            agent_id=data['agent_id'],
            decision_type=data['decision_type'],
            target_entity_type=data['target_entity_type'],
            target_entity_id=data['target_entity_id'],
            context_data=data['context_data']
        )
        
        return jsonify({
            'success': True,
            'decision': decision,
            'message': 'AI决策已生成'
        })
        
    except Exception as e:
        return jsonify({'error': f'Decision making failed: {str(e)}'}), 500

@app.route('/api/ai-decisions', methods=['GET'])
@require_api_key
def get_decisions():
    """获取AI决策列表"""
    db = get_db()
    
    agent_id = request.args.get('agent_id')
    decision_type = request.args.get('decision_type')
    status = request.args.get('status')
    limit = int(request.args.get('limit', 50))
    
    query = 'SELECT * FROM ai_decisions WHERE 1=1'
    params = []
    
    if agent_id:
        query += ' AND agent_id = ?'
        params.append(agent_id)
    
    if decision_type:
        query += ' AND decision_type = ?'
        params.append(decision_type)
    
    if status:
        query += ' AND status = ?'
        params.append(status)
    
    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)
    
    cursor = db.execute(query, params)
    decisions = [dict_from_row(row) for row in cursor.fetchall()]
    
    # 解析JSON字段
    for decision in decisions:
        if decision.get('decision_data'):
            decision['decision_data'] = json.loads(decision['decision_data'])
    
    return jsonify({
        'decisions': decisions,
        'count': len(decisions),
        'retrieved_at': datetime.now().isoformat()
    })

@app.route('/api/ai-tasks', methods=['GET'])
@require_api_key
def get_ai_tasks():
    """获取AI管理任务"""
    db = get_db()
    
    agent_id = request.args.get('agent_id')
    customer_id = request.args.get('customer_id')
    status = request.args.get('status')
    priority = request.args.get('priority')
    limit = int(request.args.get('limit', 50))
    
    query = '''
        SELECT t.*, c.name as customer_name, a.agent_name
        FROM ai_managed_tasks t
        LEFT JOIN customer_organizations c ON t.customer_id = c.id
        LEFT JOIN ai_agents a ON t.agent_id = a.id
        WHERE 1=1
    '''
    params = []
    
    if agent_id:
        query += ' AND t.agent_id = ?'
        params.append(agent_id)
    
    if customer_id:
        query += ' AND t.customer_id = ?'
        params.append(customer_id)
    
    if status:
        query += ' AND t.status = ?'
        params.append(status)
    
    if priority:
        query += ' AND t.priority = ?'
        params.append(priority)
    
    query += ' ORDER BY t.priority DESC, t.scheduled_time ASC LIMIT ?'
    params.append(limit)
    
    cursor = db.execute(query, params)
    tasks = [dict_from_row(row) for row in cursor.fetchall()]
    
    return jsonify({
        'tasks': tasks,
        'count': len(tasks),
        'retrieved_at': datetime.now().isoformat()
    })

@app.route('/api/ai-tasks/create', methods=['POST'])
@require_api_key
def create_ai_task():
    """创建AI管理任务"""
    data = request.get_json()
    
    required_fields = ['agent_id', 'customer_id', 'task_type', 'task_description']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    task_id = f"task_{uuid.uuid4().hex[:16]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    db = get_db()
    
    try:
        cursor = db.execute('''
            INSERT INTO ai_managed_tasks 
            (task_id, agent_id, customer_id, contact_id, task_type, task_description,
             expected_outcome, priority, status, scheduled_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_id,
            data['agent_id'],
            data['customer_id'],
            data.get('contact_id'),
            data['task_type'],
            data['task_description'],
            data.get('expected_outcome'),
            data.get('priority', 'medium'),
            data.get('status', 'pending'),
            data.get('scheduled_time', datetime.now().isoformat())
        ))
        
        task_db_id = cursor.lastrowid
        db.commit()
        
        # 获取任务详情
        cursor = db.execute('''
            SELECT t.*, c.name as customer_name, a.agent_name
            FROM ai_managed_tasks t
            LEFT JOIN customer_organizations c ON t.customer_id = c.id
            LEFT JOIN ai_agents a ON t.agent_id = a.id
            WHERE t.id = ?
        ''', (task_db_id,))
        
        task = dict_from_row(cursor.fetchone())
        
        return jsonify({
            'success': True,
            'task': task,
            'message': 'AI任务已创建'
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Task creation failed: {str(e)}'}), 500

@app.route('/api/ai-tasks/<string:task_id>/execute', methods=['POST'])
@require_api_key
def execute_ai_task(task_id):
    """执行AI任务"""
    data = request.get_json() or {}
    
    db = get_db()
    
    # 获取任务信息
    cursor = db.execute('SELECT * FROM ai_managed_tasks WHERE task_id = ?', (task_id,))
    task = dict_from_row(cursor.fetchone())
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    if task['status'] not in ['pending', 'scheduled']:
        return jsonify({'error': f'Task status {task["status"]} cannot be executed'}), 400
    
    start_time = datetime.now()
    
    try:
        # 更新任务状态为执行中
        db.execute('''
            UPDATE ai_managed_tasks 
            SET status = 'in_progress', started_time = ?
            WHERE task_id = ?
        ''', (start_time.isoformat(), task_id))
        
        # 根据任务类型执行相应操作
        task_type = task['task_type']
        execution_result = {
            'task_id': task_id,
            'task_type': task_type,
            'execution_started': start_time.isoformat(),
            'actions_taken': []
        }
        
        if task_type == 'customer_outreach':
            # 客户沟通任务
            communication_result = execute_customer_outreach(task)
            execution_result['actions_taken'].append(communication_result)
            
        elif task_type == 'opportunity_followup':
            # 机会跟进任务
            followup_result = execute_opportunity_followup(task)
            execution_result['actions_taken'].append(followup_result)
            
        elif task_type == 'renewal_reminder':
            # 续约提醒任务
            reminder_result = execute_renewal_reminder(task)
            execution_result['actions_taken'].append(reminder_result)
            
        elif task_type == 'risk_mitigation':
            # 风险缓解任务
            mitigation_result = execute_risk_mitigation(task)
            execution_result['actions_taken'].append(mitigation_result)
        
        # 更新任务为完成
        completed_time = datetime.now()
        db.execute('''
            UPDATE ai_managed_tasks 
            SET status = 'completed', completed_time = ?, 
                execution_details = ?, outcome_achieved = ?,
                success_score = ?
            WHERE task_id = ?
        ''', (
            completed_time.isoformat(),
            json.dumps(execution_result, ensure_ascii=False),
            data.get('outcome', '任务执行完成'),
            data.get('success_score', 0.8),
            task_id
        ))
        
        db.commit()
        
        execution_result['execution_completed'] = completed_time.isoformat()
        execution_result['duration_seconds'] = (completed_time - start_time).total_seconds()
        execution_result['status'] = 'success'
        
        return jsonify({
            'success': True,
            'execution_result': execution_result,
            'message': 'AI任务执行完成'
        })
        
    except Exception as e:
        error_time = datetime.now()
        
        # 更新任务为失败
        db.execute('''
            UPDATE ai_managed_tasks 
            SET status = 'failed', completed_time = ?, 
                execution_details = ?
            WHERE task_id = ?
        ''', (
            error_time.isoformat(),
            json.dumps({'error': str(e), 'execution_time': error_time.isoformat()}, ensure_ascii=False),
            task_id
        ))
        
        db.commit()
        
        return jsonify({'error': f'Task execution failed: {str(e)}'}), 500

def execute_customer_outreach(task):
    """执行客户沟通任务"""
    # 这里应该是实际的沟通执行逻辑
    # 目前模拟执行
    return {
        'action': 'customer_outreach',
        'method': 'email',  # 假设通过邮件沟通
        'content_preview': f"与客户{task.get('customer_id')}进行沟通：{task.get('task_description', '')}",
        'status': '模拟执行',
        'timestamp': datetime.now().isoformat()
    }

def execute_opportunity_followup(task):
    """执行机会跟进任务"""
    return {
        'action': 'opportunity_followup',
        'method': 'meeting_scheduled',
        'content_preview': f"安排销售机会跟进会议",
        'status': '模拟执行',
        'timestamp': datetime.now().isoformat()
    }

def execute_renewal_reminder(task):
    """执行续约提醒任务"""
    return {
        'action': 'renewal_reminder',
        'method': 'notification_sent',
        'content_preview': f"发送续约提醒",
        'status': '模拟执行',
        'timestamp': datetime.now().isoformat()
    }

def execute_risk_mitigation(task):
    """执行风险缓解任务"""
    return {
        'action': 'risk_mitigation',
        'method': 'plan_activated',
        'content_preview': f"启动风险缓解计划",
        'status': '模拟执行',
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/ai-dashboard', methods=['GET'])
@require_api_key
def get_ai_dashboard():
    """获取AI管理仪表盘"""
    db = get_db()
    
    # 获取仪表盘数据
    cursor = db.execute('SELECT * FROM ai_management_dashboard LIMIT 1')
    dashboard_data = dict_from_row(cursor.fetchone())
    
    # 获取AI代理绩效
    cursor = db.execute('SELECT * FROM ai_performance_overview')
    agent_performance = [dict_from_row(row) for row in cursor.fetchall()]
    
    # 获取待处理任务
    cursor = db.execute('''
        SELECT t.*, c.name as customer_name, a.agent_name
        FROM ai_managed_tasks t
        LEFT JOIN customer_organizations c ON t.customer_id = c.id
        LEFT JOIN ai_agents a ON t.agent_id = a.id
        WHERE t.status IN ('pending', 'scheduled')
        ORDER BY t.priority DESC, t.scheduled_time ASC
        LIMIT 10
    ''')
    pending_tasks = [dict_from_row(row) for row in cursor.fetchall()]
    
    # 获取待批准决策
    cursor = db.execute('''
        SELECT d.*, a.agent_name
        FROM ai_decisions d
        LEFT JOIN ai_agents a ON d.agent_id = a.id
        WHERE d.status = 'pending'
        ORDER BY d.created_at DESC
        LIMIT 5
    ''')
    pending_decisions = [dict_from_row(row) for row in cursor.fetchall()]
    
    # 解析JSON字段
    for decision in pending_decisions:
        if decision.get('decision_data'):
            decision['decision_data'] = json.loads(decision['decision_data'])
    
    return jsonify({
        'dashboard': dashboard_data,
        'agent_performance': agent_performance,
        'pending_tasks': pending_tasks,
        'pending_decisions': pending_decisions,
        'generated_at': datetime.now().isoformat()
    })

# ==================== 客户管理API（AI管理优化版） ====================

@app.route('/api/ai-customers', methods=['GET'])
@require_api_key
def get_ai_customers():
    """获取AI管理的客户列表"""
    db = get_db()
    
    segment = request.args.get('segment')
    relationship_stage = request.args.get('relationship_stage')
    priority = request.args.get('priority')
    limit = int(request.args.get('limit', 50))
    
    query = '''
        SELECT 
            c.*,
            (SELECT COUNT(*) FROM ai_managed_tasks t WHERE t.customer_id = c.id AND t.status IN ('pending', 'scheduled')) as pending_tasks,
            (SELECT COUNT(*) FROM ai_decisions d WHERE d.target_entity_type = 'customer' AND d.target_entity_id = c.id AND d.status = 'executing') as active_decisions,
            (SELECT COUNT(*) FROM ai_communications com WHERE com.customer_id = c.id AND DATE(com.created_at) = DATE('now')) as today_communications
        FROM customer_organizations c
        WHERE 1=1
    '''
    params = []
    
    if segment:
        query += ' AND c.ai_managed_segment = ?'
        params.append(segment)
    
    if relationship_stage:
        query += ' AND c.ai_relationship_stage = ?'
        params.append(relationship_stage)
    
    if priority:
        query += ' AND c.ai_management_priority > 0'
        if priority == 'high':
            query += ' AND c.ai_management_priority >= 8'
        elif priority == 'medium':
            query += ' AND c.ai_management_priority BETWEEN 4 AND 7'
    
    query += ' ORDER BY c.ai_management_priority DESC, c.health_score ASC LIMIT ?'
    params.append(limit)
    
    cursor = db.execute(query, params)
    customers = [dict_from_row(row) for row in cursor.fetchall()]
    
    # 解析JSON字段
    for customer in customers:
        if customer.get('inoc_modules'):
            customer['inoc_modules'] = json.loads(customer['inoc_modules'])
    
    return jsonify({
        'customers': customers,
        'count': len(customers),
        'ai_managed': True,
        'retrieved_at': datetime.now().isoformat()
    })

@app.route('/api/ai-customers/<int:customer_id>/analyze', methods=['POST'])
@require_api_key
def analyze_customer(customer_id):
    """AI分析客户"""
    db = get_db()
    
    # 获取客户信息
    cursor = db.execute('SELECT * FROM customer_organizations WHERE id = ?', (customer_id,))
    customer = dict_from_row(cursor.fetchone())
    
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    # 获取相关数据
    cursor = db.execute('''
        SELECT 
            (SELECT COUNT(*) FROM ai_managed_tasks WHERE customer_id = ? AND status IN ('pending', 'scheduled')) as pending_tasks,
            (SELECT COUNT(*) FROM ai_communications WHERE customer_id = ? AND DATE(created_at) >= DATE('now', '-30 days')) as recent_communications,
            (SELECT AVG(sentiment_score) FROM ai_communications WHERE customer_id = ? AND direction = 'inbound') as avg_sentiment
    ''', (customer_id, customer_id, customer_id))
    
    stats = dict_from_row(cursor.fetchone())
    
    # AI分析
    analysis_result = {
        'customer_id': customer_id,
        'customer_name': customer['name'],
        'analysis_time': datetime.now().isoformat(),
        
        'current_state': {
            'health_score': customer['health_score'],
            'relationship_stage': customer['ai_relationship_stage'],
            'engagement_score': customer['ai_engagement_score'],
            'management_priority': customer['ai_management_priority']
        },
        
        'activity_analysis': {
            'pending_tasks': stats['pending_tasks'] or 0,
            'recent_communications': stats['recent_communications'] or 0,
            'avg_sentiment': stats['avg_sentiment'] or 0.5
        },
        
        'ai_recommendations': []
    }
    
    # 生成推荐
    recommendations = []
    
    if customer['health_score'] < 60:
        recommendations.append({
            'type': 'health_intervention',
            'priority': 'high',
            'action': '立即启动健康度提升计划',
            'rationale': f'客户健康度评分{customer["health_score"]}分，低于安全阈值',
            'expected_impact': '健康度提升20+分'
        })
    
    if customer['ai_engagement_score'] < 0.3:
        recommendations.append({
            'type': 'engagement_boost',
            'priority': 'high',
            'action': '增加互动频率和深度',
            'rationale': f'客户互动评分{customer["ai_engagement_score"]:.2f}，互动不足',
            'expected_impact': '互动评分提升0.3+'
        })
    
    if customer.get('netshield_license_expiry'):
        expiry_date = datetime.strptime(customer['netshield_license_expiry'], '%Y-%m-%d')
        days_until = (expiry_date - datetime.now()).days
        if 0 < days_until <= 90:
            recommendations.append({
                'type': 'renewal_preparation',
                'priority': 'medium' if days_until > 30 else 'high',
                'action': f'启动续约准备工作（{days_until}天后到期）',
                'rationale': '许可证即将到期，需要提前准备续约',
                'expected_impact': '确保续约成功'
            })
    
    if stats['pending_tasks'] and stats['pending_tasks'] > 5:
        recommendations.append({
            'type': 'task_optimization',
            'priority': 'medium',
            'action': '优化任务分配和执行',
            'rationale': f'有{stats["pending_tasks"]}个待处理任务，需要优化',
            'expected_impact': '任务完成率提升'
        })
    
    analysis_result['ai_recommendations'] = recommendations
    
    # 保存分析结果
    db.execute('''
        INSERT INTO ai_decisions 
        (decision_id, agent_id, decision_type, target_entity_type, target_entity_id,
         decision_data, rationale, confidence_score, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'completed')
    ''', (
        f"analysis_{uuid.uuid4().hex[:16]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        2,  # AI客户成功经理
        'customer_segmentation',
        'customer',
        customer_id,
        json.dumps(analysis_result, ensure_ascii=False),
        f'AI对客户{customer["name"]}进行全面分析，生成{len(recommendations)}条推荐',
        0.85,
        'completed'
    ))
    
    db.commit()
    
    return jsonify({
        'success': True,
        'analysis': analysis_result,
        'message': 'AI客户分析完成'
    })

# ==================== 首页和健康检查 ====================

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    try:
        db = get_db()
        db.execute('SELECT 1')
        
        # 检查核心表状态
        tables = ['ai_agents', 'ai_decisions', 'ai_managed_tasks', 'customer_organizations']
        table_status = {}
        
        for table in tables:
            try:
                cursor = db.execute(f'SELECT COUNT(*) as count FROM {table}')
                result = cursor.fetchone()
                table_status[table] = {'count': result['count'], 'status': 'healthy'}
            except Exception as e:
                table_status[table] = {'error': str(e), 'status': 'unhealthy'}
        
        # 获取AI代理状态
        cursor = db.execute('SELECT COUNT(*) as active_agents FROM ai_agents WHERE is_active = TRUE')
        active_agents = cursor.fetchone()['active_agents']
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'system': 'AI管理的CRM系统',
            'version': '3.0',
            'ai_agents_active': active_agents,
            'tables': table_status
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/')
def index():
    """首页"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI管理的CRM系统 🤖</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; background: #f0f4f8; }
            h1 { color: #2c3e50; margin-bottom: 20px; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 40px; border-bottom: 2px solid #3498db; padding-bottom: 20px; }
            .ai-features { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; margin: 40px 0; }
            .ai-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 12px; box-shadow: 0 6px 15px rgba(0,0,0,0.2); }
            .ai-card.manager { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
            .ai-card.decider { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
            .ai-card.executor { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
            .ai-card.learner { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
            .api-section { margin-top: 50px; background: #f8f9fa; padding: 25px; border-radius: 10px; }
            .endpoint { margin: 12px 0; padding: 15px; background: white; border-radius: 8px; border-left: 5px solid #2ecc71; font-family: 'Courier New', monospace; }
            .badge { display: inline-block; padding: 4px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; margin-left: 10px; }
            .badge.ai { background: #9b59b6; color: white; }
            .badge.manager { background: #e74c3c; color: white; }
            .badge.decision { background: #3498db; color: white; }
            .stats { display: flex; justify-content: space-around; margin: 30px 0; text-align: center; }
            .stat-item { padding: 20px; }
            .stat-value { font-size: 2.5em; font-weight: bold; color: #2c3e50; }
            .stat-label { color: #7f8c8d; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 AI管理的CRM系统</h1>
                <p style="font-size: 1.2em; color: #34495e;">AI不仅是工具，更是管理者。让AI负责客户关系的决策、执行和优化。</p>
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-value">5</div>
                        <div class="stat-label">AI代理</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">4</div>
                        <div class="stat-label">管理角色</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">3</div>
                        <div class="stat-label">权限级别</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">∞</div>
                        <div class="stat-label">学习能力</div>
                    </div>
                </div>
            </div>
            
            <h2>🎯 AI管理核心能力</h2>
            <div class="ai-features">
                <div class="ai-card manager">
                    <h3>📊 AI销售经理</h3>
                    <p>自动识别销售机会，制定销售策略，管理销售流程。</p>
                    <p><strong>权限：</strong> 决策者</p>
                </div>
                
                <div class="ai-card">
                    <h3>🤝 AI客户成功</h3>
                    <p>监控客户健康度，规划互动策略，确保价值实现。</p>
                    <p><strong>权限：</strong> 执行者</p>
                </div>
                
                <div class="ai-card decider">
                    <h3>🧠 AI决策引擎</h3>
                    <p>分析数据，做出决策，提供决策理由和置信度。</p>
                    <p><strong>权限：</strong> 决策者</p>
                </div>
                
                <div class="ai-card executor">
                    <h3>⚡ AI任务执行</h3>
                    <p>创建、分配、执行任务，自动化客户互动。</p>
                    <p><strong>权限：</strong> 执行者</p>
                </div>
                
                <div class="ai-card learner">
                    <h3>📈 AI学习优化</h3>
                    <p>从决策结果中学习，优化策略，提升管理效率。</p>
                    <p><strong>权限：</strong> 持续进化</p>
                </div>
            </div>
            
            <div class="api-section">
                <h2>🔧 API端点</h2>
                <p>所有API都需要 <code>X-API-Key</code> 请求头</p>
                
                <div class="endpoint">
                    <strong>GET /api/ai-agents</strong> - 获取AI代理列表<span class="badge ai">AI</span>
                </div>
                
                <div class="endpoint">
                    <strong>POST /api/ai-decisions/make</strong> - AI做出决策<span class="badge decision">决策</span>
                </div>
                
                <div class="endpoint">
                    <strong>GET /api/ai-dashboard</strong> - AI管理仪表盘<span class="badge manager">管理</span>
                </div>
                
                <div class="endpoint">
                    <strong>GET /api/ai-tasks</strong> - 获取AI管理任务
                </div>
                
                <div class="endpoint">
                    <strong>POST /api/ai-customers/{id}/analyze</strong> - AI分析客户
                </div>
                
                <div class="endpoint">
                    <strong>GET /health</strong> - 健康检查（包含AI代理状态）
                </div>
            </div>
            
            <div style="margin-top: 40px; padding: 20px; background: #e8f6f3; border-radius: 10px;">
                <h3>🚀 立即体验AI管理</h3>
                <p>1. 初始化数据库: <code>python init_ai_manager_db.py</code></p>
                <p>2. 启动AI管理服务: <code>python ai_manager_crm_app.py</code></p>
                <p>3. 设置API密钥: <code>export CRM_AI_MANAGER_KEY="ai-manager-api-key-change-me"</code></p>
                <p>4. 访问AI仪表盘: <code>curl -H "X-API-Key: ai-manager-api-key-change-me" http://localhost:5003/api/ai-dashboard</code></p>
                <p>5. 让AI做出第一个决策: <code>curl -H "X-API-Key: ..." -X POST -H "Content-Type: application/json" -d '{"agent_id":1,"decision_type":"customer_segmentation","target_entity_type":"customer","target_entity_id":1,"context_data":{}}' http://localhost:5003/api/ai-decisions/make</code></p>
            </div>
            
            <div style="margin-top: 30px; text-align: center; color: #7f8c8d; font-size: 0.9em;">
                <p>🤖 AI管理的CRM系统 v3.0 | 这不是传统CRM，这是AI作为管理者的新时代</p>
            </div>
        </div>
    </body>
    </html>
    '''

# ==================== 数据库初始化 ====================

def init_database():
    """初始化AI管理CRM数据库"""
    with app.app_context():
        db = get_db()
        
        # 读取schema文件
        schema_path = os.path.join(os.path.dirname(__file__), 'ai_manager_crm_schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print("正在创建AI管理的CRM数据库...")
        db.executescript(schema_sql)
        
        # 插入AI代理
        print("初始化AI代理...")
        for agent in AI_AGENTS:
            db.execute('''
                INSERT OR REPLACE INTO ai_agents 
                (id, agent_name, role, capabilities, authority_level, is_active)
                VALUES (?, ?, ?, ?, ?, TRUE)
            ''', (
                agent['id'],
                agent['agent_name'],
                agent['role'],
                json.dumps(agent['capabilities'], ensure_ascii=False),
                agent['authority_level']
            ))
        
        # 插入示例客户（AI管理优化）
        print("插入示例客户数据...")
        db.execute('''
            INSERT OR REPLACE INTO customer_organizations 
            (id, name, type, industry, scale, security_level, 
             ai_managed_segment, ai_engagement_score, ai_relationship_stage, ai_management_priority,
             using_netshield, netshield_version, netshield_license_expiry,
             using_inoc, inoc_modules, inoc_license_expiry,
             health_score, potential_score, risk_level, created_by)
            VALUES 
            (1, '国家电网华北分公司', 'final_customer', '电力能源', 'critical_infrastructure', 'enhanced',
             '战略客户', 0.65, 'established', 9,
             TRUE, 'v3.2', '2026-06-30',
             TRUE, '["智能发现", "根因分析"]', '2026-12-31',
             72, 95, 'medium', 'ai_manager'),
             
            (2, '中国银行信息安全部', 'final_customer', '金融', 'enterprise', 'enhanced',
             '活跃客户', 0.45, 'developing', 7,
             TRUE, 'v3.1', '2026-05-15',
             FALSE, NULL, NULL,
             88, 90, 'low', 'ai_manager'),
             
            (3, '航天科工集团', 'final_customer', '军工', 'critical_infrastructure', 'classified',
             '战略客户', 0.75, 'strategic', 10,
             TRUE, 'v3.3', '2027-01-01',
             TRUE, '["智能发现", "凭据保险箱"]', '2027-06-30',
             85, 98, 'high', 'ai_manager'),
             
            (4, '奇智科技（北京）有限公司', 'partner', '网络安全', 'medium', 'standard',
             '高潜力客户', 0.35, 'new', 5,
             FALSE, NULL, NULL,
             FALSE, NULL, NULL,
             95, 85, 'low', 'ai_manager')
        ''')
        
        # 插入示例AI决策
        print("插入示例AI决策...")
        example_decisions = [
            {
                'decision_id': f"decision_example_{i}",
                'agent_id': random.randint(1, 5),
                'decision_type': random.choice(['customer_segmentation', 'opportunity_priority', 'engagement_strategy', 'renewal_action']),
                'target_entity_type': 'customer',
                'target_entity_id': random.randint(1, 4),
                'decision_data': json.dumps({'segment': '战略客户', 'actions': ['高层会议', '定制方案']}),
                'rationale': '示例AI决策',
                'confidence_score': random.uniform(0.7, 0.95),
                'status': random.choice(['approved', 'completed', 'executing'])
            }
            for i in range(1, 6)
        ]
        
        for decision in example_decisions:
            db.execute('''
                INSERT INTO ai_decisions 
                (decision_id, agent_id, decision_type, target_entity_type, target_entity_id,
                 decision_data, rationale, confidence_score, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                decision['decision_id'],
                decision['agent_id'],
                decision['decision_type'],
                decision['target_entity_type'],
                decision['target_entity_id'],
                decision['decision_data'],
                decision['rationale'],
                decision['confidence_score'],
                decision['status']
            ))
        
        db.commit()
        print("AI管理的CRM数据库初始化完成！")

if __name__ == '__main__':
    # 检查数据库是否存在，如果不存在则初始化
    if not os.path.exists(app.config['DATABASE']):
        print("AI管理的CRM数据库不存在，正在初始化...")
        init_database()
        print("数据库初始化完成")
    
    port = int(os.environ.get('PORT', 5003))
    print(f"🤖 启动AI管理的CRM系统，端口: {port}")
    print(f"🌐 访问地址: http://0.0.0.0:{port}")
    print(f"🔑 API密钥: {app.config['API_KEY']}")
    print("📋 注意: 所有API都需要 X-API-Key 请求头")
    print("\n🎯 AI代理已就绪:")
    for agent in AI_AGENTS:
        print(f"   • {agent['agent_name']} ({agent['role']}) - 权限: {agent['authority_level']}")
    
    app.run(host='0.0.0.0', port=port, debug=True)