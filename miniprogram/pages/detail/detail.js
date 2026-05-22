const api = require('../../utils/api')

Page({
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
    wx.previewImage({
      urls: [url],
      current: url
    })
  }
})
