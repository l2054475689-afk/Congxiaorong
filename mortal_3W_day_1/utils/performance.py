import gc
import psutil
import threading
import time
from functools import wraps, lru_cache
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
import weakref
import sys


class PerformanceOptimizer:
    """性能优化管理器"""
    
    def __init__(self):
        self.cache_stats = {"hits": 0, "misses": 0}
        self.memory_warnings = []
        self.performance_metrics = {}
        self.cleanup_tasks = []
        
        # 启动内存监控线程
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_memory, daemon=True)
        self.monitor_thread.start()
    
    def _monitor_memory(self):
        """监控内存使用情况"""
        while self.monitoring_active:
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                memory_percent = process.memory_percent()
                
                # 记录内存使用情况
                self.performance_metrics["memory_rss"] = memory_info.rss / 1024 / 1024  # MB
                self.performance_metrics["memory_vms"] = memory_info.vms / 1024 / 1024  # MB
                self.performance_metrics["memory_percent"] = memory_percent
                
                # 内存警告阈值
                if memory_percent > 80:
                    self.memory_warnings.append({
                        "timestamp": datetime.now(),
                        "memory_percent": memory_percent,
                        "memory_mb": memory_info.rss / 1024 / 1024
                    })
                    
                    # 自动清理
                    self.auto_cleanup()
                
                time.sleep(30)  # 每30秒检查一次
                
            except Exception as e:
                print(f"内存监控错误: {e}")
                time.sleep(60)
    
    def auto_cleanup(self):
        """自动内存清理"""
        try:
            # 执行注册的清理任务
            for cleanup_func in self.cleanup_tasks:
                try:
                    cleanup_func()
                except Exception as e:
                    print(f"清理任务执行失败: {e}")
            
            # 强制垃圾回收
            collected = gc.collect()
            print(f"自动清理: 回收了 {collected} 个对象")
            
        except Exception as e:
            print(f"自动清理失败: {e}")
    
    def register_cleanup_task(self, func: Callable):
        """注册清理任务"""
        self.cleanup_tasks.append(func)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        try:
            process = psutil.Process()
            cpu_percent = process.cpu_percent()
            
            return {
                "memory": self.performance_metrics.copy(),
                "cpu_percent": cpu_percent,
                "cache_stats": self.cache_stats.copy(),
                "memory_warnings_count": len(self.memory_warnings),
                "gc_counts": gc.get_count(),
                "object_count": len(gc.get_objects()),
            }
        except Exception as e:
            return {"error": str(e)}
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False


# 全局性能优化器实例
performance_optimizer = PerformanceOptimizer()


def performance_timer(func):
    """性能计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # 记录性能指标
            func_name = f"{func.__module__}.{func.__name__}"
            if func_name not in performance_optimizer.performance_metrics:
                performance_optimizer.performance_metrics[func_name] = {
                    "total_calls": 0,
                    "total_time": 0,
                    "avg_time": 0,
                    "max_time": 0,
                    "min_time": float('inf')
                }
            
            metrics = performance_optimizer.performance_metrics[func_name]
            metrics["total_calls"] += 1
            metrics["total_time"] += execution_time
            metrics["avg_time"] = metrics["total_time"] / metrics["total_calls"]
            metrics["max_time"] = max(metrics["max_time"], execution_time)
            metrics["min_time"] = min(metrics["min_time"], execution_time)
            
            return result
            
        except Exception as e:
            print(f"函数 {func.__name__} 执行错误: {e}")
            raise
    
    return wrapper


def cached_result(ttl_seconds: int = 300):
    """结果缓存装饰器"""
    def decorator(func):
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 创建缓存键
            cache_key = str(args) + str(sorted(kwargs.items()))
            current_time = time.time()
            
            # 检查缓存
            if cache_key in cache:
                cached_data, cached_time = cache[cache_key]
                if current_time - cached_time < ttl_seconds:
                    performance_optimizer.cache_stats["hits"] += 1
                    return cached_data
                else:
                    # 缓存过期，删除
                    del cache[cache_key]
            
            # 缓存未命中
            performance_optimizer.cache_stats["misses"] += 1
            result = func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            
            return result
        
        def clear_cache():
            cache.clear()
        
        wrapper.clear_cache = clear_cache
        performance_optimizer.register_cleanup_task(clear_cache)
        
        return wrapper
    
    return decorator


class DataManager:
    """数据管理器 - 优化数据库访问"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.query_cache = {}
        self.last_cache_clear = time.time()
        self.cache_ttl = 300  # 5分钟缓存
    
    @performance_timer
    @cached_result(ttl_seconds=300)
    def get_user_stats_cached(self):
        """获取用户统计信息（缓存版）"""
        return self.db.get_user_stats()
    
    @performance_timer
    @cached_result(ttl_seconds=600)
    def get_finance_summary_cached(self):
        """获取财务汇总（缓存版）"""
        return self.db.get_finance_summary()
    
    @performance_timer
    def get_today_tasks_optimized(self):
        """获取今日任务（优化版）"""
        # 这里可以添加更多优化逻辑
        return self.db.get_today_tasks()
    
    @performance_timer
    @cached_result(ttl_seconds=1800)  # 30分钟缓存
    def get_trend_data_cached(self, data_type: str, days: int = 7):
        """获取趋势数据（缓存版）"""
        if data_type == "spirit":
            return self.db.get_spirit_trend_data(days)
        elif data_type == "finance":
            return self.db.get_finance_trend_data(days)
        else:
            return []
    
    def invalidate_cache(self, cache_type: Optional[str] = None):
        """清除缓存"""
        if cache_type is None:
            # 清除所有缓存
            if hasattr(self.get_user_stats_cached, 'clear_cache'):
                self.get_user_stats_cached.clear_cache()
            if hasattr(self.get_finance_summary_cached, 'clear_cache'):
                self.get_finance_summary_cached.clear_cache()
            if hasattr(self.get_trend_data_cached, 'clear_cache'):
                self.get_trend_data_cached.clear_cache()
        
        self.last_cache_clear = time.time()


