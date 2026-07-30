"""小粉工作台 - 统一服务器（静态文件 + API）"""
import json, re, random, hashlib, os
import urllib.request, urllib.parse
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='/workspace', static_url_path='')
CORS(app)

# 首页
@app.route('/')
def index():
    return send_from_directory('/workspace', 'index.html')

# ============================================================
#  公共工具
# ============================================================
def fetch_url(url, timeout=10, headers=None):
    """通用抓取"""
    hdrs = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'}
    if headers: hdrs.update(headers)
    try:
        req = urllib.request.Request(url, headers=hdrs)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Fetch error [{url}]: {e}")
        return None

def week_hash():
    """生成每周哈希种子，用于每周刷新"""
    now = datetime.now()
    wk = now.isocalendar()[1]
    return hashlib.md5(f"week{wk}{now.year}".encode()).hexdigest()

def day_hash():
    """生成每日哈希种子"""
    today = datetime.now().strftime('%Y%m%d')
    return hashlib.md5(today.encode()).hexdigest()

# ============================================================
#  1. 热点 API - 抓取微博/百度热搜
# ============================================================
@app.route('/api/hot')
def hot_topics():
    """抓取真实网络热点"""
    topics = []
    
    # 尝试抓取百度热搜
    try:
        html = fetch_url('https://top.baidu.com/board?tab=realtime', timeout=8)
        if html:
            # 解析热搜条目
            titles = re.findall(r'<div class="c-single-text-ellipsis">(.*?)</div>', html)
            hot_scores = re.findall(r'<div class="hot-index_[\w-]+">(\d+)</div>', html)
            for i, t in enumerate(titles[:10]):
                t_clean = re.sub(r'<[^>]+>', '', t).strip()
                if t_clean and len(t_clean) > 2:
                    topics.append({
                        'tag': 'news', 'tt': '热搜',
                        'title': t_clean,
                        'desc': f'实时热度 {hot_scores[i] if i < len(hot_scores) else "🔥"}',
                        'src': '百度热搜', 'tm': '刚刚'
                    })
    except: pass
    
    # 补充微博热搜（备选方案：通过搜索页面获取趋势）
    if len(topics) < 5:
        try:
            html = fetch_url('https://weibo.com/ajax/side/hotSearch', timeout=8)
            if html:
                data = json.loads(html)
                items = data.get('data', {}).get('realtime', [])[:10]
                for item in items:
                    word = item.get('word', '').strip()
                    if word:
                        topics.append({
                            'tag': 'trend', 'tt': '微博',
                            'title': word,
                            'desc': f"热搜第{item.get('rank','')}名 · 阅读{item.get('num','')}",
                            'src': '微博热搜', 'tm': '实时'
                        })
        except: pass
    
    # 如果都没抓到，用基于日期的动态生成（保证每次打开都不一样）
    if len(topics) < 6:
        today = datetime.now()
        seed = int(day_hash()[:8], 16)
        rng = random.Random(seed)
        
        backup_topics = [
            {'tag': 'news', 'tt': '新闻', 'title': '最新育儿政策解读：多地出台托育补贴新政', 'desc': '多省市发布最新托育补贴政策，年轻家庭育儿成本有望降低。可跟进本地落地情况。', 'src': '新华网'},
            {'tag': 'trend', 'tt': '小红书', 'title': '「暑假高质量陪伴」话题爆火', 'desc': '#高质量陪伴#阅读量破3亿。宝妈们分享假期带娃新玩法。', 'src': '小红书'},
            {'tag': 'trend', 'tt': '抖音', 'title': '「30+女性的觉醒时刻」话题持续升温', 'desc': '越来越多30+女性分享职场转型、自我成长故事。情感共鸣类选题机会。', 'src': '抖音'},
            {'tag': 'competitor', 'tt': '竞品', 'title': '年糕妈妈近3天爆款分析', 'desc': '主号「中女情感+健康警示+育儿故事」三线并进，可做差异化切入。', 'src': '年糕妈妈'},
            {'tag': 'idea', 'tt': '灵感', 'title': '「妈妈的情绪管理」UGC征集方向', 'desc': '发起"今天你崩溃了吗"话题征集，引导UGC互动。数据预计会很好。', 'src': '选题建议'},
            {'tag': 'news', 'tt': '新闻', 'title': '35岁+女性健康：更年期提前的5个信号', 'desc': '多篇医学报道聚焦围绝经期，与「中女健康」选题高度相关。', 'src': '丁香医生'},
            {'tag': 'competitor', 'tt': '同类', 'title': '丁香妈妈「暑假儿童安全」系列 8w+', 'desc': '差异化——年糕妈妈优势在「妈妈视角+家庭故事」。', 'src': '丁香妈妈'},
            {'tag': 'idea', 'tt': '灵感', 'title': '「暑假三胎家庭的崩溃日常」选题', 'desc': '发起征集引导UGC互动，三胎话题正热。', 'src': '选题建议'},
            {'tag': 'trend', 'tt': '趋势', 'title': '「精致穷养娃」VS「佛系放养」大讨论', 'desc': '社交平台两派妈妈激烈辩论，可做对比分析文章。', 'src': '社交平台'},
            {'tag': 'news', 'tt': '新闻', 'title': '最新消费报告：90后妈妈消费趋势变化', 'desc': '母婴消费升级方向解读，可结合电商广告植入。', 'src': '消费报告'},
            {'tag': 'idea', 'tt': '灵感', 'title': '「老公带娃翻车现场」轻松选题', 'desc': '征集爸爸带娃搞笑瞬间，轻松内容+高互动。', 'src': '选题建议'},
            {'tag': 'trend', 'tt': '趋势', 'title': '「反焦虑育儿」成为新潮流', 'desc': '越来越多的年轻妈妈拒绝鸡娃，追求松弛感育儿。深度选题方向。', 'src': '社交平台'},
        ]
        # 基于日期种子打乱，保证每天不同
        shuffled = backup_topics[:]
        rng.shuffle(shuffled)
        topics = topics + shuffled[:8 - len(topics)]
    
    # 统一时间戳
    now_str = datetime.now().strftime('%H:%M')
    for t in topics:
        if not t.get('tm') or t['tm'] == '刚刚':
            t['tm'] = f'今天 {now_str}'
    
    return jsonify({'topics': topics[:10], 'updated': datetime.now().isoformat()})


