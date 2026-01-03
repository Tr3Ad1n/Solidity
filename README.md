# 智能合约安全审计工具

一个面向 Solidity 智能合约的静态安全审计工具，支持漏洞检测、数据流分析和可视化报告生成。

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

### 报告生成
- JSON 格式报告
- HTML 可视化报告（带交互式界面）

### CI 集成
- GitHub Actions 自动扫描
- 报告上传到 Artifact

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

### 手动运行（推荐）

**1. 激活虚拟环境**

Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

Windows (CMD):
```cmd
.venv\Scripts\activate.bat
```

Linux/Mac:
```bash
source .venv/bin/activate
```

**2. 运行扫描命令**

```bash
# 扫描单文件
python -m contract_auditor.main examples/single_file_1.sol

# 扫描项目目录
python -m contract_auditor.main examples/project/contracts/

# 指定输出目录
python -m contract_auditor.main contract.sol --output-dir ./reports/

# 只生成JSON报告
python -m contract_auditor.main contract.sol --format json

# 只显示高危问题
python -m contract_auditor.main contract.sol --severity high
```

详细命令说明请查看 [MANUAL_RUN.md](MANUAL_RUN.md)

**重要提示：**
- ✅ 正确方式：`python -m contract_auditor.main [文件]`
- ❌ 错误方式：`python contract_auditor/main.py [文件]` （会导致导入错误）

### 选项说明
- `--output-dir`: 指定报告输出目录（默认：合约文件目录或项目根目录）
- `--format`: 输出格式 (json/html/both，默认：both)
- `--severity`: 最低风险等级过滤 (critical/high/medium/low)

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
- **单文件**：直接在目录下的.sol文件
- **项目**：在 `contracts/`、`src/`、`solidity/` 等目录下的文件

### 如果只有单文件或只有项目

**单文件扫描：**
```
[合约文件目录]/audit_report_[时间戳]/
├── report.html
└── report.json
```

**项目扫描：**
```
[项目根目录]/audit_reports/[时间戳]/
├── report.html
└── report.json
```

### 指定输出目录

使用 `--output-dir` 参数指定自定义目录：

```bash
python -m contract_auditor.main examples/ --output-dir ./reports/
# 如果同时有单文件和项目，报告保存在:
# ./reports/single_files/ 和 ./reports/projects/
```

### 报告文件

- **report.html** - 交互式HTML报告（推荐在浏览器中打开查看）
- **report.json** - JSON格式报告（结构化数据）

运行工具后，终端会显示报告保存路径。

## CI 集成

项目包含 GitHub Actions 配置，push 代码后自动触发扫描，报告上传到 Artifact。

### 测试CI集成

**快速开始（手动命令）:**

```bash
# 1. 初始化Git（如果还没初始化）
git init
git add .
git commit -m "Initial commit"

# 2. 添加远程仓库
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 3. 推送到GitHub（会触发CI）
git checkout -b main
git push -u origin main

# 4. 在GitHub网站查看结果
# 访问: https://github.com/你的用户名/你的仓库名/actions
```

**查看CI运行结果:**
- 在GitHub仓库页面点击 **"Actions"** 标签
- 找到 **"智能合约安全审计"** 工作流
- 点击运行记录查看详情
- 在 **"Artifacts"** 部分下载报告

详细步骤请查看 [CI_QUICK_START.md](CI_QUICK_START.md)

## 测试示例

查看 `examples/` 目录中的示例合约。

