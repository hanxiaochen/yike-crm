<template>
  <div class="invoice-page">
    <template v-if="!detailMode">
      <div class="search-bar">
        <div class="search-form">
          <el-input ref="searchInputRef" v-model="query.keyword" placeholder="搜索发票号/合同/客户..." clearable style="width: 260px" @clear="handleSearch" @keyup.enter="handleSearch">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="query.status" placeholder="发票状态" clearable style="width: 140px" @change="handleSearch">
            <el-option label="待开票" value="pending" />
            <el-option label="已开票" value="issued" />
            <el-option label="已作废" value="voided" />
          </el-select>
          <el-select v-model="query.payment_status" placeholder="付款状态" clearable style="width: 140px" @change="handleSearch">
            <el-option label="未付款" value="unpaid" />
            <el-option label="部分付款" value="partial" />
            <el-option label="已付清" value="paid" />
          </el-select>
        </div>
        <span class="search-shortcut-hint">按 / 聚焦搜索</span>
        <div class="action-buttons">
          <span v-if="selectedRows.length > 0" class="selected-info">已选择 {{ selectedRows.length }} 项</span>
          <el-button v-if="selectedRows.length > 0" type="danger" @click="handleBatchDelete"><el-icon><Delete /></el-icon>批量删除</el-button>
          <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon>新建发票</el-button>
        </div>
      </div>

      <div>
        <el-card shadow="never" class="table-card">
          <el-table v-loading="loading" :data="tableData" row-key="id" @selection-change="handleSelectionChange" table-layout="auto">
            <el-table-column type="selection" min-width="50" />
            <el-table-column prop="invoice_number" label="发票名称" min-width="120" sortable>
              <template #default="{ row }"><el-link type="primary" @click="handleView(row)">{{ row.invoice_number }}</el-link></template>
            </el-table-column>
            <el-table-column prop="org_name" label="客户" min-width="110" show-overflow-tooltip />
            <el-table-column prop="contract_name" label="合同" min-width="130" show-overflow-tooltip>
              <template #default="{ row }"><span>{{ row.contract_name || '—' }}</span></template>
            </el-table-column>
            <el-table-column prop="invoice_type" label="发票类型" min-width="100">
              <template #default="{ row }"><el-tag size="small">{{ row.invoice_type || '—' }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="total_amount" label="价税合计" min-width="120" sortable>
              <template #default="{ row }"><span class="amount-text">¥{{ row.total_amount?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span></template>
            </el-table-column>
            <el-table-column prop="billing_date" label="开票日期" min-width="100" />
            <el-table-column prop="payment_status" label="付款状态" min-width="100">
              <template #default="{ row }"><el-tag :type="getPaymentType(row.payment_status)" size="small">{{ getPaymentLabel(row.payment_status) }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="status" label="状态" min-width="90">
              <template #default="{ row }"><el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag></template>
            </el-table-column>
            <el-table-column label="操作" min-width="150">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleView(row)"><el-icon><View /></el-icon>查看</el-button>
                <el-button type="primary" link size="small" @click="handleEdit(row)"><el-icon><Edit /></el-icon>编辑</el-button>
                <el-popconfirm title="确定删除该发票？" @confirm="handleDelete(row)"><template #reference><el-button type="danger" link size="small"><el-icon><Delete /></el-icon>删除</el-button></template></el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-container">
            <el-pagination background layout="total, prev, pager, next, sizes, jumper" v-model:current-page="query.page" v-model:page-size="query.pageSize" :total="total" :page-sizes="[10, 20, 50, 100]" @current-change="fetchData" @size-change="handleSizeChange" />
          </div>
        </el-card>
      </div>
    </template>

    <template v-if="detailMode">
      <div class="detail-header">
        <el-page-header :content="isEdit ? '编辑发票' : '发票详情'" @back="handleBack">
          <template #extra>
            <template v-if="!isEdit"><el-button @click="handlePrintPreview">打印预览</el-button><el-button type="primary" @click="startEditFromDetail">编辑</el-button></template>
            <template v-else><el-button @click="handleCancel">取消</el-button><el-button type="primary" @click="handleSave" :loading="submitLoading">保存 <span style="font-size:11px;opacity:0.7;margin-left:4px;">⌘↵</span></el-button><span class="shortcut-hint">ESC 返回</span></template>
          </template>
        </el-page-header>
      </div>

      <el-card v-if="isEdit" shadow="never" style="margin-top: 20px;">
        <el-form ref="formRef" :model="form" label-width="110px">
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="发票名称"><el-input v-model="form.invoice_number" placeholder="请输入发票名称" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="发票类型"><el-select v-model="form.invoice_type" placeholder="请选择类型" style="width:100%"><el-option label="增值税专用发票" value="增值税专用发票" /><el-option label="增值税普通发票" value="增值税普通发票" /><el-option label="电子发票" value="电子发票" /><el-option label="收据" value="收据" /></el-select></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="客户"><el-select v-model="form.organization_id" placeholder="请选择客户" style="width:100%" filterable clearable @change="handleOrgChange"><el-option v-for="org in orgOptions" :key="org.id" :label="org.name" :value="org.id" /></el-select></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="关联合同"><el-select v-model="form.contract_id" placeholder="请选择合同" style="width:100%" filterable clearable @change="handleContractChange"><el-option v-for="c in contractOptions" :key="c.id" :label="c.contract_name" :value="c.id" /></el-select></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="价税合计"><el-input v-model="totalAmountDisplay" placeholder="自动计算" style="width:100%" readonly /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="已付款"><el-input v-model="paidAmountDisplay" placeholder="请输入已付款金额" style="width:100%" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="付款状态"><el-select v-model="form.payment_status" style="width:100%"><el-option label="未付款" value="unpaid" /><el-option label="部分付款" value="partial" /><el-option label="已付清" value="paid" /></el-select></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="开票日期"><el-date-picker v-model="form.billing_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="发票状态"><el-select v-model="form.status" style="width:100%"><el-option label="待开票" value="pending" /><el-option label="已开票" value="issued" /><el-option label="已作废" value="voided" /></el-select></el-form-item></el-col>
          </el-row>
          <el-form-item label="备注"><el-input v-model="form.notes" type="textarea" :rows="2" placeholder="请输入备注" /></el-form-item>
          <!-- 开票信息 -->
          <el-divider content-position="center"><span style="font-weight: 600; color: #303133;">开票信息</span></el-divider>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="发票抬头"><el-input v-model="form.invoice_title" placeholder="请输入发票抬头" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="税号"><el-input v-model="form.tax_number" placeholder="请输入税号" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="开户行"><el-input v-model="form.bank_name" placeholder="请输入开户行" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="银行账号"><el-input v-model="form.bank_account" placeholder="请输入银行账号" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="地址"><el-input v-model="form.invoice_address" placeholder="请输入地址" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="电话"><el-input v-model="form.invoice_phone" placeholder="请输入电话" /></el-form-item></el-col>
          </el-row>
        </el-form>

        <!-- 发票明细 -->
        <el-divider content-position="center"><span style="font-weight: 600; color: #303133;">发票明细</span></el-divider>
        
        <!-- 预览对话框 -->
        <el-table :data="invoiceItems" border style="margin-bottom: 12px;" show-summary :summary-method="customSummary">
          <el-table-column prop="item_name" label="项目名称" min-width="150">
            <template #default="{ row, $index }">
              <el-input v-model="row.item_name" placeholder="请输入项目名称" />
            </template>
          </el-table-column>
          <el-table-column prop="spec_model" label="规格型号" min-width="120">
            <template #default="{ row }">
              <el-input v-model="row.spec_model" placeholder="请输入规格型号" />
            </template>
          </el-table-column>
          <el-table-column prop="unit" label="单位" min-width="80">
            <template #default="{ row }">
              <el-input v-model="row.unit" placeholder="如：项、台、套" />
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" min-width="120">
            <template #default="{ row, $index }">
              <el-input v-model="row._quantityDisplay" placeholder="0.00" size="small" @input="onQuantityInput($event, $index)" @blur="onQuantityBlur($index)" />
            </template>
          </el-table-column>
          <el-table-column prop="tax_included_amount" label="含税金额" min-width="150">
            <template #default="{ row, $index }">
              <el-input v-model="row._taxIncludedDisplay" placeholder="0" size="small" @blur="onTaxIncludedBlur($index)" />
            </template>
          </el-table-column>
          <el-table-column prop="unit_price" label="单价" min-width="120">
            <template #default="{ row }">
              <span class="calc-field">{{ formatNumberFull(row?.unit_price) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="amount" label="金额" min-width="140">
            <template #default="{ row }">
              <span class="calc-field">{{ fixed2(row?.amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="tax_rate" label="税率" min-width="80">
            <template #default="{ row, $index }">
              <el-select v-model="row.tax_rate" size="small" style="width:100%" @change="onTaxRateChange($index)">
                <el-option label="6%" :value="0.06" />
                <el-option label="13%" :value="0.13" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="tax_amount" label="税额" min-width="120">
            <template #default="{ row }">
              <span class="calc-field">{{ fixed2(row?.tax_amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="80">
            <template #default="{ row, $index }">
              <el-button type="danger" link size="small" @click="removeInvoiceItem($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <!-- 含税金额汇总 -->
        <div class="invoice-summary">
          <div class="summary-row inline">
            <span class="summary-item"><span class="summary-label">大写（含税金额）：</span><span class="summary-value upper">{{ toChineseCurrency(totalTaxAmount) }}</span></span>
            <span class="summary-item"><span class="summary-label">小写（含税金额）：</span><span class="summary-value">{{ fixed2(totalTaxAmount) }}</span></span>
          </div>
        </div>
        <el-button type="primary" size="small" @click="addInvoiceItem"><el-icon><Plus /></el-icon>添加明细</el-button>
      </el-card>

      <el-card v-if="!isEdit && detail" shadow="never" style="margin-top: 20px;">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="发票名称">{{ detail.invoice_number }}</el-descriptions-item>
          <el-descriptions-item label="发票类型">{{ detail.invoice_type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ detail.org_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="合同">{{ detail.contract_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="价税合计"><span class="amount-text">¥{{ detail.total_amount?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span></el-descriptions-item>
          <el-descriptions-item label="已付款"><span class="amount-text">¥{{ detail.paid_amount?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span></el-descriptions-item>
          <el-descriptions-item label="付款状态"><el-tag :type="getPaymentType(detail.payment_status)" size="small">{{ getPaymentLabel(detail.payment_status) }}</el-tag></el-descriptions-item>
          <el-descriptions-item label="开票日期">{{ detail.billing_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="发票状态"><el-tag :type="getStatusType(detail.status)" size="small">{{ getStatusLabel(detail.status) }}</el-tag></el-descriptions-item>
          <el-descriptions-item label="备注">{{ detail.notes || '-' }}</el-descriptions-item>
        </el-descriptions>

        <!-- 开票信息 -->
        <el-divider content-position="center"><span style="font-weight: 600; color: #303133;">开票信息</span></el-divider>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="发票抬头">{{ detail.invoice_title || '-' }}</el-descriptions-item>
          <el-descriptions-item label="税号">{{ detail.tax_number || '-' }}</el-descriptions-item>
          <el-descriptions-item label="开户行">{{ detail.bank_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="银行账号">{{ detail.bank_account || '-' }}</el-descriptions-item>
          <el-descriptions-item label="地址">{{ detail.invoice_address || '-' }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ detail.invoice_phone || '-' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 发票明细 -->
      <el-card v-if="!isEdit && detail" shadow="never" style="margin-top: 20px;">
        <el-divider content-position="center"><span style="font-weight: 600; color: #303133;">发票明细</span></el-divider>
        <el-table v-if="invoiceItems.length > 0" :data="invoiceItems" border size="small" show-summary :summary-method="customSummary">
          <el-table-column prop="item_name" label="项目名称" min-width="200" />
          <el-table-column prop="spec_model" label="规格型号" />
          <el-table-column prop="unit" label="单位" />
          <el-table-column prop="quantity" label="数量" min-width="120">
            <template #default="{ row }">
              {{ fixed2(row?.quantity) }}
            </template>
          </el-table-column>
          <el-table-column prop="tax_included_amount" label="含税金额" min-width="150">
            <template #default="{ row }">
              {{ fixed2(getTaxIncludedAmount(row) || 0) }}
            </template>
          </el-table-column>
          <el-table-column prop="unit_price" label="单价" min-width="120">
            <template #default="{ row }">
              {{ formatNumberFull(row?.unit_price) }}
            </template>
          </el-table-column>
          <el-table-column prop="amount" label="金额" min-width="140">
            <template #default="{ row }">
              {{ fixed2(row?.amount) }}
            </template>
          </el-table-column>
          <el-table-column prop="tax_rate" label="税率" min-width="80">
            <template #default="{ row }">
              {{ row?.tax_rate != null ? (row.tax_rate * 100).toFixed(0) + '%' : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="tax_amount" label="税额" min-width="120">
            <template #default="{ row }">
              {{ fixed2(row?.tax_amount) }}
            </template>
          </el-table-column>
        </el-table>
        <!-- 含税金额汇总 -->
        <div v-if="invoiceItems.length > 0" class="invoice-summary" style="margin-top: 12px;">
          <div class="summary-row inline">
            <span class="summary-item"><span class="summary-label">大写（含税金额）：</span><span class="summary-value upper">{{ toChineseCurrency(totalTaxAmount) }}</span></span>
            <span class="summary-item"><span class="summary-label">小写（含税金额）：</span><span class="summary-value">{{ fixed2(totalTaxAmount) }}</span></span>
          </div>
        </div>
        <el-empty v-else description="暂无发票明细" />
      </el-card>

      <!-- 打印专用区域 - 完全匹配详情页布局 -->
      <div v-if="!isEdit && detail" class="invoice-print-area">
        <!-- 基本信息 -->
        <el-card shadow="never" style="margin-bottom: 10px;">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="发票名称">{{ detail.invoice_number || '-' }}</el-descriptions-item>
            <el-descriptions-item label="发票类型">{{ detail.invoice_type || '-' }}</el-descriptions-item>
            <el-descriptions-item label="客户">{{ detail.org_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="合同">{{ detail.contract_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="价税合计">¥{{ (detail.total_amount || 0).toLocaleString('zh-CN', {minimumFractionDigits:2}) }}</el-descriptions-item>
            <el-descriptions-item label="已付款">¥{{ (detail.paid_amount || 0).toLocaleString('zh-CN', {minimumFractionDigits:2}) }}</el-descriptions-item>
            <el-descriptions-item label="付款状态">{{ getPaymentLabel(detail.payment_status) || '-' }}</el-descriptions-item>
            <el-descriptions-item label="开票日期">{{ detail.billing_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="发票状态">{{ getStatusLabel(detail.status) || '-' }}</el-descriptions-item>
            <el-descriptions-item label="备注">{{ detail.notes || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
        <!-- 开票信息 -->
        <el-card shadow="never" style="margin-bottom: 10px;">
          <el-divider content-position="center"><span style="font-weight: 600; color: #303133;">开票信息</span></el-divider>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="发票抬头">{{ detail.invoice_title || '-' }}</el-descriptions-item>
            <el-descriptions-item label="税号">{{ detail.tax_number || '-' }}</el-descriptions-item>
            <el-descriptions-item label="开户行">{{ detail.bank_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="银行账号">{{ detail.bank_account || '-' }}</el-descriptions-item>
            <el-descriptions-item label="地址">{{ detail.invoice_address || '-' }}</el-descriptions-item>
            <el-descriptions-item label="电话">{{ detail.invoice_phone || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
        <!-- 发票明细 -->
        <el-card shadow="never">
          <el-divider content-position="center"><span style="font-weight: 600; color: #303133;">发票明细</span></el-divider>
          <el-table :data="invoiceItems" border size="small" show-summary :summary-method="getPrintSummary">
            <el-table-column prop="item_name" label="项目名称" min-width="200" />
            <el-table-column prop="spec_model" label="规格型号" />
            <el-table-column prop="unit" label="单位" />
            <el-table-column prop="quantity" label="数量" align="right" />
            <el-table-column prop="tax_included_amount" label="含税金额" align="right">
              <template #default="{ row }">¥{{ (getTaxIncludedAmount(row) || 0).toLocaleString('zh-CN', {minimumFractionDigits:2}) }}</template>
            </el-table-column>
            <el-table-column prop="unit_price" label="单价" align="right">
              <template #default="{ row }">{{ formatNumberFull(row?.unit_price) }}</template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" align="right">
              <template #default="{ row }">¥{{ (row.amount || 0).toLocaleString('zh-CN', {minimumFractionDigits:2}) }}</template>
            </el-table-column>
            <el-table-column prop="tax_rate" label="税率" align="center">
              <template #default="{ row }">{{ row?.tax_rate != null ? (row.tax_rate * 100).toFixed(0) + '%' : '-' }}</template>
            </el-table-column>
            <el-table-column prop="tax_amount" label="税额" align="right">
              <template #default="{ row }">¥{{ (row.tax_amount || 0).toLocaleString('zh-CN', {minimumFractionDigits:2}) }}</template>
            </el-table-column>
          </el-table>
          <div v-if="invoiceItems.length > 0" class="invoice-print-summary">
            <span>大写（含税金额）：{{ toChineseCurrency(totalTaxAmount) }}</span>
            <span style="margin-left: 20px;">小写（含税金额）：¥{{ totalTaxAmount?.toLocaleString('zh-CN', {minimumFractionDigits:2}) }}</span>
          </div>
        </el-card>
      </div>

      <el-tabs v-if="!isEdit && detail" style="margin-top: 20px;">
        <!-- 跟踪记录 Tab -->
        <el-tab-pane>
          <template #label><span>跟踪记录 <el-badge :value="followupRecords.length" :hidden="followupRecords.length === 0" /></span></template>
          <el-card shadow="never">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>跟踪记录</span>
                <el-button type="primary" size="small" @click="handleSaveFollowup" :loading="followupLoading">保存跟踪记录</el-button>
              </div>
            </template>
            <el-input v-model="followupText" type="textarea" :rows="4" placeholder="请输入跟踪记录内容（支持Markdown格式）" style="margin-bottom:12px;" />
            <div v-if="followupText" class="followup-preview">
              <div class="preview-label">预览：</div>
              <div v-html="renderMarkdown(followupText)"></div>
            </div>
            <div v-if="followupRecords.length > 0" class="followup-records">
              <el-divider content-position="center">历史记录</el-divider>
              <div v-for="record in followupRecords" :key="record.id" class="followup-record-item">
                <div class="record-title">{{ record.title }}</div>
                <div class="record-body" v-html="renderMarkdown(record.description)"></div>
                <div class="record-footer">{{ record.recorded_by || '未知' }} · {{ record.activity_date || record.created_at }}</div>
              </div>
            </div>
          </el-card>
        </el-tab-pane>

        <!-- 操作日志 Tab -->
        <el-tab-pane>
          <template #label>
            <span>操作日志 <el-badge :value="operationLogs.length" :hidden="operationLogs.length === 0" type="warning" /></span>
          </template>
          <el-card shadow="never">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>操作日志</span>
                <el-button type="primary" size="small" @click="detail && fetchOperationLogs(detail.id)" :loading="opLogLoading">刷新</el-button>
              </div>
            </template>
            <div v-if="operationLogs.length > 0" class="operation-logs">
              <el-timeline>
                <el-timeline-item v-for="log in operationLogs" :key="log.id" :timestamp="log.activity_date" placement="top" type="warning">
                  <el-card shadow="never">
                    <div class="log-title">{{ log.title }}</div>
                    <div class="log-body">{{ log.description }}</div>
                    <div class="log-footer">{{ log.recorded_by }} · {{ log.created_at }}</div>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </div>
            <el-empty v-else description="暂无操作日志" />
          </el-card>
        </el-tab-pane>

        <!-- 关联合同 Tab -->
        <el-tab-pane>
          <template #label><span>关联合同 <el-badge :value="detail.contract_id ? 1 : 0" :hidden="!detail.contract_id" /></span></template>
          <el-card shadow="never">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>关联合同</span>
              </div>
            </template>
            <div v-if="detail.contract_id">
              <el-table :data="[{contract_number: detail.contract_number, contract_name: detail.contract_name, id: detail.contract_id}]" border>
                <el-table-column prop="contract_number" label="合同编号" min-width="150" />
                <el-table-column prop="contract_name" label="合同名称" min-width="200" />
                <el-table-column label="操作" width="120" align="center">
                  <template #default="{ row }">
                    <el-button type="primary" link size="small" @click="router.push('/contract?id=' + row.id)">查看详情</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <el-empty v-else description="暂无关联合同" />
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getInvoiceList, getInvoiceDetail, createInvoice, updateInvoice, deleteInvoice, getInvoiceOperationLogs } from '@/api/invoice'
import { getCustomerList } from '@/api/customer'
import { request } from '@/api/request'
import { Search, Plus, View, Edit, Delete } from '@element-plus/icons-vue'
import { marked } from 'marked'

function renderMarkdown(text: string) { if (!text) return ''; return marked(text) }

const router = useRouter()
const detailMode = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const query = reactive({ page: 1, pageSize: 20, keyword: '', status: '', payment_status: '' })
const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const selectedRows = ref<any[]>([])
const orgOptions = ref<any[]>([])
const contractOptions = ref<any[]>([])
const detail = ref<any>(null)
const invoiceItems = ref<any[]>([])
const previewDialogVisible = ref(false)
const printRef = ref<any>(null)
const deletedItemIds = ref<number[]>([])  // 跟踪已删除的发票明细ID
const editingId = ref<number | null>(null)
const followupRecords = ref<any[]>([])
const followupText = ref('')
const followupLoading = ref(false)
const operationLogs = ref<any[]>([])
const opLogLoading = ref(false)
const formRef = ref()
const searchInputRef = ref()
const form = reactive<any>({
  invoice_number: '', organization_id: null, contract_id: null, invoice_type: '增值税专用发票',
  invoice_title: '', tax_number: '', bank_name: '', bank_account: '', invoice_address: '', invoice_phone: '',
  total_amount: 0, billing_date: '', status: 'pending', payment_status: 'unpaid', paid_amount: 0, notes: ''
})

const totalAmountDisplay = computed({
  get: () => form.total_amount ? form.total_amount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00',
  set: (val: string) => { form.total_amount = parseFloat(val.replace(/,/g, '')) || 0 }
})
const paidAmountDisplay = computed({
  get: () => form.paid_amount ? form.paid_amount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '',
  set: (val: string) => { form.paid_amount = parseFloat(val.replace(/,/g, '')) || 0 }
})

// 监听发票明细变化，更新价税合计
watch(() => invoiceItems.value.reduce((sum, item) => sum + (item.tax_included_amount || 0), 0), (val) => {
  form.total_amount = val
})

async function fetchData() { loading.value = true; try { const data = await getInvoiceList(query); tableData.value = data.items || []; total.value = data.total || 0 } catch (e) { console.error(e) } finally { loading.value = false } }
async function fetchOrgs() { try { const data = await getCustomerList({ page: 1, pageSize: 1000 }); orgOptions.value = data.items || [] } catch (e) { console.error(e) } }
async function fetchContracts(orgId?: number) { try { const params: any = { page: 1, pageSize: 1000 }; if (orgId) params.org_id = orgId; const data = await request.get('/contracts', params); contractOptions.value = data.items || [] } catch (e) { console.error(e) } }
function handleOrgChange(orgId: number) { 
  form.contract_id = null
  fetchContracts(orgId)
  // 自动填充客户开票信息
  const org = orgOptions.value.find(o => o.id === orgId)
  if (org) {
    form.invoice_title = org.invoice_info || ''
    form.tax_number = org.tax_number || ''
    form.bank_name = org.bank_name || ''
    form.bank_account = org.bank_account || ''
    form.invoice_address = org.invoice_address || ''
    form.invoice_phone = org.invoice_phone || ''
  }
}
function handleSelectionChange(val: any[]) { selectedRows.value = val }
async function handleBatchDelete() { if (!selectedRows.value.length) return; try { await Promise.all(selectedRows.value.map(r => deleteInvoice(r.id))); ElMessage.success('删除成功'); selectedRows.value = []; fetchData() } catch (e) { if (e !== 'cancel') console.error(e) } }
function handleSearch() { query.page = 1; fetchData() }
function handleSizeChange(val: number) { query.pageSize = val; fetchData() }

function handleAdd() { editingId.value = null; invoiceItems.value = []; deletedItemIds.value = []; Object.assign(form, { invoice_number: '', organization_id: null, contract_id: null, invoice_type: '增值税专用发票', amount: 0, tax_rate: 0.13, tax_amount: 0, total_amount: 0, billing_date: '', due_date: '', status: 'pending', payment_status: 'unpaid', paid_amount: 0, notes: '' }); contractOptions.value = []; detailMode.value = true; isEdit.value = true }
function handleBack() { detailMode.value = false; isEdit.value = false; detail.value = null; fetchData() }
async function handleView(row: any) {
  try {
    detail.value = await getInvoiceDetail(row.id)
    await fetchInvoiceItems(row.id)
    detailMode.value = true
    isEdit.value = false
    try {
      const actData = await request.get('/activities', { invoice_id: row.id, page: 1, pageSize: 50 })
      followupRecords.value = (actData.items || []).filter((r: any) => r.invoice_id === row.id)
    } catch (e) {
      console.error('获取跟踪记录失败', e)
    }
    fetchOperationLogs(row.id)
  } catch (e: any) {
    console.error('获取发票详情失败，详细错误:', e)
    ElMessage.error(`获取发票详情失败: ${e?.message || e?.response?.data?.message || '未知错误'}`)
  }
}

function handlePrintPreview() {
  // 直接触发浏览器打印
  window.print()
}

function getPrintSummary(param: any) {
  const { columns } = param
  return columns.map((col: any, index: number) => {
    if (index === 4) return '合计'
    if (index === 5) return '¥' + invoiceItems.value.reduce((sum: number, item: any) => sum + (item.amount || 0), 0).toLocaleString('zh-CN', {minimumFractionDigits:2})
    if (index === 7) return '¥' + invoiceItems.value.reduce((sum: number, item: any) => sum + (item.tax_amount || 0), 0).toLocaleString('zh-CN', {minimumFractionDigits:2})
    return ''
  })
}

function handleEdit(row: any) { editingId.value = row.id; detail.value = row; deletedItemIds.value = []; Object.assign(form, { invoice_number: row.invoice_number, invoice_title: row.invoice_title || '', tax_number: row.tax_number || '', bank_name: row.bank_name || '', bank_account: row.bank_account || '', invoice_address: row.invoice_address || '', invoice_phone: row.invoice_phone || '', organization_id: row.organization_id, contract_id: row.contract_id, invoice_type: row.invoice_type || '', amount: row.amount, tax_rate: row.tax_rate ?? 0.13, tax_amount: row.tax_amount || 0, total_amount: row.total_amount, billing_date: row.billing_date || '', due_date: row.due_date || '', status: row.status, payment_status: row.payment_status, paid_amount: row.paid_amount || 0, notes: row.notes || '' }); if (row.organization_id) fetchContracts(row.organization_id); fetchInvoiceItems(row.id); detailMode.value = true; isEdit.value = true }

function startEditFromDetail() { if (detail.value) { editingId.value = detail.value.id; Object.assign(form, { invoice_number: detail.value.invoice_number || '', invoice_title: detail.value.invoice_title || '', tax_number: detail.value.tax_number || '', bank_name: detail.value.bank_name || '', bank_account: detail.value.bank_account || '', invoice_address: detail.value.invoice_address || '', invoice_phone: detail.value.invoice_phone || '', organization_id: detail.value.organization_id, contract_id: detail.value.contract_id, invoice_type: detail.value.invoice_type || '', amount: detail.value.amount || 0, tax_rate: detail.value.tax_rate ?? 0.13, tax_amount: detail.value.tax_amount || 0, total_amount: detail.value.total_amount || 0, billing_date: detail.value.billing_date || '', due_date: detail.value.due_date || '', status: detail.value.status || 'pending', payment_status: detail.value.payment_status || 'unpaid', paid_amount: detail.value.paid_amount || 0, notes: detail.value.notes || '' }); if (detail.value.organization_id) fetchContracts(detail.value.organization_id); fetchInvoiceItems(detail.value.id); } isEdit.value = true }
function handleCancel() { if (editingId.value) { isEdit.value = false } else { handleBack() } }
async function handleSave() { submitLoading.value = true; try { let invoiceId = editingId.value; if (editingId.value) { await updateInvoice(editingId.value, form); } else { const res = await createInvoice(form); invoiceId = res.id || editingId.value; } if (invoiceId) { // 先删除已标记删除的明细
        for (const itemId of deletedItemIds.value) { await request.delete(`/invoices/items/${itemId}`); }
        deletedItemIds.value = []; await saveInvoiceItems(invoiceId); } ElMessage.success('保存成功'); if (editingId.value) { detail.value = await getInvoiceDetail(editingId.value); await fetchInvoiceItems(editingId.value); } else { handleBack(); return }; isEdit.value = false } catch (e) { ElMessage.error('保存失败') } finally { submitLoading.value = false } }

async function saveInvoiceItems(invoiceId: number) { 
  for (const item of invoiceItems.value) {
    // 确保 tax_included_amount 有值
    if (!item.tax_included_amount && item.amount) {
      item.tax_included_amount = item.amount * (1 + (item.tax_rate || 0.13))
    }
    if (item.id) {
      // 更新现有明细
      await request.put(`/invoices/items/${item.id}`, item)
    } else if (item.item_name) {
      // 创建新明细并更新本地ID
      const res = await request.post(`/invoices/${invoiceId}/items`, item)
      if (res.id) item.id = res.id
    }
  }
}
async function handleDelete(row: any) { try { await deleteInvoice(row.id); ElMessage.success('删除成功'); fetchData() } catch (e) { ElMessage.error('删除失败') } }

async function handleSaveFollowup() {
  if (!followupText.value.trim()) { ElMessage.warning('请输入跟踪记录内容'); return }
  followupLoading.value = true
  try {
    await request.post('/activities', {
      invoice_id: detail.value.id,
      activity_type: 'other',
      activity_date: new Date().toISOString().slice(0, 19).replace('T', ' '),
      title: '发票跟踪记录',
      description: followupText.value,
      recorded_by: '管理员'
    })
    ElMessage.success('跟踪记录已保存')
    followupText.value = ''
    // 刷新跟踪记录
    try {
      const data = await request.get('/activities', { invoice_id: detail.value.id, page: 1, pageSize: 50 })
      followupRecords.value = (data.items || []).filter((r: any) => r.invoice_id === detail.value.id)
    } catch (e) { console.error('获取跟踪记录失败', e) }
  } catch (e: any) { ElMessage.error(e?.message || '保存跟踪记录失败') }
  finally { followupLoading.value = false }
}

function getPaymentType(s: string) { const m: Record<string, string> = { unpaid: 'danger', partial: 'warning', paid: 'success' }; return m[s] || 'info' }
function getPaymentLabel(s: string) { const m: Record<string, string> = { unpaid: '未付款', partial: '部分付款', paid: '已付清' }; return m[s] || s }
function getStatusType(s: string) { const m: Record<string, string> = { pending: 'warning', issued: 'success', voided: 'info' }; return m[s] || 'info' }
function getStatusLabel(s: string) { const m: Record<string, string> = { pending: '待开票', issued: '已开票', voided: '已作废' }; return m[s] || s }
function isOverdue(row: any) { if (!row.due_date || row.payment_status === 'paid') return false; return new Date(row.due_date) < new Date() }

function addInvoiceItem() { invoiceItems.value.push({ item_name: '', spec_model: '', unit: '', quantity: 1, unit_price: 0, amount: 0, tax_rate: 0.13, tax_amount: 0, tax_included_amount: 0, _quantityDisplay: '1.00', _taxIncludedDisplay: '0.00' }) }
function removeInvoiceItem(index: number) { const item = invoiceItems.value[index]; if (item?.id) { deletedItemIds.value.push(item.id); } invoiceItems.value.splice(index, 1); updateAmountFromItems() }

// 计算含税金额相关值
function calcFromTaxIncluded(item: any) { if (!item) return; const taxIncluded = item.tax_included_amount || 0; const rate = item.tax_rate || 0.13; item.amount = taxIncluded / (1 + rate); item.tax_amount = taxIncluded - item.amount; item.quantity = item.quantity || 1; item.unit_price = item.quantity > 0 ? item.amount / item.quantity : 0; item._quantityDisplay = fixed2(item.quantity); item._taxIncludedDisplay = fixed2(item.tax_included_amount); }

// 数量变化时
function onQuantityInput(event: any, index: number) { const item = invoiceItems.value[index]; if (item) { const val = parseFloat(item._quantityDisplay.replace(/,/g, '')) || 0; item.quantity = val; item.tax_included_amount = (item.amount || 0) * (1 + (item.tax_rate || 0.13)); item.unit_price = val > 0 ? (item.amount || 0) / val : 0; item._taxIncludedDisplay = fixed2(item.tax_included_amount); updateAmountFromItems(); } }
function onQuantityBlur(index: number) { const item = invoiceItems.value[index]; if (item) { item._quantityDisplay = fixed2(item.quantity); item._taxIncludedDisplay = fixed2(item.tax_included_amount); } }

// 含税金额变化时 - 直接输入，不格式化
function onTaxIncludedBlur(index: number) { const item = invoiceItems.value[index]; if (item) { const val = parseFloat(item._taxIncludedDisplay.replace(/,/g, '')) || 0; item.tax_included_amount = val; calcFromTaxIncluded(item); item._taxIncludedDisplay = fixed2(item.tax_included_amount); updateAmountFromItems(); } }

// 税率变化时
function onTaxRateChange(index: number) { const item = invoiceItems.value[index]; if (item) { calcFromTaxIncluded(item); updateAmountFromItems(); } }

function fixed2(num: number): string { if (!num && num !== 0) return ''; return num.toFixed(2); }
function formatNumberFull(num: number): string { if (!num && num !== 0) return ''; return num.toFixed(2); }
function getTaxIncludedAmount(row: any): number { if (!row) return 0; if (row.tax_included_amount != null) return row.tax_included_amount; return (row.amount || 0) * (1 + (row.tax_rate || 0.13)); }

// 自定义汇总方法 - 只汇总数量、含税金额、金额、税额
function customSummary(param: any) { const { columns } = param; const data = invoiceItems.value; const sums: Record<number, string> = {}; columns.forEach((col: any, idx: number) => { const label = col.label || ''; if (label === '数量') { sums[idx] = fixed2(data.reduce((acc: number, item: any) => acc + (item.quantity || 0), 0)); } else if (label === '含税金额') { sums[idx] = '¥' + fixed2(data.reduce((acc: number, item: any) => acc + (item.tax_included_amount || 0), 0)); } else if (label === '金额') { sums[idx] = '¥' + fixed2(data.reduce((acc: number, item: any) => acc + (item.amount || 0), 0)); } else if (label === '税额') { sums[idx] = '¥' + fixed2(data.reduce((acc: number, item: any) => acc + (item.tax_amount || 0), 0)); } else if (label === '操作') { sums[idx] = ''; } else { sums[idx] = ''; } }); return sums; }

function updateAmountFromItems() { const taxIncludedSum = invoiceItems.value.reduce((acc, item) => acc + (item.tax_included_amount || 0), 0); form.amount = invoiceItems.value.reduce((acc, item) => acc + (item.amount || 0), 0); form.tax_amount = invoiceItems.value.reduce((acc, item) => acc + (item.tax_amount || 0), 0); form.total_amount = taxIncludedSum; updateTaxAndTotal() }

// 大写金额转换
function toChineseCurrency(num: number): string {
  if (!num || num === 0) return '零元整'
  const digit = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
  const units = ['仟', '佰', '拾', '']  // posInGroup 0,1,2,3
  const intPart = Math.floor(num)
  const decPart = Math.round((num - intPart) * 100)
  const intStr = intPart.toString()
  
  // 分组：每4位一组，从右往左
  const groups: string[] = []
  for (let i = intStr.length; i > 0; i -= 4) {
    groups.push(intStr.slice(Math.max(0, i - 4), i))
  }
  
  const bigUnits = ['', '万', '亿']
  let result = ''
  let needZero = false
  
  for (let g = groups.length - 1; g >= 0; g--) {
    const groupStr = groups[g]
    const groupLen = groupStr.length
    
    let groupHasValue = false
    
    // 从左往右处理（仟位开始）
    for (let i = 0; i < groupLen; i++) {
      const d = parseInt(groupStr[i])
      // 位置偏移：4位组从仟开始，更短的组从佰/拾/个开始
      const posInGroup = (4 - groupLen) + i
      
      if (d !== 0) {
        groupHasValue = true
        if (needZero) {
          result += '零'
          needZero = false
        }
        if (posInGroup < 3) {
          result += digit[d] + units[posInGroup]
        } else {
          result += digit[d]
        }
      } else {
        if (i < groupLen - 1) {
          const remaining = groupStr.slice(i + 1)
          if (/[1-9]/.test(remaining)) {
            needZero = true
          }
        }
      }
    }
    
    // 不是最低组，添加大单位
    if (g > 0 && groupHasValue) {
      result += bigUnits[g]
    }
  }
  
  while (result.endsWith('零')) {
    result = result.slice(0, -1)
  }
  
  if (result === '') result = '零'
  result += '元'
  
  if (decPart === 0) {
    result += '整'
  } else {
    const d1 = Math.floor(decPart / 10)
    const d2 = decPart % 10
    if (d1 > 0) result += digit[d1]
    if (d2 > 0) result += digit[d2]
    if (d1 > 0 || d2 > 0) result += '分'
  }
  return result
}

const totalTaxAmount = computed(() => invoiceItems.value.reduce((acc, item) => acc + (item.tax_included_amount || 0), 0))
const summaryQuantity = computed(() => invoiceItems.value.reduce((acc, item) => acc + (item.quantity || 0), 0))
const summaryTaxIncluded = computed(() => invoiceItems.value.reduce((acc, item) => acc + (item.tax_included_amount || 0), 0))
const summaryAmount = computed(() => invoiceItems.value.reduce((acc, item) => acc + (item.amount || 0), 0))
const summaryTaxAmount = computed(() => invoiceItems.value.reduce((acc, item) => acc + (item.tax_amount || 0), 0))

async function fetchInvoiceItems(invoiceId: number) { try { const data = await request.get(`/invoices/${invoiceId}/items`); const items = (data.items || []).filter((item: any) => item.item_name || item.spec_model || item.amount); items.forEach((item: any) => { item.quantity = item.quantity || 1; // 如果 tax_included_amount 为0或不正确，从金额反推
  if (!item.tax_included_amount || item.tax_included_amount === 0) { item.tax_included_amount = (item.amount || 0) * (1 + (item.tax_rate || 0.13)); } item._quantityDisplay = fixed2(item.quantity); item._taxIncludedDisplay = fixed2(item.tax_included_amount); calcFromTaxIncluded(item); }); invoiceItems.value = items } catch (e) { console.error('获取发票明细失败', e) } }

async function fetchOperationLogs(invoiceId: number) {
  opLogLoading.value = true
  try {
    const data = await getInvoiceOperationLogs(invoiceId)
    operationLogs.value = data.items || []
  } catch (e) { console.error('获取操作日志失败', e) } finally { opLogLoading.value = false }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  fetchOrgs()
  fetchData()
})

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    e.preventDefault()
    if (detailMode.value) {
      handleBack()
    }
  } else if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
    e.preventDefault()
    if (detailMode.value && isEdit.value) {
      handleSave()
    }
  } else if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
    e.preventDefault()
    searchInputRef.value?.focus()
  }
}

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>



<style scoped lang="scss">
.invoice-page {
  padding: 20px;
}

:deep(.el-table__footer) {
  display: table-row !important;
  visibility: visible !important;
}

:deep(.el-table__footer .cell) {
  visibility: visible !important;
  display: table-cell !important;
  font-weight: bold;
  background-color: #f5f7fa;
}

.invoice-summary {
  margin-top: 12px;
  
  .summary-row {
    display: flex;
    gap: 24px;
    justify-content: flex-end;
    
    &.inline {
      display: flex;
      gap: 24px;
    }
  }
  
  .summary-item {
    font-size: 14px;
    
    .summary-label {
      color: #909399;
    }
    
    .summary-value {
      color: #303133;
      font-weight: 600;
      
      &.upper {
        color: #67c23a;
        font-size: 16px;
      }
    }
  }
}

.invoice-print-area {
  display: none;
}

@media print {
  body * {
    visibility: hidden !important;
  }
  
  .invoice-print-area,
  .invoice-print-area * {
    visibility: visible !important;
  }
  
  .invoice-print-area {
    position: fixed !important;
    left: 0 !important;
    top: 0 !important;
    width: 100% !important;
    background: white !important;
    padding: 20px !important;
    z-index: 9999 !important;
    display: block !important;
  }
  
  .invoice-print-area .el-card {
    box-shadow: none !important;
    border: 1px solid #ebeef5 !important;
    page-break-inside: avoid;
    margin-bottom: 10px !important;
  }
  
  .invoice-print-area .el-descriptions {
    font-size: 12px;
    width: 100%;
  }
  
  .invoice-print-area .el-descriptions__table {
    table-layout: auto;
    width: auto;
  }
  
  .invoice-print-area .el-descriptions__label {
    width: auto;
    font-weight: normal;
    white-space: nowrap;
  }
  
  .invoice-print-area .el-descriptions__content {
    width: auto;
    white-space: nowrap;
  }
  
  .invoice-print-area .el-descriptions-item {
    width: auto;
  }
  
  .invoice-print-summary {
    text-align: right;
    font-weight: bold;
    margin-top: 10px;
    font-size: 14px;
  }
  
  .invoice-print-area table {
    width: 100%;
    border-collapse: collapse;
  }
  
  .invoice-print-area td {
    border: 1px solid #ebeef5;
    padding: 4px 8px;
  }
}

.operation-logs {
  .log-title { font-weight: 600; color: #303133; margin-bottom: 8px; }
  .log-body { color: #606266; font-size: 14px; line-height: 1.6; white-space: pre-wrap; }
  .log-footer { text-align: right; font-size: 12px; color: #909399; margin-top: 8px; }
}
</style>