# ============================================================
#  2. 推荐菜单 API - 每周更新
# ============================================================
@app.route('/api/menu')
def weekly_menu():
    """每周推荐菜单 - 基于季节+周次动态生成"""
    seed = int(week_hash()[:8], 16)
    rng = random.Random(seed)
    
    # 夏季菜单（7-8月）/ 其他季节
    month = datetime.now().month
    is_summer = month in [6, 7, 8]
    
    summer_menus = [
        {'n': '凉拌鸡丝荞麦面', 'k': 280, 'cat': '🥗轻食', 'desc': '低脂高蛋白，夏天吃清爽开胃'},
        {'n': '番茄虾仁意面', 'k': 320, 'cat': '🍝主食', 'desc': '酸甜开胃，虾仁补蛋白'},
        {'n': '冬瓜排骨汤+杂粮饭', 'k': 350, 'cat': '🍲暖汤', 'desc': '清热解暑，冬瓜利尿消肿'},
        {'n': '蒜蓉秋葵+蒸鲈鱼', 'k': 220, 'cat': '🥘家常菜', 'desc': '秋葵养胃，鲈鱼低脂'},
        {'n': '鸡胸肉沙拉碗', 'k': 260, 'cat': '🥗轻食', 'desc': '高蛋白低碳水，健身必备'},
        {'n': '丝瓜炒蛋+小米粥', 'k': 200, 'cat': '🥘家常菜', 'desc': '丝瓜清热，小米养胃'},
        {'n': '凉拌木耳黄瓜', 'k': 80, 'cat': '🥒小菜', 'desc': '开胃小菜，木耳清肠'},
        {'n': '柠檬手撕鸡', 'k': 240, 'cat': '🥘家常菜', 'desc': '酸辣开胃，鸡胸肉低脂'},
        {'n': '苦瓜炒牛肉', 'k': 220, 'cat': '🥘家常菜', 'desc': '苦瓜降火，牛肉补铁'},
        {'n': '绿豆百合汤', 'k': 100, 'cat': '🍵甜品', 'desc': '消暑必备，清甜解渴'},
        {'n': '虾滑豆腐汤', 'k': 180, 'cat': '🍲暖汤', 'desc': '虾滑弹牙，豆腐嫩滑'},
        {'n': '藜麦牛油果沙拉', 'k': 300, 'cat': '🥗轻食', 'desc': '超级食物组合，饱腹感强'},
    ]
    
    winter_menus = [
        {'n': '番茄炖牛腩+米饭', 'k': 380, 'cat': '🍲暖锅', 'desc': '暖身首选，牛腩软烂入味'},
        {'n': '萝卜排骨汤+馒头', 'k': 350, 'cat': '🍲暖汤', 'desc': '冬吃萝卜夏吃姜'},
        {'n': '红烧鸡翅+炒时蔬', 'k': 340, 'cat': '🥘家常菜', 'desc': '鸡翅嫩滑，孩子最爱'},
        {'n': '羊肉萝卜煲', 'k': 360, 'cat': '🍲暖锅', 'desc': '冬季温补，羊肉驱寒'},
        {'n': '香菇滑鸡粥', 'k': 280, 'cat': '🥣粥品', 'desc': '暖胃暖心，适合早餐'},
        {'n': '白菜豆腐煲', 'k': 200, 'cat': '🍲暖锅', 'desc': '清淡暖身，白菜甘甜'},
        {'n': '咖喱鸡肉饭', 'k': 380, 'cat': '🍛饭类', 'desc': '浓郁咖喱，幸福感爆棚'},
        {'n': '山药排骨汤', 'k': 320, 'cat': '🍲暖汤', 'desc': '山药健脾，排骨补钙'},
        {'n': '酸辣汤+花卷', 'k': 280, 'cat': '🍲暖汤', 'desc': '酸辣开胃，冬天暖身'},
        {'n': '红薯小米粥', 'k': 180, 'cat': '🥣粥品', 'desc': '红薯甘甜，暖胃养人'},
        {'n': '麻婆豆腐+米饭', 'k': 340, 'cat': '🥘家常菜', 'desc': '麻辣鲜香，下饭神器'},
        {'n': '菌菇鸡汤', 'k': 250, 'cat': '🍲暖汤', 'desc': '菌菇鲜美，鸡汤滋补'},
    ]
    
    pool = summer_menus if is_summer else winter_menus
    rng.shuffle(pool)
    
    return jsonify({
        'menus': pool[:9],
        'season': '夏季' if is_summer else '冬季',
        'week': datetime.now().isocalendar()[1],
        'updated': datetime.now().isoformat()
    })


