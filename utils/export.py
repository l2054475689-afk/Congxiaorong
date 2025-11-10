import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import sqlite3

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from config import ThemeConfig, GameConfig


class ReportExporter:
    """报告导出器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.export_dir = Path("exports")
        self.export_dir.mkdir(exist_ok=True)
        
        # 注册中文字体（如果需要）
        self._setup_fonts()
    
    def _setup_fonts(self):
        """设置字体支持"""
        if REPORTLAB_AVAILABLE:
            try:
                # 尝试注册系统中文字体
                font_paths = [
                    "C:/Windows/Fonts/msyh.ttc",  # Windows 微软雅黑
                    "C:/Windows/Fonts/simhei.ttf",  # Windows 黑体
                    "/System/Library/Fonts/Arial.ttf",  # macOS
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"  # Linux
                ]
                
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('Chinese', font_path))
                        break
            except Exception:
                pass  # 如果字体注册失败，使用默认字体
    
    def _get_db_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def get_user_data(self) -> Dict[str, Any]:
        """获取用户基础数据"""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 获取用户配置
            cursor.execute("SELECT * FROM user_config LIMIT 1")
            user_config = cursor.fetchone()
            
            # 获取当前状态
            cursor.execute("SELECT blood_value, spirit_value FROM user_stats ORDER BY id DESC LIMIT 1")
            current_stats = cursor.fetchone()
            
            # 获取财务信息
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
                    SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
                FROM finance_records
            """)
            finance_stats = cursor.fetchone()
            
            return {
                'user_config': user_config,
                'current_stats': current_stats,
                'finance_stats': finance_stats,
                'export_time': datetime.now()
            }
        finally:
            conn.close()
    
    def get_period_data(self, period_type: str = "day", date_from: Optional[datetime] = None) -> Dict[str, Any]:
        """获取指定周期的数据"""
        if date_from is None:
            date_from = datetime.now()
        
        # 计算时间范围
        if period_type == "day":
            start_date = date_from.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif period_type == "week":
            start_date = date_from - timedelta(days=date_from.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)
        elif period_type == "month":
            start_date = date_from.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if date_from.month == 12:
                end_date = start_date.replace(year=date_from.year + 1, month=1)
            else:
                end_date = start_date.replace(month=date_from.month + 1)
        elif period_type == "year":
            start_date = date_from.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(year=date_from.year + 1)
        else:
            raise ValueError(f"不支持的周期类型: {period_type}")
        
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 获取任务完成记录
            cursor.execute("""
                SELECT tr.*, t.name, t.category, tr.spirit_change, tr.blood_change
                FROM task_records tr
                JOIN tasks t ON tr.task_id = t.id
                WHERE tr.completed_at >= ? AND tr.completed_at < ?
                ORDER BY tr.completed_at DESC
            """, (start_date.isoformat(), end_date.isoformat()))
            task_records = cursor.fetchall()
            
            # 获取财务记录
            cursor.execute("""
                SELECT * FROM finance_records
                WHERE created_at >= ? AND created_at < ?
                ORDER BY created_at DESC
            """, (start_date.isoformat(), end_date.isoformat()))
            finance_records = cursor.fetchall()
            
            # 获取心境变化统计
            spirit_changes = sum(record[4] or 0 for record in task_records)  # spirit_change
            blood_changes = sum(record[5] or 0 for record in task_records)   # blood_change
            
            # 获取财务统计
            income_total = sum(record[2] for record in finance_records if record[1] == 'income')
            expense_total = sum(record[2] for record in finance_records if record[1] == 'expense')
            
            return {
                'period_type': period_type,
                'start_date': start_date,
                'end_date': end_date,
                'task_records': task_records,
                'finance_records': finance_records,
                'summary': {
                    'total_tasks': len(task_records),
                    'spirit_changes': spirit_changes,
                    'blood_changes': blood_changes,
                    'income_total': income_total,
                    'expense_total': expense_total,
                    'net_income': income_total - expense_total
                }
            }
        finally:
            conn.close()
    
    def export_markdown_report(self, period_type: str = "day", date_from: Optional[datetime] = None) -> str:
        """导出Markdown格式报告"""
        user_data = self.get_user_data()
        period_data = self.get_period_data(period_type, date_from)
        
        # 生成文件名
        date_str = period_data['start_date'].strftime("%Y%m%d")
        filename = f"修仙报告_{period_type}_{date_str}.md"
        filepath = self.export_dir / filename
        
        # 生成报告内容
        report_lines = [
            f"# 凡人修仙3w天 - {period_type.upper()}报告",
            f"",
            f"**报告周期**: {period_data['start_date'].strftime('%Y-%m-%d')} 至 {period_data['end_date'].strftime('%Y-%m-%d')}",
            f"**生成时间**: {user_data['export_time'].strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"## 📊 本期概览",
            f"",
            f"- **完成任务**: {period_data['summary']['total_tasks']} 项",
            f"- **心境变化**: {period_data['summary']['spirit_changes']:+d}",
            f"- **血量变化**: {period_data['summary']['blood_changes']:+d}",
            f"- **收入总计**: ¥{period_data['summary']['income_total']:,.2f}",
            f"- **支出总计**: ¥{period_data['summary']['expense_total']:,.2f}",
            f"- **净收入**: ¥{period_data['summary']['net_income']:,.2f}",
            f"",
        ]
        
        # 添加任务详情
        if period_data['task_records']:
            report_lines.extend([
                f"## 🎯 任务完成记录",
                f"",
                f"| 时间 | 任务名称 | 分类 | 心境影响 | 血量影响 |",
                f"|------|----------|------|----------|----------|"
            ])
            
            for record in period_data['task_records'][:20]:  # 最多显示20条
                completed_time = datetime.fromisoformat(record[2]).strftime('%m-%d %H:%M')
                task_name = record[7] or "未知任务"
                category = record[8] or "其他"
                spirit_change = f"{record[4]:+d}" if record[4] else "0"
                blood_change = f"{record[5]:+d}" if record[5] else "0"
                
                report_lines.append(
                    f"| {completed_time} | {task_name} | {category} | {spirit_change} | {blood_change} |"
                )
            
            report_lines.append("")
        
        # 添加财务详情
        if period_data['finance_records']:
            report_lines.extend([
                f"## 💰 财务记录",
                f"",
                f"| 时间 | 类型 | 金额 | 分类 | 描述 |",
                f"|------|------|------|------|------|"
            ])
            
            for record in period_data['finance_records'][:20]:  # 最多显示20条
                record_time = datetime.fromisoformat(record[5]).strftime('%m-%d %H:%M')
                record_type = "收入" if record[1] == 'income' else "支出"
                amount = f"¥{record[2]:,.2f}"
                category = record[3] or "其他"
                description = record[4] or ""
                
                report_lines.append(
                    f"| {record_time} | {record_type} | {amount} | {category} | {description} |"
                )
            
            report_lines.append("")
        
        # 添加修炼感悟
        report_lines.extend([
            f"## 🧘 修炼感悟",
            f"",
            f"_此处可添加个人感悟和反思..._",
            f"",
            f"---",
            f"",
            f"*报告由凡人修仙3w天系统自动生成*"
        ])
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        return str(filepath)
    
    def export_excel_report(self, period_type: str = "day", date_from: Optional[datetime] = None) -> str:
        """导出Excel格式报告"""
        if not PANDAS_AVAILABLE:
            raise ImportError("需要安装pandas和openpyxl库来导出Excel文件")
        
        user_data = self.get_user_data()
        period_data = self.get_period_data(period_type, date_from)
        
        # 生成文件名
        date_str = period_data['start_date'].strftime("%Y%m%d")
        filename = f"修仙报告_{period_type}_{date_str}.xlsx"
        filepath = self.export_dir / filename
        
        # 创建Excel文件
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # 概览数据
            summary_data = {
                '指标': ['完成任务', '心境变化', '血量变化', '收入总计', '支出总计', '净收入'],
                '数值': [
                    period_data['summary']['total_tasks'],
                    period_data['summary']['spirit_changes'],
                    period_data['summary']['blood_changes'],
                    period_data['summary']['income_total'],
                    period_data['summary']['expense_total'],
                    period_data['summary']['net_income']
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='概览', index=False)
            
            # 任务记录
            if period_data['task_records']:
                task_data = []
                for record in period_data['task_records']:
                    task_data.append({
                        '完成时间': datetime.fromisoformat(record[2]).strftime('%Y-%m-%d %H:%M:%S'),
                        '任务名称': record[7] or "未知任务",
                        '分类': record[8] or "其他",
                        '心境影响': record[4] or 0,
                        '血量影响': record[5] or 0
                    })
                task_df = pd.DataFrame(task_data)
                task_df.to_excel(writer, sheet_name='任务记录', index=False)
            
            # 财务记录
            if period_data['finance_records']:
                finance_data = []
                for record in period_data['finance_records']:
                    finance_data.append({
                        '记录时间': datetime.fromisoformat(record[5]).strftime('%Y-%m-%d %H:%M:%S'),
                        '类型': "收入" if record[1] == 'income' else "支出",
                        '金额': record[2],
                        '分类': record[3] or "其他",
                        '描述': record[4] or ""
                    })
                finance_df = pd.DataFrame(finance_data)
                finance_df.to_excel(writer, sheet_name='财务记录', index=False)
        
        return str(filepath)
    
    def export_pdf_report(self, period_type: str = "day", date_from: Optional[datetime] = None) -> str:
        """导出PDF格式报告"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("需要安装reportlab库来导出PDF文件")
        
        user_data = self.get_user_data()
        period_data = self.get_period_data(period_type, date_from)
        
        # 生成文件名
        date_str = period_data['start_date'].strftime("%Y%m%d")
        filename = f"修仙报告_{period_type}_{date_str}.pdf"
        filepath = self.export_dir / filename
        
        # 创建PDF文档
        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # 标题样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=1,  # 居中
            textColor=HexColor(ThemeConfig.PRIMARY_COLOR)
        )
        
        # 添加标题
        title = Paragraph(f"凡人修仙3w天 - {period_type.upper()}报告", title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # 添加报告信息
        info_text = f"""
        <b>报告周期:</b> {period_data['start_date'].strftime('%Y-%m-%d')} 至 {period_data['end_date'].strftime('%Y-%m-%d')}<br/>
        <b>生成时间:</b> {user_data['export_time'].strftime('%Y-%m-%d %H:%M:%S')}
        """
        story.append(Paragraph(info_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # 添加概览表格
        overview_data = [
            ['指标', '数值'],
            ['完成任务', f"{period_data['summary']['total_tasks']} 项"],
            ['心境变化', f"{period_data['summary']['spirit_changes']:+d}"],
            ['血量变化', f"{period_data['summary']['blood_changes']:+d}"],
            ['收入总计', f"¥{period_data['summary']['income_total']:,.2f}"],
            ['支出总计', f"¥{period_data['summary']['expense_total']:,.2f}"],
            ['净收入', f"¥{period_data['summary']['net_income']:,.2f}"]
        ]
        
        overview_table = Table(overview_data, colWidths=[2*inch, 2*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(ThemeConfig.PRIMARY_COLOR)),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F5F5F5')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#CCCCCC'))
        ]))
        
        story.append(Paragraph("<b>本期概览</b>", styles['Heading2']))
        story.append(overview_table)
        story.append(Spacer(1, 20))
        
        # 添加任务记录表格（如果有数据）
        if period_data['task_records']:
            story.append(Paragraph("<b>任务完成记录</b>", styles['Heading2']))
            
            task_data = [['时间', '任务名称', '分类', '心境影响', '血量影响']]
            for record in period_data['task_records'][:10]:  # 最多显示10条
                completed_time = datetime.fromisoformat(record[2]).strftime('%m-%d %H:%M')
                task_name = record[7] or "未知任务"
                category = record[8] or "其他"
                spirit_change = f"{record[4]:+d}" if record[4] else "0"
                blood_change = f"{record[5]:+d}" if record[5] else "0"
                
                task_data.append([completed_time, task_name, category, spirit_change, blood_change])
            
            task_table = Table(task_data, colWidths=[1*inch, 2*inch, 1*inch, 1*inch, 1*inch])
            task_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor(ThemeConfig.SUCCESS_COLOR)),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F9F9F9')),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#CCCCCC'))
            ]))
            
            story.append(task_table)
        
        # 构建PDF
        doc.build(story)
        
        return str(filepath)
    
    def export_custom_report(self, config: Dict[str, Any]) -> str:
        """导出自定义报告"""
        # 解析自定义配置
        period_type = config.get('period_type', 'day')
        date_from = config.get('date_from', None)
        format_type = config.get('format', 'markdown')
        include_charts = config.get('include_charts', False)
        
        # 根据格式选择导出方法
        if format_type == 'pdf':
            return self.export_pdf_report(period_type, date_from)
        elif format_type == 'excel':
            return self.export_excel_report(period_type, date_from)
        else:
            return self.export_markdown_report(period_type, date_from)


# 使用示例
if __name__ == "__main__":
    exporter = ReportExporter("immortal_cultivation.db")
    
    # 导出今日报告
    try:
        md_file = exporter.export_markdown_report("day")
        print(f"Markdown报告已导出: {md_file}")
        
        if PANDAS_AVAILABLE:
            excel_file = exporter.export_excel_report("day")
            print(f"Excel报告已导出: {excel_file}")
        
        if REPORTLAB_AVAILABLE:
            pdf_file = exporter.export_pdf_report("day")
            print(f"PDF报告已导出: {pdf_file}")
            
    except Exception as e:
        print(f"导出失败: {e}") 