class UIOptimizer:
    """UI性能优化器"""
    
    def __init__(self):
        self.widget_pool = {}
        self.lazy_load_queue = []
        self.render_cache = {}
    
    def get_pooled_widget(self, widget_type: str, create_func: Callable):
        """获取池化的组件"""
        if widget_type not in self.widget_pool:
            self.widget_pool[widget_type] = []
        
        pool = self.widget_pool[widget_type]
        if pool:
            return pool.pop()
        else:
            return create_func()
    
    def return_widget_to_pool(self, widget_type: str, widget):
        """将组件返回到池中"""
        if widget_type not in self.widget_pool:
            self.widget_pool[widget_type] = []
        
        # 重置组件状态
        self._reset_widget(widget)
        self.widget_pool[widget_type].append(widget)
    
    def _reset_widget(self, widget):
        """重置组件状态"""
        # 根据具体组件类型重置状态
        try:
            if hasattr(widget, 'visible'):
                widget.visible = True
            if hasattr(widget, 'disabled'):
                widget.disabled = False
        except:
            pass
    
    def schedule_lazy_load(self, load_func: Callable, priority: int = 0):
        """安排延迟加载"""
        self.lazy_load_queue.append((priority, load_func))
        self.lazy_load_queue.sort(key=lambda x: x[0], reverse=True)
    
    def process_lazy_load_queue(self, max_items: int = 3):
        """处理延迟加载队列"""
        processed = 0
        while self.lazy_load_queue and processed < max_items:
            _, load_func = self.lazy_load_queue.pop(0)
            try:
                load_func()
                processed += 1
            except Exception as e:
                print(f"延迟加载失败: {e}")
    
    def clear_render_cache(self):
        """清除渲染缓存"""
        self.render_cache.clear()


