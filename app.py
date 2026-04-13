#!/usr/bin/env python3
"""
市场营销官CRM系统 - 主应用
版本：1.0
"""

import os
import sqlite3
import json
from datetime import datetime
from flask import Flask, request, jsonify, g, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'crm.db')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db():
    """初始化数据库"""
    with app.app_context():
        db = get_db()
        with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), 'r') as f:
            db.executescript(f.read())
        db.commit()

@app.teardown_appcontext
def close_db(error):
    """关闭数据库连接"""
    if hasattr(g, 'db'):
        g.db.close()

# 工具函数
def dict_from_row(row):
    """将SQLite行转换为字典"""
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}

def parse_json_fields(data, json_fields):
    """解析JSON字段"""
    for field in json_fields:
        if field in data and data[field]:
            if isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except json.JSONDecodeError:
                    pass
    return data

# 客户单位管理API
@app.route('/api/customer-organizations', methods=['GET'])
def get_customer_organizations():
    """获取客户单位列表"""
    db = get_db()
    cursor = db.execute('''
        SELECT * FROM customer_organizations 
        ORDER BY updated_at DESC
    ''')
    organizations = [dict_from_row(row) for row in cursor.fetchall()]
    return jsonify(organizations)

@app.route('/api/customer-organizations/<int:org_id>', methods=['GET'])
def get_customer_organization(org_id):
    """获取特定客户单位"""
    db = get_db()
    cursor = db.execute('SELECT * FROM customer_organizations WHERE id = ?', (org_id,))
    org = cursor.fetchone()
    if org is None:
        return jsonify({'error': '客户单位不存在'}), 404
    return jsonify(dict_from_row(org))

@app.route('/api/customer-organizations', methods=['POST'])
def create_customer_organization():
    """创建客户单位"""
    data = request.json
    required_fields = ['name', 'type', 'created_by']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
    
    db = get_db()
    cursor = db.execute('''
        INSERT INTO customer_organizations 
        (name, type, industry, scale, address, phone, email, 
         invoice_info, tax_number, bank_account, potential_score,
         classification, tags, created_by, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'],
        data['type'],
        data.get('industry'),
        data.get('scale'),
        data.get('address'),
        data.get('phone'),
        data.get('email'),
        data.get('invoice_info'),
        data.get('tax_number'),
        data.get('bank_account'),
        data.get('potential_score', 0),
        data.get('classification'),
        json.dumps(data.get('tags', [])) if data.get('tags') else None,
        data['created_by'],
        data.get('notes')
    ))
    db.commit()
    return jsonify({'id': cursor.lastrowid, 'message': '客户单位创建成功'}), 201

@app.route('/api/customer-organizations/<int:org_id>', methods=['PUT'])
def update_customer_organization(org_id):
    """更新客户单位"""
    data = request.json
    db = get_db()
    
    # 检查客户单位是否存在
    cursor = db.execute('SELECT id FROM customer_organizations WHERE id = ?', (org_id,))
    if cursor.fetchone() is None:
        return jsonify({'error': '客户单位不存在'}), 404
    
    # 构建更新语句
    update_fields = []
    update_values = []
    field_mapping = {
        'name': 'name',
        'type': 'type',
        'industry': 'industry',
        'scale': 'scale',
        'address': 'address',
        'phone': 'phone',
        'email': 'email',
        'invoice_info': 'invoice_info',
        'tax_number': 'tax_number',
        'bank_account': 'bank_account',
        'potential_score': 'potential_score',
        'classification': 'classification',
        'tags': 'tags',
        'notes': 'notes'
    }
    
    for key, db_field in field_mapping.items():
        if key in data:
            update_fields.append(f'{db_field} = ?')
            if key == 'tags' and data[key]:
                update_values.append(json.dumps(data[key]))
            else:
                update_values.append(data[key])
    
    if not update_fields:
        return jsonify({'error': '没有提供更新字段'}), 400
    
    update_values.append(org_id)
    update_sql = f'''
        UPDATE customer_organizations 
        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    '''
    
    db.execute(update_sql, update_values)
    db.commit()
    return jsonify({'message': '客户单位更新成功'})

# 联系人管理API
@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """获取联系人列表"""
    organization_id = request.args.get('organization_id')
    db = get_db()
    
    if organization_id:
        cursor = db.execute('''
            SELECT * FROM contacts 
            WHERE organization_id = ?
            ORDER BY is_primary DESC, name
        ''', (organization_id,))
    else:
        cursor = db.execute('''
            SELECT * FROM contacts 
            ORDER BY updated_at DESC
        ''')
    
    contacts = [dict_from_row(row) for row in cursor.fetchall()]
    return jsonify(contacts)

@app.route('/api/contacts', methods=['POST'])
def create_contact():
    """创建联系人"""
    data = request.json
    required_fields = ['organization_id', 'name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
    
    db = get_db()
    cursor = db.execute('''
        INSERT INTO contacts 
        (organization_id, name, position, phone, email, 
         is_alumni, alumni_info, other_info, is_primary, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['organization_id'],
        data['name'],
        data.get('position'),
        data.get('phone'),
        data.get('email'),
        data.get('is_alumni', False),
        json.dumps(data.get('alumni_info')) if data.get('alumni_info') else None,
        data.get('other_info'),
        data.get('is_primary', False),
        json.dumps(data.get('tags', [])) if data.get('tags') else None
    ))
    db.commit()
    return jsonify({'id': cursor.lastrowid, 'message': '联系人创建成功'}), 201

