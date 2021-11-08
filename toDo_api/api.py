#from typing_extensions import Required
from flask import Flask
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy, sqlalchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db = SQLAlchemy(app)


class ToDoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200))
    summary = db.Column(db.String(500))

# ~~~~~~~~| We nolonger need this now that the database has been created |~~~~~~~~~~~~~~~~~~
# db.create_all()


# class HelloWorld(Resource):
#       def get (self):
#           return{'data':'Hello, world!'}

# class HelloName(Resource):
#     def get (self, name):
#         return{'data' : 'Hello, {}'.format(name)}

# ~~~~~~~~~~~~| Storage we used before creating sqlite Database |~~~~~~~~~~~~~~~~
# todos = {
#     1:{"task": 'write a Hello Karios Program', "summary": 'Write good code using python' },
#     2:{"task": 'write a like Karios code', "summary": 'Always Write good code using python' },
#     3:{"task": 'write a Non- disclosure Agreement', "summary": 'Remember never to disclose anything.' },
#     4:{"task": 'write a Hello Stupid Program', "summary": 'We will be better sooner or later' },
# }
task_post_args = reqparse.RequestParser()
task_post_args.add_argument(
    "task", type=str, help="A task is required", required=True)
task_post_args.add_argument(
    "summary", type=str, help="A summary is required", required=True)

task_put_args = reqparse.RequestParser()
task_put_args.add_argument("task", type=str)
task_put_args.add_argument("summary", type=str)

resource_fields = {
    'id': fields.Integer,
    'task': fields.String,
    'summary': fields.String
}


class toDoList(Resource):
    def get(self):
        tasks = ToDoModel.query.all()
        todos = {}
        for task in tasks:
            todos[task.id] = {"task": task.task, "summary": task.summary}
        return todos


class ToDo(Resource):
    @marshal_with(resource_fields)
    def get(self, todo_id):
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404, message='Could not find task with that id')
        return task

 # ~~~~~~~~~~~~~| POST |~~~~~~~~~~~~~~~~
    @marshal_with(resource_fields)
    def post(self, todo_id):
        args = task_post_args.parse_args()
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if task:
            abort(409, message="Task ID already taken")

        todo = ToDoModel(
            id=todo_id, task=args['task'], summary=args['summary'])
        db.session.add(todo)
        db.session.commit()
        return todo, 201

        # appending
        # todos[todo_id]= {"task": args["task"], "summary": args["summary"]}
        # return todos[todo_id]

 # ~~~~~~~~~~~~~| DELETE |~~~~~~~~~~~~~~~~
    def delete(self, todo_id):
        task = ToDoModel.query.filter_by(id=todo_id).first()
        db.session.delete(task)
        return 'ToDo deleted', 204

# ~~~~~~~~~~~~~~| PUT |~~~~~~~~~~~~~~~~~~~
    @marshal_with(resource_fields)
    def put(self, todo_id):
        args = task_put_args.parse_args()
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404, message="Task doesn't exist, can't update")
        if args['task']:
            task.task = args['task']
        if args['summary']:
            task.summary = args['summary']
        db.session.commit()
        return task

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~| ENDPOINTS |~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# api.add_resource(HelloWorld, '/helloworld')
# api.add_resource(HelloName, '/helloworld/<string:name>')


api.add_resource(ToDo, '/todos/<int:todo_id>')
api.add_resource(toDoList, '/todos')


if __name__ == '__main__':
    app.run(debug=True)
