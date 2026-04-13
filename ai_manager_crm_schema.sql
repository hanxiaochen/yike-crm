-- AI管理的CRM系统数据库架构
-- AI作为核心管理者，负责决策和执行
-- 版本：3.0
-- 创建时间：2026-03-10

-- ==================== 核心管理表 ====================

-- AI代理表 - 每个AI代理负责不同管理职能
CREATE TABLE IF NOT EXISTS ai_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL, -- 代理名称
    role TEXT NOT NULL CHECK(role IN ('sales_manager', 'customer_success', 'relationship_manager', 'renewal_specialist', 'risk_analyst')),
    capabilities TEXT NOT NULL, -- 能力描述（JSON格式）
    authority_level TEXT NOT NULL CHECK(authority_level IN ('advisor', 'executor', 'decision_maker')), -- 权限级别
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- AI管理决策表
CREATE TABLE IF NOT EXISTS ai_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id TEXT UNIQUE NOT NULL, -- 决策ID（UUID格式）
    agent_id INTEGER NOT NULL, -- 负责的AI代理
    decision_type TEXT NOT NULL CHECK(decision_type IN ('customer_segmentation', 'opportunity_priority', 'engagement_strategy', 'renewal_action', 'risk_mitigation', 'resource_allocation')),
    target_entity_type TEXT NOT NULL CHECK(target_entity_type IN ('customer', 'contact', 'opportunity', 'contract')),
    target_entity_id INTEGER NOT NULL,
    decision_data TEXT NOT NULL, -- 决策详细数据（JSON格式）
    rationale TEXT NOT NULL, -- 决策理由
    confidence_score REAL CHECK(confidence_score >= 0 AND confidence_score <= 1), -- 置信度
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'executing', 'completed', 'rejected', 'cancelled')),
    approved_by TEXT, -- 批准人（如果是人机协同）
    approved_at DATETIME,
    execution_started_at DATETIME,
    execution_completed_at DATETIME,
    outcome TEXT, -- 执行结果
    performance_score REAL CHECK(performance_score >= 0 AND performance_score <= 1), -- 绩效评分
    feedback TEXT, -- 反馈信息
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES ai_agents(id) ON DELETE CASCADE
);

-- AI管理任务表
CREATE TABLE IF NOT EXISTS ai_managed_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT UNIQUE NOT NULL, -- 任务ID（UUID格式）
    decision_id INTEGER, -- 关联的决策
    agent_id INTEGER NOT NULL, -- 负责的AI代理
    task_type TEXT NOT NULL CHECK(task_type IN ('customer_outreach', 'opportunity_followup', 'renewal_reminder', 'risk_mitigation', 'data_collection', 'report_generation')),
    customer_id INTEGER NOT NULL,
    contact_id INTEGER, -- 相关联系人
    task_description TEXT NOT NULL, -- 任务描述
    expected_outcome TEXT, -- 预期结果
    priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'critical')),
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'scheduled', 'in_progress', 'completed', 'failed', 'cancelled')),
    scheduled_time DATETIME, -- 计划执行时间
    started_time DATETIME, -- 实际开始时间
    completed_time DATETIME, -- 完成时间
    execution_details TEXT, -- 执行详情（JSON格式）
    outcome_achieved TEXT, -- 实际达成结果
    success_score REAL CHECK(success_score >= 0 AND success_score <= 1), -- 成功评分
    next_action TEXT, -- 下一步行动
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (decision_id) REFERENCES ai_decisions(id) ON DELETE SET NULL,
    FOREIGN KEY (agent_id) REFERENCES ai_agents(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customer_organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL
);

-- AI沟通记录表
CREATE TABLE IF NOT EXISTS ai_communications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    communication_id TEXT UNIQUE NOT NULL, -- 沟通ID（UUID格式）
    task_id INTEGER, -- 关联的任务
    customer_id INTEGER NOT NULL,
    contact_id INTEGER,
    communication_type TEXT NOT NULL CHECK(communication_type IN ('email', 'wechat', 'phone_call', 'meeting', 'message')),
    direction TEXT NOT NULL CHECK(direction IN ('outbound', 'inbound')),
    subject TEXT, -- 主题
    content TEXT NOT NULL, -- 内容
    ai_generated BOOLEAN DEFAULT TRUE, -- 是否为AI生成
    sentiment_score REAL, -- 情感分析得分（-1到1）
    key_topics TEXT, -- 关键话题（JSON格式）
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_by TIMESTAMP,
    status TEXT DEFAULT 'sent' CHECK(status IN ('draft', 'sent', 'delivered', 'read', 'responded', 'failed')),
    response_received TEXT, -- 收到的回复
    response_analyzed BOOLEAN DEFAULT FALSE, -- 是否已分析回复
    analysis_result TEXT, -- 分析结果（JSON格式）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES ai_managed_tasks(id) ON DELETE SET NULL,
    FOREIGN KEY (customer_id) REFERENCES customer_organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL
);

