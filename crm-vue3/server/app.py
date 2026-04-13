import sys
#!/usr/bin/env python3
"""
CRM管理系统 - Flask后端API
支持Vue3 Element Admin前端
"""

import os
import re
import sqlite3
import json
import jwt
import hashlib
import bcrypt as bcrypt_lib
from werkzeug.security import check_password_hash as werkzeug_check
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=None)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://81.70.39.181:5000", "http://81.70.39.181"], "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})
app.config['DATABASE'] = '/root/.openclaw/workspace/crm/crm_enhanced.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

def dict_from_row(row):
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}

def row_to_dict(rows):
    return [dict_from_row(row) for row in rows]

def hash_password(password: str) -> str:
    return bcrypt_lib.hashpw(password.encode('utf-8'), bcrypt_lib.gensalt()).decode('utf-8')

# 弱口令黑名单
WEAK_PASSWORDS = {
    '123456', '123456789', '12345678', '12345', '1234567', 'password', 'passwd',
    'admin', 'admin123', 'admin888', 'administrator', 'root', 'root123',
    'demo', 'demo123', 'test', 'test123', '123123', '111111', '222222', '333333',
    '444444', '555555', '666666', '777777', '888888', '999999', '000000',
    'qwerty', 'asdfgh', 'zxcvbn', 'iloveyou', 'welcome', 'monkey', 'dragon',
    'master', 'login', 'passw0rd', 'p@ssword', 'p@ssw0rd', 'abc123', 'abcd1234',
    '123456a', '123abc', 'aaa111', 'qq123456', 'taobao', 'alipay', 'password1'
}

def check_password_strength(password: str) -> tuple:
    """
    检查密码强度，返回 (是否通过, 错误信息)
    密码要求：长度8-32位，包含大小写字母和数字
    """
    if not password:
        return False, '密码不能为空'
    if len(password) < 8:
        return False, '密码长度至少8位'
    if len(password) > 32:
        return False, '密码长度不能超过32位'
    if password.lower() in WEAK_PASSWORDS:
        return False, '禁止使用弱口令'
    if not re.search(r'[A-Z]', password):
        return False, '密码必须包含大写字母'
    if not re.search(r'[a-z]', password):
        return False, '密码必须包含小写字母'
    if not re.search(r'\d', password):
        return False, '密码必须包含数字'
    return True, ''

