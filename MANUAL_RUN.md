# 手动运行审计工具指南

不使用CI集成，直接在本地手动运行命令的完整指南。

## 前置准备

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

### 2. 安装依赖（如果还没安装）

```bash
pip install -r requirements.txt
pip install -e .
```

## 基本命令

### 扫描单文件

```bash
# 基本扫描（生成JSON和HTML报告）
python -m contract_auditor.main examples/single_file_1.sol

# 只生成JSON报告
python -m contract_auditor.main examples/single_file_1.sol --format json

# 只生成HTML报告
python -m contract_auditor.main examples/single_file_1.sol --format html

# 指定输出目录
python -m contract_auditor.main examples/single_file_1.sol --output-dir ./my_reports/

# 只显示高危及以上问题
python -m contract_auditor.main examples/single_file_1.sol --severity high
```

### 扫描项目目录

```bash
# 扫描整个项目
python -m contract_auditor.main examples/project/contracts/

# 指定输出目录
python -m contract_auditor.main examples/project/contracts/ --output-dir ./project_reports/
```

## 完整操作流程

### 示例1: 扫描单个合约文件

```bash
# 1. 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 2. 运行扫描
python -m contract_auditor.main examples/single_file_1.sol

# 3. 查看输出
# 终端会显示报告保存路径，例如:
# 报告已保存到: examples\audit_report_20260102_170103

# 4. 打开报告
# Windows: start examples\audit_report_20260102_170103\report.html
# Linux: xdg-open examples/audit_report_20260102_170103/report.html
# Mac: open examples/audit_report_20260102_170103/report.html
```

### 示例2: 扫描项目并指定输出目录

```bash
# 1. 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 2. 运行扫描，指定输出目录
python -m contract_auditor.main examples/project/contracts/ --output-dir ./reports/

# 3. 查看报告
# 报告保存在: ./reports/report.html 和 report.json
```

### 示例3: 只生成JSON报告

```bash
# 1. 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 2. 只生成JSON格式
python -m contract_auditor.main examples/single_file_1.sol --format json --output-dir ./json_reports/

# 3. 查看JSON文件
# 可以用文本编辑器打开，或使用jq工具查看
```

## 命令参数说明

### 基本参数

- `输入路径` (必需): 要扫描的合约文件或目录
  ```bash
  python -m contract_auditor.main <文件或目录路径>
  ```

### 可选参数

- `--output-dir` 或 `-o`: 指定报告输出目录
  ```bash
  --output-dir ./my_reports/
  ```

- `--format` 或 `-f`: 输出格式 (json/html/both)
  ```bash
  --format json    # 只生成JSON
  --format html    # 只生成HTML
  --format both    # 生成两种格式（默认）
  ```

- `--severity` 或 `-s`: 最低风险等级过滤
  ```bash
  --severity critical  # 只显示严重问题
  --severity high      # 显示高危及以上
  --severity medium    # 显示中危及以上
  --severity low       # 显示所有问题（默认）
  ```

## 查看报告

### 报告位置

**单文件扫描:**
```
[合约文件目录]/audit_report_[时间戳]/
├── report.html
└── report.json
```

**项目扫描:**
```
[项目根目录]/audit_reports/[时间戳]/
├── report.html
└── report.json
```

**指定输出目录:**
```
[你指定的目录]/
├── report.html
└── report.json
```

### 打开报告

**Windows:**
```powershell
# 打开HTML报告
start report.html

# 或指定完整路径
start examples\audit_report_20260102_170103\report.html
```

**Linux:**
```bash
xdg-open report.html
```

**Mac:**
```bash
open report.html
```

## 常用命令组合

### 快速扫描并查看

```bash
# 扫描并立即打开报告（Windows）
python -m contract_auditor.main examples/single_file_1.sol --output-dir ./temp_report/ && start ./temp_report/report.html
```

### 批量扫描多个文件

```bash
# 扫描examples目录下的所有.sol文件
python -m contract_auditor.main examples/ --output-dir ./all_reports/
```

### 只查看高危问题

```bash
# 只显示高危和严重问题
python -m contract_auditor.main examples/single_file_1.sol --severity high
```

## 输出说明

运行命令后，终端会显示：

```
============================================================
  智能合约安全审计工具
============================================================

正在查找 Solidity 文件...
找到 1 个 Solidity 文件
输出目录: examples\audit_report_20260102_170103

正在解析合约...
  解析: examples\single_file_1.sol

正在执行安全检测...
  ReentrancyDetector: 发现 1 个问题
  AccessControlDetector: 发现 3 个问题
  ExternalCallDetector: 发现 2 个问题
  UncheckedReturnDetector: 发现 2 个问题

正在执行分析...
  调用图: 7 个节点
  污点分析: 发现 7 条传播路径
  控制流分析: 分析了 4 个函数
  数据流分析: 分析了 4 个函数

正在生成报告...
  JSON报告: examples\audit_report_20260102_170103\report.json
  HTML报告: examples\audit_report_20260102_170103\report.html

============================================================
  检测完成
============================================================

总计发现: 8 个问题
  Critical: 0
  High: 3
  Medium: 5
  Low: 0

报告已保存到: examples\audit_report_20260102_170103
```

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

## 完整示例

```bash
# 1. 进入项目目录
cd C:\Users\TiAmo\Desktop\Solidity

# 2. 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 3. 扫描示例文件1
python -m contract_auditor.main examples/single_file_1.sol

# 4. 查看终端输出的报告路径
# 例如: 报告已保存到: examples\audit_report_20260102_170103

# 5. 打开HTML报告
start examples\audit_report_20260102_170103\report.html

# 6. 或者扫描项目
python -m contract_auditor.main examples/project/contracts/ --output-dir ./project_reports/

# 7. 打开项目报告
start .\project_reports\report.html
```