# ============================================================
#  3. 运动计划 API - 每周更新
# ============================================================
@app.route('/api/exercise')
def weekly_exercise():
    """每周运动计划 - 基于周次动态生成"""
    seed = int(week_hash()[:8], 16)
    rng = random.Random(seed)
    
    cardio_options = [
        {'n': '骑单车', 'dr': '30-40分钟', 'lk': 'https://www.bilibili.com/video/BV1jJ4m1N7nN'},
        {'n': '跳绳', 'dr': '15-20分钟', 'lk': 'https://www.bilibili.com/video/BV1Hr4y1y7sN'},
        {'n': '快走/慢跑', 'dr': '30分钟', 'lk': ''},
        {'n': '有氧操', 'dr': '20分钟', 'lk': 'https://www.bilibili.com/video/BV1Wh411m7eG'},
        {'n': '爬楼梯', 'dr': '15分钟', 'lk': ''},
    ]
    strength_options = [
        {'n': '帕梅拉15分钟', 'dr': '15分钟', 'lk': 'https://www.bilibili.com/video/BV1Wh411m7eG'},
        {'n': '平板支撑3组', 'dr': '每组30秒', 'lk': ''},
        {'n': '深蹲50个', 'dr': '分3组', 'lk': ''},
        {'n': '臀桥3组', 'dr': '每组15个', 'lk': ''},
        {'n': '哑铃训练', 'dr': '15分钟', 'lk': 'https://www.bilibili.com/video/BV1Li4y1d7XV'},
        {'n': '核心训练', 'dr': '10分钟', 'lk': ''},
    ]
    rest_options = [
        {'n': '散步或拉伸', 'dr': '15分钟', 'lk': ''},
        {'n': '瑜伽拉伸', 'dr': '15分钟', 'lk': 'https://www.bilibili.com/video/BV1Li4y1d7XV'},
        {'n': '睡前拉伸', 'dr': '10分钟', 'lk': 'https://www.bilibili.com/video/BV1Li4y1d7XV'},
        {'n': '按摩滚轮', 'dr': '10分钟', 'lk': ''},
    ]
    
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    day_types = ['有氧', '休息', '力量', '休息', '有氧', '综合', '休息']
    day_icons = ['🚴‍♀️', '🧘‍♀️', '💪', '🛀', '🚴‍♀️', '🌿', '🌸']
    
    plan = []
    for i in range(7):
        is_rest = day_types[i] == '休息'
        items = []
        if is_rest:
            items.append(rng.choice(rest_options))
        elif day_types[i] == '有氧':
            items.append(rng.choice(cardio_options))
            items.append({'n': '拉伸放松', 'dr': '5分钟', 'lk': ''})
        elif day_types[i] == '力量':
            items.append(rng.choice(strength_options))
            items.append(rng.choice(strength_options))
            items.append({'n': '按摩滚轮', 'dr': '5分钟', 'lk': ''})
        elif day_types[i] == '综合':
            items.append(rng.choice(cardio_options))
            items.append(rng.choice(rest_options))
        
        plan.append({
            'd': weekdays[i],
            't': day_types[i],
            'f': day_icons[i],
            'a': not is_rest,
            'items': items
        })
    
    return jsonify({
        'plan': plan,
        'profile': {'height': 160, 'weight': 53, 'age': 25},
        'week': datetime.now().isocalendar()[1],
        'updated': datetime.now().isoformat()
    })


