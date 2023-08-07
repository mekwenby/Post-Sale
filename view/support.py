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
            return redirect('/S/processing')
        else:
            return render_template('S_L.html')

    else:
        name = request.form.get('name')
        pwd = request.form.get('pwd')

        stats = api.manage_login(name=name, pwd=pwd)
        if not stats:
            """用户名或密码错误时"""
            return render_template('S_L.html', msg='999')
        else:
            """正确"""
            manage = api.get_manege(name=name)
            manage.m_token = mytools.get_m_token(name)
            manage.save()
            response = make_response(redirect('/S/all'))
            response.set_cookie(key='m_token', value=manage.m_token, max_age=int(60 * 60 * 16))

            return response


@bp.route('/logout')
def logout():
    """注销"""
    resp = make_response(redirect('/S'))
    resp.delete_cookie('m_token')
    return resp


@bp.route('/all')
def spall():
    m_token = request.cookies.get('m_token')
    if m_token is not None:
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

    else:
        p.submit = True

    p.save()

    return redirect('/S/processing')


@bp.route('/search')
def search():
    """搜索"""
    search_text = request.args.get('search')
    print(search_text)
    return render_template('S_ALL.html', plist=api.search_problem(search_text), tite=f'搜索 {search_text}')