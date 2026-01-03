# 智能合约安全审计工具

一个面向 Solidity 智能合约的静态安全审计工具，支持漏洞检测、数据流分析和可视化报告生成。

> 作者: tr3

## 功能特性

### 漏洞检测
- ✅ 重入攻击风险检测
- ✅ 权限控制缺失检测
- ✅ 外部调用风险检测
- ✅ 未检查返回值检测
- ✅ 危险的 delegatecall 检测

### 分析功能
- 控制流分析
- 调用图构建
- 污点分析（简化版）
- 数据流分析

### 报告生成
- JSON 格式报告（结构化数据）
- HTML 可视化报告（黑白主题，易于阅读）

### CI 集成
- GitHub Actions 自动扫描
- 报告上传到 Artifact（保留30天）

## 安装

### 1. 激活虚拟环境

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 2. 安装依赖

激活虚拟环境后：

```bash
pip install -r requirements.txt
pip install -e .
```

## 使用方法

### 命令行使用

#### 基本命令格式

```bash
python -m contract_auditor.main <文件或目录> [选项]
```

**重要提示：**
-  正确方式：`python -m contract_auditor.main [文件]`
-  错误方式：`python contract_auditor/main.py [文件]` （会导致导入错误）

#### 查看帮助信息

```bash
# 查看完整帮助信息
python -m contract_auditor.main -h
# 或
python -m contract_auditor.main --help
```

**无参数运行：**
如果直接运行命令而不提供参数，工具会显示提示信息：

```bash
python -m contract_auditor.main
```

输出示例：
```
============================================================
  智能合约安全审计工具
============================================================

提示: 请指定要扫描的合约文件或目录路径
使用 -h 或 --help 查看详细帮助信息

快速示例：
  python -m contract_auditor.main examples/single_file_1.sol
  python -m contract_auditor.main examples/project/contracts/
  python -m contract_auditor.main -h  # 查看完整帮助
```

#### 命令参数说明

| 参数 | 简写 | 说明 | 可选值 |
|------|------|------|--------|
| `--output-dir` | `-o` | 指定报告输出目录 | 任意目录路径 |
| `--format` | `-f` | 输出格式 | `json` / `html` / `both`（默认） |
| `--severity` | `-s` | 最低风险等级过滤 | `critical` / `high` / `medium` / `low`（默认） |

#### 常用命令示例

**0. 查看帮助和提示**

```bash
# 查看完整帮助信息（包含所有参数说明和使用示例）
python -m contract_auditor.main -h

# 无参数运行（显示快速提示）
python -m contract_auditor.main
```

**1. 扫描单个合约文件**

```bash
# 基本扫描（生成JSON和HTML报告）
python -m contract_auditor.main examples/single_file_1.sol

# 指定输出目录
python -m contract_auditor.main examples/single_file_1.sol --output-dir ./my_reports/

# 只生成JSON报告
python -m contract_auditor.main examples/single_file_1.sol --format json

# 只生成HTML报告
python -m contract_auditor.main examples/single_file_1.sol --format html

# 只显示高危及以上问题
python -m contract_auditor.main examples/single_file_1.sol --severity high
```

**2. 扫描项目目录**

```bash
# 扫描整个项目
python -m contract_auditor.main examples/project/contracts/

# 指定输出目录
python -m contract_auditor.main examples/project/contracts/ --output-dir ./project_reports/

# 只显示严重问题
python -m contract_auditor.main examples/project/contracts/ --severity critical
```

**3. 扫描包含多个文件的目录**

```bash
# 扫描整个examples目录（包含单文件和项目）
python -m contract_auditor.main examples/ --output-dir ./all_reports/

# 工具会自动分类，分别生成报告
# 报告保存在: ./all_reports/single_files/ 和 ./all_reports/projects/
```

#### 完整操作流程示例

```bash
# 1. 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 2. 运行扫描
python -m contract_auditor.main examples/single_file_1.sol

# 3. 查看终端输出的报告路径
# 例如: 报告已保存到: examples\audit_report_20260102_170103

# 4. 打开HTML报告（Windows）
start examples\audit_report_20260102_170103\report.html

# Linux/Mac
# xdg-open examples/audit_report_20260102_170103/report.html
# open examples/audit_report_20260102_170103/report.html
```

## 输出报告位置

### 如果目录下既有单文件也有项目

工具会自动分类并分别生成报告：

```
[输出目录]/
├── single_files/      # 单文件报告
│   ├── report.html
│   └── report.json
└── projects/          # 项目报告
    ├── report.html
    └── report.json
```

**分类规则：**
- **单文件**：直接在目录下的.sol文件（如 `examples/single_file_1.sol`）
- **项目**：在 `contracts/`、`src/`、`solidity/` 等目录下的文件，或目录下有多个.sol文件

### 如果只有单文件或只有项目

**单文件扫描（未指定输出目录）：**
```
[合约文件目录]/audit_report_[时间戳]/
├── report.html
└── report.json
```

**项目扫描（未指定输出目录）：**
```
[项目根目录]/audit_reports/[时间戳]/
├── report.html
└── report.json
```

**指定输出目录：**
```
[你指定的目录]/
├── report.html
└── report.json
```

### 报告文件说明

- **report.html** - HTML可视化报告（推荐在浏览器中打开查看）
- **report.json** - JSON格式报告（结构化数据，便于程序处理）

运行工具后，终端会显示报告保存路径。

## CI 集成（GitHub Actions）

项目已配置 GitHub Actions，push 代码到 GitHub 后会自动触发扫描，报告上传到 Artifact。

### 设置CI集成

**1. 初始化Git仓库（如果还没初始化）**

