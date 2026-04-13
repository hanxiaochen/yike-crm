import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Layout from '@/layouts/index.vue'

// 静态路由
export const constantRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', hidden: true }
  },
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '404', hidden: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404',
    meta: { hidden: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/profile/index.vue'),
    meta: { title: '个人中心', hidden: true }
  },
  {
    path: '/password',
    name: 'Password',
    component: () => import('@/views/profile/index.vue'),
    meta: { title: '修改密码', hidden: true }
  }
]

// 动态路由
export const asyncRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    meta: { title: '首页', icon: 'HomeFilled' },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '仪表盘', icon: 'DataAnalysis' }
      }
    ]
  },
  {
    path: '/customer',
    component: Layout,
    redirect: '/customer/list',
    meta: { title: '客户管理', icon: 'OfficeBuilding' },
    children: [
      {
        path: 'list',
        name: 'CustomerList',
        component: () => import('@/views/customer/index.vue'),
        meta: { title: '客户列表' }
      },
      {
        path: 'contact',
        name: 'CustomerContact',
        component: () => import('@/views/contact/index.vue'),
        meta: { title: '联系人', icon: 'UserFilled' }
      },
      {
        path: 'detail/:id',
        name: 'CustomerDetail',
        component: () => import('@/views/customer/detail.vue'),
        meta: { title: '客户详情', hidden: true }
      }
    ]
  },
  {
    path: '/opportunity',
    component: Layout,
    redirect: '/opportunity/list',
    meta: { title: '商机管理', icon: 'Money' },
    children: [
      {
        path: 'list',
        name: 'OpportunityList',
        component: () => import('@/views/opportunity/index.vue'),
        meta: { title: '商机列表' }
      },
      {
        path: 'kanban',
        name: 'OpportunityKanban',
        component: () => import('@/views/opportunity/kanban.vue'),
        meta: { title: '商机看板' }
      }
    ]
  },
  {
    path: '/contract',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Contract',
        component: () => import('@/views/contract/index.vue'),
        meta: { title: '合同管理', icon: 'Document' }
      }
    ]
  },
  {
    path: '/invoice',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Invoice',
        component: () => import('@/views/invoice/index.vue'),
        meta: { title: '发票管理', icon: 'Receipt' }
      }
    ]
  },
  {
    path: '/activity',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Activity',
        component: () => import('@/views/activity/index.vue'),
        meta: { title: '活动记录', icon: 'Calendar' }
      }
    ]
  },
  {
    path: '/followup',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Followup',
        component: () => import('@/views/followup/index.vue'),
        meta: { title: '待办跟进', icon: 'Tickets' }
      }
    ]
  },
  {
    path: '/statistics',
    component: Layout,
    meta: { title: '数据分析', icon: 'DataLine' },
    children: [
      {
        path: '',
        name: 'Statistics',
        component: () => import('@/views/statistics/index.vue'),
        meta: { title: '统计分析' }
      }
    ]
  },
  {
    path: '/system',
    component: Layout,
    meta: { title: '系统管理', icon: 'Setting', admin: true },
    children: [
      {
        path: 'user',
        name: 'SystemUser',
        component: () => import('@/views/system/user.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'role',
        name: 'SystemRole',
        component: () => import('@/views/system/role.vue'),
        meta: { title: '角色管理' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes: [...constantRoutes, ...asyncRoutes],
  scrollBehavior: () => ({ left: 0, top: 0 })
})

// 路由守卫
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 易客CRM` : '易客CRM'
  const token = localStorage.getItem('crm_token')

  if (to.path === '/login') {
    if (token) {
      next('/dashboard')
    } else {
      next()
    }
    return
  }

  if (!token) {
    next('/login')
    return
  }

  if (to.meta.admin) {
    const userStr = localStorage.getItem('crm_user')
    if (userStr) {
      const user = JSON.parse(userStr)
      if (user.role !== 1 && user.role !== 'admin' && user.role !== '1') {
        next('/dashboard')
        return
      }
    }
  }

  next()
})

export default router
