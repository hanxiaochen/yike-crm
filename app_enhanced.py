#!/usr/bin/env python3
"""
差异化CRM系统 - 针对网络安全公司优化
版本：2.1
包含：产品使用跟踪、安全日志、AI洞察、自动化工作流、系统集成、用户管理、角色管理
"""

import os
import sqlite3
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, g, render_template, redirect
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'crm_enhanced.db')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['API_KEY'] = os.environ.get('CRM_API_KEY', 'default-api-key-change-in-production')

# ==================== Token 存储（内存） ====================
tokens = {}  # token -> {user_id, username, role_id, role_name, real_name, created_at}

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

# ==================== 认证中间件 ====================

def no_auth(f):
    """无需认证的装饰器"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper

def login_required(f):
    """需要登录的装饰器"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token or token not in tokens:
            return jsonify({'error': '未登录或会话已过期'}), 401
        # 检查token是否过期（24小时）
        token_data = tokens[token]
        if datetime.utcnow() - token_data['created_at'] > timedelta(hours=24):
            del tokens[token]
            return jsonify({'error': '会话已过期，请重新登录'}), 401
        # 获取用户信息
        db = get_db()
        cursor = db.execute('SELECT * FROM users WHERE id=?', (token_data['user_id'],))
        user = cursor.fetchone()
        if not user or not user['status']:
            del tokens[token]
            return jsonify({'error': '用户已被禁用'}), 401
        # 获取角色信息
        cursor = db.execute('SELECT * FROM roles WHERE id=?', (user['role_id'],))
        role = cursor.fetchone()
        g.current_user = user
        g.current_role = role
        g.token = token
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    """需要管理员权限"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not hasattr(g, 'current_role') or not g.current_role:
            return jsonify({'error': '无权限'}), 403
        perms = json.loads(g.current_role['permissions']) if g.current_role['permissions'] else {}
        if not perms.get('users', {}).get('view'):
            return jsonify({'error': '无权限访问用户管理'}), 403
        return f(*args, **kwargs)
    return wrapper

def check_permission(module, action='view'):
    """检查当前用户是否有指定模块的权限"""
    if not hasattr(g, 'current_role') or not g.current_role:
        return False
    perms = json.loads(g.current_role['permissions']) if g.current_role['permissions'] else {}
    return perms.get(module, {}).get(action, False)

# ==================== 日志 ====================

def log_security_event(log_type, action_description, resource_type=None, resource_id=None, severity='info'):
    """记录安全事件"""
    db = get_db()
    ip_address = request.remote_addr if request else 'unknown'
    user_agent = request.headers.get('User-Agent', 'unknown') if request else 'unknown'
    user_id = 'system'
    if hasattr(g, 'current_user'):
        user_id = g.current_user['username']
    db.execute('''
        INSERT INTO security_logs 
        (log_type, event_time, user_id, action_description, resource_type, resource_id, 
         ip_address, user_agent, severity, details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        log_type, datetime.now().isoformat(), user_id, action_description,
        resource_type, resource_id, ip_address, user_agent, severity,
        json.dumps({'method': request.method if request else 'none', 'path': request.path if request else 'none'})
    ))
    db.commit()

# ==================== 认证API ====================

@app.route('/api/auth/login', methods=['POST'])
@no_auth
def login():
    """用户登录"""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': '请输入用户名和密码'}), 400
    
    db = get_db()
    cursor = db.execute('SELECT u.*, r.role_name, r.display_name as role_display_name FROM users u LEFT JOIN roles r ON CAST(u.role_id AS INTEGER) = r.id WHERE u.username=?', (data['username'],))
    user = cursor.fetchone()
    
    if not user:
        return jsonify({'error': '用户名或密码错误'}), 401
    
    if not user['status']:
        return jsonify({'error': '账户已被禁用，请联系管理员'}), 401
    
    if not check_password_hash(user['password_hash'], data['password']):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # 生成token
    token = str(uuid.uuid4())
    tokens[token] = {
        'user_id': user['id'],
        'username': user['username'],
        'role_id': user['role_id'],
        'role_name': user['role_display_name'] or user['role_name'],
        'real_name': user['real_name'],
        'created_at': datetime.utcnow()
    }
    
    # 更新最后登录时间
    db.execute('UPDATE users SET last_login=CURRENT_TIMESTAMP WHERE id=?', (user['id'],))
    db.commit()
    
    log_security_event('access', f'用户登录: {user["username"]}')
    
    # 明确使用 role_display_name (从 roles 表 JOIN 来的) 而不是 users 表的 role_name
    final_role_name = user['role_display_name'] if user['role_display_name'] else user['role_name']
    print(f"DEBUG login: role_display_name={user['role_display_name']!r}, role_name={user['role_name']!r}, final={final_role_name!r}")
    
    return jsonify({
        'code': 200,
        'token': token,
        'userInfo': {
            'id': user['id'],
            'username': user['username'],
            'real_name': user['real_name'],
            'name': user['real_name'],
            'role': user['role'] if user['role'] else 'admin',
            'roleName': final_role_name,
            'email': user['email'] or ''
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """用户登出"""
    token = g.token
    if token in tokens:
        del tokens[token]
    return jsonify({'message': '已登出'})

@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_me():
    """获取当前用户信息"""
    user = g.current_user
    role = g.current_role
    perms = json.loads(role['permissions']) if role and role['permissions'] else {}
    return jsonify({
        'id': user['id'],
        'username': user['username'],
        'real_name': user['real_name'],
        'phone': user['phone'],
        'email': user['email'],
        'role_name': role['display_name'] if role else '',
        'role_key': role['role_name'] if role else '',
        'permissions': perms
    })

@app.route('/api/auth/password', methods=['PUT'])
@login_required
def change_password():
    """修改密码"""
    data = request.get_json()
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': '请输入旧密码和新密码'}), 400
    if len(data['new_password']) < 6:
        return jsonify({'error': '新密码长度至少6位'}), 400
    
    user = g.current_user
    if not check_password_hash(user['password_hash'], data['old_password']):
        return jsonify({'error': '旧密码错误'}), 400
    
    db = get_db()
    db.execute('UPDATE users SET password_hash=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
               (generate_password_hash(data['new_password']), user['id']))
    db.commit()
    
    log_security_event('modification', f'用户修改密码: {user["username"]}')
    return jsonify({'message': '密码修改成功'})

# ==================== 用户管理API ====================

@app.route('/api/users', methods=['GET'])
@login_required
@admin_required
def list_users():
    """用户列表"""
    db = get_db()
    cursor = db.execute('''SELECT u.*, r.role_name, r.display_name as role_display_name 
        FROM users u LEFT JOIN roles r ON CAST(u.role_id AS INTEGER) = r.id ORDER BY u.id''')
    users = [dict_from_row(r) for r in cursor.fetchall()]
    # 去掉password_hash
    for u in users:
        u.pop('password_hash', None)
    return jsonify(users)

@app.route('/api/users/<int:uid>/detail', methods=['GET'])
@login_required
@admin_required
def user_detail(uid):
    """用户详情"""
    db = get_db()
    cursor = db.execute('''SELECT u.*, r.role_name, r.display_name as role_display_name 
        FROM users u LEFT JOIN roles r ON CAST(u.role_id AS INTEGER) = r.id WHERE u.id=?''', (uid,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': '未找到'}), 404
    user = dict_from_row(row)
    user.pop('password_hash', None)
    return jsonify(user)

@app.route('/api/users', methods=['POST'])
@login_required
@admin_required
def create_user():
    """新增用户"""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': '用户名和密码不能为空'}), 400
    if len(data['password']) < 6:
        return jsonify({'error': '密码长度至少6位'}), 400
    
    db = get_db()
    # 检查用户名是否已存在
    cursor = db.execute('SELECT id FROM users WHERE username=?', (data['username'],))
    if cursor.fetchone():
        return jsonify({'error': '用户名已存在'}), 400
    
    try:
        cursor = db.execute('''INSERT INTO users (username, password_hash, real_name, phone, email, role_id, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', (
            data['username'],
            generate_password_hash(data['password']),
            data.get('real_name', ''),
            data.get('phone', ''),
            data.get('email', ''),
            data.get('role_id'),
            data.get('is_active', True) if data.get('is_active') is not None else True
        ))
        db.commit()
        log_security_event('modification', f'新增用户: {data["username"]}', 'users', cursor.lastrowid)
        return jsonify({'id': cursor.lastrowid, 'message': '创建成功'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:uid>', methods=['PUT'])
@login_required
@admin_required
def update_user(uid):
    """编辑用户"""
    data = request.get_json()
    db = get_db()
    fields = ['real_name', 'phone', 'email', 'role_id']
    sets = []
    vals = []
    for f in fields:
        if f in data:
            sets.append(f'{f}=?')
            vals.append(data[f])
    if data.get('is_active') is not None:
        sets.append('is_active=?')
        vals.append(1 if data['is_active'] else 0)
    if not sets:
        return jsonify({'error': '没有要更新的字段'}), 400
    sets.append("updated_at=CURRENT_TIMESTAMP")
    vals.append(uid)
    db.execute(f"UPDATE users SET {','.join(sets)} WHERE id=?", vals)
    db.commit()
    log_security_event('modification', f'编辑用户: id={uid}', 'users', uid)
    return jsonify({'message': '更新成功'})

@app.route('/api/users/<int:uid>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(uid):
    """删除用户"""
    if g.current_user['id'] == uid:
        return jsonify({'error': '不能删除自己'}), 400
    
    db = get_db()
    cursor = db.execute('SELECT * FROM users WHERE id=?', (uid,))
    user = cursor.fetchone()
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    db.execute('DELETE FROM users WHERE id=?', (uid,))
    db.commit()
    log_security_event('deletion', f'删除用户: {user["username"]}', 'users', uid)
    return jsonify({'message': '删除成功'})

@app.route('/api/users/<int:uid>/reset-password', methods=['PUT'])
@login_required
@admin_required
def reset_password(uid):
    """重置密码"""
    data = request.get_json()
    new_pwd = data.get('password', '') if data else ''
    if not new_pwd:
        new_pwd = '123456'  # 默认密码
    if len(new_pwd) < 6:
        return jsonify({'error': '密码长度至少6位'}), 400
    
    db = get_db()
    db.execute('UPDATE users SET password_hash=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
               (generate_password_hash(new_pwd), uid))
    db.commit()
    log_security_event('modification', f'重置用户密码: id={uid}', 'users', uid)
    return jsonify({'message': f'密码已重置为: {new_pwd}'})

@app.route('/api/users/<int:uid>/toggle-active', methods=['PUT'])
@login_required
@admin_required
def toggle_user_active(uid):
    """启用/禁用用户"""
    if g.current_user['id'] == uid:
        return jsonify({'error': '不能禁用自己'}), 400
    db = get_db()
    db.execute('UPDATE users SET is_active = CASE WHEN is_active=1 THEN 0 ELSE 1 END, updated_at=CURRENT_TIMESTAMP WHERE id=?', (uid,))
    db.commit()
    log_security_event('modification', f'切换用户状态: id={uid}', 'users', uid)
    return jsonify({'message': '操作成功'})

# ==================== 角色管理API ====================

@app.route('/api/roles', methods=['GET'])
@login_required
@admin_required
def list_roles():
    """角色列表"""
    db = get_db()
    cursor = db.execute('SELECT * FROM roles ORDER BY id')
    roles = []
    for r in cursor.fetchall():
        role = dict_from_row(r)
        perms = json.loads(role['permissions']) if role['permissions'] else {}
        # 计算权限数量
        count = 0
        for mod, actions in perms.items():
            count += sum(1 for v in actions.values() if v)
        role['permission_count'] = count
        roles.append(role)
    return jsonify(roles)

@app.route('/api/roles/<int:rid>/detail', methods=['GET'])
@login_required
@admin_required
def role_detail(rid):
    """角色详情"""
    db = get_db()
    cursor = db.execute('SELECT * FROM roles WHERE id=?', (rid,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': '未找到'}), 404
    role = dict_from_row(row)
    perms = json.loads(role['permissions']) if role['permissions'] else {}
    role['permissions_parsed'] = perms
    return jsonify(role)

@app.route('/api/roles', methods=['POST'])
@login_required
@admin_required
def create_role():
    """新增角色"""
    data = request.get_json()
    if not data or not data.get('role_name') or not data.get('display_name'):
        return jsonify({'error': '角色名称和显示名称不能为空'}), 400
    
    db = get_db()
    cursor = db.execute('SELECT id FROM roles WHERE role_name=?', (data['role_name'],))
    if cursor.fetchone():
        return jsonify({'error': '角色标识已存在'}), 400
    
    try:
        cursor = db.execute('''INSERT INTO roles (role_name, display_name, description, permissions, is_system)
            VALUES (?, ?, ?, ?, ?)''', (
            data['role_name'],
            data['display_name'],
            data.get('description', ''),
            json.dumps(data.get('permissions', {})),
            data.get('is_system', False)
        ))
        db.commit()
        return jsonify({'id': cursor.lastrowid, 'message': '创建成功'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/roles/<int:rid>', methods=['PUT'])
@login_required
@admin_required
def update_role(rid):
    """编辑角色"""
    data = request.get_json()
    db = get_db()
    cursor = db.execute('SELECT * FROM roles WHERE id=?', (rid,))
    role = cursor.fetchone()
    if not role:
        return jsonify({'error': '角色不存在'}), 404
    
    sets = []
    vals = []
    if 'display_name' in data:
        sets.append('display_name=?')
        vals.append(data['display_name'])
    if 'description' in data:
        sets.append('description=?')
        vals.append(data['description'])
    if 'permissions' in data:
        sets.append('permissions=?')
        vals.append(json.dumps(data['permissions']))
    if not sets:
        return jsonify({'error': '没有要更新的字段'}), 400
    vals.append(rid)
    db.execute(f"UPDATE roles SET {','.join(sets)} WHERE id=?", vals)
    db.commit()
    log_security_event('modification', f'编辑角色: id={rid}', 'roles', rid)
    return jsonify({'message': '更新成功'})

@app.route('/api/roles/<int:rid>', methods=['DELETE'])
@login_required
@admin_required
def delete_role(rid):
    """删除角色"""
    db = get_db()
    cursor = db.execute('SELECT * FROM roles WHERE id=?', (rid,))
    role = cursor.fetchone()
    if not role:
        return jsonify({'error': '角色不存在'}), 404
    if role['is_system']:
        return jsonify({'error': '系统内置角色不可删除'}), 400
    
    # 检查是否有用户使用该角色
    cursor = db.execute('SELECT COUNT(*) as cnt FROM users WHERE role_id=?', (rid,))
    if cursor.fetchone()['cnt'] > 0:
        return jsonify({'error': '该角色下还有用户，请先迁移用户'}), 400
    
    db.execute('DELETE FROM roles WHERE id=?', (rid,))
    db.commit()
    log_security_event('deletion', f'删除角色: {role["role_name"]}', 'roles', rid)
    return jsonify({'message': '删除成功'})

# ==================== CRM核心管理API（需登录）====================

@app.route('/api/organizations', methods=['GET'])
@login_required
def list_organizations():
    """获取客户单位列表"""
    db = get_db()
    org_id = request.args.get('organization_id')
    if org_id:
        cursor = db.execute('SELECT * FROM customer_organizations WHERE id=?', (org_id,))
        row = cursor.fetchone()
        return jsonify(dict_from_row(row)) if row else jsonify({'error': '未找到'}), 404
    cursor = db.execute('SELECT * FROM customer_organizations ORDER BY id')
    return jsonify([dict_from_row(r) for r in cursor.fetchall()])

@app.route('/api/organizations', methods=['POST'])
@login_required
def create_organization():
    """创建客户单位"""
    data = request.get_json()
    db = get_db()
    try:
        cursor = db.execute('''INSERT INTO customer_organizations 
            (name,type,industry,scale,security_level,address,phone,email,created_by,notes,tags)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (
            data['name'], data.get('type','final_customer'), data.get('industry'), data.get('scale'),
            data.get('security_level','standard'), data.get('address'), data.get('phone'),
            data.get('email'), data.get('created_by','韩晓晨'), data.get('notes'),
            json.dumps(data.get('tags',[])) if data.get('tags') else None))
        db.commit()
        log_security_event('modification', f'创建客户单位: {data["name"]}', 'customer_organizations', cursor.lastrowid)
        return jsonify({'id': cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizations/<int:oid>', methods=['PUT'])
@login_required
def update_organization(oid):
    """更新客户单位"""
    data = request.get_json()
    db = get_db()
    fields = ['name','type','industry','scale','security_level','address','phone','email','notes','tags',
              'using_netshield','netshield_version','netshield_license_expiry',
              'using_inoc','inoc_modules','inoc_license_expiry',
              'potential_score','health_score','risk_level','classification']
    sets = []
    vals = []
    for f in fields:
        if f in data:
            sets.append(f'{f}=?')
            if f in ('tags','inoc_modules'):
                vals.append(json.dumps(data[f]) if data[f] else None)
            else:
                vals.append(data[f])
    if not sets:
        return jsonify({'error': '没有要更新的字段'}), 400
    sets.append("updated_at=CURRENT_TIMESTAMP")
    vals.append(oid)
    db.execute(f"UPDATE customer_organizations SET {','.join(sets)} WHERE id=?", vals)
    db.commit()
    return jsonify({'message': '更新成功'})

@app.route('/api/organizations/<int:oid>/detail', methods=['GET'])
@login_required
def organization_detail(oid):
    """客户详情（含关联数据）"""
    db = get_db()
    cursor = db.execute('SELECT * FROM customer_organizations WHERE id=?', (oid,))
    org = dict_from_row(cursor.fetchone())
    if not org:
        return jsonify({'error': '未找到'}), 404
    cursor = db.execute('SELECT c.*, co.name as org_name FROM contacts c LEFT JOIN customer_organizations co ON c.organization_id=co.id WHERE c.organization_id=? ORDER BY c.id', (oid,))
    org['contacts'] = [dict_from_row(r) for r in cursor.fetchall()]
    cursor = db.execute('SELECT d.*, co.name as org_name, c.name as contact_name FROM deals d LEFT JOIN customer_organizations co ON d.organization_id=co.id LEFT JOIN contacts c ON d.contact_id=c.id WHERE d.organization_id=? ORDER BY d.id DESC', (oid,))
    org['deals'] = [dict_from_row(r) for r in cursor.fetchall()]
    cursor = db.execute('SELECT a.*, co.name as org_name, c.name as contact_name FROM activities a LEFT JOIN customer_organizations co ON a.organization_id=co.id LEFT JOIN contacts c ON a.contact_id=c.id WHERE a.organization_id=? ORDER BY a.created_at DESC LIMIT 10', (oid,))
    org['activities'] = [dict_from_row(r) for r in cursor.fetchall()]
    cursor = db.execute('''SELECT f.*, co.name as org_name, d.name as deal_name, c.name as contact_name 
        FROM followups f LEFT JOIN customer_organizations co ON f.organization_id=co.id 
        LEFT JOIN deals d ON f.deal_id=d.id LEFT JOIN contacts c ON f.contact_id=c.id 
        WHERE f.organization_id=? AND f.status NOT IN ('已完成','已取消') ORDER BY f.due_date''', (oid,))
    org['followups'] = [dict_from_row(r) for r in cursor.fetchall()]
    return jsonify(org)

@app.route('/api/organizations/<int:oid>', methods=['DELETE'])
@login_required
def delete_organization(oid):
    """删除客户单位"""
    db = get_db()
    db.execute('DELETE FROM customer_organizations WHERE id=?', (oid,))
    db.commit()
    log_security_event('deletion', f'删除客户单位: id={oid}', 'customer_organizations', oid)
    return jsonify({'message': '删除成功'})

@app.route('/api/contacts', methods=['GET'])
@login_required
def list_contacts():
    """获取联系人列表"""
    db = get_db()
    org_id = request.args.get('organization_id')
    q = 'SELECT c.*, co.name as org_name FROM contacts c LEFT JOIN customer_organizations co ON c.organization_id=co.id WHERE 1=1'
    params = []
    if org_id:
        q += ' AND c.organization_id=?'
        params.append(org_id)
    q += ' ORDER BY c.id DESC'
    cursor = db.execute(q, params)
    return jsonify([dict_from_row(r) for r in cursor.fetchall()])

@app.route('/api/contacts', methods=['POST'])
@login_required
def create_contact():
    """创建联系人"""
    data = request.get_json()
    db = get_db()
    try:
        cursor = db.execute('''INSERT INTO contacts (name,position,phone,email,organization_id,tags,notes)
            VALUES (?,?,?,?,?,?,?)''', (
            data['name'], data.get('position'), data.get('phone'), data.get('email'),
            data.get('organization_id'), data.get('tags'), data.get('notes')))
        db.commit()
        return jsonify({'id': cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:cid>', methods=['PUT'])
@login_required
def update_contact(cid):
    """更新联系人"""
    data = request.get_json()
    db = get_db()
    fields = ['name','position','phone','email','organization_id','tags','notes']
    sets = [f'{f}=?' for f in fields if f in data]
    vals = [data[f] for f in fields if f in data]
    if not sets:
        return jsonify({'error': '没有要更新的字段'}), 400
    sets.append("updated_at=CURRENT_TIMESTAMP")
    vals.append(cid)
    db.execute(f"UPDATE contacts SET {','.join(sets)} WHERE id=?", vals)
    db.commit()
    return jsonify({'message': '更新成功'})

@app.route('/api/contacts/<int:cid>/detail', methods=['GET'])
@login_required
def contact_detail(cid):
    """联系人详情（含关联数据）"""
    db = get_db()
    cursor = db.execute('SELECT c.*, co.name as org_name FROM contacts c LEFT JOIN customer_organizations co ON c.organization_id=co.id WHERE c.id=?', (cid,))
    contact = dict_from_row(cursor.fetchone())
    if not contact:
        return jsonify({'error': '未找到'}), 404
    if contact['organization_id']:
        cursor = db.execute('SELECT * FROM customer_organizations WHERE id=?', (contact['organization_id'],))
        contact['organization'] = dict_from_row(cursor.fetchone())
    else:
        contact['organization'] = None
    cursor = db.execute('SELECT d.*, co.name as org_name, c.name as contact_name FROM deals d LEFT JOIN customer_organizations co ON d.organization_id=co.id LEFT JOIN contacts c ON d.contact_id=c.id WHERE d.contact_id=? ORDER BY d.id DESC', (cid,))
    contact['deals'] = [dict_from_row(r) for r in cursor.fetchall()]
    cursor = db.execute('SELECT a.*, co.name as org_name, c2.name as contact_name FROM activities a LEFT JOIN customer_organizations co ON a.organization_id=co.id LEFT JOIN contacts c2 ON a.contact_id=c2.id WHERE a.contact_id=? ORDER BY a.created_at DESC LIMIT 10', (cid,))
    contact['activities'] = [dict_from_row(r) for r in cursor.fetchall()]
    return jsonify(contact)

@app.route('/api/contacts/<int:cid>', methods=['DELETE'])
@login_required
def delete_contact(cid):
    """删除联系人"""
    db = get_db()
    db.execute('DELETE FROM contacts WHERE id=?', (cid,))
    db.commit()
    return jsonify({'message': '删除成功'})

@app.route('/api/deals', methods=['GET'])
@login_required
def list_deals():
    """获取商机列表"""
    db = get_db()
    org_id = request.args.get('organization_id')
    q = 'SELECT d.*, co.name as org_name, c.name as contact_name FROM deals d LEFT JOIN customer_organizations co ON d.organization_id=co.id LEFT JOIN contacts c ON d.contact_id=c.id WHERE 1=1'
    params = []
    if org_id:
        q += ' AND d.organization_id=?'
        params.append(org_id)
    q += ' ORDER BY d.id DESC'
    cursor = db.execute(q, params)
    return jsonify([dict_from_row(r) for r in cursor.fetchall()])

@app.route('/api/deals', methods=['POST'])
@login_required
def create_deal():
    """创建商机"""
    data = request.get_json()
    db = get_db()
    try:
        cursor = db.execute('''INSERT INTO deals (name,organization_id,amount,stage,product_line,contact_id,notes)
            VALUES (?,?,?,?,?,?,?)''', (
            data['name'], data.get('organization_id'), data.get('amount',0),
            data.get('stage','初期沟通'), data.get('product_line'), data.get('contact_id'), data.get('notes')))
        db.commit()
        return jsonify({'id': cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deals/<int:did>', methods=['PUT'])
@login_required
def update_deal(did):
    """更新商机"""
    data = request.get_json()
    db = get_db()
    fields = ['name','organization_id','amount','stage','product_line','contact_id','notes']
    sets = [f'{f}=?' for f in fields if f in data]
    vals = [data[f] for f in fields if f in data]
    if not sets:
        return jsonify({'error': '没有要更新的字段'}), 400
    sets.append("updated_at=CURRENT_TIMESTAMP")
    vals.append(did)
    db.execute(f"UPDATE deals SET {','.join(sets)} WHERE id=?", vals)
    db.commit()
    return jsonify({'message': '更新成功'})

@app.route('/api/deals/<int:did>/detail', methods=['GET'])
@login_required
def deal_detail(did):
    """商机详情（含关联数据）"""
    db = get_db()
    cursor = db.execute('SELECT d.*, co.name as org_name, c.name as contact_name FROM deals d LEFT JOIN customer_organizations co ON d.organization_id=co.id LEFT JOIN contacts c ON d.contact_id=c.id WHERE d.id=?', (did,))
    deal = dict_from_row(cursor.fetchone())
    if not deal:
        return jsonify({'error': '未找到'}), 404
    if deal['organization_id']:
        cursor = db.execute('SELECT * FROM customer_organizations WHERE id=?', (deal['organization_id'],))
        deal['organization'] = dict_from_row(cursor.fetchone())
    else:
        deal['organization'] = None
    if deal['contact_id']:
        cursor = db.execute('SELECT * FROM contacts WHERE id=?', (deal['contact_id'],))
        deal['contact'] = dict_from_row(cursor.fetchone())
    else:
        deal['contact'] = None
    cursor = db.execute('''SELECT a.*, co.name as org_name, c.name as contact_name 
        FROM activities a LEFT JOIN customer_organizations co ON a.organization_id=co.id 
        LEFT JOIN contacts c ON a.contact_id=c.id WHERE a.organization_id=? ORDER BY a.created_at DESC LIMIT 10''', (deal['organization_id'],))
    deal['activities'] = [dict_from_row(r) for r in cursor.fetchall()]
    cursor = db.execute('''SELECT f.*, co.name as org_name, d.name as deal_name, c.name as contact_name 
        FROM followups f LEFT JOIN customer_organizations co ON f.organization_id=co.id 
        LEFT JOIN deals d ON f.deal_id=d.id LEFT JOIN contacts c ON f.contact_id=c.id 
        WHERE f.deal_id=? AND f.status NOT IN ('已完成','已取消') ORDER BY f.due_date''', (did,))
    deal['followups'] = [dict_from_row(r) for r in cursor.fetchall()]
    return jsonify(deal)

@app.route('/api/deals/<int:did>', methods=['DELETE'])
@login_required
def delete_deal(did):
    """删除商机"""
    db = get_db()
    db.execute('DELETE FROM deals WHERE id=?', (did,))
    db.commit()
    return jsonify({'message': '删除成功'})

@app.route('/api/activities', methods=['GET'])
@login_required
def list_activities():
    """获取活动记录"""
    db = get_db()
    org_id = request.args.get('organization_id')
    q = 'SELECT a.*, co.name as org_name, c.name as contact_name FROM activities a LEFT JOIN customer_organizations co ON a.organization_id=co.id LEFT JOIN contacts c ON a.contact_id=c.id WHERE 1=1'
    params = []
    if org_id:
        q += ' AND a.organization_id=?'
        params.append(org_id)
    q += ' ORDER BY a.created_at DESC'
    cursor = db.execute(q, params)
    return jsonify([dict_from_row(r) for r in cursor.fetchall()])

@app.route('/api/activities', methods=['POST'])
@login_required
def create_activity():
    """创建活动记录"""
    data = request.get_json()
    db = get_db()
    try:
        cursor = db.execute('''INSERT INTO activities (type,organization_id,contact_id,summary)
            VALUES (?,?,?,?)''', (
            data['type'], data.get('organization_id'), data.get('contact_id'), data.get('summary')))
        db.commit()
        return jsonify({'id': cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/activities/<int:aid>/detail', methods=['GET'])
@login_required
def activity_detail(aid):
    """活动详情"""
    db = get_db()
    cursor = db.execute('''SELECT a.*, co.name as org_name, co.id as org_id, c.name as contact_name, c.id as contact_id 
        FROM activities a LEFT JOIN customer_organizations co ON a.organization_id=co.id 
        LEFT JOIN contacts c ON a.contact_id=c.id WHERE a.id=?''', (aid,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': '未找到'}), 404
    activity = dict_from_row(row)
    return jsonify(activity)

@app.route('/api/activities/<int:aid>', methods=['DELETE'])
@login_required
def delete_activity(aid):
    """删除活动记录"""
    db = get_db()
    db.execute('DELETE FROM activities WHERE id=?', (aid,))
    db.commit()
    return jsonify({'message': '删除成功'})

@app.route('/api/followups', methods=['GET'])
@login_required
def list_followups():
    """获取待办跟进"""
    db = get_db()
    q = '''SELECT f.*, co.name as org_name, d.name as deal_name, c.name as contact_name 
        FROM followups f LEFT JOIN customer_organizations co ON f.organization_id=co.id 
        LEFT JOIN deals d ON f.deal_id=d.id LEFT JOIN contacts c ON f.contact_id=c.id 
        WHERE 1=1 ORDER BY f.created_at DESC'''
    cursor = db.execute(q)
    return jsonify([dict_from_row(r) for r in cursor.fetchall()])

@app.route('/api/followups/<int:fid>/detail', methods=['GET'])
@login_required
def followup_detail(fid):
    """待办详情"""
    db = get_db()
    cursor = db.execute('''SELECT f.*, co.name as org_name, co.id as org_id, d.name as deal_name, d.id as deal_id, c.name as contact_name, c.id as contact_id 
        FROM followups f LEFT JOIN customer_organizations co ON f.organization_id=co.id 
        LEFT JOIN deals d ON f.deal_id=d.id LEFT JOIN contacts c ON f.contact_id=c.id 
        WHERE f.id=?''', (fid,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': '未找到'}), 404
    followup = dict_from_row(row)
    return jsonify(followup)

@app.route('/api/followups', methods=['POST'])
@login_required
def create_followup():
    """创建待办跟进"""
    data = request.get_json()
    db = get_db()
    try:
        cursor = db.execute('''INSERT INTO followups (deal_id,organization_id,contact_id,content,due_date,status)
            VALUES (?,?,?,?,?,?)''', (
            data.get('deal_id'), data.get('organization_id'), data.get('contact_id'), data['content'],
            data.get('due_date'), data.get('status','待处理')))
        db.commit()
        return jsonify({'id': cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/followups/<int:fid>', methods=['PUT'])
@login_required
def update_followup(fid):
    """更新待办跟进"""
    data = request.get_json()
    db = get_db()
    fields = ['deal_id','organization_id','contact_id','content','due_date','status']
    sets = [f'{f}=?' for f in fields if f in data]
    vals = [data[f] for f in fields if f in data]
    if not sets:
        return jsonify({'error': '没有要更新的字段'}), 400
    vals.append(fid)
    db.execute(f"UPDATE followups SET {','.join(sets)} WHERE id=?", vals)
    db.commit()
    return jsonify({'message': '更新成功'})

@app.route('/api/followups/<int:fid>', methods=['DELETE'])
@login_required
def delete_followup(fid):
    """删除待办跟进"""
    db = get_db()
    db.execute('DELETE FROM followups WHERE id=?', (fid,))
    db.commit()
    return jsonify({'message': '删除成功'})

@app.route('/api/ai-insights-web', methods=['GET'])
@login_required
def list_ai_insights_web():
    """获取AI洞察（Web管理界面）"""
    db = get_db()
    q = 'SELECT ai.*, co.name as org_name FROM ai_insights ai LEFT JOIN customer_organizations co ON ai.organization_id=co.id ORDER BY ai.generated_date DESC'
    cursor = db.execute(q)
    return jsonify([dict_from_row(r) for r in cursor.fetchall()])

@app.route('/api/ai-insights-web/<int:iid>', methods=['GET'])
@login_required
def insight_detail(iid):
    """AI洞察详情"""
    db = get_db()
    cursor = db.execute('''SELECT ai.*, co.name as org_name, co.id as org_id 
        FROM ai_insights ai LEFT JOIN customer_organizations co ON ai.organization_id=co.id WHERE ai.id=?''', (iid,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': '未找到'}), 404
    insight = dict_from_row(row)
    if insight.get('recommended_actions'):
        try:
            insight['recommended_actions'] = json.loads(insight['recommended_actions'])
        except:
            pass
    return jsonify(insight)

@app.route('/api/ai-insights-web/<int:iid>', methods=['PUT'])
@login_required
def update_ai_insight_web(iid):
    """更新AI洞察状态"""
    data = request.get_json()
    db = get_db()
    if 'status' in data:
        db.execute('UPDATE ai_insights SET status=?, reviewed_at=CURRENT_TIMESTAMP WHERE id=?', (data['status'], iid))
    db.commit()
    return jsonify({'message': '更新成功'})

@app.route('/api/dashboard', methods=['GET'])
@login_required
def dashboard_stats():
    """仪表盘统计数据"""
    db = get_db()
    cursor = db.execute('SELECT COUNT(*) as cnt FROM customer_organizations')
    org_count = cursor.fetchone()['cnt']
    cursor = db.execute('SELECT COUNT(*) as cnt FROM contacts')
    contact_count = cursor.fetchone()['cnt']
    cursor = db.execute('SELECT COALESCE(SUM(amount),0) as total, COUNT(*) as cnt FROM deals')
    deal_stats = dict_from_row(cursor.fetchone())
    cursor = db.execute("SELECT stage, COUNT(*) as cnt, SUM(amount) as amount FROM deals GROUP BY stage")
    deal_stages = [dict_from_row(r) for r in cursor.fetchall()]
    cursor = db.execute('''SELECT a.id, a.type, a.summary as subject, a.created_at as date, co.name as org_name 
        FROM activities a LEFT JOIN customer_organizations co ON a.organization_id=co.id 
        ORDER BY a.created_at DESC LIMIT 10''')
    recent_activities = [dict_from_row(r) for r in cursor.fetchall()]
    cursor = db.execute('''SELECT f.id, f.content as title, f.due_date, f.status, 
        co.name as org_name, d.name as deal_name, c.name as contact_name
        FROM followups f LEFT JOIN customer_organizations co ON f.organization_id=co.id 
        LEFT JOIN deals d ON f.deal_id=d.id LEFT JOIN contacts c ON f.contact_id=c.id 
        WHERE f.status='待处理' ORDER BY f.due_date LIMIT 10''')
    pending_followups = [dict_from_row(r) for r in cursor.fetchall()]
    cursor = db.execute("SELECT COUNT(*) as cnt FROM ai_insights WHERE status='new'")
    new_insights = cursor.fetchone()['cnt']
    cursor = db.execute('''SELECT id, insight_type, insight_text as title, priority, status, generated_date 
        FROM ai_insights WHERE status='new' ORDER BY generated_date DESC LIMIT 5''')
    recent_insights = []
    priority_map = {'low': '低', 'medium': '中', 'high': '高', 'critical': '紧急'}
    insight_type_map = {
        'churn_risk': '流失预警',
        'upsell_opportunity': '商机预警',
        'cross_sell': '交叉销售',
        'health_alert': '客户风险',
        'renewal_prediction': '跟进建议',
    }
    for row in cursor.fetchall():
        r = dict_from_row(row)
        r['priority'] = priority_map.get(r['priority'], r['priority'])
        r['insight_type'] = insight_type_map.get(r['insight_type'], r['insight_type'])
        recent_insights.append(r)

    return jsonify({
        'organizations': org_count,
        'contacts': contact_count,
        'deal_amount': deal_stats['total'],
        'deals': deal_stats['cnt'],
        'deals_by_stage': deal_stages,
        'recent_activities': recent_activities,
        'upcoming_followups': pending_followups,
        'new_insights': new_insights,
        'recent_insights': recent_insights
    })

# ==================== 差异化功能API（保留兼容）====================

@app.route('/api/product-usage', methods=['GET'])
@login_required
def get_product_usage():
    """获取产品使用数据"""
    db = get_db()
    organization_id = request.args.get('organization_id')
    product_type = request.args.get('product_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = 'SELECT * FROM product_usage WHERE 1=1'
    params = []
    if organization_id:
        query += ' AND organization_id = ?'
        params.append(organization_id)
    if product_type:
        query += ' AND product_type = ?'
        params.append(product_type)
    if start_date:
        query += ' AND usage_date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND usage_date <= ?'
        params.append(end_date)
    query += ' ORDER BY usage_date DESC'
    cursor = db.execute(query, params)
    return jsonify([dict_from_row(row) for row in cursor.fetchall()])

@app.route('/api/product-usage', methods=['POST'])
@login_required
def create_product_usage():
    """创建产品使用记录"""
    data = request.get_json()
    required_fields = ['organization_id', 'product_type', 'usage_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    db = get_db()
    try:
        cursor = db.execute('''
            INSERT INTO product_usage 
            (organization_id, product_type, module_name, usage_date, usage_count, 
             active_users, performance_score, issues_reported, support_tickets, feature_requests)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['organization_id'], data['product_type'], data.get('module_name'),
            data['usage_date'], data.get('usage_count', 1), data.get('active_users'),
            data.get('performance_score'), data.get('issues_reported', 0),
            data.get('support_tickets', 0),
            json.dumps(data.get('feature_requests', [])) if data.get('feature_requests') else None
        ))
        usage_id = cursor.lastrowid
        db.commit()
        log_security_event('modification', f'创建产品使用记录: id={usage_id}', 'product_usage', usage_id)
        generate_ai_insights(data['organization_id'])
        return jsonify({'id': usage_id, 'message': 'Product usage record created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-insights', methods=['GET'])
@login_required
def get_ai_insights():
    """获取AI洞察"""
    db = get_db()
    organization_id = request.args.get('organization_id')
    insight_type = request.args.get('insight_type')
    status = request.args.get('status', 'new')
    priority = request.args.get('priority')
    
    query = 'SELECT * FROM ai_insights WHERE 1=1'
    params = []
    if organization_id:
        query += ' AND organization_id = ?'
        params.append(organization_id)
    if insight_type:
        query += ' AND insight_type = ?'
        params.append(insight_type)
    if status:
        query += ' AND status = ?'
        params.append(status)
    if priority:
        query += ' AND priority = ?'
        params.append(priority)
    query += ' ORDER BY priority DESC, generated_date DESC'
    cursor = db.execute(query, params)
    return jsonify([dict_from_row(row) for row in cursor.fetchall()])

@app.route('/api/ai-insights/<int:insight_id>', methods=['PUT'])
@login_required
def update_ai_insight(insight_id):
    """更新AI洞察状态"""
    data = request.get_json()
    if 'status' not in data:
        return jsonify({'error': 'Missing status field'}), 400
    db = get_db()
    try:
        cursor = db.execute('''
            UPDATE ai_insights SET status = ?, reviewed_by = ?, reviewed_at = ? WHERE id = ?
        ''', (data['status'], data.get('reviewed_by', 'system'), datetime.now().isoformat(), insight_id))
        if cursor.rowcount == 0:
            return jsonify({'error': 'Insight not found'}), 404
        db.commit()
        return jsonify({'message': 'Insight updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customer-health', methods=['GET'])
@login_required
def get_customer_health():
    """获取客户健康度报告"""
    db = get_db()
    organization_id = request.args.get('organization_id')
    
    if organization_id:
        cursor = db.execute('SELECT * FROM customer_health_view WHERE id = ?', (organization_id,))
        health_data = dict_from_row(cursor.fetchone())
        if not health_data:
            return jsonify({'error': 'Customer not found'}), 404
        cursor = db.execute('''
            SELECT * FROM ai_insights WHERE organization_id = ? AND status = 'new'
            ORDER BY priority DESC, generated_date DESC LIMIT 5
        ''', (organization_id,))
        insights = [dict_from_row(row) for row in cursor.fetchall()]
        cursor = db.execute('''
            SELECT product_type, usage_date, usage_count FROM product_usage 
            WHERE organization_id = ? AND usage_date >= date('now', '-90 days') ORDER BY usage_date
        ''', (organization_id,))
        usage_trend = [dict_from_row(row) for row in cursor.fetchall()]
        result = {'health_data': health_data, 'recent_insights': insights, 'usage_trend': usage_trend, 'generated_at': datetime.now().isoformat()}
    else:
        cursor = db.execute('''
            SELECT COUNT(*) as total_customers, AVG(health_score) as avg_health_score,
                SUM(CASE WHEN risk_level = 'critical' THEN 1 ELSE 0 END) as critical_risk_count,
                SUM(CASE WHEN risk_level = 'high' THEN 1 ELSE 0 END) as high_risk_count,
                SUM(CASE WHEN using_netshield = 1 THEN 1 ELSE 0 END) as netshield_users,
                SUM(CASE WHEN using_inoc = 1 THEN 1 ELSE 0 END) as inoc_users
            FROM customer_organizations
        ''')
        overview = dict_from_row(cursor.fetchone())
        cursor = db.execute('''
            SELECT CASE WHEN health_score >= 80 THEN 'excellent' WHEN health_score >= 60 THEN 'good'
                WHEN health_score >= 40 THEN 'fair' ELSE 'poor' END as health_category, COUNT(*) as count
            FROM customer_organizations GROUP BY health_category
        ''')
        distribution = [dict_from_row(row) for row in cursor.fetchall()]
        result = {'overview': overview, 'health_distribution': distribution, 'generated_at': datetime.now().isoformat()}
    
    return jsonify(result)

@app.route('/api/workflows', methods=['GET'])
@login_required
def get_workflows():
    """获取自动化工作流"""
    db = get_db()
    cursor = db.execute('SELECT * FROM workflow_automations ORDER BY name')
    return jsonify([dict_from_row(row) for row in cursor.fetchall()])

@app.route('/api/workflows/<int:workflow_id>/execute', methods=['POST'])
@login_required
def execute_workflow(workflow_id):
    """执行工作流"""
    data = request.get_json() or {}
    db = get_db()
    cursor = db.execute('SELECT * FROM workflow_automations WHERE id = ?', (workflow_id,))
    workflow = dict_from_row(cursor.fetchone())
    if not workflow:
        return jsonify({'error': 'Workflow not found'}), 404
    if not workflow['enabled']:
        return jsonify({'error': 'Workflow is disabled'}), 400
    
    start_time = datetime.now()
    try:
        actions = json.loads(workflow['actions'])
        execution_result = {'workflow_id': workflow_id, 'execution_time': start_time.isoformat(),
            'actions_executed': len(actions), 'status': 'success', 'details': f"Executed {len(actions)} actions"}
        db.execute('''UPDATE workflow_automations SET last_executed = ?, execution_count = execution_count + 1, 
            success_count = success_count + 1 WHERE id = ?''', (start_time.isoformat(), workflow_id))
        db.execute('''INSERT INTO workflow_executions 
            (workflow_id, execution_time, trigger_event, input_data, output_data, status, execution_duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', (
            workflow_id, start_time.isoformat(), data.get('trigger_event', 'manual'),
            json.dumps(data), json.dumps(execution_result), 'success',
            int((datetime.now() - start_time).total_seconds() * 1000)))
        db.commit()
        return jsonify(execution_result)
    except Exception as e:
        error_time = datetime.now()
        db.execute('''UPDATE workflow_automations SET last_executed = ?, execution_count = execution_count + 1, 
            failure_count = failure_count + 1 WHERE id = ?''', (error_time.isoformat(), workflow_id))
        db.execute('''INSERT INTO workflow_executions 
            (workflow_id, execution_time, trigger_event, input_data, output_data, status, error_message, execution_duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
            workflow_id, error_time.isoformat(), data.get('trigger_event', 'manual'),
            json.dumps(data), json.dumps({'error': str(e)}), 'failed', str(e),
            int((error_time - start_time).total_seconds() * 1000)))
        db.commit()
        return jsonify({'error': str(e)}), 500

@app.route('/api/security-logs', methods=['GET'])
@login_required
def get_security_logs():
    """获取安全日志"""
    db = get_db()
    organization_id = request.args.get('organization_id')
    log_type = request.args.get('log_type')
    severity = request.args.get('severity')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = request.args.get('limit', 100)
    
    query = 'SELECT * FROM security_logs WHERE 1=1'
    params = []
    if organization_id:
        query += ' AND organization_id = ?'
        params.append(organization_id)
    if log_type:
        query += ' AND log_type = ?'
        params.append(log_type)
    if severity:
        query += ' AND severity = ?'
        params.append(severity)
    if start_date:
        query += ' AND event_time >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND event_time <= ?'
        params.append(end_date)
    query += ' ORDER BY event_time DESC LIMIT ?'
    params.append(limit)
    cursor = db.execute(query, params)
    return jsonify([dict_from_row(row) for row in cursor.fetchall()])

# ==================== 兼容旧API（保留重定向） ====================

@app.route('/api/customer-organizations', methods=['GET'])
@login_required
def get_customer_organizations():
    """获取客户单位列表（兼容旧API）"""
    db = get_db()
    cursor = db.execute('SELECT * FROM customer_organizations ORDER BY name')
    return jsonify([dict_from_row(row) for row in cursor.fetchall()])

@app.route('/api/customer-organizations', methods=['POST'])
@login_required
def create_customer_organization():
    """创建客户单位（兼容旧API）"""
    data = request.get_json()
    required_fields = ['name', 'type', 'created_by']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    db = get_db()
    try:
        cursor = db.execute('''INSERT INTO customer_organizations 
            (name, type, industry, scale, security_level, address, phone, email, 
             invoice_info, tax_number, bank_account, using_netshield, netshield_version,
             netshield_license_expiry, using_inoc, inoc_modules, inoc_license_expiry,
             potential_score, health_score, risk_level, classification, tags, created_by, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['name'], data['type'], data.get('industry'), data.get('scale'),
            data.get('security_level', 'standard'), data.get('address'), data.get('phone'),
            data.get('email'), data.get('invoice_info'), data.get('tax_number'), data.get('bank_account'),
            data.get('using_netshield', False), data.get('netshield_version'), data.get('netshield_license_expiry'),
            data.get('using_inoc', False),
            json.dumps(data.get('inoc_modules', [])) if data.get('inoc_modules') else None,
            data.get('inoc_license_expiry'), data.get('potential_score', 0), data.get('health_score', 100),
            data.get('risk_level', 'low'), data.get('classification'),
            json.dumps(data.get('tags', [])) if data.get('tags') else None,
            data['created_by'], data.get('notes')))
        org_id = cursor.lastrowid
        db.commit()
        log_security_event('modification', f'创建客户单位: id={org_id}, name={data["name"]}', 'customer_organizations', org_id)
        return jsonify({'id': org_id, 'message': 'Customer organization created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== AI洞察生成函数 ====================

def generate_ai_insights(organization_id):
    """生成AI洞察（模拟）"""
    db = get_db()
    try:
        cursor = db.execute('SELECT * FROM customer_organizations WHERE id = ?', (organization_id,))
        customer = dict_from_row(cursor.fetchone())
        if not customer:
            return
        insights_to_create = []
        if customer.get('netshield_license_expiry'):
            expiry_date = datetime.strptime(customer['netshield_license_expiry'], '%Y-%m-%d')
            days_until_expiry = (expiry_date - datetime.now()).days
            if 0 < days_until_expiry <= 90:
                confidence = max(0.1, min(0.9, (90 - days_until_expiry) / 90))
                insights_to_create.append({
                    'insight_type': 'renewal_prediction', 'confidence_score': confidence,
                    'insight_text': f'网盾许可证将在{days_until_expiry}天后到期，需及时跟进续约',
                    'recommended_actions': ['联系客户确认续约意向', '准备续约报价单', '安排续约沟通会议'],
                    'priority': 'high' if days_until_expiry <= 30 else 'medium'
                })
        if customer.get('using_netshield') and not customer.get('using_inoc'):
            cursor = db.execute('''SELECT COUNT(*) as usage_count FROM product_usage 
                WHERE organization_id = ? AND product_type = 'netshield' AND usage_date >= date('now', '-30 days')''', (organization_id,))
            usage = cursor.fetchone()
            if usage and usage['usage_count'] >= 10:
                insights_to_create.append({
                    'insight_type': 'cross_sell', 'confidence_score': 0.7,
                    'insight_text': '客户频繁使用网盾，可能对I-NOC智能运维平台感兴趣',
                    'recommended_actions': ['准备I-NOC产品介绍', '安排产品演示', '制定交叉销售方案'],
                    'priority': 'medium'
                })
        cursor = db.execute('''SELECT COUNT(*) as recent_usage FROM product_usage 
            WHERE organization_id = ? AND usage_date >= date('now', '-30 days')''', (organization_id,))
        recent_usage = cursor.fetchone()
        if recent_usage and recent_usage['recent_usage'] == 0:
            insights_to_create.append({
                'insight_type': 'churn_risk', 'confidence_score': 0.6,
                'insight_text': '客户近30天无产品使用记录，可能存在流失风险',
                'recommended_actions': ['主动联系客户了解使用情况', '提供产品使用培训', '收集反馈意见'],
                'priority': 'high'
            })
        for insight in insights_to_create:
            db.execute('''INSERT INTO ai_insights 
                (organization_id, insight_type, generated_date, confidence_score, 
                 insight_text, recommended_actions, priority, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'new')
            ''', (organization_id, insight['insight_type'], datetime.now().date().isoformat(),
                insight['confidence_score'], insight['insight_text'],
                json.dumps(insight['recommended_actions']), insight['priority']))
        db.commit()
        log_security_event('modification', f'生成AI洞察: org={organization_id}, count={len(insights_to_create)}')
    except Exception as e:
        log_security_event('modification', f'生成AI洞察失败: {str(e)}', severity='error')
        print(f"Error generating AI insights: {e}")

# ==================== 健康检查和页面路由 ====================

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    try:
        db = get_db()
        db.execute('SELECT 1')
        tables = ['customer_organizations', 'product_usage', 'ai_insights', 'security_logs', 'users', 'roles']
        table_status = {}
        for table in tables:
            try:
                cursor = db.execute(f'SELECT COUNT(*) as count FROM {table}')
                result = cursor.fetchone()
                table_status[table] = {'count': result['count'], 'status': 'healthy'}
            except Exception as e:
                table_status[table] = {'error': str(e), 'status': 'unhealthy'}
        return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat(), 'tables': table_status, 'version': '2.1'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# /, /login, /index routes now handled by Vue SPA static file serving below

# ==================== 数据库初始化 ====================

def init_auth_tables():
    """初始化用户和角色表"""
    with app.app_context():
        db = get_db()
        
        # 创建roles表
        db.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_name TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                description TEXT DEFAULT '',
                permissions TEXT DEFAULT '{}',
                is_system BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建users表
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                real_name TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                role_id INTEGER DEFAULT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                last_login DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (role_id) REFERENCES roles(id)
            )
        ''')
        
        db.commit()
        
        # 检查是否已有预置角色
        cursor = db.execute('SELECT COUNT(*) as cnt FROM roles')
        if cursor.fetchone()['cnt'] == 0:
            print("正在创建预置角色...")
            
            # 管理员 - 全部权限
            admin_perms = {
                'customers': {'view': True, 'create': True, 'edit': True, 'delete': True},
                'contacts': {'view': True, 'create': True, 'edit': True, 'delete': True},
                'deals': {'view': True, 'create': True, 'edit': True, 'delete': True},
                'activities': {'view': True, 'create': True, 'edit': True, 'delete': True},
                'followups': {'view': True, 'create': True, 'edit': True, 'delete': True},
                'insights': {'view': True, 'edit': True},
                'users': {'view': True, 'create': True, 'edit': True, 'delete': True},
                'roles': {'view': True, 'create': True, 'edit': True, 'delete': True}
            }
            
            # 销售经理
            sm_perms = {
                'customers': {'view': True, 'create': True, 'edit': True, 'delete': True},
                'contacts': {'view': True, 'create': True, 'edit': True, 'delete': True},
                'deals': {'view': True, 'create': True, 'edit': True, 'delete': True},
                'activities': {'view': True, 'create': True, 'edit': True, 'delete': True},
                'followups': {'view': True, 'create': True, 'edit': True, 'delete': True},
                'insights': {'view': True, 'edit': False},
                'users': {'view': False, 'create': False, 'edit': False, 'delete': False},
                'roles': {'view': False, 'create': False, 'edit': False, 'delete': False}
            }
            
            # 销售
            sales_perms = {
                'customers': {'view': True, 'create': True, 'edit': True, 'delete': False},
                'contacts': {'view': True, 'create': True, 'edit': True, 'delete': True},
                'deals': {'view': True, 'create': False, 'edit': False, 'delete': False},
                'activities': {'view': True, 'create': True, 'edit': True, 'delete': True},
                'followups': {'view': True, 'create': True, 'edit': True, 'delete': True},
                'insights': {'view': True, 'edit': False},
                'users': {'view': False, 'create': False, 'edit': False, 'delete': False},
                'roles': {'view': False, 'create': False, 'edit': False, 'delete': False}
            }
            
            # 访客 - 只读
            viewer_perms = {
                'customers': {'view': True, 'create': False, 'edit': False, 'delete': False},
                'contacts': {'view': True, 'create': False, 'edit': False, 'delete': False},
                'deals': {'view': True, 'create': False, 'edit': False, 'delete': False},
                'activities': {'view': True, 'create': False, 'edit': False, 'delete': False},
                'followups': {'view': True, 'create': False, 'edit': False, 'delete': False},
                'insights': {'view': True, 'edit': False},
                'users': {'view': False, 'create': False, 'edit': False, 'delete': False},
                'roles': {'view': False, 'create': False, 'edit': False, 'delete': False}
            }
            
            roles_data = [
                ('admin', '管理员', '系统管理员，拥有全部权限', json.dumps(admin_perms)),
                ('sales_manager', '销售经理', '销售经理，管理客户、商机和团队', json.dumps(sm_perms)),
                ('sales', '销售', '销售人员，管理日常客户跟进', json.dumps(sales_perms)),
                ('viewer', '访客', '只读访客，可查看所有数据', json.dumps(viewer_perms))
            ]
            
            for role_name, display_name, desc, perms in roles_data:
                db.execute('INSERT INTO roles (role_name, display_name, description, permissions, is_system) VALUES (?, ?, ?, ?, TRUE)',
                          (role_name, display_name, desc, perms))
            
            db.commit()
            print("预置角色创建完成")
        
        # 检查是否已有预置用户
        cursor = db.execute('SELECT COUNT(*) as cnt FROM users')
        if cursor.fetchone()['cnt'] == 0:
            print("正在创建预置用户...")
            
            # 获取角色ID
            cursor = db.execute('SELECT id FROM roles WHERE role_name=?', ('admin',))
            admin_role_id = cursor.fetchone()['id']
            cursor = db.execute('SELECT id FROM roles WHERE role_name=?', ('sales_manager',))
            sm_role_id = cursor.fetchone()['id']
            
            # 创建管理员
            db.execute('INSERT INTO users (username, password_hash, real_name, role_id, is_active) VALUES (?, ?, ?, ?, TRUE)',
                      ('admin', generate_password_hash('admin123'), '管理员', admin_role_id))
            # 创建演示用户
            db.execute('INSERT INTO users (username, password_hash, real_name, role_id, is_active) VALUES (?, ?, ?, ?, TRUE)',
                      ('demouser', generate_password_hash('demo123'), '演示用户', sm_role_id))
            
            db.commit()
            print("预置用户创建完成：admin/admin123, demouser/demo123")

def init_database():
    """初始化数据库"""
    with app.app_context():
        db = get_db()
        schema_path = os.path.join(os.path.dirname(__file__), 'schema_enhanced.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        print("正在创建差异化CRM数据库...")
        db.executescript(schema_sql)
        
        example_workflows = [
            {'name': '客户健康度检查', 'trigger_type': 'scheduled',
             'trigger_condition': json.dumps({'schedule': 'daily', 'time': '09:00'}),
             'actions': json.dumps([
                {'type': 'check_customer_health', 'parameters': {}},
                {'type': 'generate_report', 'parameters': {'format': 'summary'}},
                {'type': 'send_notification', 'parameters': {'channel': 'feishu', 'recipients': ['韩晓晨']}}])},
            {'name': '许可证到期提醒', 'trigger_type': 'condition_based',
             'trigger_condition': json.dumps({'condition': 'license_expiry_days <= 30'}),
             'actions': json.dumps([
                {'type': 'send_email', 'parameters': {'template': 'license_renewal_reminder'}},
                {'type': 'create_task', 'parameters': {'assignee': '韩晓晨', 'due_days': 7}}])}
        ]
        for workflow in example_workflows:
            db.execute('''INSERT INTO workflow_automations (name, trigger_type, trigger_condition, actions, enabled)
                VALUES (?, ?, ?, ?, ?)''', (workflow['name'], workflow['trigger_type'],
                workflow['trigger_condition'], workflow['actions'], True))
        db.commit()
        print("差异化CRM数据库初始化完成！")
        
        # 初始化认证表
        init_auth_tables()

# ==================== 前端静态文件路由 ====================
import sys

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web', 'dist')

if os.path.isdir(STATIC_DIR):
    from flask import send_from_directory, send_file

    @app.route('/')
    def serve_index():
        return send_from_directory(STATIC_DIR, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        # Don't intercept API routes
        if path.startswith('api/'):
            return '', 404
        file_path = os.path.join(STATIC_DIR, path)
        if os.path.isfile(file_path):
            return send_from_directory(STATIC_DIR, path)
        # SPA fallback: return index.html for non-API, non-static routes
        return send_from_directory(STATIC_DIR, 'index.html')

    @app.route('/login')
    def serve_login():
        return send_from_directory(STATIC_DIR, 'index.html')

    print(f"前端静态文件目录: {STATIC_DIR}")
else:
    print(f"警告: 前端构建目录不存在 ({STATIC_DIR})，仅提供API服务")

if __name__ == '__main__':
    if not os.path.exists(app.config['DATABASE']):
        print("差异化CRM数据库不存在，正在初始化...")
        init_database()
        print("数据库初始化完成")
    else:
        # 即使数据库已存在，也检查认证表
        init_auth_tables()
    
    port = int(os.environ.get('PORT', 5002))
    print(f"启动差异化CRM系统，端口: {port}")
    print(f"访问地址: http://0.0.0.0:{port}")
    print(f"默认账户: admin/admin123")
    
    app.run(host='0.0.0.0', port=port, debug=True)