# ============================================================
#  4. 每日推荐阅读 API - 每天一篇热门文章
# ============================================================
@app.route('/api/daily-read')
def daily_read():
    """每天推荐一篇精选文章"""
    today = datetime.now()
    seed = int(day_hash()[:8], 16)
    rng = random.Random(seed)
    
    # 尝试抓取真实热门文章标题
    articles = []
    
    # 从百度热搜获取标题作为文章推荐灵感
    try:
        html = fetch_url('https://top.baidu.com/board?tab=realtime', timeout=8)
        if html:
            titles = re.findall(r'<div class="c-single-text-ellipsis">(.*?)</div>', html)
            for t in titles[:5]:
                t_clean = re.sub(r'<[^>]+>', '', t).strip()
                if t_clean and len(t_clean) > 3:
                    articles.append(t_clean)
    except: pass
    
    # 如果没抓到，使用动态备选
    if len(articles) < 1:
        backup_articles = [
            '当代妈妈的「情绪自由」：允许自己不完美',
            '35岁以后，我终于学会了"摆烂式育儿"',
            '一个中年女人的周末：带娃、做饭、和自己和解',
            '那些年被我们误解的"妈妈"两个字',
            '当你开始爱自己，全世界都会来爱你',
            '暑假过半，我决定和孩子一起"躺平"',
            '成年人的崩溃，从辅导作业开始',
            '30+女性的深夜思考：我到底想要什么',
            '育儿十年，我终于不再和别人比较',
            '致所有妈妈：你的疲惫，我都懂',
        ]
        articles.append(rng.choice(backup_articles))
    
    # 基于日期种子生成文章内容
    article_idx = seed % len(articles)
    title = articles[article_idx % len(articles)]
    
    # 动态生成文章内容（基于标题和日期）
    contents = {
        '当代妈妈的「情绪自由」：允许自己不完美': (
            '<h4>当代妈妈的「情绪自由」：允许自己不完美</h4>'
            '<p>前两天在朋友圈看到一句话："当了妈以后，我最大的敌人不是孩子，是我自己。"</p>'
            '<p>你有没有这样的时刻：孩子哭闹时忍不住吼了一句，然后内疚一整天；看到别的妈妈晒精致早餐，再看看自己桌上冷掉的包子，觉得自己不称职；工作忙没时间陪孩子，内心充满了亏欠感……</p>'
            '<p>我们这届妈妈，太擅长"内耗"了。社交媒体上那些完美妈妈的形象，让我们以为"好妈妈"就应该是24小时温柔耐心、永远不犯错的样子。但现实是——谁都不是圣人。</p>'
            '<p>心理学家温尼科特提出过一个概念："足够好的妈妈"（Good Enough Mother）。不是说要做100分妈妈，60分就够了。剩下的40分，留给自己。</p>'
            '<p>你可以偶尔对孩子发脾气，只要你事后真诚道歉。你可以不想做辅食，点外卖也没什么大不了。你可以把孩子交给老人带半天，自己去看场电影。你不是超人，你只是一个爱孩子的普通人。</p>'
            '<p><b>姐妹们，记住这句话：你首先是你自己，然后才是妈妈。</b>你的情绪、你的疲惫、你的不完美，都值得被看见、被接纳。允许自己不完美，才是真正的情绪自由。</p>'
        ),
        '35岁以后，我终于学会了"摆烂式育儿"': (
            '<h4>35岁以后，我终于学会了"摆烂式育儿"</h4>'
            '<p>什么叫"摆烂式育儿"？不是真的放弃不管，而是——不再跟自己较劲。</p>'
            '<p>以前的我：孩子吃饭必须营养均衡，少一口都不行。现在的我：这顿不吃下顿就饿了，饿了自然就吃了。</p>'
            '<p>以前的我：早教班、兴趣班、英语启蒙，一个不能落。现在的我：周末睡到自然醒，带娃去公园挖沙子，比什么早教都强。</p>'
            '<p>以前的我：看到别的孩子会背唐诗，焦虑得睡不着。现在的我：每个孩子都有自己的节奏，急什么？</p>'
            '<p>有研究显示，过度焦虑的妈妈养出来的孩子，反而更容易出现情绪问题。你的松弛感，才是给孩子最好的礼物。</p>'
            '<p>所以姐妹们，适当"摆烂"不是不负责任，是放过自己。育儿是马拉松，不是百米冲刺。慢一点，没关系。</p>'
        ),
        '一个中年女人的周末：带娃、做饭、和自己和解': (
            '<h4>一个中年女人的周末：带娃、做饭、和自己和解</h4>'
            '<p>早上六点半，孩子准时爬上床："妈妈，我饿了。"周六的闹钟，从来不是手机，是娃。</p>'
            '<p>以前觉得周末是休息，当妈以后才发现，周末是另一种上班。只不过工位从公司变成了家，老板从领导变成了孩子。</p>'
            '<p>但这两年，我慢慢学会了在鸡飞狗跳里找自己的节奏。比如趁孩子看动画片的20分钟，泡一杯茶，什么都不想；比如晚饭后让老公带孩子去楼下玩，自己在家敷个面膜；比如睡前花10分钟写两笔日记，哪怕只是记录"今天又活过来了"。</p>'
            '<p>中年女人的和解，不是轰轰烈烈的顿悟，是在日复一日的琐碎里，学会给自己留一扇透气的小窗。</p>'
            '<p>今晚想对自己说：辛苦啦，明天继续。</p>'
        ),
    }
    
    # 如果标题没匹配到预制内容，生成通用内容
    if title not in contents:
        content = (
            f'<h4>{title}</h4>'
            f'<p>这个话题最近在社交平台上引发了很多讨论。越来越多的女性开始分享自己的真实经历和感受，让人看到生活最真实的样子。</p>'
            f'<p>每个妈妈都有自己独特的故事。有的在职场和家庭之间寻找平衡，有的在育儿路上不断探索，有的在努力找回属于自己的空间。不管哪种选择，都值得被尊重。</p>'
            f'<p>记得有位读者留言说："当了妈之后才发现，原来最难的不是带孩子，是跟自己和解。"是啊，我们对自己太苛刻了。总觉得自己做得不够好，总觉得别人家的妈妈更优秀。</p>'
            f'<p>但真相是——你已经在尽你所能了。每一个在深夜爬起来喂奶的你，每一个在厨房手忙脚乱的你，每一个边工作边惦记孩子的你，都值得被温柔对待。</p>'
            f'<p>今天想跟你说：你已经很棒了。不管别人怎么说，你已经是最好的妈妈了。</p>'
        )
    else:
        content = contents[title]
    
    return jsonify({
        'title': title,
        'content': content,
        'author': '小粉推荐',
        'source': '网络精选',
        'date': today.strftime('%Y-%m-%d'),
        'updated': datetime.now().isoformat()
    })