def verify_password(password: str, hashed: str) -> bool:
    try:
        # bcrypt format: starts with $2a$, $2b$, or $2y$
        if hashed.startswith('$2'):
            return bcrypt_lib.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        # scrypt format (werkzeug default): starts with 'scrypt:'
        elif hashed.startswith('scrypt:'):
            return werkzeug_check(hashed, password)
        # Legacy SHA256 format: 64-char hex
        elif len(hashed) == 64:
            return hashlib.sha256(password.encode()).hexdigest() == hashed
        else:
            return False
    except Exception:
        return False

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'code': 401, 'message': '缺少Token'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            g.current_user = data
        except jwt.ExpiredSignatureError:
            return jsonify({'code': 401, 'message': 'Token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'code': 401, 'message': '无效Token'}), 401
        return f(*args, **kwargs)
    return decorated

def init_database():
    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS customer_organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('final_customer', 'partner', 'undecided')),
            industry TEXT,
            scale TEXT CHECK(scale IN ('small', 'medium', 'large', 'enterprise')),
            address TEXT,
            phone TEXT,
            email TEXT,
            invoice_info TEXT,
            tax_number TEXT,
            bank_account TEXT,
            potential_score INTEGER DEFAULT 3,
            classification TEXT,
            tags TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            position TEXT,
            phone TEXT,
            email TEXT,
            is_alumni INTEGER DEFAULT 0,
            major TEXT,
            is_primary INTEGER DEFAULT 0,
            tags TEXT,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS sales_opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            opportunity_name TEXT NOT NULL,
            source TEXT,
            stage TEXT NOT NULL DEFAULT 'initial' CHECK(stage IN ('initial', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost')),
            estimated_amount REAL DEFAULT 0,
            estimated_close_date TEXT,
            probability INTEGER DEFAULT 10,
            priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high', 'urgent')),
            assigned_to TEXT NOT NULL DEFAULT '韩晓晨',
            description TEXT,
            requirements TEXT,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'closed', 'archived')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            contract_number TEXT UNIQUE NOT NULL,
            contract_name TEXT NOT NULL,
            contract_amount REAL NOT NULL,
            currency TEXT DEFAULT 'CNY',
            start_date TEXT,
            end_date TEXT,
            duration_months INTEGER,
            contract_type TEXT,
            status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'pending_approval', 'approved', 'active', 'completed', 'terminated', 'renewed')),
            signed_date TEXT,
            termination_reason TEXT,
            renewal_date TEXT,
            tags TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS customer_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            contact_id INTEGER,
            activity_type TEXT NOT NULL CHECK(activity_type IN ('call', 'visit', 'meeting', 'email', 'other')),
            activity_date DATETIME NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            recorded_by TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE,
            FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS followups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER,
            title TEXT NOT NULL,
            type TEXT DEFAULT '跟进' CHECK(type IN ('跟进', '会议', '签约', '回款', '其他')),
            due_date TEXT NOT NULL,
            priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high', 'urgent')),
            done INTEGER DEFAULT 0,
            created_by TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user' CHECK(role IN ('admin', 'user')),
            role_name TEXT DEFAULT '普通用户',
            status INTEGER DEFAULT 1,
            last_login DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TRIGGER IF NOT EXISTS update_org_timestamp AFTER UPDATE ON customer_organizations
        BEGIN UPDATE customer_organizations SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

        CREATE TRIGGER IF NOT EXISTS update_contact_timestamp AFTER UPDATE ON contacts
        BEGIN UPDATE contacts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

        CREATE TRIGGER IF NOT EXISTS update_opportunity_timestamp AFTER UPDATE ON sales_opportunities
        BEGIN UPDATE sales_opportunities SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT NOT NULL,
            contract_id INTEGER,
            organization_id INTEGER NOT NULL,
            invoice_type TEXT,
            amount REAL DEFAULT 0,
            tax_rate REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            total_amount REAL DEFAULT 0,
            billing_date TEXT,
            due_date TEXT,
            status TEXT DEFAULT 'pending',
            payment_status TEXT DEFAULT 'unpaid',
            paid_amount REAL DEFAULT 0,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            invoice_title TEXT,
            tax_number TEXT,
            bank_name TEXT,
            bank_account TEXT,
            invoice_address TEXT,
            invoice_phone TEXT
        );

        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            spec_model TEXT,
            unit TEXT,
            quantity REAL DEFAULT 1,
            unit_price REAL DEFAULT 0,
            amount REAL DEFAULT 0,
            tax_rate REAL DEFAULT 0.13,
            tax_amount REAL DEFAULT 0,
            tax_included_amount REAL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
        );
    ''')

    cursor = db.execute("SELECT id FROM users WHERE username = 'admin'")
    if cursor.fetchone() is None:
        admin_pwd = hash_password('admin123')
        db.execute('INSERT INTO users (username, password, real_name, email, role_id) VALUES (?, ?, ?, ?, ?)',
            ('admin', admin_pwd, '管理员', 'admin@crm.com', 1))
        demo_pwd = hash_password('demo123')
        db.execute('INSERT INTO users (username, password, real_name, email, role_id) VALUES (?, ?, ?, ?, ?)',
            ('hanxiaoc', demo_pwd, '韩晓晨', 'han@crm.com', 2))

    cursor = db.execute("SELECT id FROM customer_organizations LIMIT 1")
    if cursor.fetchone() is None:
        db.execute('''INSERT INTO customer_organizations (name, type, industry, scale, address, phone, email, potential_score, classification, created_by, notes) VALUES
            ('华能集团', 'final_customer', '能源电力', 'enterprise', '北京市西城区', '010-12345678', 'hn@huanneng.com', 5, 'key', 'admin', '重要客户'),
            ('国电集团', 'final_customer', '能源电力', 'enterprise', '北京市东城区', '010-87654321', 'gd@guodian.com', 5, 'key', 'admin', '重点客户'),
            ('大唐发电', 'final_customer', '能源电力', 'large', '北京市海淀区', '010-11112222', 'dt@diantan.com', 4, 'normal', 'admin', ''),
            ('中国移动', 'final_customer', '通信科技', 'enterprise', '北京市西城区', '010-99998888', 'cmcc@chinamobile.com', 4, 'normal', 'admin', ''),
            ('阿里云', 'partner', '通信科技', 'enterprise', '杭州市', '0571-12345678', 'ali@alibabacloud.com', 3, 'normal', 'admin', '合作伙伴')''')
        db.execute('''INSERT INTO contacts (organization_id, name, position, phone, email, is_primary) VALUES
            (1, '张总', '董事长', '13800138001', 'zhang@huanneng.com', 1),
            (1, '李明', 'IT总监', '13800138002', 'liming@huanneng.com', 0),
            (2, '王主任', '信息中心主任', '13800138003', 'wang@guodian.com', 1),
            (3, '赵经理', '采购部经理', '13800138004', 'zhao@diantan.com', 1),
            (4, '钱总', 'CTO', '13800138005', 'qian@chinamobile.com', 1)''')
        db.execute('''INSERT INTO sales_opportunities (organization_id, opportunity_name, source, stage, estimated_amount, probability, priority, assigned_to, requirements) VALUES
            (1, '华能智能电网项目', '客户主动联系', 'proposal', 2000000, 50, 'high', '韩晓晨', '智能运维平台建设'),
            (1, '华能数据中心安全', '展会获取', 'negotiation', 5000000, 80, 'urgent', '韩晓晨', '数据中心网络安全方案'),
            (2, '国电集团运维平台', '老客户介绍', 'initial', 1500000, 10, 'medium', '韩晓晨', '运维管理系统'),
            (3, '大唐发电安全设备', '招标信息', 'qualification', 800000, 30, 'medium', '韩晓晨', '防火墙设备采购'),
            (4, '移动云安全项目', '招标信息', 'closed_won', 3000000, 100, 'high', '韩晓晨', '云平台安全防护')''')
        db.execute('''INSERT INTO contracts (organization_id, contract_number, contract_name, contract_amount, status, start_date, end_date) VALUES
            (4, 'HT-2026-001', '中国移动云安全服务合同', 3000000, 'active', '2026-01-01', '2026-12-31'),
            (1, 'HT-2026-002', '华能集团安全设备采购', 1500000, 'active', '2026-02-01', '2026-12-31')''')
        db.execute('''INSERT INTO followups (organization_id, title, type, due_date, priority, created_by) VALUES
            (1, '联系华能张总确认项目需求', '跟进', date('now'), 'high', '韩晓晨'),
            (2, '跟进国电集团合同签订', '签约', date('now', '+1 day'), 'urgent', '韩晓晨'),
            (1, '准备华能技术方案', '跟进', date('now', '+2 days'), 'medium', '韩晓晨'),
            (3, '大唐发电招标投标', '其他', date('now', '+5 days'), 'high', '韩晓晨')''')
        db.execute('''INSERT INTO customer_activities (organization_id, activity_type, activity_date, title, description, recorded_by) VALUES
            (1, 'call', datetime('now'), '电话沟通项目需求', '与张总电话沟通了项目需求', '韩晓晨'),
            (2, 'visit', datetime('now', '-1 day'), '拜访客户信息部', '拜访了国电集团信息部负责人', '韩晓晨'),
            (3, 'meeting', datetime('now', '-3 days'), '参加产品技术交流会', '参加大唐发电组织的产品技术交流会', '韩晓晨')''')
    db.commit()

# ============== 认证API ==============

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
    db = get_db()
    
    cursor = db.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    if not user:
        return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401
    pwd_ok = verify_password(password, user['password'])
    if not pwd_ok:
        return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401
    db.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now().isoformat(), user['id']))
    db.commit()
    # 直接使用users表的role和role_name字段
    final_role_name = user['role_name'] if user['role_name'] else ('管理员' if user['role'] == 'admin' else '普通用户')
    token = jwt.encode({
        'user_id': user['id'],
        'username': user['username'],
        'name': user['real_name'],
        'role': user['role'] if user['role'] else 'user',
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({
        'code': 200,
        'token': token,
        'userInfo': {
            'id': user['id'],
            'username': user['username'],
            'name': user['real_name'],
            'email': user['email'],
            'role': user['role'],
            'roleName': final_role_name,
            'avatar': ''
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout():
    return jsonify({'code': 200, 'message': '登出成功'})

@app.route('/api/auth/userinfo', methods=['GET'])
@token_required
def get_userinfo():
    db = get_db()
    cursor = db.execute('''
        SELECT u.id, u.username, u.real_name as name, u.email, u.role, r.display_name as role_display_name 
        FROM users u 
        LEFT JOIN roles r ON u.role_id = r.id 
        WHERE u.id = ?
    ''', (g.current_user['user_id'],))
    user = cursor.fetchone()
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    result = dict_from_row(user)
    result['roleName'] = user['role_display_name'] if user['role_display_name'] else ('管理员' if user['role'] == 'admin' else '普通用户')
    return jsonify(result)


# ============== 用户管理API ==============

@app.route('/api/users', methods=['GET'])
@token_required
def get_users():
    if g.current_user.get('role') not in (1, 'admin', '1'):
        return jsonify({'code': 403, 'message': '无权限'}), 403
    db = get_db()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    keyword = request.args.get('keyword', '')
    offset = (page - 1) * page_size
    where_clauses = ['1=1']
    params = []
    if keyword:
        where_clauses.append('(username LIKE ? OR real_name LIKE ? OR email LIKE ?)')
        params.extend(['%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%'])
    where_sql = ' AND '.join(where_clauses)
    cursor = db.execute('SELECT COUNT(*) as total FROM users WHERE ' + where_sql, params)
    total = cursor.fetchone()['total']
    cursor = db.execute('SELECT id, username, real_name as name, email, role, status, last_login, created_at FROM users WHERE ' + where_sql + ' ORDER BY id ASC LIMIT ? OFFSET ?', params + [page_size, offset])
    items = [dict_from_row(r) for r in cursor.fetchall()]
    return jsonify({'items': items, 'total': total, 'page': page, 'pageSize': page_size})

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    if g.current_user.get('role') not in (1, 'admin', '1'):
        return jsonify({'code': 403, 'message': '无权限'}), 403
    data = request.json
    db = get_db()
    cursor = db.execute('SELECT id FROM users WHERE id = ?', (user_id,))
    if not cursor.fetchone():
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    fields = []
    params = []
    # 字段映射：前端字段 -> 数据库字段
    field_map = {
        'name': 'real_name',
        'email': 'email',
        'role': 'role',
        'role_id': 'role_id',
        'status': 'status'
    }
    role_reverse_map = {'admin': 'admin', 'user': 'user'}  # 数据库直接存role_name
    role_id_to_name = {1: 'admin', 2: 'user'}
    for frontend_field, value in data.items():
        if frontend_field in field_map:
            db_field = field_map[frontend_field]
            fields.append(db_field + ' = ?')
            # role_id: 1 -> 'admin', 2 -> 'user'
            if frontend_field == 'role_id':
                value = role_id_to_name.get(value, 'user')
            params.append(value)
    # 处理密码更新
    if 'password' in data and data['password']:
        pwd_hash = hash_password(data['password'])
        db.execute('UPDATE users SET password = ? WHERE id = ?', (pwd_hash, user_id))
        db.commit()
    
    if fields:
        params.append(user_id)
        db.execute('UPDATE users SET ' + ', '.join(fields) + ' WHERE id = ?', params)
        db.commit()
    return jsonify({'code': 200, 'message': '更新成功'})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    if g.current_user.get('role') not in (1, 'admin', '1'):
        return jsonify({'code': 403, 'message': '无权限'}), 403
    if user_id == 1:
        return jsonify({'code': 400, 'message': '不能删除超级管理员'}), 400
    db = get_db()
    cursor = db.execute('SELECT id FROM users WHERE id = ?', (user_id,))
    if not cursor.fetchone():
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    return jsonify({'code': 200, 'message': '删除成功'})

@app.route('/api/users/<int:user_id>/reset-password', methods=['POST'])
@token_required
def reset_user_password(user_id):
    if g.current_user.get('role') not in (1, 'admin', '1'):
        return jsonify({'code': 403, 'message': '无权限'}), 403
    import secrets
    import string
    # 生成12位随机强密码
    alphabet = string.ascii_letters + string.digits
    new_password = ''.join(secrets.choice(alphabet) for _ in range(12))
    pwd_hash = hash_password(new_password)
    db = get_db()
    db.execute('UPDATE users SET password = ? WHERE id = ?', (pwd_hash, user_id))
    db.commit()
    return jsonify({'code': 200, 'message': f'密码已重置为随机强密码：{new_password}（请告知用户后督促其修改）'})

@app.route('/api/users/<int:user_id>/change-password', methods=['POST'])
@token_required
def change_password(user_id):
    """用户修改自己的密码"""
    # 验证权限：只能修改自己的密码
    if g.current_user.get('user_id') != user_id:
        return jsonify({'code': 403, 'message': '无权限修改他人密码'}), 403
    
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'code': 400, 'message': '请输入旧密码和新密码'}), 400
    
    # 密码强度检查
    pwd_ok, pwd_msg = check_password_strength(new_password)
    if not pwd_ok:
        return jsonify({'code': 400, 'message': f'新密码不符合要求：{pwd_msg}'}), 400
    
    db = get_db()
    cursor = db.execute('SELECT password FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
    # 验证旧密码
    if not verify_password(old_password, user['password']):
        return jsonify({'code': 401, 'message': '旧密码错误'}), 401
    
    # 更新密码
    pwd_hash = hash_password(new_password)
    db.execute('UPDATE users SET password = ? WHERE id = ?', (pwd_hash, user_id))
    db.commit()
    
    return jsonify({'code': 200, 'message': '密码修改成功'})

@app.route('/api/users', methods=['POST'])
@token_required
def create_user():
    if g.current_user.get('role') not in (1, 'admin', '1'):
        return jsonify({'code': 403, 'message': '无权限'}), 403
    data = request.json
    if not data.get('username') or not data.get('password') or not data.get('name'):
        return jsonify({'code': 400, 'message': '缺少必填字段'}), 400
    # 密码强度检查
    pwd_ok, pwd_msg = check_password_strength(data['password'])
    if not pwd_ok:
        return jsonify({'code': 400, 'message': f'密码不符合要求：{pwd_msg}'}), 400
    db = get_db()
    cursor = db.execute('SELECT id FROM users WHERE username = ?', (data['username'],))
    if cursor.fetchone():
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400
    pwd_hash = hash_password(data['password'])
    role_map = {1: 'admin', 2: 'user'}
    role = role_map.get(data.get('role', 2), 'user')
    cursor = db.execute('INSERT INTO users (username, password, real_name, email, role, status) VALUES (?, ?, ?, ?, ?, ?)', (
        data['username'], pwd_hash, data['name'],
        data.get('email', ''), role,
        data.get('status', 1)
    ))
    db.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'id': cursor.lastrowid})

# ============== 角色管理API ==============

@app.route('/api/roles', methods=['GET'])
@token_required
def get_roles():
    if g.current_user.get('role') not in (1, 'admin', '1'):
        return jsonify({'code': 403, 'message': '无权限'}), 403
    db = get_db()
    cursor = db.execute('''
        SELECT r.id, r.role_name, r.display_name, r.description, r.permissions, r.is_system,
               (SELECT COUNT(*) FROM users WHERE role_id = r.id) as userCount
        FROM roles r ORDER BY r.id ASC
    ''')
    roles = []
    for row in cursor.fetchall():
        roles.append({
            'id': row['id'],
            'name': row['display_name'],
            'code': row['role_name'],
            'description': row['description'],
            'permissions': row['permissions'] or '*',
            'is_system': row['is_system'],
            'userCount': row['userCount'],
            'status': 1
        })
    return jsonify({'items': roles, 'total': len(roles)})

@app.route('/api/roles/<int:role_id>/permissions', methods=['PUT'])
@token_required
def update_role_permissions(role_id):
    if g.current_user.get('role') not in (1, 'admin', '1'):
        return jsonify({'code': 403, 'message': '无权限'}), 403
    data = request.json
    db = get_db()
    # 检查是否是系统角色
    cursor = db.execute('SELECT is_system FROM roles WHERE id = ?', (role_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'code': 404, 'message': '角色不存在'}), 404
    if row['is_system']:
        return jsonify({'code': 400, 'message': '系统角色不能修改权限'}), 400
    permissions = json.dumps(data.get('permissions', {}))
    db.execute('UPDATE roles SET permissions = ? WHERE id = ?', (permissions, role_id))
    db.commit()
    return jsonify({'code': 200, 'message': '权限更新成功'})

# ============== 客户API ==============

@app.route('/api/customers', methods=['GET'])
@token_required
def get_customers():
    db = get_db()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    keyword = request.args.get('keyword', '')
    type_filter = request.args.get('type', '')
    industry = request.args.get('industry', '')
    classification = request.args.get('classification', '')
    offset = (page - 1) * page_size

    where_clauses = []
    params = []
    if keyword:
        where_clauses.append('(name LIKE ? OR industry LIKE ?)')
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    if type_filter:
        where_clauses.append('type = ?')
        params.append(type_filter)
    if industry:
        where_clauses.append('industry = ?')
        params.append(industry)
    if classification:
        where_clauses.append('classification = ?')
        params.append(classification)

    where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'

    cursor = db.execute(f'SELECT COUNT(*) as total FROM customer_organizations WHERE {where_sql}', params)
    total = cursor.fetchone()['total']

    cursor = db.execute(f'''
        SELECT co.*,
               (SELECT COUNT(*) FROM contacts WHERE organization_id = co.id) as contact_count,
               (SELECT COUNT(*) FROM sales_opportunities WHERE organization_id = co.id) as opportunity_count,
               (SELECT COUNT(*) FROM contracts WHERE organization_id = co.id) as contract_count,
               (SELECT MAX(activity_date) FROM customer_activities WHERE organization_id = co.id) as last_followup_date
        FROM customer_organizations co
        WHERE {where_sql}
        ORDER BY co.updated_at DESC LIMIT ? OFFSET ?
    ''', params + [page_size, offset])
    items = row_to_dict(cursor.fetchall())
    return jsonify({'items': items, 'total': total, 'page': page, 'pageSize': page_size})

@app.route('/api/customers/<int:customer_id>', methods=['GET'])
@token_required
def get_customer(customer_id):
    db = get_db()
    cursor = db.execute('''
        SELECT co.*,
               (SELECT COUNT(*) FROM contacts WHERE organization_id = co.id) as contact_count,
               (SELECT COUNT(*) FROM sales_opportunities WHERE organization_id = co.id) as opportunity_count,
               (SELECT COUNT(*) FROM contracts WHERE organization_id = co.id) as contract_count,
               (SELECT MAX(activity_date) FROM customer_activities WHERE organization_id = co.id) as last_followup_date
        FROM customer_organizations co
        WHERE co.id = ?
    ''', (customer_id,))
    customer = cursor.fetchone()
    if not customer:
        return jsonify({'code': 404, 'message': '客户不存在'}), 404
    return jsonify(dict_from_row(customer))

@app.route('/api/customers', methods=['POST'])
@token_required
def create_customer():
    try:
        data = request.json
        print("DEBUG CREATE data:", data, type(data))
    except Exception as e:
        print("DEBUG JSON parse error:", e)
        return jsonify({'code': 400, 'message': '无效的JSON数据'}), 400
    
    if not data:
        return jsonify({'code': 400, 'message': '请求体为空'}), 400
    
    name = data.get('name')
    ctype = data.get('type')
    
    if not name or not ctype:
        return jsonify({'code': 400, 'message': '缺少必填字段'}), 400
    
    valid_scales = ['small', 'medium', 'large', 'enterprise', 'critical_infrastructure']
    scale_value = data.get('scale', 'medium')
    if scale_value not in valid_scales:
        scale_value = 'medium'
    
    try:
        db = get_db()
        cursor = db.execute('''
            INSERT INTO customer_organizations (name, type, industry, scale, address, phone, email, potential_score, classification, invoice_info, tax_number, bank_account, bank_name, invoice_address, invoice_phone, tags, created_by, notes, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name, ctype, data.get('industry', ''), scale_value,
            data.get('address', ''), data.get('phone', ''), data.get('email', ''),
            data.get('potential_score', 3), data.get('classification', 'normal'),
            data.get('invoice_info', ''), data.get('tax_number', ''), data.get('bank_account', ''),
            data.get('bank_name', ''), data.get('invoice_address', ''), data.get('invoice_phone', ''),
            json.dumps(data.get('tags', [])), g.current_user.get('name', 'admin'),
            data.get('notes', ''), data.get('description', '')
        ))
        db.commit()
        return jsonify({'code': 200, 'message': '创建成功', 'id': cursor.lastrowid})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'code': 500, 'message': '服务器错误'}), 500

