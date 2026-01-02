# CI集成快速指南

## 前提条件

1. 在GitHub上创建仓库
2. 确保 `.github/workflows/audit.yml` 文件存在

## 执行步骤

### 1. 初始化Git仓库（如果还没初始化）

```bash
git init
git add .
git commit -m "Initial commit"
```

### 2. 添加远程仓库

```bash
git remote add origin https://github.com/你的用户名/你的仓库名.git
```

### 3. 推送到GitHub

```bash
# 推送到main分支（会触发CI）
git checkout -b main
git push -u origin main

# 或推送到master分支
git checkout -b master
git push -u origin master
```

## 查看CI运行结果

### 方法1: 在GitHub网站查看

1. 访问你的仓库页面: `https://github.com/你的用户名/你的仓库名`
2. 点击顶部的 **"Actions"** 标签
3. 在左侧工作流列表中找到 **"智能合约安全审计"**
4. 点击查看运行记录
5. 等待运行完成（通常1-2分钟）

### 方法2: 使用GitHub CLI查看（如果已安装）

```bash
# 查看工作流运行列表
gh run list

# 查看最新运行详情
gh run view

# 查看运行日志
gh run view --log
```

## 下载报告

### 在GitHub网站下载

1. 在Actions页面，点击运行记录
2. 滚动到页面底部
3. 找到 **"Artifacts"** 部分
4. 点击 **"audit-reports"** 下载
5. 解压后查看 `report.html` 和 `report.json`

### 使用GitHub CLI下载

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

## 完整命令示例

```bash
# 1. 进入项目目录
cd C:\Users\TiAmo\Desktop\Solidity

# 2. 初始化Git（如果还没初始化）
git init
git add .
git commit -m "Initial commit"

# 3. 添加远程仓库（替换为你的实际仓库地址）
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 4. 推送到GitHub
git checkout -b main
git push -u origin main

# 5. 然后去GitHub网站查看
# 访问: https://github.com/你的用户名/你的仓库名/actions
```

## 注意事项

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

