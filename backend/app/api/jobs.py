from flask import Blueprint, request, jsonify
from app.models import JobsRaw, StatSkillFreq
from app.main import db
from datetime import date
import json
import logging

jobs_bp = Blueprint('jobs', __name__)
logger = logging.getLogger(__name__)

# 岗位名称 → 常见技能映射（全行业覆盖）
JOB_TITLE_SKILLS_MAP = {
    '大数据': ['Spark', 'Hadoop', 'Hive', 'SQL', 'Python', 'ETL', '数据仓库'],
    '数据开发': ['Spark', 'Hadoop', 'Hive', 'SQL', 'Python', 'ETL'],
    '数据分析': ['Python', 'SQL', 'Excel', 'Tableau', 'Pandas', 'NumPy', '数据可视化'],
    '数据挖掘': ['Python', 'SQL', '机器学习', 'Spark', 'TensorFlow', 'PyTorch'],
    '数据仓库': ['SQL', 'Hive', 'Spark', 'ETL', '数据仓库', 'Hadoop'],
    '数据工程师': ['Spark', 'Hadoop', 'SQL', 'Python', 'Hive', 'ETL'],
    'ETL': ['SQL', 'Python', 'ETL', 'Spark', 'Hive', '数据仓库'],
    'Python': ['Python', 'Flask', 'Django', 'Linux', 'MySQL', 'Git', 'SQL'],
    'Java': ['Java', 'Spring', 'MyBatis', 'MySQL', 'Redis', 'Linux', '微服务'],
    '前端': ['JavaScript', 'Vue', 'React', 'HTML', 'CSS', 'TypeScript', 'Node.js'],
    '后端': ['Java', 'Python', 'Spring', 'MySQL', 'Redis', '微服务', 'Linux'],
    '全栈': ['JavaScript', 'Python', 'Java', 'Vue', 'React', 'MySQL', 'Node.js'],
    '测试': ['Selenium', 'JMeter', '自动化测试', '功能测试', '性能测试', '测试用例'],
    '运维': ['Linux', 'Docker', 'K8s', 'Shell', 'Python', 'MySQL', '监控'],
    'DevOps': ['Docker', 'K8s', 'Linux', 'Jenkins', 'Git', 'Shell', 'CI/CD'],
    '算法': ['Python', 'C++', 'TensorFlow', 'PyTorch', '机器学习', '深度学习', 'NLP'],
    'AI': ['Python', 'TensorFlow', 'PyTorch', '机器学习', '深度学习', 'NLP'],
    '人工智能': ['Python', 'TensorFlow', 'PyTorch', '机器学习', '深度学习', 'NLP'],
    '机器学习': ['Python', 'TensorFlow', 'PyTorch', '机器学习', '深度学习', 'Sklearn'],
    '深度学习': ['Python', 'TensorFlow', 'PyTorch', '深度学习', '计算机视觉', 'NLP'],
    'NLP': ['Python', 'NLP', 'TensorFlow', 'PyTorch', 'BERT', 'Transformer'],
    '云计算': ['Linux', 'Docker', 'K8s', 'Python', '微服务', '分布式', 'Kafka'],
    'DBA': ['MySQL', 'Oracle', 'SQL', 'Redis', 'MongoDB', 'Linux', '数据备份'],
    '架构师': ['Java', '微服务', '分布式', 'Spring', 'Kafka', 'Redis', 'Docker'],
    '项目经理': ['敏捷开发', '项目管理', 'Scrum', 'JIRA', '团队管理'],
    '产品经理': ['Axure', 'Figma', '用户研究', '数据分析', 'PRD', '项目管理'],
    'UI': ['Figma', 'Sketch', 'Photoshop', 'HTML', 'CSS', 'UI设计'],
    '安全': ['网络安全', '渗透测试', 'Linux', 'Python', '安全分析', '防火墙'],
    '嵌入式': ['C', 'C++', 'Linux', 'ARM', 'RTOS', '驱动开发'],
    'Go': ['Go', 'Docker', 'K8s', '微服务', 'Linux', 'MySQL', 'Redis'],
    'C++': ['C++', 'Linux', 'STL', '多线程', '算法', 'Qt', '嵌入式'],
    'PHP': ['PHP', 'MySQL', 'Redis', 'Linux', 'Nginx', 'Laravel', 'JavaScript'],
    'Node': ['JavaScript', 'Node.js', 'TypeScript', 'MySQL', 'Redis', 'MongoDB', 'K8s'],
    'Android': ['Java', 'Kotlin', 'Android', 'MVVM', 'Git', 'Retrofit'],
    'iOS': ['Swift', 'Objective-C', 'iOS', 'SwiftUI', 'Git', 'Xcode'],
    'React': ['JavaScript', 'React', 'TypeScript', 'HTML', 'CSS', 'Node.js', 'Redux'],
    'Vue': ['JavaScript', 'Vue', 'TypeScript', 'HTML', 'CSS', 'Node.js', 'Vuex'],
    'Flutter': ['Dart', 'Flutter', 'iOS', 'Android', 'Git', 'Firebase'],
    '区块链': ['Go', 'Solidity', '智能合约', '区块链', '分布式', '密码学'],
    '游戏': ['C++', 'Unity', 'Unreal', '游戏开发', '图形学', '3D建模'],
    '运维开发': ['Python', 'Linux', 'Docker', 'K8s', 'Shell', 'CI/CD', '监控'],
    'SRE': ['Linux', 'Docker', 'K8s', 'Python', '监控', '自动化运维'],
    '网络': ['TCP/IP', '路由交换', '防火墙', 'VPN', '网络安全', 'Linux'],
    '技术支持': ['Linux', 'SQL', 'Shell', '网络', '故障排查'],
    '实施': ['SQL', 'Linux', '项目管理', '客户沟通'],
    '销售': ['客户开发', '商务谈判', '客户关系', '市场分析', '合同管理'],
    '运营': ['数据分析', '用户运营', '活动策划', 'Excel', 'SQL'],
    '市场': ['数据分析', '营销策划', 'SEO', 'SEM', '用户增长', '品牌推广'],
    'CNC': ['CNC编程', '数控加工', 'CAD', 'CAM', '机械制图', '精密加工'],
    '数控': ['数控编程', 'CNC', 'CAD', 'CAM', '机械加工', 'Fanuc'],
    '普工': ['生产线操作', '设备操作', '安全生产', '质量检验'],
    '操作工': ['设备操作', '安全生产', '流程管理', '质量检验'],
    '生产': ['生产管理', '质量控制', '精益生产', '5S管理', '安全生产'],
    '工厂': ['生产管理', '设备维护', '质量检验', '安全生产'],
    '装配': ['机械装配', '电气装配', '图纸阅读', '质量检验', '工具使用'],
    '焊接': ['电焊', '氩弧焊', '二保焊', '气割', '焊接工艺'],
    '模具': ['模具设计', 'CAD', '加工中心', 'EDM', '模具维修'],
    '注塑': ['注塑工艺', '模具维护', '塑料材料', '调机', '质量检验'],
    '冲压': ['冲压工艺', '模具维护', '金属成型', '设备操作'],
    '钣金': ['钣金工艺', '折弯', '焊接', 'CAD', '金属加工'],
    '喷涂': ['喷涂工艺', '表面处理', '涂装技术', '颜色调配'],
    '铸造': ['铸造工艺', '模具设计', '熔炼', '热处理'],
    '锻造': ['锻造工艺', '金属成型', '模具设计', '热处理'],
    '热处理': ['热处理工艺', '金相分析', '硬度检测', '材料科学'],
    '质检': ['质量检验', '质量管理', 'ISO标准', '检测仪器', '来料检验'],
    '品管': ['质量管理', 'QC手法', 'ISO9001', '过程控制', '统计分析'],
    '设备': ['设备维修', '机械原理', '电气控制', 'PLC', '预防性维护'],
    '电工': ['电路检修', 'PLC', '配电系统', '电气安全', '万用表'],
    '机修': ['机械维修', '故障诊断', '液压系统', '气动系统', '润滑技术'],
    '机械': ['机械设计', 'CAD', 'SolidWorks', '机械原理', '材料力学'],
    '工艺': ['工艺流程', '工艺设计', '技术改进', '生产优化', '标准化'],
    '化工': ['化工工艺', '实验室操作', '安全规程', '化学分析', 'DCS'],
    '材料': ['材料科学', '材料检测', '性能分析', '材料工艺', '理化实验'],
    '电子': ['电路设计', 'PCB', '电子元器件', '焊接技术', '示波器使用'],
    '电气': ['电气设计', 'PLC', '变频器', '电气图纸', '自动化控制'],
    '自动化': ['PLC', 'SCADA', '工业机器人', '传感器', '自动控制'],
    '机器人': ['机器人编程', '运动控制', '传感器', 'ROS', '自动化集成'],
    '半导体': ['半导体工艺', '晶圆', '光刻', '封装测试', '洁净室'],
    '芯片': ['芯片设计', 'Verilog', '版图设计', '仿真验证', '半导体工艺'],
    'SMT': ['SMT贴片', '回流焊', 'AOI检测', 'PCB组装', '电子元器件'],
    '印刷': ['印刷工艺', '色彩管理', '印刷设备', '纸张材料', '品质控制'],
    '建筑': ['建筑设计', 'CAD', 'BIM', '建筑施工', '工程管理'],
    '施工': ['施工管理', '工程图纸', '安全管理', '进度控制', '材料管理'],
    '工程': ['工程管理', 'CAD', '项目协调', '技术方案', '现场管理'],
    '土木': ['结构设计', '土建施工', '工程测量', '混凝土', '地基处理'],
    '造价': ['工程造价', '广联达', '成本核算', '招投标', '工程量清单'],
    '招投标': ['招投标流程', '标书制作', '合同管理', '成本分析'],
    '监理': ['工程监理', '质量验收', '安全管理', '进度控制', '施工规范'],
    '测绘': ['工程测量', 'RTK', '全站仪', 'GIS', 'CAD'],
    '暖通': ['暖通空调', '给排水', 'CAD', 'BIM', '负荷计算'],
    '给排水': ['给排水设计', 'CAD', '管道系统', 'BIM', '水力计算'],
    '装饰': ['室内设计', 'CAD', '3DMax', '材料工艺', '施工管理'],
    '园林': ['园林设计', '景观规划', '植物配置', 'CAD', '绿化施工'],
    '房产': ['房产销售', '市场分析', '客户开发', '合同签订', '政策法规'],
    '物业': ['物业管理', '客户服务', '设施维护', '安全消防', '费用收缴'],
    '装修': ['装饰装修', '材料选购', '施工管理', 'CAD', '预算控制'],
    '财务': ['财务软件', '税务申报', '账务处理', '财务报表', '成本核算'],
    '会计': ['用友', '金蝶', '税务申报', '总账', '财务报表', 'Excel'],
    '出纳': ['现金管理', '银行对账', '票据管理', 'Excel', '财务软件'],
    '审计': ['审计流程', '风险评估', '内部控制', '会计准则', '审计软件'],
    '税务': ['税务申报', '税务筹划', '税法', '汇算清缴', '税务风险'],
    '金融': ['金融市场', '风险管理', '投资分析', '财务建模', '尽调'],
    '投资': ['投资分析', '尽调', '估值建模', '行业研究', '财务分析'],
    '银行': ['银行业务', '信贷管理', '风险控制', '客户服务', '金融产品'],
    '人事': ['招聘', '薪酬福利', '员工关系', '培训管理', '劳动法'],
    'HR': ['招聘', '薪酬管理', '绩效管理', '人才发展', 'HR系统'],
    '招聘': ['人才寻访', '面试技巧', '渠道管理', '背景调查', 'Offer谈判'],
    '行政': ['办公管理', '档案管理', '会议组织', '公文写作', '物资管理'],
    '前台': ['来访接待', '电话接听', '快递收发', '办公设备', '礼仪服务'],
    '文员': ['文档管理', 'Office办公', '数据录入', '会议记录', '沟通协调'],
    '秘书': ['日程管理', '公文写作', '会议组织', '商务礼仪', '沟通协调'],
    '助理': ['日程管理', '文档处理', '沟通协调', 'Office办公', '会议组织'],
    '法务': ['合同法', '公司法', '知识产权', '法律文书', '合规管理'],
    '律师': ['法律研究', '诉讼仲裁', '合同审查', '法律意见', '谈判'],
    '销售经理': ['销售管理', '客户开发', '团队管理', '商务谈判', 'CRM'],
    '销售代表': ['客户开发', '产品介绍', '商务谈判', '合同签订', '售后服务'],
    '销售工程师': ['技术销售', '方案讲解', '客户需求分析', '招投标', '技术方案'],
    '大客户': ['大客户管理', '关系维护', '商务谈判', '需求挖掘', '合同管理'],
    '渠道': ['渠道开发', '经销商管理', '市场拓展', '政策制定', '终端管理'],
    '区域经理': ['区域管理', '团队管理', '市场开拓', '客户维护', '业绩达成'],
    '招商': ['招商谈判', '市场调研', '客户开发', '合同管理', '商业规划'],
    '外贸': ['国际贸易', '英语沟通', '报关流程', '信用证', '外贸平台'],
    '电商': ['电商运营', '平台规则', '数据分析', '推广引流', '供应链'],
    '客服': ['客户沟通', '问题处理', '服务规范', '投诉处理', '工单系统'],
    '售后': ['售后服务', '故障处理', '客户培训', '维修保养', '备件管理'],
    '门店': ['门店运营', '库存管理', '客户服务', '收银系统', '陈列管理'],
    '品牌': ['品牌策划', '品牌传播', '市场调研', '媒体关系', '内容营销'],
    '策划': ['活动策划', '方案撰写', '项目管理', '创意设计', '预算控制'],
    '广告': ['广告投放', '创意设计', '数据分析', '媒体渠道', '效果优化'],
    '公关': ['媒体关系', '危机公关', '活动策划', '舆情管理', '新闻稿'],
    '物流': ['物流管理', '仓储管理', '运输调度', '供应链', 'WMS'],
    '仓储': ['库存管理', '出入库', 'WMS', '盘点', '安全管理'],
    '采购': ['供应商管理', '采购谈判', '成本控制', '合同管理', 'ERP'],
    '供应链': ['供应链管理', '需求预测', '库存优化', '物流协调', 'ERP'],
    '司机': ['驾驶技能', '车辆保养', '路线规划', '安全意识', '交通法规'],
    '快递': ['快件收发', '路线规划', '客户服务', '包裹分拣', '时效管理'],
    '配送': ['路线优化', '货物配送', '车辆管理', '客户沟通', '时效控制'],
    '厨师': ['烹饪技能', '食品安全', '成本控制', '菜品研发', '厨房管理'],
    '餐饮': ['餐饮管理', '食品安全', '成本控制', '团队管理', '客户服务'],
    '酒店': ['酒店管理', '客房服务', '前台接待', 'OTA运营', '客户满意度'],
    '前台接待': ['接待礼仪', '沟通技巧', '预定系统', '外语能力', '客户服务'],
    '客房': ['客房清洁', '布草管理', '客房服务', '物品管理', '卫生标准'],
    '保洁': ['清洁操作', '卫生标准', '设备使用', '安全规范', '垃圾分类'],
    '安保': ['安全巡逻', '监控系统', '消防知识', '应急处理', '门禁管理'],
    '保安': ['安全巡逻', '消防知识', '门禁管理', '应急处理', '监控值守'],
    '医生': ['临床诊断', '病历书写', '医学知识', '医患沟通', '医疗法规'],
    '护士': ['护理操作', '患者护理', '药品管理', '院感控制', '护理记录'],
    '医药': ['药品知识', 'GMP', '医药法规', '临床试验', '药学专业'],
    '制药': ['GMP', '药物制剂', '质量检测', '工艺验证', '药品注册'],
    '医疗': ['医疗器械', '临床知识', 'GMP', '法规合规', '技术支持'],
    '生物': ['生物技术', '实验操作', '细胞培养', '分子生物学', '数据分析'],
    '实验': ['实验操作', '仪器使用', '数据分析', '实验记录', '安全规范'],
    '教师': ['教学能力', '课程设计', '学生管理', '专业学科', '教育心理学'],
    '老师': ['教学能力', '课程设计', '学生管理', '专业学科', '教育心理学'],
    '培训': ['培训管理', '课程开发', '授课技能', '需求分析', '效果评估'],
    '讲师': ['授课技能', '课程开发', '演讲表达', '互动教学', '专业领域'],
    '教练': ['运动训练', '技能教学', '训练计划', '运动科学', '安全防护'],
    '课程': ['课程设计', '教学能力', '内容开发', '用户研究', '多媒体'],
    '设计': ['设计软件', '创意能力', '审美能力', '需求理解', '项目管理'],
    '平面': ['Photoshop', 'Illustrator', 'InDesign', '印刷工艺', '版式设计'],
    '工业设计': ['工业设计', 'Rhino', 'SolidWorks', '人机工程', '产品造型'],
    '结构': ['结构设计', 'CAD', '有限元分析', '力学计算', '材料选择'],
    '美工': ['Photoshop', 'Illustrator', '审美能力', '排版设计', '电商设计'],
    '经理': ['团队管理', '目标管理', '项目管理', '沟通协调', '决策能力'],
    '主管': ['团队管理', '任务分配', '绩效管理', '沟通协调', '业务指导'],
    '总监': ['战略规划', '团队管理', '资源整合', '决策能力', '行业经验'],
    '副总裁': ['战略规划', '高层管理', '资源整合', '决策能力', '行业洞察'],
    '总经理': ['企业运营', '战略管理', '团队领导', '财务管理', '市场洞察'],
    '管培生': ['学习能力', '沟通表达', '轮岗实践', 'Office办公', '职场素养'],
    '实习生': ['学习能力', 'Office办公', '沟通表达', '团队合作', '基础技能'],
    '合伙人': ['资源整合', '战略决策', '团队搭建', '业务拓展', '风险管控'],
    '软件开发': ['编程语言', '数据库', '系统设计', 'Git', '软件工程'],
    '计算机': ['计算机基础', 'Office办公', '网络基础', '编程基础', '数据库基础'],
    '数据标注': ['数据标注', '数据分类', '标注工具', '质量审核', '细致耐心'],
    '技术员': ['设备操作', '工艺规范', '质量检验', '故障排查', '安全生产'],
    '仓库管理': ['库存管理', '出入库', 'ERP', '物料管理', '安全管理'],
    '仓库': ['库存管理', '出入库', '物料管理', 'ERP', '安全管理'],
    '加工中心': ['CNC', '数控编程', 'CAD', '刀具管理', '设备维护'],
    '维修': ['故障诊断', '设备维修', '电路知识', '机械原理', '配件管理'],
    '商务': ['商务沟通', '合同管理', '市场分析', '客户关系', '招投标'],
    '制版': ['版型设计', 'CAD制版', '面料知识', '服装工艺', '排版放码'],
    '美妆': ['美妆产品', '销售技巧', '客户服务', '库存管理', '团队管理'],
    '低空': ['无人机技术', '低空法规', '飞行操作', '航测', '数据分析'],
    '电力': ['电力系统', '电气设备', '电力交易', '配电网', '能源管理'],
    '交易': ['市场分析', '风险控制', '交易策略', '数据分析', '合规管理'],
    '保险': ['保险产品', '精算基础', '风险评估', '理赔流程', '合规管理'],
    '车险': ['车险产品', '精算定价', '数据分析', '理赔管理', '保险法规'],
    '居家': ['远程办公', '自律管理', '在线协作', '时间管理', '电脑操作'],
    '数学': ['数学知识', '教学能力', '课程设计', '学生辅导', '表达能力'],
    '特气': ['特种气体', '气路系统', '安全规程', '纯度检测', '设备维护'],
    '滚齿': ['滚齿机操作', '齿轮加工', '机械制图', '量具使用', '设备维护'],
    'PM': ['项目管理', '敏捷开发', 'Scrum', '风险管理', '沟通协调'],
    'Data': ['数据分析', 'SQL', 'Python', '数据可视化', '统计学'],
    'Analytics': ['数据分析', 'SQL', 'Python', 'Tableau', '统计学'],
    '项目辅助': ['文档管理', '沟通协调', '进度跟踪', 'Office办公', '会议组织'],
    '手机': ['手机维修', '电路分析', '焊接技术', '故障诊断', '配件管理'],
    '博主': ['内容创作', '短视频制作', '社交媒体', '选题策划', '用户运营'],
    'Engineer': ['工程设计', '技术方案', '项目管理', '数据分析', 'CAD'],
    'Manager': ['团队管理', '战略规划', '预算管理', '沟通协调', '绩效考核'],
    'Specialist': ['专业技术', '流程优化', '数据分析', '报告撰写', '行业知识'],
    '电火花': ['电火花加工', 'EDM', '模具加工', '精密加工', '机械制图'],
    '省模': ['模具抛光', '表面处理', '模具维护', '精密测量', '手工技能'],
    '铣工': ['铣床操作', '机械加工', '机械制图', '量具使用', '刀具选择'],
    '磨床': ['磨床操作', '磨削工艺', '精密加工', '尺寸检测', '设备维护'],
    '线切割': ['线切割加工', '慢走丝', '编程', 'CAD', '精密测量'],
    '店员': ['客户服务', '收银操作', '商品陈列', '库存管理', '销售技巧'],
    '淘宝': ['淘宝运营', '直通车推广', '数据分析', '文案撰写', '客户服务'],
    '短视频': ['短视频拍摄', '视频剪辑', '选题策划', '平台运营', '数据分析'],
    '视频': ['视频制作', '拍摄技巧', '剪辑软件', '内容策划', '后期制作'],
    '会务': ['会议策划', '活动执行', '供应商管理', '预算控制', '现场管理'],
    '差旅': ['差旅管理', '预订系统', '客户服务', '成本控制', '供应商管理'],
    '纪检': ['纪律检查', '党规党纪', '调查取证', '文书写作', '沟通谈话'],
    '服务专家': ['客户服务', '服务设计', '流程优化', '沟通技巧', '投诉处理'],
    '固定资产': ['资产管理', '台账管理', '盘点清查', 'ERP', 'Excel'],
    '选址': ['市场调研', '数据分析', '商务谈判', '地产评估', '合规审查'],
    '车务': ['车辆管理', '车辆调度', '维修保养', '保险理赔', '合规管理'],
    '录题': ['视频录制', '题目讲解', '教学能力', '表达能力', '时间管理'],
    '效率': ['流程优化', '精益管理', '数据分析', '项目管理', '库存管理'],
}




