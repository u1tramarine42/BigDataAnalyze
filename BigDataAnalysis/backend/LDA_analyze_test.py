import requests
import json

# 测试数据 - 模拟知网论文格式
test_paper = """
基于 STM32 的厨房燃气安防监测报警系统设计
唐英杰,常香香,范长胜
(东北林业大学,黑龙江 哈尔滨 15040)
摘要:设计了一款厨房燃气安防监测报警系统。 该系统集成了 DHT22 温湿度传感器与红外人体感应传感器,并采用
STM32F103C6T6 作为核心控制芯片。 通过运用单片机技术,系统能够实时监测厨房内的多种状态，包括人员存在情况、温度、湿度
及燃气使用时间等关键参数。 基于这些监测数据，系统进行综合判断，并根据预设的安全报警等级，采取相应的报警措施或自动切
断燃气供应，从而有效预防火灾事故的发生。
关键词: 智能厨房;燃气安防监测;预警系统;单片机
中图分类号: TP277 文献标志码: A 文章编号: 1006-2394(2025)02-0022-03
Design of Kitchen Gas Security Monitoring and Alarm System Based on STM32
TANG Yingjie, CHANG Xiangxiang, FAN Changsheng
(Northeast Forestry University, Harbin 150040, China)
Abstract: A kitchen gas security monitoring and alarm system was designed. The system integrates DHT22 temperature and humidity sensors and infrared human body sensing sensors, and uses STM32F103C6T6 as the core control chip.
By using microcontroller technology, the system can monitor various states in the kitchen in real time, including key
parameters such as personnel presence, temperature, humidity, and gas usage time. Based on these monitoring data, the
system makes comprehensive judgments and takes corresponding alarm measures or automatically cuts off gas supply
according to the preset safety alarm level, thereby effectively preventing the occurrence of fire accidents.
Key words: smart kitchen; gas security monitoring; alarm system; single-chip microcomputer
0 引言
随着现代社会的飞速发展，厨房已成为家庭生活
中不可或缺的重要空间，其智能化与安全化的需求日
益凸显。 因此，未来厨房的设计应朝着更加舒适与安
全的方向发展。 相较于传统厨房燃气报警器仅具备检
测燃气泄漏的功能，本监测报警系统在设计上实现了
重大突破。 它不仅将厨房内是否有人作为检测状态之
一，还全面监控厨房的燃气使用情况，并同时检测厨房
的温湿度以及燃气使用时间。 这些功能的加入极大地
提升了厨房监测报警系统的实用性和厨房的整体安
全性。
参考文献:
[1] 严强虎,曹新莉,张军.高压高阻标准器的设计与制作[D].
武汉:武汉工程大学,2017.
[2] 李成祥,姬光荣.热交换式农业大棚温湿度自动控制系统
[D].青岛:中国海洋大学,2012.
[3] 彭勇,陶曾杰,林振,等.基于 STM32 和 OneNET 的智能家
居系统的设计[J].物联网技术,2024(2):86-87.
"""
test_paper2="""
从DeepSeek突破看我国人工智能产业创新范式、挑战与应对
魏　巍，曾　铮，刘　蕾
（国家发展和改革委员会市场与价格研究所，北京 100038）
（北京工商大学商学院，北京 100048）
摘要：作为引领新一轮科技革命和产业变革的关键技术，人工智能已成为全球竞争最关键的领域。
DeepSeek的突破标志着我国在AI大模型技术研发中取得显著进展，不仅展现出我国AI企业在大模型
领域的创新能力，更反映出新时代科技产业创新范式的深刻变革。从DeepSeek的创新实践可以发现，
其在技术路径选择、创新资源配置、商业模式创新和产业生态构建等方面形成了独特的创新范式特征，
但在核心技术持续突破、人才储备、计算资源保障和治理规范等方面也面临着诸多挑战。面对全球AI
产业发展的新态势，我国应着力构建韧性供应链，完善人才培养体系，建设国家算力网络，优化创新生
态环境，建立有效的治理机制，深化国际合作，以推动我国人工智能产业实现高质量发展，在全球AI技
术与产业竞争中占据有利地位。
关键词： 人工智能；产业创新范式；大模型；Deepseek
中图分类号：F49 文献标志码：A
一、引言
人类自首次尝试用机械与计算机解决复杂问题以来，就一直在追求创造具有“类人智能”的技术系
统。从1950年图灵测试的提出，到1956年达特茅斯会议确立人工智能（AI）概念，AI技术开启了不断迭
代创新的发展历程。经过七十多年的发展与突破，人工智能技术已经历了多次起伏，从早期的符号推
理、专家系统，到机器学习、深度学习，再到如今的大规模预训练模型，呈现技术范式不断迭代更新的发
展轨迹。当前，以大语言模型为代表的生成式人工智能技术正引领新一轮创新浪潮，重塑着全球科技
竞争格局和产业发展路径。特别是以OpenAI公司GPT系列为代表的大语言模型（Large Language Mod⁃
els，LLMs）的快速崛起，推动人工智能技术从面向特定任务的“专用智能”走向具备广泛适应性和泛化
能力的“通用智能”，引发了全球范围内的技术竞争与产业变革。2025年初，国产大模型企业杭州深度
求索公司（DeepSeek）凭借在混合专家模型（Mixture of Experts，MoE）架构上的技术创新，结合群体相对
策略优化（Group Relative Policy Optimization，GRPO）、多头隐式注意力（Multi-head Latent Attention，
MLA）等方法的突破，大幅提升了大模型的训练效率与推理性能，实现了在有限计算资源条件下达到国
际领先水平的技术跨越，迅速赢得了国际市场的广泛关注，为全球人工智能技术发展提供了新的路径
作者简介：魏巍，国家发展和改革委员会市场与价格研究所助理研究员；曾铮，国家发展和改革委员会市场与价格研究
所研究员；刘蕾（通讯作者），北京工商大学商学院博士后、副教授。
注：本文是中国宏观经济研究院（国家发展和改革委员会宏观经济研究院）基本经费研究课题“中美科技竞争下的革新
突围：基于AI大模型发展看我国人工智能产业创新范式、挑战与应对”的成果。

参考文献：
[1]习近平在中共中央政治局第九次集体学习时强调 加强领导做好规划明确任务夯实基础 推动我国新一代人工智能健康发展[N].
人民日报，2018-11-01.
[2]习近平.高举中国特色社会主义伟大旗帜 为全面建设社会主义现代化国家而团结奋斗——在中国共产党第二十次全国代表大
会上的报告[N].人民日报，2022-10-26.
[3“] 十四五”国家信息化规划[EB/OL].[2021-12-28].中国政府网，https：//www.gov.cn/xinwen/2021-12/28/5664873/files/1760823a103e4
d75ac681564fe481af4.pdf
[4]Parker G G，Van Alstyne M W，Choudary S P.Platform Revolution：How Networked Markets are Transforming the Economy and How to
Make Them Work for You[M].New York：W.W.Norton & Company，2016.
[5]Chesbrough H W.Open Innovation：The New Imperative for Creating and Profiting from Technology[M].Harvard Business School Press，
2003.
[6]陈劲.整合式创新——新时代创新范式探索[M].北京：科学出版社，2021.
[7]熊彼特.经济发展理论[M].北京：中国人民大学出版社，2019.
— 12 —
经济纵横
[8]Thomas K.The Structure of Scientific Revolutions[M].University of Chicago Press，1962.
[9]Freeman C，Perez C.Structural Crises of Adjustment，Business Cycles and Investment Behaviour[M]//Dosi G，Freeman C，Nelson R，et al.
Technical Change and Economic Theory[M].London：Pinter Publishers，1988：38-66.
[10]Lundvall B-A.National Systems of Innovation：Towards a Theory of Innovation and Interactive Learning[M].London：Pinter Publishers，
1992.
[11]Nelson R R.National Innovation Systems：A Comparative Analysis[M].New York：Oxford University Press，1993.
[12]龙海波.科技创新与产业创新深度融合：模式、堵点与突破[J].北京行政学院学报，2025（1）：22-30.
[13]刘丛，王薇，谢斌，等.科技人才、技术扩散与经济转型：留学生对近代中国工业发展的影响[J].经济学（季刊），2025（1）：1-17.
"""

