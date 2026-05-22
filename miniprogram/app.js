const store = require('./utils/store')

App({
  globalData: {
    token: '',
    userId: '',
    merchantId: '',
    userInfo: null,
    baseUrl: 'http://192.168.0.59:8000'
  },

  onLaunch() {
    const token = store.getToken()
    if (token) {
      this.globalData.token = token
      this.globalData.userId = store.getUserId()
      this.globalData.merchantId = store.getMerchantId()
    }
  },

  checkLogin() {
    if (!this.globalData.token) {
      wx.reLaunch({ url: '/pages/login/login' })
      return false
    }
    if (!this.globalData.merchantId) {
      wx.reLaunch({ url: '/pages/register/register' })
      return false
    }
    return true
  }
})
