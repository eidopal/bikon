const KEYS = {
  TOKEN: 'bikon_token',
  USER_ID: 'bikon_user_id',
  MERCHANT_ID: 'bikon_merchant_id',
  OPENID: 'bikon_openid',
  MERCHANT_NAME: 'bikon_merchant_name'
}

function getToken() {
  return wx.getStorageSync(KEYS.TOKEN) || ''
}

function setToken(token) {
  wx.setStorageSync(KEYS.TOKEN, token)
}

function getUserId() {
  return wx.getStorageSync(KEYS.USER_ID) || ''
}

function setUserId(id) {
  wx.setStorageSync(KEYS.USER_ID, id)
}

function getMerchantId() {
  return wx.getStorageSync(KEYS.MERCHANT_ID) || ''
}

function setMerchantId(id) {
  wx.setStorageSync(KEYS.MERCHANT_ID, id)
}

function setOpenid(openid) {
  wx.setStorageSync(KEYS.OPENID, openid)
}

function getOpenid() {
  return wx.getStorageSync(KEYS.OPENID) || ''
}

function setMerchantName(name) {
  wx.setStorageSync(KEYS.MERCHANT_NAME, name)
}

function getMerchantName() {
  return wx.getStorageSync(KEYS.MERCHANT_NAME) || ''
}

function saveLoginData(data) {
  setToken(data.token)
  setUserId(data.user_id)
  setOpenid(data.openid || '')
  if (data.merchant_id) {
    setMerchantId(data.merchant_id)
  }
}

function clearAll() {
  wx.clearStorageSync()
}

module.exports = {
  getToken, setToken,
  getUserId, setUserId,
  getMerchantId, setMerchantId,
  setOpenid, getOpenid,
  setMerchantName, getMerchantName,
  saveLoginData,
  clearAll
}