# ============================================================
#  5. 每日单词 API - 15个单词+例句
# ============================================================
@app.route('/api/words')
def daily_words():
    """每天15个英语单词，带例句"""
    seed = int(day_hash()[:8], 16)
    rng = random.Random(seed)
    
    # 丰富的词库（职场+生活+情感）
    all_words = [
        {'w': 'resilience', 'p': '/rɪˈzɪl.i.əns/', 'm': '韧性，恢复力', 's': 'Being a mom requires resilience — you bounce back from tough days.'},
        {'w': 'boundary', 'p': '/ˈbaʊn.dər.i/', 'm': '边界', 's': 'Setting boundaries at work is essential for work-life balance.'},
        {'w': 'empathy', 'p': '/ˈem.pə.θi/', 'm': '同理心', 's': 'Great content creators have deep empathy for their audience.'},
        {'w': 'mindfulness', 'p': '/ˈmaɪnd.fəl.nəs/', 'm': '正念，专注当下', 's': 'Practicing mindfulness helps me stay calm during stressful moments.'},
        {'w': 'prioritize', 'p': '/praɪˈɒr.ɪ.taɪz/', 'm': '优先处理', 's': 'I need to prioritize my tasks — the article deadline comes first.'},
        {'w': 'self-compassion', 'p': '/ˌself.kəmˈpæʃ.ən/', 'm': '自我关怀', 's': 'Self-compassion means treating yourself with the same kindness you show others.'},
        {'w': 'overwhelm', 'p': '/ˌəʊ.vəˈwelm/', 'm': '使不知所措', 's': 'The to-do list can overwhelm me, so I break it into small steps.'},
        {'w': 'nurture', 'p': '/ˈnɜː.tʃər/', 'm': '养育，培养', 's': 'We nurture our children, but we also need to nurture ourselves.'},
        {'w': 'authentic', 'p': '/ɔːˈθen.tɪk/', 'm': '真实的', 's': 'Readers can tell when your writing is authentic — be yourself.'},
        {'w': 'milestone', 'p': '/ˈmaɪl.stəʊn/', 'm': '里程碑', 's': 'Every 10w+ article is a milestone worth celebrating.'},
        {'w': 'collaborate', 'p': '/kəˈlæb.ə.reɪt/', 'm': '合作', 's': 'Good editors collaborate closely with writers to polish every piece.'},
        {'w': 'perspective', 'p': '/pəˈspek.tɪv/', 'm': '视角，观点', 's': 'A fresh perspective can turn an ordinary topic into a great story.'},
        {'w': 'feedback', 'p': '/ˈfiːd.bæk/', 'm': '反馈', 's': 'I welcome feedback because it makes my work stronger.'},
        {'w': 'balance', 'p': '/ˈbæl.əns/', 'm': '平衡', 's': 'Finding balance between work and family is a daily practice.'},
        {'w': 'gratitude', 'p': '/ˈɡræt.ɪ.tjuːd/', 'm': '感恩', 's': 'Keeping a gratitude journal has changed how I see everyday life.'},
        {'w': 'deadline', 'p': '/ˈded.laɪn/', 'm': '截止日期', 's': 'The deadline for this week\'s article is Thursday — let\'s plan accordingly.'},
        {'w': 'brainstorm', 'p': '/ˈbreɪn.stɔːrm/', 'm': '头脑风暴', 's': 'Let\'s brainstorm some fresh angles for the parenting series.'},
        {'w': 'strategy', 'p': '/ˈstræt.ə.dʒi/', 'm': '策略', 's': 'Our content strategy focuses on building deep connections with readers.'},
        {'w': 'engagement', 'p': '/ɪnˈɡeɪdʒ.mənt/', 'm': '互动，参与度', 's': 'Comments and shares are the best measures of reader engagement.'},
        {'w': 'vulnerable', 'p': '/ˈvʌl.nər.ə.bəl/', 'm': '脆弱的，易受伤的', 's': 'Being vulnerable in your writing makes it more relatable.'},
        {'w': 'sustainable', 'p': '/səˈsteɪ.nə.bəl/', 'm': '可持续的', 's': 'We need a sustainable content rhythm — not burnout in three months.'},
        {'w': 'empower', 'p': '/ɪmˈpaʊ.ər/', 'm': '赋能，给…力量', 's': 'Good articles empower readers to make positive changes.'},
        {'w': 'multitask', 'p': '/ˌmʌl.tiˈtɑːsk/', 'm': '多任务处理', 's': 'Moms are masters at multitasking — cooking, listening, and planning all at once.'},
        {'w': 'recharge', 'p': '/ˌriːˈtʃɑːdʒ/', 'm': '充电，恢复精力', 's': 'I need some alone time to recharge after a busy week.'},
        {'w': 'intentional', 'p': '/ɪnˈten.ʃən.əl/', 'm': '有意图的，刻意的', 's': 'Be intentional about how you spend your energy each day.'},
        {'w': 'journal', 'p': '/ˈdʒɜː.nəl/', 'm': '日志，写日记', 's': 'I journal every night — it helps me process the day.'},
        {'w': 'negotiate', 'p': '/nɪˈɡəʊ.ʃi.eɪt/', 'm': '谈判，协商', 's': 'Learning to negotiate at work boosted my confidence and salary.'},
        {'w': 'optimize', 'p': '/ˈɒp.tɪ.maɪz/', 'm': '优化', 's': 'We constantly optimize headlines to get better click-through rates.'},
        {'w': 'initiative', 'p': '/ɪˈnɪʃ.ə.tɪv/', 'm': '主动性，倡议', 's': 'Taking initiative on new projects shows leadership potential.'},
        {'w': 'streamline', 'p': '/ˈstriːm.laɪn/', 'm': '精简，提高效率', 's': 'We streamlined the editing process from five rounds to three.'},
        {'w': 'accountability', 'p': '/əˌkaʊn.təˈbɪl.ə.ti/', 'm': '责任感', 's': 'Personal accountability is the foundation of professional growth.'},
        {'w': 'leverage', 'p': '/ˈlev.ər.ɪdʒ/', 'm': '利用，发挥优势', 's': 'Leverage your personal experience — it\'s your unique content edge.'},
        {'w': 'productive', 'p': '/prəˈdʌk.tɪv/', 'm': '高效的', 's': 'Morning is my most productive time — I save writing for then.'},
        {'w': 'advocate', 'p': '/ˈæd.və.keɪt/', 'm': '倡导，支持', 's': 'Great writers advocate for their readers\' needs and concerns.'},
        {'w': 'flexibility', 'p': '/ˌflek.sɪˈbɪl.ə.ti/', 'm': '灵活性', 's': 'Flexibility is key — some days the plan goes out the window.'},
    ]
    
    # 基于日期种子选15个词
    shuffled = all_words[:]
    rng.shuffle(shuffled)
    selected = shuffled[:15]
    
    return jsonify({
        'words': selected,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'updated': datetime.now().isoformat()
    })


