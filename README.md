# 学习通作业批改 Skill
一个面向教师端 Codex 工作流的实验报告批改 skill。它通过浏览器直接打开学习通附件预览，不下载学生原始 Word/PDF 文件，并结合题目要求、实现代码、运行结果、结果分析、实验心得和报告规范进行评分。
## 适用场景
- 学习通教师端按人批阅或按题批阅
- Word、DOCX、PDF 实验报告
- 包含代码、运行截图、图表或实验现象说明的课程作业
- 需要批量评分、给低分作业添加问题批注并核对全部待批项的场景
仅应在你有权审阅和处理相应学生作业的账号中使用。
## 核心安全约束
- 不点击附件“下载”；使用学习通内置浏览预览。
- 不把学生原始作业复制到本地项目或代码仓库。
- 如需 OCR，只为预览页建立独立临时目录，并在完成后删除。
- 不根据页数单独打分；必须查看关键章节、代码、结果图片及分析。
- 校验姓名、学号和附件是否匹配；发现重复文件或错交时先核实再处理。
- 不根据文风直接认定 AI 生成或抄袭，只记录可观察到的证据。
- 每次批量提交前遵守当前任务的确认规则；提交后逐项核对“已完成”和全班“待批 0”。
## 评分标准
### 100 分
同时满足以下条件：
- 实验目的、要求和环境明确
- 实现流程完整，代码或操作过程可复现
- 有实际运行结果截图、输出或图表
- 对结果进行了个人解释和分析，而非只贴图片
- 有实验结论、心得、反思或改进方向
- 体现个人思考、创新或合理扩展
- 报告结构清楚、格式整洁
### 80-99 分
主体完整且能够满足实验要求，但存在少量不足，例如：
- 分析较简短或重复
- 反思泛泛
- 个别章节内容偏少
- 代码与结果之间的联系不够充分
- 排版或格式存在小问题
基本完成但证据较简单的报告通常给 80 分左右；内容越充分、解释越深入，分数越高。
### 70-79 分
仅完成基础实验报告，或存在以下明显问题：
- 缺少关键分析
- 代码、结果和说明不完整
- 大量保留模板内容
- 格式明显不规范
- 内容高度雷同或与实际实验不符
### 50-60 分
明显未认真完成：
- 只有图片或零星文字
- 缺少可验证的实验过程
- 作业主题与实际实验严重不符
- 姓名、学号或提交文件明显错误
- 提交文件重复
- 内容过于简单，无法体现所要求的学习内容
教师可设置最低分；默认建议最低 60 分。70 分及以下应添加具体、可执行的批注。
## 工作流程
1. 确认课程、班级、作业名称、总分和待批数量。
2. 阅读题目要求及页面上的评分标准。
3. 逐个点击附件，在学习通浏览器内预览。
4. 核查学生身份、报告章节、代码、运行结果、图片分析、心得与格式。
5. 按评分标准形成分数和批注。
6. 通过 `scripts/validate_grades.py` 校验成绩清单。
7. 仅在获得相应授权后提交。
8. 检查每名学生是否显示“已完成”，并确认所有班级的待批数量为 0。
9. 清除 OCR/截图临时目录，确认没有下载或遗留学生原始文件。
详细步骤见 [references/workflow-and-safety.md](references/workflow-and-safety.md)，评分细则见 [references/grading-rubric.md](references/grading-rubric.md)。
## 安装
将此仓库克隆到 Codex 的用户 skill 目录：
```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/Teakasa/chaoxing-assignment-grader.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/chaoxing-assignment-grader"
```
Windows PowerShell：
```powershell
$target = "$HOME\.codex\skills\chaoxing-assignment-grader"
New-Item -ItemType Directory -Force (Split-Path $target) | Out-Null
git clone https://github.com/Teakasa/chaoxing-assignment-grader.git $target
```
安装后重新打开 Codex，或通过技能列表确认 `chaoxing-assignment-grader` 可用。
## 使用
```text
使用 $chaoxing-assignment-grader，在学习通教师端批阅所有待批实验报告。
使用浏览器预览附件，不下载原始文件。评分和批注完成后先给出清单。
```
提交成绩是影响学生记录的高风险操作，应根据当前授权策略在提交前确认。
## 成绩清单校验
可选用 JSON 保存待提交成绩并运行：
```bash
python scripts/validate_grades.py grades.json
```
清单格式示例：
```json
{
  "assignment": "Python 基础语法学习_列表和字典",
  "class_name": "物联网 307",
  "minimum_score": 60,
  "grades": [
    {
      "name": "示例学生",
      "student_id": "24100000",
      "score": 100,
      "attachment_id": "optional-object-id",
      "comment": "",
      "topic_mismatch": false,
      "evidence": {
        "purpose": true,
        "process": true,
        "results": true,
        "analysis": true,
        "reflection": true,
        "originality": true,
        "formatting": true
      }
    }
  ]
}
```
校验脚本会检查分数范围、重复学生、重复附件、低分批注以及满分证据完整性。
## 可靠性验证
发布前建议进行以下检查：
1. 在测试课程中验证附件通过预览打开且没有触发下载。
2. 验证普通完成、低质量、错交和重复文件四类样本得到不同分数。
3. 验证 70 分及以下包含具体批注。
4. 验证成绩提交后列表状态变为“已完成”。
5. 对每个班级重新盘点，确认“待批”均为 0。
6. 检查临时目录已删除，仓库中没有学生原始文件或个人数据。
本 skill 不绕过登录、验证码、权限或其他网站安全机制。