-- ==================== AI学习与优化表 ====================

-- AI决策历史表
CREATE TABLE IF NOT EXISTS ai_decision_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id INTEGER NOT NULL,
    agent_id INTEGER NOT NULL,
    decision_type TEXT NOT NULL,
    action_taken TEXT NOT NULL, -- 采取的行动（JSON格式）
    expected_outcome TEXT, -- 预期结果
    actual_outcome TEXT, -- 实际结果
    outcome_match_score REAL CHECK(outcome_match_score >= 0 AND outcome_match_score <= 1), -- 结果匹配度
    effectiveness_score REAL CHECK(effectiveness_score >= 0 AND effectiveness_score <= 1), -- 有效性评分
    learning_points TEXT, -- 学习要点
    improved_strategy TEXT, -- 改进策略
    reviewed_by_ai BOOLEAN DEFAULT FALSE, -- 是否已被AI分析
    review_conclusions TEXT, -- 分析结论
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (decision_id) REFERENCES ai_decisions(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES ai_agents(id) ON DELETE CASCADE
);

-- AI策略库
CREATE TABLE IF NOT EXISTS ai_strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_name TEXT NOT NULL, -- 策略名称
    strategy_type TEXT NOT NULL CHECK(strategy_type IN ('customer_engagement', 'opportunity_conversion', 'renewal_optimization', 'risk_management', 'resource_allocation')),
    target_segment TEXT, -- 目标客户细分
    trigger_conditions TEXT NOT NULL, -- 触发条件（JSON格式）
    actions TEXT NOT NULL, -- 执行动作（JSON格式）
    success_criteria TEXT, -- 成功标准（JSON格式）
    effectiveness_score REAL DEFAULT 0 CHECK(effectiveness_score >= 0 AND effectiveness_score <= 1), -- 有效性评分
    usage_count INTEGER DEFAULT 0, -- 使用次数
    success_count INTEGER DEFAULT 0, -- 成功次数
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at DATETIME,
    created_by_agent_id INTEGER, -- 创建代理
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by_agent_id) REFERENCES ai_agents(id) ON DELETE SET NULL
);

-- AI性能评估表
CREATE TABLE IF NOT EXISTS ai_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL,
    evaluation_period TEXT NOT NULL, -- 评估周期（daily, weekly, monthly）
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- 决策指标
    decisions_made INTEGER DEFAULT 0, -- 决策数量
    decisions_approved INTEGER DEFAULT 0, -- 批准的决策
    decisions_completed INTEGER DEFAULT 0, -- 完成的决策
    avg_decision_confidence REAL DEFAULT 0, -- 平均决策置信度
    avg_decision_performance REAL DEFAULT 0, -- 平均决策绩效
    
    -- 任务指标
    tasks_created INTEGER DEFAULT 0, -- 创建任务数
    tasks_completed INTEGER DEFAULT 0, -- 完成任务数
    task_completion_rate REAL DEFAULT 0, -- 任务完成率
    avg_task_success_score REAL DEFAULT 0, -- 平均任务成功评分
    
    -- 沟通指标
    communications_sent INTEGER DEFAULT 0, -- 发送沟通数
    response_rate REAL DEFAULT 0, -- 回复率
    avg_sentiment_score REAL DEFAULT 0, -- 平均情感得分
    
    -- 业务成果指标
    opportunities_identified INTEGER DEFAULT 0, -- 识别机会数
    opportunities_converted INTEGER DEFAULT 0, -- 转化机会数
    renewals_secured INTEGER DEFAULT 0, -- 成功续约数
    risks_mitigated INTEGER DEFAULT 0, -- 缓解风险数
    customer_satisfaction_change REAL DEFAULT 0, -- 客户满意度变化
    
    -- 总体评分
    overall_performance_score REAL DEFAULT 0, -- 总体绩效评分
    performance_trend TEXT, -- 绩效趋势（improving, stable, declining）
    
    strengths TEXT, -- 优势分析
    improvement_areas TEXT, -- 改进领域
    action_plan TEXT, -- 行动计划
    
    evaluated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES ai_agents(id) ON DELETE CASCADE
);

-- ==================== 人机协同表 ====================