class BatchProcessor:
    """批处理器 - 优化大量数据操作"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.pending_operations = []
        self.last_flush = time.time()
        self.auto_flush_interval = 5  # 5秒自动刷新
    
    def add_operation(self, operation: Dict[str, Any]):
        """添加操作到批处理队列"""
        self.pending_operations.append(operation)
        
        # 检查是否需要自动刷新
        if (len(self.pending_operations) >= self.batch_size or 
            time.time() - self.last_flush > self.auto_flush_interval):
            self.flush()
    
    def flush(self):
        """执行批处理操作"""
        if not self.pending_operations:
            return
        
        operations = self.pending_operations.copy()
        self.pending_operations.clear()
        self.last_flush = time.time()
        
        # 按类型分组操作
        grouped_ops = {}
        for op in operations:
            op_type = op.get('type', 'unknown')
            if op_type not in grouped_ops:
                grouped_ops[op_type] = []
            grouped_ops[op_type].append(op)
        
        # 执行分组操作
        for op_type, ops in grouped_ops.items():
            try:
                self._execute_batch_operation(op_type, ops)
            except Exception as e:
                print(f"批处理操作失败 {op_type}: {e}")
    
    def _execute_batch_operation(self, op_type: str, operations: List[Dict[str, Any]]):
        """执行具体的批处理操作"""
        # 根据操作类型执行相应的批处理逻辑
        if op_type == "database_insert":
            self._batch_database_insert(operations)
        elif op_type == "database_update":
            self._batch_database_update(operations)
        # 可以添加更多操作类型
    
    def _batch_database_insert(self, operations: List[Dict[str, Any]]):
        """批量数据库插入"""
        # 实现批量插入逻辑
        pass
    
    def _batch_database_update(self, operations: List[Dict[str, Any]]):
        """批量数据库更新"""
        # 实现批量更新逻辑
        pass


# 全局优化器实例
ui_optimizer = UIOptimizer()
batch_processor = BatchProcessor()


def optimize_large_list_rendering(items: List[Any], render_func: Callable, 
                                visible_count: int = 20, buffer_count: int = 5):
    """优化大列表渲染 - 虚拟滚动"""
    
    class VirtualListRenderer:
        def __init__(self):
            self.start_index = 0
            self.end_index = min(visible_count + buffer_count, len(items))
            self.rendered_items = {}
        
        def get_visible_items(self):
            """获取当前可见的项目"""
            visible_items = []
            for i in range(self.start_index, self.end_index):
                if i < len(items):
                    if i not in self.rendered_items:
                        self.rendered_items[i] = render_func(items[i], i)
                    visible_items.append(self.rendered_items[i])
            return visible_items
        
        def scroll_to(self, index: int):
            """滚动到指定位置"""
            self.start_index = max(0, index - buffer_count)
            self.end_index = min(len(items), index + visible_count + buffer_count)
            
            # 清理不再需要的渲染项
            to_remove = []
            for i in self.rendered_items:
                if i < self.start_index or i >= self.end_index:
                    to_remove.append(i)
            
            for i in to_remove:
                del self.rendered_items[i]
    
    return VirtualListRenderer()


def debounce(wait_seconds: float):
    """防抖装饰器"""
    def decorator(func):
        timer = None
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal timer
            
            def call_func():
                func(*args, **kwargs)
            
            if timer:
                timer.cancel()
            timer = threading.Timer(wait_seconds, call_func)
            timer.start()
        
        return wrapper
    return decorator


def throttle(limit_seconds: float):
    """节流装饰器"""
    def decorator(func):
        last_called = 0
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_called
            now = time.time()
            
            if now - last_called >= limit_seconds:
                last_called = now
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


# 使用示例和工具函数
def cleanup_memory():
    """手动内存清理"""
    performance_optimizer.auto_cleanup()


def get_performance_report() -> str:
    """生成性能报告"""
    stats = performance_optimizer.get_performance_stats()
    
    report_lines = [
        "# 性能报告",
        f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 内存使用情况",
        f"- 当前内存: {stats['memory'].get('memory_rss', 0):.1f} MB",
        f"- 内存占用率: {stats['memory'].get('memory_percent', 0):.1f}%",
        f"- 内存警告次数: {stats['memory_warnings_count']}",
        "",
        "## CPU使用情况", 
        f"- CPU占用率: {stats.get('cpu_percent', 0):.1f}%",
        "",
        "## 缓存统计",
        f"- 缓存命中: {stats['cache_stats']['hits']}",
        f"- 缓存未命中: {stats['cache_stats']['misses']}",
        f"- 命中率: {stats['cache_stats']['hits'] / (stats['cache_stats']['hits'] + stats['cache_stats']['misses']) * 100:.1f}%" if (stats['cache_stats']['hits'] + stats['cache_stats']['misses']) > 0 else "- 命中率: 0%",
        "",
        "## 垃圾回收",
        f"- 对象总数: {stats['object_count']}",
        f"- GC计数: {stats['gc_counts']}",
    ]
    
    return "\n".join(report_lines)


# 清理资源的函数
def cleanup_performance_resources():
    """清理性能优化相关资源"""
    performance_optimizer.stop_monitoring()
    ui_optimizer.clear_render_cache()
    batch_processor.flush()


if __name__ == "__main__":
    # 测试性能优化功能
    print("性能优化器测试")
    
    @performance_timer
    @cached_result(ttl_seconds=10)
    def test_function(x):
        time.sleep(0.1)  # 模拟耗时操作
        return x * 2
    
    # 测试缓存和计时
    for i in range(5):
        result = test_function(i)
        print(f"结果: {result}")
    
    # 重复调用测试缓存
    for i in range(3):
        result = test_function(1)  # 应该命中缓存
        print(f"缓存测试: {result}")
    
    # 输出性能报告
    print("\n" + get_performance_report()) 