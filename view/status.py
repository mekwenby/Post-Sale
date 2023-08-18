import datetime

from flask import Blueprint, request, redirect, jsonify
import database.api as api

bp = Blueprint('status', __name__)
"""
状态API
"""


@bp.route('/message_length/<rid>')
def message_length(rid=None):
    if rid is not None:
        p = api.get_problem(rid)
        return jsonify({'rid': rid, 'length': len(p.Message)})
    else:
        return jsonify({'rid': 'None', 'length': 0})


@bp.route('/processing')
def processing():
    """获取全部待处理数量"""
    # m_token = request.cookies.get('m_token')
    return jsonify({'processing': len(api.get_allprocessing_problem())})


@bp.route('/myprocessing')
def myprocessing():
    """获取我的待处理数量"""
    m_token = request.cookies.get('m_token')
    user = api.form_token_get_manege(m_token)
    if user is not None:  # 处理m_token 失效的情况
        return jsonify({'processing': len(api.get_manage_processing_problem(user.name))})
    else:
        return jsonify({'processing': 0})


@bp.route("/ping")
def ping():
    return jsonify({"status": "OK", "date": datetime.datetime.now()})
