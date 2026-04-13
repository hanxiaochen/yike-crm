-- CRM系统数据库架构
-- 版本：1.0
-- 创建时间：2026-03-09

-- 客户单位表
CREATE TABLE IF NOT EXISTS customer_organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, -- 客户单位名称
    type TEXT NOT NULL CHECK(type IN ('final_customer', 'partner', 'undecided')), -- 客户类型：最终客户、合作伙伴、待定
    industry TEXT, -- 所属行业
    scale TEXT CHECK(scale IN ('small', 'medium', 'large', 'enterprise')), -- 规模
    address TEXT, -- 地址
    phone TEXT, -- 联系电话
    email TEXT, -- 邮箱
    invoice_info TEXT, -- 开票信息
    tax_number TEXT, -- 税号
    bank_account TEXT, -- 银行账户
    potential_score INTEGER DEFAULT 0, -- 潜力评分
    classification TEXT, -- 客户分类
    tags TEXT, -- 标签，JSON格式存储
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL, -- 创建人
    notes TEXT -- 备注
);

-- 联系人表
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL, -- 所属客户单位ID
    name TEXT NOT NULL, -- 联系人姓名
    position TEXT, -- 职位
    phone TEXT, -- 联系电话
    email TEXT, -- 邮箱
    is_alumni BOOLEAN DEFAULT FALSE, -- 是否是校友
    alumni_info TEXT, -- 校友信息（JSON格式）
    other_info TEXT, -- 其他信息
    is_primary BOOLEAN DEFAULT FALSE, -- 是否为主要联系人
    tags TEXT, -- 标签，JSON格式
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE
);

-- 客户关系维护记录
CREATE TABLE IF NOT EXISTS customer_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    contact_id INTEGER, -- 相关联系人
    communication_type TEXT NOT NULL CHECK(communication_type IN ('call', 'meeting', 'email', 'wechat', 'other')),
    communication_date DATE NOT NULL,
    summary TEXT NOT NULL, -- 沟通摘要
    details TEXT, -- 详细记录
    follow_up_plan TEXT, -- 跟进计划
    follow_up_date DATE, -- 跟进日期
    satisfaction_score INTEGER CHECK(satisfaction_score >= 1 AND satisfaction_score <= 5), -- 满意度评分
    recorded_by TEXT NOT NULL, -- 记录人
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL
);

-- 销售机会表
CREATE TABLE IF NOT EXISTS sales_opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    opportunity_name TEXT NOT NULL, -- 机会名称
    source TEXT, -- 来源
    stage TEXT NOT NULL CHECK(stage IN ('initial', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost')), -- 阶段
    estimated_amount DECIMAL(15,2), -- 预计成交金额
    estimated_close_date DATE, -- 预计成交日期
    probability INTEGER CHECK(probability >= 0 AND probability <= 100), -- 成交概率
    priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'urgent')), -- 优先级
    assigned_to TEXT NOT NULL DEFAULT '韩晓晨', -- 分配给
    tags TEXT, -- 标签
    description TEXT, -- 描述
    requirements TEXT, -- 客户需求
    competitors TEXT, -- 竞争对手
    win_reason TEXT, -- 赢单原因（如果成交）
    loss_reason TEXT, -- 丢单原因（如果未成交）
    closed_date DATE, -- 关闭日期
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'closed', 'archived')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE
);

-- 销售机会跟进记录
CREATE TABLE IF NOT EXISTS opportunity_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL CHECK(activity_type IN ('call', 'meeting', 'email', 'demo', 'proposal', 'other')),
    activity_date DATETIME NOT NULL,
    summary TEXT NOT NULL,
    details TEXT,
    next_step TEXT,
    next_step_date DATE,
    recorded_by TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (opportunity_id) REFERENCES sales_opportunities(id) ON DELETE CASCADE
);