def infer_skills_from_title(job_title):
    """从岗位名称推断技能列表"""
    if not job_title:
        return []
    for pattern, skills in JOB_TITLE_SKILLS_MAP.items():
        if pattern.lower() in job_title.lower():
            return skills
    return []


def _format_job(j):
    """Format a job row to dict, with skill inference for empty skills."""
    skills_raw = j.skills
    if not skills_raw or skills_raw == '[]' or skills_raw == 'null':
        inferred = infer_skills_from_title(j.job_title)
        skills_raw = json.dumps(inferred, ensure_ascii=False) if inferred else None
    return {
        'id': j.id,
        'job_title': j.job_title,
        'company': j.company,
        'city': j.city,
        'salary_raw': j.salary_raw,
        'salary_min': float(j.salary_min) if j.salary_min else None,
        'salary_max': float(j.salary_max) if j.salary_max else None,
        'experience': j.experience,
        'education': j.education,
        'skills': skills_raw,
        'crawl_time': j.crawl_time.isoformat() if j.crawl_time else None,
        'source': j.source,
        'enterprise_type': j.enterprise_type or '',
    }


@jobs_bp.route('/', methods=['GET'])
def list_jobs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    city = request.args.get('city')
    education = request.args.get('education')
    keyword = request.args.get('keyword')
    sort_by = request.args.get('sort_by', 'crawl_time')
    sort_order = request.args.get('sort_order', 'desc')
    fresh = request.args.get('fresh', 'true')  # 默认仅最近3个月

    query = JobsRaw.query

    # 默认只看最近 3 个月的岗位，传 fresh=false 查看全部
    if fresh.lower() != 'false':
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=90)
        query = query.filter(JobsRaw.crawl_time >= cutoff)

    if city:
        query = query.filter(JobsRaw.city == city)
    if education:
        query = query.filter(JobsRaw.education == education)
    if keyword:
        query = query.filter(
            JobsRaw.job_title.like(f'%{keyword}%') |
            JobsRaw.company.like(f'%{keyword}%')
        )

    # Configurable sort: allow salary_min, salary_max, crawl_time
    sort_col = {
        'crawl_time': JobsRaw.crawl_time,
        'salary_min': JobsRaw.salary_min,
        'salary_max': JobsRaw.salary_max,
    }.get(sort_by, JobsRaw.crawl_time)

    if sort_order == 'asc':
        order_clause = sort_col.asc()
    else:
        order_clause = sort_col.desc()

    pagination = query.order_by(order_clause).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify(
        total=pagination.total,
        page=page,
        per_page=per_page,
        items=[_format_job(j) for j in pagination.items]
    )


