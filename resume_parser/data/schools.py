from typing import Dict, List, Set, Tuple
from functools import lru_cache
import json
import os


def _load_985_schools() -> List[Dict]:
    return [
        {"name": "北京大学", "aliases": ["北大", "PKU"], "tags": ["985", "211", "双一流"]},
        {"name": "清华大学", "aliases": ["清华", "THU", "Tsinghua"], "tags": ["985", "211", "双一流"]},
        {"name": "中国人民大学", "aliases": ["人大", "RUC"], "tags": ["985", "211", "双一流"]},
        {"name": "北京航空航天大学", "aliases": ["北航", "北航大学", "BUAA"], "tags": ["985", "211", "双一流"]},
        {"name": "北京理工大学", "aliases": ["北理工", "BIT"], "tags": ["985", "211", "双一流"]},
        {"name": "中国农业大学", "aliases": ["中农大", "CAU"], "tags": ["985", "211", "双一流"]},
        {"name": "北京师范大学", "aliases": ["北师", "北师大", "BNU"], "tags": ["985", "211", "双一流"]},
        {"name": "中央民族大学", "aliases": ["民大", "MUC"], "tags": ["985", "211", "双一流"]},
        {"name": "南开大学", "aliases": ["南开", "NKU"], "tags": ["985", "211", "双一流"]},
        {"name": "天津大学", "aliases": ["天大", "TJU"], "tags": ["985", "211", "双一流"]},
        {"name": "大连理工大学", "aliases": ["大工", "DUT"], "tags": ["985", "211", "双一流"]},
        {"name": "东北大学", "aliases": ["东大", "NEU"], "tags": ["985", "211", "双一流"]},
        {"name": "吉林大学", "aliases": ["吉大", "JLU"], "tags": ["985", "211", "双一流"]},
        {"name": "哈尔滨工业大学", "aliases": ["哈工大", "HIT"], "tags": ["985", "211", "双一流"]},
        {"name": "复旦大学", "aliases": ["复旦", "Fudan", "FDU"], "tags": ["985", "211", "双一流"]},
        {"name": "同济大学", "aliases": ["同济", "Tongji"], "tags": ["985", "211", "双一流"]},
        {"name": "上海交通大学", "aliases": ["上海交大", "上交", "SJTU"], "tags": ["985", "211", "双一流"]},
        {"name": "华东师范大学", "aliases": ["华师大", "华东师大", "ECNU"], "tags": ["985", "211", "双一流"]},
        {"name": "南京大学", "aliases": ["南大", "NJU"], "tags": ["985", "211", "双一流"]},
        {"name": "东南大学", "aliases": ["东大", "SEU"], "tags": ["985", "211", "双一流"]},
        {"name": "浙江大学", "aliases": ["浙大", "ZJU", "Zhejiang"], "tags": ["985", "211", "双一流"]},
        {"name": "中国科学技术大学", "aliases": ["中科大", "USTC", "科大"], "tags": ["985", "211", "双一流"]},
        {"name": "厦门大学", "aliases": ["厦大", "XMU"], "tags": ["985", "211", "双一流"]},
        {"name": "山东大学", "aliases": ["山大", "SDU"], "tags": ["985", "211", "双一流"]},
        {"name": "中国海洋大学", "aliases": ["海大", "中海洋", "OUC"], "tags": ["985", "211", "双一流"]},
        {"name": "武汉大学", "aliases": ["武大", "WHU"], "tags": ["985", "211", "双一流"]},
        {"name": "华中科技大学", "aliases": ["华科", "华科大", "HUST"], "tags": ["985", "211", "双一流"]},
        {"name": "湖南大学", "aliases": ["湖大", "HNU"], "tags": ["985", "211", "双一流"]},
        {"name": "中南大学", "aliases": ["中南", "CSU"], "tags": ["985", "211", "双一流"]},
        {"name": "国防科技大学", "aliases": ["国防科大", "NUDT"], "tags": ["985", "211", "双一流"]},
        {"name": "中山大学", "aliases": ["中大", "SYSU"], "tags": ["985", "211", "双一流"]},
        {"name": "华南理工大学", "aliases": ["华工", "华南理工", "SCUT"], "tags": ["985", "211", "双一流"]},
        {"name": "四川大学", "aliases": ["川大", "SCU"], "tags": ["985", "211", "双一流"]},
        {"name": "重庆大学", "aliases": ["重大", "CQU"], "tags": ["985", "211", "双一流"]},
        {"name": "电子科技大学", "aliases": ["成电", "电子科大", "UESTC"], "tags": ["985", "211", "双一流"]},
        {"name": "西安交通大学", "aliases": ["西交", "西安交大", "XJTU"], "tags": ["985", "211", "双一流"]},
        {"name": "西北工业大学", "aliases": ["西工大", "NWPU"], "tags": ["985", "211", "双一流"]},
        {"name": "西北农林科技大学", "aliases": ["西农", "NWAFU"], "tags": ["985", "211", "双一流"]},
        {"name": "兰州大学", "aliases": ["兰大", "LZU"], "tags": ["985", "211", "双一流"]},
    ]