-- 人工干预表
CREATE TABLE IF NOT EXISTS human_interventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intervention_id TEXT UNIQUE NOT NULL, -- 干预ID
    decision_id INTEGER, -- 关联的决策
    task_id INTEGER, -- 关联的任务
    intervention_type TEXT NOT NULL CHECK(intervention_type IN ('approval', 'modification', 'override', 'guidance', 'feedback')),
    intervened_by TEXT NOT NULL, -- 干预人
    reason TEXT NOT NULL, -- 干预原因
    original_content TEXT, -- 原始内容（JSON格式）
    modified_content TEXT, -- 修改后内容（JSON格式）
    ai_learning_applied BOOLEAN DEFAULT FALSE, -- 是否已用于AI学习
    learning_outcome TEXT, -- 学习成果
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (decision_id) REFERENCES ai_decisions(id) ON DELETE SET NULL,
    FOREIGN KEY (task_id) REFERENCES ai_managed_tasks(id) ON DELETE SET NULL
);

-- AI建议采纳表
CREATE TABLE IF NOT EXISTS ai_recommendation_adoptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recommendation_id INTEGER NOT NULL,
    recommended_by_agent_id INTEGER NOT NULL, -- 推荐代理
    adopted_by TEXT NOT NULL, -- 采纳人
    adoption_date DATE NOT NULL,
    implementation_details TEXT, -- 实施详情
    results_achieved TEXT, -- 达成结果
    effectiveness_rating INTEGER CHECK(effectiveness_rating >= 1 AND effectiveness_rating <= 5), -- 有效性评分（1-5）
    feedback_for_ai TEXT, -- 给AI的反馈
    ai_learning_integrated BOOLEAN DEFAULT FALSE, -- 是否已集成到AI学习
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recommended_by_agent_id) REFERENCES ai_agents(id) ON DELETE CASCADE
);

-- ==================== 客户数据表（简化版，聚焦AI管理） ====================

-- 客户组织表（优化版）
CREATE TABLE IF NOT EXISTS customer_organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('final_customer', 'partner', 'government', 'financial', 'energy', 'military')),
    industry TEXT,
    scale TEXT CHECK(scale IN ('small', 'medium', 'large', 'enterprise', 'critical_infrastructure')),
    security_level TEXT CHECK(security_level IN ('basic', 'standard', 'enhanced', 'classified')),
    
    -- AI管理的关键字段
    ai_managed_segment TEXT, -- AI管理的客户细分
    ai_engagement_score REAL DEFAULT 0.5 CHECK(ai_engagement_score >= 0 AND ai_engagement_score <= 1), -- AI互动评分
    ai_relationship_stage TEXT DEFAULT 'new' CHECK(ai_relationship_stage IN ('new', 'developing', 'established', 'strategic', 'at_risk')),
    next_ai_interaction_type TEXT, -- 下一次AI互动类型
    next_ai_interaction_date DATE, -- 下一次AI互动日期
    ai_management_priority INTEGER DEFAULT 0, -- AI管理优先级
    
    -- 基础信息
    address TEXT,
    phone TEXT,
    email TEXT,
    
    -- 产品信息
    using_netshield BOOLEAN DEFAULT FALSE,
    netshield_version TEXT,
    netshield_license_expiry DATE,
    using_inoc BOOLEAN DEFAULT FALSE,
    inoc_modules TEXT,
    inoc_license_expiry DATE,
    
    -- 评分
    health_score INTEGER DEFAULT 100,
    potential_score INTEGER DEFAULT 0,
    risk_level TEXT DEFAULT 'low' CHECK(risk_level IN ('low', 'medium', 'high', 'critical')),
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT DEFAULT 'ai_manager' -- 默认由AI管理创建
);

-- 联系人表（AI管理优化）
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    position TEXT,
    phone TEXT,
    email TEXT,
    
    -- AI互动字段
    ai_preferred_channel TEXT CHECK(ai_preferred_channel IN ('email', 'wechat', 'phone', 'meeting', 'any')),
    ai_interaction_frequency INTEGER DEFAULT 0, -- AI互动频率
    last_ai_interaction DATE, -- 最后一次AI互动
    next_ai_interaction DATE, -- 下一次AI互动计划
    ai_relationship_score REAL DEFAULT 0.5, -- AI关系评分
    ai_communication_style TEXT, -- AI沟通风格偏好
    
    is_primary BOOLEAN DEFAULT FALSE,
    is_decision_maker BOOLEAN DEFAULT FALSE,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES customer_organizations(id) ON DELETE CASCADE
);

-- ==================== 视图 ====================

