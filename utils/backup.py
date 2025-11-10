import os
import json
import shutil
import sqlite3
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import threading
import schedule
import time

from config import APP_NAME


class BackupManager:
    """数据备份管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # 备份设置
        self.max_backups = 30  # 最多保留30个备份
        self.auto_backup_enabled = True
        self.backup_schedule = "daily"  # daily, weekly, monthly
        
        # 启动自动备份调度器
        self._schedule_auto_backup()
        
        # 启动后台线程
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def _schedule_auto_backup(self):
        """设置自动备份调度"""
        schedule.clear()
        
        if self.auto_backup_enabled:
            if self.backup_schedule == "daily":
                schedule.every().day.at("02:00").do(self._auto_backup)
            elif self.backup_schedule == "weekly":
                schedule.every().week.do(self._auto_backup)
            elif self.backup_schedule == "monthly":
                schedule.every().month.do(self._auto_backup)
    
    def _run_scheduler(self):
        """运行调度器后台线程"""
        while self.scheduler_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
            except Exception as e:
                print(f"调度器错误: {e}")
    
    def _auto_backup(self):
        """自动备份"""
        try:
            filename = self.create_backup(backup_type="auto")
            print(f"自动备份完成: {filename}")
            self._cleanup_old_backups()
        except Exception as e:
            print(f"自动备份失败: {e}")
    
    def create_backup(self, backup_type: str = "manual", description: str = "") -> str:
        """创建备份
        
        Args:
            backup_type: 备份类型 (manual, auto, export)
            description: 备份描述
            
        Returns:
            备份文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{APP_NAME}_backup_{backup_type}_{timestamp}"
        backup_filename = f"{backup_name}.zip"
        backup_path = self.backup_dir / backup_filename
        
        # 创建备份文件夹
        temp_backup_dir = self.backup_dir / backup_name
        temp_backup_dir.mkdir(exist_ok=True)
        
        try:
            # 备份数据库文件
            if self.db_path.exists():
                shutil.copy2(self.db_path, temp_backup_dir / self.db_path.name)
            
            # 备份配置文件
            config_files = [
                "config.py",
                "assets/initial_tasks.json",
                "assets/api_config.json"
            ]
            
            for config_file in config_files:
                src_path = Path(config_file)
                if src_path.exists():
                    dst_path = temp_backup_dir / src_path.name
                    shutil.copy2(src_path, dst_path)
            
            # 导出JSON格式的数据（便于查看和恢复）
            json_data = self._export_database_to_json()
            json_path = temp_backup_dir / "data_export.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2, default=str)
            
            # 创建备份信息文件
            backup_info = {
                "app_name": APP_NAME,
                "backup_type": backup_type,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "database_file": self.db_path.name,
                "files": [
                    self.db_path.name,
                    "data_export.json"
                ] + [Path(f).name for f in config_files if Path(f).exists()]
            }
            
            info_path = temp_backup_dir / "backup_info.json"
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, ensure_ascii=False, indent=2, default=str)
            
            # 压缩备份文件夹
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in temp_backup_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_backup_dir)
                        zipf.write(file_path, arcname)
            
            # 清理临时文件夹
            shutil.rmtree(temp_backup_dir)
            
            return str(backup_path)
            
        except Exception as e:
            # 清理临时文件夹
            if temp_backup_dir.exists():
                shutil.rmtree(temp_backup_dir)
            raise e
    
    def _export_database_to_json(self) -> Dict[str, Any]:
        """将数据库导出为JSON格式"""
        if not self.db_path.exists():
            return {}
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 使返回结果可以像字典一样访问
        cursor = conn.cursor()
        
        try:
            data = {}
            
            # 获取所有表名
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # 导出每个表的数据
            for table in tables:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                # 转换为字典列表
                data[table] = []
                for row in rows:
                    row_dict = dict(row)
                    data[table].append(row_dict)
            
            return data
            
        finally:
            conn.close()
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """列出所有备份文件"""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.zip"):
            try:
                # 尝试读取备份信息
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    if "backup_info.json" in zipf.namelist():
                        with zipf.open("backup_info.json") as f:
                            backup_info = json.load(f)
                    else:
                        # 从文件名解析信息
                        parts = backup_file.stem.split('_')
                        backup_info = {
                            "backup_type": parts[2] if len(parts) > 2 else "unknown",
                            "created_at": "unknown",
                            "description": ""
                        }
                
                backup_info.update({
                    "filename": backup_file.name,
                    "filepath": str(backup_file),
                    "size": backup_file.stat().st_size,
                    "size_mb": round(backup_file.stat().st_size / 1024 / 1024, 2)
                })
                
                backups.append(backup_info)
                
            except Exception as e:
                print(f"读取备份文件失败 {backup_file}: {e}")
        
        # 按创建时间排序
        backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return backups
    
    def restore_backup(self, backup_path: str, restore_type: str = "full") -> bool:
        """恢复备份
        
        Args:
            backup_path: 备份文件路径
            restore_type: 恢复类型 (full, data_only, config_only)
            
        Returns:
            是否恢复成功
        """
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"备份文件不存在: {backup_path}")
        
        # 创建当前数据的临时备份
        current_backup = None
        if self.db_path.exists():
            current_backup = self.create_backup("restore_temp", "恢复前的临时备份")
        
        try:
            # 解压备份文件
            temp_restore_dir = self.backup_dir / "temp_restore"
            temp_restore_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(temp_restore_dir)
            
            # 读取备份信息
            backup_info_path = temp_restore_dir / "backup_info.json"
            if backup_info_path.exists():
                with open(backup_info_path, 'r', encoding='utf-8') as f:
                    backup_info = json.load(f)
            else:
                backup_info = {"files": []}
            
            # 恢复数据库文件
            if restore_type in ["full", "data_only"]:
                for filename in backup_info.get("files", []):
                    if filename.endswith('.db'):
                        src_db = temp_restore_dir / filename
                        if src_db.exists():
                            shutil.copy2(src_db, self.db_path)
                            break
                else:
                    # 如果没有找到数据库文件，尝试从JSON恢复
                    json_data_path = temp_restore_dir / "data_export.json"
                    if json_data_path.exists():
                        self._restore_database_from_json(json_data_path)
            
            # 恢复配置文件
            if restore_type in ["full", "config_only"]:
                config_files = [
                    "config.py",
                    "initial_tasks.json",
                    "api_config.json"
                ]
                
                for config_file in config_files:
                    src_config = temp_restore_dir / config_file
                    if src_config.exists():
                        if config_file == "config.py":
                            dst_config = Path("config.py")
                        else:
                            dst_config = Path("assets") / config_file
                            dst_config.parent.mkdir(exist_ok=True)
                        
                        shutil.copy2(src_config, dst_config)
            
            # 清理临时文件夹
            shutil.rmtree(temp_restore_dir)
            
            # 删除临时备份（如果恢复成功）
            if current_backup:
                Path(current_backup).unlink(missing_ok=True)
            
            return True
            
        except Exception as e:
            # 恢复失败，尝试恢复原数据
            if current_backup and Path(current_backup).exists():
                try:
                    self.restore_backup(current_backup, "data_only")
                except:
                    pass
            
            # 清理临时文件夹
            if temp_restore_dir.exists():
                shutil.rmtree(temp_restore_dir)
            
            raise e
    
    def _restore_database_from_json(self, json_path: Path):
        """从JSON文件恢复数据库"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 创建新数据库
        if self.db_path.exists():
            self.db_path.unlink()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 这里需要根据实际的数据库模型重新创建表结构
            # 为了简化，我们假设可以从现有的模型文件获取表结构
            
            # 恢复数据
            for table_name, rows in data.items():
                if not rows:
                    continue
                
                # 获取列名
                columns = list(rows[0].keys())
                placeholders = ', '.join(['?' for _ in columns])
                
                # 插入数据
                for row in rows:
                    values = [row[col] for col in columns]
                    cursor.execute(
                        f"INSERT OR REPLACE INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})",
                        values
                    )
            
            conn.commit()
            
        finally:
            conn.close()
    
    def _cleanup_old_backups(self):
        """清理过期的备份文件"""
        backups = self.list_backups()
        
        # 按类型分组
        auto_backups = [b for b in backups if b.get('backup_type') == 'auto']
        manual_backups = [b for b in backups if b.get('backup_type') == 'manual']
        
        # 清理自动备份（保留最近的）
        if len(auto_backups) > self.max_backups:
            for backup in auto_backups[self.max_backups:]:
                try:
                    Path(backup['filepath']).unlink()
                except Exception as e:
                    print(f"删除备份文件失败 {backup['filename']}: {e}")
        
        # 清理超过90天的手动备份
        cutoff_date = datetime.now() - timedelta(days=90)
        for backup in manual_backups:
            try:
                created_at = datetime.fromisoformat(backup.get('created_at', ''))
                if created_at < cutoff_date:
                    Path(backup['filepath']).unlink()
            except:
                pass
    
    def delete_backup(self, backup_path: str) -> bool:
        """删除指定的备份文件"""
        try:
            Path(backup_path).unlink()
            return True
        except Exception:
            return False
    
    def export_backup_report(self) -> str:
        """导出备份报告"""
        backups = self.list_backups()
        
        report_lines = [
            f"# {APP_NAME} 备份报告",
            f"",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**总备份数量**: {len(backups)}",
            f"**备份目录**: {self.backup_dir.absolute()}",
            f"**自动备份**: {'启用' if self.auto_backup_enabled else '禁用'}",
            f"**备份策略**: {self.backup_schedule}",
            f"",
            f"## 备份列表",
            f"",
            f"| 文件名 | 类型 | 创建时间 | 大小(MB) | 描述 |",
            f"|--------|------|----------|----------|------|"
        ]
        
        for backup in backups:
            created_at = backup.get('created_at', 'unknown')
            if created_at != 'unknown':
                try:
                    created_at = datetime.fromisoformat(created_at).strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
            report_lines.append(
                f"| {backup['filename']} | {backup.get('backup_type', 'unknown')} | {created_at} | {backup['size_mb']} | {backup.get('description', '')} |"
            )
        
        report_content = '\n'.join(report_lines)
        
        # 保存报告
        report_path = self.backup_dir / f"backup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(report_path)
    
    def get_backup_settings(self) -> Dict[str, Any]:
        """获取备份设置"""
        return {
            "auto_backup_enabled": self.auto_backup_enabled,
            "backup_schedule": self.backup_schedule,
            "max_backups": self.max_backups,
            "backup_dir": str(self.backup_dir.absolute())
        }
    
    def update_backup_settings(self, settings: Dict[str, Any]):
        """更新备份设置"""
        if "auto_backup_enabled" in settings:
            self.auto_backup_enabled = settings["auto_backup_enabled"]
        
        if "backup_schedule" in settings:
            self.backup_schedule = settings["backup_schedule"]
        
        if "max_backups" in settings:
            self.max_backups = max(1, int(settings["max_backups"]))
        
        # 重新设置调度
        self._schedule_auto_backup()
    
    def stop_scheduler(self):
        """停止调度器"""
        self.scheduler_running = False
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)


# 使用示例
if __name__ == "__main__":
    backup_manager = BackupManager("immortal_cultivation.db")
    
    try:
        # 创建手动备份
        backup_file = backup_manager.create_backup("manual", "测试备份")
        print(f"备份创建成功: {backup_file}")
        
        # 列出所有备份
        backups = backup_manager.list_backups()
        print(f"共有 {len(backups)} 个备份文件")
        
        # 导出备份报告
        report_file = backup_manager.export_backup_report()
        print(f"备份报告已生成: {report_file}")
        
    except Exception as e:
        print(f"操作失败: {e}")
    finally:
        backup_manager.stop_scheduler() 