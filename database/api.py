import datetime
import os

import mytools.Mek_master
from database import Problem, User, ProblemAtt, ProblemMessage, ManageUser
from threading import Thread

"""
数据库查询接口 20230807
"""


def problem_init_message(rid):
    """
    工单初始化时将图片转换为消息
    """
    file_path = os.path.join('static', 'upload', rid)
    try:  # 处理没有附件的情况
        file_list = os.listdir(file_path)
    except:
        file_list = []

    p = Problem.get(rid=rid)

    for file in file_list:
        if os.path.splitext(file)[-1] in ['.png', '.jpg', '.jpeg', '.webp']:  # 是图片
            ProblemMessage.create(problem=p, text=file, type='img', author=p.establish_id)

        else:  # 不是图片
            ProblemMessage.create(problem=p, text=f'已上传附件 {file}', type='file', author=p.establish_id)


def upload_att_message(rid, file, up_name):
    """上传文件时生成消息"""
    manage_name_list = [manage.name for manage in get_manage_list()]
    source = 'user'
    print(manage_name_list)
    if up_name in manage_name_list:
        source = 'manage'
    if Problem.get_or_none(rid=rid) is not None:
        if os.path.splitext(file)[-1] in ['.png', '.jpg', '.jpeg', '.webp']:  # 是图片的情况

            ProblemMessage.create(problem=Problem.get(rid=rid), text=file, type='img', author=up_name, source=source)
        else:  # 不是图片
            ProblemMessage.create(problem=Problem.get(rid=rid), text=f'已上传附件 {file}', type='file', author=up_name,
                                  source=source)


def save_problem(rid, project_name, user_name, module, ptype, text, uid):
    """
    保存工单
    :param rid:
    :param project_name:
    :param user_name:
    :param module:
    :param ptype:
    :param text:
    :param uid:
    :return:
    """
    if Problem.get_or_none(rid=rid) is None:  # 该工单号不存在时创建
        Problem.create(rid=rid, project_name=project_name, user_name=user_name, ptype=ptype, text=text, module=module,
                       establish_id=uid)
        # 通过协程初始化图文消息
        t1 = Thread(target=problem_init_message, args=(rid,))
        t1.run()


def get_all_problem():
    """
    获取全部工单,只取前100个
    :return:
    """
    return [p for p in Problem.select().order_by(Problem.generate_time.desc()).limit(100)]


def get_allprocessing_problem():
    """
    获取全部待处理工单
    :return:
    """
    return [p for p in Problem.select().where(Problem.submit == True).order_by(Problem.generate_time.desc())]


def get_manage_processing_problem(name):
    """
    获取指定manage待处理工单
    :param name:
    :return:
    """
    return [p for p in Problem.select().where((Problem.solve_name == name) & (Problem.submit == True)).order_by(
        Problem.generate_time.desc())]


def get_user_problem(uid):
    """
    获取指定用户的工单
    :param uid:
    :return:
    """
    return [p for p in Problem.select().where(Problem.establish_id == uid).order_by(Problem.generate_time.desc())]


def get_manage_list():
    """
    获取全部manage列表 前端指派时需要
    :return:
    """
    return [name for name in ManageUser().select()]


def get_user(uid, bm):
    """
    处理用户模型
    用于存在则返回,不存在则创建
    :param bm: 部门
    :param uid: 用户名
    :return:
    """
    user = User.get_or_none(uid=uid)
    if user is not None:  # 用户存在

        if user.department != bm and bm != '默认':  # 部门有变动时
            user.department = bm
            user.save()

        return user
    else:  # 用户不存在时就创建
        user = User.create(uid=uid, department=bm)
        return user


def from_u_token_user(u_token):
    """
    从token获得用户信息
    :param u_token:
    :return:
    """
    user = User.get_or_none(u_token=u_token)
    if user is not None:
        return user


def upload_file(rid, filename, up_name):
    """
    处理上传文件数据库写入
    :param rid:
    :param filename:
    :param up_name:
    :return:
    """
    ProblemAtt.create(rid=rid, filename=filename, up_name=up_name)
    # 通过协程把附件转换为消息
    t1 = Thread(target=upload_att_message, args=(rid, filename, up_name))
    t1.run()


def get_problem(rid):
    """获得一张工单"""
    p = Problem.get_or_none(rid=rid)
    if p is not None:
        return p
    return None


