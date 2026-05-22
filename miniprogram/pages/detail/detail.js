const api = require('../../utils/api')

Page({
  onShareAppMessage: function () {
    var images = this.data.result.visual_assets.processed_images || []
    return {
      title: 'BIKON 生成的水印图片',
      path: '/pages/detail/detail?task_id=' + this.data.taskId,
      imageUrl: images[0] || ''
    }
  },

  data: {
    taskId: '',
    taskStatus: '',
    loading: true,
    result: { copywriting: {}, visual_assets: { processed_images: [] } },
    errorMsg: '',
    statusText: {
      PENDING: '等待处理',
      PROCESSING: 'AI 生成中',
      COMPLETED: '生成完成',
      FAILED: '处理失败',
      NOT_FOUND: '任务不存在'
    }
  },

  onLoad: function (options) {
    if (options.task_id) {
      this.setData({ taskId: options.task_id })
      this.fetchResult()
    }
  },

  fetchResult: function () {
    var that = this
    that.setData({ loading: true })

    api.getTaskResult(that.data.taskId).then(function (res) {
      if (res.code === 200 && res.data) {
        var data = res.data
        var status = data.task_status || 'PENDING'
        that.setData({
          taskStatus: status,
          loading: false,
          result: data,
          errorMsg: (data.error || '')
        })

        if (status === 'PROCESSING' || status === 'PENDING') {
          setTimeout(function () { that.fetchResult() }, 3000)
        }
      } else if (res.code === 404) {
        that.setData({ taskStatus: 'NOT_FOUND', loading: false })
      }
    }).catch(function (err) {
      that.setData({ loading: false })
      api.showError(err, '获取任务结果失败')
    })
  },

  refresh: function () {
    this.fetchResult()
  },

  copyText: function (e) {
    var text = e.currentTarget.dataset.text
    wx.setClipboardData({
      data: text,
      success: function () {
        wx.showToast({ title: '文案已复制', icon: 'success' })
      }
    })
  },

  previewImage: function (e) {
    var url = e.currentTarget.dataset.url
    var allUrls = this.data.result.visual_assets.processed_images || [url]
    wx.previewImage({
      urls: allUrls,
      current: url
    })
  },

  saveImage: function (e) {
    var url = e.currentTarget.dataset.url
    wx.showLoading({ title: '保存中...' })
    wx.downloadFile({
      url: url,
      success: function (res) {
        wx.saveImageToPhotosAlbum({
          filePath: res.tempFilePath,
          success: function () {
            wx.hideLoading()
            wx.showToast({ title: '已保存到相册', icon: 'success' })
          },
          fail: function () {
            wx.hideLoading()
            wx.showToast({ title: '请授权相册权限', icon: 'none' })
          }
        })
      },
      fail: function () {
        wx.hideLoading()
        wx.showToast({ title: '下载失败，请重试', icon: 'none' })
      }
    })
  },

  saveAllImages: function () {
    var urls = this.data.result.visual_assets.processed_images || []
    if (!urls.length) return
    var that = this
    wx.showLoading({ title: '保存中 1/' + urls.length })

    function saveNext(index) {
      if (index >= urls.length) {
        wx.hideLoading()
        wx.showToast({ title: '全部已保存到相册', icon: 'success' })
        return
      }
      wx.showLoading({ title: '保存中 ' + (index + 1) + '/' + urls.length })
      wx.downloadFile({
        url: urls[index],
        success: function (res) {
          wx.saveImageToPhotosAlbum({
            filePath: res.tempFilePath,
            success: function () { saveNext(index + 1) },
            fail: function () {
              wx.showToast({ title: '请授权相册权限', icon: 'none' })
              wx.hideLoading()
            }
          })
        },
        fail: function () {
          saveNext(index + 1)
        }
      })
    }
    saveNext(0)
  },

  copyAllAndGo: function (e) {
    var platform = e.currentTarget.dataset.platform
    var result = this.data.result.copywriting || {}
    var text = ''

    if (platform === 'xhs' && result.xiaohongshu) {
      text = result.xiaohongshu.text
      if (result.xiaohongshu.tags) {
        text += '\n\n' + result.xiaohongshu.tags.join(' ')
      }
    } else if (platform === 'wechat' && result.wechat_moments) {
      text = result.wechat_moments.text
    }

    if (!text) {
      wx.showToast({ title: '暂无可复制文案', icon: 'none' })
      return
    }

    wx.setClipboardData({
      data: text,
      success: function () {
        wx.showModal({
          title: '文案已复制',
          content: platform === 'xhs' ? '已复制小红书文案，去小红书 App 发布吧' : '已复制朋友圈文案，去微信发布吧',
          showCancel: false,
          confirmText: '好的'
        })
      }
    })
  }
})
