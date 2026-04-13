#!/usr/bin/env python3
"""
CRM系统同步工具
策略：仅AI管理CRM（端口5003）向其他两个CRM同步数据
冲突时以AI管理CRM为准
"""

import os
import sqlite3
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional

# ==================== 配置 ====================

class CRMConfig:
    """CRM系统配置"""
    
    # AI管理CRM (端口5003) - 主系统
    AI_MANAGER_DB_PATH = os.path.join(os.path.dirname(__file__), 'crm_ai_manager.db')
    AI_MANAGER_API_URL = "http://0.0.0.0:5003"
    AI_MANAGER_API_KEY = "ai-manager-api-key-change-me"
    
    # 差异化CRM (端口5002) - 网络安全专用
    ENHANCED_DB_PATH = os.path.join(os.path.dirname(__file__), 'crm_enhanced.db')
    ENHANCED_API_URL = "http://0.0.0.0:5002"
    ENHANCED_API_KEY = "default-api-key-change-in-production"
    
    # 传统CRM (端口5001) - 基础功能
    TRADITIONAL_DB_PATH = os.path.join(os.path.dirname(__file__), 'crm.db')
    TRADITIONAL_API_URL = "http://0.0.0.0:5001"
    # 传统CRM没有API密钥认证
    
    # 同步选项
    SYNC_CUSTOMERS = True  # 同步客户组织
    SYNC_CONTACTS = True   # 同步联系人
    SYNC_ON_CONFLICT = "ai_prevails"  # 冲突处理：ai_prevails（以AI为准），skip（跳过）
    DRY_RUN = False  # 干运行，只显示计划操作不执行

# ==================== 数据库工具 ====================

def get_db_connection(db_path: str) -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def dict_from_row(row) -> Optional[Dict]:
    """将SQLite行转换为字典"""
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}

# ==================== 字段映射配置 ====================

class FieldMappings:
    """字段映射配置"""
    
    # AI管理CRM → 差异化CRM 客户组织字段映射
    CUSTOMER_AI_TO_ENHANCED = {
        'id': 'id',  # ID可能不同，主要用于匹配
        'name': 'name',
        'type': 'type',
        'industry': 'industry',
        'scale': 'scale',
        'security_level': 'security_level',
        'address': 'address',
        'phone': 'phone',
        'email': 'email',
        'using_netshield': 'using_netshield',
        'netshield_version': 'netshield_version',
        'netshield_license_expiry': 'netshield_license_expiry',
        'using_inoc': 'using_inoc',
        'inoc_modules': 'inoc_modules',
        'inoc_license_expiry': 'inoc_license_expiry',
        'health_score': 'health_score',
        'potential_score': 'potential_score',
        'risk_level': 'risk_level',
        'notes': 'notes',
        'created_by': 'created_by'
    }
    
    # AI管理CRM → 传统CRM 客户组织字段映射
    CUSTOMER_AI_TO_TRADITIONAL = {
        'name': 'name',
        'type': 'type',
        'industry': 'industry',
        'scale': 'scale',
        'address': 'address',
        'phone': 'phone',
        'email': 'email',
        'potential_score': 'potential_score',
        'notes': 'notes',
        'created_by': 'created_by'
    }
    
    # AI管理CRM → 差异化CRM 联系人字段映射
    CONTACT_AI_TO_ENHANCED = {
        'id': 'id',
        'organization_id': 'organization_id',
        'name': 'name',
        'position': 'position',
        'phone': 'phone',
        'email': 'email',
        'is_primary': 'is_primary',
        'is_decision_maker': 'is_decision_maker',
        'recommended_by': 'notes'  # 差异化CRM可能没有recommended_by，存到notes
    }
    
    # AI管理CRM → 传统CRM 联系人字段映射
    CONTACT_AI_TO_TRADITIONAL = {
        'organization_id': 'organization_id',
        'name': 'name',
        'position': 'position',
        'phone': 'phone',
        'email': 'email',
        'is_primary': 'is_primary',
        'is_decision_maker': 'is_decision_maker'
    }

# ==================== 同步核心逻辑 ====================

