import os

import mytools.Mek_master
from database import Problem, User, ProblemAtt, ProblemMessage, ManageUser
from threading import Thread


def problem_init_message(rid):
    """
    工单初始化时将图片转换为消息
    """
    file_path = os.path.join('static', 'upload', rid)
    try:
        file_list = os.listdir(file_path)
    except:
        file_list = []
    for file in file_list:
        if os.path.splitext(file)[-1] in ['.png', '.jpg', '.jpeg', '.webp']:
            ProblemMessage.create(problem=Problem.get(rid=rid), text=file, type='img')

        else:
            ProblemMessage.create(problem=Problem.get(rid=rid), text=f'已上传附件 {file}', type='file')


def upload_att_message(rid, file, up_name):
    """上传文件时生成消息"""
    if Problem.get_or_none(rid=rid) is not None:
        if os.path.splitext(file)[-1] in ['.png', '.jpg', '.jpeg', '.webp']:
            ProblemMessage.create(problem=Problem.get(rid=rid), text=file, type='img', author=up_name)
        else:
            ProblemMessage.create(problem=Problem.get(rid=rid), text=f'已上传附件 {file}', type='file', author=up_name)


def save_problem(rid, project_name, user_name, module, ptype, text, uid):
    Problem.create(rid=rid, project_name=project_name, user_name=user_name, ptype=ptype, text=text, module=module,
                   establish_id=uid)

    t1 = Thread(target=problem_init_message, args=(rid,))
    t1.run()


def get_all_problem():
    return [p for p in Problem.select().order_by(Problem.generate_time.desc()).limit(100)]


def get_allprocessing_problem():
    return [p for p in Problem.select().where(Problem.submit == True).order_by(Problem.generate_time.desc())]


def get_manage_processing_problem(name):
    return [p for p in Problem.select().where((Problem.solve_name == name) & (Problem.submit == True)).order_by(
        Problem.generate_time.desc())]


def get_user_problem(uid):
    return [p for p in Problem.select().where(Problem.establish_id == uid).order_by(Problem.generate_time.desc())]


def get_manage_list():
    return [name for name in ManageUser().select()]


def get_user(uid):
    user = User.get_or_none(uid=uid)
    if user is not None:
        return user
    else:
        user = User.create(uid=uid)
        return user


def from_u_token_user(u_token):
    user = User.get_or_none(u_token=u_token)
    if user is not None:
        return user


def upload_file(rid, filename, up_name):
    ProblemAtt.create(rid=rid, filename=filename, up_name=up_name)
    t1 = Thread(target=upload_att_message, args=(rid, filename, up_name))
    t1.run()


def get_problem(rid):
    p = Problem.get_or_none(rid=rid)
    if p is not None:
        return p
    return None


def get_problem_att(rid):
    file_list = [p for p in ProblemAtt.select().where(ProblemAtt.rid == rid)]
    return file_list


def add_problem_message(rid, uid, text):
    problem = Problem.get(rid=rid)
    if not problem.submit:  # 处理再次回复
        problem.submit = True
        problem.solve = '再反馈'
        problem.save()
    ProblemMessage.create(problem=problem, text=text, author=uid)
    return True


def add_problem_Smessage(rid, uid, text):
    problem = Problem.get(rid=rid)
    problem.submit = True
    problem.solve = '处理中'
    problem.save()
    ProblemMessage.create(problem=problem, text=text, author=uid, source='manage')
    return True


def manage_login(name, pwd):
    print(name, pwd)
    manege = ManageUser.get_or_none(name=name)
    if manege is not None:
        if pwd == manege.passwd:
            return True
        else:
            return False
    else:
        return False


def get_manege(name):
    manege = ManageUser.get_or_none(name=name)
    return manege


def form_token_get_manege(token):
    manege = ManageUser.get_or_none(m_token=token)
    return manege


def search_problem(text):
    """工单搜索接口 支持 rid project_name user_name """
    query = Problem.select().where(
        (Problem.rid.contains(text)) |
        (Problem.project_name.contains(text)) |
        (Problem.user_name.contains(text))
    )
    sorted_problems = query.order_by(Problem.generate_time.desc())
    return list(sorted_problems)