@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
@token_required
def update_customer(customer_id):
    try:
        data = request.json
        if not data:
            return jsonify({'code': 400, 'message': '请求体为空'}), 400
        
        db = get_db()
        # 检查客户是否存在
        cursor = db.execute('SELECT id FROM customer_organizations WHERE id = ?', (customer_id,))
        if not cursor.fetchone():
            return jsonify({'code': 404, 'message': '客户不存在'}), 404
        
        # 构建更新语句
        fields = []
        values = []
        allowed_fields = ['name', 'type', 'industry', 'scale', 'address', 'phone', 'email', 
                         'potential_score', 'classification', 'invoice_info', 'tax_number',
                         'bank_account', 'bank_name', 'invoice_address', 'invoice_phone',
                         'tags', 'notes', 'description']
        
        for field in allowed_fields:
            if field in data:
                if field == 'tags':
                    fields.append(f"{field} = ?")
                    values.append(json.dumps(data[field]))
                else:
                    fields.append(f"{field} = ?")
                    values.append(data[field])
        
        if not fields:
            return jsonify({'code': 400, 'message': '没有需要更新的字段'}), 400
        
        values.append(customer_id)
        sql = f"UPDATE customer_organizations SET {', '.join(fields)} WHERE id = ?"
        db.execute(sql, values)
        db.commit()
        
        return jsonify({'code': 200, 'message': '更新成功'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'code': 500, 'message': '服务器错误'}), 500

@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
@token_required
def delete_customer(customer_id):
    try:
        db = get_db()
        # 检查客户是否存在
        cursor = db.execute('SELECT id FROM customer_organizations WHERE id = ?', (customer_id,))
        if not cursor.fetchone():
            return jsonify({'code': 404, 'message': '客户不存在'}), 404
        
        # 删除客户（级联删除会自动处理关联数据）
        db.execute('DELETE FROM customer_organizations WHERE id = ?', (customer_id,))
        db.commit()
        return jsonify({'code': 200, 'message': '删除成功'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'code': 500, 'message': '服务器错误'}), 500