@jobs_bp.route('/cities', methods=['GET'])
def list_cities():
    cities = db.session.query(JobsRaw.city, db.func.count(JobsRaw.id)) \
        .group_by(JobsRaw.city) \
        .order_by(db.func.count(JobsRaw.id).desc()) \
        .all()
    return jsonify([{'city': c, 'count': n} for c, n in cities])


@jobs_bp.route('/count', methods=['GET'])
def total_count():
    count = db.session.query(db.func.count(JobsRaw.id)).scalar()
    return jsonify(total=count)


@jobs_bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    """Keyword autocomplete — returns matching job titles and company names."""
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify(titles=[], companies=[])

    titles = db.session.query(JobsRaw.job_title, db.func.count(JobsRaw.id)) \
        .filter(JobsRaw.job_title.like(f'%{q}%')) \
        .group_by(JobsRaw.job_title) \
        .order_by(db.func.count(JobsRaw.id).desc()) \
        .limit(8).all()

    companies = db.session.query(JobsRaw.company, db.func.count(JobsRaw.id)) \
        .filter(JobsRaw.company.like(f'%{q}%')) \
        .group_by(JobsRaw.company) \
        .order_by(db.func.count(JobsRaw.id).desc()) \
        .limit(8).all()

    return jsonify(
        titles=[{'name': t, 'count': c} for t, c in titles],
        companies=[{'name': t, 'count': c} for t, c in companies],
    )


