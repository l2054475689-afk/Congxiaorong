from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Task():
    """任务模型"""
    id: int
    name: str
    category: str  # positive/negative
    spirit_effect: int
    blood_effect: int
    frequency: str = "daily"
    completed_today: bool = False
    created_at: Optional[datetime] = None

@dataclass
class UserData:
    """用户数据模型"""
    birth_year: int
    current_spirit: int
    current_blood: int
    target_money: int
    current_money: int
    created_at: Optional[datetime] = None

@dataclass
class TaskRecord:
    """任务记录模型"""
    id: int
    task_id: int
    completed_at: datetime
    spirit_change: int
    blood_change: int

@dataclass
class FamilyMember:
    """家族成员模型"""
    id: int
    name: str
    birthday: str
    phone: str
    notes: str
    created_at: Optional[datetime] = None

@dataclass
class FamilyEvent:
    """家族事件模型"""
    id: int
    member_id: int
    event_name: str
    event_date: str
    completed: bool = False
    created_at: Optional[datetime] = None

@dataclass
class Friend:
    """朋友模型"""
    id: int
    name: str
    category: str
    personality: str
    hobbies: str
    notes: str
    last_contact: Optional[str] = None
    is_close_friend: bool = False  # 密友标识
    ai_analysis: Optional[str] = None  # AI性格分析
    created_at: Optional[datetime] = None

@dataclass
class FriendRelation:
    """朋友关系模型"""
    id: int
    friend_id: int
    related_friend_id: int
    relation_type: str = "acquaintance"  # acquaintance, close, etc.
    created_at: Optional[datetime] = None

@dataclass
class FriendTask:
    """朋友交互任务模型"""
    id: int
    friend_id: int
    task_name: str
    reward_type: str  # spirit/blood/money
    reward_amount: int
    completed: bool = False
    created_at: Optional[datetime] = None

@dataclass
class InteractionRecord:
    """互动记录模型"""
    id: int
    friend_id: int
    content: str
    interaction_date: str
    created_at: Optional[datetime] = None