test_paper3="""
基于计算机视觉的车致桥梁挠度测试与车辆定位研究
万华平1，王灿 1，房天乐 1，曹素功 2，王宁波 3
(1. 浙江大学建筑工程学院, 杭州 310058；2. 浙江省交通运输科学研究院, 杭州 311305；
3. 中南大学土木工程学院, 长沙 410075)
摘要：为提高桥梁挠度测试与车辆定位的便捷性和准确性，提出基于计算机视觉的车致桥梁
挠度测试与车辆定位方法。采用无人机拍摄车辆，结合 SLAM 算法和 YOLO 算法实现相机
姿态估计和车辆实时定位。针对车致桥梁挠度测试，提出了改进的 SIFT 算法来提取和匹配
桥梁图像特征点，并根据特征点的位置变化识别桥梁挠度响应。通过车辆过桥室内试验验证
了该方法的可行性及准确性。结果表明，通过剔除无人机视野中的动态特征点，可提升无人
机姿态估计的准确性，车辆定位误差可控制在 1%以下。改进的 SIFT 算法可较好提取并匹
配特征点，在 1.5 m 的拍摄距离下，可实现约±0.368 pixel 精度的图像位移识别。基于计算机
视觉的挠度测试与车辆定位方法兼具非接触、高精度优势，可为中小桥梁快速检测评估提供
可靠的数据支撑。
关键词：桥梁工程; 移动车辆荷载; 车辆定位; 挠度测试; 计算机视觉; 无人机
中图分类号：U446.2
Measurement of vehicle-induced bridge deflection
and vehicle localization based on computer vision
WAN Huaping1
, WANG Can1
, FANG Tianle1
, CAO Sugong2
, WANG Ningbo3
(1. College of Civil Engineering and Architectural, Zhejiang University, Hangzhou 310058, China;
2. Zhejiang Transportation Research Institute, Hangzhou 311305, China;
3. School of Civil Engineering, Central South University, Changsha 410075, China)
Abstract: To improve the convenience and accuracy of bridge deflection measurement and vehicle
localization, a computer vision-based method for vehicle-induced bridge deflection measurement
and vehicle localization is proposed. A UAV is used to capture vehicle images, and the SLAM
algorithm combined with the YOLO algorithm is used to estimate camera pose and achieve vehicle
localization. For bridge deflection measurement, an improved SIFT algorithm is proposed to extract
and match bridge features. The bridge deflection is calculated by the movement of bridge features.
The feasibility and accuracy of this method are verified by laboratory experiment. The results show
that removing dynamic features from UAV imagery enhances pose estimation, reducing vehicle
localization errors to below 1%. The improved SIFT algorithm effectively extracts and matches
features, achieving deflection measurement with an accuracy of approximately ±0.368 pixels at a
shooting distance of 1.5 m. The proposed computer vision-based deflection measurement and
vehicle localization method combines non-contact measurement and high precision, offering
reliable data support for rapid assessment of small and medium-span bridges.

收稿日期:2025-01-14.
作者简介:万华平(1986—)，男，博士，研究员，博士生导师，hpwan@zju.edu.cn.
基金项目:国家自然科学基金优秀青年基金资助项目(52422804)；公路桥隧智能运维技术浙江省工程中心开
放基金资助项目(202401G).
网络首发时间：2025-04-30 17:02:58 网络首发地址：https://link.cnki.net/urlid/32.1178.N.20250430.1525.004
Key words: bridge engineering; moving vehicle load; vehicle localization; deflection measurement;
computer vision; unmanned aerial vehicle
车辆荷载是桥梁结构主要的动荷载之一，在各类荷载组合中占据重要地位。车辆荷载信
息和车致挠度响应是分析桥梁结构性能的重要参数，广泛应用于影响线提取[1]、损伤检测[2]、
刚度识别[3]等桥梁检测评估研究中。准确获取车辆荷载信息和车致挠度响应，对中小桥梁快
速检测评估具有重要意义。目前，车辆荷载大小通常采用动态称重系统或车载称重系统获得
轴重信息[4]，荷载位置则通过激光测距仪[5]或 GPS[6]等方式获取，在经济性和时效性上较为
欠缺。针对桥梁挠度测试，桥梁常跨河流、道路等，在下方设置工作平台难度较大，导致传
统接触式测试方法存在实施困难等不足[7]。
基于计算机视觉的测试方法已被广泛应用到土木工程领域[8-9]，为车辆定位提供了新思
路。Ge 等[10]基于 YOLO（you only look once，YOLO）框架，引入几何模型来测量车辆尺寸
和修正车辆质心，实现车辆精准定位。桥梁结构在跨度方向尺寸通常较大，采用单个摄像头
无法记录车辆过桥的全过程。对此，Zhu 等人[11]在桥梁跨度方向布设多个摄像头，利用边缘
计算技术对拍摄信息进行拼接，实现车辆过桥的全过程定位。基于即时定位与地图构建
（simultaneous localization and mapping，SLAM）技术[12]的无人机巡航技术增加了相机视角
的灵活性，无需在试验前后布设和拆卸摄像头，是快速定位移动车辆的可行方式。但 SLAM
算法估计的相机姿态会受到移动车辆的干扰，并不具有真实尺寸，将其应用至车辆移动过桥
场景还需进一步研究。
在车致桥梁挠度测试方面，计算机视觉的测试具备远距离、多点测试等优势，在结构位
移测试中具有较好前景[13-14]。特征点匹配是计算机视觉测试位移的核心，它将不同图像中的
目标特征点对应，并根据特征点的位置变化计算位移。尺度不变特征转换(scale-invariant
feature transform，SIFT)[15]是常用的特征点匹配算法，该算法对环境光照、视频噪声等因素
不敏感，具有较好的鲁棒性。Perry 等[16]利用光学摄像机记录拉索在爆炸荷载下的视频图像，
并采用 SIFT 算法识别拉索的动态位移，实现拉索动态参数提取。由于 SIFT 算法通过固定
的距离比阈值来判断特征点匹配效果，易引起误匹配问题，影响位移测试的准确性。
本文提出了一种基于计算机视觉的车致桥梁挠度测试与车辆定位方法。该方法采用无人
机拍摄车辆，提出结合 SLAM 算法和 YOLO 算法的相机姿态估计和车辆实时定位方法。针
对车致桥梁挠度测试，提出了改进的 SIFT 算法提取和匹配桥梁特征点，实现桥梁挠度响应
测试。通过车辆过桥室内试验验证了该方法的准确性和有效性。
参考文献（References）
[1] WANG N B, WANG C, ZHOU H, et al. A novel extraction method for the actual influence line of bridge
structures[J]. Journal of Sound and Vibration, 2023, 553: 117605.
[2] WANG N B, WANG C, HUANG T L, et al. A novel attached-spring model for damage quantification and
degradation evaluation of short/mid-span bridges[J]. Structural Health Monitoring, 2025, 24(2): 853-868.
[3] WAN H P, WANG C, WANG N B, et al. Bending stiffness identification of continuous girder bridges using
multiple rotation influence lines[J]. Journal of Bridge Engineering, 2024, 29(12): 04024097.
[4] 李小年, 陈艾荣, 马如进. 桥梁动态称重研究综述[J]. 土木工程学报, 2013, 46(3): 79-85.
LI X N, CHEN A R, MA R J. Review of bridge weigh-in-motion[J]. China Civil Engineering Journal, 2013,
46(3): 79-85. (in Chinese)
[5] HE W Y, REN W X, ZHU S Y. Damage detection of beam structures using quasi-static moving load induced
displacement response[J]. Engineering Structures, 2017, 145: 70-82.
[6] ZHENG X, YANG D H, YI T H, et al. Development of bridge influence line identification methods based on
direct measurement data: A comprehensive review and comparison,[J]. Engineering Structures, 2019, 198:
109539.
[7] WANG N B, WANG C, WAN H P, et al. An approach for identification of bridge bending stiffness distribution
using improved Gaussian peak function[J]. Journal of Sound and Vibration, 2024, 573: 118218.
[8] 朱尧于, 李佳欢, 朱力, 等. 基于视觉增强的桥梁检测算法及技术[J]. 东南大学学报(自然科学版),
2024, 54(4): 902-910.
ZHU Y Y, LI J H, ZHU L, et al. Visual enhancement-based bridge detection algorithm and technique[J].
Journal of Southeast University (Natural Science Edition), 2024, 54(4): 902-910. (in Chinese)
[9] WAN H P, ZHANG W J, CHEN Y, et al. An efficient three-dimensional point cloud segmentation method for
the dimensional quality assessment of precast concrete components utilizing multiview information fusion[J].
Journal of Computing in Civil Engineering, 2025, 39(3): 04025028.
[10] GE L F, DAN D H, LI H. An accurate and robust monitoring method of full-bridge traffic load distribution
based on YOLO-v3 machine vision[J]. Structural Control and Health Monitoring, 2020, 27(12): e2636.
[11] ZHU J S, LI X T. Cross-camera tracking of vehicle loads based on deep metric learning and edge computing[J].
Measurement, 2022, 199: 111578.
[12] MUR-ARTAL R, TARDÓS J D. ORB-SLAM2: An open-source SLAM system for monocular, stereo, and
RGB-D cameras[J]. IEEE Transactions on Robotics, 2017, 33(5): 1255-1262.
[13] 单伽锃, 张宏泽, 白子轩, 等. 基于视觉与振动数据融合的结构层间位移响应识别[J]. 东南大学学报
(自然科学版), 2025, 55(1): 41-50.
SHAN J Z, ZHANG H Z, BAI Z X, et al. Interstory drift response identification of structures based on vision
and vibration data fusion[J]. Journal of Southeast University (Natural Science Edition), 2025, 55(1): 41-50.
(in Chinese)
[14] 杜文康, 王浩, 雷冬, 等. 基于机器视觉和边缘重构的拉索振动响应识别[J/OL]. 东南大学学报(自然
科学版), 2025[2025-02-26]. http://kns.cnki.net/kcms/detail/32.1178.N.20250226.1007.002.html.
DU W K, WANG H, LEI D, et al. Vibration response identification of cable based on machine vision and edge
reconstruction[J/OL]. Journal of Southeast University (Natural Science Edition), 2025[2025-02-26].
http://kns.cnki.net/kcms/detail/32.1178.N.20250226.1007.002.html. (in Chinese)
[15] LOWE D G. Distinctive image features from scale-invariant keypoints[J]. International Journal of Computer
Vision, 2004, 60(2): 91-110.
[16] PERRY B J, HEYLIGER P R, GUO Y L, et al. Unmanned aerial system-based portable sensing for blastloaded cables[J]. Journal of Structural Engineering, 2024, 150(3): 06023003.
[17] BOCHKOVSKIY A, WANG C Y, LIAO H M. YOLOv4: Optimal speed and accuracy of object
detection[EB/OL]. (2020-04-23)[2025-01-14]https://arxiv.org/abs/2004.10934v1.
[18] ZHANG Z. A flexible new technique for camera calibration[J]. IEEE Transactions on Pattern Analysis and
Machine Intelligence, 2000, 22(11): 1330-1334.
[19] BESL P J, MCKAY N D. A method for registration of 3-D shapes[J]. IEEE Transactions on Pattern Analysis
and Machine Intelligence, 1992, 14(2): 239-256.
[20] DETONE D, MALISIEWICZ T, RABINOVICH A. SuperPoint: Self-supervised interest point detection and
description[C]// 2018 IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops
(CVPRW). Salt Lake City, UT, USA, 2018: 337-349.
"""

