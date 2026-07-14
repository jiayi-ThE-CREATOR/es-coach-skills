# es-coach-skills — 日本就活 ES 对话教练 Claude Code Skills

**简体中文** | [日本語](README.md)

面向日本就活(应届生招聘)ES(自我推荐信/エントリーシート)对策的三件套 [Claude Code](https://claude.com/claude-code) Skill。从内定者的经验谈中蒸馏成功模式,以此为依据批改 ES,并用企业分析报告核对企业理念、求人形象与 ES 内容是否契合。

> 这是从个人就活自动化项目中抽取出的 Skill 本体。不包含你的 ES 内容、企业信息或 vault 数据——一切都会积累在你自己的 Obsidian vault 里。

## 三个 Skill 的关系

```
shukatsu-distill (ingest / grill)   kigyou-report
  收集内定者经验谈 / 本人经历          把企业理念、部门、
  作为素材积累                        求人形象整理成结构化报告
        │                                   │
        ▼                                   ▼
shukatsu-distill (distill)  ──────────►  蒸馏知识文件
        │                                   │
        └───────────────┬───────────────────┘
                         ▼
                     es-coach
              接收 ES,以上述两者为依据批改
```

| Skill | 作用 |
|-------|------|
| `es-coach` | 对话式批改 ES(事实核查 → 评价 → 修改循环 → 定稿签字)。以蒸馏知识、企业分析报告、本人过往经历为依据 |
| `shukatsu-distill` | 四种模式:`ingest`(录入内定者经验谈)/ `distill`(提炼成功模式)/ `coach mock`(模拟面试)/ `grill`(反向面试,挖掘并素材化本人经历) |
| `kigyou-report` | 把指定企业整理成固定 12 章节的结构化报告(部门地图、企业理念、ES 攻略法等) |

三者都以读写 Obsidian vault 为前提,vault 内的路径统一经由 `vault.paths.env` 这一**唯一注册表文件**解析(即使 vault 目录重新整理,也不用改 Skill 正文)。

## 前置依赖

- [Claude Code](https://claude.com/claude-code)(Skills 功能)
- Obsidian(或同等的 Markdown vault)
- Python 3(运行 `tools/count_chars.py` 和 `tools/experience_inventory_sync.py` 需要,依赖 `pyyaml`)

## 安装步骤

```bash
# 1. 克隆仓库
git clone <this-repo-url> es-coach-skills
cd es-coach-skills

# 2. 把本仓库位置设为环境变量(写入 shell 启动文件)
echo 'export SHUKATSU_SKILLS_ROOT="'"$(pwd)"'"' >> ~/.zshrc
source ~/.zshrc

# 3. 配置 vault 路径
cp vault.paths.example.env vault.paths.env
$EDITOR vault.paths.env   # 改成你自己 Obsidian vault 的实际路径

# 4. 让 Claude Code 识别这几个 Skill(复制或软链接都可以)
mkdir -p ~/.claude/skills
ln -s "$SHUKATSU_SKILLS_ROOT/skills/es-coach"         ~/.claude/skills/es-coach
ln -s "$SHUKATSU_SKILLS_ROOT/skills/shukatsu-distill" ~/.claude/skills/shukatsu-distill
ln -s "$SHUKATSU_SKILLS_ROOT/skills/kigyou-report"    ~/.claude/skills/kigyou-report

# 5. Python 依赖
pip install pyyaml
```

配置完成后,建议在 Claude Code 里从 `/shukatsu-distill ingest` 开始(投入内定者经验谈、YouTube 视频文字稿、就活网站文章等 → 自动蒸馏 → 用 `/es-coach` 批改 ES,形成完整流程)。

## 使用方法

```
/shukatsu-distill ingest      录入内定者经验谈/文章作为素材
/shukatsu-distill distill     从素材中提炼成功模式,写入蒸馏知识
/shukatsu-distill grill       以反向面试的形式挖掘你自己的经历并素材化
/shukatsu-distill coach mock  模拟面试
/kigyou-report <企业名>        生成企业分析报告
/es-coach                     对话式批改 ES
```

## 蒸馏知识、素材存在哪里?

存在 `vault.paths.env` 里指定的 vault 中,随着你就活的推进逐步积累。本仓库只包含逻辑(Skill 的指令文本和辅助脚本),不含你任何具体的企业选考内容或 ES 实际数据。

## 许可证

MIT。见 `LICENSE`。