# 销售机会管理API
@app.route('/api/sales-opportunities', methods=['GET'])
def get_sales_opportunities():
    """获取销售机会列表"""
    stage = request.args.get('stage')
    assigned_to = request.args.get('assigned_to')
    status = request.args.get('status', 'active')
    
    db = get_db()
    query = 'SELECT * FROM sales_opportunities WHERE status = ?'
    params = [status]
    
    if stage:
        query += ' AND stage = ?'
        params.append(stage)
    if assigned_to:
        query += ' AND assigned_to = ?'
        params.append(assigned_to)
    
    query += ' ORDER BY updated_at DESC'
    cursor = db.execute(query, params)
    
    opportunities = [dict_from_row(row) for row in cursor.fetchall()]
    return jsonify(opportunities)

@app.route('/api/sales-opportunities', methods=['POST'])
def create_sales_opportunity():
    """创建销售机会"""
    data = request.json
    required_fields = ['organization_id', 'opportunity_name', 'stage', 'assigned_to']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
    
    db = get_db()
    cursor = db.execute('''
        INSERT INTO sales_opportunities 
        (organization_id, opportunity_name, source, stage, 
         estimated_amount, estimated_close_date, probability, 
         priority, assigned_to, tags, description, requirements, competitors)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['organization_id'],
        data['opportunity_name'],
        data.get('source'),
        data['stage'],
        data.get('estimated_amount'),
        data.get('estimated_close_date'),
        data.get('probability'),
        data.get('priority', 'medium'),
        data['assigned_to'],
        json.dumps(data.get('tags', [])) if data.get('tags') else None,
        data.get('description'),
        data.get('requirements'),
        data.get('competitors')
    ))
    db.commit()
    return jsonify({'id': cursor.lastrowid, 'message': '销售机会创建成功'}), 201

# 合同管理API
@app.route('/api/contracts', methods=['GET'])
def get_contracts():
    """获取合同列表"""
    status = request.args.get('status')
    organization_id = request.args.get('organization_id')
    
    db = get_db()
    query = 'SELECT * FROM contracts WHERE 1=1'
    params = []
    
    if status:
        query += ' AND status = ?'
        params.append(status)
    if organization_id:
        query += ' AND organization_id = ?'
        params.append(organization_id)
    
    query += ' ORDER BY updated_at DESC'
    cursor = db.execute(query, params)
    
    contracts = [dict_from_row(row) for row in cursor.fetchall()]
    return jsonify(contracts)

@app.route('/api/contracts/<int:contract_id>', methods=['GET'])
def get_contract(contract_id):
    """获取单个合同"""
    db = get_db()
    cursor = db.execute('SELECT * FROM contracts WHERE id = ?', (contract_id,))
    row = cursor.fetchone()
    if row is None:
        return jsonify({'error': '合同不存在'}), 404
    return jsonify(dict_from_row(row))

@app.route('/api/contracts', methods=['POST'])
def create_contract():
    """创建合同"""
    data = request.json
    required_fields = ['contract_number', 'contract_name', 'organization_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
    
    db = get_db()
    cursor = db.execute('''
        INSERT INTO contracts 
        (opportunity_id, organization_id, contract_number, contract_name, contract_amount, 
         currency, start_date, end_date, duration_months, contract_type, status, 
         signed_date, termination_reason, renewal_date, contract_file_url, 
         terms_and_conditions, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('opportunity_id'),
        data.get('organization_id'),
        data['contract_number'],
        data['contract_name'],
        data.get('contract_amount', 0),
        data.get('currency', 'CNY'),
        data.get('start_date'),
        data.get('end_date'),
        data.get('duration_months'),
        data.get('contract_type'),
        data.get('status', 'draft'),
        data.get('signed_date'),
        data.get('termination_reason'),
        data.get('renewal_date'),
        data.get('contract_file_url'),
        data.get('terms_and_conditions'),
        json.dumps(data.get('tags', [])) if data.get('tags') else None
    ))
    db.commit()
    return jsonify({'id': cursor.lastrowid, 'message': '合同创建成功'}), 201