def _load_211_schools() -> List[Dict]:
    non_985_211 = [
        {"name": "北京交通大学", "aliases": ["北交", "北交大"], "tags": ["211", "双一流"]},
        {"name": "北京工业大学", "aliases": ["北工大"], "tags": ["211", "双一流"]},
        {"name": "北京科技大学", "aliases": ["北科", "北科大"], "tags": ["211", "双一流"]},
        {"name": "北京化工大学", "aliases": ["北化", "北化工"], "tags": ["211", "双一流"]},
        {"name": "北京邮电大学", "aliases": ["北邮", "北邮大"], "tags": ["211", "双一流"]},
        {"name": "北京林业大学", "aliases": ["北林", "北林大"], "tags": ["211", "双一流"]},
        {"name": "北京外国语大学", "aliases": ["北外", "BFSU"], "tags": ["211", "双一流"]},
        {"name": "中国传媒大学", "aliases": ["中传", "CUC"], "tags": ["211", "双一流"]},
        {"name": "中央财经大学", "aliases": ["央财", "中财"], "tags": ["211", "双一流"]},
        {"name": "对外经济贸易大学", "aliases": ["贸大", "外经贸", "UIBE"], "tags": ["211", "双一流"]},
        {"name": "北京体育大学", "aliases": ["北体", "北体大"], "tags": ["211", "双一流"]},
        {"name": "中央音乐学院", "aliases": ["央音"], "tags": ["211", "双一流"]},
        {"name": "中国政法大学", "aliases": ["法大", "政法大", "CUPL"], "tags": ["211", "双一流"]},
        {"name": "华北电力大学", "aliases": ["华电", "华电大"], "tags": ["211", "双一流"]},
        {"name": "中国矿业大学（北京）", "aliases": ["矿大北京"], "tags": ["211", "双一流"]},
        {"name": "中国石油大学（北京）", "aliases": ["石大北京", "中石大北京"], "tags": ["211", "双一流"]},
        {"name": "中国地质大学（北京）", "aliases": ["地大北京"], "tags": ["211", "双一流"]},
        {"name": "天津医科大学", "aliases": ["天医", "天医大"], "tags": ["211", "双一流"]},
        {"name": "河北工业大学", "aliases": ["河工大"], "tags": ["211", "双一流"]},
        {"name": "太原理工大学", "aliases": ["太原理工", "太工大"], "tags": ["211", "双一流"]},
        {"name": "内蒙古大学", "aliases": ["内大"], "tags": ["211", "双一流"]},
        {"name": "辽宁大学", "aliases": ["辽大"], "tags": ["211", "双一流"]},
        {"name": "大连海事大学", "aliases": ["海大", "大连海大"], "tags": ["211", "双一流"]},
        {"name": "东北师范大学", "aliases": ["东师", "东北师大"], "tags": ["211", "双一流"]},
        {"name": "哈尔滨工程大学", "aliases": ["哈工程", "HEU"], "tags": ["211", "双一流"]},
        {"name": "东北农业大学", "aliases": ["东农", "东北农大"], "tags": ["211", "双一流"]},
        {"name": "东北林业大学", "aliases": ["东林", "东北林大"], "tags": ["211", "双一流"]},
        {"name": "华东理工大学", "aliases": ["华理", "华东理工"], "tags": ["211", "双一流"]},
        {"name": "东华大学", "aliases": ["东华"], "tags": ["211", "双一流"]},
        {"name": "上海财经大学", "aliases": ["上财", "上海财大", "SUFE"], "tags": ["211", "双一流"]},
        {"name": "上海大学", "aliases": ["上大"], "tags": ["211", "双一流"]},
        {"name": "第二军医大学", "aliases": ["二军大"], "tags": ["211"]},
        {"name": "苏州大学", "aliases": ["苏大"], "tags": ["211", "双一流"]},
        {"name": "南京航空航天大学", "aliases": ["南航", "南京航空航天"], "tags": ["211", "双一流"]},
        {"name": "南京理工大学", "aliases": ["南理工"], "tags": ["211", "双一流"]},
        {"name": "中国矿业大学", "aliases": ["矿大", "中国矿大"], "tags": ["211", "双一流"]},
        {"name": "河海大学", "aliases": ["河海"], "tags": ["211", "双一流"]},
        {"name": "江南大学", "aliases": ["江南大"], "tags": ["211", "双一流"]},
        {"name": "南京农业大学", "aliases": ["南农", "南京农大"], "tags": ["211", "双一流"]},
        {"name": "中国药科大学", "aliases": ["药大", "中国药大"], "tags": ["211", "双一流"]},
        {"name": "南京师范大学", "aliases": ["南师", "南师大"], "tags": ["211", "双一流"]},
        {"name": "浙江大学", "aliases": ["浙大"], "tags": ["985", "211", "双一流"]},
        {"name": "安徽大学", "aliases": ["安大"], "tags": ["211", "双一流"]},
        {"name": "合肥工业大学", "aliases": ["合工大"], "tags": ["211", "双一流"]},
        {"name": "福州大学", "aliases": ["福大"], "tags": ["211", "双一流"]},
        {"name": "南昌大学", "aliases": ["昌大"], "tags": ["211", "双一流"]},
        {"name": "中国石油大学（华东）", "aliases": ["石大华东", "中石大华东"], "tags": ["211", "双一流"]},
        {"name": "郑州大学", "aliases": ["郑大"], "tags": ["211", "双一流"]},
        {"name": "中国地质大学（武汉）", "aliases": ["地大武汉"], "tags": ["211", "双一流"]},
        {"name": "武汉理工大学", "aliases": ["武理", "武汉理工"], "tags": ["211", "双一流"]},
        {"name": "华中农业大学", "aliases": ["华农", "华中农大"], "tags": ["211", "双一流"]},
        {"name": "华中师范大学", "aliases": ["华师", "华中师大"], "tags": ["211", "双一流"]},
        {"name": "中南财经政法大学", "aliases": ["中南财大", "中南财经"], "tags": ["211", "双一流"]},
        {"name": "湖南师范大学", "aliases": ["湖师", "湖南师大"], "tags": ["211", "双一流"]},
        {"name": "暨南大学", "aliases": ["暨大"], "tags": ["211", "双一流"]},
        {"name": "华南师范大学", "aliases": ["华师", "华南师大"], "tags": ["211", "双一流"]},
        {"name": "广西大学", "aliases": ["西大"], "tags": ["211", "双一流"]},
        {"name": "海南大学", "aliases": ["海大"], "tags": ["211", "双一流"]},
        {"name": "西南大学", "aliases": ["西大", "西南大"], "tags": ["211", "双一流"]},
        {"name": "西南交通大学", "aliases": ["西南交大", "西交"], "tags": ["211", "双一流"]},
        {"name": "四川农业大学", "aliases": ["川农", "四川农大"], "tags": ["211", "双一流"]},
        {"name": "西南财经大学", "aliases": ["西财", "西南财大"], "tags": ["211", "双一流"]},
        {"name": "贵州大学", "aliases": ["贵大"], "tags": ["211", "双一流"]},
        {"name": "云南大学", "aliases": ["云大"], "tags": ["211", "双一流"]},
        {"name": "西藏大学", "aliases": ["藏大"], "tags": ["211", "双一流"]},
        {"name": "西北大学", "aliases": ["西大", "西北大"], "tags": ["211", "双一流"]},
        {"name": "西安电子科技大学", "aliases": ["西电", "西电大", "Xidian"], "tags": ["211", "双一流"]},
        {"name": "长安大学", "aliases": ["长大"], "tags": ["211", "双一流"]},
        {"name": "陕西师范大学", "aliases": ["陕师", "陕西师大"], "tags": ["211", "双一流"]},
        {"name": "青海大学", "aliases": ["青大"], "tags": ["211", "双一流"]},
        {"name": "宁夏大学", "aliases": ["宁大"], "tags": ["211", "双一流"]},
        {"name": "新疆大学", "aliases": ["新大"], "tags": ["211", "双一流"]},
        {"name": "石河子大学", "aliases": ["石大", "石河子"], "tags": ["211", "双一流"]},
    ]
    return non_985_211


