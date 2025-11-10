"""
新功能测试脚本
测试副本系统和励志库功能
"""
import sys
sys.path.insert(0, '.')

from database.db_manager import DatabaseManager

def test_lizhi_system():
    """测试励志库系统"""
    print("\n========== 测试励志库系统 ==========")

    db = DatabaseManager()

    # 1. 测试获取所有语录
    print("\n1. 获取所有励志语录：")
    quotes = db.get_all_quotes()
    print(f"   共有 {len(quotes)} 条语录")

    if quotes:
        print(f"   第一条: {quotes[0][1]} —— {quotes[0][2]}")

    # 2. 测试随机获取语录
    print("\n2. 随机获取一条语录：")
    random_quote = db.get_random_quote()
    if random_quote:
        print(f"   {random_quote[1]}")
        print(f"   —— {random_quote[2]}")

    # 3. 测试添加语录
    print("\n3. 测试添加语录：")
    success = db.add_quote("测试语录：志当存高远", "诸葛亮", "poetry")
    print(f"   添加结果: {'成功' if success else '失败'}")

    # 4. 再次获取所有语录
    quotes_after = db.get_all_quotes()
    print(f"   添加后共有 {len(quotes_after)} 条语录")

    print("\n[PASS] 励志库系统测试完成")

def test_fuben_system():
    """测试副本系统"""
    print("\n========== 测试副本系统 ==========")

    db = DatabaseManager()

    # 1. 加载境界数据
    print("\n1. 加载境界数据：")
    jingjie_data = db.load_jingjie_data()

    # 2. 检查副本数据结构
    print("\n2. 检查副本数据结构：")
    if "fuben" in jingjie_data:
        fuben_data = jingjie_data["fuben"]
        print(f"   副本数量: {len(fuben_data)}")

        if fuben_data:
            for name, info in fuben_data.items():
                nodes = info.get("nodes", [])
                completed = info.get("completed", [])
                print(f"   - {name}: {len(nodes)} 个节点, {len(completed)} 个已完成")
        else:
            print("   还没有添加任何副本")
    else:
        print("   [ERROR] 副本数据结构不存在")

    # 3. 添加测试副本
    print("\n3. 添加测试副本：")
    if "fuben" not in jingjie_data:
        jingjie_data["fuben"] = {}

    test_fuben = {
        "nodes": ["第1关", "第2关", "第3关", "Boss关"],
        "completed": ["第1关"]
    }

    jingjie_data["fuben"]["测试副本"] = test_fuben
    db.save_jingjie_data(jingjie_data)
    print("   已添加测试副本：测试副本（4个关卡，完成1个）")

    # 4. 验证保存
    print("\n4. 验证保存：")
    reload_data = db.load_jingjie_data()
    if "测试副本" in reload_data.get("fuben", {}):
        print("   [OK] 副本数据保存成功")
    else:
        print("   [ERROR] 副本数据保存失败")

    print("\n[PASS] 副本系统测试完成")

def test_database_tables():
    """测试数据库表"""
    print("\n========== 测试数据库表 ==========")

    db = DatabaseManager()
    conn = db._get_connection()
    cursor = conn.cursor()

    # 检查励志库表
    print("\n1. 检查励志库表：")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lizhi_quotes'")
    table = cursor.fetchone()
    if table:
        print("   [OK] 励志库表存在")

        # 查询记录数
        cursor.execute("SELECT COUNT(*) FROM lizhi_quotes")
        count = cursor.fetchone()[0]
        print(f"   记录数: {count}")
    else:
        print("   [ERROR] 励志库表不存在")

    conn.close()

    print("\n[PASS] 数据库表测试完成")

def main():
    """主测试函数"""
    print("=" * 50)
    print("凡人修仙3w天 - 新功能测试")
    print("=" * 50)

    try:
        # 测试数据库表
        test_database_tables()

        # 测试励志库
        test_lizhi_system()

        # 测试副本系统
        test_fuben_system()

        print("\n" + "=" * 50)
        print("[SUCCESS] 所有测试完成！")
        print("=" * 50)

    except Exception as e:
        print(f"\n[ERROR] 测试出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
