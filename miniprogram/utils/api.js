const store = require('./store.js')

const BASE_URL = 'http://localhost:8000'

function request(method, path, data, options) {
  options = options || {}
  const header = { 'Content-Type': 'application/json' }
  const token = store.getToken()
  if (token) {
    header['Authorization'] = 'Bearer ' + token
  }

  const config = {
    url: BASE_URL + path,
    method: method,
    header: header,
    timeout: options.timeout || 30000
  }
  if (method === 'GET') {
    config.data = data
  } else {
    config.data = data
  }

  return new Promise(function (resolve, reject) {
    wx.request(Object.assign(config, {
      success: function (res) {
        if (res.statusCode === 401) {
          store.clearAll()
          wx.reLaunch({ url: '/pages/login/login' })
          reject(new Error('登录已过期'))
          return
        }
        resolve(res.data)
      },
      fail: function (err) { reject(err) }
    }))
  })
}

function uploadSingleFile(path, filePath, formData) {
  var token = store.getToken()
  return new Promise(function (resolve, reject) {
    wx.uploadFile({
      url: BASE_URL + path,
      filePath: filePath,
      name: 'file',
      header: { 'Authorization': 'Bearer ' + token },
      formData: formData || {},
      success: function (res) {
        if (res.statusCode === 401) {
          store.clearAll()
          wx.reLaunch({ url: '/pages/login/login' })
          reject(new Error('登录已过期'))
          return
        }
        try { resolve(JSON.parse(res.data)) }
        catch (e) { reject(new Error('解析响应失败')) }
      },
      fail: function (err) { reject(err) }
    })
  })
}

// Upload multiple images in parallel, returns array of URLs
function uploadImages(filePaths) {
  var tasks = filePaths.map(function (fp) {
    return uploadSingleFile('/api/v1/production/upload-image', fp).then(function (res) {
      return res.data && res.data.url ? res.data.url : null
    })
  })
  return Promise.all(tasks)
}

// ========== WeChat ==========

function code2session(code) {
  return request('POST', '/api/v1/wechat/code2session', { code: code })
}

// ========== Merchant ==========

function registerMerchant(data) {
  return request('POST', '/api/v1/merchant/register', data)
}

function getMerchant(merchantId) {
  return request('GET', '/api/v1/merchant/' + merchantId)
}

function updateMerchant(merchantId, data) {
  return request('PUT', '/api/v1/merchant/' + merchantId + '/profile', data)
}

function uploadBrandAsset(merchantId, filePath, assetType) {
  return new Promise(function (resolve, reject) {
    var token = store.getToken()
    wx.uploadFile({
      url: BASE_URL + '/api/v1/merchant/' + merchantId + '/brand-asset',
      filePath: filePath,
      name: 'file',
      header: { 'Authorization': 'Bearer ' + token },
      formData: { asset_type: assetType || 'logo' },
      success: function (res) {
        try { resolve(JSON.parse(res.data)) }
        catch (e) { reject(new Error('解析响应失败')) }
      },
      fail: function (err) { reject(err) }
    })
  })
}

function getBrandAssets(merchantId) {
  return request('GET', '/api/v1/merchant/' + merchantId + '/brand-assets')
}

// ========== Production ==========

function submitTask(payload) {
  return request('POST', '/api/v1/production/submit-task', payload)
}

function getTaskResult(taskId) {
  return request('GET', '/api/v1/production/task-result/' + taskId)
}

function listTasks(params) {
  var query = []
  if (params.merchant_id) query.push('merchant_id=' + params.merchant_id)
  if (params.page) query.push('page=' + params.page)
  if (params.page_size) query.push('page_size=' + params.page_size)
  var path = '/api/v1/production/tasks'
  if (query.length) path += '?' + query.join('&')
  return request('GET', path)
}

// ========== Helper ==========

function showError(err, defaultMsg) {
  var msg = (err && err.detail) || (err && err.message) || defaultMsg || '请求失败'
  wx.showToast({ title: String(msg).substring(0, 50), icon: 'none' })
}

module.exports = {
  BASE_URL: BASE_URL,
  code2session: code2session,
  registerMerchant: registerMerchant,
  getMerchant: getMerchant,
  updateMerchant: updateMerchant,
  uploadBrandAsset: uploadBrandAsset,
  getBrandAssets: getBrandAssets,
  uploadImages: uploadImages,
  submitTask: submitTask,
  getTaskResult: getTaskResult,
  listTasks: listTasks,
  showError: showError
}