@jobs_bp.route('/backfill-skills', methods=['POST'])
def backfill_skills():
    """
    Backfill empty skills for existing jobs by inferring from job titles.
    Returns count of updated rows.
    """
    # Find jobs with empty/null skills
    empty_jobs = JobsRaw.query.filter(
        (JobsRaw.skills.is_(None)) |
        (JobsRaw.skills == '') |
        (JobsRaw.skills == '[]') |
        (JobsRaw.skills == 'null')
    ).all()

    updated = 0
    for job in empty_jobs:
        inferred = infer_skills_from_title(job.job_title)
        if inferred:
            job.skills = json.dumps(inferred, ensure_ascii=False)
            updated += 1

    if updated > 0:
        db.session.commit()

    return jsonify({
        'status': 'success',
        'total_empty': len(empty_jobs),
        'backfilled': updated,
        'message': f'Backfilled {updated} out of {len(empty_jobs)} empty-skill jobs.',
    })


@jobs_bp.route('/stats/skills', methods=['GET'])
def skills_stats():
    """Get statistics about skill coverage in the data."""
    total = db.session.query(db.func.count(JobsRaw.id)).scalar()
    with_skills = db.session.query(db.func.count(JobsRaw.id)).filter(
        JobsRaw.skills.isnot(None),
        JobsRaw.skills != '',
        JobsRaw.skills != '[]',
        JobsRaw.skills != 'null',
    ).scalar()
    without_skills = total - with_skills
    return jsonify({
        'total_jobs': total,
        'with_skills': with_skills,
        'without_skills': without_skills,
        'coverage_pct': round(with_skills / max(total, 1) * 100, 1),
    })