```bash
git init
git add .
git commit -m "Initial commit"
```

**2. 添加远程仓库**

```bash
git remote add origin https://github.com/你的用户名/你的仓库名.git
```

**3. 推送到GitHub（会触发CI）**

```bash
# 推送到main分支
git checkout -b main
git push -u origin main

# 或推送到master分支
git checkout -b master
git push -u origin master
```

### 查看CI运行结果

#### 方法1: 在GitHub网站查看（推荐）

1. 访问你的仓库页面: `https://github.com/你的用户名/你的仓库名`
2. 点击顶部的 **"Actions"** 标签
3. 在左侧工作流列表中找到 **"智能合约安全审计"**
4. 点击查看运行记录
5. 等待运行完成（通常1-2分钟）

#### 方法2: 使用GitHub CLI查看（如果已安装）

```bash
# 查看工作流运行列表
gh run list

# 查看最新运行详情
gh run view

# 查看运行日志
gh run view --log
```

### 下载CI报告

#### 在GitHub网站下载

1. 在Actions页面，点击运行记录
2. 滚动到页面底部
3. 找到 **"Artifacts"** 部分
4. 点击 **"audit-reports"** 下载（ZIP文件）
5. 解压后查看报告文件

**报告目录结构：**

如果同时有单文件和项目：
```
audit-reports.zip (下载后解压)
├── single_files/
│   ├── report.html
│   └── report.json
└── projects/
    ├── report.html
    └── report.json
```

如果只有单文件或只有项目：
```
audit-reports.zip (下载后解压)
├── report.html
└── report.json
```

#### 使用GitHub CLI下载

```bash
# 下载最新的Artifact
gh run download --name audit-reports

# Windows查看报告
start audit-reports\report.html

# Linux查看报告
xdg-open audit-reports/report.html

# Mac查看报告
open audit-reports/report.html
```

### CI触发条件

CI会在以下情况自动触发：
- Push 到 `main`、`master` 或 `develop` 分支
- 创建 Pull Request 到 `main`、`master` 或 `develop` 分支

### CI注意事项

1. **确保工作流文件已提交**
   - 文件路径: `.github/workflows/audit.yml`
   - 如果文件不存在，CI不会运行

2. **分支名称要匹配**
   - CI会在 `main`、`master` 或 `develop` 分支触发
   - 如果推送到其他分支，需要创建PR到这些分支

3. **CI运行时间**
   - 通常需要1-2分钟
   - 可以在Actions页面实时查看进度

4. **Artifact保留时间**
   - 默认保留30天
   - 过期后需要重新运行CI才能下载

5. **报告分类**
   - 如果同时有单文件和项目，会分别生成报告
   - 下载Artifact后查看 `single_files/` 和 `projects/` 目录

## 测试示例

项目包含测试示例合约，位于 `examples/` 目录：

- **单文件示例：**
  - `examples/single_file_1.sol` - 包含重入、权限控制、未检查返回值等漏洞
  - `examples/single_file_2.sol` - 包含delegatecall和外部调用风险

- **项目示例：**
  - `examples/project/contracts/Token.sol` - 代币合约
  - `examples/project/contracts/Vault.sol` - 保险库合约

## 故障排查

### 问题1: 找不到文件

**错误**: `在 xxx 中未找到 .sol 文件`

**解决**: 检查文件路径是否正确
```bash
# 检查文件是否存在
ls examples/single_file_1.sol  # Linux/Mac
dir examples\single_file_1.sol  # Windows
```

### 问题2: 导入错误

**错误**: `ImportError: attempted relative import`

**解决**: 使用模块方式运行
```bash
# 正确方式
python -m contract_auditor.main file.sol

# 错误方式
python contract_auditor/main.py file.sol
```

### 问题3: 虚拟环境未激活

**错误**: `ModuleNotFoundError: No module named 'xxx'`

**解决**: 先激活虚拟环境
```powershell
.\.venv\Scripts\Activate.ps1
```

### 问题4: 不知道如何使用工具

**情况**: 不确定命令格式或参数用法

**解决**: 使用帮助命令查看详细说明
```bash
# 查看完整帮助信息
python -m contract_auditor.main -h

# 无参数运行查看快速提示
python -m contract_auditor.main
```

帮助信息包含：
- 所有参数和选项的详细说明
- 使用示例
- 参数的可选值

### 问题5: CI中找不到HTML模板

**错误**: `FileNotFoundError: HTML模板文件未找到`

**解决**: 
1. 确保 `contract_auditor/reporter/templates/report_template.html` 文件存在
2. 检查 `.gitignore` 是否忽略了模板文件（应该包含 `!contract_auditor/reporter/templates/*.html`）
3. 确保 `setup.py` 和 `MANIFEST.in` 正确配置了 `package_data`

## 项目结构

```
Solidity/
├── contract_auditor/          # 主包
│   ├── parser/               # 解析模块
│   ├── detectors/            # 检测器模块（5个）
│   ├── analyzer/             # 分析模块（控制流/调用图/污点/数据流）
│   ├── reporter/             # 报告生成模块
│   └── utils/               # 工具函数
├── examples/                 # 测试示例
│   ├── single_file_1.sol
│   ├── single_file_2.sol
│   └── project/
├── .github/workflows/        # CI配置
├── requirements.txt          # 依赖包
└── setup.py                  # 安装配置
```

## 依赖包

- `pygments` - 代码高亮
- `jinja2` - HTML模板引擎
- `networkx` - 图分析（调用图）
- `click` - CLI接口
- `colorama` - 终端颜色输出

## 许可证

本项目仅供学习,课程设计中CI集成测试功能。

---

**Author:** tr3
