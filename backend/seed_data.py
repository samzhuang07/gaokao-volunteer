"""
Seed data generator for the Gaokao volunteer system.
Uses real score-rank mappings from official Gaokao one-point-one-section tables
to generate accurate admission score data for demonstration.
"""
import random
from database import SessionLocal, init_db
from models import Province, University, Major, AdmissionScore
from services.rank_lookup import lookup as rank_lookup

random.seed(12345)

PROVINCES = [
    ("北京", "新高考"), ("天津", "新高考"), ("河北", "新高考"),
    ("山西", "传统高考"), ("内蒙古", "传统高考"), ("辽宁", "新高考"),
    ("吉林", "传统高考"), ("黑龙江", "传统高考"), ("上海", "新高考"),
    ("江苏", "新高考"), ("浙江", "新高考"), ("安徽", "新高考"),
    ("福建", "新高考"), ("江西", "传统高考"), ("山东", "新高考"),
    ("河南", "传统高考"), ("湖北", "新高考"), ("湖南", "新高考"),
    ("广东", "新高考"), ("广西", "传统高考"), ("海南", "新高考"),
    ("重庆", "新高考"), ("四川", "传统高考"), ("贵州", "传统高考"),
    ("云南", "传统高考"), ("西藏", "传统高考"), ("陕西", "传统高考"),
    ("甘肃", "传统高考"), ("青海", "传统高考"), ("宁夏", "传统高考"),
    ("新疆", "传统高考"),
]

UNIVERSITY_LEVELS = {
    "985": 39, "211": 80, "双一流": 40, "普通": 80,
}

UNIVERSITY_TYPES = ["综合", "理工", "师范", "医药", "农林", "财经", "政法", "语言", "艺术", "体育"]

