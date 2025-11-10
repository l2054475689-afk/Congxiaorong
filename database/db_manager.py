import sqlite3
import json
from datetime import datetime, date
from typing import List, Optional
from pathlib import Path
import os

from database.models import Task, UserData, TaskRecord, FamilyMember, FamilyEvent, Friend, FriendRelation, FriendTask, InteractionRecord
from config import DB_PATH, GameConfig

class DatabaseManager:
    """数据库管理器 - 性能优化版"""

    def __init__(self, db_path: str = None):
        # 使用绝对路径，确保有写权限的目录
        if db_path is None:
            # 使用用户主目录或应用数据目录
            if os.name == 'nt':  # Windows
                app_data = os.path.expanduser('~\\AppData\\Local\\FanRenXiuXian')
            else:  # Linux/Mac
                app_data = os.path.expanduser('~/.fanrenxiuxian')

            # 创建目录如果不存在
            os.makedirs(app_data, exist_ok=True)
            self.db_path = os.path.join(app_data, 'immortal_cultivation.db')
        else:
            self.db_path = db_path

        print(f"数据库路径: {self.db_path}")

        # 数据缓存
        self._cache = {}
        self._cache_timeout = {}

        # 检查并设置文件权限
        self._check_permissions()
        self.init_database()
        self._optimize_database()
    
    def _check_permissions(self):
        """检查并设置数据库文件权限"""
        if os.path.exists(self.db_path):
            try:
                # 尝试设置文件为可写
                os.chmod(self.db_path, 0o666)
            except:
                pass
    
    def _optimize_database(self):
        """优化数据库性能设置"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 启用WAL模式，提高并发性能
            cursor.execute('PRAGMA journal_mode=WAL')

            # 优化性能参数
            cursor.execute('PRAGMA synchronous=NORMAL')  # 平衡性能和安全
            cursor.execute('PRAGMA cache_size=-64000')   # 64MB缓存
            cursor.execute('PRAGMA temp_store=MEMORY')   # 临时表存内存
            cursor.execute('PRAGMA mmap_size=268435456') # 256MB内存映射

            conn.commit()
            conn.close()
            print("数据库性能优化完成")
        except Exception as e:
            print(f"数据库优化警告: {e}")

    def _get_cache(self, key: str, timeout: int = 5):
        """获取缓存数据"""
        import time
        if key in self._cache:
            # 检查缓存是否过期
            if key in self._cache_timeout:
                if time.time() - self._cache_timeout[key] < timeout:
                    return self._cache[key]
        return None

    def _set_cache(self, key: str, value):
        """设置缓存数据"""
        import time
        self._cache[key] = value
        self._cache_timeout[key] = time.time()

    def _clear_cache(self, pattern: str = None):
        """清除缓存"""
        if pattern:
            keys_to_delete = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self._cache[key]
                if key in self._cache_timeout:
                    del self._cache_timeout[key]
        else:
            self._cache.clear()
            self._cache_timeout.clear()

    def _get_connection(self):
        """获取数据库连接，统一处理连接参数"""
        conn = sqlite3.connect(
            self.db_path,
            timeout=10.0,  # 增加超时时间
            check_same_thread=False,  # 允许多线程访问
            isolation_level=None  # 自动提交模式，提升性能
        )
        # 设置WAL模式，提高并发性能
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA synchronous=NORMAL')
        return conn
    
    def init_database(self):
        """初始化数据库表结构"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 用户配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_config (
                    id INTEGER PRIMARY KEY,
                    birth_year INTEGER NOT NULL,
                    initial_blood INTEGER NOT NULL,
                    current_blood INTEGER NOT NULL,
                    current_spirit INTEGER DEFAULT 0,
                    current_money INTEGER DEFAULT 0,
                    target_money INTEGER DEFAULT 5000000,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 任务表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    spirit_effect INTEGER DEFAULT 0,
                    blood_effect INTEGER DEFAULT 0,
                    frequency TEXT DEFAULT 'daily',
                    status INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 任务记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    spirit_change INTEGER,
                    blood_change INTEGER,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                )
            ''')
            
            # 财务记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS finance_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    amount DECIMAL NOT NULL,
                    category TEXT,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 技能进度表（已废弃，使用新的境界表）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS skill_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_name TEXT NOT NULL,
                    parent_id INTEGER,
                    total_nodes INTEGER DEFAULT 0,
                    completed_nodes INTEGER DEFAULT 0,
                    realm_level TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 境界表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS realms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    order_index INTEGER NOT NULL,
                    completed BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 功法/秘术/副本表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    realm_id INTEGER,
                    skill_type TEXT NOT NULL CHECK(skill_type IN ('gongfa', 'secret_art', 'fuben')),
                    nodes_json TEXT NOT NULL,
                    completed_json TEXT DEFAULT '[]',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (realm_id) REFERENCES realms(id)
                )
            ''')
            
            # 境界系统配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jingjie_config (
                    id INTEGER PRIMARY KEY,
                    current_realm_index INTEGER DEFAULT 0,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 负债表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS debts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    monthly_payment DECIMAL NOT NULL,
                    remaining_months INTEGER NOT NULL,
                    total_amount DECIMAL NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status INTEGER DEFAULT 1
                )
            ''')
            
            # 资产表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    monthly_income DECIMAL NOT NULL,
                    duration_months INTEGER NOT NULL,
                    total_value DECIMAL NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status INTEGER DEFAULT 1
                )
            ''')
            
            # 固定收支项表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fixed_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                    amount DECIMAL NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status INTEGER DEFAULT 1
                )
            ''')
            
            # 统御系统 - 家族成员表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS family_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    birthday TEXT NOT NULL,
                    phone TEXT,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 统御系统 - 家族事件表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS family_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id INTEGER NOT NULL,
                    event_name TEXT NOT NULL,
                    event_date TEXT NOT NULL,
                    completed BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (member_id) REFERENCES family_members(id)
                )
            ''')
            
            # 统御系统 - 朋友表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS friends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    personality TEXT,
                    hobbies TEXT,
                    notes TEXT,
                    last_contact TEXT,
                    is_close_friend BOOLEAN DEFAULT FALSE,
                    ai_analysis TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 统御系统 - 朋友关系表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS friend_relations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    friend_id INTEGER NOT NULL,
                    related_friend_id INTEGER NOT NULL,
                    relation_type TEXT DEFAULT 'acquaintance',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (friend_id) REFERENCES friends(id),
                    FOREIGN KEY (related_friend_id) REFERENCES friends(id)
                )
            ''')
            
            # 统御系统 - 朋友交互任务表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS friend_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    friend_id INTEGER NOT NULL,
                    task_name TEXT NOT NULL,
                    reward_type TEXT NOT NULL CHECK(reward_type IN ('spirit', 'blood', 'money')),
                    reward_amount INTEGER NOT NULL,
                    completed BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (friend_id) REFERENCES friends(id)
                )
            ''')
            
            # 统御系统 - 互动记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interaction_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    friend_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    interaction_date TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (friend_id) REFERENCES friends(id)
                )
            ''')

            # 励志库表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lizhi_quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    author TEXT,
                    category TEXT DEFAULT 'poetry',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status INTEGER DEFAULT 1
                )
            ''')

            conn.commit()
            conn.close()
            
            # 初始化默认数据
            self._init_default_data()
            
        except Exception as e:
            print(f"数据库初始化错误: {e}")
            if conn:
                conn.close()
    
    def _init_default_data(self):
        """初始化默认数据"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 初始化用户数据
            cursor.execute("SELECT COUNT(*) FROM user_config")
            if cursor.fetchone()[0] == 0:
                birth_year = 1998
                age = datetime.now().year - birth_year
                initial_blood = (80 - age) * 365 * 24 * 60
                
                cursor.execute('''
                    INSERT INTO user_config 
                    (birth_year, initial_blood, current_blood, current_spirit, current_money, target_money)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (birth_year, initial_blood, initial_blood, 0, 125840, 5000000))
            
            # 初始化默认任务
            cursor.execute("SELECT COUNT(*) FROM tasks")
            if cursor.fetchone()[0] == 0:
                default_tasks = [
                    ("早起", "positive", 1, 0, "daily"),
                    ("晨跑30分钟", "positive", 1, 1, "daily"),
                    ("八部金刚功", "positive", 1, 2, "daily"),
                    ("冥想15分钟", "positive", 2, 0, "daily"),
                    ("阅读1小时", "positive", 1, 0, "daily"),
                    ("控制情绪", "positive", 1, 0, "daily"),
                    ("打扫房间", "positive", 1, 0, "daily"),
                    ("熬夜", "negative", -3, -1, "daily"),
                    ("刷自媒体", "negative", -3, 0, "daily"),
                    ("打游戏", "negative", -3, 0, "daily"),
                    ("发脾气", "negative", -3, -3, "daily"),
                    ("晚起", "negative", -2, 0, "daily"),
                ]
                
                for task in default_tasks:
                    cursor.execute('''
                        INSERT INTO tasks (name, category, spirit_effect, blood_effect, frequency)
                        VALUES (?, ?, ?, ?, ?)
                    ''', task)
            
            # 初始化默认固定收支项
            cursor.execute("SELECT COUNT(*) FROM fixed_items")
            if cursor.fetchone()[0] == 0:
                default_fixed_items = [
                    ("工资", "income", 15000, "固定工作收入"),
                    ("副业", "income", 2000, "额外收入来源"),
                    ("房租", "expense", 3000, "每月房租支出"),
                    ("房贷", "expense", 5000, "每月房贷还款"),
                    ("生活费", "expense", 2000, "日常生活费用"),
                ]
                
                for item in default_fixed_items:
                    cursor.execute('''
                        INSERT INTO fixed_items (name, type, amount, description)
                        VALUES (?, ?, ?, ?)
                    ''', item)
            
            # 初始化境界系统配置
            cursor.execute("SELECT COUNT(*) FROM jingjie_config")
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO jingjie_config (id, current_realm_index)
                    VALUES (1, 0)
                ''')
            
            # 初始化默认境界
            cursor.execute("SELECT COUNT(*) FROM realms")
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO realms (name, order_index, completed)
                    VALUES (?, ?, ?)
                ''', ("练气期", 0, False))
            
            # 初始化默认家族成员
            cursor.execute("SELECT COUNT(*) FROM family_members")
            if cursor.fetchone()[0] == 0:
                # 添加默认家族成员
                cursor.execute('''
                    INSERT INTO family_members (name, birthday, phone, notes)
                    VALUES (?, ?, ?, ?)
                ''', ("父亲", "1970-03-15", "138****1234", "喜欢钓鱼，注意血压"))
                
                father_id = cursor.lastrowid
                
                cursor.execute('''
                    INSERT INTO family_members (name, birthday, phone, notes)
                    VALUES (?, ?, ?, ?)
                ''', ("母亲", "1972-08-20", "139****5678", "喜欢跳舞，胃不好"))
                
                mother_id = cursor.lastrowid
                
                # 添加默认家族事件
                cursor.execute('''
                    INSERT INTO family_events (member_id, event_name, event_date, completed)
                    VALUES (?, ?, ?, ?)
                ''', (father_id, "生日", "2024-03-15", True))
                
                cursor.execute('''
                    INSERT INTO family_events (member_id, event_name, event_date, completed)
                    VALUES (?, ?, ?, ?)
                ''', (father_id, "父亲节", "2024-06-16", False))
                
                cursor.execute('''
                    INSERT INTO family_events (member_id, event_name, event_date, completed)
                    VALUES (?, ?, ?, ?)
                ''', (mother_id, "母亲节", "2024-05-12", False))
                
                cursor.execute('''
                    INSERT INTO family_events (member_id, event_name, event_date, completed)
                    VALUES (?, ?, ?, ?)
                ''', (mother_id, "生日", "2024-08-20", False))
            
            # 初始化默认朋友
            cursor.execute("SELECT COUNT(*) FROM friends")
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO friends (name, category, personality, hobbies, notes, last_contact)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', ("张三", "挚友", "外向开朗", "篮球、游戏", "大学室友，在深圳工作", "2024-12-01"))

                cursor.execute('''
                    INSERT INTO friends (name, category, personality, hobbies, notes, last_contact)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', ("李四", "同事", "稳重内敛", "读书、电影", "技术大牛，可以多交流", "2024-12-15"))

            # 初始化默认励志语录
            cursor.execute("SELECT COUNT(*) FROM lizhi_quotes")
            if cursor.fetchone()[0] == 0:
                default_quotes = [
                    ("大鹏一日同风起，扶摇直上九万里", "李白", "poetry"),
                    ("天行健，君子以自强不息", "周易", "poetry"),
                    ("不经一番寒彻骨，怎得梅花扑鼻香", "黄蘗禅师", "poetry"),
                    ("长风破浪会有时，直挂云帆济沧海", "李白", "poetry"),
                    ("千磨万击还坚劲，任尔东西南北风", "郑板桥", "poetry"),
                    ("路漫漫其修远兮，吾将上下而求索", "屈原", "poetry"),
                    ("宝剑锋从磨砺出，梅花香自苦寒来", "古诗", "poetry"),
                    ("莫愁前路无知己，天下谁人不识君", "高适", "poetry"),
                    ("会当凌绝顶，一览众山小", "杜甫", "poetry"),
                    ("天生我材必有用，千金散尽还复来", "李白", "poetry"),
                ]

                for content, author, category in default_quotes:
                    cursor.execute('''
                        INSERT INTO lizhi_quotes (content, author, category)
                        VALUES (?, ?, ?)
                    ''', (content, author, category))

            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"初始化默认数据错误: {e}")
            if conn:
                conn.close()
    
    def get_user_data(self) -> Optional[UserData]:
        """获取用户数据 - 带缓存优化"""
        # 检查缓存
        cached = self._get_cache('user_data', timeout=2)
        if cached:
            return cached

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT birth_year, current_spirit, current_blood, target_money, current_money
                FROM user_config LIMIT 1
            ''')
            row = cursor.fetchone()
            conn.close()

            if row:
                user_data = UserData(
                    birth_year=row[0],
                    current_spirit=row[1] or 0,
                    current_blood=row[2],
                    target_money=row[3],
                    current_money=row[4] or 0
                )
                # 设置缓存
                self._set_cache('user_data', user_data)
                return user_data
            return None
        except Exception as e:
            print(f"获取用户数据错误: {e}")
            return None
    
    def update_spirit_blood(self, spirit_change: int = 0, blood_change: int = 0):
        """更新心境和血量 - 性能优化"""
        # 清除用户数据缓存
        self._clear_cache('user_data')

        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 先检查当前血量
            cursor.execute('SELECT current_blood, current_spirit FROM user_config WHERE id = 1')
            result = cursor.fetchone()
            
            if result:
                current_blood, current_spirit = result
                # 确保血量不会变为负数
                new_blood = max(0, current_blood + blood_change)
                # 确保心境在范围内
                new_spirit = max(GameConfig.MIN_SPIRIT, 
                               min(GameConfig.MAX_SPIRIT, current_spirit + spirit_change))
                
                cursor.execute('''
                    UPDATE user_config 
                    SET current_spirit = ?,
                        current_blood = ?
                    WHERE id = 1
                ''', (new_spirit, new_blood))
                
                conn.commit()
                return True
            
            return False
            
        except Exception as e:
            print(f"更新心境血量错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def decrease_blood_by_time(self, amount: int = 1):
        """按时间减少血量（用于定时器）"""
        return self.update_spirit_blood(0, -amount)
    
    def get_tasks(self, category: Optional[str] = None) -> List[Task]:
        """获取任务列表"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if category:
                cursor.execute('''
                    SELECT id, name, category, spirit_effect, blood_effect, frequency 
                    FROM tasks WHERE status = 1 AND category = ?
                    ORDER BY id
                ''', (category,))
            else:
                cursor.execute('''
                    SELECT id, name, category, spirit_effect, blood_effect, frequency 
                    FROM tasks WHERE status = 1
                    ORDER BY category DESC, id
                ''')
            
            rows = cursor.fetchall()
            
            # 检查今日完成情况
            today = date.today().isoformat()
            cursor.execute('''
                SELECT task_id FROM task_records 
                WHERE DATE(completed_at) = ?
            ''', (today,))
            completed_ids = {row[0] for row in cursor.fetchall()}
            
            conn.close()
            
            tasks = []
            for row in rows:
                tasks.append(Task(
                    id=row[0],
                    name=row[1],
                    category=row[2],
                    spirit_effect=row[3],
                    blood_effect=row[4],
                    frequency=row[5],
                    completed_today=(row[0] in completed_ids)
                ))
            
            return tasks
            
        except Exception as e:
            print(f"获取任务列表错误: {e}")
            return []
    
    def complete_task(self, task_id: int, spirit_effect: int, blood_effect: int):
        """完成任务"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 检查今天是否已经完成过
            today = date.today().isoformat()
            cursor.execute('''
                SELECT COUNT(*) FROM task_records 
                WHERE task_id = ? AND DATE(completed_at) = ?
            ''', (task_id, today))
            
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO task_records (task_id, spirit_change, blood_change)
                    VALUES (?, ?, ?)
                ''', (task_id, spirit_effect, blood_effect))
                
                conn.commit()
                self.update_spirit_blood(spirit_effect, blood_effect)
            
        except Exception as e:
            print(f"完成任务错误: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def uncomplete_task(self, task_id: int, spirit_effect: int, blood_effect: int):
        """取消完成任务"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            today = date.today().isoformat()
            cursor.execute('''
                DELETE FROM task_records 
                WHERE task_id = ? AND DATE(completed_at) = ?
            ''', (task_id, today))
            
            if cursor.rowcount > 0:
                conn.commit()
                self.update_spirit_blood(-spirit_effect, -blood_effect)
            
        except Exception as e:
            print(f"取消任务错误: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def add_task(self, name: str, category: str, spirit_effect: int, blood_effect: int):
        """添加新任务"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tasks (name, category, spirit_effect, blood_effect)
                VALUES (?, ?, ?, ?)
            ''', (name, category, spirit_effect, blood_effect))
            
            conn.commit()
            
        except Exception as e:
            print(f"添加任务错误: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def add_finance_record(self, record_type: str, amount: float, category: str = None, description: str = None):
        """添加财务记录"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO finance_records (type, amount, category, description)
                VALUES (?, ?, ?, ?)
            ''', (record_type, amount, category, description))
            
            # 注意：不再直接更新current_money，保持其作为初始余额
            # 实际余额通过计算所有财务记录来获得
            
            conn.commit()
            
        except Exception as e:
            print(f"添加财务记录错误: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def get_finance_records(self, limit: int = 20) -> list:
        """获取财务记录"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT type, amount, category, description, created_at
                FROM finance_records
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            records = cursor.fetchall()
            conn.close()
            
            return records
            
        except Exception as e:
            print(f"获取财务记录错误: {e}")
            return []
        
    def delete_finance_record_by_details(self, record_type: str, amount: float, category: str, description: str, created_at: str) -> bool:
        """根据详细信息删除财务记录"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 先查找记录ID
            cursor.execute('''
                SELECT id, type, amount FROM finance_records 
                WHERE type = ? AND amount = ? AND category = ? AND 
                      (description = ? OR (description IS NULL AND ? IS NULL)) AND 
                      created_at = ?
                ORDER BY created_at DESC
                LIMIT 1
            ''', (record_type, amount, category, description, description, created_at))
            
            record = cursor.fetchone()
            if not record:
                print(f"未找到匹配的财务记录: {category} ¥{amount}")
                return False
            
            record_id, rec_type, rec_amount = record
            
            # 删除记录
            cursor.execute('DELETE FROM finance_records WHERE id = ?', (record_id,))
            
            # 注意：不再直接更新current_money，保持其作为初始余额
            # 删除记录后，实际余额会通过重新计算所有财务记录来获得
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"删除财务记录错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def delete_task(self, task_id: int):
        """删除任务"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 先删除相关的任务记录
            cursor.execute('DELETE FROM task_records WHERE task_id = ?', (task_id,))
            
            # 再删除任务本身
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"删除任务错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def update_task(self, task_id: int, name: str, spirit_effect: int, blood_effect: int):
        """更新任务"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE tasks 
                SET name = ?, spirit_effect = ?, blood_effect = ?
                WHERE id = ?
            ''', (name, spirit_effect, blood_effect, task_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"更新任务错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def set_money(self, amount: float):
        """设置当前灵石余额"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_config 
                SET current_money = ?
                WHERE id = 1
            ''', (amount,))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"设置余额错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def set_target_money(self, amount: float):
        """设置目标金额"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_config 
                SET target_money = ?
                WHERE id = 1
            ''', (amount,))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"设置目标金额错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    # 负债管理方法
    def add_debt(self, name: str, monthly_payment: float, remaining_months: int, description: str = None):
        """添加负债"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            total_amount = monthly_payment * remaining_months
            
            cursor.execute('''
                INSERT INTO debts (name, monthly_payment, remaining_months, total_amount, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, monthly_payment, remaining_months, total_amount, description))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"添加负债错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def get_debts(self) -> list:
        """获取负债列表"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, monthly_payment, remaining_months, total_amount, description, created_at
                FROM debts
                WHERE status = 1
                ORDER BY created_at DESC
            ''')
            
            debts = cursor.fetchall()
            conn.close()
            
            return debts
            
        except Exception as e:
            print(f"获取负债列表错误: {e}")
            return []
    
    def update_debt(self, debt_id: int, name: str, monthly_payment: float, remaining_months: int, description: str = None):
        """更新负债"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            total_amount = monthly_payment * remaining_months
            
            cursor.execute('''
                UPDATE debts 
                SET name = ?, monthly_payment = ?, remaining_months = ?, total_amount = ?, description = ?
                WHERE id = ?
            ''', (name, monthly_payment, remaining_months, total_amount, description, debt_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"更新负债错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def delete_debt(self, debt_id: int):
        """删除负债"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('UPDATE debts SET status = 0 WHERE id = ?', (debt_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"删除负债错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def get_debt_summary(self) -> dict:
        """获取负债汇总"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    SUM(total_amount) as total_debt,
                    SUM(monthly_payment) as monthly_payment,
                    COUNT(*) as debt_count
                FROM debts
                WHERE status = 1
            ''')
            
            row = cursor.fetchone()
            conn.close()
            
            return {
                'total_debt': row[0] or 0,
                'monthly_payment': row[1] or 0,
                'debt_count': row[2] or 0
            }
            
        except Exception as e:
            print(f"获取负债汇总错误: {e}")
            return {'total_debt': 0, 'monthly_payment': 0, 'debt_count': 0}
    
    # 资产管理方法
    def add_asset(self, name: str, monthly_income: float, duration_months: int, description: str = None):
        """添加资产"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            total_value = monthly_income * duration_months
            
            cursor.execute('''
                INSERT INTO assets (name, monthly_income, duration_months, total_value, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, monthly_income, duration_months, total_value, description))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"添加资产错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def get_assets(self) -> list:
        """获取资产列表"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, monthly_income, duration_months, total_value, description, created_at
                FROM assets
                WHERE status = 1
                ORDER BY created_at DESC
            ''')
            
            assets = cursor.fetchall()
            conn.close()
            
            return assets
            
        except Exception as e:
            print(f"获取资产列表错误: {e}")
            return []
    
    def update_asset(self, asset_id: int, name: str, monthly_income: float, duration_months: int, description: str = None):
        """更新资产"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            total_value = monthly_income * duration_months
            
            cursor.execute('''
                UPDATE assets 
                SET name = ?, monthly_income = ?, duration_months = ?, total_value = ?, description = ?
                WHERE id = ?
            ''', (name, monthly_income, duration_months, total_value, description, asset_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"更新资产错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def delete_asset(self, asset_id: int):
        """删除资产"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('UPDATE assets SET status = 0 WHERE id = ?', (asset_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"删除资产错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def get_asset_summary(self) -> dict:
        """获取资产汇总"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    SUM(total_value) as total_value,
                    SUM(monthly_income) as monthly_income,
                    COUNT(*) as asset_count
                FROM assets
                WHERE status = 1
            ''')
            
            row = cursor.fetchone()
            conn.close()
            
            return {
                'total_value': row[0] or 0,
                'monthly_income': row[1] or 0,
                'asset_count': row[2] or 0
            }
            
        except Exception as e:
            print(f"获取资产汇总错误: {e}")
            return {'total_value': 0, 'monthly_income': 0, 'asset_count': 0}
    
    # 固定收支项管理方法
    def add_fixed_item(self, name: str, item_type: str, amount: float, description: str = None):
        """添加固定收支项"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO fixed_items (name, type, amount, description)
                VALUES (?, ?, ?, ?)
            ''', (name, item_type, amount, description))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"添加固定收支项错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def get_fixed_items(self, item_type: str = None) -> dict:
        """获取固定收支项列表，返回按类型分组的字典"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if item_type:
                cursor.execute('''
                    SELECT id, name, type, amount, description, created_at
                    FROM fixed_items
                    WHERE status = 1 AND type = ?
                    ORDER BY created_at
                ''', (item_type,))
            else:
                cursor.execute('''
                    SELECT id, name, type, amount, description, created_at
                    FROM fixed_items
                    WHERE status = 1
                    ORDER BY type, created_at
                ''')
            
            items = cursor.fetchall()
            conn.close()
            
            # 按类型分组
            income_items = {}
            expense_items = {}
            
            for item in items:
                item_id, name, type_val, amount, description, created_at = item
                if type_val == 'income':
                    income_items[name] = amount
                elif type_val == 'expense':
                    expense_items[name] = amount
            
            return {
                'income': income_items,
                'expense': expense_items,
                'raw_items': items  # 包含完整信息的原始数据
            }
            
        except Exception as e:
            print(f"获取固定收支项错误: {e}")
            return {'income': {}, 'expense': {}, 'raw_items': []}
    
    def update_fixed_item(self, item_id: int, name: str, amount: float, description: str = None):
        """更新固定收支项"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE fixed_items 
                SET name = ?, amount = ?, description = ?
                WHERE id = ?
            ''', (name, amount, description, item_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"更新固定收支项错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def delete_fixed_item(self, item_id: int):
        """删除固定收支项"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('UPDATE fixed_items SET status = 0 WHERE id = ?', (item_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"删除固定收支项错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def delete_fixed_item_by_name(self, name: str, item_type: str):
        """根据名称和类型删除固定收支项"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE fixed_items SET status = 0 
                WHERE name = ? AND type = ? AND status = 1
            ''', (name, item_type))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"删除固定收支项错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    # =================== 境界系统数据持久化方法 ===================
    
    def save_jingjie_data(self, realm_data: dict):
        """保存境界系统数据到数据库 - 性能优化"""
        # 清除境界数据缓存
        self._clear_cache('jingjie_data')

        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 保存当前境界索引
            current_index = realm_data["gongfa"]["current_realm_index"]
            cursor.execute('''
                UPDATE jingjie_config SET current_realm_index = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = 1
            ''', (current_index,))
            
            # 清除现有数据
            cursor.execute('DELETE FROM skills')
            cursor.execute('DELETE FROM realms')
            
            # 保存境界数据
            realms = realm_data["gongfa"]["realms"]
            for i, realm in enumerate(realms):
                cursor.execute('''
                    INSERT INTO realms (name, order_index, completed)
                    VALUES (?, ?, ?)
                ''', (realm["name"], i, realm.get("completed", False)))
                
                realm_id = cursor.lastrowid
                
                # 保存该境界的功法
                for skill_name, skill_data in realm.get("skills", {}).items():
                    nodes_json = json.dumps(skill_data.get("nodes", []))
                    completed_json = json.dumps(skill_data.get("completed", []))
                    
                    cursor.execute('''
                        INSERT INTO skills (name, realm_id, skill_type, nodes_json, completed_json)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (skill_name, realm_id, 'gongfa', nodes_json, completed_json))
            
            # 保存秘术数据
            secret_arts = realm_data.get("secret_arts", {})
            for art_name, art_data in secret_arts.items():
                nodes_json = json.dumps(art_data.get("nodes", []))
                completed_json = json.dumps(art_data.get("completed", []))

                cursor.execute('''
                    INSERT INTO skills (name, realm_id, skill_type, nodes_json, completed_json)
                    VALUES (?, ?, ?, ?, ?)
                ''', (art_name, None, 'secret_art', nodes_json, completed_json))

            # 保存副本数据
            fuben_data = realm_data.get("fuben", {})
            for fuben_name, fuben_info in fuben_data.items():
                nodes_json = json.dumps(fuben_info.get("nodes", []))
                completed_json = json.dumps(fuben_info.get("completed", []))

                cursor.execute('''
                    INSERT INTO skills (name, realm_id, skill_type, nodes_json, completed_json)
                    VALUES (?, ?, ?, ?, ?)
                ''', (fuben_name, None, 'fuben', nodes_json, completed_json))

            conn.commit()
            return True
            
        except Exception as e:
            print(f"保存境界数据错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def load_jingjie_data(self) -> dict:
        """从数据库加载境界系统数据 - 带缓存优化"""
        # 检查缓存（3秒有效期）
        cached = self._get_cache('jingjie_data', timeout=3)
        if cached:
            return cached

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 加载当前境界索引
            cursor.execute('SELECT current_realm_index FROM jingjie_config WHERE id = 1')
            config_row = cursor.fetchone()
            current_realm_index = config_row[0] if config_row else 0
            
            # 加载境界数据
            cursor.execute('''
                SELECT id, name, order_index, completed 
                FROM realms 
                ORDER BY order_index
            ''')
            realm_rows = cursor.fetchall()
            
            realms = []
            realm_id_map = {}
            
            for realm_row in realm_rows:
                realm_id, name, order_index, completed = realm_row
                realm = {
                    "name": name,
                    "skills": {},
                    "completed": bool(completed)
                }
                realms.append(realm)
                realm_id_map[realm_id] = len(realms) - 1
            
            # 加载功法数据
            cursor.execute('''
                SELECT name, realm_id, skill_type, nodes_json, completed_json
                FROM skills
                WHERE skill_type = 'gongfa'
            ''')
            skill_rows = cursor.fetchall()
            
            for skill_row in skill_rows:
                name, realm_id, skill_type, nodes_json, completed_json = skill_row
                if realm_id in realm_id_map:
                    realm_index = realm_id_map[realm_id]
                    realms[realm_index]["skills"][name] = {
                        "nodes": json.loads(nodes_json),
                        "completed": json.loads(completed_json)
                    }
            
            # 加载秘术数据
            cursor.execute('''
                SELECT name, nodes_json, completed_json
                FROM skills
                WHERE skill_type = 'secret_art'
            ''')
            secret_art_rows = cursor.fetchall()
            
            secret_arts = {}
            for art_row in secret_art_rows:
                name, nodes_json, completed_json = art_row
                secret_arts[name] = {
                    "nodes": json.loads(nodes_json),
                    "completed": json.loads(completed_json)
                }

            # 加载副本数据
            cursor.execute('''
                SELECT name, nodes_json, completed_json
                FROM skills
                WHERE skill_type = 'fuben'
            ''')
            fuben_rows = cursor.fetchall()

            fuben_data = {}
            for fuben_row in fuben_rows:
                name, nodes_json, completed_json = fuben_row
                fuben_data[name] = {
                    "nodes": json.loads(nodes_json),
                    "completed": json.loads(completed_json)
                }

            conn.close()

            # 如果没有境界数据，创建默认境界
            if not realms:
                realms = [{
                    "name": "练气期",
                    "skills": {},
                    "completed": False
                }]

            result = {
                "gongfa": {
                    "realms": realms,
                    "current_realm_index": current_realm_index
                },
                "secret_arts": secret_arts,
                "fuben": fuben_data
            }

            # 设置缓存
            self._set_cache('jingjie_data', result)
            return result
            
        except Exception as e:
            print(f"加载境界数据错误: {e}")
            # 返回默认数据
            return {
                "gongfa": {
                    "realms": [{
                        "name": "练气期",
                        "skills": {},
                        "completed": False
                    }],
                    "current_realm_index": 0
                },
                "secret_arts": {},
                "fuben": {}
            }
    
    # =================== 统御系统数据操作方法 ===================
    
    def get_family_members(self) -> List[FamilyMember]:
        """获取家族成员列表"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, birthday, phone, notes, created_at
                FROM family_members
                ORDER BY created_at
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            members = []
            for row in rows:
                members.append(FamilyMember(
                    id=row[0],
                    name=row[1],
                    birthday=row[2],
                    phone=row[3] or "",
                    notes=row[4] or "",
                    created_at=row[5]
                ))
            
            return members
            
        except Exception as e:
            print(f"获取家族成员错误: {e}")
            return []
    
    def add_family_member(self, name: str, birthday: str, phone: str = "", notes: str = "") -> bool:
        """添加家族成员"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO family_members (name, birthday, phone, notes)
                VALUES (?, ?, ?, ?)
            ''', (name, birthday, phone, notes))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"添加家族成员错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def update_family_member(self, member_id: int, name: str, birthday: str, phone: str = "", notes: str = "") -> bool:
        """更新家族成员"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE family_members 
                SET name = ?, birthday = ?, phone = ?, notes = ?
                WHERE id = ?
            ''', (name, birthday, phone, notes, member_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"更新家族成员错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def delete_family_member(self, member_id: int) -> bool:
        """删除家族成员"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 先删除相关事件
            cursor.execute('DELETE FROM family_events WHERE member_id = ?', (member_id,))
            
            # 再删除成员
            cursor.execute('DELETE FROM family_members WHERE id = ?', (member_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"删除家族成员错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def get_family_events(self, member_id: int = None) -> List[FamilyEvent]:
        """获取家族事件列表"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if member_id:
                cursor.execute('''
                    SELECT id, member_id, event_name, event_date, completed, created_at
                    FROM family_events
                    WHERE member_id = ?
                    ORDER BY event_date
                ''', (member_id,))
            else:
                cursor.execute('''
                    SELECT id, member_id, event_name, event_date, completed, created_at
                    FROM family_events
                    ORDER BY event_date
                ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            events = []
            for row in rows:
                events.append(FamilyEvent(
                    id=row[0],
                    member_id=row[1],
                    event_name=row[2],
                    event_date=row[3],
                    completed=bool(row[4]),
                    created_at=row[5]
                ))
            
            return events
            
        except Exception as e:
            print(f"获取家族事件错误: {e}")
            return []
    
    def add_family_event(self, member_id: int, event_name: str, event_date: str) -> bool:
        """添加家族事件"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO family_events (member_id, event_name, event_date)
                VALUES (?, ?, ?)
            ''', (member_id, event_name, event_date))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"添加家族事件错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def toggle_family_event(self, event_id: int, completed: bool) -> bool:
        """切换家族事件完成状态"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE family_events 
                SET completed = ?
                WHERE id = ?
            ''', (completed, event_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"切换家族事件状态错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def get_friends(self) -> List[Friend]:
        """获取朋友列表"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, category, personality, hobbies, notes, 
                       last_contact, is_close_friend, ai_analysis, created_at
                FROM friends
                ORDER BY is_close_friend DESC, created_at
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            friends = []
            for row in rows:
                friends.append(Friend(
                    id=row[0],
                    name=row[1],
                    category=row[2],
                    personality=row[3] or "",
                    hobbies=row[4] or "",
                    notes=row[5] or "",
                    last_contact=row[6],
                    is_close_friend=bool(row[7]),
                    ai_analysis=row[8],
                    created_at=row[9]
                ))
            
            return friends
            
        except Exception as e:
            print(f"获取朋友列表错误: {e}")
            return []
    
    def add_friend(self, name: str, category: str, personality: str = "", hobbies: str = "", notes: str = "") -> Optional[int]:
        """添加朋友"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO friends (name, category, personality, hobbies, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, category, personality, hobbies, notes))
            
            friend_id = cursor.lastrowid
            conn.commit()
            return friend_id
            
        except Exception as e:
            print(f"添加朋友错误: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()
    
    def update_friend(self, friend_id: int, name: str, category: str, personality: str = "", hobbies: str = "", notes: str = "", ai_analysis: str = None) -> bool:
        """更新朋友信息"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE friends 
                SET name = ?, category = ?, personality = ?, hobbies = ?, notes = ?, ai_analysis = ?
                WHERE id = ?
            ''', (name, category, personality, hobbies, notes, ai_analysis, friend_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"更新朋友信息错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def delete_friend(self, friend_id: int) -> bool:
        """删除朋友"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 删除相关的关系、任务和互动记录
            cursor.execute('DELETE FROM friend_relations WHERE friend_id = ? OR related_friend_id = ?', (friend_id, friend_id))
            cursor.execute('DELETE FROM friend_tasks WHERE friend_id = ?', (friend_id,))
            cursor.execute('DELETE FROM interaction_records WHERE friend_id = ?', (friend_id,))
            
            # 删除朋友
            cursor.execute('DELETE FROM friends WHERE id = ?', (friend_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"删除朋友错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def update_friend_last_contact(self, friend_id: int, contact_date: str) -> bool:
        """更新朋友最后联系时间"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE friends 
                SET last_contact = ?
                WHERE id = ?
            ''', (contact_date, friend_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"更新朋友联系时间错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def auto_update_close_friend_status(self) -> bool:
        """自动更新密友状态（任务数量>10的朋友）"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 先重置所有朋友的密友状态
            cursor.execute('UPDATE friends SET is_close_friend = FALSE')
            
            # 查找任务数量>10的朋友并设置为密友
            cursor.execute('''
                UPDATE friends 
                SET is_close_friend = TRUE
                WHERE id IN (
                    SELECT friend_id 
                    FROM friend_tasks 
                    GROUP BY friend_id 
                    HAVING COUNT(*) > 10
                )
            ''')
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"自动更新密友状态错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def add_friend_relation(self, friend_id: int, related_friend_id: int, relation_type: str = "acquaintance") -> bool:
        """添加朋友关系"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO friend_relations (friend_id, related_friend_id, relation_type)
                VALUES (?, ?, ?)
            ''', (friend_id, related_friend_id, relation_type))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"添加朋友关系错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def get_friend_relations(self, friend_id: int) -> List[FriendRelation]:
        """获取朋友关系列表"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, friend_id, related_friend_id, relation_type, created_at
                FROM friend_relations
                WHERE friend_id = ? OR related_friend_id = ?
                ORDER BY created_at
            ''', (friend_id, friend_id))
            
            rows = cursor.fetchall()
            conn.close()
            
            relations = []
            for row in rows:
                relations.append(FriendRelation(
                    id=row[0],
                    friend_id=row[1],
                    related_friend_id=row[2],
                    relation_type=row[3],
                    created_at=row[4]
                ))
            
            return relations
            
        except Exception as e:
            print(f"获取朋友关系错误: {e}")
            return []
    
    def add_friend_task(self, friend_id: int, task_name: str, reward_type: str, reward_amount: int) -> bool:
        """添加朋友交互任务"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO friend_tasks (friend_id, task_name, reward_type, reward_amount)
                VALUES (?, ?, ?, ?)
            ''', (friend_id, task_name, reward_type, reward_amount))
            
            conn.commit()
            # 自动更新密友状态
            self.auto_update_close_friend_status()
            return True
            
        except Exception as e:
            print(f"添加朋友任务错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def get_friend_tasks(self, friend_id: int) -> List[FriendTask]:
        """获取朋友任务列表"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, friend_id, task_name, reward_type, reward_amount, completed, created_at
                FROM friend_tasks
                WHERE friend_id = ?
                ORDER BY completed, created_at DESC
            ''', (friend_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            tasks = []
            for row in rows:
                tasks.append(FriendTask(
                    id=row[0],
                    friend_id=row[1],
                    task_name=row[2],
                    reward_type=row[3],
                    reward_amount=row[4],
                    completed=bool(row[5]),
                    created_at=row[6]
                ))
            
            return tasks
            
        except Exception as e:
            print(f"获取朋友任务错误: {e}")
            return []
    
    def complete_friend_task(self, task_id: int) -> bool:
        """完成朋友任务"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 获取任务信息
            cursor.execute('''
                SELECT reward_type, reward_amount 
                FROM friend_tasks 
                WHERE id = ? AND completed = FALSE
            ''', (task_id,))
            
            task_info = cursor.fetchone()
            if not task_info:
                return False
            
            reward_type, reward_amount = task_info
            
            # 标记任务完成
            cursor.execute('''
                UPDATE friend_tasks 
                SET completed = TRUE
                WHERE id = ?
            ''', (task_id,))
            
            # 应用奖励
            if reward_type == "spirit":
                self.update_spirit_blood(reward_amount, 0)
            elif reward_type == "blood":
                self.update_spirit_blood(0, reward_amount)
            elif reward_type == "money":
                self.add_finance_record("income", reward_amount, "朋友任务", f"完成朋友任务奖励")
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"完成朋友任务错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def add_interaction_record(self, friend_id: int, content: str, interaction_date: str) -> bool:
        """添加互动记录"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO interaction_records (friend_id, content, interaction_date)
                VALUES (?, ?, ?)
            ''', (friend_id, content, interaction_date))
            
            # 更新朋友的最后联系时间
            self.update_friend_last_contact(friend_id, interaction_date)
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"添加互动记录错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def get_interaction_records(self, friend_id: int, limit: int = 10) -> List[InteractionRecord]:
        """获取互动记录"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, friend_id, content, interaction_date, created_at
                FROM interaction_records
                WHERE friend_id = ?
                ORDER BY interaction_date DESC
                LIMIT ?
            ''', (friend_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            records = []
            for row in rows:
                records.append(InteractionRecord(
                    id=row[0],
                    friend_id=row[1],
                    content=row[2],
                    interaction_date=row[3],
                    created_at=row[4]
                ))
            
            return records
            
        except Exception as e:
            print(f"获取互动记录错误: {e}")
            return []

    # =================== 励志库管理方法 ===================

    def get_all_quotes(self) -> list:
        """获取所有励志语录"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, content, author, category, created_at
                FROM lizhi_quotes
                WHERE status = 1
                ORDER BY created_at DESC
            ''')

            quotes = cursor.fetchall()
            conn.close()

            return quotes

        except Exception as e:
            print(f"获取励志语录错误: {e}")
            return []

    def get_random_quote(self) -> tuple:
        """随机获取一条励志语录"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, content, author, category
                FROM lizhi_quotes
                WHERE status = 1
                ORDER BY RANDOM()
                LIMIT 1
            ''')

            quote = cursor.fetchone()
            conn.close()

            return quote

        except Exception as e:
            print(f"获取随机励志语录错误: {e}")
            return None

    def add_quote(self, content: str, author: str = "", category: str = "poetry") -> bool:
        """添加励志语录"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO lizhi_quotes (content, author, category)
                VALUES (?, ?, ?)
            ''', (content, author, category))

            conn.commit()
            return True

        except Exception as e:
            print(f"添加励志语录错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def delete_quote(self, quote_id: int) -> bool:
        """删除励志语录"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('UPDATE lizhi_quotes SET status = 0 WHERE id = ?', (quote_id,))

            conn.commit()
            return True

        except Exception as e:
            print(f"删除励志语录错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()