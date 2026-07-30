const FDB={
  '米饭':{k:116,p:2.6,f:0.3,c:25.9,fb:0.3},'馒头':{k:223,p:7,f:1.1,c:44,fb:1.3},'面条':{k:110,p:3.5,f:0.3,c:22,fb:0.4},'鸡蛋':{k:144,p:13.3,f:8.8,c:2.8,fb:0},'牛奶':{k:54,p:3,f:3.2,c:3.4,fb:0},'豆浆':{k:16,p:1.8,f:0.7,c:1.1,fb:0.5},'鸡胸肉':{k:133,p:19.4,f:5,c:2.5,fb:0},'牛肉':{k:125,p:19.9,f:4.2,c:2,fb:0},'鱼肉':{k:123,p:18,f:5,c:1.5,fb:0},'虾':{k:93,p:18.6,f:0.8,c:2.8,fb:0},'番茄':{k:20,p:0.9,f:0.2,c:4,fb:0.5},'黄瓜':{k:16,p:0.8,f:0.2,c:2.9,fb:0.5},'西兰花':{k:36,p:4.1,f:0.6,c:4.3,fb:1.6},'生菜':{k:16,p:1.3,f:0.3,c:2,fb:0.7},'菠菜':{k:28,p:2.6,f:0.3,c:4.5,fb:1.7},'土豆':{k:81,p:2,f:0.2,c:17.8,fb:0.7},'苹果':{k:53,p:0.2,f:0.2,c:13.5,fb:1.2},'香蕉':{k:93,p:1.4,f:0.2,c:22,fb:1.2},'橙子':{k:48,p:0.8,f:0.2,c:11.1,fb:0.6},'酸奶':{k:72,p:2.5,f:2.7,c:9.3,fb:0},'咖啡':{k:2,p:0.1,f:0,c:0.3,fb:0},'番茄炒蛋':{k:85,p:5,f:4,c:6,fb:0.8},'清蒸鱼':{k:110,p:17,f:4,c:1,fb:0},'炒青菜':{k:45,p:2,f:2.5,c:4,fb:1.5},'红烧肉':{k:340,p:10,f:30,c:8,fb:0},'宫保鸡丁':{k:175,p:15,f:10,c:8,fb:0.5},'麻婆豆腐':{k:85,p:6,f:5,c:4,fb:0.5},'饺子':{k:220,p:8,f:7,c:30,fb:1},'沙拉':{k:60,p:3,f:3,c:6,fb:3},'三明治':{k:250,p:10,f:10,c:30,fb:2},'火锅':{k:300,p:20,f:20,c:15,fb:2},'坚果':{k:560,p:20,f:45,c:20,fb:8},'奶茶':{k:65,p:0.5,f:2,c:11,fb:0},'蒜蓉西兰花':{k:42,p:4,f:1,c:5,fb:2},'鸡胸肉炒青椒':{k:95,p:14,f:4,c:3,fb:1},'牛肉炒洋葱':{k:130,p:16,f:5,c:6,fb:1},'杂粮饭':{k:100,p:3,f:1,c:22,fb:2},'清蒸鲈鱼':{k:105,p:18,f:3.5,c:1,fb:0},'虾仁豆腐煲':{k:65,p:8,f:2.5,c:3,fb:0.5},'白灼生菜':{k:20,p:1.5,f:0.5,c:2.5,fb:1},'蒸南瓜':{k:22,p:0.7,f:0.1,c:5.3,fb:0.8},'凉拌黄瓜':{k:20,p:1,f:0.5,c:3,fb:1},'紫菜蛋花汤':{k:30,p:3,f:1,c:2,fb:0.3}
};

