const api = require('../../utils/api')
const store = require('../../utils/store')
const app = getApp()

Page({
  data: {
    name: '',
    context: '',
    brandSymbol: '',
    loading: false
  },

  onNameInput: function (e) {
    this.setData({ name: e.detail.value })
  },
  onContextInput: function (e) {
    this.setData({ context: e.detail.value })
  },
  onBrandInput: function (e) {
    this.setData({ brandSymbol: e.detail.value })
  },

  handleRegister: function () {
    var that = this
    if (!that.data.name.trim()) {
      wx.showToast({ title: '请输入门店名称', icon: 'none' })
      return
    }
    if (!that.data.context.trim()) {
      wx.showToast({ title: '请输入行业描述', icon: 'none' })
      return
    }
    if (that.data.loading) return

    that.setData({ loading: true })

    api.registerMerchant({
      name: that.data.name.trim(),
      industry_context: that.data.context.trim(),
      brand_symbol: that.data.brandSymbol.trim()
    }).then(function (res) {
      that.setData({ loading: false })
      if (res.code !== 200 || !res.data || !res.data.merchant_id) {
        api.showError(null, res.msg || '注册失败')
        return
      }
      store.setMerchantId(res.data.merchant_id)
      store.setMerchantName(res.data.name)
      app.globalData.merchantId = res.data.merchant_id
      wx.reLaunch({ url: '/pages/home/home' })
    }).catch(function (err) {
      that.setData({ loading: false })
      api.showError(err, '网络请求失败')
    })
  }
})