@app.route('/api/customers/batch-delete', methods=['POST'])
@token_required
def batch_delete_customers():
    try:
        data = request.json
        if not data or 'ids' not in data:
            return jsonify({'code': 400, 'message': '缺少ids参数'}), 400
        
        ids = data.get('ids', [])
        if not ids:
            return jsonify({'code': 400, 'message': 'ids不能为空'}), 400
        
        db = get_db()
        placeholders = ','.join(['?'] * len(ids))
        db.execute(f'DELETE FROM customer_organizations WHERE id IN ({placeholders})', ids)
        db.commit()
        return jsonify({'code': 200, 'message': f'成功删除 {len(ids)} 个客户'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'code': 500, 'message': '服务器错误'}), 500

    if org_id:
        where_clauses.append('c.organization_id = ?')
        params.append(org_id)

    where_sql = ' AND '.join(where_clauses)
    cursor = db.execute(f'SELECT COUNT(*) as total FROM contacts c WHERE {where_sql}', params)
    total = cursor.fetchone()['total']

    cursor = db.execute(f'''
        SELECT c.*, co.name as org_name FROM contacts c
        LEFT JOIN customer_organizations co ON c.organization_id = co.id
        WHERE {where_sql} ORDER BY c.updated_at DESC LIMIT ? OFFSET ?
    ''', params + [page_size, offset])
    items = row_to_dict(cursor.fetchall())
    return jsonify({'items': items, 'total': total, 'page': page, 'pageSize': page_size})

@app.route('/api/contacts', methods=['GET'])
@token_required
def get_contacts():
    db = get_db()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    offset = (page - 1) * page_size
    keyword = request.args.get('keyword', '')
    org_id = request.args.get('org_id', type=int)
    
    where_clauses = []
    params = []
    
    if keyword:
        where_clauses.append('(c.name LIKE ? OR c.phone LIKE ? OR c.email LIKE ?)')
        params.extend([f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'])
    
    if org_id:
        where_clauses.append('c.organization_id = ?')
        params.append(org_id)
    
    where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'
    
    cursor = db.execute(f'SELECT COUNT(*) as total FROM contacts c WHERE {where_sql}', params)
    total = cursor.fetchone()['total']
    
    cursor = db.execute(f'''
        SELECT c.*, co.name as org_name FROM contacts c
        LEFT JOIN customer_organizations co ON c.organization_id = co.id
        WHERE {where_sql} ORDER BY c.updated_at DESC LIMIT ? OFFSET ?
    ''', params + [page_size, offset])
    items = [dict_from_row(row) for row in cursor.fetchall()]
    return jsonify({'items': items, 'total': total, 'page': page, 'pageSize': page_size})

@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
@token_required
def get_contact(contact_id):
    db = get_db()
    cursor = db.execute('SELECT c.*, co.name as org_name FROM contacts c LEFT JOIN customer_organizations co ON c.organization_id = co.id WHERE c.id = ?', (contact_id,))
    contact = cursor.fetchone()
    if not contact:
        return jsonify({'code': 404, 'message': '联系人不存在'}), 404
    return jsonify(dict_from_row(contact))

@app.route('/api/contacts', methods=['POST'])
@token_required
def create_contact():
    data = request.json
    if not data.get('name') or not (data.get('org_id') or data.get('organization_id')):
        return jsonify({'code': 400, 'message': '缺少必填字段'}), 400
    db = get_db()
    cursor = db.execute('''
        INSERT INTO contacts (organization_id, name, department, position, responsibility, phone, email, is_primary, is_alumni, major, tags, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('org_id') or data.get('organization_id'), data['name'], data.get('department', ''),
        data.get('position', ''), data.get('responsibility', ''),
        data.get('phone', ''), data.get('email', ''), data.get('is_primary', 0),
        data.get('is_alumni', 0), data.get('major', ''),
        json.dumps(data.get('tags', [])), data.get('notes', '')
    ))
    db.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'id': cursor.lastrowid})

@app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
@token_required
def update_contact(contact_id):
    data = request.json
    db = get_db()
    db.execute('UPDATE contacts SET name=?, organization_id=?, department=?, position=?, responsibility=?, phone=?, email=?, is_primary=?, is_alumni=?, major=?, tags=?, notes=? WHERE id=?',
        (data.get('name'), data.get('org_id') or data.get('organization_id'), data.get('department', ''),
         data.get('position', ''), data.get('responsibility', ''),
         data.get('phone', ''), data.get('email', ''),
         data.get('is_primary', 0), data.get('is_alumni', 0), data.get('major', ''),
         json.dumps(data.get('tags', [])), data.get('notes', ''), contact_id))
    db.commit()
    return jsonify({'code': 200, 'message': '更新成功'})

@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
@token_required
def delete_contact(contact_id):
    db = get_db()
    db.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
    db.commit()
    return jsonify({'code': 200, 'message': '删除成功'})

# ============== 商机API ==============

@app.route('/api/opportunities', methods=['GET'])
@token_required
def get_opportunities():
    db = get_db()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    keyword = request.args.get('keyword', '')
    stage = request.args.get('stage', '')
    priority = request.args.get('priority', '')
    forecast_category = request.args.get('forecast_category', '')
    org_id = request.args.get('org_id', type=int)
    offset = (page - 1) * page_size

    where_clauses = ['1=1']
    params = []
    if keyword:
        where_clauses.append('(opportunity_name LIKE ? OR description LIKE ?)')
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    if stage:
        where_clauses.append('stage = ?')
        params.append(stage)
    if priority:
        where_clauses.append('priority = ?')
        params.append(priority)
    if forecast_category:
        where_clauses.append('forecast_category = ?')
        params.append(forecast_category)
    if org_id:
        where_clauses.append('organization_id = ?')
        params.append(org_id)

    where_sql = ' AND '.join(where_clauses)
    cursor = db.execute(f'SELECT COUNT(*) as total FROM sales_opportunities WHERE {where_sql}', params)
    total = cursor.fetchone()['total']

    cursor = db.execute(f'''
        SELECT s.*, co.name as org_name FROM sales_opportunities s
        LEFT JOIN customer_organizations co ON s.organization_id = co.id
        WHERE {where_sql} ORDER BY s.updated_at DESC LIMIT ? OFFSET ?
    ''', params + [page_size, offset])
    items = row_to_dict(cursor.fetchall())
    return jsonify({'items': items, 'total': total, 'page': page, 'pageSize': page_size})

@app.route('/api/opportunities/<int:opp_id>', methods=['GET'])
@token_required
def get_opportunity(opp_id):
    db = get_db()
    cursor = db.execute('SELECT s.*, co.name as org_name FROM sales_opportunities s LEFT JOIN customer_organizations co ON s.organization_id = co.id WHERE s.id = ?', (opp_id,))
    opp = cursor.fetchone()
    if not opp:
        return jsonify({'code': 404, 'message': '商机不存在'}), 404
    
    result = dict_from_row(opp)
    
    # 获取关联的合同列表
    cursor = db.execute('''SELECT c.*, co.name as org_name FROM contracts c 
                           LEFT JOIN customer_organizations co ON c.organization_id = co.id
                           WHERE c.opportunity_id = ? ORDER BY c.created_at DESC''', (opp_id,))
    result['contracts'] = row_to_dict(cursor.fetchall())
    
    # 获取跟踪记录（该商机所属客户的活动）
    cursor = db.execute('''SELECT a.*, u.real_name as recorded_by_name FROM customer_activities a
                           LEFT JOIN users u ON a.recorded_by = u.username
                           WHERE a.opportunity_id = ? ORDER BY a.activity_date DESC''', (opp_id,))
    result['activities'] = row_to_dict(cursor.fetchall())
    
    return jsonify(result)

@app.route('/api/opportunities', methods=['POST'])
@token_required
def create_opportunity():
    data = request.json
    if not data.get('opportunity_name') or not data.get('organization_id'):
        return jsonify({'code': 400, 'message': '缺少必填字段'}), 400
    db = get_db()
    cursor = db.execute('''
        INSERT INTO sales_opportunities (organization_id, opportunity_name, source, stage, estimated_amount, estimated_close_date, probability, priority, assigned_to, description, requirements, forecast_category)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['organization_id'], data['opportunity_name'], data.get('source', ''),
        data.get('stage', 'business_driven'), data.get('estimated_amount', 0),
        data.get('estimated_close_date', ''), data.get('probability', 10),
        data.get('priority', 'medium'), g.current_user.get('name', 'admin'),
        data.get('description', ''), data.get('requirements', ''),
        data.get('forecast_category', '')
    ))
    db.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'id': cursor.lastrowid})

