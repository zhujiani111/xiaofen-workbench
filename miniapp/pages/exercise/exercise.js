const PLAN=[
  {day:'周一',type:'有氧',focus:'🚴‍♀️单车',items:[{name:'骑单车',dur:'30-40分钟'},{name:'拉伸',dur:'5分钟',link:'https://www.bilibili.com/video/BV1jJ4m1N7nN'}],active:true},
  {day:'周二',type:'休息',focus:'🧘‍♀️放松',items:[{name:'睡前拉伸',dur:'10分钟',link:'https://www.bilibili.com/video/BV1Li4y1d7XV'}],active:false},
  {day:'周三',type:'力量',focus:'💪居家',items:[{name:'帕梅拉15分钟',dur:'15分钟',link:'https://www.bilibili.com/video/BV1Wh411m7eG'},{name:'平板支撑3组',dur:'每组30秒'},{name:'按摩滚轮',dur:'5分钟'}],active:true},
  {day:'周四',type:'休息',focus:'🛀恢复',items:[{name:'散步或拉伸',dur:'15分钟'}],active:false},
  {day:'周五',type:'有氧',focus:'🚴‍♀️单车',items:[{name:'骑单车',dur:'30-40分钟'},{name:'按摩滚轮',dur:'5分钟'}],active:true},
  {day:'周六',type:'综合',focus:'🌿自由',items:[{name:'快走/慢跑',dur:'30分钟'},{name:'瑜伽拉伸',dur:'15分钟',link:'https://www.bilibili.com/video/BV1Li4y1d7XV'}],active:true},
  {day:'周日',type:'休息',focus:'🌸放松',items:[{name:'按摩滚轮',dur:'10分钟'}],active:false}
];

Page({
  data:{plan:PLAN,wd:{},doneCount:0,activeCount:4,streak:0,todayIdx:0,steps:0},
  onShow(){
    const data=wx.getStorageSync('exercise')||{wd:{},streak:0};
    const now=new Date();
    const todayIdx=(now.getDay()+6)%7;
    const doneCount=Object.values(data.wd||{}).filter(Boolean).length;

    // 获取微信运动步数
    wx.getWeRunData({
      success:res=>{
        // 微信运动需要解密，这里先显示占位
        this.setData({steps:'--'});
      },
      fail:()=>{this.setData({steps:'需授权'});}
    });

    this.setData({
      wd:data.wd||{},
      doneCount,
      streak:data.streak||0,
      todayIdx,
      plan:PLAN
    });
  },
  toggle(e){
    const key=e.currentTarget.dataset.key;
    const data=wx.getStorageSync('exercise')||{wd:{},streak:0};
    data.wd=data.wd||{};
    data.wd[key]=!data.wd[key];
    wx.setStorageSync('exercise',data);
    const doneCount=Object.values(data.wd).filter(Boolean).length;
    this.setData({wd:data.wd,doneCount});
    wx.showToast({title:data.wd[key]?'✅完成':'已取消'});
  },
  openLink(e){
    wx.setClipboardData({data:e.currentTarget.dataset.link});
    wx.showToast({title:'链接已复制，去B站粘贴打开'});
  }
});
