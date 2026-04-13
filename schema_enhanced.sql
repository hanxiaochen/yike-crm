-- 差异化CRM系统数据库架构
-- 针对网络安全公司优化
-- 版本：2.0
-- 创建时间：2026-03-10

-- ==================== 基础表（增强版） ====================

-- 客户单位表（增强版）
CREATE TABLE IF NOT EXISTS customer_organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, -- 客户单位名称
    type TEXT NOT NULL CHECK(type IN ('final_customer', 'partner', 'undecided', 'government', 'financial', 'energy', 'military')), -- 客户类型扩展
    industry TEXT, -- 所属行业
    scale TEXT CHECK(scale IN ('small', 'medium', 'large', 'enterprise', 'critical_infrastructure')), -- 规模（增加关键基础设施）
    security_level TEXT CHECK(security_level IN ('basic', 'standard', 'enhanced', 'classified')), -- 安全等级
    address TEXT, -- 地址
    phone TEXT, -- 联系电话
    email TEXT, -- 邮箱
    invoice_info TEXT, -- 开票信息
    tax_number TEXT, -- 税号
    bank_account TEXT, -- 银行账户
    
    -- 产品使用相关
    using_netshield BOOLEAN DEFAULT FALSE, -- 是否使用网盾
    netshield_version TEXT, -- 网盾版本
    netshield_license_expiry DATE, -- 网盾许可证到期日
    using_inoc BOOLEAN DEFAULT FALSE, -- 是否使用I-NOC
    inoc_modules TEXT, -- I-NOC使用模块（JSON格式）
    inoc_license_expiry DATE, -- I-NOC许可证到期日
    
    -- 评估指标
    potential_score INTEGER DEFAULT 0, -- 潜力评分
    health_score INTEGER DEFAULT 100, -- 客户健康度评分
    risk_level TEXT CHECK(risk_level IN ('low', 'medium', 'high', 'critical')), -- 风险等级
    classification TEXT, -- 客户分类
    tags TEXT, -- 标签，JSON格式存储
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL, -- 创建人
    notes TEXT -- 备注
);

-- ==================== 差异化功能表 ====================

-- 产品使用跟踪表
CREATE TABLE IF NOT EXISTS product_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    product_type TEXT NOT NULL CHECK(product_type IN ('netshield', 'inoc', 'other')),
    module_name TEXT, -- 模块名称
    usage_date DATE NOT NULL, -- 使用日期
    usage_count INTEGER DEFAULT 1, -- 使用次数
    active_users INTEGER, -- 活跃用户数
    performance_score INTEGER CHECK(performance_score >= 1 AND performance_score <= 5), -- 性能评分
    issues_reported INTEGER DEFAULT 0, -- 报告问题数
    support_tickets INTEGER DEFAULT 0, -- 支持工单数
    feature_requests TEXT, -- 功能请求（JSON格式）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE
);

-- 安全事件与日志表
CREATE TABLE IF NOT EXISTS security_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER,
    log_type TEXT NOT NULL CHECK(log_type IN ('access', 'modification', 'deletion', 'export', 'api_call', 'security_alert')),
    event_time DATETIME NOT NULL,
    user_id TEXT, -- 操作用户
    action_description TEXT NOT NULL, -- 操作描述
    resource_type TEXT, -- 资源类型（customer, contact, opportunity等）
    resource_id INTEGER, -- 资源ID
    ip_address TEXT, -- IP地址
    user_agent TEXT, -- 用户代理
    severity TEXT CHECK(severity IN ('info', 'warning', 'error', 'critical')),
    details TEXT, -- 详细日志（JSON格式）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE SET NULL
);

-- AI分析与洞察表
CREATE TABLE IF NOT EXISTS ai_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    insight_type TEXT NOT NULL CHECK(insight_type IN ('churn_risk', 'upsell_opportunity', 'cross_sell', 'health_alert', 'renewal_prediction')),
    generated_date DATE NOT NULL,
    confidence_score REAL CHECK(confidence_score >= 0 AND confidence_score <= 1), -- 置信度
    insight_text TEXT NOT NULL, -- 洞察描述
    recommended_actions TEXT, -- 推荐行动（JSON格式）
    priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'critical')),
    status TEXT DEFAULT 'new' CHECK(status IN ('new', 'reviewed', 'acted_upon', 'dismissed')),
    reviewed_by TEXT,
    reviewed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE
);

