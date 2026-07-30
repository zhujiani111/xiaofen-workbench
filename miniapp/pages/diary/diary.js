Page({
  data:{step:0,a0:'',a1:'',diaryText:'',photoUrl:'',mood:'😊',moods:['😊','😢','😤','😌','🥰'],entries:[]},
  onShow(){
    const data=wx.getStorageSync('diary')||{entries:[]};
    this.setData({entries:(data.entries||[]).slice(-10).reverse(),step:0,a0:'',a1:'',diaryText:'',photoUrl:''});
  },
  onA0(e){this.setData({a0:e.detail.value})},
  onA1(e){this.setData({a1:e.detail.value})},
  nextStep(){
    if(this.data.step===0){this.setData({step:1})}
    else if(this.data.step===1){
      const text=`${this.data.a0}\n\n当时的感觉：${this.data.a1}\n\n想对自己说：`;
      this.setData({step:2,diaryText:text});
    }
  },
  takePhoto(){
    wx.chooseMedia({count:1,mediaType:['image'],sourceType:['camera'],success:res=>{this.setData({photoUrl:res.tempFiles[0].tempFilePath})}});
  },
  onDiaryText(e){this.setData({diaryText:e.detail.value})},
  setMood(e){this.setData({mood:e.currentTarget.dataset.m})},
  saveDiary(){
    const t=this.data.diaryText.trim();
    if(!t&&!this.data.photoUrl){wx.showToast({title:'写点什么或拍张照吧~',icon:'none'});return}
    const data=wx.getStorageSync('diary')||{entries:[]};
    data.entries.push({date:new Date().toISOString().slice(0,10),text:t,mood:this.data.mood,photo:this.data.photoUrl,time:new Date().toISOString()});
    wx.setStorageSync('diary',data);
    this.setData({step:0,a0:'',a1:'',diaryText:'',photoUrl:''});
    this.onShow();
    wx.showToast({title:'🌸已保存'});
  }
});
