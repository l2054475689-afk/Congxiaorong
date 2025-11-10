#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI接口集成测试脚本

测试功能：
1. AI管理器基本功能
2. OpenAI提供商接口
3. 诗句系统集成
4. 配置保存和加载
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ai_manager():
    """测试AI管理器"""
    print("🔧 测试AI管理器...")
    
    try:
        from ai_providers.ai_manager import ai_manager
        
        # 测试获取可用提供商
        providers = ai_manager.get_available_providers()
        print(f"✅ 可用提供商: {len(providers)} 个")
        for provider in providers:
            status_text = " (未支持)" if provider.get("disabled") else ""
            print(f"   - {provider['label']}{status_text}")
        
        # 测试配置状态
        is_configured = ai_manager.is_configured()
        print(f"✅ AI配置状态: {'已配置' if is_configured else '未配置'}")
        
        # 测试默认诗句生成
        poetry = ai_manager.generate_poetry("励志")
        print(f"✅ 默认诗句生成: {poetry}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI管理器测试失败: {e}")
        return False


def test_openai_provider():
    """测试OpenAI提供商（无需真实API密钥）"""
    print("\n🤖 测试OpenAI提供商...")
    
    try:
        from ai_providers.openai_provider import OpenAIProvider
        
        # 测试创建提供商实例
        provider = OpenAIProvider("test_key")
        print(f"✅ 提供商名称: {provider.get_provider_name()}")
        
        # 测试配置架构
        schema = provider.get_config_schema()
        print(f"✅ 配置项数量: {len(schema)} 个")
        for key, config in schema.items():
            print(f"   - {config['label']}: {config['type']}")
        
        # 测试状态获取
        status = provider.get_status()
        print(f"✅ 提供商状态: {status['connection_status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI提供商测试失败: {e}")
        return False


def test_poetry_system():
    """测试诗句系统"""
    print("\n📜 测试诗句系统...")
    
    try:
        from systems.poetry_system import PoetrySystem
        from database.db_manager import DatabaseManager
        
        # 创建诗句系统实例
        db = DatabaseManager()
        poetry_system = PoetrySystem(db)
        
        # 测试基本功能
        print(f"✅ 内置诗句数量: {len(poetry_system.default_poetry)}")
        
        # 测试分类功能
        categories = poetry_system.get_categories()
        print(f"✅ 诗句分类: {categories}")
        
        # 测试随机诗句
        random_poetry = poetry_system.get_random_poetry("励志")
        print(f"✅ 随机励志诗句: {random_poetry['text']} —{random_poetry['author']}")
        
        # 测试添加自定义诗句
        success = poetry_system.add_custom_poetry(
            "测试诗句：道路千万条，安全第一条",
            "测试作者",
            "测试分类"
        )
        print(f"✅ 添加自定义诗句: {'成功' if success else '失败'}")
        
        # 测试今日诗句功能
        should_show = poetry_system.should_show_daily_poetry()
        print(f"✅ 今日是否显示诗句: {should_show}")
        
        if should_show:
            daily_poetry = poetry_system.get_daily_poetry()
            print(f"✅ 今日诗句: {daily_poetry['text']}")
        
        # 测试统计信息
        stats = poetry_system.get_poetry_statistics()
        print(f"✅ 诗句统计: 总数{stats['total_poetry']}, 自定义{stats['custom_poetry']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 诗句系统测试失败: {e}")
        return False


def test_ai_configuration():
    """测试AI配置功能"""
    print("\n⚙️ 测试AI配置...")
    
    try:
        from ai_providers.ai_manager import ai_manager
        
        # 测试配置架构
        schema = ai_manager.get_provider_config_schema("openai")
        if schema:
            print(f"✅ OpenAI配置架构获取成功")
            required_fields = [k for k, v in schema.items() if v.get('required')]
            print(f"   必填字段: {required_fields}")
        
        # 测试状态获取
        all_status = ai_manager.get_all_providers_status()
        print(f"✅ 所有提供商状态获取成功")
        for name, status in all_status.items():
            print(f"   {status['name']}: {status['connection_status']}")
        
        # 测试配置保存和加载
        ai_manager.save_config()
        print(f"✅ 配置保存成功")
        
        return True
        
    except Exception as e:
        print(f"❌ AI配置测试失败: {e}")
        return False