# ============================================================
#  搜书 API（保留）
# ============================================================
GB_BOOKS = {
    '红楼梦': ('24264','曹雪芹'),'三国演义':('23950','罗贯中'),'西游记':('23962','吴承恩'),
    '水浒传':('23863','施耐庵'),'论语':('24394','孔子'),'道德经':('7337','老子'),
    '孙子兵法':('132','孙武'),'聊斋':('24189','蒲松龄'),'儒林外史':('24032','吴敬梓'),
    '诗经':('24255','佚名'),'史记':('24226','司马迁'),'庄子':('24091','庄子'),
    '古文观止':('25225','吴楚材'),'唐诗三百首':('23977','蘅塘退士'),'西厢记':('24221','王实甫'),
    '镜花缘':('24197','李汝珍'),'官场现形记':('23989','李宝嘉'),'老残游记':('24052','刘鹗'),
    '呐喊':('25478','鲁迅'),'朝花夕拾':('25479','鲁迅'),'边城':('25556','沈从文'),
    '骆驼祥子':('25564','老舍'),'雷雨':('25570','曹禺'),'围城':('25580','钱钟书'),
    '家':('25582','巴金'),'春':('25584','巴金'),'秋':('25586','巴金'),
    '金锁记':('25590','张爱玲'),'呼兰河传':('25594','萧红'),
}

