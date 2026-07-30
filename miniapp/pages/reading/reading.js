const ALL_BOOKS=[
  {id:'prince',title:'小王子',author:'圣-埃克苏佩里',emoji:'🌹',cat:'经典',chapters:7,desc:'全球销量仅次于《圣经》的治愈经典。'},
  {id:'renjian',title:'人间词话',author:'王国维',emoji:'📜',cat:'国学',chapters:4,desc:'"人生三境界"就出自这里。'},
  {id:'fusheng',title:'浮生六记',author:'沈复',emoji:'🏮',cat:'古典',chapters:2,desc:'中国文学史上最可爱的女人。'},
  {id:'courage',title:'被讨厌的勇气',author:'岸见一郎',emoji:'💪',cat:'心理',chapters:5,desc:'"课题分离"对职场关系极有帮助。'},
  {id:'atomic',title:'原子习惯',author:'詹姆斯·克利尔',emoji:'⚛️',cat:'成长',chapters:5,desc:'每天进步1%，一年后37倍。'},
  {id:'nonviolent',title:'非暴力沟通',author:'马歇尔·卢森堡',emoji:'🗣️',cat:'职场',chapters:4,desc:'公众号运营必备沟通技巧。'},
  {id:'qiuyuan',title:'秋园',author:'杨本芬',emoji:'📖',cat:'文学',chapters:3,desc:'80岁奶奶写的女性家族史。'},
  {id:'operate',title:'运营之光',author:'黄有璨',emoji:'💡',cat:'职场',chapters:4,desc:'运营方法论直接用到公众号。'},
  {id:'findme',title:'也许你该找个人聊聊',author:'洛莉·戈特利布',emoji:'🛋️',cat:'心理',chapters:5,desc:'心理治疗师的回忆录。'},
  {id:'deepwork',title:'深度工作',author:'卡尔·纽波特',emoji:'🧠',cat:'成长',chapters:5,desc:'分心时代的专注力。'}
];

const QUOTES=[
  {text:'我们终其一生，就是要摆脱他人的期待，找到真正的自己。',src:'《无声告白》'},
  {text:'你不需要成为更好的自己，你只需要更好地成为自己。',src:'佚名'},
  {text:'种一棵树最好的时间是十年前，其次是现在。',src:'非洲谚语'},
  {text:'不必匆忙，不必火花四溅，不必成为别人，只需做自己。',src:'伍尔夫'},
  {text:'一个人知道自己为什么而活，就可以忍受任何一种生活。',src:'尼采'}
];

// 内置搜书库
const SEARCH_DB=[
  {id:'honglou',title:'红楼梦',author:'曹雪芹'},{id:'sanguo',title:'三国演义',author:'罗贯中'},
  {id:'xiyou',title:'西游记',author:'吴承恩'},{id:'shuihu',title:'水浒传',author:'施耐庵'},
  {id:'lunyu',title:'论语',author:'孔子'},{id:'daodejing',title:'道德经',author:'老子'},
  {id:'sunzi',title:'孙子兵法',author:'孙武'},{id:'liaozhai',title:'聊斋志异',author:'蒲松龄'},
  {id:'weicheng',title:'围城',author:'钱钟书'},{id:'biancheng',title:'边城',author:'沈从文'},
  {id:'luotuo',title:'骆驼祥子',author:'老舍'},{id:'nahan',title:'呐喊',author:'鲁迅'}
];

