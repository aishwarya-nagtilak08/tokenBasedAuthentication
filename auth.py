from functools import wraps
from flask import Flask, make_response, request, jsonify, session
import jwt
from flask import current_app as app
import models

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
  
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
            current_user = models.User.query.filter_by(username = data['username']).first()
        except Exception as e:
            return jsonify({
                "message": "Token is invalid !!",
                "error": str(e),
                "data": None
            }), 500
        return  f(current_user, *args, **kwargs)
    return decorated