@app.route('/api/opportunities/<int:opp_id>', methods=['PUT'])
@token_required
def update_opportunity(opp_id):
    data = request.json
    db = get_db()
    
    # 获取更新前的旧数据
    cursor = db.execute('SELECT * FROM sales_opportunities WHERE id = ?', (opp_id,))
    old = cursor.fetchone()
    if not old:
        return jsonify({'code': 404, 'message': '商机不存在'}), 404
    
    # 需记录的字段及其中文名
    track_fields = {
        'opportunity_name': '商机名称',
        'stage': '采购阶段',
        'estimated_amount': '商机金额',
        'probability': '赢单概率',
        'priority': '优先级',
        'source': '商机来源',
        'estimated_close_date': '预计成交日期',
        'description': '描述',
        'requirements': '需求',
        'forecast_category': '预测类别'
    }
    
    # 阶段值映射
    stage_labels = {
        'business_driven': '①业务驱动、定位问题',
        'needs_defined': '②确定需求、启动项目',
        'evaluation': '③评估方案、圈定供应商',
        'procurement': '④制定规则、落实采购',
        'contract_signed': '⑤得到结果、签订合同',
        'payment_implementation': '⑥付款收货、实施评估',
        'closed_won': '赢单',
        'closed_lost': '输单'
    }
    
    # 执行更新
    db.execute('''UPDATE sales_opportunities SET opportunity_name=?, source=?, stage=?, estimated_amount=?, estimated_close_date=?, probability=?, priority=?, description=?, requirements=?, forecast_category=? WHERE id=?''',
        (data.get('opportunity_name'), data.get('source', ''), data.get('stage', 'business_driven'),
         data.get('estimated_amount', 0), data.get('estimated_close_date', ''),
         data.get('probability', 10), data.get('priority', 'medium'),
         data.get('description', ''), data.get('requirements', ''),
         data.get('forecast_category', ''), opp_id))
    db.commit()
    
    # 生成变更日志
    changes = []
    for field, label in track_fields.items():
        old_val = old[field] if old[field] is not None else ''
        new_val = data.get(field, '')
        if field == 'stage':
            old_val = stage_labels.get(str(old_val), str(old_val))
            new_val = stage_labels.get(str(new_val), str(new_val))
        elif field in ('estimated_amount', 'probability'):
            # 金额和概率做数值比较，避免格式差异产生误报
            try:
                if float(old_val) == float(new_val):
                    continue
            except (ValueError, TypeError):
                if str(old_val) == str(new_val):
                    continue
            old_val = f'¥{float(old_val):,.2f}' if old_val else '¥0.00'
            new_val = f'¥{float(new_val):,.2f}' if new_val else '¥0.00'
        if str(old_val) != str(new_val):
            changes.append(f'{label}: {old_val} → {new_val}')
    
    # 如果有变更，记录到操作日志
    if changes:
        current_user = g.current_user.get('name') or g.current_user.get('username', '未知')
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = db.execute('SELECT organization_id FROM sales_opportunities WHERE id = ?', (opp_id,))
        row = cursor.fetchone()
        org_id = row['organization_id'] if row else None
        
        db.execute('''INSERT INTO customer_activities 
            (organization_id, opportunity_id, activity_type, activity_date, title, description, recorded_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (org_id, opp_id, 'other', now, '商机修改', '\n'.join(changes), current_user))
        db.commit()
    
    return jsonify({'code': 200, 'message': '更新成功'})

@app.route('/api/opportunities/<int:opp_id>', methods=['DELETE'])
@token_required
def delete_opportunity(opp_id):
    db = get_db()
    db.execute('DELETE FROM sales_opportunities WHERE id = ?', (opp_id,))
    db.commit()
    return jsonify({'code': 200, 'message': '删除成功'})

@app.route('/api/opportunities/<int:opp_id>/stage', methods=['POST'])
@token_required
def update_opportunity_stage(opp_id):
    data = request.json
    new_stage = data.get('stage')
    db = get_db()
    
    stage_labels = {
        'business_driven': '①业务驱动、定位问题',
        'needs_defined': '②确定需求、启动项目',
        'evaluation': '③评估方案、圈定供应商',
        'procurement': '④制定规则、落实采购',
        'contract_signed': '⑤得到结果、签订合同',
        'payment_implementation': '⑥付款收货、实施评估',
        'closed_won': '赢单',
        'closed_lost': '输单'
    }
    
    # 获取旧阶段
    cursor = db.execute('SELECT stage, organization_id FROM sales_opportunities WHERE id = ?', (opp_id,))
    row = cursor.fetchone()
    old_stage = row['stage']
    org_id = row['organization_id']
    
    db.execute('UPDATE sales_opportunities SET stage=? WHERE id=?', (new_stage, opp_id))
    db.commit()
    
    # 记录变更
    if old_stage != new_stage:
        current_user = g.current_user.get('name') or g.current_user.get('username', '未知')
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        old_label = stage_labels.get(old_stage, old_stage)
        new_label = stage_labels.get(new_stage, new_stage)
        db.execute('''INSERT INTO customer_activities 
            (organization_id, opportunity_id, activity_type, activity_date, title, description, recorded_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (org_id, opp_id, 'other', now, '商机阶段变更', f'采购阶段: {old_label} → {new_label}', current_user))
        db.commit()
    
    return jsonify({'code': 200, 'message': '阶段更新成功'})

@app.route('/api/opportunities/<int:opp_id>/activities', methods=['GET'])
@token_required
def get_opportunity_activities(opp_id):
    db = get_db()
    cursor = db.execute('SELECT * FROM customer_activities WHERE opportunity_id = ? ORDER BY activity_date DESC', (opp_id,))
    return jsonify({'items': row_to_dict(cursor.fetchall())})

@app.route('/api/opportunities/<int:opp_id>/operation-logs', methods=['GET'])
@token_required
def get_opportunity_operation_logs(opp_id):
    """获取商机操作日志（字段变更记录）"""
    db = get_db()
    cursor = db.execute('''SELECT * FROM customer_activities 
                           WHERE opportunity_id = ? AND title IN ('商机修改', '商机阶段变更')
                           ORDER BY activity_date DESC''',
                           (opp_id,))
    return jsonify({'items': row_to_dict(cursor.fetchall())})

# ============== 合同API ==============

@app.route('/api/contracts', methods=['GET'])
@token_required
def get_contracts():
    db = get_db()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', '')
    org_id = request.args.get('org_id', type=int)
    offset = (page - 1) * page_size

    where_clauses = ['1=1']
    params = []
    if keyword:
        where_clauses.append('(contract_name LIKE ? OR contract_number LIKE ?)')
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    if status:
        where_clauses.append('status = ?')
        params.append(status)
    if org_id:
        where_clauses.append('organization_id = ?')
        params.append(org_id)

    where_sql = ' AND '.join(where_clauses)
    cursor = db.execute(f'SELECT COUNT(*) as total FROM contracts WHERE {where_sql}', params)
    total = cursor.fetchone()['total']

    # For SELECT query with JOIN, use table prefix for organization_id to avoid ambiguity
    select_where = where_sql.replace('organization_id =', 'c.organization_id =')
    cursor = db.execute(f'''
        SELECT c.*, co.name as org_name, s.opportunity_name as opportunity_name
        FROM contracts c
        LEFT JOIN customer_organizations co ON c.organization_id = co.id
        LEFT JOIN sales_opportunities s ON c.opportunity_id = s.id
        WHERE {select_where} ORDER BY c.updated_at DESC LIMIT ? OFFSET ?
    ''', params + [page_size, offset])
    items = row_to_dict(cursor.fetchall())
    return jsonify({'items': items, 'total': total, 'page': page, 'pageSize': page_size})

@app.route('/api/contracts/<int:contract_id>', methods=['GET'])
@app.route('/api/contracts/<int:contract_id>', methods=['GET'])
@token_required
def get_contract(contract_id):
    db = get_db()
    cursor = db.execute('SELECT c.*, co.name as org_name, s.opportunity_name, sup.name as supplier_name FROM contracts c LEFT JOIN customer_organizations co ON c.organization_id = co.id LEFT JOIN sales_opportunities s ON c.opportunity_id = s.id LEFT JOIN customer_organizations sup ON c.supplier_id = sup.id WHERE c.id = ?', (contract_id,))
    contract = cursor.fetchone()
    if not contract:
        return jsonify({'code': 404, 'message': '合同不存在'}), 404
    
    result = dict_from_row(contract)
    
    # 获取关联的发票列表
    cursor = db.execute('SELECT * FROM invoices WHERE contract_id = ? ORDER BY created_at DESC', (contract_id,))
    result['invoices'] = row_to_dict(cursor.fetchall())
    
    # 获取跟踪记录
    cursor = db.execute('''SELECT a.*, u.real_name as recorded_by_name FROM customer_activities a
                           LEFT JOIN users u ON a.recorded_by = u.username
                           WHERE a.contract_id = ? ORDER BY a.activity_date DESC''', (contract_id,))
    result['activities'] = row_to_dict(cursor.fetchall())
    
    # 获取付款条件
    cursor = db.execute('SELECT * FROM contract_payment_conditions WHERE contract_id = ? ORDER BY sort_order, id', (contract_id,))
    result['payment_conditions'] = row_to_dict(cursor.fetchall())
    
    # 获取货物内容
    cursor = db.execute('SELECT * FROM contract_goods_items WHERE contract_id = ? ORDER BY id', (contract_id,))
    result['goods_items'] = row_to_dict(cursor.fetchall())
    
    return jsonify(result)

# 合同货物内容API
@app.route('/api/contracts/<int:contract_id>/payment-conditions', methods=['GET'])
@token_required
def get_payment_conditions(contract_id):
    db = get_db()
    cursor = db.execute('SELECT * FROM contract_payment_conditions WHERE contract_id = ? ORDER BY sort_order, id', (contract_id,))
    items = row_to_dict(cursor.fetchall())
    return jsonify({'items': items, 'total': len(items)})

@app.route('/api/contracts/<int:contract_id>/payment-conditions', methods=['POST'])
@token_required
def create_payment_condition(contract_id):
    data = request.json
    db = get_db()
    cursor = db.execute('''
        INSERT INTO contract_payment_conditions (contract_id, name, payment_condition, payment_ratio, amount, notes, sort_order)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        contract_id, data.get('name', ''), data.get('payment_condition', ''),
        data.get('payment_ratio', 0), data.get('amount', 0), data.get('notes', ''),
        data.get('sort_order', 0)
    ))
    db.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'id': cursor.lastrowid})

@app.route('/api/contracts/payment-conditions/<int:pc_id>', methods=['PUT'])
@token_required
def update_payment_condition(pc_id):
    data = request.json
    db = get_db()
    db.execute('''
        UPDATE contract_payment_conditions SET name=?, payment_condition=?, payment_ratio=?, amount=?, notes=?, sort_order=?
        WHERE id=?
    ''', (
        data.get('name', ''), data.get('payment_condition', ''),
        data.get('payment_ratio', 0), data.get('amount', 0), data.get('notes', ''),
        data.get('sort_order', 0), pc_id
    ))
    db.commit()
    return jsonify({'code': 200, 'message': '更新成功'})

@app.route('/api/contracts/payment-conditions/<int:pc_id>', methods=['DELETE'])
@token_required
def delete_payment_condition(pc_id):
    db = get_db()
    db.execute('DELETE FROM contract_payment_conditions WHERE id = ?', (pc_id,))
    db.commit()
    return jsonify({'code': 200, 'message': '删除成功'})

# 合同货物内容 API
@app.route('/api/contracts/<int:contract_id>/goods-items', methods=['GET'])
@token_required
def get_goods_items(contract_id):
    db = get_db()
    cursor = db.execute('SELECT * FROM contract_goods_items WHERE contract_id = ? ORDER BY id', (contract_id,))
    items = row_to_dict(cursor.fetchall())
    return jsonify(items)

@app.route('/api/contracts/<int:contract_id>/goods-items', methods=['POST'])
@token_required
def create_goods_item(contract_id):
    data = request.json
    db = get_db()
    cursor = db.execute('''
        INSERT INTO contract_goods_items (contract_id, goods_name, brand, model, quantity, unit_price, subtotal, warranty_period)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        contract_id, data.get('goods_name', ''), data.get('brand', ''),
        data.get('model', ''), data.get('quantity', 1), data.get('unit_price', 0),
        data.get('subtotal', 0), data.get('warranty_period', '')
    ))
    db.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'id': cursor.lastrowid})

