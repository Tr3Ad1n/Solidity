"""风险等级定义"""

from enum import Enum


class Severity(Enum):
    """漏洞风险等级"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    
    def __str__(self):
        return self.value
    
    @classmethod
    def from_string(cls, s):
        """从字符串转换为Severity"""
        s = s.upper()
        for severity in cls:
            if severity.name == s:
                return severity
        return cls.LOW

