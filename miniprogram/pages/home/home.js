const api = require('../../utils/api')
const store = require('../../utils/store')

Page({
  data: {
    merchantName: '',
    todayCount: 0,
    monthCount: 0,
    recentTasks: [],
    statusText: {
      pending: '等待中',
      processing: '处理中',
      completed: '已完成',
      failed: '失败'
    }
  },

  onShow: function () {
    var merchantId = store.getMerchantId()
    this.setData({ merchantName: store.getMerchantName() })

    if (!merchantId) return

    api.listTasks({ merchant_id: merchantId, page: 1, page_size: 3 })
      .then(function (res) {
        if (res.code === 200 && res.data) {
          this.setData({
            recentTasks: res.data.tasks || [],
            monthCount: res.data.total || 0
          })
        }
      }.bind(this))
      .catch(function () {})

    api.listTasks({ merchant_id: merchantId, page: 1, page_size: 20 })
      .then(function (res) {
        if (res.code === 200 && res.data) {
          this.setData({ monthCount: res.data.total || 0 })
        }
      }.bind(this))
      .catch(function () {})

    api.getMerchant(merchantId)
      .then(function (res) {
        if (res.code === 200 && res.data) {
          store.setMerchantName(res.data.name)
          this.setData({ merchantName: res.data.name })
        }
      }.bind(this))
      .catch(function () {})
  },

  goCreate: function () {
    wx.navigateTo({ url: '/pages/create/create' })
  },

  goDetail: function (e) {
    var id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/detail/detail?task_id=' + id })
  },

  goSettings: function () {
    wx.navigateTo({ url: '/pages/settings/settings' })
  }
})
