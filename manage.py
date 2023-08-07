import sys
from database import create_table, recover

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        command = sys.argv[1]

        if command == 'create_table':
            create_table()
        elif command == 'recover':
            recover()
    else:
        text = """
        Post-Sale Help
        ----------------------------------
        create_table            创建数据库
        recover                 重置数据库
        
        """
        print(text)
