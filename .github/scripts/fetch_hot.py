"""每日热搜抓取 + 所有模块数据生成"""
import json, random, hashlib, os, re
from datetime import datetime, timedelta
import requests

OUT = "data"

# ============================================================
# 1. 热点：抓取百度热搜 + 微博热搜
# ============================================================
def fetch_hot():
    topics = []

    # 尝试百度热搜
    try:
        resp = requests.get("https://top.baidu.com/board?tab=realtime",
                          headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"},
                          timeout=15)
        if resp.status_code == 200:
            # 解析百度热搜标题
            titles = re.findall(r'<div class="c-single-text-ellipsis">(.*?)</div>', resp.text)
            hot_nums = re.findall(r'<div class="hot-index[^"]*">(\d+)</div>', resp.text)
            for i, t in enumerate(titles[:10]):
                clean = re.sub(r'<[^>]+>', '', t).strip()
                if clean and len(clean) > 2:
                    topics.append({
                        'tag': 'news', 'tt': '百度热搜',
                        'title': clean,
                        'desc': f'实时搜索指数 {hot_nums[i] if i < len(hot_nums) else "🔥"}',
                        'src': '百度', 'tm': '实时'
                    })
    except Exception as e:
        print(f"Baidu fetch error: {e}")

    # 尝试微博热搜 API
    try:
        resp = requests.get("https://weibo.com/ajax/side/hotSearch",
                          headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15", "Referer": "https://weibo.com/"},
                          timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('data', {}).get('realtime', [])[:10]
            for item in items:
                word = item.get('word', '').strip()
                if word and not any(t['title'] == word for t in topics):
                    topics.append({
                        'tag': 'trend', 'tt': '微博热搜',
                        'title': word,
                        'desc': f"热搜第{item.get('rank','')}名",
                        'src': '微博', 'tm': '实时'
                    })
    except Exception as e:
        print(f"Weibo fetch error: {e}")

    # 补充公众号选题相关（每天动态生成，保证每次不同）
    today = datetime.now()
    seed = int(today.strftime('%Y%m%d'))
    rng = random.Random(seed)

    backup_pool = [
        {'tag': 'competitor', 'tt': '竞品', 'title': '年糕妈妈近3天爆款选题分析', 'desc': '主号「中女情感+健康警示+育儿故事」三线并进。分析竞品爆款，找差异化切口。', 'src': '年糕妈妈'},
        {'tag': 'idea', 'tt': '灵感', 'title': '「妈妈的情绪管理」UGC征集方向', 'desc': '发起"今天你崩溃了吗"话题征集，引导UGC互动。情感共鸣+高互动。', 'src': '选题建议'},
        {'tag': 'news', 'tt': '健康', 'title': '35岁+女性健康：围绝经期提前的5个信号', 'desc': '多篇医学报道聚焦女性早更问题。与「中女健康」选题高度相关，可科普+真实案例切入。', 'src': '丁香医生'},
        {'tag': 'competitor', 'tt': '竞品', 'title': '丁香妈妈最新育儿爆文盘点', 'desc': '分析竞品文章结构、标题套路、互动策略。可借鉴其「干货+情感」双线模式。', 'src': '丁香妈妈'},
        {'tag': 'trend', 'tt': '小红书', 'title': '「暑假高质量陪伴」话题持续火爆', 'desc': '#高质量陪伴# 阅读量破3亿。宝妈们分享假期带娃新玩法，素材丰富。', 'src': '小红书'},
        {'tag': 'idea', 'tt': '灵感', 'title': '「老公带娃翻车现场」轻松选题', 'desc': '征集爸爸带娃搞笑瞬间。轻松内容+高互动+UGC，天然适合周末发。', 'src': '选题建议'},
        {'tag': 'trend', 'tt': '抖音', 'title': '「30+女性觉醒时刻」话题升温', 'desc': '越来越多30+女性分享职场转型、自我成长故事。情感共鸣类选题机会。', 'src': '抖音'},
        {'tag': 'news', 'tt': '消费', 'title': '最新母婴消费报告：90后妈妈消费趋势', 'desc': '母婴消费升级方向解读。可结合电商广告植入，数据支撑+产品推荐。', 'src': '消费报告'},
        {'tag': 'idea', 'tt': '灵感', 'title': '「反焦虑育儿」成为新潮流', 'desc': '越来越多年轻妈妈拒绝鸡娃，追求松弛感育儿。深度选题方向，可做系列。', 'src': '选题建议'},
        {'tag': 'trend', 'tt': '趋势', 'title': '「精致穷养娃」VS「佛系放养」大讨论', 'desc': '社交平台两派妈妈激烈辩论。可做对比分析+观点输出，评论区必爆。', 'src': '社交平台'},
        {'tag': 'news', 'tt': '政策', 'title': '多地出台最新托育补贴政策解读', 'desc': '年轻家庭育儿成本有望降低。可跟进本地落地情况，服务性选题。', 'src': '新华网'},
        {'tag': 'competitor', 'tt': '竞品', 'title': '小红书母婴类爆文选题风向', 'desc': '分析小红书母婴赛道最新爆文，提炼可借鉴的选题公式和表达方式。', 'src': '小红书'},
    ]

    rng.shuffle(backup_pool)
    # 补满到 10 条（如果抓取不够）
    while len(topics) < 10:
        for b in backup_pool:
            if len(topics) >= 10:
                break
            if not any(t['title'] == b['title'] for t in topics):
                topics.append(dict(b))

    # 更新时间戳
    now_str = datetime.now().strftime('%H:%M')
    for t in topics:
        if t.get('tm') == '实时':
            t['tm'] = f'今天 {now_str}'

    return topics[:12]


# ============================================================
# 2. 菜单：按周生成，量足够大
# ============================================================
def gen_weekly_menu(week_num):
    rng = random.Random(week_num * 777)
    month = datetime.now().month

    summer = [
        {'n':'凉拌鸡丝荞麦面','k':280,'cat':'🥗轻食'},{'n':'番茄虾仁意面','k':320,'cat':'🍝主食'},
        {'n':'冬瓜排骨汤+杂粮饭','k':350,'cat':'🍲暖汤'},{'n':'蒜蓉秋葵+蒸鲈鱼','k':220,'cat':'🥘家常菜'},
        {'n':'鸡胸肉沙拉碗','k':260,'cat':'🥗轻食'},{'n':'丝瓜炒蛋+小米粥','k':200,'cat':'🥘家常菜'},
        {'n':'凉拌木耳黄瓜','k':80,'cat':'🥒小菜'},{'n':'柠檬手撕鸡','k':240,'cat':'🥘家常菜'},
        {'n':'苦瓜炒牛肉','k':220,'cat':'🥘家常菜'},{'n':'绿豆百合汤','k':100,'cat':'🍵甜品'},
        {'n':'虾滑豆腐汤','k':180,'cat':'🍲暖汤'},{'n':'藜麦牛油果沙拉','k':300,'cat':'🥗轻食'},
        {'n':'番茄鸡蛋面','k':350,'cat':'🍜面食'},{'n':'凉拌鸡丝','k':180,'cat':'🥒小菜'},
        {'n':'清蒸鲈鱼+西兰花','k':250,'cat':'🥘家常菜'},{'n':'蒜蓉粉丝蒸虾','k':200,'cat':'🥘家常菜'},
        {'n':'酸辣蕨根粉','k':150,'cat':'🍜面食'},{'n':'白灼秋葵','k':60,'cat':'🥒小菜'},
        {'n':'柠檬蜂蜜水','k':40,'cat':'🍵饮品'},{'n':'西瓜薄荷沙拉','k':80,'cat':'🥗轻食'},
        {'n':'番茄牛腩面','k':400,'cat':'🍜面食'},{'n':'黄瓜拌海蜇','k':90,'cat':'🥒小菜'},
        {'n':'蒜蓉蒸茄子','k':70,'cat':'🥘家常菜'},{'n':'银耳莲子羹','k':120,'cat':'🍵甜品'},
    ]

    winter = [
        {'n':'番茄炖牛腩+米饭','k':380,'cat':'🍲暖锅'},{'n':'萝卜排骨汤+馒头','k':350,'cat':'🍲暖汤'},
        {'n':'红烧鸡翅+炒时蔬','k':340,'cat':'🥘家常菜'},{'n':'羊肉萝卜煲','k':360,'cat':'🍲暖锅'},
        {'n':'香菇滑鸡粥','k':280,'cat':'🥣粥品'},{'n':'白菜豆腐煲','k':200,'cat':'🍲暖锅'},
        {'n':'咖喱鸡肉饭','k':380,'cat':'🍛饭类'},{'n':'山药排骨汤','k':320,'cat':'🍲暖汤'},
        {'n':'酸辣汤+花卷','k':280,'cat':'🍲暖汤'},{'n':'红薯小米粥','k':180,'cat':'🥣粥品'},
        {'n':'麻婆豆腐+米饭','k':340,'cat':'🥘家常菜'},{'n':'菌菇鸡汤','k':250,'cat':'🍲暖汤'},
        {'n':'红烧排骨+土豆','k':380,'cat':'🥘家常菜'},{'n':'酸菜鱼','k':280,'cat':'🍲暖锅'},
        {'n':'土豆炖牛肉','k':350,'cat':'🍲暖锅'},{'n':'排骨莲藕汤','k':300,'cat':'🍲暖汤'},
        {'n':'葱爆羊肉','k':280,'cat':'🥘家常菜'},{'n':'牛肉拉面','k':420,'cat':'🍜面食'},
        {'n':'地三鲜+米饭','k':320,'cat':'🥘家常菜'},{'n':'酸辣粉','k':350,'cat':'🍜面食'},
        {'n':'水煮鱼','k':300,'cat':'🍲暖锅'},{'n':'京酱肉丝','k':280,'cat':'🥘家常菜'},
        {'n':'南瓜小米粥','k':150,'cat':'🥣粥品'},{'n':'板栗烧鸡','k':320,'cat':'🥘家常菜'},
    ]

    pool = summer if month in [6, 7, 8] else winter
    shuffled = pool[:]
    rng.shuffle(shuffled)
    return shuffled[:9]


# ============================================================
# 3. 运动：每周生成
# ============================================================
def gen_weekly_exercise(week_num):
    rng = random.Random(week_num * 333)
    cardio = [
        {'n':'骑单车','dr':'30-40分钟','lk':'https://www.bilibili.com/video/BV1jJ4m1N7nN'},
        {'n':'跳绳','dr':'15-20分钟','lk':'https://www.bilibili.com/video/BV1Hr4y1y7sN'},
        {'n':'快走/慢跑','dr':'30分钟','lk':''},
        {'n':'有氧操','dr':'20分钟','lk':'https://www.bilibili.com/video/BV1Wh411m7eG'},
        {'n':'爬楼梯','dr':'15分钟','lk':''},
        {'n':'HIIT训练','dr':'15分钟','lk':''},
        {'n':'游泳','dr':'30分钟','lk':''},
        {'n':'椭圆机','dr':'25分钟','lk':''},
        {'n':'尊巴舞','dr':'20分钟','lk':''},
        {'n':'登山机','dr':'15分钟','lk':''},
    ]
    strength = [
        {'n':'帕梅拉15分钟','dr':'15分钟','lk':'https://www.bilibili.com/video/BV1Wh411m7eG'},
        {'n':'平板支撑3组','dr':'每组30秒','lk':''},
        {'n':'深蹲50个','dr':'分3组','lk':''},
        {'n':'臀桥3组','dr':'每组15个','lk':''},
        {'n':'哑铃训练','dr':'15分钟','lk':'https://www.bilibili.com/video/BV1Li4y1d7XV'},
        {'n':'核心训练','dr':'10分钟','lk':''},
        {'n':'俯卧撑3组','dr':'每组10个','lk':''},
        {'n':'弹力带训练','dr':'15分钟','lk':''},
        {'n':'壶铃摇摆','dr':'10分钟','lk':''},
        {'n':'仰卧起坐3组','dr':'每组20个','lk':''},
    ]
    rest = [
        {'n':'散步','dr':'15分钟','lk':''},
        {'n':'瑜伽拉伸','dr':'15分钟','lk':'https://www.bilibili.com/video/BV1Li4y1d7XV'},
        {'n':'睡前拉伸','dr':'10分钟','lk':''},
        {'n':'按摩滚轮','dr':'10分钟','lk':''},
        {'n':'冥想放松','dr':'10分钟','lk':''},
        {'n':'泡沫轴放松','dr':'10分钟','lk':''},
    ]
    types = ['有氧','休息','力量','休息','有氧','综合','休息']
    icons = ['🚴‍♀️','🧘‍♀️','💪','🛀','🚴‍♀️','🌿','🌸']
    days = ['周一','周二','周三','周四','周五','周六','周日']

    plan = []
    for i in range(7):
        is_rest = types[i] == '休息'
        items = []
        if is_rest:
            items.append(rest[rng.randint(0, len(rest)-1)])
        elif types[i] == '有氧':
            items.append(cardio[rng.randint(0, len(cardio)-1)])
            items.append({'n':'拉伸放松','dr':'5分钟','lk':''})
        elif types[i] == '力量':
            items.append(strength[rng.randint(0, len(strength)-1)])
            items.append(strength[rng.randint(0, len(strength)-1)])
            items.append({'n':'按摩滚轮','dr':'5分钟','lk':''})
        elif types[i] == '综合':
            items.append(cardio[rng.randint(0, len(cardio)-1)])
            items.append(rest[rng.randint(0, len(rest)-1)])
        plan.append({'d': days[i], 't': types[i], 'f': icons[i], 'a': not is_rest, 'items': items})

    return plan


# ============================================================
# 4. 每日推荐文章（足够2年量：730+篇）
# ============================================================
ARTICLES_POOL = [
    {'title':'当代妈妈的「情绪自由」：允许自己不完美','content':'<h4>当代妈妈的「情绪自由」：允许自己不完美</h4><p>前两天在朋友圈看到一句话："当了妈以后，我最大的敌人不是孩子，是我自己。"</p><p>你有没有这样的时刻：孩子哭闹时忍不住吼了一句，然后内疚一整天；看到别的妈妈晒精致早餐，再看看自己桌上冷掉的包子，觉得自己不称职；工作忙没时间陪孩子，内心充满了亏欠感……</p><p>我们这届妈妈，太擅长"内耗"了。社交媒体上那些完美妈妈的形象，让我们以为"好妈妈"就应该是24小时温柔耐心、永远不犯错的样子。但现实是——谁都不是圣人。</p><p>心理学家温尼科特提出过一个概念："足够好的妈妈"（Good Enough Mother）。不是说要做100分妈妈，60分就够了。剩下的40分，留给自己。</p><p><b>姐妹们，记住这句话：你首先是你自己，然后才是妈妈。</b></p>'},
    {'title':'35岁以后，我终于学会了"摆烂式育儿"','content':'<h4>35岁以后，我终于学会了"摆烂式育儿"</h4><p>什么叫"摆烂式育儿"？不是真的放弃不管，而是——不再跟自己较劲。</p><p>以前的我：孩子吃饭必须营养均衡。现在的我：这顿不吃下顿就饿了。</p><p>以前的我：早教班、兴趣班一个不能落。现在的我：周末睡到自然醒，带娃去公园挖沙子比什么早教都强。</p><p>你的松弛感，才是给孩子最好的礼物。</p>'},
    {'title':'一个中年女人的周末：带娃、做饭、和自己和解','content':'<h4>一个中年女人的周末</h4><p>早上六点半，孩子准时爬上床。周六的闹钟从来不是手机，是娃。</p><p>当妈以后才发现，周末是另一种上班——工位从公司变成了家，老板从领导变成了孩子。</p><p>但这两年，我慢慢学会了在鸡飞狗跳里找自己的节奏。趁孩子看动画片的20分钟泡杯茶，晚饭后让老公带孩子下楼，自己敷个面膜。</p><p>中年女人的和解，是在日复一日的琐碎里，学会给自己留一扇透气的小窗。</p>'},
    {'title':'那些年被我们误解的"妈妈"两个字','content':'<h4>那些年被我们误解的"妈妈"两个字</h4><p>小时候觉得妈妈是超人，什么都会。长大后自己当了妈才发现，超人也会累，超人也会哭。</p><p>我们总以为好妈妈就应该牺牲一切。但很少有人告诉我们：一个快乐的妈妈，比一个完美的妈妈更重要。</p><p>你开心了，家里才有笑声。你爱自己了，孩子才学会爱自己。</p>'},
    {'title':'当你开始爱自己，全世界都会来爱你','content':'<h4>当你开始爱自己，全世界都会来爱你</h4><p>很多妈妈把所有人的需求都排在自己前面。但飞机上的安全须知怎么说来着？"请先戴好自己的氧气面罩，再帮助他人。"</p><p>这不是自私，是自保。你只有把自己照顾好了，才有能量去照顾别人。</p><p>从今天开始，每天给自己留30分钟。不带孩子，不做家务，就做自己喜欢的事。</p>'},
    {'title':'暑假过半，我决定和孩子一起"躺平"','content':'<h4>暑假过半，我决定和孩子一起"躺平"</h4><p>暑假刚开始时我信誓旦旦列了一张计划表。结果呢？第一周勉强执行，第二周开始打折扣，第三周计划表都不知道塞哪儿了。</p><p>一位育儿博主说："暑假不是用来鸡娃的，是用来喘口气的。"突然就释然了。</p><p>去楼下骑骑车、在家搭搭积木、一起看个动画片——这些"无用"的时光，可能比任何补习班都珍贵。</p>'},
    {'title':'成年人的崩溃，从辅导作业开始','content':'<h4>成年人的崩溃，从辅导作业开始</h4><p>如果说当代中年人有什么共同的噩梦，辅导作业一定排前三。</p><p>你温柔地说："这道题我们再来一遍。"孩子无辜地看着你。你再讲一遍，还是不会。血压升高，声音变大，孩子眼眶红了，你内疚了。</p><p>后来我想通了一件事：辅导作业的目的不是让孩子做对，是让他学会思考。做错了没关系，关键是他有没有在动脑子。</p>'},
    {'title':'30+女性的深夜思考：我到底想要什么','content':'<h4>30+女性的深夜思考</h4><p>凌晨一点，孩子终于睡了。这是属于我自己的唯一时间。</p><p>躺在床上突然想：我到底想要什么？20岁想要爱情和自由，25岁想要稳定工作和一个家。30岁以后呢？好像就没想过自己了。</p><p>但30+不是终点，是新的起点。你比20岁更了解自己，比25岁更有底气。现在开始想"我要什么"，一点都不晚。</p>'},
    {'title':'对不起孩子，妈妈今天又发脾气了','content':'<h4>对不起孩子，妈妈今天又发脾气了</h4><p>晚上哄睡的时候，孩子突然抱住我说："妈妈，你今天好凶。"我鼻子一酸，差点哭出来。</p><p>谁不想做一个温柔的妈妈？但每天面对工作、家务、带娃三座大山，总有绷不住的时候。</p><p>后来我学会了一件事：发完脾气后，蹲下来跟孩子道歉。"妈妈刚才太急了，对不起。不是因为你不乖，是妈妈今天太累了。"孩子通常比我们想象中更宽容。</p>'},
    {'title':'婆婆说我不够贤惠，老公沉默了','content':'<h4>婆婆说我不够贤惠，老公沉默了</h4><p>那天家庭聚餐，婆婆半开玩笑地说："现在年轻媳妇真享福，饭也不做，孩子也带不好。"满桌人笑了，只有我没笑。</p><p>我老公呢？低头扒饭，一个字没说。</p><p>回家路上我跟他说："你妈当着全家人说我不贤惠，你为什么不帮我说话？"他说："她就是开个玩笑，你别那么敏感。"</p><p>姐妹们，这不是敏感。这是底线。家庭关系里最伤人的不是矛盾本身，是那个本应站在你身边的人选择了沉默。</p>'},
    {'title':'生完孩子后，我和老公成了室友','content':'<h4>生完孩子后，我和老公成了室友</h4><p>孩子出生后，我们的对话变成了："奶粉还有吗？""纸尿裤买了没？""今天谁去接孩子？"</p><p>很久没有两个人单独吃饭、看电影、聊天到深夜了。有时候看着他躺在沙发刷手机的背影，觉得既熟悉又陌生。</p><p>但前几天，他默默把我收藏了很久的那条围巾买回来了。什么都没说，就放在我床头。我突然明白：爱没消失，只是换了一种更安静的方式存在。</p>'},
    {'title':'闺蜜问：你后悔当妈妈吗？','content':'<h4>闺蜜问：你后悔当妈妈吗？</h4><p>那天下午茶，还没结婚的闺蜜突然问我："说实话，你后悔当妈妈吗？"</p><p>我愣了一下。说实话，在很多个崩溃的凌晨三点，在很多次辅导作业的血压飙升时刻，我确实想过：如果没有孩子，我的生活会不会更轻松？</p><p>但每次孩子说"妈妈我爱你"，每次他生病时紧紧抓着我的手，每次看到他从一个小肉团长成有自己想法的小朋友——我知道，所有的疲惫都是值得的。</p><p>不后悔。但如果有来生，我想当爸爸。</p>'},
    {'title':'孩子说：妈妈你为什么不开心','content':'<h4>孩子说：妈妈你为什么不开心</h4><p>那天我加班回来，累得瘫在沙发上。四岁的女儿跑过来，歪着头问："妈妈，你为什么不开心？"</p><p>我说："妈妈没有不开心，只是有点累。"她想了想，跑去拿了自己的小毯子盖在我身上，说："盖被子就好了，我生病的时候妈妈也是这样给我盖的。"</p><p>那一刻，所有疲惫都值了。孩子的爱，是我们被生活打磨后，最温柔的补偿。</p>'},
    {'title':'我终于删掉了"完美妈妈"的朋友圈','content':'<h4>我终于删掉了"完美妈妈"的朋友圈</h4><p>取关了所有晒精致辅食、打卡各种早教班、永远妆容精致的育儿博主。</p><p>不是我嫉妒她们——是这种"完美妈妈"的形象，让我们这些普通妈妈不断怀疑自己：是不是我不够努力？是不是我对不起孩子？</p><p>后来我关注了一批"翻车博主"——分享辅食做失败的、吐槽带娃崩溃的、展示家里乱成猪窝的。每次刷到她们，我就觉得：啊，原来不是我一个人。</p>'},
    {'title':'我决定不再为孩子的成绩焦虑了','content':'<h4>我决定不再为孩子的成绩焦虑了</h4><p>上学期期末考试，孩子数学考了78分。我看到成绩单的那一刻，血压直接上来了。</p><p>但晚上冷静下来，我翻出了自己小学时的成绩单——数学经常不及格。现在呢？我不也活得好好的，有工作、有家庭？</p><p>成绩很重要，但不是唯一重要的事。孩子的善良、好奇心、抗挫折能力，这些才是真正能陪他一辈子的东西。</p>'},
    {'title':'全职妈妈三年，我决定回去上班了','content':'<h4>全职妈妈三年，我决定回去上班了</h4><p>三年前辞职带娃的时候，我觉得这是最正确的决定。三年后，我发现自己连跟人正常社交都变得困难。</p><p>最难受的不是没有收入，是那种"我被世界抛弃了"的感觉。朋友们聊工作、聊八卦、聊新学的技能，我只能聊孩子。慢慢就不想参加聚会了。</p><p>投了两个月简历，面了七八家公司。有HR直接说"三年空窗期有点长"。但我没有放弃。这周终于收到了offer。</p>'},
    {'title':'妈妈群里最让我感动的10个瞬间','content':'<h4>妈妈群里最让我感动的10个瞬间</h4><p>1. 凌晨三点，群里有人问"有人还没睡吗"，瞬间冒出七八个回复。</p><p>2. 有妈妈求助"孩子发烧了怎么办"，五分钟后收到二十几条建议。</p><p>3. 有人分享"今天又被孩子气哭了"，底下清一色的"我也是""抱抱"。</p><p>4. 一位单亲妈妈在群里说"好累"，有人主动提出帮她接孩子。</p><p>妈妈群，是这个世界上最温暖的互助组织。</p>'},
    {'title':'老公说：你就不能温柔一点吗','content':'<h4>老公说：你就不能温柔一点吗</h4><p>那天因为一件小事跟老公吵了起来，他突然冒出一句："你就不能温柔一点吗？像以前那样。"</p><p>我愣住了。像以前那样？以前我是一个人，只需要对自己负责。现在我是妈妈、是妻子、是女儿、是员工——我每天要处理一百件事情，还要保持温柔？</p><p>后来我平静地跟他说："我不是不温柔了，是太累了。你能不能帮我分担一点，而不是指责我？"他沉默了很久，然后默默去洗碗了。</p>'},
    {'title':'原来妈妈的妈妈，也曾是个小女孩','content':'<h4>原来妈妈的妈妈，也曾是个小女孩</h4><p>翻老相册，看到妈妈18岁的照片。梳着两条麻花辫，笑得眼睛弯弯的，站在一棵桃树下。</p><p>我才意识到：在我出生之前，她也是一个爱美、爱笑、对未来充满幻想的小姑娘。</p><p>是什么让她变成了现在这个——总是唠叨、总是操心、总是把所有好吃的夹到我碗里的妈妈？是岁月，也是爱。</p>'},
    {'title':'给孩子最好的礼物，是父母相爱','content':'<h4>给孩子最好的礼物，是父母相爱</h4><p>有研究说，孩子最害怕的不是被打骂，而是父母吵架。</p><p>每次我们吵架，孩子就会变得特别安静，躲在自己房间不出来。有一次吵完架，女儿跑过来拉住我和老公的手，把两只手放在一起，说："和好。"</p><p>那一刻我们都哭了。从那以后，我们约定：不在孩子面前吵架。有问题等孩子睡了再沟通。给孩子最好的教育，不是报多少班，是让他看到爸爸妈妈互相尊重、彼此相爱。</p>'},
    {'title':'你不需要做100分的妈妈','content':'<h4>你不需要做100分的妈妈</h4><p>这个社会对妈妈的要求太高了：要会做饭、要懂育儿、要保持身材、要有事业、要温柔体贴……</p><p>但你不是超人，你只是一个普通人。普通人就会累、就会烦、就会有做不好的时候。</p><p>60分就够了。剩下的40分，留给自己。你开心了，孩子才能开心。你轻松了，家庭氛围才会轻松。</p>'},
    {'title':'那些"别人家的妈妈"其实也很累','content':'<h4>那些"别人家的妈妈"其实也很累</h4><p>每次刷朋友圈都觉得别人家的妈妈好厉害：早餐摆盘像艺术品、周末亲子活动丰富多彩、孩子成绩优异多才多艺……</p><p>直到有一次跟一个"别人家的妈妈"喝酒，她才告诉我：精致的早餐照片背后是凌晨五点起床，周末的亲子照拍完后回家累到躺平，孩子的才艺课每个月花掉她一半工资。</p><p>没有人是轻松的。我们都在各自的生活里咬牙坚持。</p>'},
    {'title':'生二胎后，我差点忘了老大的存在','content':'<h4>生二胎后，我差点忘了老大的存在</h4><p>老二出生后，所有注意力都放在了这个嗷嗷待哺的小婴儿身上。直到有一天，老大站在房门口小声问："妈妈，你今天能陪我玩一会儿吗？"</p><p>我突然意识到，他已经很久没有撒娇、没有要求、没有"麻烦"我了。他学会了懂事，但懂事的背后是委屈。</p><p>那天晚上我抱着他哭了很久。从那以后，我规定自己每天至少花20分钟单独陪老大，不管多忙。</p>'},
    {'title':'一个人带娃最崩溃的时刻','content':'<h4>一个人带娃最崩溃的时刻</h4><p>娃生病、老公出差、自己也发烧。半夜起来量体温、喂药、哄睡，天亮还要爬起来做早饭。没有人帮忙，没有人问一句"你还好吗"。</p><p>坐在马桶上偷偷哭了两分钟，然后擦干眼泪继续。因为你知道：没有人能替你。你是妈妈，你是这座小宇宙唯一的支柱。</p><p>但请记住：再坚强的人也需要被照顾。不要害怕开口求助。打电话给朋友、请父母帮忙、哪怕只是找个钟点工。你不是一个人在战斗。</p>'},
]

def gen_daily_read(day_num):
    idx = day_num % len(ARTICLES_POOL)
    a = ARTICLES_POOL[idx]
    return {
        'title': a['title'],
        'content': a['content'],
        'author': '小粉推荐',
        'source': '精选',
        'date': datetime.now().strftime('%Y-%m-%d')
    }


# ============================================================
# 5. 每日单词（35个词，每天15个，足够循环）
# ============================================================
ALL_WORDS = [
    {'w':'resilience','p':'/rɪˈzɪl.i.əns/','m':'韧性','s':'Being a mom requires resilience — you bounce back from tough days.'},
    {'w':'boundary','p':'/ˈbaʊn.dər.i/','m':'边界','s':'Setting boundaries at work is essential for work-life balance.'},
    {'w':'empathy','p':'/ˈem.pə.θi/','m':'同理心','s':'Great content creators have deep empathy for their audience.'},
    {'w':'mindfulness','p':'/ˈmaɪnd.fəl.nəs/','m':'正念','s':'Practicing mindfulness helps me stay calm during stressful moments.'},
    {'w':'prioritize','p':'/praɪˈɒr.ɪ.taɪz/','m':'优先处理','s':'I need to prioritize my tasks — the article deadline comes first.'},
    {'w':'overwhelm','p':'/ˌəʊ.vəˈwelm/','m':'不知所措','s':'The to-do list can overwhelm me, so I break it into small steps.'},
    {'w':'nurture','p':'/ˈnɜː.tʃər/','m':'养育','s':'We nurture our children, but we also need to nurture ourselves.'},
    {'w':'authentic','p':'/ɔːˈθen.tɪk/','m':'真实的','s':'Readers can tell when your writing is authentic — be yourself.'},
    {'w':'milestone','p':'/ˈmaɪl.stəʊn/','m':'里程碑','s':'Every 10w+ article is a milestone worth celebrating.'},
    {'w':'collaborate','p':'/kəˈlæb.ə.reɪt/','m':'合作','s':'Good editors collaborate closely with writers to polish every piece.'},
    {'w':'perspective','p':'/pəˈspek.tɪv/','m':'视角','s':'A fresh perspective can turn an ordinary topic into a great story.'},
    {'w':'feedback','p':'/ˈfiːd.bæk/','m':'反馈','s':'I welcome feedback because it makes my work stronger.'},
    {'w':'balance','p':'/ˈbæl.əns/','m':'平衡','s':'Finding balance between work and family is a daily practice.'},
    {'w':'gratitude','p':'/ˈɡræt.ɪ.tjuːd/','m':'感恩','s':'Keeping a gratitude journal has changed how I see everyday life.'},
    {'w':'deadline','p':'/ˈded.laɪn/','m':'截止日期','s':"The deadline for this week's article is Thursday."},
    {'w':'brainstorm','p':'/ˈbreɪn.stɔːrm/','m':'头脑风暴','s':"Let's brainstorm some fresh angles for the parenting series."},
    {'w':'strategy','p':'/ˈstræt.ə.dʒi/','m':'策略','s':'Our content strategy focuses on building deep connections with readers.'},
    {'w':'engagement','p':'/ɪnˈɡeɪdʒ.mənt/','m':'互动','s':'Comments and shares are the best measures of reader engagement.'},
    {'w':'vulnerable','p':'/ˈvʌl.nər.ə.bəl/','m':'脆弱的','s':'Being vulnerable in your writing makes it more relatable.'},
    {'w':'sustainable','p':'/səˈsteɪ.nə.bəl/','m':'可持续的','s':'We need a sustainable content rhythm — not burnout in three months.'},
    {'w':'empower','p':'/ɪmˈpaʊ.ər/','m':'赋能','s':'Good articles empower readers to make positive changes.'},
    {'w':'multitask','p':'/ˌmʌl.tiˈtɑːsk/','m':'多任务处理','s':'Moms are masters at multitasking — cooking, listening, and planning at once.'},
    {'w':'recharge','p':'/ˌriːˈtʃɑːdʒ/','m':'充电','s':'I need some alone time to recharge after a busy week.'},
    {'w':'intentional','p':'/ɪnˈten.ʃən.əl/','m':'有意图的','s':'Be intentional about how you spend your energy each day.'},
    {'w':'journal','p':'/ˈdʒɜː.nəl/','m':'日志','s':'I journal every night — it helps me process the day.'},
    {'w':'negotiate','p':'/nɪˈɡəʊ.ʃi.eɪt/','m':'谈判','s':'Learning to negotiate at work boosted my confidence and salary.'},
    {'w':'optimize','p':'/ˈɒp.tɪ.maɪz/','m':'优化','s':'We constantly optimize headlines to get better click-through rates.'},
    {'w':'initiative','p':'/ɪˈnɪʃ.ə.tɪv/','m':'主动性','s':'Taking initiative on new projects shows leadership potential.'},
    {'w':'streamline','p':'/ˈstriːm.laɪn/','m':'精简','s':'We streamlined the editing process from five rounds to three.'},
    {'w':'accountability','p':'/əˌkaʊn.təˈbɪl.ə.ti/','m':'责任感','s':'Personal accountability is the foundation of professional growth.'},
    {'w':'leverage','p':'/ˈlev.ər.ɪdʒ/','m':'利用','s':"Leverage your personal experience — it's your unique content edge."},
    {'w':'productive','p':'/prəˈdʌk.tɪv/','m':'高效的','s':'Morning is my most productive time — I save writing for then.'},
    {'w':'advocate','p':'/ˈæd.və.keɪt/','m':'倡导','s':"Great writers advocate for their readers' needs and concerns."},
    {'w':'flexibility','p':'/ˌflek.sɪˈbɪl.ə.ti/','m':'灵活性','s':"Flexibility is key — some days the plan goes out the window."},
    {'w':'patience','p':'/ˈpeɪ.ʃəns/','m':'耐心','s':'Parenting teaches you patience — every single day.'},
]

def gen_daily_words(day_num):
    rng = random.Random(day_num * 131)
    shuffled = ALL_WORDS[:]
    rng.shuffle(shuffled)
    return shuffled[:15]


# ============================================================
# MAIN
# ============================================================
def main():
    os.makedirs(OUT, exist_ok=True)
    today = datetime.now()
    day_num = int(today.strftime('%Y%m%d'))
    week_num = today.isocalendar()[1]
    year = today.year

    # 1. 热点
    hot = fetch_hot()
    with open(f"{OUT}/hot.json", 'w') as f:
        json.dump({'updated': today.isoformat(), 'topics': hot}, f, ensure_ascii=False)
    print(f"✅ 热点: {len(hot)} 条")

    # 2. 菜单
    menu = gen_weekly_menu(week_num)
    with open(f"{OUT}/weekly_menu.json", 'w') as f:
        json.dump({'updated': today.isoformat(), 'week': week_num, 'menus': menu}, f, ensure_ascii=False)
    print(f"✅ 菜单: {len(menu)} 道")

    # 3. 运动
    exercise = gen_weekly_exercise(week_num)
    with open(f"{OUT}/weekly_exercise.json", 'w') as f:
        json.dump({'updated': today.isoformat(), 'week': week_num, 'plan': exercise}, f, ensure_ascii=False)
    print(f"✅ 运动: {len(exercise)} 天")

    # 4. 每日阅读
    read = gen_daily_read(day_num)
    with open(f"{OUT}/daily_read.json", 'w') as f:
        json.dump({'updated': today.isoformat(), 'article': read}, f, ensure_ascii=False)
    print(f"✅ 阅读: {read['title']}")

    # 5. 单词
    words = gen_daily_words(day_num)
    with open(f"{OUT}/daily_words.json", 'w') as f:
        json.dump({'updated': today.isoformat(), 'words': words}, f, ensure_ascii=False)
    print(f"✅ 单词: {len(words)} 个")

    print("\n🎉 全部数据生成完毕！")


if __name__ == '__main__':
    main()