@app.route('/api/contracts/goods-items/<int:gi_id>', methods=['PUT'])
@token_required
def update_goods_item(gi_id):
    data = request.json
    db = get_db()
    db.execute('''
        UPDATE contract_goods_items SET goods_name=?, brand=?, model=?, quantity=?, unit_price=?, subtotal=?, warranty_period=?
        WHERE id=?
    ''', (
        data.get('goods_name', ''), data.get('brand', ''),
        data.get('model', ''), data.get('quantity', 1), data.get('unit_price', 0),
        data.get('subtotal', 0), data.get('warranty_period', ''), gi_id
    ))
    db.commit()
    return jsonify({'code': 200, 'message': '更新成功'})

@app.route('/api/contracts/goods-items/<int:gi_id>', methods=['DELETE'])
@token_required
def delete_goods_item(gi_id):
    db = get_db()
    db.execute('DELETE FROM contract_goods_items WHERE id = ?', (gi_id,))
    db.commit()
    return jsonify({'code': 200, 'message': '删除成功'})

@app.route('/api/contracts', methods=['POST'])
@token_required
def create_contract():
    data = request.json
    if not data.get('contract_number') or not data.get('contract_name') or not data.get('organization_id'):
        return jsonify({'code': 400, 'message': '缺少必填字段'}), 400
    db = get_db()
    cursor = db.execute('''
        INSERT INTO contracts (organization_id, opportunity_id, contract_number, contract_name, contract_amount, status, start_date, end_date, contract_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['organization_id'], data.get('opportunity_id'), data['contract_number'], data['contract_name'],
        data.get('contract_amount', 0), data.get('status', 'draft'),
        data.get('start_date', ''), data.get('end_date', ''), data.get('contract_type', '')
    ))
    db.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'id': cursor.lastrowid})

@app.route('/api/contracts/<int:contract_id>', methods=['PUT'])
@token_required
def update_contract(contract_id):
    data = request.json
    db = get_db()
    db.execute('''UPDATE contracts SET opportunity_id=?, supplier_id=?, contract_name=?, contract_amount=?, status=?, start_date=?, end_date=?, contract_type=?, signed_date=? WHERE id=?''',
        (data.get('opportunity_id'), data.get('supplier_id'), data.get('contract_name'), data.get('contract_amount', 0), data.get('status', 'draft'),
         data.get('start_date', ''), data.get('end_date', ''), data.get('contract_type', ''), data.get('signed_date', ''), contract_id))
    db.commit()
    return jsonify({'code': 200, 'message': '更新成功'})

@app.route('/api/contracts/<int:contract_id>', methods=['DELETE'])
@token_required
def delete_contract(contract_id):
    db = get_db()
    db.execute('DELETE FROM contracts WHERE id = ?', (contract_id,))
    db.commit()
    return jsonify({'code': 200, 'message': '删除成功'})

# ============== 仪表盘API ==============

@app.route('/api/dashboard', methods=['GET'])
@token_required
def get_dashboard():
    db = get_db()
    stats = {}

    cursor = db.execute('SELECT COUNT(*) as count FROM customer_organizations')
    stats['organizations'] = cursor.fetchone()['count']

    cursor = db.execute('SELECT COUNT(*) as count FROM contacts')
    stats['contacts'] = cursor.fetchone()['count']

    cursor = db.execute('SELECT COUNT(*) as count, COALESCE(SUM(estimated_amount), 0) as amount FROM sales_opportunities WHERE status = "active"')
    row = cursor.fetchone()
    stats['deals'] = row['count']
    stats['deal_amount'] = row['amount']

    cursor = db.execute('SELECT COUNT(*) as count, COALESCE(SUM(contract_amount), 0) as amount FROM contracts WHERE status IN ("active", "approved") AND contract_type = "销售合同"')
    row = cursor.fetchone()
    stats['sales_contracts'] = row['count']
    stats['sales_contract_amount'] = row['amount']

    cursor = db.execute('SELECT COUNT(*) as count, COALESCE(SUM(contract_amount), 0) as amount FROM contracts WHERE status IN ("active", "approved") AND contract_type = "采购合同"')
    row = cursor.fetchone()
    stats['purchase_contracts'] = row['count']
    stats['purchase_contract_amount'] = row['amount']

    stats['contracts'] = stats['sales_contracts'] + stats['purchase_contracts']
    stats['contract_amount'] = stats['sales_contract_amount'] + stats['purchase_contract_amount']

    cursor = db.execute('SELECT COUNT(*) as count FROM followups WHERE done = 0')
    stats['followup_count'] = cursor.fetchone()['count']

    # 商机阶段分布
    cursor = db.execute('SELECT stage, COUNT(*) as count, COALESCE(SUM(estimated_amount), 0) as amount FROM sales_opportunities WHERE status = "active" GROUP BY stage')
    deals_by_stage = row_to_dict(cursor.fetchall())

    # 待办列表
    cursor = db.execute('''SELECT f.*, co.name as org_name FROM followups f
        LEFT JOIN customer_organizations co ON f.organization_id = co.id
        WHERE f.done = 0 ORDER BY f.due_date ASC LIMIT 10''')
    upcoming_followups = row_to_dict(cursor.fetchall())

    # 近期活动
    cursor = db.execute('''SELECT a.*, co.name as org_name, c.name as contact_name FROM customer_activities a
        LEFT JOIN customer_organizations co ON a.organization_id = co.id
        LEFT JOIN contacts c ON a.contact_id = c.id
        ORDER BY a.activity_date DESC LIMIT 10''')
    recent_activities = row_to_dict(cursor.fetchall())

    # 漏斗数据
    funnel_data = [
        {'name': '①业务驱动、定位问题', 'value': 0},
        {'name': '②确定需求、启动项目', 'value': 0},
        {'name': '③评估方案、圈定供应商', 'value': 0},
        {'name': '④制定规则、落实采购', 'value': 0},
        {'name': '⑤得到结果、签订合同', 'value': 0},
        {'name': '赢单', 'value': 0}
    ]
    stage_map = {'business_driven': 0, 'needs_defined': 1, 'evaluation': 2, 'procurement': 3, 'contract_signed': 4, 'closed_won': 5}
    cursor = db.execute("SELECT stage, COUNT(*) as count FROM sales_opportunities WHERE status = 'active' GROUP BY stage")
    for row in cursor.fetchall():
        if row['stage'] in stage_map:
            funnel_data[stage_map[row['stage']]]['value'] = row['count']

    # 趋势数据
    trend_data = []
    now = datetime.now()
    for i in range(5, -1, -1):
        month = now.month - i
        year = now.year
        if month <= 0:
            month += 12
            year -= 1
        month_name = f"{year}-{month:02d}"
        cursor = db.execute("SELECT COUNT(*) as cnt FROM sales_opportunities WHERE strftime('%Y-%m', created_at) = ?", (month_name,))
        result = cursor.fetchone()
        trend_data.append({'date': f"{month}月", 'value': result['cnt'] if result else 0})

    return jsonify({
        'stats': stats,
        'deals_by_stage': deals_by_stage,
        'upcoming_followups': upcoming_followups,
        'recent_activities': recent_activities,
        'recent_insights': [],
        'funnel_data': funnel_data,
        'trend_data': trend_data
    })

# ============== 活动API ==============

@app.route('/api/activities', methods=['GET'])
@token_required
def get_activities():
    db = get_db()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    activity_type = request.args.get('type', '')
    offset = (page - 1) * page_size

    where_sql = '1=1'
    params = []
    if activity_type:
        where_sql += ' AND activity_type = ?'
        params.append(activity_type)
    if request.args.get('organization_id'):
        where_sql += ' AND organization_id = ?'
        params.append(request.args.get('organization_id', type=int))
    if request.args.get('contact_id'):
        where_sql += ' AND contact_id = ?'
        params.append(request.args.get('contact_id', type=int))
    if request.args.get('opportunity_id'):
        where_sql += ' AND opportunity_id = ?'
        params.append(request.args.get('opportunity_id', type=int))
    if request.args.get('contract_id'):
        where_sql += ' AND contract_id = ?'
        params.append(request.args.get('contract_id', type=int))
    if request.args.get('invoice_id'):
        where_sql += ' AND invoice_id = ?'
        params.append(request.args.get('invoice_id', type=int))

    cursor = db.execute(f'SELECT COUNT(*) as total FROM customer_activities WHERE {where_sql}', params)
    total = cursor.fetchone()['total']

    # For SELECT, use alias 'a' for customer_activities
    select_where = where_sql.replace('activity_type', 'a.activity_type').replace('organization_id', 'a.organization_id').replace('contact_id', 'a.contact_id').replace('opportunity_id', 'a.opportunity_id').replace('contract_id', 'a.contract_id').replace('invoice_id', 'a.invoice_id')
    cursor = db.execute(f'''
        SELECT a.*, co.name as org_name, c.name as contact_name FROM customer_activities a
        LEFT JOIN customer_organizations co ON a.organization_id = co.id
        LEFT JOIN contacts c ON a.contact_id = c.id
        WHERE {select_where} ORDER BY a.activity_date DESC LIMIT ? OFFSET ?
    ''', params + [page_size, offset])
    items = row_to_dict(cursor.fetchall())
    return jsonify({'items': items, 'total': total, 'page': page, 'pageSize': page_size})

@app.route('/api/activities', methods=['POST'])
@token_required
def create_activity():
    data = request.json
    if not data.get('activity_type') or not data.get('activity_date') or not data.get('title'):
        return jsonify({'code': 400, 'message': '缺少必填字段'}), 400
    db = get_db()
    # 如果没有传organization_id，自动从contact_id/invoice_id/contract_id获取
    if not data.get('organization_id'):
        if data.get('contact_id'):
            c = db.execute('SELECT organization_id FROM contacts WHERE id = ?', (data.get('contact_id'),)).fetchone()
            if c: data['organization_id'] = c['organization_id']
        elif data.get('invoice_id'):
            inv = db.execute('SELECT organization_id FROM invoices WHERE id = ?', (data.get('invoice_id'),)).fetchone()
            if inv: data['organization_id'] = inv['organization_id']
        elif data.get('contract_id'):
            con = db.execute('SELECT organization_id FROM contracts WHERE id = ?', (data.get('contract_id'),)).fetchone()
            if con: data['organization_id'] = con['organization_id']
        elif data.get('opportunity_id'):
            opp = db.execute('SELECT organization_id FROM sales_opportunities WHERE id = ?', (data.get('opportunity_id'),)).fetchone()
            if opp: data['organization_id'] = opp['organization_id']
    cursor = db.execute('''
        INSERT INTO customer_activities (organization_id, contact_id, opportunity_id, contract_id, invoice_id, activity_type, activity_date, title, description, recorded_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('organization_id'), data.get('contact_id'), data.get('opportunity_id'),
        data.get('contract_id'), data.get('invoice_id'),
        data['activity_type'], data['activity_date'], data['title'],
        data.get('description', ''), g.current_user.get('name', 'admin')
    ))
    db.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'id': cursor.lastrowid})

