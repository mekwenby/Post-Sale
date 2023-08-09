import os
from flask import Flask, redirect, render_template, request, make_response, jsonify
from flask_bootstrap import Bootstrap4

import database
import mytools
from database import api
from view.support import bp as support_view
from view.status import bp as status_view

app = Flask(__name__)
bootstrap = Bootstrap4(app=app)

# 本地加载bootstrap,默认使用CDN加载bootstrap
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

app.register_blueprint(support_view, url_prefix='/S')
app.register_blueprint(status_view, url_prefix='/status')


@app.before_request
def _db_connect():
    """请求开始时链接数据库"""
    #print('db.connect')
    database.db.connect()


@app.teardown_request
def _db_close(exc):
    """请求结束时关闭数据库"""
    if not database.db.is_closed():
        database.db.close()


@app.template_filter('time_ftm')
def time_ftm(value):
    """将数据库读取的时间格式化为Web页面显示格式"""
    try:
        datev = mytools.Mek_master.from_unix_time(value)
        return datev[1]
    except:
        return ''


@app.template_filter('text_br')
def time_ftm(value):
    """处理前端换行"""
    formatted_text = value.replace('\n', '<br>')
    return formatted_text


@app.route('/')
def hello_world():
    uid = request.args.get('uid')
    u_token = request.cookies.get('u_token')
    # print(uid, u_token)
    if uid is None and u_token is None:  # 没有uid也没有cookie
        uid = 'Guest'
        user = api.get_user(uid)
        user.u_token = mytools.get_u_token(uid)
        user.save()
        response = make_response(render_template('index.html'))
        response.set_cookie('u_token', user.u_token)

    elif uid is not None and u_token is None:  # 有uid 没有cookie
        user = api.get_user(uid)
        user.u_token = mytools.get_u_token(uid)
        user.save()
        response = make_response(render_template('index.html'))
        response.set_cookie('u_token', user.u_token)

    elif uid is not None and u_token is not None:
        user = api.from_u_token_user(u_token)
        if user is not None:
            response = make_response(render_template('index.html'))
        else:
            response = make_response(redirect('/'))
            response.delete_cookie('u_token')
            return response
    else:
        response = make_response(render_template('index.html'))

    return response


# 通过path登录
@app.route('/uid/<uid>')
def hello_uid(uid=None):
    if uid is None:
        uid = 'Guest'
    user = api.get_user(uid)
    user.u_token = mytools.get_u_token(uid)
    user.save()
    response = make_response(render_template('index.html'))
    response.set_cookie('u_token', user.u_token)
    return response


@app.route('/register', methods=["POST", "GET"])
def register():
    """创建工单路由"""
    if request.method == 'GET':
        u_token = request.cookies.get('u_token')
        if u_token is not None:
            # print(u_token)
            user = api.from_u_token_user(u_token)
            return render_template('register.html', rid=mytools.get_problem_id(), user=user)
        else:
            return redirect('/')

    if request.method == 'POST':
        rid = request.form.get('rid')
        department = request.form['department']
        name = request.form['name']
        module = request.form['module']
        description = request.form['description']
        problem_type = request.form.get('problem_type')
        uid = request.form.get('uid')
        # print(rid)
        api.save_problem(rid=rid, project_name=department, user_name=name, module=module, text=description,
                         ptype=problem_type, uid=uid)

        return redirect('/my')


@app.route('/all')
def palls():
    return render_template('all.html', plist=api.get_all_problem())


@app.route('/my')
def my_all():
    """我的工单路由"""
    u_token = request.cookies.get('u_token')
    if u_token is not None:
        # print(u_token)
        user = api.from_u_token_user(u_token)

        try:
            plist = api.get_user_problem(user.uid)
        except:
            plist = []

        return render_template('all.html', plist=plist)
    else:
        return redirect('/')


@app.route('/view/<rid>')
def view(rid):
    """查看工单路由"""
    u_token = request.cookies.get('u_token')
    if u_token is not None:
        user = api.from_u_token_user(u_token)
        p = api.get_problem(rid)
        p_list = api.get_problem_att(rid)
        # print(user.uid, p.rid, p_list)
        return render_template('_View.html', p=p, p_list=p_list, user=user)

    else:
        return redirect('/')


@app.route('/_view/<rid>')
def _view(rid):
    """查看工单**测试**"""
    u_token = request.cookies.get('u_token')
    if u_token is not None:
        user = api.from_u_token_user(u_token)
        p = api.get_problem(rid)
        p_list = api.get_problem_att(rid)
        # print(user.uid, p.rid, p_list)
        return render_template('_View.html', p=p, p_list=p_list, user=user)

    else:
        return redirect('/')


@app.route('/upload_test', methods=['POST'])
def upload_test():
    """文件上传"""
    rid = request.form.get('rid')
    up_name = request.form.get('up_name')
    if up_name is None:
        up_name = 'Infinite'

    def is_allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'zip', 'rar', 'pdf',
                                                                          'txt', 'doc', 'docx', 'xls', 'xlsx', 'xlsm']

    if 'file' in request.files:
        uploaded_file = request.files['file']
        if uploaded_file and is_allowed_file(uploaded_file.filename):
            # 处理上传的文件，例如保存到特定位置
            file_path = os.path.join('static', 'upload', rid)
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            uploaded_file.save(os.path.join(file_path, uploaded_file.filename))

            api.upload_file(rid, uploaded_file.filename, up_name)

            return '文件上传成功'
        else:
            return "只能上传'png', 'jpg', 'jpeg', 'zip', 'rar', 'pdf','txt'格式的文件"
    else:
        return '没有选择文件'


@app.route('/Message', methods=['POST'])
def Message():
    """
    前端消息发送
    :return:
    """
    # print(request.cookies.get('u_token'))
    rid = request.form.get('rid')
    uid = request.form.get('author')
    text = request.form.get('text')

    # print(f'rid:{rid}  uid:{uid}  text:{text}')
    state = api.add_problem_message(rid=rid, uid=uid, text=text)
    response_data = {"success": state}
    return jsonify(response_data)


@app.route('/SMessage', methods=['POST'])
def SMessage():
    """Manage消息发送"""
    # print(request.cookies.get('m_token'))
    rid = request.form.get('rid')
    uid = request.form.get('author')
    text = request.form.get('text')

    # print(f'rid:{rid}  uid:{uid}  text:{text}')
    state = api.add_problem_Smessage(rid=rid, uid=uid, text=text)
    response_data = {"success": state}
    return jsonify(response_data)


@app.route('/search')
def search():
    """搜索"""
    search_text = request.args.get('search')
    return render_template('all.html', plist=api.search_problem(search_text))


@app.route('/S')
def support():
    """后台登录入口"""
    return redirect('/S/Login')


if __name__ == '__main__':
    app.run(debug=True)