const RECIPES={
  '番茄炒蛋':'1.番茄切块，鸡蛋打散加少许盐\n2.热锅冷油，倒入蛋液炒至凝固盛出\n3.锅中再加少许油，放入番茄翻炒出汁\n4.加入鸡蛋，加盐、少许糖调味\n5.翻炒均匀出锅\n💡加一点糖可以中和酸味',
  '清蒸鲈鱼':'1.鲈鱼洗净，两面各划三刀，抹盐料酒腌10分钟\n2.盘中铺姜片葱段，放上鱼\n3.水开上锅蒸8-10分钟\n4.倒掉腥水，撒葱花\n5.热油淋鱼身，淋蒸鱼豉油\n💡蒸不超10分钟，鱼眼突出即熟',
  '鸡胸肉炒青椒':'1.鸡胸肉切丝，加料酒生抽淀粉腌10分钟\n2.青椒切丝，蒜切片\n3.热油滑炒鸡丝至变色盛出\n4.爆香蒜片，下青椒翻炒\n5.加鸡丝，盐生抽调味\n💡加淀粉腌制更嫩',
  '虾仁豆腐煲':'1.嫩豆腐切块，虾仁料酒盐腌制\n2.砂锅放油爆香姜蒜\n3.放豆腐轻翻，加半碗水\n4.水开放虾仁煮2-3分钟\n5.加盐白胡椒葱花\n💡豆腐不要翻动太多',
  '牛肉炒洋葱':'1.牛肉逆纹切片，加生抽料酒淀粉腌15分钟\n2.洋葱切丝\n3.热锅多油大火滑炒牛肉至变色\n4.炒洋葱至透明\n5.加牛肉黑胡椒盐大火翻炒\n💡牛肉逆纹切才嫩',
  '麻婆豆腐':'1.嫩豆腐切块焯水1分钟\n2.炒肉末至变色，加豆瓣酱炒出红油\n3.加水放豆腐小火煮3分钟\n4.加花椒粉生抽\n5.水淀粉勾芡撒葱花\n💡豆腐先焯水不易碎',
  '沙拉':'1.生菜洗净沥干撕碎\n2.加小番茄黄瓜玉米粒\n3.加鸡胸肉丝或虾仁\n4.淋橄榄油+柠檬汁+盐+黑胡椒\n5.拌匀即可\n💡蔬菜要沥干，酱汁吃前再淋',
  '饺子':'1.水烧开加一小勺盐防粘\n2.饺子下锅轻推散\n3.水开加半碗冷水，重复3次\n4.饺子全部浮起鼓胀即捞出\n5.蘸料：醋+生抽+蒜末+辣椒油\n💡加3次冷水是秘诀',
  '蒸南瓜':'1.南瓜去皮去籽切厚片\n2.水开上锅蒸15-20分钟\n3.筷子能插入即熟\n💡选贝贝南瓜更粉糯',
  '凉拌黄瓜':'1.黄瓜拍碎（拍的口感更好！）\n2.加盐腌5分钟倒掉出水\n3.加蒜末醋生抽香油辣椒油\n4.拌匀即可\n💡拍黄瓜比切的好吃10倍',
  '紫菜蛋花汤':'1.水烧开放入撕碎紫菜\n2.鸡蛋打散沿筷子缓慢倒入\n3.加盐香油葱花煮1分钟\n💡蛋液沿筷子慢慢倒蛋花才漂亮',
  '蒜蓉西兰花':'1.西兰花掰小朵焯水1分钟\n2.蒜切末\n3.热油爆香蒜末\n4.放西兰花翻炒加盐\n💡焯水加盐和油更翠绿',
  '火锅':'1.锅中加水+火锅底料\n2.准备：肉片虾豆腐蔬菜菌菇\n3.调蘸料：芝麻酱+蒜泥+香菜+醋+生抽\n4.水开先涮肉再涮菜\n5.最后下面条粉丝\n💡清汤底料热量更低'
};

const MENU_POOL=[
  {cat:'🥘家常菜',items:[{n:'番茄炒蛋+米饭',k:200},{n:'清蒸鲈鱼+炒时蔬',k:250},{n:'鸡胸肉炒青椒+杂粮饭',k:240},{n:'虾仁豆腐煲+白灼生菜',k:180},{n:'牛肉炒洋葱+蒸南瓜',k:250},{n:'麻婆豆腐+蒜蓉西兰花',k:200},{n:'宫保鸡丁+凉拌黄瓜',k:260}]},
  {cat:'🥗轻食',items:[{n:'沙拉+鸡胸肉',k:200},{n:'全麦三明治+牛奶',k:280},{n:'蒸鱼+水煮西兰花',k:200},{n:'酸奶+坚果+水果',k:250}]},
  {cat:'🍜暖锅',items:[{n:'番茄鸡蛋面',k:350},{n:'紫菜蛋花汤+饺子',k:300},{n:'简易小火锅（清汤）',k:350}]}
];