@app.route('/api/contracts/<int:contract_id>', methods=['PUT'])
def update_contract(contract_id):
    """更新合同"""
    data = request.json
    db = get_db()
    
    # 检查合同是否存在
    cursor = db.execute('SELECT id FROM contracts WHERE id = ?', (contract_id,))
    if cursor.fetchone() is None:
        return jsonify({'error': '合同不存在'}), 404
    
    # 构建更新语句
    update_fields = []
    update_values = []
    field_mapping = {
        'opportunity_id': 'opportunity_id',
        'organization_id': 'organization_id',
        'contract_number': 'contract_number',
        'contract_name': 'contract_name',
        'contract_amount': 'contract_amount',
        'currency': 'currency',
        'start_date': 'start_date',
        'end_date': 'end_date',
        'duration_months': 'duration_months',
        'contract_type': 'contract_type',
        'status': 'status',
        'signed_date': 'signed_date',
        'termination_reason': 'termination_reason',
        'renewal_date': 'renewal_date',
        'contract_file_url': 'contract_file_url',
        'terms_and_conditions': 'terms_and_conditions'
    }
    
    for key, db_field in field_mapping.items():
        if key in data:
            update_fields.append(f'{db_field} = ?')
            update_values.append(data[key])
    
    if 'tags' in data:
        update_fields.append('tags = ?')
        update_values.append(json.dumps(data['tags']) if data['tags'] else None)
    
    if not update_fields:
        return jsonify({'error': '没有提供更新字段'}), 400
    
    update_values.append(contract_id)
    update_sql = f'''
        UPDATE contracts 
        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    '''
    
    db.execute(update_sql, update_values)
    db.commit()
    return jsonify({'message': '合同更新成功'})

# 发票管理API
@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    """获取发票列表"""
    status = request.args.get('status')
    contract_id = request.args.get('contract_id')
    
    db = get_db()
    query = 'SELECT * FROM invoices WHERE 1=1'
    params = []
    
    if status:
        query += ' AND status = ?'
        params.append(status)
    if contract_id:
        query += ' AND contract_id = ?'
        params.append(contract_id)
    
    query += ' ORDER BY invoice_date DESC'
    cursor = db.execute(query, params)
    
    invoices = [dict_from_row(row) for row in cursor.fetchall()]
    return jsonify(invoices)

# 应收应付管理API
@app.route('/api/financial-transactions', methods=['GET'])
def get_financial_transactions():
    """获取应收应付记录"""
    transaction_type = request.args.get('type')
    status = request.args.get('status')
    
    db = get_db()
    query = 'SELECT * FROM financial_transactions WHERE 1=1'
    params = []
    
    if transaction_type:
        query += ' AND type = ?'
        params.append(transaction_type)
    if status:
        query += ' AND status = ?'
        params.append(status)
    
    query += ' ORDER BY due_date'
    cursor = db.execute(query, params)
    
    transactions = [dict_from_row(row) for row in cursor.fetchall()]
    return jsonify(transactions)

