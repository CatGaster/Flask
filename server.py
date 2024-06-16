from flask import Flask, request, Response, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError


import pydantic

from schema import CreateMessageSchema, Schema, UpdateMessageSchema
from models import Messages, Session

app = Flask("app")


class HttpError(Exception):

    def __init__(self, status_code: int, error_message: str | dict):
        self.status_code = status_code
        self.error_message = error_message

    def __str__(self):
        return str(self.error_message)

def validate(schema_cls: Schema, json_data: dict):
    try:
        return schema_cls(**json_data).dict(exclude_unset=True)
    except pydantic.ValidationError as err:
        error = err.errors()[0]
        error.pop("ctx", None)
        raise HttpError(409, error)

@app.errorhandler(HttpError)
def error_handler(err: HttpError):
    json_response = jsonify({"error": err.error_message})
    json_response.status_code = err.status_code
    return json_response


@app.before_request
def before_request():
    session = Session()
    request.session = session

@app.after_request
def after_request(response: Response):
    request.session.close()
    return response

def get_user_id(user_id: int):
    user = request.session.get(Messages, user_id)
    if user is None:
        raise HttpError(404, "user not found")
    return user

def add_user(user: Messages):
    request.session.add(user)
    try:
        request.session.commit()
    except IntegrityError:
        raise HttpError(400, "user already exists")
    return user

class MessagesView(MethodView):
    

    @property
    def session(self):
        return request.session
    

    def get(self, id):
        messages_id = get_user_id(id)
        return jsonify(messages_id.json)

    def post(self):
        json_data = validate(CreateMessageSchema, request.json)
        message = add_user(Messages(**json_data))
        return jsonify(message.json)
    
    def patch(self, id):
        json_data = validate(UpdateMessageSchema, request.json)
        message = get_user_id(id)
        for field, value in json_data.items():
            setattr(message, field, value)
        message = add_user(message)
        return jsonify(message.json)
    
    def delete(self, id):
        message = get_user_id(id)
        self.session.delete(message)
        self.session.commit()
        return jsonify({"status": "deleted"})
        
massage_view = MessagesView.as_view("messages")

app.add_url_rule("/messages/", view_func=massage_view, methods=["POST"])
app.add_url_rule("/messages/<int:id>", view_func=massage_view, methods=["GET","PATCH", "DELETE"])
app.run()