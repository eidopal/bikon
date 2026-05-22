const api = require('../../utils/api')
const store = require('../../utils/store')
const app = getApp()

Page({
  data: {
    loading: false
  },

  handleLogin: function () {
    var that = this
    if (that.data.loading) return

    that.setData({ loading: true })

    wx.login({
      success: function (loginRes) {
        if (!loginRes.code) {
          api.showError(null, '获取登录凭证失败')
          that.setData({ loading: false })
          return
        }

        api.code2session(loginRes.code).then(function (res) {
          that.setData({ loading: false })

          if (res.code !== 200 || !res.data || !res.data.token) {
            api.showError(null, res.msg || '登录失败，请稍后重试')
            return
          }

          store.saveLoginData(res.data)
          app.globalData.token = res.data.token
          app.globalData.userId = res.data.user_id
          app.globalData.merchantId = res.data.merchant_id || ''

          if (res.data.merchant_id) {
            wx.reLaunch({ url: '/pages/home/home' })
          } else {
            wx.reLaunch({ url: '/pages/register/register' })
          }
        }).catch(function (err) {
          that.setData({ loading: false })
          api.showError(err, '网络请求失败')
        })
      },
      fail: function () {
        that.setData({ loading: false })
        wx.showToast({ title: '微信登录失败', icon: 'none' })
      }
    })
  }
})
