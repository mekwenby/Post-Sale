import sys
import getpass
from database import create_table, recover
from database.api import get_manege, add_manage

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        command = sys.argv[1]

        if command == 'create_table':  # 创建数据表
            create_table()

        elif command == 'recover':  # 重置数据表
            recover()

        elif command == 'add':  # 添加Manage用户
            if len(sys.argv) >= 3:
                name = sys.argv[2]
            else:
                name = input("输入要添加的用户名:")
            manage_user = get_manege(name)
            if manage_user is None:
                passwd = getpass.getpass("输入新密码:")
                re_passwd = getpass.getpass("再次输入新密码:")
                if passwd == re_passwd:
                    add_manage(name=name, passwd=passwd)
                    print(f'{name} 创建成功.')
                else:
                    print("两次输入的密码不一致.")
            else:
                print(f'用户名: {name} 已存在.')

        elif command == 'passwd':  # 修改manage用户密码
            if len(sys.argv) >= 3:
                name = sys.argv[2]
            else:
                name = input("输入要修改密码的用户名:")
            manage_user = get_manege(name)
            if manage_user is not None:
                passwd = getpass.getpass("输入新密码:")
                re_passwd = getpass.getpass("再次输入新密码:")
                if passwd == re_passwd:
                    manage_user.passwd = passwd
                    manage_user.save()
                    print(f'{name} 密码修改成功.')
                else:
                    print("两次输入的密码不一致.")
            else:
                print(f'用户名: {name} 不存在.')
        else:
            print(f"没有'{command}命令,请查看帮助.'")
    else:
        text = """
        Manage Help
        ----------------------------------
        create_table            创建数据表
        recover                 重置数据库
        add                     添加用户 <m_id>
        passwd                  重新设置用户密码 <m_id>
        """
        print(text)
