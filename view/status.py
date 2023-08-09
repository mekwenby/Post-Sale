from flask import Blueprint, request, redirect, jsonify
import database.api as api
import mytools

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
