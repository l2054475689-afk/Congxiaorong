import requests
import json
from typing import Dict, Any, Optional
from .base_provider import BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    """OpenAI接口提供商"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get('base_url', 'https://api.openai.com/v1')
        self.model = kwargs.get('model', 'gpt-3.5-turbo')
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 150)
        self.timeout = kwargs.get('timeout', 30)
    
    def get_provider_name(self) -> str:
        """获取提供商名称"""
        return "OpenAI"
    
    def get_config_schema(self) -> Dict[str, Any]:
        """获取配置架构"""
        schema = super().get_config_schema()
        schema.update({
            "base_url": {
                "type": "string",
                "required": False,
                "label": "API地址",
                "placeholder": "https://api.openai.com/v1",
                "default": "https://api.openai.com/v1"
            },
            "model": {
                "type": "select",
                "required": False,
                "label": "模型选择",
                "default": "gpt-3.5-turbo",
                "options": [
                    {"value": "gpt-3.5-turbo", "label": "GPT-3.5 Turbo"},
                    {"value": "gpt-4", "label": "GPT-4"},
                    {"value": "gpt-4-turbo", "label": "GPT-4 Turbo"},
                ]
            },
            "temperature": {
                "type": "number",
                "required": False,
                "label": "创造性",
                "default": 0.7,
                "min": 0,
                "max": 2,
                "step": 0.1
            }
        })
        return schema
    
    def _make_request(self, messages: list, **kwargs) -> Optional[str]:
        """发送API请求"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model,
            'messages': messages,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            **kwargs
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                print(f"OpenAI API错误: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            print(f"请求错误: {e}")
            return None
        except KeyError as e:
            print(f"响应格式错误: {e}")
            return None
        except Exception as e:
            print(f"未知错误: {e}")
            return None
    
    def test_connection(self) -> bool:
        """测试API连接"""
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        
        result = self._make_request(messages, max_tokens=10)
        return result is not None
    
    def generate_poetry(self, theme: str = "励志") -> str:
        """生成诗句"""
        prompts = {
            "励志": "请生成一句简短的励志诗句或名言，要求积极向上，鼓舞人心，适合修仙主题。不要超过20个字。",
            "修仙": "请生成一句关于修仙、修炼、成长的诗句，要有古典韵味，不要超过20个字。",
            "生活": "请生成一句关于生活感悟的诗句，要有哲理性，不要超过20个字。",
            "成长": "请生成一句关于个人成长、自我提升的诗句，要积极正面，不要超过20个字。"
        }
        
        prompt = prompts.get(theme, prompts["励志"])
        
        messages = [
            {"role": "system", "content": "你是一位智慧的修仙导师，擅长创作富有哲理的诗句和名言。"},
            {"role": "user", "content": prompt}
        ]
        
        result = self._make_request(messages, max_tokens=100)
        
        if result:
            # 清理返回的诗句，去除多余的标点和说明
            poetry = result.replace('"', '').replace('"', '').replace('"', '')
            poetry = poetry.replace('。', '').replace('，', ' ')
            poetry = poetry.strip()
            
            # 如果太长，取前20个字
            if len(poetry) > 20:
                poetry = poetry[:20] + "..."
            
            return poetry
        
        # 如果API调用失败，返回默认诗句
        default_poems = [
            "道可道，非常道",
            "天行健，君子以自强不息",
            "路漫漫其修远兮，吾将上下而求索",
            "宝剑锋从磨砺出，梅花香自苦寒来",
            "山重水复疑无路，柳暗花明又一村"
        ]
        
        import random
        return random.choice(default_poems)
    
    def analyze_mood_event(self, event_description: str) -> Dict[str, Any]:
        """分析心境事件影响"""
        prompt = f"""
请分析以下事件对心境的影响，并给出建议：

事件描述：{event_description}

请按以下格式返回JSON：
{{
    "mood_impact": 影响分数（-10到+10的整数），
    "category": "正面" 或 "负面" 或 "中性",
    "analysis": "简短的分析说明",
    "suggestion": "建议"
}}

注意：只返回JSON格式，不要其他文字。
"""
        
        messages = [
            {"role": "system", "content": "你是一位心理分析师，擅长分析事件对情绪的影响。"},
            {"role": "user", "content": prompt}
        ]
        
        result = self._make_request(messages, max_tokens=200)
        
        if result:
            try:
                # 尝试解析JSON
                analysis = json.loads(result)
                
                # 验证返回格式
                if all(key in analysis for key in ['mood_impact', 'category', 'analysis', 'suggestion']):
                    # 确保mood_impact在合理范围内
                    analysis['mood_impact'] = max(-10, min(10, int(analysis['mood_impact'])))
                    return analysis
            except (json.JSONDecodeError, ValueError, KeyError):
                pass
        
        # 如果解析失败，返回默认分析
        return {
            "mood_impact": 0,
            "category": "中性",
            "analysis": "暂时无法分析此事件的具体影响",
            "suggestion": "请保持平和心态，专注当下的修炼"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """获取提供商状态"""
        status = super().get_status()
        
        if self.is_configured:
            try:
                connection_ok = self.test_connection()
                status["connection_status"] = "正常" if connection_ok else "连接失败"
            except:
                status["connection_status"] = "连接异常"
        else:
            status["connection_status"] = "未配置"
        
        status.update({
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature
        })
        
        return status 