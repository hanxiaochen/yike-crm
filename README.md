# 易客CRM系统

一款简洁实用的客户关系管理系统，采用 Flask + Vue3 技术栈开发。

> **截图预览** 
> <img width="2304" height="1060" alt="image" src="https://github.com/user-attachments/assets/05261bc1-b804-4c12-9da6-a3a9b6eed7e5" />
<img width="4608" height="2120" alt="fd48d09b-1f51-4294-b32b-f3c24d46ddd2" src="https://github.com/user-attachments/assets/fa58a8d2-aa0c-422b-824a-afb2933e28be" />
<img width="2304" height="1060" alt="image" src="https://github.com/user-attachments/assets/a2fac9a0-cc14-4d63-8fd2-9aaa9dd6267d" />
<img width="2304" height="1060" alt="image" src="https://github.com/user-attachments/assets/f247d5f7-52f9-4834-8d90-59b745421496" />
<img width="2304" height="1060" alt="image" src="https://github.com/user-attachments/assets/4e62c258-922b-4b57-8b0f-57297a6d3b80" />
<img width="2304" height="1060" alt="image" src="https://github.com/user-attachments/assets/e6f88e5f-6e2c-4f80-b560-7a551e242f17" />


---

## 功能模块详解

### 1. 数据分析仪表盘

数据分析仪表盘提供企业运营的全景视图，帮助管理者快速掌握业务状况。

**核心功能：**
- 📊 **销售概况** - 今日销售额、本月销售额、同比增长率
- 📈 **业绩趋势** - 折线图展示月度销售额变化趋势
- 🥧 **业务分布** - 饼图展示客户行业分布、销售阶段分布
- 🏆 **业绩排行** - 团队或个人业绩排名
- 📋 **待办事项** - 近期需要跟进的销售机会和合同

**适用场景：** 管理层每日晨会、销售周报生成、业务决策数据支持

---

### 2. 客户管理

客户是企业的核心资产，客户管理模块帮助您系统化地管理和维护客户关系。

**核心功能：**
- ➕ **客户添加** - 支持批量导入客户信息
- 🔍 **客户搜索** - 支持按名称、行业、标签等多维度搜索
- 🏷️ **客户分类** - 按行业、规模、价值等维度分类管理
- 📝 **客户标签** - 灵活打标签，支持自定义标签类型
- 📜 **跟进记录** - 记录每次客户沟通内容
- 📊 **客户分析** - 查看客户价值、活跃度等分析数据

**字段说明：**
| 字段 | 说明 | 必填 |
|------|------|------|
| 客户名称 | 企业/单位全称 | ✅ |
| 行业 | 客户所属行业分类 | ✅ |
| 规模 | 企业规模（大型/中型/小型） | - |
| 价值评级 | VIP/A/B/C 级客户 | - |
| 地址 | 企业办公地址 | - |
| 备注 | 其他补充信息 | - |

**适用场景：** 客户信息集中管理、销售团队客户分配、客户服务记录

---

### 3. 联系人管理

每个客户可能有多个联系人，联系人管理帮助您精细化管理决策链。

**核心功能：**
- 👤 **联系人档案** - 姓名、职位、性别、生日、邮箱、电话
- 🔗 **关联客户** - 一个联系人只能属于一个客户单位
- 💼 **决策定位** - 标记是否为决策人、关键影响人
- 📱 **快速拨号** - 一键拨打联系人电话
- 📧 **邮件发送** - 快速发送邮件（需配置邮件服务）
- 📅 **跟进提醒** - 设置联系人的跟进提醒

**字段说明：**
| 字段 | 说明 | 必填 |
|------|------|------|
| 姓名 | 联系人姓名 | ✅ |
| 客户 | 所属客户单位 | ✅ |
| 部门 | 所在部门 | - |
| 职位 | 担任职务 | - |
| 电话 | 手机/座机 | ✅ |
| 邮箱 | 电子邮箱 | - |
| 决策链 | 决策人/影响人/执行人 | - |

**适用场景：** 销售跟进联系人管理、项目对接人记录、关键决策人维护

---

### 4. 销售机会管理

销售机会（商机）管理是销售过程管理的核心，帮助团队跟踪从线索到成交的完整路径。