# 数据分析与报告API
@app.route('/api/reports/summary', methods=['GET'])
def get_summary_report():
    """获取汇总报告"""
    db = get_db()
    
    # 客户单位统计
    cursor = db.execute('SELECT COUNT(*) as count, type FROM customer_organizations GROUP BY type')
    customer_stats = {row['type']: row['count'] for row in cursor.fetchall()}
    
    # 销售机会统计
    cursor = db.execute('''
        SELECT stage, COUNT(*) as count, SUM(estimated_amount) as total_amount 
        FROM sales_opportunities 
        WHERE status = 'active'
        GROUP BY stage
    ''')
    opportunity_stats = [
        {'stage': row['stage'], 'count': row['count'], 'total_amount': row['total_amount'] or 0}
        for row in cursor.fetchall()
    ]
    
    # 合同统计
    cursor = db.execute('''
        SELECT status, COUNT(*) as count, SUM(contract_amount) as total_amount 
        FROM contracts 
        GROUP BY status
    ''')
    contract_stats = [
        {'status': row['status'], 'count': row['count'], 'total_amount': row['total_amount'] or 0}
        for row in cursor.fetchall()
    ]
    
    # 应收应付统计
    cursor = db.execute('''
        SELECT type, status, SUM(balance) as total_balance 
        FROM financial_transactions 
        GROUP BY type, status
    ''')
    financial_stats = [
        {'type': row['type'], 'status': row['status'], 'total_balance': row['total_balance'] or 0}
        for row in cursor.fetchall()
    ]
    
    return jsonify({
        'customer_stats': customer_stats,
        'opportunity_stats': opportunity_stats,
        'contract_stats': contract_stats,
        'financial_stats': financial_stats,
        'generated_at': datetime.now().isoformat()
    })

# 健康检查
@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    try:
        db = get_db()
        db.execute('SELECT 1')
        return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# 首页
@app.route('/')
def index():
    """首页"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>市场营销官CRM系统</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            h1 { color: #333; }
            .container { max-width: 800px; margin: 0 auto; }
            .api-list { background: #f5f5f5; padding: 20px; border-radius: 5px; }
            .endpoint { margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #4CAF50; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>市场营销官CRM系统</h1>
            <p>版本: 1.0 | 数据库: SQLite</p>
            <p>这是一个为市场营销官设计的CRM系统，包含客户关系管理、销售机会管理、合同管理、发票管理、应收应付管理和数据分析报告等功能。</p>
            
            <div class="api-list">
                <h2>API端点</h2>
                <div class="endpoint"><strong>GET /api/customer-organizations</strong> - 获取客户单位列表</div>
                <div class="endpoint"><strong>POST /api/customer-organizations</strong> - 创建客户单位</div>
                <div class="endpoint"><strong>GET /api/contacts</strong> - 获取联系人列表</div>
                <div class="endpoint"><strong>POST /api/contacts</strong> - 创建联系人</div>
                <div class="endpoint"><strong>GET /api/sales-opportunities</strong> - 获取销售机会列表</div>
                <div class="endpoint"><strong>POST /api/sales-opportunities</strong> - 创建销售机会</div>
                <div class="endpoint"><strong>GET /api/contracts</strong> - 获取合同列表</div>
                <div class="endpoint"><strong>GET /api/invoices</strong> - 获取发票列表</div>
                <div class="endpoint"><strong>GET /api/financial-transactions</strong> - 获取应收应付记录</div>
                <div class="endpoint"><strong>GET /api/reports/summary</strong> - 获取汇总报告</div>
                <div class="endpoint"><strong>GET /health</strong> - 健康检查</div>
            </div>
            
            <h2>使用说明</h2>
            <p>1. 首先初始化数据库: <code>python init_db.py</code></p>
            <p>2. 启动服务: <code>python app.py</code></p>
            <p>3. 访问 <a href="/api/customer-organizations">/api/customer-organizations</a> 开始使用</p>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    # 检查数据库是否存在，如果不存在则初始化
    if not os.path.exists(app.config['DATABASE']):
        print("数据库不存在，正在初始化...")
        init_db()
        print("数据库初始化完成")
    
    app.run(host='0.0.0.0', port=5000, debug=True)