UNIVERSITIES_BY_PROVINCE = {
    "北京": [
        ("北京大学", "985", "综合"), ("清华大学", "985", "理工"), ("中国人民大学", "985", "综合"),
        ("北京师范大学", "985", "师范"), ("北京航空航天大学", "985", "理工"), ("北京理工大学", "985", "理工"),
        ("中国农业大学", "985", "农林"), ("中央民族大学", "985", "综合"), ("北京邮电大学", "211", "理工"),
        ("北京交通大学", "211", "理工"), ("北京科技大学", "211", "理工"), ("北京化工大学", "211", "理工"),
        ("北京工业大学", "211", "理工"), ("北京林业大学", "211", "农林"), ("北京中医药大学", "211", "医药"),
        ("中国传媒大学", "211", "语言"), ("中央财经大学", "211", "财经"), ("对外经济贸易大学", "211", "财经"),
        ("中国政法大学", "211", "政法"), ("北京外国语大学", "211", "语言"), ("首都师范大学", "双一流", "师范"),
        ("中国科学院大学", "双一流", "综合"), ("北京协和医学院", "双一流", "医药"),
    ],
    "天津": [
        ("南开大学", "985", "综合"), ("天津大学", "985", "理工"), ("天津医科大学", "211", "医药"),
        ("河北工业大学", "211", "理工"), ("天津工业大学", "双一流", "理工"),
        ("天津师范大学", "普通", "师范"), ("天津财经大学", "普通", "财经"),
    ],
    "河北": [
        ("华北电力大学(保定)", "211", "理工"), ("燕山大学", "普通", "理工"), ("河北大学", "普通", "综合"),
        ("河北师范大学", "普通", "师范"), ("河北医科大学", "普通", "医药"),
    ],
    "山西": [
        ("太原理工大学", "211", "理工"), ("山西大学", "双一流", "综合"), ("中北大学", "普通", "理工"),
        ("山西医科大学", "普通", "医药"),
    ],
    "内蒙古": [
        ("内蒙古大学", "211", "综合"), ("内蒙古科技大学", "普通", "理工"),
        ("内蒙古师范大学", "普通", "师范"),
    ],
    "辽宁": [
        ("大连理工大学", "985", "理工"), ("东北大学", "985", "理工"), ("大连海事大学", "211", "理工"),
        ("辽宁大学", "211", "综合"), ("东北财经大学", "普通", "财经"), ("中国医科大学", "普通", "医药"),
    ],
    "吉林": [
        ("吉林大学", "985", "综合"), ("东北师范大学", "211", "师范"), ("延边大学", "211", "综合"),
        ("长春理工大学", "普通", "理工"),
    ],
    "黑龙江": [
        ("哈尔滨工业大学", "985", "理工"), ("哈尔滨工程大学", "211", "理工"),
        ("东北林业大学", "211", "农林"), ("东北农业大学", "211", "农林"), ("黑龙江大学", "普通", "综合"),
    ],
    "上海": [
        ("复旦大学", "985", "综合"), ("上海交通大学", "985", "理工"), ("同济大学", "985", "理工"),
        ("华东师范大学", "985", "师范"), ("上海财经大学", "211", "财经"), ("华东理工大学", "211", "理工"),
        ("上海大学", "211", "综合"), ("东华大学", "211", "理工"), ("上海外国语大学", "211", "语言"),
        ("上海科技大学", "双一流", "理工"),
    ],
    "江苏": [
        ("南京大学", "985", "综合"), ("东南大学", "985", "理工"), ("南京航空航天大学", "211", "理工"),
        ("南京理工大学", "211", "理工"), ("苏州大学", "211", "综合"), ("河海大学", "211", "理工"),
        ("南京师范大学", "211", "师范"), ("中国药科大学", "211", "医药"), ("江南大学", "211", "综合"),
        ("南京农业大学", "211", "农林"), ("南京邮电大学", "双一流", "理工"), ("南京医科大学", "双一流", "医药"),
    ],
    "浙江": [
        ("浙江大学", "985", "综合"), ("浙江工业大学", "普通", "理工"), ("宁波大学", "双一流", "综合"),
        ("浙江师范大学", "普通", "师范"), ("杭州电子科技大学", "普通", "理工"),
        ("温州医科大学", "普通", "医药"),
    ],
    "安徽": [
        ("中国科学技术大学", "985", "理工"), ("合肥工业大学", "211", "理工"),
        ("安徽大学", "211", "综合"), ("安徽师范大学", "普通", "师范"), ("安徽医科大学", "普通", "医药"),
    ],
    "福建": [
        ("厦门大学", "985", "综合"), ("福州大学", "211", "理工"), ("福建师范大学", "普通", "师范"),
        ("华侨大学", "普通", "综合"),
    ],
    "江西": [
        ("南昌大学", "211", "综合"), ("江西财经大学", "普通", "财经"), ("江西师范大学", "普通", "师范"),
    ],
    "山东": [
        ("山东大学", "985", "综合"), ("中国海洋大学", "985", "综合"), ("中国石油大学(华东)", "211", "理工"),
        ("山东师范大学", "普通", "师范"), ("青岛大学", "普通", "综合"), ("山东科技大学", "普通", "理工"),
        ("济南大学", "普通", "综合"), ("山东农业大学", "普通", "农林"),
    ],
    "河南": [
        ("郑州大学", "211", "综合"), ("河南大学", "双一流", "综合"), ("河南师范大学", "普通", "师范"),
        ("河南科技大学", "普通", "理工"), ("河南农业大学", "普通", "农林"),
    ],
    "湖北": [
        ("武汉大学", "985", "综合"), ("华中科技大学", "985", "理工"), ("武汉理工大学", "211", "理工"),
        ("华中师范大学", "211", "师范"), ("中南财经政法大学", "211", "财经"), ("中国地质大学(武汉)", "211", "理工"),
        ("华中农业大学", "211", "农林"),
    ],
    "湖南": [
        ("中南大学", "985", "综合"), ("湖南大学", "985", "综合"), ("国防科技大学", "985", "理工"),
        ("湖南师范大学", "211", "师范"), ("湘潭大学", "双一流", "综合"),
    ],
    "广东": [
        ("中山大学", "985", "综合"), ("华南理工大学", "985", "理工"), ("暨南大学", "211", "综合"),
        ("华南师范大学", "211", "师范"), ("华南农业大学", "双一流", "农林"), ("南方医科大学", "普通", "医药"),
        ("广东工业大学", "普通", "理工"), ("深圳大学", "普通", "综合"), ("广州大学", "普通", "综合"),
        ("广东外语外贸大学", "普通", "语言"), ("南方科技大学", "双一流", "理工"),
        ("广州医科大学", "双一流", "医药"),
    ],
    "广西": [
        ("广西大学", "211", "综合"), ("广西师范大学", "普通", "师范"), ("广西医科大学", "普通", "医药"),
    ],
    "海南": [
        ("海南大学", "211", "综合"), ("海南师范大学", "普通", "师范"),
    ],
    "重庆": [
        ("重庆大学", "985", "综合"), ("西南大学", "211", "综合"), ("西南政法大学", "普通", "政法"),
        ("重庆医科大学", "普通", "医药"), ("重庆邮电大学", "普通", "理工"),
    ],
    "四川": [
        ("四川大学", "985", "综合"), ("电子科技大学", "985", "理工"), ("西南交通大学", "211", "理工"),
        ("西南财经大学", "211", "财经"), ("四川农业大学", "211", "农林"), ("成都理工大学", "双一流", "理工"),
    ],
    "贵州": [
        ("贵州大学", "211", "综合"), ("贵州师范大学", "普通", "师范"), ("贵州医科大学", "普通", "医药"),
    ],
    "云南": [
        ("云南大学", "211", "综合"), ("昆明理工大学", "普通", "理工"), ("云南师范大学", "普通", "师范"),
    ],
    "西藏": [
        ("西藏大学", "211", "综合"),
    ],
    "陕西": [
        ("西安交通大学", "985", "理工"), ("西北工业大学", "985", "理工"), ("西安电子科技大学", "211", "理工"),
        ("陕西师范大学", "211", "师范"), ("西北大学", "211", "综合"), ("长安大学", "211", "理工"),
        ("西北农林科技大学", "985", "农林"),
    ],
    "甘肃": [
        ("兰州大学", "985", "综合"), ("西北师范大学", "普通", "师范"), ("兰州理工大学", "普通", "理工"),
    ],
    "青海": [
        ("青海大学", "211", "综合"), ("青海师范大学", "普通", "师范"),
    ],
    "宁夏": [
        ("宁夏大学", "211", "综合"),
    ],
    "新疆": [
        ("新疆大学", "211", "综合"), ("石河子大学", "211", "综合"),
    ],
}

