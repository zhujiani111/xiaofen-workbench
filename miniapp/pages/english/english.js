const WORDS=[{w:'deadline',p:'/ˈded.laɪn/',m:'截止日期'},{w:'brainstorm',p:'/ˈbreɪn.stɔːrm/',m:'头脑风暴'},{w:'feedback',p:'/ˈfiːd.bæk/',m:'反馈'},{w:'priority',p:'/praɪˈɒr.ə.ti/',m:'优先事项'},{w:'collaborate',p:'/kəˈlæb.ə.reɪt/',m:'合作'},{w:'schedule',p:'/ˈʃedʒ.uːl/',m:'日程'},{w:'proposal',p:'/prəˈpəʊ.zəl/',m:'提案'},{w:'strategy',p:'/ˈstræt.ə.dʒi/',m:'策略'},{w:'budget',p:'/ˈbʌdʒ.ɪt/',m:'预算'},{w:'campaign',p:'/kæmˈpeɪn/',m:'营销'},{w:'stakeholder',p:'/ˈsteɪk.həʊl.dər/',m:'利益相关者'},{w:'implement',p:'/ˈɪm.plɪ.ment/',m:'实施'},{w:'evaluate',p:'/ɪˈvæl.ju.eɪt/',m:'评估'},{w:'negotiate',p:'/nɪˈɡəʊ.ʃi.eɪt/',m:'谈判'},{w:'productivity',p:'/ˌprɒd.ʌkˈtɪv.ə.ti/',m:'生产力'},{w:'milestone',p:'/ˈmaɪl.stəʊn/',m:'里程碑'},{w:'benchmark',p:'/ˈbentʃ.mɑːrk/',m:'基准'},{w:'optimize',p:'/ˈɒp.tɪ.maɪz/',m:'优化'},{w:'initiative',p:'/ɪˈnɪʃ.ə.tɪv/',m:'倡议'},{w:'accountability',p:'/əˌkaʊn.təˈbɪl.ə.ti/',m:'责任感'},{w:'alignment',p:'/əˈlaɪn.mənt/',m:'对齐'},{w:'scalable',p:'/ˈskeɪ.lə.bəl/',m:'可扩展'},{w:'leverage',p:'/ˈlev.ər.ɪdʒ/',m:'利用'},{w:'streamline',p:'/ˈstriːm.laɪn/',m:'精简'},{w:'onboarding',p:'/ˈɒn.bɔːr.dɪŋ/',m:'入职'},{w:'deliverable',p:'/dɪˈlɪv.ər.ə.bəl/',m:'交付物'},{w:'touch base',p:'/tʌtʃ beɪs/',m:'碰头'},{w:'follow up',p:'/ˈfɒl.əʊ ʌp/',m:'跟进'},{w:'circle back',p:'/ˈsɜː.kəl bæk/',m:'回头再议'}];

const SCENARIOS=[
  {title:'📧 写邮件：请求反馈',content:'Subject: Feedback Request\n\nHi Team,\n\nI\'ve drafted the Q3 content calendar and would love your input.\nKey highlights:\n- Focus on "midlife women wellness" series\n- 3 tentpole campaigns\n\nPlease share your thoughts by Friday. Thanks!\n\nBest,\n[Your Name]',tip:'💡 礼貌开头→需求→重点→时间节点'},
  {title:'🗣️ 会议发言：表达观点',content:'"I\'d like to add something. From my perspective, we should prioritize the wellness series. The engagement data shows our audience resonates with health topics. What does everyone think?"',tip:'💡 插话→观点→数据→邀请讨论'},
  {title:'📊 汇报进度',content:'"Quick update: We\'re at 70%. First 3 articles live, averaging 85K reads. Next milestone: video companions by Wednesday."',tip:'💡 进度→数据→下一步→时间'}
];

Page({
  data:{streak:0,wordsLearned:0,isDone:false,masteredCount:0,words:[],showScenario:false,scenario:{}},
  onShow(){this.loadData()},
  loadData(){
    const data=wx.getStorageSync('english')||{streak:0,wl:0,ld:'',md:{}};
    const today=new Date().toISOString().slice(0,10);
    const isDone=data.ld===today;
    const dow=new Date().getDay();
    const showScenario=[1,3,5].includes(dow);

    const si=(new Date().getDate()*7)%WORDS.length;
    const words=[];
    for(let i=0;i<15;i++){
      const w=WORDS[(si+i)%WORDS.length];
      words.push({...w,mastered:!!(data.md||{})[w.w]});
    }

    let scenario={};
    if(showScenario)scenario=SCENARIOS[Math.floor(new Date().getDate()/7)%SCENARIOS.length];

    this.setData({
      streak:data.streak||0,wordsLearned:data.wl||0,isDone,masteredCount:Object.keys(data.md||{}).length,
      words,showScenario,scenario
    });
  },
  masterWord(e){
    const w=e.currentTarget.dataset.w;
    const data=wx.getStorageSync('english')||{streak:0,wl:0,ld:'',md:{}};
    data.md=data.md||{};
    data.md[w]=true;
    wx.setStorageSync('english',data);
    this.loadData();
  },
  markDone(){
    const today=new Date().toISOString().slice(0,10);
    const data=wx.getStorageSync('english')||{streak:0,wl:0,ld:'',md:{}};
    if(data.ld===today){wx.showToast({title:'今天已打卡~',icon:'none'});return}
    const y=new Date();y.setDate(y.getDate()-1);
    if(data.ld===y.toISOString().slice(0,10))data.streak=(data.streak||0)+1;else data.streak=1;
    data.ld=today;data.wl=(data.wl||0)+15;
    wx.setStorageSync('english',data);
    this.loadData();
    wx.showToast({title:'🎉打卡成功！'});
  }
});
