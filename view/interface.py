import datetime

from flask import Blueprint, request, redirect, jsonify, make_response
import database.api as api
import mytools

"""

第三方获取数据API

"""

bp = Blueprint('interface', __name__)


@bp.route("/create", methods=["POST"])
def create():
    """
    创建工单
    :return:
    """

    # 获取表单数据
    rid = mytools.get_problem_id()
    uid = request.form.get('uid')
    department = request.form['bm']
    name = request.form['phone']
    module = request.form['module']
    description = request.form['text']
    problem_type = request.form.get('type')
    # 获取用户信息,创建token
    user = api.get_user(uid, department)
    user.u_token = mytools.get_u_token(uid)
    user.save()
    # 创建工单
    if uid is not None and department is not None and name is not None and module is not None \
            and description is not None and problem_type is not None:
        api.save_problem(rid=rid, project_name=department, user_name=name, module=module, text=description,
                         ptype=problem_type, uid=uid)
        response = make_response(jsonify({"status": True, "rid": rid}))
        response.set_cookie('u_token', user.u_token)
        return response
    else:

        response = make_response(jsonify({"status": False, "rid": None}))
        response.set_cookie('u_token', user.u_token)
        return response


@bp.route("/get_messages/<rid>", methods=["GET"])
def get_messages(rid):
    p = api.get_problem(rid)
    if p is not None:
        mess = [{"up_time": p.generate_time, "type": 'text', "text": p.text, "author": p.establish_id}]
        for m in p.Message:
            mess.append({"up_time": m.up_time, "type": m.type, "text": m.text, "author": m.author})
        return jsonify({"data": mess})
    else:
        return jsonify({"data": []})


@bp.route("/get_user_order/<uid>", methods=["GET"])
def get_user_order(uid):
    """
    获取用户未完成的工单状态
    :return:
    """
    p_list = []
    for p in api.get_user_problem(uid):
        p_list.append({'rid': p.rid, "module": p.module, "type": p.ptype, "text": p.text,
                       "generate_time": p.generate_time, "solve_name": p.solve_name, "status": p.solve})
    return jsonify({"data": p_list})
