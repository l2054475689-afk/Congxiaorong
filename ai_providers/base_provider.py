from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json


class BaseAIProvider(ABC):
    """AI提供商基类"""
    
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs
        self.is_configured = bool(api_key)
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """获取提供商名称"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """测试API连接"""
        pass
    
    @abstractmethod
    def generate_poetry(self, theme: str = "励志") -> str:
        """生成诗句"""
        pass
    
    @abstractmethod
    def analyze_mood_event(self, event_description: str) -> Dict[str, Any]:
        """分析心境事件影响"""
        pass
    
    def get_config_schema(self) -> Dict[str, Any]:
        """获取配置架构"""
        return {
            "api_key": {
                "type": "string",
                "required": True,
                "label": "API密钥",
                "placeholder": "请输入API密钥"
            }
        }
    
    def validate_config(self) -> bool:
        """验证配置"""
        return bool(self.api_key)
    
    def get_status(self) -> Dict[str, Any]:
        """获取提供商状态"""
        return {
            "name": self.get_provider_name(),
            "configured": self.is_configured,
            "api_key_masked": f"***{self.api_key[-4:]}" if self.api_key and len(self.api_key) > 4 else "未配置",
            "connection_status": "未知"
        } 