MAJORS = [
    ("计算机科学与技术", "工学", "080901"), ("软件工程", "工学", "080902"),
    ("人工智能", "工学", "080717"), ("数据科学与大数据技术", "工学", "080910"),
    ("电子信息工程", "工学", "080701"), ("通信工程", "工学", "080703"),
    ("自动化", "工学", "080801"), ("电气工程及其自动化", "工学", "080601"),
    ("机械工程", "工学", "080201"), ("土木工程", "工学", "081001"),
    ("临床医学", "医学", "100201"), ("口腔医学", "医学", "100301"),
    ("药学", "医学", "100701"), ("护理学", "医学", "101101"),
    ("经济学", "经济学", "020101"), ("金融学", "经济学", "020301"),
    ("国际经济与贸易", "经济学", "020401"), ("会计学", "管理学", "120203"),
    ("工商管理", "管理学", "120201"), ("市场营销", "管理学", "120202"),
    ("法学", "法学", "030101"), ("知识产权", "法学", "030102"),
    ("汉语言文学", "文学", "050101"), ("英语", "文学", "050201"),
    ("新闻学", "文学", "050301"), ("广告学", "文学", "050303"),
    ("数学与应用数学", "理学", "070101"), ("物理学", "理学", "070201"),
    ("化学", "理学", "070301"), ("生物科学", "理学", "071001"),
    ("统计学", "理学", "071201"), ("心理学", "理学", "071101"),
    ("哲学", "哲学", "010101"), ("历史学", "历史学", "060101"),
    ("教育学", "教育学", "040101"), ("学前教育", "教育学", "040106"),
    ("建筑学", "工学", "082801"), ("城乡规划", "工学", "082802"),
    ("环境工程", "工学", "082502"), ("材料科学与工程", "工学", "080401"),
    ("能源与动力工程", "工学", "080501"), ("交通工程", "工学", "081802"),
    ("食品科学与工程", "工学", "082701"), ("生物医学工程", "工学", "082601"),
    ("信息管理与信息系统", "管理学", "120102"), ("工程管理", "管理学", "120103"),
    ("物流管理", "管理学", "120601"), ("旅游管理", "管理学", "120901"),
    ("农学", "农学", "090101"), ("园艺", "农学", "090102"),
]