**核心功能：**
- 💰 **机会创建** - 录入销售机会基本信息
- 📍 **销售阶段** - 线索→初步接触→需求确认→方案报价→合同签订→成交
- 💵 **金额管理** - 预估金额、实际成交金额
- 📅 **预计成交日期** - 设置预期成交时间
- 📊 **赢单率评估** - 系统根据阶段自动计算赢单概率
- 🔄 **阶段流转** - 拖拽即可更新销售阶段
- 📉 **丢单原因** - 记录丢单原因，分析改进

**销售阶段说明：**
| 阶段 | 赢单率 | 说明 |
|------|--------|------|
| 线索 | 10% | 刚获得的潜在客户信息 |
| 初步接触 | 20% | 已进行首次沟通 |
| 需求确认 | 40% | 已明确客户需求 |
| 方案报价 | 60% | 已发送方案或报价 |
| 合同签订 | 80% | 商务谈判阶段 |
| 成交 | 100% | 合同已签署 |

**适用场景：** 销售过程可视化、业绩预测、团队销售管理

---

### 5. 合同管理

合同管理模块帮助您系统化管理销售合同，确保合同执行可追溯。

**核心功能：**
- 📄 **合同信息** - 合同编号、名称、类型
- 💵 **金额管理** - 合同总金额、已收款、未收款
- 📅 **日期跟踪** - 签订日期、生效日期、到期日期
- 🔗 **关联机会** - 合同与销售机会关联
- 🏭 **供应商管理** - 关联合同供应商信息
- 📎 **合同附件** - 上传合同扫描件或PDF
- ⏰ **到期提醒** - 合同到期前自动提醒

**字段说明：**
| 字段 | 说明 | 必填 |
|------|------|------|
| 合同编号 | 唯一标识 | ✅ |
| 合同名称 | 项目/合同名称 | ✅ |
| 客户 | 所属客户 | ✅ |
| 商机 | 关联销售机会 | - |
| 供应商 | 合同供应商 | - |
| 签订日期 | 合同签订时间 | - |
| 开始日期 | 合同生效日期 | - |
| 结束日期 | 合同到期日期 | - |
| 合同金额 | 合同总金额 | - |
| 合同状态 | 履行中/已完成/已终止 | - |

**适用场景：** 合同文档电子化、收款进度跟踪、合同到期管理

---

### 6. 发票管理

发票管理模块帮助您追踪发票开具和付款状态，确保财务往来清晰。

**核心功能：**
- 🧾 **发票开具** - 记录发票抬头、金额、税率
- 💳 **付款状态** - 已付款/未付款/部分付款
- 📅 **付款日期** - 记录实际付款时间
- 🔗 **关联合同** - 发票与合同关联
- 📤 **发票影像** - 上传发票扫描件

**字段说明：**
| 字段 | 说明 | 必填 |
|------|------|------|
| 发票号码 | 发票编号 | ✅ |
| 客户 | 发票抬头客户 | ✅ |
| 合同 | 关联合同 | - |
| 发票金额 | 含税金额 | ✅ |
| 税率 | 税率（13%/6%/免税） | - |
| 开票日期 | 开具日期 | - |
| 付款状态 | 已付/未付/部分 | - |
| 付款日期 | 实际付款日期 | - |

**适用场景：** 财务对账、应收账款管理、税务申报支持

---

## 技术架构

### 后端
- **框架**：Flask（轻量级 Python Web 框架）
- **数据库**：SQLite（默认，支持 PostgreSQL/MySQL）
- **认证**：Token-based JWT 认证
- **API**：RESTful API 设计

### 前端
- **框架**：Vue 3 + Composition API
- **语言**：TypeScript（类型安全）
- **UI组件**：Element Plus（企业级组件库）
- **图表**：ECharts（数据可视化）
- **构建工具**：Vite（快速构建）
- **状态管理**：Pinia（新一代状态管理）

### 技术亮点
- 🎨 **响应式设计** - 支持桌面、平板、手机多端访问
- ⚡ **增量更新** - 数据变化无需刷新页面
- 🔄 **操作平滑** - 流畅的交互动效
- 🌙 **深色模式** - 支持深色/浅色主题切换

---

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- npm 或 pnpm

