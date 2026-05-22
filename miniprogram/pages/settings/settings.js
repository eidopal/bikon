const api = require('../../utils/api')
const store = require('../../utils/store')
const app = getApp()

Page({
  data: {
    merchantId: '',
    name: '',
    industryContext: '',
    brandSymbol: '',
    assets: [],
    saving: false
  },

  onShow: function () {
    var merchantId = store.getMerchantId()
    this.setData({ merchantId: merchantId })
    if (!merchantId) return

    api.getMerchant(merchantId).then(function (res) {
      if (res.code === 200 && res.data) {
        this.setData({
          name: res.data.name || '',
          industryContext: res.data.industry_context || '',
          brandSymbol: res.data.brand_symbol || ''
        })
      }
    }.bind(this)).catch(function () {})

    api.getBrandAssets(merchantId).then(function (res) {
      if (res.code === 200 && res.data) {
        this.setData({ assets: res.data })
      }
    }.bind(this)).catch(function () {})
  },

  onNameInput: function (e) { this.setData({ name: e.detail.value }) },
  onContextInput: function (e) { this.setData({ industryContext: e.detail.value }) },
  onBrandInput: function (e) { this.setData({ brandSymbol: e.detail.value }) },

  handleSave: function () {
    var that = this
    that.setData({ saving: true })

    api.updateMerchant(that.data.merchantId, {
      name: that.data.name,
      industry_context: that.data.industryContext,
      brand_symbol: that.data.brandSymbol
    }).then(function (res) {
      that.setData({ saving: false })
      if (res.code === 200) {
        store.setMerchantName(that.data.name)
        wx.showToast({ title: '保存成功', icon: 'success' })
      } else {
        api.showError(null, res.msg || '保存失败')
      }
    }).catch(function (err) {
      that.setData({ saving: false })
      api.showError(err, '保存失败')
    })
  },

  uploadAsset: function () {
    var that = this
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album'],
      success: function (res) {
        var filePath = res.tempFiles[0].tempFilePath
        wx.showLoading({ title: '上传中...' })
        api.uploadBrandAsset(that.data.merchantId, filePath, 'logo').then(function (res) {
          wx.hideLoading()
          if (res.code === 200) {
            wx.showToast({ title: '上传成功', icon: 'success' })
            that.onShow()
          }
        }).catch(function () {
          wx.hideLoading()
        })
      }
    })
  },

  handleLogout: function () {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出吗？',
      success: function (res) {
        if (res.confirm) {
          store.clearAll()
          app.globalData.token = ''
          app.globalData.merchantId = ''
          wx.reLaunch({ url: '/pages/login/login' })
        }
      }
    })
  }
})
