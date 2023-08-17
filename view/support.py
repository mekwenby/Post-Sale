from flask import Blueprint, render_template, request, g, redirect, make_response
import database.api as api
import mytools

bp = Blueprint('S', __name__)
"""
后台路由
"""


@bp.route('/Login', methods=['POST', 'GET'])
def Login():
    """登录"""
    if request.method == 'GET':
        m_token = request.cookies.get('m_token')
        manage = api.form_token_get_manege(m_token)
        if manage is not None:
            return redirect('/S/dashboard')
        else:
            return render_template('New_S_L.html')

    else:
        name = request.form.get('name')
        pwd = request.form.get('pwd')

        stats = api.manage_login(name=name, pwd=pwd)
        if not stats:
            """用户名或密码错误时"""
            return render_template('New_S_L.html', msg='999')
        else:
            """正确"""
            manage = api.get_manege(name=name)
            manage.m_token = mytools.get_m_token(name)
            manage.save()
            response = make_response(redirect('/S/dashboard'))
            # cookie 有效期为 20小时 60秒*60分钟*20
            response.set_cookie(key='m_token', value=manage.m_token, max_age=int(60 * 60 * 20))

            return response


@bp.route('/logout')
def logout():
    """注销"""
    resp = make_response(redirect('/S'))
    # 删除Token
    resp.delete_cookie('m_token')
    return resp


@bp.route('/all')
def spall():
    m_token = request.cookies.get('m_token')
    if m_token is not None:  # token 为空时
        return render_template('S_ALL.html', plist=api.get_all_problem(), tite='全部工单')
    else:
        return redirect('/S')


@bp.route('/processing')
def processing():
    m_token = request.cookies.get('m_token')
    if m_token is not None:
        return render_template('S_ALL.html', plist=api.get_allprocessing_problem(), tite='全部待处理')
    else:
        return redirect('/S')


@bp.route('/myprocessing')
def my_processing():
    m_token = request.cookies.get('m_token')
    if m_token is not None:
        manage = api.form_token_get_manege(m_token)
        if manage is not None:
            return render_template('S_ALL.html', plist=api.get_manage_processing_problem(manage.name), tite='我的待处理')
        else:
            return redirect('/S')
    else:
        return redirect('/S')


@bp.route('/view/<rid>')
def view(rid):
    """工单处理视图"""
    m_token = request.cookies.get('m_token')
    if m_token is not None:
        user = api.form_token_get_manege(m_token)
        if user is not None:
            p = api.get_problem(rid)
            p.solve_name = user.name
            p_list = api.get_problem_att(rid)
            manege_list = api.get_manage_list()
            return render_template('_S_View.html', p=p, p_list=p_list, user=user, manege_list=manege_list)
        else:
            return redirect('/S')

    else:
        return redirect('/S')


@bp.route('/pull/<rid>', methods=["POST"])
def s_r_pull(rid):
    """修改工单状态"""
    p = api.get_problem(rid)
    status = request.form.get('status')
    assign = request.form.get('assign')
    p.solve_name = assign
    p.solve = status
    if status == '已完成' or status == '关闭':
        p.submit = False
        api.add_problem_Smessage(rid=rid, uid="System", text=f"{assign} 将工单状态修改为已完成")
    else:
        p.submit = True

    p.save()

    return redirect('/S/dashboard')


@bp.route('/search')
def search():
    """搜索"""
    search_text = request.args.get('search')
    # print(search_text)
    return render_template('S_ALL.html', plist=api.search_problem(search_text), tite=f'搜索 {search_text}')


@bp.route('/ChangePassword', methods=['POST', 'GET'])
def change_password():
    """
    修改密码
    原密码正确返回 True
    """
    m_token = request.cookies.get('m_token')
    user = api.form_token_get_manege(m_token)
    if request.method == 'GET' and user is not None:  # 判断用户Token是否失效
        return render_template('ChangePassword.html')

    elif request.method == 'POST' and user is not None:
        # original new confirm
        new = request.form.get('new')
        original = request.form.get('original')
        if user.passwd == original:  # 判断原密码是否正确
            user.passwd = new
            user.save()
            """此处必须返回字符串,否则后端报错"""
            return 'True'
        else:
            return 'False'

    else:
        return redirect('/logout')


@bp.route('/addManage', methods=['POST', 'GET'])
def add_manage():
    m_token = request.cookies.get('m_token')
    user = api.form_token_get_manege(m_token)
    if request.method == 'GET' and user is not None:
        if user.name == "超管":
            return render_template('S_add_Manage.html')
        else:
            return render_template('S_Remind.html', msg="权限不足")

    elif request.method == 'POST' and user is not None:
        # original new confirm
        name = request.form.get('name')
        passwd = request.form.get('passwd')
        user = api.get_manege(name)
        if user is None:
            # 用户名不存在时创建
            api.add_manage(name=name, passwd=passwd)
            return 'True'
        else:
            return 'False'

    else:
        return redirect('/logout')


@bp.route('/dashboard')
def dashboard():
    m_token = request.cookies.get('m_token')
    user = api.form_token_get_manege(m_token)
    if user is not None:
        data = api.get_manage_p_list(user.name)
        print(data)
        return render_template('S_Dashboard.html', title='Dashboard', data=data)
    else:
        return redirect('/S')


