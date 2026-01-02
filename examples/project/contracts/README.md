# 项目示例

这是一个包含多个合约的项目示例，用于测试审计工具的项目扫描功能。

## 合约说明

- `Token.sol`: ERC20风格的代币合约，包含权限控制问题
- `Vault.sol`: 保险库合约，包含重入攻击和外部调用风险

## 使用方法

```bash
# 扫描整个项目
python -m contract_auditor.main examples/project/contracts/
```