-- AI管理仪表盘视图
CREATE VIEW IF NOT EXISTS ai_management_dashboard AS
SELECT 
    -- 客户统计
    (SELECT COUNT(*) FROM customer_organizations) as total_customers,
    (SELECT COUNT(*) FROM customer_organizations WHERE ai_relationship_stage = 'at_risk') as at_risk_customers,
    (SELECT COUNT(*) FROM customer_organizations WHERE ai_management_priority > 0) as prioritized_customers,
    
    -- AI代理统计
    (SELECT COUNT(*) FROM ai_agents WHERE is_active = TRUE) as active_agents,
    (SELECT COUNT(DISTINCT agent_id) FROM ai_managed_tasks WHERE status = 'in_progress') as agents_busy,
    
    -- 任务统计
    (SELECT COUNT(*) FROM ai_managed_tasks WHERE status = 'pending') as pending_tasks,
    (SELECT COUNT(*) FROM ai_managed_tasks WHERE status = 'in_progress') as in_progress_tasks,
    (SELECT COUNT(*) FROM ai_managed_tasks WHERE status = 'completed' AND DATE(completed_time) = DATE('now')) as completed_today,
    
    -- 决策统计
    (SELECT COUNT(*) FROM ai_decisions WHERE status = 'pending') as pending_decisions,
    (SELECT COUNT(*) FROM ai_decisions WHERE status = 'executing') as executing_decisions,
    (SELECT AVG(confidence_score) FROM ai_decisions WHERE status = 'completed') as avg_decision_confidence,
    
    -- 沟通统计
    (SELECT COUNT(*) FROM ai_communications WHERE DATE(created_at) = DATE('now')) as communications_today,
    (SELECT AVG(sentiment_score) FROM ai_communications WHERE direction = 'inbound') as avg_response_sentiment,
    (SELECT COUNT(*) FROM ai_communications WHERE follow_up_required = TRUE AND follow_up_by <= DATETIME('now')) as overdue_followups
FROM customer_organizations LIMIT 1;

-- AI绩效概览视图
CREATE VIEW IF NOT EXISTS ai_performance_overview AS
SELECT 
    a.id as agent_id,
    a.agent_name,
    a.role,
    p.overall_performance_score,
    p.performance_trend,
    p.decisions_made,
    p.task_completion_rate,
    p.response_rate,
    p.opportunities_converted,
    p.evaluated_at
FROM ai_agents a
LEFT JOIN (
    SELECT agent_id, MAX(evaluated_at) as latest_eval
    FROM ai_performance 
    GROUP BY agent_id
) latest ON a.id = latest.agent_id
LEFT JOIN ai_performance p ON a.id = p.agent_id AND p.evaluated_at = latest.latest_eval
WHERE a.is_active = TRUE;

-- ==================== 索引 ====================

-- AI决策索引
CREATE INDEX IF NOT EXISTS idx_ai_decisions_agent_status ON ai_decisions(agent_id, status, created_at);
CREATE INDEX IF NOT EXISTS idx_ai_decisions_customer ON ai_decisions(target_entity_type, target_entity_id, decision_type);

-- AI任务索引
CREATE INDEX IF NOT EXISTS idx_ai_tasks_status_priority ON ai_managed_tasks(status, priority, scheduled_time);
CREATE INDEX IF NOT EXISTS idx_ai_tasks_customer_agent ON ai_managed_tasks(customer_id, agent_id, task_type);

-- 沟通索引
CREATE INDEX IF NOT EXISTS idx_ai_comms_customer_date ON ai_communications(customer_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_comms_followup ON ai_communications(follow_up_required, follow_up_by) WHERE follow_up_required = TRUE;

-- 性能索引
CREATE INDEX IF NOT EXISTS idx_ai_performance_agent_period ON ai_performance(agent_id, period_start DESC);

-- ==================== 触发器 ====================

-- 自动更新客户AI互动评分
CREATE TRIGGER IF NOT EXISTS update_customer_ai_score
AFTER INSERT ON ai_communications
FOR EACH ROW WHEN NEW.direction = 'inbound'
BEGIN
    UPDATE customer_organizations
    SET 
        ai_engagement_score = ai_engagement_score * 0.9 + 0.1, -- 互动增加评分
        last_ai_interaction = DATE('now')
    WHERE id = NEW.customer_id;
END;

-- 自动创建跟进任务（当沟通需要跟进时）
CREATE TRIGGER IF NOT EXISTS auto_create_followup_task
AFTER INSERT ON ai_communications
FOR EACH ROW WHEN NEW.follow_up_required = TRUE
BEGIN
    INSERT INTO ai_managed_tasks (
        task_id, agent_id, customer_id, contact_id, task_type, 
        task_description, priority, status, scheduled_time
    ) VALUES (
        'task_' || LOWER(HEX(RANDOMBLOB(8))) || '_' || STRFTIME('%Y%m%d_%H%M%S', 'now'),
        1, -- 默认分配给客户成功代理
        NEW.customer_id,
        NEW.contact_id,
        'customer_outreach',
        '跟进沟通：' || COALESCE(NEW.subject, '未回复沟通'),
        'medium',
        'scheduled',
        NEW.follow_up_by
    );
END;