# ============== 跟进待办API ==============

@app.route('/api/followups', methods=['GET'])
@token_required
def get_followups():
    db = get_db()
    cursor = db.execute('''SELECT f.*, co.name as org_name FROM followups f
        LEFT JOIN customer_organizations co ON f.organization_id = co.id
        ORDER BY f.done ASC, f.due_date ASC''')
    items = row_to_dict(cursor.fetchall())
    return jsonify({'items': items, 'total': len(items)})

@app.route('/api/followups/<int:followup_id>', methods=['POST'])
@token_required
def update_followup(followup_id):
    data = request.json
    db = get_db()
    db.execute('UPDATE followups SET done=? WHERE id=?', (data.get('done', 0), followup_id))
    db.commit()
    return jsonify({'code': 200, 'message': '更新成功'})

@app.route('/api/followups', methods=['POST'])
@token_required
def create_followup():
    data = request.json
    db = get_db()
    cursor = db.execute('''
        INSERT INTO followups (organization_id, title, type, due_date, priority, created_by)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get('organization_id'), data['title'], data.get('type', '跟进'),
        data['due_date'], data.get('priority', 'medium'), g.current_user.get('name', 'admin')
    ))
    db.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'id': cursor.lastrowid})

# ============== 发票API ==============

@app.route('/api/invoices', methods=['GET'])
@token_required
def get_invoices():
    db = get_db()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', '')
    contract_id = request.args.get('contract_id', type=int)
    offset = (page - 1) * page_size

    where_clauses = ['1=1']
    params = []
    if keyword:
        where_clauses.append('(i.invoice_number LIKE ? OR c.contract_name LIKE ? OR o.name LIKE ?)')
        params.extend([f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'])
    if status:
        where_clauses.append('i.status = ?')
        params.append(status)
    if contract_id:
        where_clauses.append('i.contract_id = ?')
        params.append(contract_id)

    where_sql = ' AND '.join(where_clauses)
    cursor = db.execute(f'SELECT COUNT(*) as total FROM invoices i WHERE {where_sql}', params)
    total = cursor.fetchone()['total']

    cursor = db.execute(f'''
        SELECT i.*, o.name as org_name, c.contract_name, c.contract_number
        FROM invoices i
        LEFT JOIN customer_organizations o ON i.organization_id = o.id
        LEFT JOIN contracts c ON i.contract_id = c.id
        WHERE {where_sql}
        ORDER BY i.created_at DESC LIMIT ? OFFSET ?
    ''', params + [page_size, offset])
    items = row_to_dict(cursor.fetchall())
    return jsonify({'items': items, 'total': total, 'page': page, 'pageSize': page_size})

@app.route('/api/invoices/<int:invoice_id>', methods=['GET'])
@token_required
def get_invoice(invoice_id):
    db = get_db()
    cursor = db.execute('''
        SELECT i.*, o.name as org_name, c.contract_name, c.contract_number
        FROM invoices i
        LEFT JOIN customer_organizations o ON i.organization_id = o.id
        LEFT JOIN contracts c ON i.contract_id = c.id
        WHERE i.id = ?
    ''', (invoice_id,))
    invoice = cursor.fetchone()
    if not invoice:
        return jsonify({'code': 404, 'message': '发票不存在'}), 404
    return jsonify(dict_from_row(invoice))

@app.route('/api/invoices', methods=['POST'])
@token_required
def create_invoice():
    data = request.json
    if not data.get('invoice_number') or not data.get('organization_id'):
        return jsonify({'code': 400, 'message': '缺少必填字段'}), 400
    
    db = get_db()
    total_amount = data.get('total_amount', 0)
    
    cursor = db.execute('''
        INSERT INTO invoices (invoice_number, contract_id, organization_id, invoice_type, amount, tax_rate, tax_amount, total_amount, billing_date, due_date, status, payment_status, paid_amount, notes, created_by, invoice_title, tax_number, bank_name, bank_account, invoice_address, invoice_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['invoice_number'], data.get('contract_id'), data['organization_id'],
        data.get('invoice_type', '增值税发票'), data.get('amount', 0), data.get('tax_rate', 0), data.get('tax_amount', 0), total_amount,
        data.get('billing_date', ''), data.get('due_date', ''),
        data.get('status', 'draft'), data.get('payment_status', 'unpaid'),
        data.get('paid_amount', 0), data.get('notes', ''),
        g.current_user.get('name', 'admin'),
        data.get('invoice_title', ''), data.get('tax_number', ''), data.get('bank_name', ''),
        data.get('bank_account', ''), data.get('invoice_address', ''), data.get('invoice_phone', '')
    ))
    db.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'id': cursor.lastrowid})