### 后端启动

```bash
# 克隆项目
git clone https://github.com/Mobisring/yike-crm.git
cd yike-crm

# 安装 Python 依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 启动后端服务
python app.py
```

后端服务默认运行在 http://localhost:5000

### 前端启动

```bash
cd crm-vue3

# 安装前端依赖
pnpm install

# 开发模式启动
pnpm dev
```

前端开发服务器默认运行在 http://localhost:5173

### 访问系统

1. 确保后端服务已启动（端口 5000）
2. 确保前端服务已启动（端口 5173）
3. 浏览器访问 http://localhost:5173
4. 使用默认管理员账号登录：`admin` / `admin123`

---

## 部署

### 生产环境部署

#### 1. 前端构建

```bash
cd crm-vue3
pnpm build
```

构建产物在 `dist` 目录，可部署到 Nginx/Apache 等 Web 服务器。

#### 2. 后端配置

```python
# app.py 中修改
DEBUG = False
SECRET_KEY = 'your-production-secret-key'
```

#### 3. Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/crm-vue3/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 4. systemd 服务（Linux）

```bash
# 复制服务文件
sudo cp crm.service /etc/systemd/system/

# 重新加载 systemd
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable crm

# 启动服务
sudo systemctl start crm

# 查看状态
sudo systemctl status crm
```

---

## 目录结构

```
yike-crm/
├── app.py                  # Flask 后端主应用
├── init_db.py              # 数据库初始化脚本
├── requirements.txt         # Python 依赖
├── schema.sql              # 数据库表结构定义
├── crm.db                  # SQLite 数据库文件
├── crm_launcher.py         # 多进程启动器
├── start_crm.sh            # Linux 一键启动脚本
├── crm.service             # systemd 服务文件
├── README.md               # 项目说明文档
├── LICENSE                 # MIT 开源协议
│
├── crm-vue3/               # Vue3 前端项目
│   ├── src/
│   │   ├── api/            # API 接口封装
│   │   ├── views/          # 页面组件
│   │   │   ├── dashboard/  # 仪表盘
│   │   │   ├── customer/    # 客户管理
│   │   │   ├── contact/     # 联系人管理
│   │   │   ├── opportunity/ # 销售机会
│   │   │   ├── contract/    # 合同管理
│   │   │   └── invoice/     # 发票管理
│   │   ├── components/     # 公共组件
│   │   ├── stores/         # Pinia 状态管理
│   │   └── router/         # 路由配置
│   ├── package.json
│   └── vite.config.ts
│
├── templates/               # Flask 模板目录
└── docs/                   # 文档目录
    └── screenshots/        # 系统截图
```

---

## 配置说明

### 数据库配置

默认使用 SQLite 数据库（`crm.db`），适合中小型企业。

如需切换 PostgreSQL 或 MySQL：

```python
# app.py
DATABASE = 'postgresql://user:password@localhost/crm'
# 或
DATABASE = 'mysql://user:password@localhost/crm'
```

### 端口配置

| 服务 | 默认端口 | 配置文件 |
|------|----------|----------|
| 后端 API | 5000 | app.py |
| 前端开发 | 5173 | vite.config.ts |

### 邮件配置（如需邮件通知）

```python
# app.py 中配置
MAIL_SERVER = 'smtp.example.com'
MAIL_PORT = 587
MAIL_USERNAME = 'your-email@example.com'
MAIL_PASSWORD = 'your-password'
```

---

## 安全建议

- 🔐 **修改默认密码** - 首次部署请立即修改 admin 默认密码
- 🌐 **启用 HTTPS** - 生产环境务必启用 HTTPS 加密传输
- 💾 **定期备份** - 定期备份数据库文件 `crm.db`
- 🚫 **限制访问** - 通过防火墙限制管理后台访问 IP
- 📝 **日志审计** - 定期检查操作日志

---

## 更新日志

### v1.0.0 (2026-04-13)
- ✅ 初始版本发布
- ✅ 客户管理模块
- ✅ 联系人管理模块
- ✅ 销售机会管理模块
- ✅ 合同管理模块
- ✅ 发票管理模块
- ✅ 数据分析仪表盘

---

## License

MIT License - 欢迎开源使用和二次开发