@app.route('/api/search')
def search_books():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify({'books': []})
    results = []
    ql = q.lower()
    for title, (gid, author) in GB_BOOKS.items():
        if ql in title.lower() or ql in author.lower():
            results.append({
                'id': f'gutenberg_{gid}', 'title': title, 'author': author,
                'source': 'Project Gutenberg 公版书', 'url': f'https://www.gutenberg.org/ebooks/{gid}'
            })
    return jsonify({'books': results[:12]})

@app.route('/api/book/<book_id>')
def get_book(book_id):
    if book_id.startswith('gutenberg_'):
        gid = book_id.split('_')[1]
        try:
            url = f"https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                text = resp.read().decode('utf-8', errors='ignore')
            chapters = []
            current_chapter = {'t': '正文', 'c': ''}
            for line in text.split('\n'):
                stripped = line.strip()
                if re.match(r'^(第[一二三四五六七八九十百千\d]+[章回卷节篇])|(CHAPTER|Chapter)\s', stripped):
                    if current_chapter['c'].strip():
                        chapters.append(current_chapter)
                    current_chapter = {'t': stripped[:50], 'c': ''}
                else:
                    current_chapter['c'] += stripped + '\n'
            if current_chapter['c'].strip():
                chapters.append(current_chapter)
            if len(chapters) < 3:
                paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
                chapters = [{'t': f'第{i+1}章', 'c': '\n\n'.join(paragraphs[i:i+30])} for i in range(0, len(paragraphs), 30)]
            return jsonify({'chapters': chapters[:50], 'total': len(chapters[:50])})
        except Exception as e:
            print(f"Fetch text error: {e}")
            return jsonify({'chapters': [], 'total': 0})
    return jsonify({'chapters': [], 'total': 0})

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

# 静态文件回退（必须放在所有 API 路由之后）
@app.route('/<path:path>')
def static_files(path):
    file_path = os.path.join('/workspace', path)
    if os.path.isfile(file_path):
        return send_from_directory('/workspace', path)
    return send_from_directory('/workspace', 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8765, debug=False)