Page({
  data:{
    meals:[],nutriBars:[],totalKcal:0,menuList:[],photoUrl:'',photoFoods:[],foodDb:FDB
  },
  onShow(){this.loadData()},
  loadData(){
    const data=wx.getStorageSync('food')||{records:[],menuRatings:{}};
    const today=new Date().toISOString().slice(0,10);
    const recs=(data.records||[]).filter(r=>r.date===today);
    const meals={breakfast:[],lunch:[],dinner:[],snack:[]};
    recs.forEach(r=>{if(meals[r.meal])meals[r.meal].push(r)});
    const mn={breakfast:'🌅早餐',lunch:'☀️午餐',dinner:'🌙晚餐',snack:'🍪加餐'},mi={breakfast:'🥐',lunch:'🍱',dinner:'🍲',snack:'🍪'};
    const mealList=Object.entries(meals).map(([k,v])=>({key:k,icon:mi[k],name:mn[k],kcal:v.reduce((s,i)=>s+(i.kcal||0),0),items:v,itemsStr:v.map(i=>i.name).join('、')}));
    const tk=recs.reduce((s,r)=>s+(r.kcal||0),0),tp=recs.reduce((s,r)=>s+(r.protein||0),0),tf=recs.reduce((s,r)=>s+(r.fat||0),0),tc=recs.reduce((s,r)=>s+(r.carbs||0),0),tfb=recs.reduce((s,r)=>s+(r.fiber||0),0);
    const tg=[['🥩蛋白质',tp,55],['🧈脂肪',tf,45],['🍚碳水',tc,180],['🥬纤维',tfb,25]];
    const nutriBars=tg.map(([l,v,t])=>{const p=Math.min(v/t*100,100),c=p>=90?'#2E8B57':p>=60?'#FFB347':'#E8557A';return{label:l,pct:p,color:c,val:Math.round(v),target:t}});

    // 菜单
    const pool=[];MENU_POOL.forEach(cat=>cat.items.forEach(item=>pool.push({...item,cat:cat.cat})));
    const ratings=data.menuRatings||{};
    const sorted=pool.sort((a,b)=>(ratings[b.n]||3)-(ratings[a.n]||3));
    const menu=sorted.slice(0,9).map(m=>({name:m.n,kcal:m.k,cat:m.cat,rating:ratings[m.n]||3}));

    this.setData({meals:mealList,nutriBars,totalKcal:tk,menuList:menu});
  },
  takePhoto(){
    wx.chooseMedia({count:1,mediaType:['image'],sourceType:['camera'],success:res=>{
      this.setData({photoUrl:res.tempFiles[0].tempFilePath});
      // 模拟识别
      setTimeout(()=>{
        const foods=['米饭','番茄炒蛋','鸡胸肉','炒青菜','清蒸鱼','沙拉','饺子','三明治'];
        this.setData({photoFoods:foods});
        wx.showToast({title:'点击确认食物',icon:'none'});
      },800);
    }});
  },
  confirmFood(e){
    const name=e.currentTarget.dataset.name,d=FDB[name]||{k:100,p:0,f:0,c:0,fb:0};
    const data=wx.getStorageSync('food')||{records:[],menuRatings:{}};
    data.records.push({date:new Date().toISOString().slice(0,10),meal:'lunch',name,kcal:d.k,protein:d.p,fat:d.f,carbs:d.c,fiber:d.fb});
    wx.setStorageSync('food',data);
    this.setData({photoUrl:'',photoFoods:[]});
    this.loadData();
    wx.showToast({title:'✅ 已记录'});
  },
  addMeal(e){
    const meal=e.currentTarget.dataset.meal;
    wx.showModal({title:'添加食物',editable:true,placeholderText:'食物名称',success:res=>{
      if(!res.content)return;
      wx.showModal({title:'热量(kcal)',editable:true,placeholderText:'例如：350',success:r2=>{
        const kcal=parseInt(r2.content)||0;if(!kcal)return;
        const db=FDB[res.content]||{k:kcal,p:0,f:0,c:0,fb:0};
        const data=wx.getStorageSync('food')||{records:[],menuRatings:{}};
        data.records.push({date:new Date().toISOString().slice(0,10),meal,name:res.content,kcal:db.k||kcal,protein:db.p||0,fat:db.f||0,carbs:db.c||0,fiber:db.fb||0});
        wx.setStorageSync('food',data);
        this.loadData();
      }});
    }});
  },
  rateMenu(e){
    const name=e.currentTarget.dataset.name,rating=e.currentTarget.dataset.rating;
    const data=wx.getStorageSync('food')||{records:[],menuRatings:{}};
    data.menuRatings=data.menuRatings||{};
    data.menuRatings[name]=rating;
    wx.setStorageSync('food',data);
    this.loadData();
    wx.showToast({title:'⭐'+rating+'/5'});
  },
  showRecipe(e){
    const name=e.currentTarget.dataset.name;
    const mainName=name.split('+')[0].trim().split('（')[0];
    const recipe=RECIPES[mainName]||'暂无详细做法';
    wx.showModal({title:'🍳 '+mainName,content:recipe,showCancel:false,confirmText:'知道了'});
  }
});
