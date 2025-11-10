import json
import random
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional
from ai_providers.ai_manager import ai_manager


class PoetrySystem:
    """诗句管理系统"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.poetry_file = Path("assets/poetry_library.json")
        self.daily_log_file = Path("daily_poetry_log.json")
        
        # 内置诗句库
        self.default_poetry = [
            {"text": "道可道，非常道", "author": "老子", "category": "哲理", "source": "内置"},
            {"text": "天行健，君子以自强不息", "author": "周易", "category": "励志", "source": "内置"},
            {"text": "路漫漫其修远兮，吾将上下而求索", "author": "屈原", "category": "励志", "source": "内置"},
            {"text": "宝剑锋从磨砺出，梅花香自苦寒来", "author": "未详", "category": "励志", "source": "内置"},
            {"text": "山重水复疑无路，柳暗花明又一村", "author": "陆游", "category": "励志", "source": "内置"},
            {"text": "千里之行，始于足下", "author": "老子", "category": "励志", "source": "内置"},
            {"text": "学而时习之，不亦说乎", "author": "孔子", "category": "学习", "source": "内置"},
            {"text": "知之者不如好之者，好之者不如乐之者", "author": "孔子", "category": "学习", "source": "内置"},
            {"text": "己所不欲，勿施于人", "author": "孔子", "category": "哲理", "source": "内置"},
            {"text": "工欲善其事，必先利其器", "author": "孔子", "category": "励志", "source": "内置"},
            {"text": "业精于勤，荒于嬉", "author": "韩愈", "category": "励志", "source": "内置"},
            {"text": "读书破万卷，下笔如有神", "author": "杜甫", "category": "学习", "source": "内置"},
            {"text": "纸上得来终觉浅，绝知此事要躬行", "author": "陆游", "category": "实践", "source": "内置"},
            {"text": "落红不是无情物，化作春泥更护花", "author": "龚自珍", "category": "奉献", "source": "内置"},
            {"text": "长风破浪会有时，直挂云帆济沧海", "author": "李白", "category": "励志", "source": "内置"},
            {"text": "天生我材必有用，千金散尽还复来", "author": "李白", "category": "自信", "source": "内置"},
            {"text": "山不厌高，海不厌深", "author": "曹操", "category": "胸怀", "source": "内置"},
            {"text": "静以修身，俭以养德", "author": "诸葛亮", "category": "修养", "source": "内置"},
            {"text": "非淡泊无以明志，非宁静无以致远", "author": "诸葛亮", "category": "修养", "source": "内置"},
            {"text": "博学之，审问之，慎思之，明辨之，笃行之", "author": "中庸", "category": "学习", "source": "内置"},
        ]
        
        # 加载诗句库
        self.poetry_library = self.load_poetry_library()
        
        # 加载每日记录
        self.daily_log = self.load_daily_log()
    
    def load_poetry_library(self) -> List[Dict[str, Any]]:
        """加载诗句库"""
        if self.poetry_file.exists():
            try:
                with open(self.poetry_file, 'r', encoding='utf-8') as f:
                    custom_poetry = json.load(f)
                
                # 合并内置诗句和自定义诗句
                all_poetry = self.default_poetry.copy()
                all_poetry.extend(custom_poetry)
                
                return all_poetry
                
            except Exception as e:
                print(f"加载诗句库失败: {e}")
        
        return self.default_poetry.copy()
    
    def save_poetry_library(self):
        """保存诗句库"""
        try:
            # 只保存自定义诗句
            custom_poetry = [p for p in self.poetry_library if p.get('source') != '内置']
            
            # 确保目录存在
            self.poetry_file.parent.mkdir(exist_ok=True)
            
            with open(self.poetry_file, 'w', encoding='utf-8') as f:
                json.dump(custom_poetry, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"保存诗句库失败: {e}")
    
    def load_daily_log(self) -> Dict[str, Any]:
        """加载每日记录"""
        if self.daily_log_file.exists():
            try:
                with open(self.daily_log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载每日记录失败: {e}")
        
        return {}
    
    def save_daily_log(self):
        """保存每日记录"""
        try:
            with open(self.daily_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.daily_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存每日记录失败: {e}")
    
    def add_custom_poetry(self, text: str, author: str = "", category: str = "自定义") -> bool:
        """添加自定义诗句"""
        if not text.strip():
            return False
        
        # 检查是否重复
        for poetry in self.poetry_library:
            if poetry['text'] == text.strip():
                return False
        
        new_poetry = {
            "text": text.strip(),
            "author": author.strip() or "未知",
            "category": category,
            "source": "自定义",
            "added_date": datetime.now().isoformat()
        }
        
        self.poetry_library.append(new_poetry)
        self.save_poetry_library()
        
        return True
    
    def remove_custom_poetry(self, text: str) -> bool:
        """移除自定义诗句"""
        for i, poetry in enumerate(self.poetry_library):
            if poetry['text'] == text and poetry.get('source') == '自定义':
                del self.poetry_library[i]
                self.save_poetry_library()
                return True
        
        return False
    
    def get_poetry_by_category(self, category: str = None) -> List[Dict[str, Any]]:
        """按分类获取诗句"""
        if category is None:
            return self.poetry_library
        
        return [p for p in self.poetry_library if p.get('category') == category]
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        categories = set()
        for poetry in self.poetry_library:
            categories.add(poetry.get('category', '其他'))
        
        return sorted(list(categories))
    
    def get_random_poetry(self, category: str = None) -> Dict[str, Any]:
        """获取随机诗句"""
        poetry_list = self.get_poetry_by_category(category)
        
        if not poetry_list:
            # 如果指定分类没有诗句，返回所有诗句中的随机一句
            poetry_list = self.poetry_library
        
        if poetry_list:
            return random.choice(poetry_list)
        
        # 如果诗句库为空，返回默认诗句
        return self.default_poetry[0]
    
    def should_show_daily_poetry(self) -> bool:
        """检查是否应该显示每日诗句"""
        today = date.today().isoformat()
        
        # 检查今天是否已经显示过
        if today in self.daily_log:
            return False
        
        return True
    
    def mark_daily_poetry_shown(self, poetry: Dict[str, Any]):
        """标记今日诗句已显示"""
        today = date.today().isoformat()
        
        self.daily_log[today] = {
            "poetry": poetry,
            "shown_at": datetime.now().isoformat(),
            "ai_generated": poetry.get('source') == 'AI生成'
        }
        
        # 清理30天前的记录
        self.cleanup_old_logs()
        
        self.save_daily_log()
    
    def cleanup_old_logs(self):
        """清理30天前的记录"""
        from datetime import timedelta
        
        cutoff_date = date.today() - timedelta(days=30)
        cutoff_str = cutoff_date.isoformat()
        
        # 移除30天前的记录
        keys_to_remove = [key for key in self.daily_log.keys() if key < cutoff_str]
        for key in keys_to_remove:
            del self.daily_log[key]
    
    def get_daily_poetry(self) -> Dict[str, Any]:
        """获取今日诗句"""
        # 优先尝试从AI生成
        ai_poetry = self.generate_ai_poetry()
        if ai_poetry:
            return ai_poetry
        
        # 如果AI不可用，从库中随机选择
        return self.get_random_poetry("励志")
    
    def generate_ai_poetry(self) -> Optional[Dict[str, Any]]:
        """使用AI生成诗句"""
        if not ai_manager.is_configured():
            return None
        
        try:
            # 随机选择主题
            themes = ["励志", "修仙", "生活", "成长"]
            theme = random.choice(themes)
            
            poetry_text = ai_manager.generate_poetry(theme)
            
            if poetry_text:
                return {
                    "text": poetry_text,
                    "author": "AI智慧导师",
                    "category": theme,
                    "source": "AI生成",
                    "generated_at": datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"AI生成诗句失败: {e}")
        
        return None
    
    def get_today_poetry_log(self) -> Optional[Dict[str, Any]]:
        """获取今日诗句记录"""
        today = date.today().isoformat()
        return self.daily_log.get(today)
    
    def get_poetry_statistics(self) -> Dict[str, Any]:
        """获取诗句统计信息"""
        total_count = len(self.poetry_library)
        custom_count = len([p for p in self.poetry_library if p.get('source') == '自定义'])
        builtin_count = len([p for p in self.poetry_library if p.get('source') == '内置'])
        
        categories = {}
        for poetry in self.poetry_library:
            category = poetry.get('category', '其他')
            categories[category] = categories.get(category, 0) + 1
        
        # 统计最近30天的显示记录
        recent_logs = []
        for log_date, log_data in self.daily_log.items():
            try:
                log_date_obj = datetime.fromisoformat(log_date).date()
                if (date.today() - log_date_obj).days <= 30:
                    recent_logs.append(log_data)
            except:
                pass
        
        ai_generated_count = len([log for log in recent_logs if log.get('ai_generated')])
        
        return {
            "total_poetry": total_count,
            "custom_poetry": custom_count,
            "builtin_poetry": builtin_count,
            "categories": categories,
            "recent_30_days": len(recent_logs),
            "ai_generated_recent": ai_generated_count,
            "last_shown": self.get_today_poetry_log()
        }
    
    def search_poetry(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索诗句"""
        if not keyword.strip():
            return self.poetry_library
        
        keyword = keyword.lower()
        results = []
        
        for poetry in self.poetry_library:
            if (keyword in poetry['text'].lower() or 
                keyword in poetry.get('author', '').lower() or
                keyword in poetry.get('category', '').lower()):
                results.append(poetry)
        
        return results
    
    def export_poetry_library(self) -> str:
        """导出诗句库"""
        export_data = {
            "export_date": datetime.now().isoformat(),
            "poetry_count": len(self.poetry_library),
            "poetry_library": self.poetry_library,
            "statistics": self.get_poetry_statistics()
        }
        
        export_path = Path("exports") / f"poetry_library_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        export_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return str(export_path)
            
        except Exception as e:
            print(f"导出诗句库失败: {e}")
            return ""
    
    def import_poetry_library(self, file_path: str) -> bool:
        """导入诗句库"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if 'poetry_library' in import_data:
                imported_poetry = import_data['poetry_library']
                
                # 只导入自定义诗句，避免重复内置诗句
                new_count = 0
                for poetry in imported_poetry:
                    if poetry.get('source') != '内置':
                        # 检查是否重复
                        if not any(p['text'] == poetry['text'] for p in self.poetry_library):
                            poetry['source'] = '导入'
                            poetry['imported_at'] = datetime.now().isoformat()
                            self.poetry_library.append(poetry)
                            new_count += 1
                
                if new_count > 0:
                    self.save_poetry_library()
                    return True
            
            return False
            
        except Exception as e:
            print(f"导入诗句库失败: {e}")
            return False 