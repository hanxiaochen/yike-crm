# CRM管理系统前端

基于 Vue3 Element Admin 框架构建的智能CRM管理系统

## 技术栈

- **Vue 3.5+** - 核心框架
- **Vite 5.x** - 构建工具
- **TypeScript 5.x** - 类型支持
- **Element Plus 2.9+** - UI组件库
- **Pinia 2.x** - 状态管理
- **Vue Router 4.x** - 路由管理
- **ECharts 5.5+** - 数据可视化
- **Axios** - HTTP客户端
- **dayjs** - 日期处理

## 项目结构

```
crm-vue3/
├── public/                 # 静态资源
├── src/
│   ├── api/               # API接口模块
│   │   ├── request.ts    # Axios封装
│   │   ├── auth.ts       # 认证接口
│   │   ├── customer.ts   # 客户管理
│   │   ├── contact.ts    # 联系人管理
│   │   ├── opportunity.ts # 商机管理
│   │   ├── contract.ts   # 合同管理
│   │   └── dashboard.ts  # 仪表盘
│   ├── assets/           # 资源文件
│   ├── components/        # 公共组件
│   ├── layouts/          # 布局组件
│   │   ├── index.vue     # 主布局
│   │   └── components/
│   │       ├── Sidebar.vue   # 侧边栏
│   │       ├── Navbar.vue    # 导航栏
│   │       ├── TagsView.vue  # 标签页
│   │       └── AppMain.vue   # 主内容区
│   ├── router/           # 路由配置
│   ├── store/            # 状态管理
│   ├── styles/           # 样式文件
│   ├── types/            # TypeScript类型
│   ├── utils/            # 工具函数
│   ├── views/            # 页面组件
│   │   ├── login/         # 登录页
│   │   ├── dashboard/     # 仪表盘
│   │   ├── customer/      # 客户管理
│   │   ├── contact/       # 联系人管理
│   │   ├── opportunity/   # 商机管理
│   │   ├── contract/      # 合同管理
│   │   ├── activity/      # 活动记录
│   │   ├── followup/      # 跟进管理
│   │   ├── statistics/    # 统计分析
│   │   ├── system/        # 系统管理
│   │   └── error/         # 错误页面
│   ├── App.vue
│   └── main.ts
├── .env.development     # 开发环境变量
├── .env.production      # 生产环境变量
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 功能模块

### 1. 仪表盘
- 核心业务数据统计卡片
- 商机漏斗图（ECharts）
- 销售趋势图
- 待办事项列表
- 近期活动时间线

### 2. 客户管理
- 客户列表（搜索、筛选、分页）
- 客户详情抽屉
- 新建/编辑客户
- 客户分类（重点/普通/低价值）
- 潜力评分

### 3. 联系人管理
- 联系人列表
- 快速拨号/邮件发送
- 关联客户查看
- 新建/编辑联系人

### 4. 商机管理
- **列表视图**：排序、筛选、分页
- **看板视图**：拖拽改变商机阶段
- 商机阶段：初步接触 → 资格确认 → 方案报价 → 合同签订 → 赢单/输单
- 成交概率进度条

### 5. 合同管理
- 合同列表
- 状态管理（草稿/待审批/已生效/执行中/已完成/已终止）
- 到期提醒
- 合同金额统计

### 6. 活动记录
- 时间线展示
- 活动类型筛选
- 日期范围筛选
- 记录活动

### 7. 待办跟进
- 统计卡片（待办/已过期/已完成/总计）
- Tab分类筛选
- 完成/未完成状态管理
- 优先级标记

### 8. 统计分析
- 核心指标统计卡片
- 商机漏斗分析
- 销售趋势图
- 客户行业分布饼图
- 团队业绩排名

### 9. 系统管理
- 用户管理（管理员/普通用户）
- 角色管理
- 权限配置

## 快速开始

### 安装依赖
```bash
cd crm-vue3
pnpm install
```

### 开发模式
```bash
pnpm dev
```

### 构建生产
```bash
pnpm build
```

### 预览生产
```bash
pnpm preview
```

## 后端接口

项目默认对接后端接口地址：`http://localhost:5000/api`

如需修改，编辑 `.env.development` 文件：
```
VITE_API_BASE_URL=http://localhost:5000/api
```

## 设计参考

- [Vue3 Element Admin](https://github.com/youlaitech/vue3-element-admin)
- [Element Plus](https://element-plus.org/)
- [ECharts](https://echarts.apache.org/)
