# 使用说明

## 安装依赖

```bash
pip install -r requirements.txt
pip install -e .
```

## 使用方法

### 激活虚拟环境

**注意：使用前请先激活虚拟环境！**

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

### 1. 扫描单文件

```bash
# 扫描单个合约文件
python -m contract_auditor.main examples/single_file_1.sol

# 指定输出目录
python -m contract_auditor.main examples/single_file_1.sol --output-dir ./reports/
```

### 2. 扫描项目目录

```bash
# 扫描整个项目
python -m contract_auditor.main examples/project/contracts/

# 只生成JSON报告
python -m contract_auditor.main examples/project/contracts/ --format json

# 只生成HTML报告
python -m contract_auditor.main examples/project/contracts/ --format html
```

### 3. 过滤风险等级

```bash
# 只显示高危及以上问题
python -m contract_auditor.main contract.sol --severity high
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
- **项目**：在 `contracts/`、`src/`、`solidity/` 等目录下的文件

**示例：**
```bash
python -m contract_auditor.main examples/ --output-dir ./reports/
# 报告保存在:
# ./reports/single_files/report.html 和 report.json
# ./reports/projects/report.html 和 report.json
```

### 如果只有单文件或只有项目

**1. 如果指定了 `--output-dir` 参数**
```
[你指定的目录]/
├── report.html
└── report.json
```

**2. 如果扫描单文件（未指定输出目录）**
```
[合约文件所在目录]/audit_report_[时间戳]/
├── report.html
└── report.json
```

**3. 如果扫描项目目录（未指定输出目录）**
```
[项目根目录]/audit_reports/[时间戳]/
├── report.html
└── report.json
```

### 报告文件说明

- **report.html** - 交互式HTML报告（可视化界面，推荐查看）
- **report.json** - JSON格式报告（结构化数据，便于程序处理）

### 查看报告

运行工具后，会在终端显示报告保存路径，例如：
```
报告已保存到: examples\audit_report_20260102_170103
```

然后可以直接打开 `report.html` 文件在浏览器中查看。

### 清理旧报告

每次运行扫描都会生成新的报告文件夹（带时间戳）。如果报告文件夹太多，可以手动删除不需要的报告文件夹。报告文件夹已添加到 `.gitignore`，不会被提交到Git仓库。

## CI集成

项目已配置GitHub Actions，push代码到GitHub后会自动触发扫描，报告会上传到Artifact。

## 检测的漏洞类型

1. **重入攻击 (Reentrancy)** - 外部调用后修改状态
2. **权限控制缺失 (Access Control)** - 关键函数缺少访问控制
3. **外部调用风险 (External Call)** - 低级别调用未检查返回值
4. **未检查返回值 (Unchecked Return)** - send/call返回值未检查
5. **危险的delegatecall (Dangerous Delegatecall)** - delegatecall使用风险

## 分析功能

- **调用图分析**: 构建函数调用关系图
- **污点分析**: 追踪外部输入到危险操作的路径
- **控制流分析**: 分析函数内的控制流