-- 自动化工作流表
CREATE TABLE IF NOT EXISTS workflow_automations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, -- 工作流名称
    trigger_type TEXT NOT NULL CHECK(trigger_type IN ('scheduled', 'event_based', 'condition_based')),
    trigger_condition TEXT, -- 触发条件（JSON格式）
    actions TEXT NOT NULL, -- 执行动作（JSON格式）
    enabled BOOLEAN DEFAULT TRUE,
    last_executed DATETIME,
    next_execution DATETIME,
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 系统集成配置表
CREATE TABLE IF NOT EXISTS integrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    integration_type TEXT NOT NULL CHECK(integration_type IN ('feishu', 'email', 'wechat', 'project_management', 'billing_system')),
    config_name TEXT NOT NULL, -- 配置名称
    config_data TEXT NOT NULL, -- 配置数据（JSON格式）
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'error')),
    last_sync DATETIME,
    sync_status TEXT,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==================== 工作流执行记录 ====================

CREATE TABLE IF NOT EXISTS workflow_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id INTEGER NOT NULL,
    execution_time DATETIME NOT NULL,
    trigger_event TEXT, -- 触发事件
    input_data TEXT, -- 输入数据（JSON格式）
    output_data TEXT, -- 输出数据（JSON格式）
    status TEXT CHECK(status IN ('success', 'failed', 'partial_success')),
    error_message TEXT,
    execution_duration_ms INTEGER, -- 执行耗时（毫秒）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflow_automations(id) ON DELETE CASCADE
);

-- ==================== 视图 ====================

-- 客户健康度视图
CREATE VIEW IF NOT EXISTS customer_health_view AS
SELECT 
    co.id,
    co.name,
    co.health_score,
    co.risk_level,
    co.using_netshield,
    co.using_inoc,
    -- 产品使用情况
    (SELECT COUNT(*) FROM product_usage pu WHERE pu.organization_id = co.id AND pu.product_type = 'netshield' AND pu.usage_date >= date('now', '-30 days')) as netshield_30d_usage,
    (SELECT COUNT(*) FROM product_usage pu WHERE pu.organization_id = co.id AND pu.product_type = 'inoc' AND pu.usage_date >= date('now', '-30 days')) as inoc_30d_usage,
    -- 未解决的AI洞察
    (SELECT COUNT(*) FROM ai_insights ai WHERE ai.organization_id = co.id AND ai.status = 'new' AND ai.priority IN ('high', 'critical')) as critical_insights,
    -- 最近的安全事件
    (SELECT COUNT(*) FROM security_logs sl WHERE sl.organization_id = co.id AND sl.severity IN ('error', 'critical') AND sl.event_time >= datetime('now', '-7 days')) as recent_security_events
FROM customer_organizations co;

-- ==================== 索引 ====================

-- 产品使用索引
CREATE INDEX IF NOT EXISTS idx_product_usage_org_date ON product_usage(organization_id, usage_date);
CREATE INDEX IF NOT EXISTS idx_product_usage_product ON product_usage(product_type, usage_date);

-- 安全日志索引
CREATE INDEX IF NOT EXISTS idx_security_logs_org_time ON security_logs(organization_id, event_time);
CREATE INDEX IF NOT EXISTS idx_security_logs_type_severity ON security_logs(log_type, severity, event_time);

-- AI洞察索引
CREATE INDEX IF NOT EXISTS idx_ai_insights_org_status ON ai_insights(organization_id, status, priority);
CREATE INDEX IF NOT EXISTS idx_ai_insights_type_date ON ai_insights(insight_type, generated_date);

-- 工作流索引
CREATE INDEX IF NOT EXISTS idx_workflow_next_execution ON workflow_automations(next_execution) WHERE enabled = TRUE;

-- ==================== 触发器 ====================

-- 自动更新客户健康度评分（示例触发器）
CREATE TRIGGER IF NOT EXISTS update_customer_health_score
AFTER INSERT ON product_usage
FOR EACH ROW
BEGIN
    UPDATE customer_organizations
    SET health_score = (
        -- 根据产品使用情况、问题报告等计算健康度
        100 
        - (SELECT COUNT(*) * 2 FROM product_usage WHERE organization_id = NEW.organization_id AND issues_reported > 0 AND usage_date >= date('now', '-30 days'))
        - (SELECT COUNT(*) * 5 FROM ai_insights WHERE organization_id = NEW.organization_id AND insight_type = 'churn_risk' AND status = 'new' AND priority = 'high')
    )
    WHERE id = NEW.organization_id;
END;