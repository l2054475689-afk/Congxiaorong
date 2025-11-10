import flet as ft
from config import ThemeConfig

class Styles:
    """UI样式定义"""
    
    @staticmethod
    def get_gradient(colors: list):
        """获取渐变色"""
        return ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=colors,
        )
    
    @staticmethod
    def get_card_shadow():
        """获取卡片阴影"""
        return ft.BoxShadow(
            spread_radius=1,
            blur_radius=5,
            color="#1A000000",  # 10% 黑色透明度
        )
    
    @staticmethod
    def get_spirit_level_info(spirit_value: int) -> tuple:
        """根据心境值获取等级信息"""
        if spirit_value <= -80:
            return ("心魔入体", "#8b0000")
        elif -80 < spirit_value <= -60:
            return ("烦躁不堪", "#dc143c")
        elif -60 < spirit_value <= -20:
            return ("心烦意乱", "#ff6347")
        elif -20 < spirit_value <= 0:
            return ("略有烦躁", "#ffa500")
        elif 0 < spirit_value <= 40:
            return ("心平气和", "#90ee90")
        elif 40 < spirit_value <= 80:
            return ("清心寡欲", "#32cd32")
        elif 80 < spirit_value <= 100:
            return ("守静笃行", "#228b22")
        elif 100 < spirit_value <= 120:
            return ("虚怀若谷", "#4169e1")
        elif 120 < spirit_value <= 140:
            return ("返璞归真", "#9370db")
        else:
            return ("逍遥自在", "#8b008b")