@app.route('/api/invoices/<int:invoice_id>', methods=['PUT'])
@token_required
def update_invoice(invoice_id):
    data = request.json
    db = get_db()
    total_amount = data.get('total_amount', 0)
    
    # 获取更新前的旧数据
    cursor = db.execute('SELECT * FROM invoices WHERE id = ?', (invoice_id,))
    old = cursor.fetchone()
    if not old:
        return jsonify({'code': 404, 'message': '发票不存在'}), 404
    
    track_fields = {
        'invoice_number': '发票号码',
        'invoice_type': '发票类型',
        'amount': '金额',
        'tax_rate': '税率',
        'tax_amount': '税额',
        'total_amount': '价税合计',
        'billing_date': '开票日期',
        'due_date': '到期日期',
        'status': '状态',
        'payment_status': '付款状态',
        'paid_amount': '已付金额',
        'notes': '备注',
        'invoice_title': '发票抬头',
        'tax_number': '税号',
        'bank_name': '开户银行',
        'bank_account': '银行账号'
    }
    
    status_labels = {'draft': '草稿', 'issued': '已开具', 'verified': '已认证', 'cancelled': '已作废'}
    payment_labels = {'unpaid': '未付款', 'partial': '部分付款', 'paid': '已付清'}
    
    db.execute('''
        UPDATE invoices SET invoice_number=?, contract_id=?, invoice_type=?, amount=?, tax_rate=?, tax_amount=?, total_amount=?, billing_date=?, due_date=?, status=?, payment_status=?, paid_amount=?, notes=?, invoice_title=?, tax_number=?, bank_name=?, bank_account=?, invoice_address=?, invoice_phone=? WHERE id=?
    ''', (
        data.get('invoice_number'), data.get('contract_id'),
        data.get('invoice_type', '增值税发票'), data.get('amount', 0), data.get('tax_rate', 0), data.get('tax_amount', 0), total_amount,
        data.get('billing_date', ''), data.get('due_date', ''),
        data.get('status', 'draft'), data.get('payment_status', 'unpaid'),
        data.get('paid_amount', 0), data.get('notes', ''),
        data.get('invoice_title', ''), data.get('tax_number', ''), data.get('bank_name', ''),
        data.get('bank_account', ''), data.get('invoice_address', ''), data.get('invoice_phone', ''),
        invoice_id
    ))
    db.commit()
    
    # 生成变更日志
    changes = []
    for field, label in track_fields.items():
        old_val = old[field] if old[field] is not None else ''
        new_val = data.get(field, '')
        if field in ('amount', 'tax_amount', 'total_amount', 'paid_amount'):
            try:
                if float(old_val or 0) == float(new_val or 0):
                    continue
            except (ValueError, TypeError):
                if str(old_val) == str(new_val):
                    continue
            old_val = f'¥{float(old_val or 0):,.2f}'
            new_val = f'¥{float(new_val or 0):,.2f}'
        elif field in ('status',):
            old_val = status_labels.get(str(old_val), str(old_val))
            new_val = status_labels.get(str(new_val), str(new_val))
        elif field in ('payment_status',):
            old_val = payment_labels.get(str(old_val), str(old_val))
            new_val = payment_labels.get(str(new_val), str(new_val))
        if str(old_val) != str(new_val):
            changes.append(f'{label}: {old_val} → {new_val}')
    
    if changes:
        current_user = g.current_user.get('name') or g.current_user.get('username', '未知')
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute('''INSERT INTO customer_activities 
            (organization_id, activity_type, activity_date, title, description, recorded_by)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (old['organization_id'], 'other', now, '发票修改', '\n'.join(changes), current_user))
        db.commit()
    
    return jsonify({'code': 200, 'message': '更新成功'})

@app.route('/api/invoices/<int:invoice_id>', methods=['DELETE'])
@token_required
def delete_invoice(invoice_id):
    db = get_db()
    db.execute('DELETE FROM invoices WHERE id = ?', (invoice_id,))
    db.commit()
    return jsonify({'code': 200, 'message': '删除成功'})

@app.route('/api/invoices/<int:invoice_id>/operation-logs', methods=['GET'])
@token_required
def get_invoice_operation_logs(invoice_id):
    """获取发票操作日志"""
    db = get_db()
    cursor = db.execute('''SELECT * FROM customer_activities
                           WHERE title = '发票修改' AND organization_id = (SELECT organization_id FROM invoices WHERE id = ?)
                           ORDER BY activity_date DESC''',
                           (invoice_id,))
    return jsonify({'items': row_to_dict(cursor.fetchall())})

# ============== 发票明细API ==============

@app.route('/api/invoices/<int:invoice_id>/items', methods=['GET'])
@token_required
def get_invoice_items(invoice_id):
    db = get_db()
    cursor = db.execute('SELECT * FROM invoice_items WHERE invoice_id = ? ORDER BY id ASC', (invoice_id,))
    items = row_to_dict(cursor.fetchall())
    return jsonify({'items': items, 'total': len(items)})

@app.route('/api/invoices/<int:invoice_id>/items', methods=['POST'])
@token_required
def create_invoice_item(invoice_id):
    data = request.json
    if not data.get('item_name'):
        return jsonify({'code': 400, 'message': '请填写项目名称'}), 400
    db = get_db()
    quantity = data.get('quantity', 1)
    unit_price = data.get('unit_price', 0)
    tax_rate = data.get('tax_rate', 0.13)
    amount = data.get('amount', 0)
    tax_amount = data.get('tax_amount', 0)
    tax_included_amount = data.get('tax_included_amount', amount + tax_amount)
    cursor = db.execute('''
        INSERT INTO invoice_items (invoice_id, item_name, spec_model, unit, quantity, unit_price, amount, tax_rate, tax_amount, tax_included_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (invoice_id, data['item_name'], data.get('spec_model', ''), data.get('unit', ''), quantity, unit_price, amount, tax_rate, tax_amount, tax_included_amount))
    db.commit()
    return jsonify({'code': 200, 'message': '添加成功', 'id': cursor.lastrowid})

@app.route('/api/invoices/items/<int:item_id>', methods=['PUT'])
@token_required
def update_invoice_item(item_id):
    data = request.json
    db = get_db()
    quantity = data.get('quantity', 1)
    unit_price = data.get('unit_price', 0)
    tax_rate = data.get('tax_rate', 0.13)
    amount = data.get('amount', 0)
    tax_amount = data.get('tax_amount', 0)
    tax_included_amount = data.get('tax_included_amount', amount + tax_amount)
    db.execute('''
        UPDATE invoice_items SET item_name=?, spec_model=?, unit=?, quantity=?, unit_price=?, amount=?, tax_rate=?, tax_amount=?, tax_included_amount=? WHERE id=?
    ''', (data.get('item_name'), data.get('spec_model', ''), data.get('unit', ''), quantity, unit_price, amount, tax_rate, tax_amount, tax_included_amount, item_id))
    db.commit()
    return jsonify({'code': 200, 'message': '更新成功'})

@app.route('/api/invoices/items/<int:item_id>', methods=['DELETE'])
@token_required
def delete_invoice_item(item_id):
    db = get_db()
    db.execute('DELETE FROM invoice_items WHERE id = ?', (item_id,))
    db.commit()
    return jsonify({'code': 200, 'message': '删除成功'})

# 获取合同下的发票列表
@app.route('/api/contracts/<int:contract_id>/invoices', methods=['GET'])
@token_required
def get_contract_invoices(contract_id):
    db = get_db()
    cursor = db.execute('SELECT * FROM invoices WHERE contract_id = ? ORDER BY created_at DESC', (contract_id,))
    items = row_to_dict(cursor.fetchall())
    return jsonify({'items': items, 'total': len(items)})

# ============== 静态文件服务 ==============

DIST_FOLDER = os.path.join(os.path.dirname(__file__), '../dist')

@app.route('/')
def serve_index():
    return send_from_directory(DIST_FOLDER, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    file = os.path.join(DIST_FOLDER, path)
    if os.path.isfile(file):
        return send_from_directory(DIST_FOLDER, path)
    return send_from_directory(DIST_FOLDER, 'index.html')

# ============== 启动 ==============

@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

if __name__ == '__main__':
    with app.app_context():
        init_database()
    print("CRM API Server starting on http://localhost:5000")
    print("Admin login: admin / admin123")
    print("Demo login: hanxiaoc / demo123")
    app.run(host='0.0.0.0', port=5000, debug=False)
