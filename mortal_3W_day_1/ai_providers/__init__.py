"""
AI接口管理模块

支持多种AI平台：
- OpenAI (ChatGPT, GPT-4)
- 通义千问 (Alibaba)
- 文心一言 (Baidu)
- ChatGLM (智谱)
- 自定义API端点
"""

from .ai_manager import AIManager
from .openai_provider import OpenAIProvider
from .base_provider import BaseAIProvider

__all__ = [
    'AIManager',
    'OpenAIProvider', 
    'BaseAIProvider'
] 