"""检测器基类"""

from abc import ABC, abstractmethod
from typing import List, Dict
from ..parser.ast_builder import AST
from ..utils.severity import Severity


class Issue:
    """漏洞问题"""
    def __init__(self, issue_type: str, severity: Severity, file_path: str, 
                 line: int, function: str = "", description: str = "", 
                 recommendation: str = ""):
        self.type = issue_type
        self.severity = severity
        self.file_path = file_path
        self.line = line
        self.function = function
        self.description = description
        self.recommendation = recommendation
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "type": self.type,
            "severity": str(self.severity),
            "file": self.file_path,
            "line": self.line,
            "function": self.function,
            "description": self.description,
            "recommendation": self.recommendation
        }


class BaseDetector(ABC):
    """检测器基类"""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    def detect(self, ast: AST) -> List[Issue]:
        """
        检测漏洞
        
        Args:
            ast: AST对象
            
        Returns:
            漏洞列表
        """
        pass