-- 合同管理表
CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id INTEGER, -- 关联的销售机会
    organization_id INTEGER NOT NULL,
    contract_number TEXT UNIQUE NOT NULL, -- 合同编号
    contract_name TEXT NOT NULL, -- 合同名称
    contract_amount DECIMAL(15,2) NOT NULL, -- 合同金额
    currency TEXT DEFAULT 'CNY', -- 货币
    start_date DATE, -- 开始日期
    end_date DATE, -- 结束日期
    duration_months INTEGER, -- 合同期限（月）
    contract_type TEXT, -- 合同类型
    status TEXT NOT NULL CHECK(status IN ('draft', 'pending_approval', 'approved', 'active', 'completed', 'terminated', 'renewed')),
    approval_workflow TEXT, -- 审批流程
    signed_date DATE, -- 签署日期
    termination_reason TEXT, -- 终止原因
    renewal_date DATE, -- 续签日期
    contract_file_url TEXT, -- 合同文件URL
    terms_and_conditions TEXT, -- 条款条件
    tags TEXT, -- 标签
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (opportunity_id) REFERENCES sales_opportunities(id) ON DELETE SET NULL,
    FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE
);

-- 发票管理表
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    organization_id INTEGER NOT NULL,
    invoice_number TEXT UNIQUE NOT NULL, -- 发票编号
    invoice_date DATE NOT NULL, -- 开票日期
    due_date DATE, -- 到期日期
    amount DECIMAL(15,2) NOT NULL, -- 发票金额
    tax_amount DECIMAL(15,2), -- 税额
    total_amount DECIMAL(15,2) NOT NULL, -- 总金额
    currency TEXT DEFAULT 'CNY', -- 货币
    status TEXT NOT NULL CHECK(status IN ('draft', 'sent', 'paid', 'overdue', 'cancelled')), -- 状态
    payment_date DATE, -- 支付日期
    payment_method TEXT, -- 支付方式
    description TEXT, -- 描述
    sent_date DATE, -- 发送日期
    reminder_sent_date DATE, -- 提醒发送日期
    tags TEXT, -- 标签
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE,
    FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE
);

-- 应收应付管理表
CREATE TABLE IF NOT EXISTS financial_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK(type IN ('receivable', 'payable')), -- 应收/应付
    organization_id INTEGER NOT NULL,
    invoice_id INTEGER, -- 关联发票
    contract_id INTEGER, -- 关联合同
    transaction_date DATE NOT NULL, -- 交易日期
    due_date DATE NOT NULL, -- 到期日期
    amount DECIMAL(15,2) NOT NULL, -- 金额
    currency TEXT DEFAULT 'CNY', -- 货币
    status TEXT NOT NULL CHECK(status IN ('open', 'partial', 'paid', 'overdue', 'written_off')), -- 状态
    paid_amount DECIMAL(15,2) DEFAULT 0, -- 已支付金额
    balance DECIMAL(15,2) GENERATED ALWAYS AS (amount - paid_amount) STORED, -- 余额
    payment_date DATE, -- 支付日期
    payment_reference TEXT, -- 支付参考号
    description TEXT, -- 描述
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE SET NULL,
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE SET NULL
);

-- 客户活动记录表
CREATE TABLE IF NOT EXISTS customer_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL CHECK(activity_type IN ('market_event', 'purchase', 'service_request', 'training', 'other')),
    activity_date DATE NOT NULL,
    description TEXT NOT NULL,
    details TEXT,
    outcome TEXT, -- 结果
    value DECIMAL(15,2), -- 价值
    recorded_by TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE
);

-- 客户反馈表
CREATE TABLE IF NOT EXISTS customer_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    contact_id INTEGER,
    feedback_type TEXT CHECK(feedback_type IN ('complaint', 'suggestion', 'praise', 'question')),
    feedback_date DATE NOT NULL,
    content TEXT NOT NULL,
    priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'urgent')),
    status TEXT DEFAULT 'open' CHECK(status IN ('open', 'in_progress', 'resolved', 'closed')),
    resolution TEXT, -- 解决方案
    resolved_date DATE, -- 解决日期
    satisfaction_score INTEGER CHECK(satisfaction_score >= 1 AND satisfaction_score <= 5),
    recorded_by TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL
);

-- 客户满意度调查表
CREATE TABLE IF NOT EXISTS customer_surveys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    survey_date DATE NOT NULL,
    survey_type TEXT NOT NULL, -- 调查类型
    overall_score INTEGER CHECK(overall_score >= 1 AND overall_score <= 10), -- 总体评分
    product_score INTEGER CHECK(product_score >= 1 AND product_score <= 10), -- 产品评分
    service_score INTEGER CHECK(service_score >= 1 AND service_score <= 10), -- 服务评分
    support_score INTEGER CHECK(support_score >= 1 AND support_score <= 10), -- 支持评分
    comments TEXT, -- 意见
    improvement_suggestions TEXT, -- 改进建议
    follow_up_required BOOLEAN DEFAULT FALSE, -- 是否需要跟进
    follow_up_notes TEXT, -- 跟进记录
    recorded_by TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE
);

