import secrets
from flask import Flask, render_template, request, Response, jsonify
from functools import wraps
from uuid import uuid4
import notes_lib

app = Flask(__name__)


def auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if (uuid := request.cookies.get("uuid", default=None)) and notes_lib.valid_uuid(uuid):
            return f(uuid, *args, **kwargs)
        new_uuid = str(uuid4())
        resp = f(new_uuid, *args, **kwargs)
        resp.set_cookie("uuid", value=new_uuid)
        return resp
    return decorated


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/create", methods=["post"])
@auth
def create(uuid):
    name = request.form.get('name', default='', type=str)
    body = request.form.get('body', default='', type=str)
    if not name or not body:
        return jsonify({
            "error": True,
            "message": "Name and body must be specified"
        })
    success, msg = notes_lib.write_note(uuid, name, body)
    return jsonify({
        "error": not success,
        "message": msg
    })

@app.route("/read", methods=["get"])
@auth
def read(uuid):
    name = request.args.get('name', default='', type=str)
    if not name:
        return jsonify({
            "error": True,
            "message": "Name must be specified"
        })
    success, msg = notes_lib.read_note(uuid, name)
    return Response(msg, 200, content_type="text/plain")

@app.route("/list", methods=["get"])
@auth
def list(uuid):
    success, notes = notes_lib.list_notes(uuid)
    if not success:
        notes = []
    return jsonify({
        "error": False,
        "notes": notes
    })