BATCHES = ["本科批", "本科一批", "本科二批"]
SUBJECT_GROUPS = ["物理", "历史", "不限"]


def generate_scores(univ_name: str, univ_level: str, major_category: str, province_name: str) -> dict:
    """Generate realistic admission scores using REAL rank-based approach.

    University difficulty is fundamentally about RANKS (percentile within exam cohort),
    not raw scores which vary across provinces. We define target rank ranges per
    university, then convert to province-specific scores using the official lookup.
    """
    # Target RANK ranges (not scores!) for each university tier.
    # Ranks are stable across provinces since they represent percentile.
    # Values represent the typical admission rank for the "home" province.
    univ_rank_range: dict[str, tuple[int, int, int]] = {
        # Top 2 — targeted by the absolute top students
        "清华大学": (20, 180, 60), "北京大学": (20, 180, 60),
        # C9 / Top 10
        "复旦大学": (60, 350, 150), "上海交通大学": (60, 350, 150),
        "浙江大学": (80, 400, 200), "中国科学技术大学": (100, 450, 220),
        "南京大学": (120, 500, 250), "中国人民大学": (150, 600, 300),
        # Strong 985
        "武汉大学": (300, 1200, 600), "华中科技大学": (350, 1300, 650),
        "北京航空航天大学": (250, 1000, 500), "北京理工大学": (350, 1400, 700),
        "同济大学": (300, 1200, 600), "南开大学": (350, 1500, 750),
        "中山大学": (400, 1800, 900), "厦门大学": (500, 2200, 1100),
        "东南大学": (500, 2200, 1100), "天津大学": (600, 2500, 1300),
        "哈尔滨工业大学": (500, 2000, 1000), "西安交通大学": (600, 2500, 1300),
        "国防科技大学": (400, 1500, 800),
        # Upper-mid 985
        "北京师范大学": (800, 3500, 1800), "华东师范大学": (900, 4000, 2000),
        "电子科技大学": (700, 3000, 1500), "四川大学": (1000, 4500, 2200),
        "华南理工大学": (1200, 5000, 2500), "中南大学": (1200, 5000, 2500),
        "大连理工大学": (1500, 6000, 3000), "湖南大学": (1500, 6000, 3000),
        "重庆大学": (1800, 7000, 3500), "山东大学": (1800, 7000, 3500),
        "吉林大学": (2000, 8000, 4000), "东北大学": (2500, 9000, 4500),
        "西北工业大学": (1500, 6000, 3000),
        # Lower 985
        "中国农业大学": (3000, 10000, 5500), "中国海洋大学": (3500, 12000, 6500),
        "兰州大学": (4000, 15000, 8000), "中央民族大学": (4000, 16000, 9000),
        "西北农林科技大学": (5000, 18000, 10000),
        # Top 211 (nearly 985 level)
        "上海财经大学": (1200, 5000, 2500), "中央财经大学": (1500, 6000, 3000),
        "对外经济贸易大学": (1800, 7000, 3500), "中国政法大学": (2500, 9000, 5000),
        "北京邮电大学": (2000, 8000, 4000), "西安电子科技大学": (3000, 10000, 5500),
        # Mid 211
        "北京交通大学": (4000, 15000, 8000), "北京科技大学": (4500, 17000, 9000),
        "南京航空航天大学": (3500, 14000, 7000), "南京理工大学": (4000, 15000, 8000),
        "武汉理工大学": (5000, 18000, 10000), "西南交通大学": (5500, 20000, 11000),
        "北京工业大学": (6000, 22000, 12000), "华东理工大学": (4000, 15000, 8000),
        "东华大学": (7000, 25000, 13000), "上海大学": (6000, 22000, 12000),
        "苏州大学": (6000, 22000, 12000), "河海大学": (5500, 20000, 10000),
        "暨南大学": (6000, 22000, 12000), "西南财经大学": (5000, 18000, 10000),
        "中南财经政法大学": (6000, 22000, 12000), "中国地质大学(武汉)": (7000, 25000, 14000),
        "华中师范大学": (8000, 28000, 15000), "南京师范大学": (8000, 28000, 15000),
        "北京外国语大学": (6000, 22000, 12000), "中国传媒大学": (8000, 28000, 15000),
        "华北电力大学(保定)": (9000, 30000, 16000), "合肥工业大学": (9000, 30000, 16000),
        # Lower 211
        "北京化工大学": (10000, 35000, 18000), "北京林业大学": (12000, 38000, 20000),
        "北京中医药大学": (12000, 38000, 20000), "中国药科大学": (10000, 35000, 18000),
        "江南大学": (12000, 40000, 22000), "南京农业大学": (13000, 42000, 24000),
        "华中农业大学": (14000, 45000, 25000), "华南师范大学": (12000, 40000, 22000),
        "陕西师范大学": (15000, 50000, 28000), "东北师范大学": (15000, 50000, 28000),
        "湖南师范大学": (16000, 52000, 30000), "安徽大学": (18000, 55000, 32000),
        "南昌大学": (18000, 55000, 32000), "郑州大学": (15000, 50000, 28000),
        "福州大学": (18000, 55000, 32000), "大连海事大学": (20000, 60000, 35000),
        "辽宁大学": (22000, 65000, 38000), "内蒙古大学": (25000, 70000, 40000),
        "新疆大学": (30000, 80000, 45000), "石河子大学": (35000, 90000, 50000),
        "西藏大学": (40000, 100000, 60000), "青海大学": (35000, 90000, 50000),
        "宁夏大学": (30000, 80000, 45000), "广西大学": (22000, 65000, 38000),
        "海南大学": (28000, 75000, 42000), "贵州大学": (25000, 70000, 40000),
        "云南大学": (25000, 70000, 40000), "延边大学": (28000, 75000, 42000),
        "太原理工大学": (22000, 65000, 38000), "河北工业大学": (20000, 60000, 35000),
        "哈尔滨工程大学": (12000, 40000, 22000), "南京邮电大学": (13000, 42000, 23000),
    }

    if univ_name in univ_rank_range:
        lo_rank, hi_rank, mode_rank = univ_rank_range[univ_name]
        target_rank = random.triangular(lo_rank, hi_rank, mode_rank)
    else:
        # Generic fallback by university level
        generic_rank = {
            "985": random.triangular(3000, 15000, 7000),
            "211": random.triangular(10000, 50000, 25000),
            "双一流": random.triangular(20000, 80000, 45000),
            "普通": random.triangular(30000, 140000, 70000),
        }
        target_rank = generic_rank.get(univ_level, 50000)

    # Hot majors: lower rank (harder to get in)
    hot_majors = {"工学", "医学", "经济学"}
    if major_category in hot_majors:
        target_rank *= random.uniform(0.65, 0.90)
    # Cold majors: higher rank (easier)
    cold_majors = {"农学", "哲学", "历史学"}
    if major_category in cold_majors:
        target_rank *= random.uniform(1.10, 1.35)

    # Add random variation
    target_rank *= random.uniform(0.80, 1.25)
    target_rank = max(1, int(target_rank))

    # Convert rank to province-specific score using REAL lookup table
    score = rank_lookup.rank_to_score(province_name, 2024, "物理", target_rank)
    if score is None:
        # Fallback: use formula (shouldn't happen with our complete dataset)
        score = round(750 - (target_rank * 5.5) ** 0.5, 1)
        score = min(720, max(380, score))

    score = round(score + random.uniform(-5, 5), 1)
    score = min(720, max(380, score))

    return {
        "min_score": score - random.uniform(0, 8),
        "min_rank": int(target_rank * (1 + random.uniform(0.05, 0.20))),
        "avg_score": score,
        "avg_rank": target_rank,
        "max_score": score + random.uniform(0, 5),
        "enrollment_count": random.randint(1, 15),
    }


