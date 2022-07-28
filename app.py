from crypt import methods
from importlib.resources import contents
from flask import Flask, make_response, request, jsonify, session
from  werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from auth import token_required
from models import db, User, Todo
from flask_sqlalchemy import SQLAlchemy
import jwt

app = Flask(__name__)

app.config['SECRET_KEY'] = 'MySecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)


@app.route('/user', methods=['GET'])
@token_required
def user(current_user):
    return jsonify({
        "message": "successfully retrieved user profile",
        "user_data": current_user.username
    })

@app.route('/login', methods=['GET','POST'])
def login():
    auth = request.json

    if not auth or not auth.get('username') or not auth.get('password'):
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
        )
  
    user = User.query.filter_by(username = auth.get('username')).first()

    if not user:
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
        )
  
    if user.password == auth.get('password'):
        token = jwt.encode({
            'username': user.username,
            'exp' : datetime.utcnow() + timedelta(hours= 24)
        }, app.config['SECRET_KEY'])

        return make_response(jsonify({'token' : token}), 201)

    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'}
    )

@app.route('/signup', methods =['POST'])
def signup():
    data = request.json
    # gets name, email and password
    username = data.get('username')
    password = data.get('password')
  
    # checking for existing user
    user = User.query.filter_by(username = username).first()
    if not user:
        user = User(
            username = username,
            password = password
        )
        db.session.add(user)
        db.session.commit()
  
        return make_response('Successfully registered.', 201)
    else:
        # returns 202 if user already exists
        return make_response('User already exists. Please Log in.', 202)


@app.route('/insert', methods=['POST','GET'])
@token_required
def insert_task(current_user):
    data = request.json
    task_content = data.get('content')
    user_id = current_user.id
    new_task = Todo(content=task_content, user_id=user_id)
    try:
            db.session.add(new_task)
            db.session.commit()
            return 'Task created successfully'
    except Exception as e:
        return jsonify({
            "message": "failed to create tasks",
            "error": str(e),
            "data": None
        }), 500
  
@app.route('/update/<int:id>', methods=['POST','GET'])
@token_required
def update_task(current_user,id):
    task_to_update = Todo.query.get_or_404(id)
    data = request.json
    update_content = data.get('content')
    task_to_update.content = update_content
    try:
        db.session.commit()
        return 'Task updated successfully'
    except:
        return 'Task update issue'

    print('update', task_to_update.content)
    return 'hi'

@app.route('/delete/<int:id>', methods=['GET'])
@token_required
def delete_task(current_user, id):
        task_to_delete = Todo.query.get_or_404(id)
        try:
            db.session.delete(task_to_delete)
            db.session.commit()
            return 'Task deleted successfully'
        except:
            return 'Delete Exception'    

@app.route("/tasks/", methods=["GET"])
@token_required
def get_tasks(current_user):
    try:
        tasks = Todo().query.filter_by(user_id=current_user.id).all()
        # res = []
        # for task in tasks:
        #     res.append(task.content)
        
        return jsonify({
            "message": "successfully retrieved all tasks",
            "data": [formatTask(task) for task in tasks]
        })
    except Exception as e:
        return jsonify({
            "message": "failed to retrieve all tasks",
            "error": str(e),
            "data": None
        }), 500

def formatTask(task):
    return {
        'id': task.id,
        'content': task.content,
        'date_creates': task.date_creates
    } 
if __name__ == '__main__':
    app.run(debug=True)