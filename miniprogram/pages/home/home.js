var api = require('../../utils/api')
var store = require('../../utils/store')

Page({
  data: {
    merchantName: '',
    todayCount: 0,
    monthCount: 0,
    recentTasks: [],
    loading: true,
    statusText: {
      pending: '等待中',
      processing: '处理中',
      completed: '已完成',
      failed: '失败'
    }
  },

  onShow: function () {
    var that = this
    var merchantId = store.getMerchantId()
    that.setData({ merchantName: store.getMerchantName(), loading: true })

    if (!merchantId) {
      that.setData({ loading: false })
      return
    }

    api.listTasks({ merchant_id: merchantId, page: 1, page_size: 20 }).then(function (res) {
      if (res.code === 200 && res.data) {
        var tasks = res.data.tasks || []
        that.setData({
          recentTasks: tasks.slice(0, 3),
          monthCount: res.data.total || 0,
          loading: false
        })
      } else {
        that.setData({ loading: false })
      }
    }).catch(function () {
      that.setData({ loading: false })
    })

    api.getMerchant(merchantId).then(function (res) {
      if (res.code === 200 && res.data) {
        store.setMerchantName(res.data.name)
        that.setData({ merchantName: res.data.name })
      }
    })
  },

  goCreate: function () { wx.navigateTo({ url: '/pages/create/create' }) },
  goDetail: function (e) {
    wx.navigateTo({ url: '/pages/detail/detail?task_id=' + e.currentTarget.dataset.id })
  },
  goTasks: function () { wx.switchTab({ url: '/pages/tasks/tasks' }) },
  goSettings: function () { wx.navigateTo({ url: '/pages/settings/settings' }) }
})