def get_problem_att(rid):
    """获得工单附件列表"""
    file_list = [p for p in ProblemAtt.select().where(ProblemAtt.rid == rid)]
    return file_list


def add_problem_message(rid, uid, text):
    """处理消息"""
    problem = Problem.get(rid=rid)  # 获得工单
    if not problem.submit:  # 处理工单完结后,用户再次回复把工单标记为 再反馈 状态
        problem.submit = True
        problem.solve = '再反馈'
        problem.save()

    if problem.solve == '待回复':
        problem.solve = '处理中'
        problem.save()

    ProblemMessage.create(problem=problem, text=text, author=uid)  # 创建消息
    return True


def add_problem_Smessage(rid, uid, text):
    """处理manage消息"""
    problem = Problem.get(rid=rid)
    # problem.submit = True
    if problem.solve != '处理中':  # 回复后修改工单状态
        problem.solve = '处理中'
        problem.save()
    ProblemMessage.create(problem=problem, text=text, author=uid, source='manage')
    return True


def manage_login(name, pwd):
    """
    manage 登录
    :param name:
    :param pwd:
    :return:
    """
    # print(name, pwd)
    manege = ManageUser.get_or_none(name=name)
    if manege is not None:
        if pwd == manege.passwd:  # 判断密码是否正确
            return True
        else:
            return False
    else:
        return False


def get_manege(name):
    manege = ManageUser.get_or_none(name=name)
    return manege


def form_token_get_manege(token):
    """manage token 处理"""
    manege = ManageUser.get_or_none(m_token=token)
    return manege


def search_problem(text):
    """工单搜索接口 支持 rid project_name user_name """
    query = Problem.select().where(
        (Problem.rid.contains(text)) |
        (Problem.project_name.contains(text)) |
        (Problem.user_name.contains(text)) |
        (Problem.module.contains(text))
    )
    sorted_problems = query.order_by(Problem.generate_time.desc())
    return list(sorted_problems)


def add_manage(name, passwd):
    """添加Manege"""
    ManageUser.create(name=name, passwd=passwd)


def get_user_p_list(uid):
    待处理 = Problem.select().where(Problem.establish_id.contains(uid) & Problem.solve.contains("待处理")).count()
    处理中 = Problem.select().where(Problem.establish_id.contains(uid) & Problem.solve.contains("处理中")).count()
    待回复 = Problem.select().where(Problem.establish_id.contains(uid) & Problem.solve.contains("待回复")).count()
    已完成 = Problem.select().where(Problem.establish_id.contains(uid) & Problem.solve.contains("已完成")).count()
    # return [len(待处理), len(处理中), len(待回复), len(已完成)]
    return [待回复, 待处理, 处理中, 已完成]


def get_manage_p_list(uid):
    # 获取当前日期时间
    current_datetime = datetime.datetime.now()
    # 获取今天0点时间
    today_midnight = current_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    # 转换为UNIX时间戳
    unix_timestamp = today_midnight.timestamp()
    now_unix = int(unix_timestamp)

    待回复 = Problem.select().where(Problem.solve.contains("待回复")).count()
    待处理 = Problem.select().where(Problem.solve == "待处理").count()
    我的待处理 = Problem.select().where(
        Problem.solve_name.contains(uid) & Problem.submit == True).count()
    处理中 = Problem.select().where(Problem.solve.contains("处理中")).count()
    今日 = Problem.select().where(Problem.generate_time >= now_unix).count()
    今日完成 = Problem.select().where(Problem.generate_time >= now_unix and Problem.solve.contains("已完成")).count()
    总数 = Problem.select().count()

    # return [len(待处理), len(处理中), len(待回复), len(已完成)]
    return [待回复, 我的待处理, 待处理, 处理中, 今日, 总数, 今日完成]


def get_file_infos(id_):
    return ProblemAtt.get_or_none(id=id_)


def del_file(id_):
    file = get_file_infos(id_)
    print(file.filename, file.rid)
    msg = ProblemMessage.delete().where((ProblemMessage.type == 'img') &
                                        (ProblemMessage.problem_id == get_problem(
                                            file.rid)) & (ProblemMessage.text == file.filename))
    msg.execute()

    ProblemAtt.delete_by_id(id_)
