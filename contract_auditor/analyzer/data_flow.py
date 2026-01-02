"""数据流分析"""

from typing import Dict, List, Set
from ..parser.ast_builder import AST, FunctionNode, ContractNode


class DataFlowAnalyzer:
    """数据流分析器"""
    
    def analyze(self, ast: AST) -> Dict[str, List[Dict]]:
        """
        执行数据流分析
        
        Args:
            ast: AST对象
            
        Returns:
            每个函数的数据流信息
        """
        data_flows = {}
        
        for contract in ast.contracts:
            for func in contract.functions:
                key = f"{contract.name}.{func.name}"
                data_flows[key] = self._analyze_function_data_flow(func)
        
        return data_flows
    
    def _analyze_function_data_flow(self, func: FunctionNode) -> List[Dict]:
        """分析函数的数据流"""
        flows = []
        
        # 提取变量定义和使用
        var_defs = self._extract_variable_definitions(func)
        var_uses = self._extract_variable_uses(func)
        
        # 构建定义-使用链
        for var_name, def_line in var_defs.items():
            uses = [use_line for use_var, use_line in var_uses.items() 
                   if use_var == var_name and use_line > def_line]
            
            if uses:
                flows.append({
                    "variable": var_name,
                    "definition_line": def_line,
                    "use_lines": uses
                })
        
        return flows
    
    def _extract_variable_definitions(self, func: FunctionNode) -> Dict[str, int]:
        """提取变量定义"""
        definitions = {}
        
        import re
        
        # 查找变量声明和赋值
        # 模式：类型 变量名 = 或 变量名 =
        patterns = [
            r'(uint|int|bool|address|string|bytes\d*)\s+(\w+)\s*=',
            r'(\w+)\s*=\s*[^;]+;'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, func.body, re.MULTILINE):
                var_name = match.group(2) if len(match.groups()) > 1 else match.group(1)
                line = func.line + func.body[:match.start()].count('\n')
                definitions[var_name] = line
        
        return definitions
    
    def _extract_variable_uses(self, func: FunctionNode) -> Dict[str, int]:
        """提取变量使用"""
        uses = {}
        
        import re
        
        # 查找变量使用（在赋值右侧、函数调用参数中等）
        # 简化：查找变量名出现的位置
        var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        
        for match in re.finditer(var_pattern, func.body):
            var_name = match.group(1)
            
            # 排除关键字
            keywords = ['if', 'else', 'while', 'for', 'return', 'require', 
                       'assert', 'revert', 'emit', 'function', 'contract']
            if var_name in keywords:
                continue
            
            line = func.line + func.body[:match.start()].count('\n')
            uses[var_name] = line
        
        return uses