def _load_double_first_class_schools() -> List[str]:
    return [
        "北京大学", "清华大学", "中国人民大学", "北京航空航天大学", "北京理工大学",
        "中国农业大学", "北京师范大学", "中央民族大学", "南开大学", "天津大学",
        "大连理工大学", "东北大学", "吉林大学", "哈尔滨工业大学", "复旦大学",
        "同济大学", "上海交通大学", "华东师范大学", "南京大学", "东南大学",
        "浙江大学", "中国科学技术大学", "厦门大学", "山东大学", "中国海洋大学",
        "武汉大学", "华中科技大学", "湖南大学", "中南大学", "国防科技大学",
        "中山大学", "华南理工大学", "四川大学", "重庆大学", "电子科技大学",
        "西安交通大学", "西北工业大学", "西北农林科技大学", "兰州大学",
        "北京交通大学", "北京工业大学", "北京科技大学", "北京化工大学", "北京邮电大学",
        "北京林业大学", "北京协和医学院", "北京中医药大学", "北京外国语大学",
        "中国传媒大学", "中央财经大学", "对外经济贸易大学", "外交学院",
        "中国人民公安大学", "北京体育大学", "中央音乐学院", "中国音乐学院",
        "中央美术学院", "中央戏剧学院", "中国政法大学", "天津工业大学",
        "天津医科大学", "天津中医药大学", "华北电力大学", "河北工业大学",
        "山西大学", "太原理工大学", "内蒙古大学", "辽宁大学", "大连海事大学",
        "吉林大学", "东北师范大学", "哈尔滨工程大学", "东北农业大学",
        "东北林业大学", "华东理工大学", "东华大学", "上海海洋大学",
        "上海中医药大学", "上海外国语大学", "上海财经大学", "上海体育学院",
        "上海音乐学院", "上海大学", "第二军医大学", "苏州大学",
        "南京航空航天大学", "南京理工大学", "中国矿业大学", "南京邮电大学",
        "河海大学", "江南大学", "南京林业大学", "南京信息工程大学",
        "南京农业大学", "南京中医药大学", "中国药科大学", "南京师范大学",
        "浙江大学", "安徽大学", "中国科学技术大学", "合肥工业大学",
        "福州大学", "南昌大学", "山东大学", "中国海洋大学", "中国石油大学（华东）",
        "郑州大学", "河南大学", "武汉大学", "华中科技大学", "中国地质大学（武汉）",
        "武汉理工大学", "华中农业大学", "华中师范大学", "中南财经政法大学",
        "湖南大学", "中南大学", "湖南师范大学", "中山大学", "暨南大学",
        "华南理工大学", "华南农业大学", "广州医科大学", "广州中医药大学",
        "华南师范大学", "海南大学", "广西大学", "四川大学", "重庆大学",
        "西南交通大学", "西南石油大学", "成都理工大学", "四川农业大学",
        "成都中医药大学", "西南大学", "西南财经大学", "贵州大学", "云南大学",
        "西藏大学", "西北大学", "西安交通大学", "西北工业大学", "西北农林科技大学",
        "西安电子科技大学", "长安大学", "陕西师范大学", "兰州大学",
        "青海大学", "宁夏大学", "新疆大学", "石河子大学",
        "宁波大学", "中国科学院大学", "中国地质大学（北京）", "中国矿业大学（北京）",
        "中国石油大学（北京）", "北京师范大学-",
    ]


