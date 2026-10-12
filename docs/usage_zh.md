# 中文使用说明

这是一套独立通用工具，内置数据和图片全部为人工虚构的 Synthetic data，不包含任何真实论文数据。适用范围是柱状图辅助数字化、独立两组连续结局Meta分析和八类科研绘图，不支持所有图片的全自动识别，也不提供RNA分析。

安装Python与R后，在代码根目录按英文README建立虚拟环境，安装requirements.txt、测试依赖requirements-dev.txt及environment/install.R列出的R包。运行 `python toolkit.py all` 可实际执行全部示例与测试；不需要知道任何旧研究目录。

数字化：`python toolkit.py digitize measure --image examples/synthetic_data/linear.png --config examples/synthetic_data/linear_points.json --out outputs/digitizer/linear`。使用自己的图片时，必须重新核对面板、组别、刻度、柱顶与误差帽。SD/SEM和样本量由使用者从可靠原文输入，程序不猜测。图形无法可靠标定时应停止取数。

统计：`python toolkit.py meta --input examples/synthetic_data/groups.csv --out outputs/meta --measure MD`。替换为自己的CSV时保留字段格式。MD要求可直接比较的单位；重复动物、共享对照、相关效应必须使用其他适合的模型。默认REML、未修正HKSJ和df=k−2的Riley型PI。具体公式及小k限制见模块文档。

绘图：先运行示例分析，再用README的八种plot命令。图形只展示输入结果，不能替代来源判断。标题、字体、颜色、图例、尺寸、DPI与CI/PI显示可在JSON中设置。

使用说明：[数字化](digitizer.md)、[Meta分析](meta_analysis.md)、[绘图](plotting.md)。许可证尚待确认，当前不是已经获得授权的开源发行版，也未上传GitHub。