def test_settings_integration():
    """测试设置系统集成"""
    print("\n🔧 测试设置系统集成...")
    
    try:
        from systems.settings import SettingsSystem
        from database.db_manager import DatabaseManager
        
        # 创建设置系统实例
        db = DatabaseManager()
        settings = SettingsSystem(db)
        
        # 测试设置创建
        settings_view = settings.create_settings_view()
        print(f"✅ 设置视图创建成功")
        
        # 测试AI设置部分
        ai_settings = settings._create_ai_settings()
        print(f"✅ AI设置部分创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 设置系统集成测试失败: {e}")
        return False


def test_poetry_dialog():
    """测试诗句弹窗功能（模拟）"""
    print("\n💬 测试诗句弹窗功能...")
    
    try:
        from systems.poetry_system import PoetrySystem
        from database.db_manager import DatabaseManager
        
        db = DatabaseManager()
        poetry_system = PoetrySystem(db)
        
        # 模拟每日诗句检查
        should_show = poetry_system.should_show_daily_poetry()
        print(f"✅ 每日诗句检查: {'需要显示' if should_show else '今日已显示'}")
        
        # 获取今日诗句
        daily_poetry = poetry_system.get_daily_poetry()
        print(f"✅ 今日诗句获取成功:")
        print(f"   内容: {daily_poetry['text']}")
        print(f"   作者: {daily_poetry.get('author', '未知')}")
        print(f"   分类: {daily_poetry.get('category', '其他')}")
        print(f"   来源: {daily_poetry.get('source', '未知')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 诗句弹窗测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始AI接口集成测试...")
    print("=" * 60)
    
    tests = [
        ("AI管理器", test_ai_manager),
        ("OpenAI提供商", test_openai_provider),
        ("诗句系统", test_poetry_system),
        ("AI配置", test_ai_configuration),
        ("设置集成", test_settings_integration),
        ("诗句弹窗", test_poetry_dialog),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！AI接口集成功能正常。")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
        return False


def test_with_real_api():
    """使用真实API密钥测试（可选）"""
    print("\n🔑 真实API测试（需要API密钥）...")
    
    api_key = input("请输入OpenAI API密钥（按回车跳过）: ").strip()
    
    if not api_key:
        print("⏭️ 跳过真实API测试")
        return True
    
    try:
        from ai_providers.ai_manager import ai_manager
        
        # 配置OpenAI
        config = {"api_key": api_key}
        success = ai_manager.configure_provider("openai", config)
        
        if success:
            print("✅ OpenAI配置成功")
            
            # 测试连接
            connection_ok = ai_manager.test_provider_connection("openai")
            print(f"✅ 连接测试: {'成功' if connection_ok else '失败'}")
            
            if connection_ok:
                # 设置为当前提供商
                ai_manager.set_current_provider("openai")
                
                # 测试生成诗句
                poetry = ai_manager.generate_poetry("修仙")
                print(f"✅ AI生成诗句: {poetry}")
                
                # 测试事件分析
                analysis = ai_manager.analyze_mood_event("今天完成了一个重要项目")
                print(f"✅ AI事件分析: {analysis}")
        
        return True
        
    except Exception as e:
        print(f"❌ 真实API测试失败: {e}")
        return False


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║              AI接口集成测试工具                        ║
    ║                                                      ║
    ║  测试AI管理器、OpenAI提供商、诗句系统等功能             ║
    ║                                                      ║
    ║  版本: v3.0.0                                        ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    try:
        # 运行基础测试
        basic_success = run_all_tests()
        
        if basic_success:
            # 询问是否进行真实API测试
            print("\n" + "=" * 60)
            test_real = input("是否进行真实API测试？(y/N): ").lower().strip()
            
            if test_real == 'y':
                test_with_real_api()
        
        print(f"\n🏁 测试完成！")
        
    except KeyboardInterrupt:
        print("\n👋 用户中断测试")
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {e}")
    
    input("\n按回车键退出...") 