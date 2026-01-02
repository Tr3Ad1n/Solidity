"""Solidity源码解析器"""

import re
from typing import List, Tuple
from .ast_builder import AST, ContractNode, FunctionNode, ModifierNode, StateVariableNode, CallNode, StateChangeNode, ASTNode


class SolidityParser:
    """Solidity解析器 - 使用正则表达式和模式匹配"""
    
    def __init__(self):
        # 函数定义模式
        self.function_pattern = re.compile(
            r'(function\s+(\w+)\s*\([^)]*\)\s*(?:public|private|internal|external)?\s*(?:payable)?\s*(?:view)?\s*(?:pure)?\s*(?:returns\s*\([^)]*\))?\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})',
            re.MULTILINE | re.DOTALL
        )
        
        # 修饰符模式
        self.modifier_pattern = re.compile(
            r'modifier\s+(\w+)\s*\([^)]*\)\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
            re.MULTILINE | re.DOTALL
        )
        
        # 合约定义模式
        self.contract_pattern = re.compile(
            r'(?:contract|interface|library)\s+(\w+)\s*(?:is\s+[^{]+)?\s*\{',
            re.MULTILINE
        )
        
        # 状态变量模式
        self.state_var_pattern = re.compile(
            r'((?:public|private|internal|external)\s+)?(?:mapping|uint|int|bool|address|string|bytes)\s+(\w+)\s*[=;]',
            re.MULTILINE
        )
        
        # 外部调用模式（在_parse_calls中重新定义，这里保留用于兼容）
        self.external_call_patterns = {
            'call': re.compile(r'\.call\s*(\{[^}]*\})?\s*\(', re.MULTILINE),
            'send': re.compile(r'\.send\s*\(', re.MULTILINE),
            'transfer': re.compile(r'\.transfer\s*\(', re.MULTILINE),
            'delegatecall': re.compile(r'\.delegatecall\s*(\{[^}]*\})?\s*\(', re.MULTILINE),
            'staticcall': re.compile(r'\.staticcall\s*(\{[^}]*\})?\s*\(', re.MULTILINE),
        }
        
        # 状态修改模式
        self.state_change_pattern = re.compile(
            r'(\w+)\s*([+\-*/]?=)\s*',
            re.MULTILINE
        )
    
    def parse(self, source_code: str, file_path: str = "") -> AST:
        """
        解析Solidity源码
        
        Args:
            source_code: Solidity源码
            file_path: 文件路径
            
        Returns:
            AST对象
        """
        ast = AST(source_code=source_code, file_path=file_path)
        
        # 查找合约
        contracts = self._find_contracts(source_code)
        
        for contract_name, contract_start in contracts:
            contract = ContractNode(name=contract_name, line=self._get_line_number(source_code, contract_start))
            
            # 提取合约内容
            contract_content = self._extract_contract_content(source_code, contract_start)
            
            # 解析函数
            contract.functions = self._parse_functions(contract_content, contract_start)
            
            # 解析修饰符
            contract.modifiers = self._parse_modifiers(contract_content, contract_start)
            
            # 解析状态变量
            contract.state_variables = self._parse_state_variables(contract_content, contract_start)
            
            ast.contracts.append(contract)
        
        return ast
    
    def _find_contracts(self, source_code: str) -> List[Tuple[str, int]]:
        """查找所有合约定义"""
        contracts = []
        for match in self.contract_pattern.finditer(source_code):
            contract_name = match.group(1)
            start_pos = match.start()
            contracts.append((contract_name, start_pos))
        return contracts
    
    def _extract_contract_content(self, source_code: str, start_pos: int) -> str:
        """提取合约内容（大括号内的代码）"""
        brace_count = 0
        start_brace = source_code.find('{', start_pos)
        if start_brace == -1:
            return ""
        
        for i in range(start_brace, len(source_code)):
            if source_code[i] == '{':
                brace_count += 1
            elif source_code[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return source_code[start_brace:i+1]
        return ""
    
    def _parse_functions(self, contract_content: str, offset: int) -> List[FunctionNode]:
        """解析函数"""
        functions = []
        
        # 改进的函数匹配 - 处理嵌套大括号
        function_pattern = re.compile(
            r'function\s+(\w+)\s*\(([^)]*)\)\s*',
            re.MULTILINE
        )
        
        for match in function_pattern.finditer(contract_content):
            func_start = match.start()
            func_name = match.group(1)
            params = match.group(2) or ""
            
            # 查找函数体开始位置
            body_start = contract_content.find('{', match.end())
            if body_start == -1:
                continue
            
            # 提取函数体（处理嵌套大括号）
            body = self._extract_braced_content(contract_content, body_start)
            if not body:
                continue
            
            # 提取函数声明部分（从function到{之前）
            decl_part = contract_content[func_start:body_start]
            
            # 解析可见性和修饰符
            visibility = "public"
            is_payable = False
            is_view = False
            is_pure = False
            returns = ""
            
            if 'external' in decl_part:
                visibility = "external"
            elif 'internal' in decl_part:
                visibility = "internal"
            elif 'private' in decl_part:
                visibility = "private"
            
            if 'payable' in decl_part:
                is_payable = True
            if 'view' in decl_part:
                is_view = True
            if 'pure' in decl_part:
                is_pure = True
            
            # 提取returns
            returns_match = re.search(r'returns\s*\(([^)]*)\)', decl_part)
            if returns_match:
                returns = returns_match.group(1)
            
            # 提取修饰符
            modifiers = self._extract_modifiers_from_function(decl_part, 0)
            
            func = FunctionNode(
                name=func_name,
                visibility=visibility,
                modifiers=modifiers,
                parameters=self._parse_parameters(params),
                returns=self._parse_parameters(returns),
                body=body,
                is_payable=is_payable,
                is_view=is_view,
                is_pure=is_pure,
                line=self._get_line_number(contract_content, func_start) + self._get_line_number(contract_content[:offset], 0)
            )
            
            # 解析函数体中的调用
            func.calls = self._parse_calls(body, func.line)
            
            # 解析状态修改
            func.state_changes = self._parse_state_changes(body, func.line)
            
            functions.append(func)
        
        return functions
    
    def _extract_braced_content(self, content: str, start_pos: int) -> str:
        """提取大括号内容（处理嵌套）"""
        brace_count = 0
        start_brace = start_pos
        
        for i in range(start_brace, len(content)):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return content[start_brace:i+1]
        return ""
    
    def _extract_modifiers_from_function(self, decl_part: str, func_start: int) -> List[str]:
        """从函数定义中提取修饰符"""
        modifiers = []
        
        # 查找修饰符（在function关键字之后，大括号之前）
        # 匹配修饰符模式: modifierName 或 modifierName(...)
        modifier_pattern = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\([^)]*\))?', re.MULTILINE)
        
        # 排除关键字
        keywords = {'function', 'public', 'private', 'internal', 'external', 
                   'payable', 'view', 'pure', 'returns', 'memory', 'storage', 'calldata'}
        
        for match in modifier_pattern.finditer(decl_part):
            mod_name = match.group(1)
            # 排除可见性和关键字
            if mod_name not in keywords and mod_name not in ['uint', 'int', 'bool', 'address', 'string', 'bytes']:
                # 检查是否是常见的修饰符模式
                common_modifiers = ['onlyOwner', 'onlyRole', 'nonReentrant', 'whenNotPaused', 
                                  'onlyAdmin', 'hasRole', 'isOwner']
                if mod_name in common_modifiers or any(cm in mod_name for cm in ['only', 'non', 'when']):
                    if mod_name not in modifiers:
                        modifiers.append(mod_name)
        
        return modifiers
    
    def _parse_modifiers(self, contract_content: str, offset: int) -> List[ModifierNode]:
        """解析修饰符"""
        modifiers = []
        for match in self.modifier_pattern.finditer(contract_content):
            mod_name = match.group(1)
            mod = ModifierNode(
                name=mod_name,
                body=match.group(0),
                line=self._get_line_number(contract_content, match.start()) + self._get_line_number(contract_content[:offset], 0)
            )
            modifiers.append(mod)
        return modifiers
    
    def _parse_state_variables(self, contract_content: str, offset: int) -> List[StateVariableNode]:
        """解析状态变量"""
        variables = []
        # 简化版：查找常见的状态变量声明
        var_pattern = re.compile(
            r'(public|private|internal|external)?\s*(mapping|uint|int|bool|address|string|bytes\d*)\s+(\w+)\s*[=;]',
            re.MULTILINE
        )
        
        for match in var_pattern.finditer(contract_content):
            visibility = match.group(1) or "internal"
            var_type = match.group(2)
            var_name = match.group(3)
            
            var = StateVariableNode(
                name=var_name,
                var_type=var_type,
                visibility=visibility,
                line=self._get_line_number(contract_content, match.start()) + self._get_line_number(contract_content[:offset], 0)
            )
            variables.append(var)
        
        return variables
    
    def _parse_calls(self, body: str, base_line: int) -> List[CallNode]:
        """解析函数体中的调用"""
        calls = []
        
        # 移除外层大括号（如果存在）
        body_content = body.strip()
        if body_content.startswith('{') and body_content.endswith('}'):
            body_content = body_content[1:-1].strip()
        
        # 查找各种外部调用（改进模式以匹配 .call{value:...}() 格式）
        call_patterns = {
            'call': re.compile(r'\.call\s*(\{[^}]*\})?\s*\(', re.MULTILINE),
            'send': re.compile(r'\.send\s*\(', re.MULTILINE),
            'transfer': re.compile(r'\.transfer\s*\(', re.MULTILINE),
            'delegatecall': re.compile(r'\.delegatecall\s*(\{[^}]*\})?\s*\(', re.MULTILINE),
            'staticcall': re.compile(r'\.staticcall\s*(\{[^}]*\})?\s*\(', re.MULTILINE),
        }
        
        for call_type, pattern in call_patterns.items():
            for match in pattern.finditer(body_content):
                # 提取value参数（如果存在）
                value_match = re.search(r'value:\s*(\w+)', match.group(0) if match.groups() else '')
                value = value_match.group(1) if value_match else None
                
                call = CallNode(
                    call_type=call_type,
                    target="",
                    value=value,
                    is_low_level=(call_type in ['call', 'delegatecall', 'staticcall']),
                    line=base_line + self._get_line_number(body_content, match.start())
                )
                calls.append(call)
        
        # 查找函数调用（改进以处理 msg.sender.call 等情况）
        func_call_pattern = re.compile(r'(\w+(?:\.\w+)?)\s*(\{[^}]*\})?\s*\(', re.MULTILINE)
        for match in func_call_pattern.finditer(body_content):
            target = match.group(1)
            # 排除关键字和已处理的外部调用
            if target in ['if', 'while', 'for', 'require', 'assert', 'revert', 'emit', 'new', 'delete']:
                continue
            # 排除已处理的外部调用模式
            if any(target.endswith(f'.{ct}') for ct in ['call', 'send', 'transfer', 'delegatecall', 'staticcall']):
                continue
            
            call = CallNode(
                call_type="function_call",
                target=target,
                line=base_line + self._get_line_number(body_content, match.start())
            )
            calls.append(call)
        
        return calls
    
    def _parse_state_changes(self, body: str, base_line: int) -> List[StateChangeNode]:
        """解析状态修改"""
        changes = []
        
        # 移除外层大括号（如果存在）
        body_content = body.strip()
        if body_content.startswith('{') and body_content.endswith('}'):
            body_content = body_content[1:-1].strip()
        
        # 查找变量赋值（改进模式，支持数组索引和复合赋值）
        # 匹配: variable = ... 或 variable[xxx] = ... 或 variable += ... 等
        # 模式1: 简单变量赋值 variable = ...
        # 模式2: 数组/映射赋值 variable[key] = ...
        assignment_patterns = [
            re.compile(r'(\w+)\s*([+\-*/]?=)\s*[^;]+;', re.MULTILINE),  # 简单变量
            re.compile(r'(\w+)\s*(\[.*?\])\s*([+\-*/]?=)\s*[^;]+;', re.MULTILINE),  # 数组/映射
        ]
        
        for pattern in assignment_patterns:
            for match in pattern.finditer(body_content):
                if len(match.groups()) == 2:
                    # 简单变量
                    var_name = match.group(1)
                    operation = match.group(2)
                else:
                    # 数组/映射
                    var_name = match.group(1) + match.group(2)  # 包含索引
                    operation = match.group(3)
                
                # 排除局部变量声明（如 uint x = ...）
                if re.match(r'^(uint|int|bool|address|string|bytes|mapping|memory|storage)', var_name.split('[')[0], re.IGNORECASE):
                    continue
                
                # 排除关键字
                if var_name.split('[')[0] in ['if', 'while', 'for', 'return', 'require', 'assert']:
                    continue
                
                change = StateChangeNode(
                    variable=var_name,
                    operation=operation,
                    line=base_line + self._get_line_number(body_content, match.start())
                )
                changes.append(change)
        
        return changes
    
    def _parse_parameters(self, param_str: str) -> List[str]:
        """解析参数列表"""
        if not param_str.strip():
            return []
        params = [p.strip() for p in param_str.split(',')]
        return [p.split()[-1] if p else "" for p in params]
    
    def _get_line_number(self, text: str, position: int) -> int:
        """获取位置对应的行号"""
        return text[:position].count('\n') + 1

