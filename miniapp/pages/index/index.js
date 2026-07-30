const app = getApp();
const db = wx.cloud.database();
const _ = db.command;

Page({
  data: {
    dateStr: '',
    hotCount: 8,
    todayKcal: 0,
    exDone: 0,
    exTotal: 4,
    monthExp: 0,
    readBooks: 0,
    engStreak: 0,
    diaryCount: 0,
    budgetRemain: '¥3000'
  },

  onShow() {
    this.updateDate();
    this.loadStats();
  },

  updateDate() {
    const n = new Date();
    const wd = ['日','一','二','三','四','五','六'];
    this.setData({
      dateStr: `${n.getFullYear()}年${n.getMonth()+1}月${n.getDate()}日 星期${wd[n.getDay()]} 🌸`
    });
  },

  async loadStats() {
    try {
      // 尝试从云数据库加载，失败则用本地存储
      const foodData = wx.getStorageSync('food') || { records: [] };
      const today = new Date().toISOString().slice(0, 10);
      const todayRecs = (foodData.records || []).filter(r => r.date === today);
      const kcal = todayRecs.reduce((s, r) => s + (r.kcal || 0), 0);

      const exData = wx.getStorageSync('exercise') || { wd: {} };
      const done = Object.values(exData.wd || {}).filter(Boolean).length;

      const finData = wx.getStorageSync('finance') || { records: [], budget: 3000 };
      const tm = today.slice(0, 7);
      const monthExp = (finData.records || [])
        .filter(r => r.date && r.date.startsWith(tm) && r.type === 'expense')
        .reduce((s, r) => s + (r.amount || 0), 0);

      const readData = wx.getStorageSync('reading') || { shelf: {} };
      const reading = Object.values(readData.shelf || {}).filter(b => !b.done).length;

      const engData = wx.getStorageSync('english') || { streak: 0 };
      const diaryData = wx.getStorageSync('diary') || { entries: [] };
      const budget = finData.budget || 3000;
      const remain = budget - monthExp;

      this.setData({
        todayKcal: kcal,
        exDone: done,
        monthExp: Math.round(monthExp),
        readBooks: reading,
        engStreak: engData.streak || 0,
        diaryCount: (diaryData.entries || []).length,
        budgetRemain: '¥' + remain.toFixed(0)
      });
    } catch(e) {
      console.log('加载统计数据失败', e);
    }
  },

  goPage(e) {
    const page = e.currentTarget.dataset.page;
    wx.switchTab({ url: '/pages/' + page + '/' + page });
  }
});
