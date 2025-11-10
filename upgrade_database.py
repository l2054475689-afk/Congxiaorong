"""
数据库升级脚本 - 添加fuben支持
"""
import sqlite3
import os

def upgrade_database():
    """升级数据库，添加fuben类型支持"""

    # 数据库路径
    if os.name == 'nt':  # Windows
        db_path = os.path.expanduser(r'~\AppData\Local\FanRenXiuXian\immortal_cultivation.db')
    else:
        db_path = os.path.expanduser('~/.fanrenxiuxian/immortal_cultivation.db')

    print(f"数据库路径: {db_path}")

    if not os.path.exists(db_path):
        print("数据库文件不存在，跳过升级")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("\n开始升级数据库...")

        # 1. 创建新表（包含fuben类型）
        print("1. 创建新的skills表...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skills_new (
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

        # 2. 复制数据
        print("2. 复制现有数据...")
        cursor.execute('''
            INSERT INTO skills_new (id, name, realm_id, skill_type, nodes_json, completed_json, created_at)
            SELECT id, name, realm_id, skill_type, nodes_json, completed_json, created_at
            FROM skills
        ''')

        # 3. 删除旧表
        print("3. 删除旧表...")
        cursor.execute('DROP TABLE skills')

        # 4. 重命名新表
        print("4. 重命名新表...")
        cursor.execute('ALTER TABLE skills_new RENAME TO skills')

        # 5. 提交更改
        conn.commit()
        print("\n[OK] 数据库升级成功！")
        print("现在skills表支持 'gongfa', 'secret_art', 'fuben' 三种类型")

        conn.close()

    except Exception as e:
        print(f"\n[ERROR] 数据库升级失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 50)
    print("数据库升级工具 - 添加副本支持")
    print("=" * 50)

    upgrade_database()

    print("\n升级完成！现在可以使用副本功能了。")
    print("=" * 50)
