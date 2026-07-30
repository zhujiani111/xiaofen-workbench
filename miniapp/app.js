App({
  globalData: {
    userInfo: null,
    openid: ''
  },
  onLaunch() {
    wx.cloud.init({
      env: 'your-env-id', // 替换为你的云开发环境ID
      traceUser: true
    });
  }
});