Page({
  data:{
    tab:'recommend',recBooks:[],reading:[],done:[],sq:'',searchResults:[],searching:false,
    quote:QUOTES[0],notes:[],noteText:''
  },
  onShow(){this.loadAll()},
  loadAll(){
    const data=wx.getStorageSync('reading')||{shelf:{},notes:[],recIdx:0};
    const shelf=data.shelf||{};
    const recIdx=data.recIdx||0;
    const recBooks=[];
    for(let i=0;i<6;i++)recBooks.push({...ALL_BOOKS[(recIdx+i)%ALL_BOOKS.length],onShelf:!!shelf[ALL_BOOKS[(recIdx+i)%ALL_BOOKS.length].id]});

    const reading=Object.entries(shelf).filter(([k,v])=>!v.done).map(([k,v])=>({id:k,...v,pct:Math.round((v.progress||0)*100)}));
    const done=Object.entries(shelf).filter(([k,v])=>v.done).map(([k,v])=>({id:k,...v,pct:100}));
    const qi=QUOTES[new Date().getDate()%QUOTES.length];
    const notes=(data.notes||[]).slice(-5).reverse();

    this.setData({recBooks,reading,done,quote:qi,notes});
  },
  switchTab(e){this.setData({tab:e.currentTarget.dataset.tab});if(e.currentTarget.dataset.tab==='shelf')this.loadAll()},
  refreshBooks(){
    const data=wx.getStorageSync('reading')||{shelf:{},notes:[],recIdx:0};
    data.recIdx=(data.recIdx||0)+3;
    wx.setStorageSync('reading',data);
    this.loadAll();
    wx.showToast({title:'已换一批'});
  },
  addShelf(e){
    const id=e.currentTarget.dataset.id;
    const data=wx.getStorageSync('reading')||{shelf:{},notes:[],recIdx:0};
    if(data.shelf[id]){wx.showToast({title:'已在书架'});return}
    const b=ALL_BOOKS.find(x=>x.id===id)||{id,title:'未知',author:'',emoji:'📖',cat:'',chapters:1};
    data.shelf[id]={title:b.title,author:b.author,emoji:b.emoji,cat:b.cat,chapters:b.chapters,progress:0,done:false,added:new Date().toISOString().slice(0,10)};
    wx.setStorageSync('reading',data);
    this.loadAll();
    wx.showToast({title:'📚已加入书架'});
  },
  readBook(e){
    const id=e.currentTarget.dataset.id;
    wx.showModal({title:'📖 阅读',content:'完整阅读功能需要在微信开发者工具中预览。\n点击确定打开本书内容。',showCancel:false,confirmText:'开始阅读',success:()=>{
      const data=wx.getStorageSync('reading')||{shelf:{}};
      if(data.shelf[id]){data.shelf[id].progress=Math.min((data.shelf[id].progress||0)+0.2,1);wx.setStorageSync('reading',data)}
      this.loadAll();
    }});
  },
  onSearchInput(e){this.setData({sq:e.detail.value})},
  doSearch(){
    const q=this.data.sq.trim().toLowerCase();
    if(!q||q.length<2){wx.showToast({title:'请输入至少2个字',icon:'none'});return}
    this.setData({searching:true});
    const results=SEARCH_DB.filter(b=>b.title.includes(q)||b.author.includes(q)).map(b=>{
      const data=wx.getStorageSync('reading')||{shelf:{}};
      return{...b,onShelf:!!data.shelf[b.id]};
    });
    setTimeout(()=>this.setData({searchResults:results,searching:false}),300);
  },
  addSearchToShelf(e){
    const {id,title,author}=e.currentTarget.dataset;
    const data=wx.getStorageSync('reading')||{shelf:{}};
    if(data.shelf[id]){wx.showToast({title:'已在书架'});return}
    data.shelf[id]={title,author,emoji:'📖',cat:'',chapters:1,progress:0,done:false,added:new Date().toISOString().slice(0,10)};
    wx.setStorageSync('reading',data);
    this.doSearch();
    this.loadAll();
    wx.showToast({title:'📚已加入书架'});
  },
  onNoteInput(e){this.setData({noteText:e.detail.value})},
  saveNote(){
    const t=this.data.noteText.trim();
    if(!t){wx.showToast({title:'写点什么吧~',icon:'none'});return}
    const data=wx.getStorageSync('reading')||{shelf:{},notes:[],recIdx:0};
    data.notes=data.notes||[];
    data.notes.push({date:new Date().toISOString().slice(0,10),text:t});
    wx.setStorageSync('reading',data);
    this.setData({noteText:''});
    this.loadAll();
    wx.showToast({title:'✅已保存'});
  }
});