class CRMSynchronizer:
    """CRM同步器"""
    
    def __init__(self, config: CRMConfig):
        self.config = config
        self.stats = {
            'customers_synced': 0,
            'contacts_synced': 0,
            'customers_updated': 0,
            'contacts_updated': 0,
            'customers_skipped': 0,
            'contacts_skipped': 0,
            'errors': 0
        }
    
    def sync_all(self):
        """执行完整同步"""
        print(f"🤖 开始CRM同步 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"同步策略: AI管理CRM → 其他两个CRM（冲突时以AI为准）")
        print(f"干运行模式: {'是' if self.config.DRY_RUN else '否'}")
        
        try:
            if self.config.SYNC_CUSTOMERS:
                print("\n📋 同步客户组织...")
                self.sync_customers()
            
            if self.config.SYNC_CONTACTS:
                print("\n👥 同步联系人...")
                self.sync_contacts()
            
            self.print_summary()
            
        except Exception as e:
            print(f"❌ 同步失败: {e}")
            self.stats['errors'] += 1
    
    def sync_customers(self):
        """同步客户组织"""
        # 从AI管理CRM获取所有客户
        ai_customers = self.get_ai_customers()
        
        if not ai_customers:
            print("AI管理CRM中没有客户数据")
            return
        
        print(f"从AI管理CRM获取到 {len(ai_customers)} 个客户")
        
        # 同步到差异化CRM
        print("\n同步到差异化CRM (端口5002)...")
        for customer in ai_customers:
            self.sync_customer_to_enhanced(customer)
        
        # 同步到传统CRM
        print("\n同步到传统CRM (端口5001)...")
        for customer in ai_customers:
            self.sync_customer_to_traditional(customer)
    
    def sync_contacts(self):
        """同步联系人"""
        # 从AI管理CRM获取所有联系人
        ai_contacts = self.get_ai_contacts()
        
        if not ai_contacts:
            print("AI管理CRM中没有联系人数据")
            return
        
        print(f"从AI管理CRM获取到 {len(ai_contacts)} 个联系人")
        
        # 同步到差异化CRM
        print("\n同步到差异化CRM (端口5002)...")
        for contact in ai_contacts:
            self.sync_contact_to_enhanced(contact)
        
        # 同步到传统CRM
        print("\n同步到传统CRM (端口5001)...")
        for contact in ai_contacts:
            self.sync_contact_to_traditional(contact)
    
    def get_ai_customers(self) -> List[Dict]:
        """从AI管理CRM获取客户列表"""
        try:
            conn = get_db_connection(self.config.AI_MANAGER_DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM customer_organizations ORDER BY id")
            rows = cursor.fetchall()
            
            customers = []
            for row in rows:
                customer = dict_from_row(row)
                
                # 处理JSON字段
                if customer.get('inoc_modules'):
                    try:
                        customer['inoc_modules'] = json.loads(customer['inoc_modules'])
                    except:
                        pass
                
                customers.append(customer)
            
            conn.close()
            return customers
            
        except Exception as e:
            print(f"❌ 获取AI管理CRM客户失败: {e}")
            return []
    
    def get_ai_contacts(self) -> List[Dict]:
        """从AI管理CRM获取联系人列表"""
        try:
            conn = get_db_connection(self.config.AI_MANAGER_DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM contacts ORDER BY id")
            rows = cursor.fetchall()
            
            contacts = []
            for row in rows:
                contact = dict_from_row(row)
                contacts.append(contact)
            
            conn.close()
            return contacts
            
        except Exception as e:
            print(f"❌ 获取AI管理CRM联系人失败: {e}")
            return []
    
    def find_customer_by_name(self, db_path: str, customer_name: str) -> Optional[Dict]:
        """在目标CRM中按名称查找客户"""
        try:
            conn = get_db_connection(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM customer_organizations WHERE name = ?", (customer_name,))
            row = cursor.fetchone()
            
            conn.close()
            return dict_from_row(row) if row else None
            
        except Exception as e:
            print(f"❌ 在目标CRM中查找客户失败: {e}")
            return None
    
    def find_contact_by_name_and_org(self, db_path: str, contact_name: str, org_id: int) -> Optional[Dict]:
        """在目标CRM中按名称和组织ID查找联系人"""
        try:
            conn = get_db_connection(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM contacts WHERE name = ? AND organization_id = ?", 
                          (contact_name, org_id))
            row = cursor.fetchone()
            
            conn.close()
            return dict_from_row(row) if row else None
            
        except Exception as e:
            print(f"❌ 在目标CRM中查找联系人失败: {e}")
            return None
    
    def sync_customer_to_enhanced(self, ai_customer: Dict):
        """同步客户到差异化CRM"""
        customer_name = ai_customer['name']
        
        # 查找目标CRM中是否已存在
        existing_customer = self.find_customer_by_name(self.config.ENHANCED_DB_PATH, customer_name)
        
        if existing_customer:
            # 客户已存在，检查是否需要更新
            if self.should_update_customer(ai_customer, existing_customer, 'enhanced'):
                print(f"  🔄 更新客户: {customer_name}")
                if not self.config.DRY_RUN:
                    self.update_customer_in_enhanced(ai_customer, existing_customer['id'])
                self.stats['customers_updated'] += 1
            else:
                print(f"  ⏭️ 跳过（数据相同）: {customer_name}")
                self.stats['customers_skipped'] += 1
        else:
            # 客户不存在，创建新客户
            print(f"  ✅ 创建新客户: {customer_name}")
            if not self.config.DRY_RUN:
                self.create_customer_in_enhanced(ai_customer)
            self.stats['customers_synced'] += 1
    
    def sync_customer_to_traditional(self, ai_customer: Dict):
        """同步客户到传统CRM"""
        customer_name = ai_customer['name']
        
        # 查找目标CRM中是否已存在
        existing_customer = self.find_customer_by_name(self.config.TRADITIONAL_DB_PATH, customer_name)
        
        if existing_customer:
            # 客户已存在，检查是否需要更新
            if self.should_update_customer(ai_customer, existing_customer, 'traditional'):
                print(f"  🔄 更新客户: {customer_name}")
                if not self.config.DRY_RUN:
                    self.update_customer_in_traditional(ai_customer, existing_customer['id'])
                self.stats['customers_updated'] += 1
            else:
                print(f"  ⏭️ 跳过（数据相同）: {customer_name}")
                self.stats['customers_skipped'] += 1
        else:
            # 客户不存在，创建新客户
            print(f"  ✅ 创建新客户: {customer_name}")
            if not self.config.DRY_RUN:
                self.create_customer_in_traditional(ai_customer)
            self.stats['customers_synced'] += 1
    
    def sync_contact_to_enhanced(self, ai_contact: Dict):
        """同步联系人到差异化CRM"""
        # 首先需要查找对应的客户ID
        org_id = ai_contact['organization_id']
        
        # 获取客户名称
        conn = get_db_connection(self.config.AI_MANAGER_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM customer_organizations WHERE id = ?", (org_id,))
        org_row = cursor.fetchone()
        conn.close()
        
        if not org_row:
            print(f"  ⚠️ 跳过联系人（组织不存在）: {ai_contact['name']}")
            return
        
        org_name = dict_from_row(org_row)['name']
        
        # 在目标CRM中查找组织
        target_org = self.find_customer_by_name(self.config.ENHANCED_DB_PATH, org_name)
        if not target_org:
            print(f"  ⚠️ 跳过联系人（组织未同步）: {ai_contact['name']} → {org_name}")
            return
        
        target_org_id = target_org['id']
        contact_name = ai_contact['name']
        
        # 查找目标CRM中是否已存在
        existing_contact = self.find_contact_by_name_and_org(
            self.config.ENHANCED_DB_PATH, contact_name, target_org_id
        )
        
        if existing_contact:
            # 联系人已存在，检查是否需要更新
            if self.should_update_contact(ai_contact, existing_contact, 'enhanced'):
                print(f"  🔄 更新联系人: {contact_name} ({org_name})")
                if not self.config.DRY_RUN:
                    self.update_contact_in_enhanced(ai_contact, existing_contact['id'], target_org_id)
                self.stats['contacts_updated'] += 1
            else:
                print(f"  ⏭️ 跳过（数据相同）: {contact_name} ({org_name})")
                self.stats['contacts_skipped'] += 1
        else:
            # 联系人不存在，创建新联系人
            print(f"  ✅ 创建新联系人: {contact_name} ({org_name})")
            if not self.config.DRY_RUN:
                self.create_contact_in_enhanced(ai_contact, target_org_id)
            self.stats['contacts_synced'] += 1
    
    def sync_contact_to_traditional(self, ai_contact: Dict):
        """同步联系人到传统CRM"""
        # 首先需要查找对应的客户ID
        org_id = ai_contact['organization_id']
        
        # 获取客户名称
        conn = get_db_connection(self.config.AI_MANAGER_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM customer_organizations WHERE id = ?", (org_id,))
        org_row = cursor.fetchone()
        conn.close()
        
        if not org_row:
            print(f"  ⚠️ 跳过联系人（组织不存在）: {ai_contact['name']}")
            return
        
        org_name = dict_from_row(org_row)['name']
        
        # 在目标CRM中查找组织
        target_org = self.find_customer_by_name(self.config.TRADITIONAL_DB_PATH, org_name)
        if not target_org:
            print(f"  ⚠️ 跳过联系人（组织未同步）: {ai_contact['name']} → {org_name}")
            return
        
        target_org_id = target_org['id']
        contact_name = ai_contact['name']
        
        # 查找目标CRM中是否已存在
        existing_contact = self.find_contact_by_name_and_org(
            self.config.TRADITIONAL_DB_PATH, contact_name, target_org_id
        )
        
        if existing_contact:
            # 联系人已存在，检查是否需要更新
            if self.should_update_contact(ai_contact, existing_contact, 'traditional'):
                print(f"  🔄 更新联系人: {contact_name} ({org_name})")
                if not self.config.DRY_RUN:
                    self.update_contact_in_traditional(ai_contact, existing_contact['id'], target_org_id)
                self.stats['contacts_updated'] += 1
            else:
                print(f"  ⏭️ 跳过（数据相同）: {contact_name} ({org_name})")
                self.stats['contacts_skipped'] += 1
        else:
            # 联系人不存在，创建新联系人
            print(f"  ✅ 创建新联系人: {contact_name} ({org_name})")
            if not self.config.DRY_RUN:
                self.create_contact_in_traditional(ai_contact, target_org_id)
            self.stats['contacts_synced'] += 1
    
    def should_update_customer(self, ai_customer: Dict, target_customer: Dict, target_type: str) -> bool:
        """检查是否需要更新客户数据"""
        # 简单策略：如果任何映射字段的值不同，则需要更新
        mappings = FieldMappings.CUSTOMER_AI_TO_ENHANCED if target_type == 'enhanced' else FieldMappings.CUSTOMER_AI_TO_TRADITIONAL
        
        for ai_field, target_field in mappings.items():
            if ai_field == 'id':
                continue
                
            ai_value = ai_customer.get(ai_field)
            target_value = target_customer.get(target_field)
            
            # 处理特殊字段
            if ai_field == 'inoc_modules' and isinstance(ai_value, (list, dict)):
                ai_value = json.dumps(ai_value, ensure_ascii=False)
            
            # 比较值
            if ai_value != target_value:
                return True
        
        return False
    
    def should_update_contact(self, ai_contact: Dict, target_contact: Dict, target_type: str) -> bool:
        """检查是否需要更新联系人数据"""
        mappings = FieldMappings.CONTACT_AI_TO_ENHANCED if target_type == 'enhanced' else FieldMappings.CONTACT_AI_TO_TRADITIONAL
        
        for ai_field, target_field in mappings.items():
            if ai_field == 'id' or ai_field == 'organization_id':
                continue
                
            ai_value = ai_contact.get(ai_field)
            target_value = target_contact.get(target_field)
            
            if ai_value != target_value:
                return True
        
        return False
    
    def create_customer_in_enhanced(self, ai_customer: Dict) -> bool:
        """在差异化CRM中创建客户"""
        try:
            conn = get_db_connection(self.config.ENHANCED_DB_PATH)
            cursor = conn.cursor()
            
            # 构建插入语句
            fields = []
            values = []
            placeholders = []
            
            for ai_field, target_field in FieldMappings.CUSTOMER_AI_TO_ENHANCED.items():
                if ai_field == 'id':
                    continue  # 跳过ID，让数据库自动生成
                    
                value = ai_customer.get(ai_field)
                
                # 处理特殊字段
                if ai_field == 'inoc_modules' and isinstance(value, (list, dict)):
                    value = json.dumps(value, ensure_ascii=False) if value else None
                
                if value is not None:
                    fields.append(target_field)
                    values.append(value)
                    placeholders.append('?')
            
            if not fields:
                conn.close()
                return False
            
            sql = f"INSERT INTO customer_organizations ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(sql, values)
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ 在差异化CRM中创建客户失败: {e}")
            self.stats['errors'] += 1
            return False
    
    def update_customer_in_enhanced(self, ai_customer: Dict, target_customer_id: int) -> bool:
        """在差异化CRM中更新客户"""
        try:
            conn = get_db_connection(self.config.ENHANCED_DB_PATH)
            cursor = conn.cursor()
            
            # 构建更新语句
            updates = []
            values = []
            
            for ai_field, target_field in FieldMappings.CUSTOMER_AI_TO_ENHANCED.items():
                if ai_field == 'id':
                    continue
                    
                value = ai_customer.get(ai_field)
                
                # 处理特殊字段
                if ai_field == 'inoc_modules' and isinstance(value, (list, dict)):
                    value = json.dumps(value, ensure_ascii=False) if value else None
                
                updates.append(f"{target_field} = ?")
                values.append(value)
            
            values.append(target_customer_id)  # WHERE条件
            
            sql = f"UPDATE customer_organizations SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(sql, values)
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ 在差异化CRM中更新客户失败: {e}")
            self.stats['errors'] += 1
            return False
    
    def create_customer_in_traditional(self, ai_customer: Dict) -> bool:
        """在传统CRM中创建客户"""
        try:
            conn = get_db_connection(self.config.TRADITIONAL_DB_PATH)
            cursor = conn.cursor()
            
            # 构建插入语句
            fields = []
            values = []
            placeholders = []
            
            for ai_field, target_field in FieldMappings.CUSTOMER_AI_TO_TRADITIONAL.items():
                value = ai_customer.get(ai_field)
                
                if value is not None:
                    fields.append(target_field)
                    values.append(value)
                    placeholders.append('?')
            
            if not fields:
                conn.close()
                return False
            
            sql = f"INSERT INTO customer_organizations ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(sql, values)
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ 在传统CRM中创建客户失败: {e}")
            self.stats['errors'] += 1
            return False
    
    def update_customer_in_traditional(self, ai_customer: Dict, target_customer_id: int) -> bool:
        """在传统CRM中更新客户"""
        try:
            conn = get_db_connection(self.config.TRADITIONAL_DB_PATH)
            cursor = conn.cursor()
            
            # 构建更新语句
            updates = []
            values = []
            
            for ai_field, target_field in FieldMappings.CUSTOMER_AI_TO_TRADITIONAL.items():
                value = ai_customer.get(ai_field)
                
                updates.append(f"{target_field} = ?")
                values.append(value)
            
            values.append(target_customer_id)  # WHERE条件
            
            sql = f"UPDATE customer_organizations SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(sql, values)
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ 在传统CRM中更新客户失败: {e}")
            self.stats['errors'] += 1
            return False
    
    def create_contact_in_enhanced(self, ai_contact: Dict, target_org_id: int) -> bool:
        """在差异化CRM中创建联系人"""
        try:
            conn = get_db_connection(self.config.ENHANCED_DB_PATH)
            cursor = conn.cursor()
            
            # 检查contacts表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contacts'")
            if not cursor.fetchone():
                print("  ⚠️ 差异化CRM中没有contacts表，跳过联系人同步")
                conn.close()
                return False
            
            # 构建插入语句
            fields = ['organization_id']
            values = [target_org_id]
            placeholders = ['?']
            
            for ai_field, target_field in FieldMappings.CONTACT_AI_TO_ENHANCED.items():
                if ai_field in ['id', 'organization_id']:
                    continue
                    
                value = ai_contact.get(ai_field)
                
                if value is not None:
                    fields.append(target_field)
                    values.append(value)
                    placeholders.append('?')
            
            sql = f"INSERT INTO contacts ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(sql, values)
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ 在差异化CRM中创建联系人失败: {e}")
            self.stats['errors'] += 1
            return False
    
    def update_contact_in_enhanced(self, ai_contact: Dict, target_contact_id: int, target_org_id: int) -> bool:
        """在差异化CRM中更新联系人"""
        try:
            conn = get_db_connection(self.config.ENHANCED_DB_PATH)
            cursor = conn.cursor()
            
            # 构建更新语句
            updates = []
            values = []
            
            for ai_field, target_field in FieldMappings.CONTACT_AI_TO_ENHANCED.items():
                if ai_field in ['id', 'organization_id']:
                    continue
                    
                value = ai_contact.get(ai_field)
                
                updates.append(f"{target_field} = ?")
                values.append(value)
            
            values.append(target_contact_id)  # WHERE条件
            
            sql = f"UPDATE contacts SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(sql, values)
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ 在差异化CRM中更新联系人失败: {e}")
            self.stats['errors'] += 1
            return False
    
    def create_contact_in_traditional(self, ai_contact: Dict, target_org_id: int) -> bool:
        """在传统CRM中创建联系人"""
        try:
            conn = get_db_connection(self.config.TRADITIONAL_DB_PATH)
            cursor = conn.cursor()
            
            # 检查contacts表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contacts'")
            if not cursor.fetchone():
                print("  ⚠️ 传统CRM中没有contacts表，跳过联系人同步")
                conn.close()
                return False
            
            # 构建插入语句
            fields = ['organization_id']
            values = [target_org_id]
            placeholders = ['?']
            
            for ai_field, target_field in FieldMappings.CONTACT_AI_TO_TRADITIONAL.items():
                if ai_field in ['id', 'organization_id']:
                    continue
                    
                value = ai_contact.get(ai_field)
                
                if value is not None:
                    fields.append(target_field)
                    values.append(value)
                    placeholders.append('?')
            
            sql = f"INSERT INTO contacts ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(sql, values)
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ 在传统CRM中创建联系人失败: {e}")
            self.stats['errors'] += 1
            return False
    
    def update_contact_in_traditional(self, ai_contact: Dict, target_contact_id: int, target_org_id: int) -> bool:
        """在传统CRM中更新联系人"""
        try:
            conn = get_db_connection(self.config.TRADITIONAL_DB_PATH)
            cursor = conn.cursor()
            
            # 构建更新语句
            updates = []
            values = []
            
            for ai_field, target_field in FieldMappings.CONTACT_AI_TO_TRADITIONAL.items():
                if ai_field in ['id', 'organization_id']:
                    continue
                    
                value = ai_contact.get(ai_field)
                
                updates.append(f"{target_field} = ?")
                values.append(value)
            
            values.append(target_contact_id)  # WHERE条件
            
            sql = f"UPDATE contacts SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(sql, values)
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ 在传统CRM中更新联系人失败: {e}")
            self.stats['errors'] += 1
            return False
    
    def print_summary(self):
        """打印同步摘要"""
        print(f"\n{'='*60}")
        print("📊 同步完成摘要")
        print(f"{'='*60}")
        
        print(f"📋 客户同步:")
        print(f"  新同步: {self.stats['customers_synced']}")
        print(f"  已更新: {self.stats['customers_updated']}")
        print(f"  已跳过: {self.stats['customers_skipped']}")
        
        print(f"\n👥 联系人同步:")
        print(f"  新同步: {self.stats['contacts_synced']}")
        print(f"  已更新: {self.stats['contacts_updated']}")
        print(f"  已跳过: {self.stats['contacts_skipped']}")
        
        if self.stats['errors'] > 0:
            print(f"\n⚠️  错误: {self.stats['errors']}")
        
        print(f"\n⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

# ==================== 命令行接口 ====================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='CRM系统同步工具')
    parser.add_argument('--dry-run', action='store_true', help='干运行模式，只显示计划操作')
    parser.add_argument('--sync-customers', action='store_true', default=True, help='同步客户组织（默认启用）')
    parser.add_argument('--no-customers', action='store_false', dest='sync_customers', help='不同步客户组织')
    parser.add_argument('--sync-contacts', action='store_true', default=True, help='同步联系人（默认启用）')
    parser.add_argument('--no-contacts', action='store_false', dest='sync_contacts', help='不同步联系人')
    parser.add_argument('--conflict', choices=['ai_prevails', 'skip'], default='ai_prevails', 
                       help='冲突处理策略：ai_prevails（以AI为准，默认），skip（跳过）')
    
    args = parser.parse_args()
    
    # 配置同步器
    config = CRMConfig()
    config.DRY_RUN = args.dry_run
    config.SYNC_CUSTOMERS = args.sync_customers
    config.SYNC_CONTACTS = args.sync_contacts
    config.SYNC_ON_CONFLICT = args.conflict
    
    # 执行同步
    synchronizer = CRMSynchronizer(config)
    synchronizer.sync_all()
    
    # 提示下次使用方式
    print(f"\n💡 下次同步使用:")
    print(f"  python crm_sync_tool.py [选项]")
    print(f"\n选项:")
    print(f"  --dry-run       干运行模式")
    print(f"  --no-customers  不同步客户")
    print(f"  --no-contacts   不同步联系人")
    print(f"  --conflict skip 冲突时跳过（默认: ai_prevails）")
    
    # 建议设置定时任务
    print(f"\n🕐 建议设置定时同步:")
    print(f"  # 每小时同步一次")
    print(f"  0 * * * * cd /root/.openclaw/workspace/crm && python3 crm_sync_tool.py")