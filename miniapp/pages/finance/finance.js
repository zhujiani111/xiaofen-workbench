Page({
  data:{
    amount:'',typeIdx:0,catIdx:0,
    types:['支出','收入'],cats:['餐饮','交通','购物','娱乐','住房','其他'],
    totalExp:'¥0',totalInc:'¥0',balance:'¥0',
    budget:3000,monthExp:0,remain:3000,budgetPct:0,records:[]
  },
  onShow(){this.loadData()},
  loadData(){
    const data=wx.getStorageSync('finance')||{records:[],budget:3000};
    const today=new Date().toISOString().slice(0,7);
    const mr=(data.records||[]).filter(r=>r.date&&r.date.startsWith(today));
    const exp=mr.filter(r=>r.type==='expense'),inc=mr.filter(r=>r.type==='income');
    const te=exp.reduce((s,r)=>s+(r.amount||0),0),ti=inc.reduce((s,r)=>s+(r.amount||0),0);
    const bgt=data.budget||3000,bp=Math.min(te/bgt*100,100),rem=bgt-te;
    const records=(data.records||[]).slice(-12).reverse().map((r,i)=>({...r,realIdx:data.records.length-1-i}));
    this.setData({
      totalExp:'¥'+te.toFixed(0),totalInc:'¥'+ti.toFixed(0),balance:'¥'+(ti-te).toFixed(0),
      budget:bgt,monthExp:Math.round(te),remain:Math.round(rem),budgetPct:Math.round(bp),records
    });
  },
  onAmount(e){this.setData({amount:e.detail.value})},
  onType(e){this.setData({typeIdx:parseInt(e.detail.value)})},
  onCat(e){this.setData({catIdx:parseInt(e.detail.value)})},
  addRecord(){
    const amt=parseFloat(this.data.amount);
    if(!amt||amt<=0){wx.showToast({title:'请输入金额',icon:'none'});return}
    const data=wx.getStorageSync('finance')||{records:[],budget:3000};
    const type=this.data.typeIdx===0?'expense':'income';
    data.records.push({date:new Date().toISOString().slice(0,10),type,amount:amt,category:this.data.cats[this.data.catIdx],note:'',time:new Date().toISOString()});
    wx.setStorageSync('finance',data);
    this.setData({amount:''});
    this.loadData();
    wx.showToast({title:'✅已记账'});
  },
  quickRecord(e){
    const {amt,cat,type}=e.currentTarget.dataset;
    let amount=parseFloat(amt);
    if(type==='income'){wx.showModal({title:'输入工资',editable:true,placeholderText:'金额',success:res=>{if(!res.content)return;amount=parseFloat(res.content);if(!amount)return;this.doQuick(amount,cat,type)}});return}
    this.doQuick(amount,cat,type);
  },
  doQuick(amount,cat,type){
    const data=wx.getStorageSync('finance')||{records:[],budget:3000};
    data.records.push({date:new Date().toISOString().slice(0,10),type,amount,category:cat,note:'',time:new Date().toISOString()});
    wx.setStorageSync('finance',data);
    this.loadData();
    wx.showToast({title:'✅已记账'});
  },
  delRecord(e){
    const idx=e.currentTarget.dataset.idx;
    const data=wx.getStorageSync('finance')||{records:[],budget:3000};
    data.records.splice(idx,1);
    wx.setStorageSync('finance',data);
    this.loadData();
  },
  setBudget(){
    wx.showModal({title:'设置月度预算',editable:true,placeholderText:'3000',success:res=>{
      if(!res.content)return;
      const v=parseInt(res.content)||3000;
      const data=wx.getStorageSync('finance')||{records:[],budget:3000};
      data.budget=v;
      wx.setStorageSync('finance',data);
      this.loadData();
    }});
  }
});
