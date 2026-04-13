<template>
  <div class="contract-page">
    <template v-if="!detailMode">
      <div class="search-bar">
        <div class="search-form">
          <el-input ref="searchInputRef" v-model="query.keyword" placeholder="搜索合同名称/编号..." clearable style="width: 260px" @clear="handleSearch" @keyup.enter="handleSearch">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="query.status" placeholder="合同状态" clearable style="width: 140px" @change="handleSearch">
            <el-option label="草稿" value="draft" />
            <el-option label="待审批" value="pending_approval" />
            <el-option label="已审批" value="approved" />
            <el-option label="执行中" value="active" />
            <el-option label="已完成" value="completed" />
            <el-option label="已终止" value="terminated" />
            <el-option label="已续约" value="renewed" />
          </el-select>
        </div>
        <span class="search-shortcut-hint">按 / 聚焦搜索</span>
        <div class="action-buttons">
          <span v-if="selectedRows.length > 0" class="selected-info">已选择 {{ selectedRows.length }} 项</span>
          <el-button v-if="selectedRows.length > 0" type="danger" @click="handleBatchDelete"><el-icon><Delete /></el-icon>批量删除</el-button>
          <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon>新建合同</el-button>
        </div>
      </div>

      <div>
        <el-card shadow="never" class="table-card">
          <el-table v-loading="loading" :data="tableData" row-key="id" @selection-change="handleSelectionChange" table-layout="auto">
            <el-table-column type="selection" min-width="50" />
            <el-table-column prop="contract_name" label="合同名称" min-width="180" sortable show-overflow-tooltip>
              <template #default="{ row }"><el-link type="primary" @click="handleView(row)"><span class="contract-name-cell">{{ row.contract_name }}</span></el-link></template>
            </el-table-column>
            <el-table-column prop="org_name" label="客户" min-width="120" show-overflow-tooltip />
            <el-table-column prop="contract_type" label="合同类型" min-width="100">
              <template #default="{ row }"><el-tag :type="getContractTypeStyle(row.contract_type)" size="small">{{ row.contract_type || '—' }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="contract_amount" label="合同金额" min-width="130" sortable>
              <template #default="{ row }"><span class="amount-text">¥{{ row.contract_amount?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span></template>
            </el-table-column>
            <el-table-column prop="status" label="状态" min-width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="signed_date" label="签订日期" min-width="110" />
            <el-table-column label="操作" min-width="150">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleView(row)"><el-icon><View /></el-icon>查看</el-button>
                <el-button type="primary" link size="small" @click="handleEdit(row)"><el-icon><Edit /></el-icon>编辑</el-button>
                <el-popconfirm title="确定删除该合同？" @confirm="handleDelete(row)"><template #reference><el-button type="danger" link size="small"><el-icon><Delete /></el-icon>删除</el-button></template></el-popconfirm>
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
        <el-page-header :content="isEdit ? '编辑合同' : '合同详情'" @back="handleBack">
          <template #extra>
            <template v-if="!isEdit"><el-button type="primary" @click="startEditFromDetail">编辑</el-button></template>
            <template v-else><el-button @click="handleCancel">取消</el-button><el-button type="primary" @click="handleSave" :loading="submitLoading">保存 <span style="font-size:11px;opacity:0.7;margin-left:4px;">⌘↵</span></el-button><span class="shortcut-hint">ESC 返回</span></template>
          </template>
        </el-page-header>
      </div>

      <el-card v-if="isEdit" shadow="never" style="margin-top: 20px;">
        <el-form ref="formRef" :model="form" label-width="110px">
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="合同编号" required><el-input v-model="form.contract_number" placeholder="请输入合同编号" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="合同名称" required><el-input v-model="form.contract_name" placeholder="请输入合同名称" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="客户" required><el-select v-model="form.organization_id" placeholder="请选择客户" style="width:100%" filterable clearable @change="handleOrgChange"><el-option v-for="org in orgOptions" :key="org.id" :label="org.name" :value="org.id" /></el-select></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="关联商机"><el-select v-model="form.opportunity_id" placeholder="请选择商机" style="width:100%" filterable clearable><el-option v-for="opp in opportunityOptions" :key="opp.id" :label="opp.opportunity_name" :value="opp.id" /></el-select></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="合同类型"><el-select v-model="form.contract_type" placeholder="请选择类型" style="width:100%"><el-option label="销售合同" value="销售合同" /><el-option label="采购合同" value="采购合同" /></el-select></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="合同金额"><el-input v-model="contractAmountDisplay" placeholder="请输入金额" style="width:100%" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item :label="form.contract_type === '采购合同' ? '供应商' : '合同状态'"><el-select v-if="form.contract_type === '采购合同'" v-model="form.supplier_id" placeholder="请选择供应商" style="width:100%" filterable clearable><el-option v-for="org in orgOptions" :key="org.id" :label="org.name" :value="org.id" /></el-select><el-select v-else v-model="form.status" style="width:100%"><el-option label="草稿" value="draft" /><el-option label="待审批" value="pending_approval" /><el-option label="已审批" value="approved" /><el-option label="执行中" value="active" /><el-option label="已完成" value="completed" /><el-option label="已终止" value="terminated" /><el-option label="已续约" value="renewed" /></el-select></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="签订日期"><el-date-picker v-model="form.signed_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20" v-if="form.contract_type === '采购合同'">
            <el-col :span="12"><el-form-item label="合同状态"><el-select v-model="form.status" style="width:100%"><el-option label="草稿" value="draft" /><el-option label="待审批" value="pending_approval" /><el-option label="已审批" value="approved" /><el-option label="执行中" value="active" /><el-option label="已完成" value="completed" /><el-option label="已终止" value="terminated" /><el-option label="已续约" value="renewed" /></el-select></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="开始日期"><el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20" v-if="form.contract_type === '采购合同'">
            <el-col :span="12"><el-form-item label="结束日期"><el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col>
            <el-col :span="12"></el-col>
          </el-row>
          <el-row :gutter="20" v-if="form.contract_type !== '采购合同'">
            <el-col :span="12"><el-form-item label="开始日期"><el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="结束日期"><el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col>
          </el-row>

          <!-- 货物内容 -->
          <el-divider content-position="center"><span style="font-weight: 600; color: #303133;">货物内容</span></el-divider>
          <div v-if="goodsItems.length > 0" style="margin-bottom: 12px;">
            <el-table :data="goodsItems" border style="width: 100%; margin-bottom: 8px;" class="goods-table" show-summary :summary-method="getGoodsSummary">
              <el-table-column prop="goods_name" label="货物名称" min-width="150">
                <template #default="{ row }">
                  <el-input v-model="row.goods_name" placeholder="请输入货物名称" size="small" />
                </template>
              </el-table-column>
              <el-table-column prop="brand" label="品牌" min-width="100">
                <template #default="{ row }">
                  <el-input v-model="row.brand" placeholder="请输入品牌" size="small" />
                </template>
              </el-table-column>
              <el-table-column prop="model" label="型号" min-width="100">
                <template #default="{ row }">
                  <el-input v-model="row.model" placeholder="请输入型号" size="small" />
                </template>
              </el-table-column>
              <el-table-column prop="quantity" label="数量" width="100">
                <template #default="{ row }">
                  <el-input-number v-model="row.quantity" :min="0" :precision="0" :controls="false" size="small" style="width: 100%;" @change="calcGoodsSubtotal(row)" />
                </template>
              </el-table-column>
              <el-table-column prop="unit_price" label="单价" width="120">
                <template #default="{ row }">
                  <el-input-number v-model="row.unit_price" :min="0" :precision="2" :controls="false" size="small" style="width: 100%;" @change="calcGoodsSubtotal(row)" />
                </template>
              </el-table-column>
              <el-table-column prop="subtotal" label="小计" width="120">
                <template #default="{ row }">
                  <span class="amount-text">{{ row.subtotal?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="warranty_period" label="质保期" width="120">
                <template #default="{ row }">
                  <el-input v-model="row.warranty_period" placeholder="如：1年" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80" align="center">
                <template #default="{ $index }">
                  <el-button type="danger" size="small" text @click="removeGoodsItem($index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <el-button type="primary" plain size="small" @click="addGoodsItem">添加货物</el-button>

          <!-- 付款条件 -->
          <el-divider content-position="center"><span style="font-weight: 600; color: #303133;">付款条件</span></el-divider>
          <div v-if="paymentConditions.length > 0" style="margin-bottom: 12px;">
            <el-table :data="paymentConditions" border style="width: 100%; margin-bottom: 8px;" class="payment-conditions-table">
              <el-table-column prop="name" label="名称" min-width="120">
                <template #default="{ row, $index }">
                  <el-input v-model="row.name" placeholder="请输入名称" size="small" />
                </template>
              </el-table-column>
              <el-table-column prop="payment_condition" label="付款条件" min-width="150">
                <template #default="{ row }">
                  <el-input v-model="row.payment_condition" placeholder="请输入付款条件" size="small" />
                </template>
              </el-table-column>
              <el-table-column prop="payment_ratio" label="付款比例(%)" width="120">
                <template #default="{ row, $index }">
                  <el-input-number v-model="row.payment_ratio" :min="0" :max="100" :precision="2" size="small" style="width: 100%;" @change="onPaymentRatioChange($index)" />
                </template>
              </el-table-column>
              <el-table-column prop="amount" label="金额" width="120">
                <template #default="{ row }">
                  <span class="amount-text">{{ row.amount?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="notes" label="备注" min-width="150">
                <template #default="{ row }">
                  <el-input v-model="row.notes" placeholder="请输入备注" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80" align="center">
                <template #default="{ $index }">
                  <el-button type="danger" size="small" text @click="removePaymentCondition($index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <el-button type="primary" plain size="small" @click="addPaymentCondition">添加付款条件</el-button>
        </el-form>
      </el-card>

      <el-card v-if="!isEdit && detail" shadow="never" style="margin-top: 20px;">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="合同编号">{{ detail.contract_number }}</el-descriptions-item>
          <el-descriptions-item label="合同名称" :span="2">{{ detail.contract_name }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ detail.org_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="商机">{{ detail.opportunity_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="合同类型"><el-tag :type="getContractTypeStyle(detail.contract_type)" size="small">{{ detail.contract_type || '-' }}</el-tag></el-descriptions-item>
          <el-descriptions-item label="供应商" v-if="detail.contract_type === '采购合同'">{{ detail.supplier_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="合同金额"><span class="amount-text">¥{{ detail.contract_amount?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span></el-descriptions-item>
          <el-descriptions-item label="合同状态"><el-tag :type="getStatusType(detail.status)" size="small">{{ getStatusLabel(detail.status) }}</el-tag></el-descriptions-item>
          <el-descriptions-item label="签订日期">{{ detail.signed_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="开始日期">{{ detail.start_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="结束日期">{{ detail.end_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
        </el-descriptions>

        <!-- 货物内容 -->
        <el-divider content-position="center" style="margin-top: 20px;"><span style="font-weight: 600; color: #303133;">货物内容</span></el-divider>
        <el-table v-if="goodsItems.length > 0" :data="goodsItems" border show-summary :summary-method="getGoodsSummary">
          <el-table-column prop="goods_name" label="货物名称" min-width="150" />
          <el-table-column prop="brand" label="品牌" min-width="100" />
          <el-table-column prop="model" label="型号" min-width="100" />
          <el-table-column prop="quantity" label="数量" width="80" align="center" />
          <el-table-column prop="unit_price" label="单价" width="120" align="right">
            <template #default="{ row }">¥{{ row.unit_price?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</template>
          </el-table-column>
          <el-table-column prop="subtotal" label="小计" width="120" align="right">
            <template #default="{ row }"><span class="amount-text">¥{{ row.subtotal?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span></template>
          </el-table-column>
          <el-table-column prop="warranty_period" label="质保期" width="120" />
        </el-table>
        <el-empty v-else description="暂无货物内容" :image-size="60" />

        <!-- 付款条件 -->
        <el-divider content-position="center" style="margin-top: 20px;"><span style="font-weight: 600; color: #303133;">付款条件</span></el-divider>
        <el-table v-if="paymentConditions.length > 0" :data="paymentConditions" border>
          <el-table-column prop="name" label="名称" min-width="120" />
          <el-table-column prop="payment_condition" label="付款条件" min-width="150" />
          <el-table-column prop="payment_ratio" label="付款比例(%)" width="120" align="center">
            <template #default="{ row }">{{ row.payment_ratio?.toFixed(2) }}%</template>
          </el-table-column>
          <el-table-column prop="amount" label="金额" width="140" align="right">
            <template #default="{ row }"><span class="amount-text">¥{{ row.amount?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span></template>
          </el-table-column>
          <el-table-column prop="notes" label="备注" min-width="150" />
        </el-table>
        <el-empty v-else description="暂无付款条件" :image-size="60" />
      </el-card>

      <!-- 详情内容（带标签页） -->
      <el-tabs v-if="!isEdit && detail" style="margin-top: 20px;">
        <!-- 跟踪记录 Tab -->
        <el-tab-pane>
          <template #label><span>跟踪记录 <el-badge :value="followupRecords.length" :hidden="followupRecords.length === 0" /></span></template>
          <el-card shadow="never">
            <template #header>
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span>跟踪记录</span>
                <el-button type="primary" size="small" @click="handleSaveFollowup" :loading="followupLoading">保存跟踪记录</el-button>
              </div>
            </template>
            <el-input v-model="followupText" type="textarea" :rows="4" placeholder="请输入跟踪记录内容（支持Markdown格式）" style="margin-bottom:12px;" />
            <div v-if="followupText" class="followup-preview"><div class="preview-label">预览：</div><div v-html="renderMarkdown(followupText)"></div></div>
            <div v-if="followupRecords.length > 0" class="followup-records">
              <el-divider content-position="center">历史记录</el-divider>
              <div v-for="record in followupRecords" :key="record.id" class="followup-record-item">
                <div class="record-title">{{ record.title }}</div>
                <div class="record-body" v-html="renderMarkdown(record.description)"></div>
                <div class="record-footer">{{ record.recorded_by }} · {{ record.activity_date || record.created_at }}</div>
              </div>
            </div>
          </el-card>
        </el-tab-pane>

        <!-- 发票 Tab -->
        <el-tab-pane>
          <template #label>
            <span>关联发票 <el-badge :value="invoices.length" :hidden="invoices.length === 0" /></span>
          </template>
          <el-card shadow="never">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>关联发票 ({{ invoices.length }})</span>
                <el-button type="primary" size="small" @click="router.push('/invoice')">查看全部发票</el-button>
              </div>
            </template>
            <el-table v-if="invoices.length > 0" :data="invoices" border stripe>
              <el-table-column prop="invoice_number" label="发票号" min-width="150" />
              <el-table-column prop="invoice_type" label="发票类型" min-width="120" />
              <el-table-column prop="amount" label="金额" min-width="120">
                <template #default="{ row }">
                  ¥{{ row.amount?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
                </template>
              </el-table-column>
              <el-table-column prop="tax_amount" label="税额" min-width="100" />
              <el-table-column prop="total_amount" label="价税合计" min-width="120">
                <template #default="{ row }">
                  ¥{{ row.total_amount?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
                </template>
              </el-table-column>
              <el-table-column prop="billing_date" label="开票日期" min-width="120" />
              <el-table-column prop="status" label="状态" min-width="100">
                <template #default="{ row }">
                  <el-tag :type="row.payment_status === 'paid' ? 'success' : 'warning'" size="small">
                    {{ row.payment_status === 'paid' ? '已付款' : '未付款' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-else description="暂无关联发票" />
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getContractList, getContractDetail, createContract, updateContract, deleteContract } from '@/api/contract'
import { getCustomerList } from '@/api/customer'
import { getOpportunityList } from '@/api/opportunity'
import { request } from '@/api/request'
import { useUserStore } from '@/store/user'
import { Search, Plus, View, Edit, Delete } from '@element-plus/icons-vue'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

const detailMode = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const query = reactive({ page: 1, pageSize: 20, keyword: '', status: '' })
const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const selectedRows = ref<any[]>([])
const orgOptions = ref<any[]>([])
const opportunityOptions = ref<any[]>([])
const detail = ref<any>(null)
const invoices = ref<any[]>([])
const followupText = ref('')
const followupLoading = ref(false)
const followupRecords = ref<any[]>([])
const goodsItems = ref<any[]>([])
const paymentConditions = ref<any[]>([])
const deletedPaymentConditionIds = ref<number[]>([])
const editingId = ref<number | null>(null)
const searchInputRef = ref()
const formRef = ref()
const form = reactive<any>({
  contract_number: '', contract_name: '', organization_id: null, opportunity_id: null,
  contract_amount: 0, status: 'draft', signed_date: '', start_date: '', end_date: '', contract_type: '销售合同', supplier_id: null
})

const contractAmountDisplay = computed({
  get: () => form.contract_amount ? Number(form.contract_amount).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '',
  set: (val: string) => { form.contract_amount = parseFloat(val.replace(/,/g, '')) || 0 }
})

async function fetchData() { loading.value = true; try { const data = await getContractList(query); tableData.value = data.items || []; total.value = data.total || 0 } catch (e) { console.error(e) } finally { loading.value = false } }

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
async function fetchOrgs() { try { const data = await getCustomerList({ page: 1, pageSize: 1000 }); orgOptions.value = data.items || [] } catch (e) { console.error(e) } }
function handleOrgChange(orgId: number) { form.opportunity_id = null; if (orgId) { fetchOpportunities(orgId); } }
async function fetchOpportunities(orgId: number) { try { const data = await getOpportunityList({ org_id: orgId, page: 1, pageSize: 1000 }); opportunityOptions.value = data.items || [] } catch (e) { console.error(e) } }
function handleSelectionChange(val: any[]) { selectedRows.value = val }
async function handleBatchDelete() { if (!selectedRows.value.length) return; try { await Promise.all(selectedRows.value.map(r => deleteContract(r.id))); ElMessage.success('删除成功'); selectedRows.value = []; fetchData() } catch (e) { if (e !== 'cancel') console.error(e) } }
function handleSearch() { query.page = 1; fetchData() }
function handleSizeChange(val: number) { query.pageSize = val; fetchData() }

function handleAdd() {
  editingId.value = null
  Object.assign(form, { contract_number: '', contract_name: '', organization_id: null, opportunity_id: null, contract_amount: 0, status: 'draft', signed_date: '', start_date: '', end_date: '', contract_type: '销售合同', supplier_id: null })
  opportunityOptions.value = []
  paymentConditions.value = []
goodsItems.value = []
  deletedPaymentConditionIds.value = []
  detailMode.value = true; isEdit.value = true
}
function handleBack() { detailMode.value = false; isEdit.value = false; detail.value = null; fetchData() }
async function handleView(row: any) { try { detail.value = await getContractDetail(row.id); invoices.value = detail.value.invoices || []; detailMode.value = true; isEdit.value = false; followupRecords.value = detail.value.activities || []; paymentConditions.value = detail.value.payment_conditions || [];
goodsItems.value = detail.value.goods_items || [];
goodsItems.value = detail.value.goods_items || [];
deletedPaymentConditionIds.value = [] } catch (e) { ElMessage.error('获取合同详情失败') } }
async function handleEdit(row: any) {
  editingId.value = row.id
  detailMode.value = true
  // 从列表进入编辑时，需要获取完整详情（含付款条件和货物内容）
  try {
    const fullDetail = await getContractDetail(row.id)
    detail.value = fullDetail
    paymentConditions.value = fullDetail.payment_conditions || []
    goodsItems.value = fullDetail.goods_items || []
  } catch (e) {
    detail.value = row
    paymentConditions.value = []
    goodsItems.value = []
  }
  deletedPaymentConditionIds.value = []
  Object.assign(form, {
    contract_number: row.contract_number, contract_name: row.contract_name,
    organization_id: row.organization_id, opportunity_id: row.opportunity_id,
    contract_amount: row.contract_amount, status: row.status,
    signed_date: row.signed_date || '', start_date: row.start_date || '',
    end_date: row.end_date || '', contract_type: row.contract_type || ''
  })
  if (row.organization_id) fetchOpportunities(row.organization_id)
  isEdit.value = true
}

function startEditFromDetail() { if (detail.value) { editingId.value = detail.value.id; paymentConditions.value = detail.value.payment_conditions || [];
goodsItems.value = detail.value.goods_items || []; deletedPaymentConditionIds.value = []; Object.assign(form, { contract_number: detail.value.contract_number || '', contract_name: detail.value.contract_name || '', organization_id: detail.value.organization_id, opportunity_id: detail.value.opportunity_id, contract_amount: detail.value.contract_amount || 0, status: detail.value.status || 'draft', signed_date: detail.value.signed_date || '', start_date: detail.value.start_date || '', end_date: detail.value.end_date || '', contract_type: detail.value.contract_type || '', supplier_id: detail.value.supplier_id }); if (detail.value.organization_id) fetchOpportunities(detail.value.organization_id); } isEdit.value = true }
function handleCancel() { if (editingId.value) { isEdit.value = false } else { handleBack() } }
async function handleSave() { submitLoading.value = true; try { if (editingId.value) { await updateContract(editingId.value, form); // 保存货物内容
        for (const gi of goodsItems.value) { if (gi.id) { await request.put(`/contracts/goods-items/${gi.id}`, gi); } else { const res = await request.post(`/contracts/${editingId.value}/goods-items`, gi); if (res.id) gi.id = res.id; } } // 保存付款条件
        for (const pc of deletedPaymentConditionIds.value) { await request.delete(`/contracts/payment-conditions/${pc}`); }
        deletedPaymentConditionIds.value = []; for (const pc of paymentConditions.value) { if (pc.id) { await request.put(`/contracts/payment-conditions/${pc.id}`, pc); } else { const res = await request.post(`/contracts/${editingId.value}/payment-conditions`, pc); if (res.id) pc.id = res.id; } } ElMessage.success('更新成功'); detail.value = await getContractDetail(editingId.value); paymentConditions.value = detail.value.payment_conditions || []; goodsItems.value = detail.value.goods_items || [] } else { const newContract = await createContract(form); // 保存货物内容
        if (goodsItems.value.length > 0 && newContract.id) { for (const gi of goodsItems.value) { const res = await request.post(`/contracts/${newContract.id}/goods-items`, gi); if (res.id) gi.id = res.id; } } // 保存付款条件
        if (paymentConditions.value.length > 0 && newContract.id) { for (const pc of paymentConditions.value) { const res = await request.post(`/contracts/${newContract.id}/payment-conditions`, pc); if (res.id) pc.id = res.id; } } ElMessage.success('创建成功'); handleBack(); return }; isEdit.value = false } catch (e) { console.error('保存失败', e); ElMessage.error('保存失败') } finally { submitLoading.value = false } }

// 付款条件相关函数
function addGoodsItem() { goodsItems.value.push({ goods_name: '', brand: '', model: '', quantity: 1, unit_price: 0, subtotal: 0, warranty_period: '' }); }
function removeGoodsItem(index: number) { goodsItems.value.splice(index, 1); }
function calcGoodsSubtotal(row: any) { if (row) { row.subtotal = (row.quantity || 0) * (row.unit_price || 0); } }
function getGoodsSummary(param: any) { const { columns } = param; const total = goodsItems.value.reduce((sum: number, item: any) => sum + (item.subtotal || 0), 0); const totalStr = '¥' + total.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); return columns.map((col: any, index: number) => { if (index === 4) return '合计:'; if (index === 5) return totalStr; return ''; }); }

function addPaymentCondition() { paymentConditions.value.push({ name: '', payment_condition: '', payment_ratio: 0, amount: 0, notes: '' }); updatePaymentAmounts(); }
function removePaymentCondition(index: number) { const pc = paymentConditions.value[index]; if (pc.id) { deletedPaymentConditionIds.value.push(pc.id); } paymentConditions.value.splice(index, 1); updatePaymentAmounts(); }
function updatePaymentAmounts() { paymentConditions.value.forEach(pc => { pc.amount = (form.contract_amount || 0) * (pc.payment_ratio || 0) / 100; }); }
function onPaymentRatioChange(index: number) { const pc = paymentConditions.value[index]; if (pc) { pc.amount = (form.contract_amount || 0) * (pc.payment_ratio || 0) / 100; } }
async function handleDelete(row: any) { try { await deleteContract(row.id); ElMessage.success('删除成功'); fetchData() } catch (e) { ElMessage.error('删除失败') } }

async function fetchFollowupRecords() { if (!detail.value?.id) return; try { const data = await request.get('/activities', { contract_id: detail.value.id, page: 1, pageSize: 50 }); followupRecords.value = (data.items || []).filter((r: any) => r.title?.includes('跟踪记录') && r.contract_id === detail.value.id) } catch (e) { console.error('获取跟踪记录失败', e) } }
async function handleSaveFollowup() { if (!followupText.value.trim()) { ElMessage.warning('请输入跟踪记录内容'); return }; followupLoading.value = true; try { await request.post('/activities', { contract_id: detail.value.id, activity_type: 'other', activity_date: new Date().toISOString().slice(0, 19).replace('T', ' '), title: '合同跟踪记录', description: followupText.value, recorded_by: userStore.userInfo?.name || '未知' }); ElMessage.success('跟踪记录已保存'); const now = new Date().toISOString().slice(0, 19).replace('T', ' '); followupRecords.value.unshift({ id: Date.now(), title: '合同跟踪记录', description: followupText.value, recorded_by: userStore.userInfo?.name || '未知', activity_date: now, created_at: now }); followupText.value = '' } catch (e) { console.error('保存跟踪记录失败', e) } finally { followupLoading.value = false } }
function renderMarkdown(text: string): string { if (!text) return ''; return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>').replace(/\n/g, '<br>') }
function getStatusType(status: string) { const map: Record<string, string> = { draft: 'info', pending_approval: 'warning', approved: 'success', active: 'success', completed: '', terminated: 'danger', renewed: 'primary' }; return map[status] || 'info' }
function getStatusLabel(status: string) { const map: Record<string, string> = { draft: '草稿', pending_approval: '待审批', approved: '已审批', active: '执行中', completed: '已完成', terminated: '已终止', renewed: '已续约' }; return map[status] || status }
function getContractTypeStyle(type: string) { const map: Record<string, string> = { '销售合同': 'success', '采购合同': 'danger' }; return map[type] || 'info' }

onMounted(async () => {
  window.addEventListener('keydown', handleKeydown)
  fetchOrgs()
  const contractId = route.query.id
  if (contractId) {
    try {
      detail.value = await getContractDetail(Number(contractId))
      invoices.value = detail.value.invoices || []
      followupRecords.value = detail.value.activities || []
      detailMode.value = true
      isEdit.value = false
    } catch (e) {
      ElMessage.error('获取合同详情失败')
    }
  } else {
    fetchData()
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped lang="scss">
.payment-conditions-table, .goods-table {
  :deep(.el-table__body-wrapper) {
    .cell {
      font-size: 12px;
    }
  }
}
.goods-table {
  :deep(.el-table__footer) {
    .cell {
      font-weight: 600;
    }
  }
}
.contract-page { .detail-header { margin-bottom: 20px; } .shortcut-hint { font-size: 12px; color: #909399; margin-left: 12px; } .search-shortcut-hint { font-size: 12px; color: #909399; margin-left: auto; } .amount-text { color: #E6A23C; font-weight: 600; } }
.pagination-container { display: flex; justify-content: flex-end; padding: 16px 0 0; }
.action-buttons { display: flex; align-items: center; gap: 12px; }
.action-buttons .selected-info { color: #606266; font-size: 14px; }
.followup-preview { background: #f5f7fa; padding: 12px; border-radius: 4px; margin-bottom: 12px; }
.followup-preview .preview-label { font-size: 12px; color: #909399; margin-bottom: 8px; }
.followup-preview :deep(p) { margin: 4px 0; }
.followup-preview :deep(strong) { font-weight: bold; }
.followup-records { margin-top: 16px; }
.followup-records .followup-record-item { padding: 12px 0; border-bottom: 1px solid #ebeef5; }
.followup-records .followup-record-item:last-child { border-bottom: none; }
.followup-records .record-title { font-weight: 600; color: #303133; margin-bottom: 8px; }
.followup-records .record-body { color: #606266; font-size: 14px; line-height: 1.6; }
.followup-records .record-body :deep(p) { margin: 4px 0; }
.followup-records .record-body :deep(strong) { font-weight: bold; }
.followup-records .record-body :deep(em) { font-style: italic; }
.followup-records .record-footer { text-align: right; font-size: 12px; color: #909399; margin-top: 8px; }

// 合同名称最多显示12个汉字
:deep(.el-table .cell .contract-name-cell) {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
:deep(.el-table .el-table__header .el-table-column--操作 .cell),
:deep(.el-table .el-table__body .el-table-column--操作 .cell) {
  white-space: nowrap;
}

// 禁用标签点击，避免点击标签时触发输入框
:deep(.el-form-item__label) {
  pointer-events: none;
}
</style>
