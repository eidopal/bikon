const api = require('../../utils/api')
const store = require('../../utils/store')

Page({
  data: {
    images: [],
    targets: { wechat: true, xiaohongshu: true },
    watermarkText: '',
    audioUrl: '',
    industryContext: '',
    submitting: false
  },

  chooseImages: function () {
    var that = this
    var remaining = 9 - that.data.images.length
    if (remaining <= 0) return

    wx.chooseMedia({
      count: remaining,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      success: function (res) {
        var newImages = res.tempFiles.map(function (f) { return f.tempFilePath })
        that.setData({ images: that.data.images.concat(newImages) })
      }
    })
  },

  removeImage: function (e) {
    var idx = e.currentTarget.dataset.index
    var images = this.data.images
    images.splice(idx, 1)
    this.setData({ images: images })
  },

  toggleTarget: function (e) {
    var key = e.currentTarget.dataset.key
    var targets = this.data.targets
    targets[key] = !targets[key]
    this.setData({ targets: targets })
  },

  onWatermarkInput: function (e) {
    this.setData({ watermarkText: e.detail.value })
  },

  onAudioUrlInput: function (e) {
    this.setData({ audioUrl: e.detail.value })
  },

  onContextInput: function (e) {
    this.setData({ industryContext: e.detail.value })
  },

  handleSubmit: function () {
    var that = this
    if (!that.data.images.length) {
      wx.showToast({ title: '请先选择图片', icon: 'none' })
      return
    }
    if (that.data.submitting) return

    that.setData({ submitting: true })
    wx.showLoading({ title: '上传图片中...' })

    api.uploadImages(that.data.images).then(function (urls) {
      var validUrls = urls.filter(function (u) { return u !== null })
      if (!validUrls.length) {
        wx.hideLoading()
        that.setData({ submitting: false })
        wx.showToast({ title: '图片上传失败', icon: 'none' })
        return
      }

      wx.showLoading({ title: '提交任务中...' })

      var targetList = []
      if (that.data.targets.wechat) targetList.push('wechat_moments')
      if (that.data.targets.xiaohongshu) targetList.push('xiaohongshu')
      if (!targetList.length) targetList.push('wechat_moments')

      api.submitTask({
        merchant_id: store.getMerchantId(),
        industry_context: that.data.industryContext || '',
        inputs: { images: validUrls, audio_url: that.data.audioUrl || '' },
        copywriting_targets: targetList,
        watermark_text: that.data.watermarkText || 'BIKON'
      }).then(function (res) {
        wx.hideLoading()
        that.setData({ submitting: false })

        if (res.code === 200 && res.data && res.data.task_id) {
          wx.showToast({ title: '任务已提交', icon: 'success' })
          wx.navigateTo({ url: '/pages/detail/detail?task_id=' + res.data.task_id })
        } else {
          api.showError(null, res.msg || '提交失败')
        }
      }).catch(function (err) {
        wx.hideLoading()
        that.setData({ submitting: false })
        api.showError(err, '提交失败')
      })
    }).catch(function (err) {
      wx.hideLoading()
      that.setData({ submitting: false })
      api.showError(err, '图片上传失败')
    })
  }
})
