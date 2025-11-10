import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from .base_provider import BaseAIProvider
from .openai_provider import OpenAIProvider


class AIManager:
    """AI接口管理器"""
    
    def __init__(self, config_file: str = "ai_config.json"):
        self.config_file = Path(config_file)
        self.providers = {}
        self.current_provider = None
        self.current_provider_name = None
        
        # 注册可用的提供商
        self.available_providers = {
            "openai": OpenAIProvider,
            # 可以在这里添加其他提供商
        }
        
        # 加载配置
        self.load_config()
    
    def get_available_providers(self) -> List[Dict[str, str]]:
        """获取可用的AI提供商列表"""
        return [
            {"value": "openai", "label": "OpenAI (ChatGPT)"},
            {"value": "qianwen", "label": "通义千问", "disabled": True},
            {"value": "wenxin", "label": "文心一言", "disabled": True},
            {"value": "chatglm", "label": "ChatGLM", "disabled": True},
            {"value": "custom", "label": "自定义API", "disabled": True},
        ]
    
    def load_config(self):
        """加载AI配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 恢复提供商配置
                for provider_name, provider_config in config.get('providers', {}).items():
                    if provider_name in self.available_providers:
                        provider_class = self.available_providers[provider_name]
                        self.providers[provider_name] = provider_class(**provider_config)
                
                # 设置当前提供商
                current = config.get('current_provider')
                if current and current in self.providers:
                    self.current_provider_name = current
                    self.current_provider = self.providers[current]
                    
            except Exception as e:
                print(f"加载AI配置失败: {e}")
    
    def save_config(self):
        """保存AI配置"""
        try:
            config = {
                'current_provider': self.current_provider_name,
                'providers': {}
            }
            
            # 保存所有提供商配置
            for name, provider in self.providers.items():
                config['providers'][name] = {
                    'api_key': provider.api_key,
                    **provider.config
                }
            
            # 确保目录存在
            self.config_file.parent.mkdir(exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"保存AI配置失败: {e}")
    
    def configure_provider(self, provider_name: str, config: Dict[str, Any]):
        """配置AI提供商"""
        if provider_name not in self.available_providers:
            raise ValueError(f"不支持的提供商: {provider_name}")
        
        provider_class = self.available_providers[provider_name]
        
        try:
            # 创建提供商实例
            provider = provider_class(**config)
            
            # 验证配置
            if not provider.validate_config():
                raise ValueError("配置验证失败")
            
            # 保存提供商
            self.providers[provider_name] = provider
            
            # 自动保存配置
            self.save_config()
            
            return True
            
        except Exception as e:
            print(f"配置提供商失败: {e}")
            return False
    
    def set_current_provider(self, provider_name: str) -> bool:
        """设置当前使用的AI提供商"""
        if provider_name not in self.providers:
            print(f"提供商未配置: {provider_name}")
            return False
        
        self.current_provider_name = provider_name
        self.current_provider = self.providers[provider_name]
        
        # 保存配置
        self.save_config()
        
        return True
    
    def get_current_provider(self) -> Optional[BaseAIProvider]:
        """获取当前AI提供商"""
        return self.current_provider
    
    def test_provider_connection(self, provider_name: str) -> bool:
        """测试指定提供商的连接"""
        if provider_name not in self.providers:
            return False
        
        try:
            return self.providers[provider_name].test_connection()
        except Exception as e:
            print(f"测试连接失败: {e}")
            return False
    
    def generate_poetry(self, theme: str = "励志") -> str:
        """生成诗句"""
        if not self.current_provider:
            # 如果没有配置AI，返回默认诗句
            default_poems = [
                "道可道，非常道",
                "天行健，君子以自强不息",
                "路漫漫其修远兮，吾将上下而求索",
                "宝剑锋从磨砺出，梅花香自苦寒来",
                "山重水复疑无路，柳暗花明又一村",
                "千里之行，始于足下",
                "学而时习之，不亦说乎",
                "知之者不如好之者，好之者不如乐之者",
                "己所不欲，勿施于人",
                "工欲善其事，必先利其器"
            ]
            
            import random
            return random.choice(default_poems)
        
        try:
            return self.current_provider.generate_poetry(theme)
        except Exception as e:
            print(f"生成诗句失败: {e}")
            return "修炼之路虽艰难，持之以恒必成功"
    
    def analyze_mood_event(self, event_description: str) -> Dict[str, Any]:
        """分析心境事件影响"""
        if not self.current_provider:
            return {
                "mood_impact": 0,
                "category": "中性",
                "analysis": "请先配置AI接口以获得智能分析",
                "suggestion": "保持平和心态，专注修炼"
            }
        
        try:
            return self.current_provider.analyze_mood_event(event_description)
        except Exception as e:
            print(f"分析心境事件失败: {e}")
            return {
                "mood_impact": 0,
                "category": "中性", 
                "analysis": "AI分析暂时不可用",
                "suggestion": "请保持平静，继续修炼"
            }
    
    def get_provider_config_schema(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """获取提供商配置架构"""
        if provider_name not in self.available_providers:
            return None
        
        # 创建临时实例以获取配置架构
        provider_class = self.available_providers[provider_name]
        temp_provider = provider_class("")  # 空API key
        
        return temp_provider.get_config_schema()
    
    def get_provider_status(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """获取提供商状态"""
        if provider_name not in self.providers:
            return {
                "name": provider_name,
                "configured": False,
                "connection_status": "未配置"
            }
        
        return self.providers[provider_name].get_status()
    
    def get_all_providers_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有提供商状态"""
        status = {}
        
        for provider_info in self.get_available_providers():
            provider_name = provider_info["value"]
            if provider_info.get("disabled"):
                status[provider_name] = {
                    "name": provider_info["label"],
                    "configured": False,
                    "connection_status": "暂未支持"
                }
            else:
                status[provider_name] = self.get_provider_status(provider_name)
        
        return status
    
    def is_configured(self) -> bool:
        """检查是否已配置AI接口"""
        return self.current_provider is not None and self.current_provider.is_configured
    
    def remove_provider(self, provider_name: str):
        """移除提供商配置"""
        if provider_name in self.providers:
            del self.providers[provider_name]
            
            # 如果移除的是当前提供商，清除当前提供商
            if self.current_provider_name == provider_name:
                self.current_provider = None
                self.current_provider_name = None
            
            # 保存配置
            self.save_config()


# 全局AI管理器实例
ai_manager = AIManager() 