def _load_qs_top_100() -> List[Dict]:
    return [
        {"name": "Massachusetts Institute of Technology", "rank": 1, "aliases": ["MIT", "麻省理工学院", "麻省理工"]},
        {"name": "University of Cambridge", "rank": 2, "aliases": ["Cambridge", "剑桥大学", "剑桥"]},
        {"name": "Stanford University", "rank": 3, "aliases": ["Stanford", "斯坦福大学", "斯坦福"]},
        {"name": "University of Oxford", "rank": 4, "aliases": ["Oxford", "牛津大学", "牛津"]},
        {"name": "Harvard University", "rank": 5, "aliases": ["Harvard", "哈佛大学", "哈佛"]},
        {"name": "Imperial College London", "rank": 6, "aliases": ["Imperial", "帝国理工学院", "帝国理工"]},
        {"name": "ETH Zurich", "rank": 7, "aliases": ["ETH", "苏黎世联邦理工学院", "苏黎世联邦理工"]},
        {"name": "University of Chicago", "rank": 10, "aliases": ["Chicago", "芝加哥大学", "芝加哥"]},
        {"name": "University of Pennsylvania", "rank": 12, "aliases": ["UPenn", "宾夕法尼亚大学", "宾大"]},
        {"name": "Columbia University", "rank": 14, "aliases": ["Columbia", "哥伦比亚大学", "哥大"]},
        {"name": "Princeton University", "rank": 17, "aliases": ["Princeton", "普林斯顿大学", "普林斯顿"]},
        {"name": "Cornell University", "rank": 20, "aliases": ["Cornell", "康奈尔大学", "康奈尔"]},
        {"name": "University of California, Berkeley", "rank": 22, "aliases": ["UC Berkeley", "Berkeley", "加州大学伯克利分校", "伯克利"]},
        {"name": "Yale University", "rank": 23, "aliases": ["Yale", "耶鲁大学", "耶鲁"]},
        {"name": "University of Michigan, Ann Arbor", "rank": 25, "aliases": ["Michigan", "密歇根大学", "密西根大学"]},
        {"name": "University of Toronto", "rank": 27, "aliases": ["U of T", "多伦多大学", "多大"]},
        {"name": "Johns Hopkins University", "rank": 28, "aliases": ["JHU", "约翰霍普金斯大学", "霍普金斯"]},
        {"name": "University of California, Los Angeles", "rank": 29, "aliases": ["UCLA", "加州大学洛杉矶分校", "洛杉矶加大"]},
        {"name": "University of Edinburgh", "rank": 30, "aliases": ["Edinburgh", "爱丁堡大学", "爱丁堡"]},
        {"name": "National University of Singapore", "rank": 31, "aliases": ["NUS", "新加坡国立大学", "新国立"]},
        {"name": "University of Manchester", "rank": 32, "aliases": ["Manchester", "曼彻斯特大学", "曼大"]},
        {"name": "Carnegie Mellon University", "rank": 34, "aliases": ["CMU", "卡内基梅隆大学", "卡梅"]},
        {"name": "University of California, San Diego", "rank": 36, "aliases": ["UCSD", "加州大学圣地亚哥分校"]},
        {"name": "University of Texas at Austin", "rank": 37, "aliases": ["UT Austin", "德克萨斯大学奥斯汀分校", "德州奥斯汀"]},
        {"name": "University of Hong Kong", "rank": 38, "aliases": ["HKU", "香港大学", "港大"]},
        {"name": "University of Illinois at Urbana-Champaign", "rank": 40, "aliases": ["UIUC", "伊利诺伊大学厄巴纳-香槟分校"]},
        {"name": "University of Waterloo", "rank": 41, "aliases": ["Waterloo", "滑铁卢大学", "滑铁卢"]},
        {"name": "The University of Tokyo", "rank": 42, "aliases": ["Tokyo", "东京大学", "东大"]},
        {"name": "King's College London", "rank": 43, "aliases": ["KCL", "伦敦国王学院", "国王学院"]},
        {"name": "University of British Columbia", "rank": 44, "aliases": ["UBC", "不列颠哥伦比亚大学", "英属哥伦比亚大学"]},
        {"name": "University of Melbourne", "rank": 45, "aliases": ["Melbourne", "墨尔本大学", "墨大"]},
        {"name": "University of Sydney", "rank": 46, "aliases": ["Sydney", "悉尼大学", "悉大"]},
        {"name": "University of California, Santa Barbara", "rank": 47, "aliases": ["UCSB", "加州大学圣塔芭芭拉分校"]},
        {"name": "Nanyang Technological University", "rank": 48, "aliases": ["NTU", "南洋理工大学", "南大"]},
        {"name": "University of North Carolina at Chapel Hill", "rank": 49, "aliases": ["UNC", "北卡罗来纳大学教堂山分校"]},
        {"name": "University of Queensland", "rank": 50, "aliases": ["UQ", "昆士兰大学", "昆大"]},
        {"name": "University of New South Wales", "rank": 51, "aliases": ["UNSW", "新南威尔士大学", "新南"]},
        {"name": "Brown University", "rank": 55, "aliases": ["Brown", "布朗大学", "布朗"]},
        {"name": "University of Amsterdam", "rank": 56, "aliases": ["UvA", "阿姆斯特丹大学", "阿大"]},
        {"name": "University of California, Davis", "rank": 57, "aliases": ["UCD", "加州大学戴维斯分校"]},
        {"name": "National Taiwan University", "rank": 68, "aliases": ["NTU", "台湾大学", "台大"]},
        {"name": "University of Montreal", "rank": 70, "aliases": ["UdeM", "蒙特利尔大学"]},
        {"name": "University of Zurich", "rank": 71, "aliases": ["UZH", "苏黎世大学"]},
        {"name": "University of Science and Technology of China", "rank": 73, "aliases": ["USTC", "中国科学技术大学", "中科大"]},
        {"name": "Duke University", "rank": 74, "aliases": ["Duke", "杜克大学", "杜克"]},
        {"name": "KU Leuven", "rank": 76, "aliases": ["Leuven", "鲁汶大学", "荷语鲁汶"]},
        {"name": "University of Wisconsin-Madison", "rank": 77, "aliases": ["UW-Madison", "威斯康星大学麦迪逊分校", "威大"]},
        {"name": "University of California, Irvine", "rank": 78, "aliases": ["UCI", "加州大学欧文分校", "加州大学尔湾分校"]},
        {"name": "University of California, Santa Cruz", "rank": 79, "aliases": ["UCSC", "加州大学圣克鲁兹分校"]},
        {"name": "University of Hong Kong", "rank": 80, "aliases": ["HKU", "香港大学", "港大"]},
        {"name": "Tsinghua University", "rank": 82, "aliases": ["Tsinghua", "清华大学", "清华"]},
        {"name": "University of Copenhagen", "rank": 83, "aliases": ["KU", "哥本哈根大学"]},
        {"name": "Peking University", "rank": 84, "aliases": ["PKU", "北京大学", "北大"]},
        {"name": "University of Washington", "rank": 85, "aliases": ["UW", "华盛顿大学", "华大"]},
        {"name": "University of Birmingham", "rank": 86, "aliases": ["Birmingham", "伯明翰大学", "伯大"]},
        {"name": "University of St Andrews", "rank": 87, "aliases": ["St Andrews", "圣安德鲁斯大学"]},
        {"name": "University of Leeds", "rank": 88, "aliases": ["Leeds", "利兹大学"]},
        {"name": "University of Auckland", "rank": 89, "aliases": ["Auckland", "奥克兰大学"]},
        {"name": "City University of Hong Kong", "rank": 90, "aliases": ["CityU", "香港城市大学", "城大"]},
        {"name": "University of Glasgow", "rank": 91, "aliases": ["Glasgow", "格拉斯哥大学", "格大"]},
        {"name": "University of California, Santa Cruz", "rank": 92, "aliases": ["UCSC", "加州大学圣克鲁兹分校"]},
        {"name": "University of Notre Dame", "rank": 93, "aliases": ["Notre Dame", "圣母大学"]},
        {"name": "University of Alberta", "rank": 94, "aliases": ["UAlberta", "阿尔伯塔大学", "阿大"]},
        {"name": "University of Southampton", "rank": 95, "aliases": ["Southampton", "南安普顿大学", "南安"]},
        {"name": "University of California, Riverside", "rank": 96, "aliases": ["UCR", "加州大学河滨分校"]},
        {"name": "University of York", "rank": 97, "aliases": ["York", "约克大学"]},
        {"name": "University of Dundee", "rank": 98, "aliases": ["Dundee", "邓迪大学"]},
        {"name": "University of Oklahoma", "rank": 99, "aliases": ["OU", "俄克拉荷马大学"]},
        {"name": "University of Lancaster", "rank": 100, "aliases": ["Lancaster", "兰卡斯特大学", "兰卡"]},
    ]