-- 客户流失分析表
CREATE TABLE IF NOT EXISTS customer_churn_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    churn_date DATE NOT NULL, -- 流失日期
    churn_reason TEXT NOT NULL, -- 流失原因
    churn_category TEXT CHECK(churn_category IN ('price', 'service', 'product', 'competition', 'other')), -- 流失类别
    estimated_value_loss DECIMAL(15,2), -- 估计价值损失
    win_back_strategy TEXT, -- 挽回策略
    win_back_status TEXT CHECK(win_back_status IN ('not_started', 'in_progress', 'successful', 'failed')), -- 挽回状态
    win_back_date DATE, -- 挽回日期
    analysis_notes TEXT, -- 分析笔记
    recorded_by TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE
);

-- 客户生命周期阶段表
CREATE TABLE IF NOT EXISTS customer_lifecycle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    stage TEXT NOT NULL CHECK(stage IN ('prospect', 'lead', 'customer', 'active', 'loyal', 'churned', 'reactivated')),
    stage_date DATE NOT NULL, -- 进入该阶段日期
    duration_days INTEGER, -- 在该阶段持续时间（天）
    value_score INTEGER CHECK(value_score >= 1 AND value_score <= 100), -- 价值评分
    next_stage_strategy TEXT, -- 下一阶段策略
    recorded_by TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE
);

-- 客户关系图谱表
CREATE TABLE IF NOT EXISTS customer_relationship_graph (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    related_organization_id INTEGER NOT NULL, -- 相关组织ID
    relationship_type TEXT NOT NULL CHECK(relationship_type IN ('parent', 'subsidiary', 'partner', 'competitor', 'supplier', 'customer')),
    strength INTEGER CHECK(strength >= 1 AND strength <= 10), -- 关系强度
    description TEXT, -- 描述
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (related_organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE
);

-- 索引创建
CREATE INDEX IF NOT EXISTS idx_customer_organizations_name ON customer_organizations(name);
CREATE INDEX IF NOT EXISTS idx_customer_organizations_type ON customer_organizations(type);
CREATE INDEX IF NOT EXISTS idx_customer_organizations_classification ON customer_organizations(classification);
CREATE INDEX IF NOT EXISTS idx_contacts_organization ON contacts(organization_id);
CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(name);
CREATE INDEX IF NOT EXISTS idx_sales_opportunities_organization ON sales_opportunities(organization_id);
CREATE INDEX IF NOT EXISTS idx_sales_opportunities_stage ON sales_opportunities(stage);
CREATE INDEX IF NOT EXISTS idx_sales_opportunities_assigned_to ON sales_opportunities(assigned_to);
CREATE INDEX IF NOT EXISTS idx_sales_opportunities_status ON sales_opportunities(status);
CREATE INDEX IF NOT EXISTS idx_contracts_organization ON contracts(organization_id);
CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status);
CREATE INDEX IF NOT EXISTS idx_invoices_contract ON invoices(contract_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_financial_transactions_type ON financial_transactions(type);
CREATE INDEX IF NOT EXISTS idx_financial_transactions_status ON financial_transactions(status);
CREATE INDEX IF NOT EXISTS idx_financial_transactions_organization ON financial_transactions(organization_id);

-- 触发器：更新时间戳
CREATE TRIGGER IF NOT EXISTS update_customer_organizations_timestamp 
AFTER UPDATE ON customer_organizations 
BEGIN
    UPDATE customer_organizations SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_contacts_timestamp 
AFTER UPDATE ON contacts 
BEGIN
    UPDATE contacts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_sales_opportunities_timestamp 
AFTER UPDATE ON sales_opportunities 
BEGIN
    UPDATE sales_opportunities SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_contracts_timestamp 
AFTER UPDATE ON contracts 
BEGIN
    UPDATE contracts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_invoices_timestamp 
AFTER UPDATE ON invoices 
BEGIN
    UPDATE invoices SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_financial_transactions_timestamp 
AFTER UPDATE ON financial_transactions 
BEGIN
    UPDATE financial_transactions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;