test_paper4="""
Upsurge of Spontaneous Knotting in Polar Diblock Active Polymers
Marin Vatin , Enzo Orlandini , and Emanuele Locatelli
Department of Physics and Astronomy, University of Padova, Via Marzolo 8, I-35131 Padova, Italy
and INFN, Sezione di Padova, Via Marzolo 8, I-35131 Padova, Italy
(Received 9 July 2024; revised 12 February 2025; accepted 12 March 2025; published 24 April 2025)
Spontaneous formation of knots in long polymers at equilibrium is inevitable but becomes rare in
sufficiently short chains. Here, we show that knotting increases by orders of magnitude in diblock polymers
having a fraction p of self-propelled monomers. Remarkably, this enhancement is not monotonic in p with
an optimal value independent of the monomer’s activity. By monitoring the knot’s size and position we
elucidate the mechanisms of its formation, diffusion, and untying and ascribe the nonmonotonic behavior
to the competition between the rate of knot formation and the knot’s lifetime. These findings suggest a
nonequilibrium mechanism to generate entangled filaments at the nano- and microscales.
DOI: 10.1103/PhysRevLett.134.168301
The emergence of topological signatures is ubiquitous in
soft matter physics, ranging from conventional polymers,
biopolymers, defect loops, and vortices [1]. Knots are the
best-known example of a topological state due to their
practical relevance in everyday life. Still, they are also
observed at the micro- and nanoscales, where their presence
can have a significant impact on the physical properties of
the hosting system [2–11]. In biology, knots in DNA can
affect the regulation of gene expression [12–14], the
process of DNA replication or recombination [15] and
the spatial organisation and ejection dynamics of viral
DNAs [16–18]. Knotted motifs have been observed in
proteins and they are believed to play a crucial role in the
folding and mechanical stability of the polypeptides
[19–24]. Going beyond thermodynamic equilibrium, topological signatures have been recently explored in active
systems such as cytoskeleton [25], actomyosin networks
[26], gliding assays [27], chromatin [28,29], worms assemblies [30,31], and active nematics [32]. Natural playgrounds to explore the physics and topology of these
nonequilibrium systems are the so-called active polymers,
which lately have attracted interest because of their
statistical properties and wide range of applications
[33,34]. The relevance of the interplay between the activity
and the topology of fluctuating filaments has emerged in
systems of active linear chains under confinement [35,36]
in melts [37–40] as well as in diluted [41–43] and
concentrated [44–46] solutions of active rings.
These works focus on unknotted rings or mutual entanglement in linear chains; self-entanglements have been
scarcely investigated in this context. In Ref. [47], the
authors observed fewer knots than in equilibrium in a
coarse-grained active polymer model with explicit motors;
recently, it was shown that a grafted polar active polymer spontaneously forms knots [48]. In these out-ofequilibrium systems, local stresses and enhanced motility
due to activity may affect the mechanism of entanglement
formation and, consequently, the frequency of spontaneous
knot formation. As such, they represent an intriguing venue
for producing knotted filaments at the nanoscales.
In this work, we study the formation of self-entanglements
in an active-passive diblock copolymer where only a fraction
of the monomers, p, are active. Focusing on knotting
probability and knot complexity in steady state, we show
that, for relatively short chains, the likelihood of observing a
knot may increase by orders of magnitude, compared to the
equilibrium case. Strikingly, the knotting probability is a
nonmonotonic function ofp with an optimal value that seems
independent of the polymer’s activity and length. By
exploring the knotting and unknotting events and the knot
motion we ascribe the nonmonotonic behaviour to the
competition between the rate of knot formation, always
occurring at the active extremity, and the knots’ lifetime,
dominated by its residence time in the passive region. The
system can therefore be steered toward forming more knots
by tuning the fraction p.
We consider a model of a flexible linear polymer chain of
length L ¼ Nσ, σ ¼ 1 being the bead’s diameter; we
consider here 200 <N< 400, focusing mostly on N ¼
300, a length that is too short to observe knot formation
events at equilibrium [49]. Following Ref. [50], we design
the active-passive heterogeneity as a diblock copolymer,
namely, a chain made by two contiguous blocks, the active
one of length Npσ and the passive one of length
Nð1 − pÞσ. The active block is located at one of the two
ends of the chain, which we call the “head” of the polymer.
Each active monomer is self-propelled by a force fa, with
constant magnitude fa, directed as the local tangent to the
backbone; this is known as tangential or polar selfpropulsion. The overall active force points in the direction
of the head (also referred to as the “leading” end) [50].
Following [50,51], both end beads are made passive.
"""
# Flask API端点
API_URL = "http://localhost:5000/extract_keywords"


def test_paper_extraction():
    # 准备请求数据
    data = {
        "text": test_paper
    }

    try:
        response = requests.post(API_URL, json=data)
        response.raise_for_status()  # 检查HTTP错误

        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            print("情感分析结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")


if __name__ == "__main__":
    test_paper_extraction()