def seed():
    init_db()
    db = SessionLocal()

    if db.query(Province).count() > 0:
        print("Database already seeded. Skipping.")
        db.close()
        return

    print("Seeding provinces...")
    province_map = {}
    for name, mode in PROVINCES:
        p = Province(name=name, gaokao_mode=mode)
        db.add(p)
        db.flush()
        province_map[name] = p.id

    print("Seeding universities...")
    univ_map = {}
    for prov_name, univ_list in UNIVERSITIES_BY_PROVINCE.items():
        pid = province_map[prov_name]
        for univ_name, level, utype in univ_list:
            u = University(name=univ_name, province_id=pid, level=level, utype=utype)
            db.add(u)
            db.flush()
            univ_map[univ_name] = u.id

    # Add extra universities for provinces with few entries (fill up to 15)
    extra_univs = []
    for prov_name in PROVINCES:
        pname = prov_name[0]
        existing = len(UNIVERSITIES_BY_PROVINCE.get(pname, []))
        for i in range(existing, 15):
            base_names = ["科技", "理工", "师范", "工程", "学院", "工商"]
            extra_name = f"{pname}{random.choice(base_names)}大学_{i}"
            level = random.choice(["普通", "普通", "普通", "双一流"])
            utype = random.choice(UNIVERSITY_TYPES)
            extra_univs.append((extra_name, pname, level, utype))

    for univ_name, pname, level, utype in extra_univs:
        pid = province_map[pname]
        u = University(name=univ_name, province_id=pid, level=level, utype=utype)
        db.add(u)
        db.flush()
        univ_map[univ_name] = u.id

    print("Seeding majors...")
    major_map = {}
    for mname, cat, code in MAJORS:
        m = Major(name=mname, category=cat, code=code)
        db.add(m)
        db.flush()
        major_map[mname] = m.id

    print("Seeding admission scores (this may take a moment)...")
    score_count = 0
    target_provinces = [p[0] for p in PROVINCES]
    years = [2023, 2024, 2025]

    # Build lookup: univ_name -> (uid, level, utype, home_province)
    all_univ_info = {}
    for prov_name, ulist in UNIVERSITIES_BY_PROVINCE.items():
        for u_name, u_level, u_type in ulist:
            all_univ_info[u_name] = (univ_map.get(u_name), u_level, u_type, prov_name)
    for u_name, u_prov, u_level, u_type in extra_univs:
        all_univ_info[u_name] = (univ_map.get(u_name), u_level, u_type, u_prov)

    # National universities (985/211) recruit across all provinces
    national = {n: info for n, info in all_univ_info.items() if info[1] in ("985", "211")}
    # Local universities (双一流/普通) primarily stay in home province
    local = {n: info for n, info in all_univ_info.items() if info[1] not in ("985", "211")}

    prov_diff = {
        "河南": 1.03, "山东": 1.02, "河北": 1.02, "江苏": 1.02,
        "广东": 1.01, "安徽": 1.01, "湖南": 1.01, "湖北": 1.01,
        "四川": 1.00, "浙江": 1.00, "江西": 1.00, "山西": 1.00,
        "重庆": 0.99, "陕西": 0.99, "广西": 0.98, "福建": 0.98,
        "贵州": 0.97, "云南": 0.97, "甘肃": 0.97, "辽宁": 0.98,
        "内蒙古": 0.96, "吉林": 0.96, "黑龙江": 0.97, "海南": 0.95,
        "天津": 0.94, "北京": 0.92, "上海": 0.91, "西藏": 0.93,
        "青海": 0.94, "宁夏": 0.95, "新疆": 0.95,
    }

    for prov_name in target_provinces:
        pid = province_map[prov_name]
        province_factor = prov_diff.get(prov_name, 1.0)

        # All 985/211 universities have scores in every province
        prov_univs = dict(national)
        # Add local universities from this province
        for n, info in local.items():
            if info[3] == prov_name:
                prov_univs[n] = info
            elif random.random() < 0.15:  # 15% cross-province
                prov_univs[n] = info

        # Cap per province
        univ_items = list(prov_univs.items())
        if len(univ_items) > 150:
            elite = [(n, i) for n, i in univ_items if i[1] in ("985", "211")]
            rest = [(n, i) for n, i in univ_items if i[1] not in ("985", "211")]
            if len(rest) > 150 - len(elite):
                rest = random.sample(rest, max(0, 150 - len(elite)))
            univ_items = elite + rest

        for univ_name, (uid, level, utype, home_prov) in univ_items:
            if not uid:
                continue
            sample_majors = random.sample(MAJORS, min(6, len(MAJORS)))
            for mname, mcat, _mcode in sample_majors:
                mid = major_map[mname]
                for year in years:
                    sd = generate_scores(univ_name, level, mcat, prov_name)

                    # The generate_scores function already uses province-specific
                    # score-rank mapping via the lookup table. For cross-province,
                    # rank (difficulty tier) stays the same, but score differs
                    # because the same rank means different scores in different provinces.

                    # Cross-province rank adjustment: slightly harder for non-home provinces
                    rank = sd["avg_rank"]
                    if home_prov != prov_name:
                        rank = int(rank * random.uniform(0.95, 1.10))

                    # Recompute score from adjusted rank for this province+year
                    score = rank_lookup.rank_to_score(prov_name, year, "物理", rank)
                    if score is None:
                        score = sd["avg_score"]
                    score = round(score + random.uniform(-3, 5), 1)
                    score = min(720, max(380, score))

                    # Year-to-year variation
                    year_offset = random.uniform(-2, 3)
                    score = round(score + year_offset, 1)
                    score = min(720, max(380, score))
                    # Recompute rank for final adjusted score
                    final_rank = rank_lookup.score_to_rank(prov_name, year, "物理", score)
                    if final_rank > 0:
                        rank = int(final_rank * random.uniform(0.90, 1.10))
                    rank = max(1, rank)

                    trad = {"山西", "内蒙古", "吉林", "黑龙江", "江西", "河南", "四川", "贵州", "云南", "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆"}
                    batch = "本科一批" if prov_name in trad else "本科批"
                    sg = "物理" if mcat in ("工学", "理学") else random.choice(SUBJECT_GROUPS)

                    s = AdmissionScore(
                        university_id=uid,
                        major_id=mid,
                        province_id=pid,
                        year=year,
                        batch=batch,
                        subject_group=sg,
                        min_score=round(score - random.uniform(1, 10), 1),
                        min_rank=int(rank * (1 + random.uniform(0.05, 0.20))),
                        avg_score=round(score, 1),
                        avg_rank=rank,
                        max_score=round(score + random.uniform(0, 6), 1),
                        enrollment_count=sd["enrollment_count"],
                    )
                    db.add(s)
                    score_count += 1

    db.commit()
    db.close()
    print(f"Seed complete: {len(PROVINCES)} provinces, {len(univ_map)} universities, "
          f"{len(major_map)} majors, {score_count} admission score records.")


if __name__ == "__main__":
    seed()
