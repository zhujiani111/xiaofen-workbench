const HOT = [
  {tag:'news',tt:'新闻',title:'35岁+女性健康：更年期提前的5个信号',desc:'多篇医学报道聚焦围绝经期，与「中女健康」选题高度相关。可科普+真实案例切入。',src:'丁香医生',tm:'2小时前'},
  {tag:'trend',tt:'小红书',title:'「暑假回老家」话题爆火，怀旧+亲子共鸣',desc:'#暑假农村老家#阅读量破2亿。年糕妈妈已发文，数据优异。可做系列延伸。',src:'小红书',tm:'3小时前'},
  {tag:'competitor',tt:'竞品',title:'年糕妈妈近3天爆款分析',desc:'主号「中女情感+健康警示+育儿故事」三线并进。离婚话题、明星健康八卦类表现突出。',src:'年糕妈妈',tm:'今天'},
  {tag:'idea',tt:'灵感',title:'「更年期妈妈 vs 青春期娃」双期碰撞',desc:'重点方向。可做系列：情绪管理、沟通技巧、身体变化科普。差异化强。',src:'选题建议',tm:'新'},
  {tag:'trend',tt:'抖音',title:'「35岁小肚子为什么难减」热门',desc:'年糕妈妈已发相关文章。可做视频延伸或「30+体态管理」系列。',src:'抖音',tm:'5小时前'},
  {tag:'competitor',tt:'同类',title:'丁香妈妈「暑假儿童安全」系列 8w+',desc:'关注差异化——年糕妈妈优势在「妈妈视角+家庭故事」。',src:'丁香妈妈',tm:'1天前'},
  {tag:'news',tt:'新闻',title:'知名果汁品牌被曝"造假"已售10万瓶',desc:'年糕妈妈已跟进。消费安全选题可常态化。',src:'央视财经',tm:'2天前'},
  {tag:'idea',tt:'灵感',title:'「暑假三胎家庭的崩溃日常」UGC方向',desc:'结合三胎文章思路，发起征集引导UGC互动。',src:'选题建议',tm:'新'}
];

Page({
  data:{
    hotList:[],pinnedList:[],newsCount:0,trendCount:0,compCount:0,pinnedCount:0,isMonday:false
  },
  onShow(){this.loadData()},
  loadData(){
    const pinned=wx.getStorageSync('hot_pinned')||[];
    const isMonday=new Date().getDay()===1;
    const list=HOT.map((item,i)=>({...item,origIdx:i,isPinned:pinned.includes(i)}));
    const pinnedList=list.filter(item=>item.isPinned).map(item=>({...item}));
    this.setData({
      hotList:list,
      pinnedList,
      newsCount:HOT.filter(t=>t.tag==='news').length,
      trendCount:HOT.filter(t=>t.tag==='trend').length,
      compCount:HOT.filter(t=>t.tag==='competitor').length,
      pinnedCount:pinned.length,
      isMonday
    });
  },
  refresh(){
    wx.showToast({title:'已刷新',icon:'success',duration:1000});
    HOT.forEach(t=>{if(Math.random()>.7)t.tm='刚刚更新'});
    this.loadData();
  },
  togglePin(e){
    const idx=e.currentTarget.dataset.idx;
    let pinned=wx.getStorageSync('hot_pinned')||[];
    const pos=pinned.indexOf(idx);
    if(pos>-1)pinned.splice(pos,1);else pinned.push(idx);
    wx.setStorageSync('hot_pinned',pinned);
    this.loadData();
    wx.showToast({title:pos>-1?'已取消':'⭐已收藏',icon:'none'});
  },
  chatTopic(e){
    wx.showModal({
      title:'💬 AI选题助手',
      editable:true,
      placeholderText:'说说你的想法...',
      success:res=>{
        if(res.content){
          const replies=['📌标题1：数据+悬念\n📌标题2：故事+共鸣\n📌互动：结尾投票引导UGC\n\n哪个方向更符合？','🎯钩子："原来我不是一个人"\n🎯结构：故事→数据→方案→互动\n🎯差异化：闺蜜分享+干货路线','💡试试"热点引入→科普→自查"公式\n💡工作日发干货，周末发情感'];
          wx.showModal({title:'🤖 AI回复',content:replies[Math.floor(Math.random()*replies.length)],showCancel:false});
        }
      }
    });
  }
});
