const api = require('../../utils/api')
const store = require('../../utils/store')

Page({
  data: {
    tasks: [],
    activeTab: 'all',
    page: 1,
    pageSize: 20,
    loading: false,
    hasMore: true,
    filteredTasks: [],
    statusText: {
      pending: '等待中',
      processing: '处理中',
      completed: '已完成',
      failed: '失败'
    }
  },

  onShow: function () {
    this.setData({ tasks: [], page: 1, hasMore: true })
    this.loadTasks()
  },

  onReachBottom: function () {
    if (this.data.hasMore && !this.data.loading) {
      this.loadMore()
    }
  },

  loadTasks: function () {
    var that = this
    that.setData({ loading: true })

    api.listTasks({
      merchant_id: store.getMerchantId(),
      page: 1,
      page_size: that.data.pageSize
    }).then(function (res) {
      that.setData({ loading: false })
      if (res.code === 200 && res.data) {
        var tasks = res.data.tasks || []
        that.setData({
          tasks: tasks,
          page: 1,
          hasMore: tasks.length >= that.data.pageSize
        })
        that.applyFilter()
      }
    }).catch(function () {
      that.setData({ loading: false })
    })
  },

  loadMore: function () {
    var that = this
    if (that.data.loading) return
    that.setData({ loading: true })

    var nextPage = that.data.page + 1
    api.listTasks({
      merchant_id: store.getMerchantId(),
      page: nextPage,
      page_size: that.data.pageSize
    }).then(function (res) {
      that.setData({ loading: false })
      if (res.code === 200 && res.data) {
        var newTasks = res.data.tasks || []
        var allTasks = that.data.tasks.concat(newTasks)
        that.setData({
          tasks: allTasks,
          page: nextPage,
          hasMore: newTasks.length >= that.data.pageSize
        })
        that.applyFilter()
      }
    }).catch(function () {
      that.setData({ loading: false })
    })
  },

  switchTab: function (e) {
    this.setData({ activeTab: e.currentTarget.dataset.tab })
    this.applyFilter()
  },

  applyFilter: function () {
    var tab = this.data.activeTab
    var tasks = this.data.tasks
    if (tab === 'all') {
      this.setData({ filteredTasks: tasks })
    } else {
      this.setData({
        filteredTasks: tasks.filter(function (t) { return t.status === tab })
      })
    }
  },

  goDetail: function (e) {
    var id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/detail/detail?task_id=' + id })
  }
})