@lru_cache(maxsize=1)
def get_school_library() -> Tuple[Dict[str, Dict], Dict[str, str], Set[str]]:
    """
    返回:
    - school_dict: 标准学校名 -> {tags, aliases, type}
    - alias_to_standard: 别名 -> 标准学校名
    - all_school_names: 所有标准学校名集合
    """
    school_dict: Dict[str, Dict] = {}
    alias_to_standard: Dict[str, str] = {}

    schools_985 = _load_985_schools()
    schools_211 = _load_211_schools()
    qs_100 = _load_qs_top_100()

    all_schools = []
    seen_names = set()

    for s in schools_985:
        if s["name"] not in seen_names:
            all_schools.append({**s, "type": "mainland", "qs_rank": None})
            seen_names.add(s["name"])

    for s in schools_211:
        if s["name"] not in seen_names:
            all_schools.append({**s, "type": "mainland", "qs_rank": None})
            seen_names.add(s["name"])

    for s in qs_100:
        merged = False
        for alias in s.get("aliases", []):
            if alias in seen_names:
                for school in all_schools:
                    if school["name"] == alias:
                        if "QS100" not in school["tags"]:
                            school["tags"].append("QS100")
                        school["qs_rank"] = s["rank"]
                        school.setdefault("aliases", []).extend(
                            [a for a in s["aliases"] if a != alias and a not in school["aliases"]]
                        )
                        merged = True
                        break
                break

        if not merged and s["name"] not in seen_names:
            all_schools.append({
                "name": s["name"],
                "aliases": s["aliases"],
                "tags": ["QS100"],
                "type": "overseas",
                "qs_rank": s["rank"]
            })
            seen_names.add(s["name"])

    for s in all_schools:
        school_dict[s["name"]] = {
            "tags": s.get("tags", []),
            "aliases": s.get("aliases", []),
            "type": s.get("type", "mainland"),
            "qs_rank": s.get("qs_rank"),
        }
        alias_to_standard[s["name"]] = s["name"]
        for alias in s.get("aliases", []):
            if alias.lower() not in alias_to_standard:
                alias_to_standard[alias.lower()] = s["name"]
            if alias not in alias_to_standard:
                alias_to_standard[alias] = s["name"]

    all_school_names = set(school_dict.keys())
    return school_dict, alias_to_standard, all_school_names
