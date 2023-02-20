from database import DB

from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/login')
def login():
    if "id" not in request.args:
        return jsonify({"message": "Нет параметра ID", "status": False})
    usr = DB.get_user_by_chat_id(request.args["id"])
    if usr is None:
        return jsonify({"message": "Пользователь не найден", "status": False})
    # if not usr[2]:
    DB.change_user_by_id(tg_chat_id=request.args["id"], new_device=1)
    DB.create_notify(request.args["id"], "Устройство успешно добавлено!")
    return jsonify({"message": "Ok", "status": True})

@app.route("/banned_app_report")
def ban_app_report():
    if "name" not in request.args:
        return jsonify({"message": "Нет параметра Name", "status": False})
    if "chat_id" not in request.args:
        return jsonify({"message": "Нет параметра Chat_id", "status": False})
    DB.create_notify(request.args["chat_id"], f"Открыто запрещенное приложение - <b>{request.args['name']}</b>!")
    return jsonify({"message": "Ok", "status": True})

@app.route("/banned_site_report")
def ban_site_report():
    if "name" not in request.args:
        return jsonify({"message": "Нет параметра Name", "status": False})
    if "chat_id" not in request.args:
        return jsonify({"message": "Нет параметра Chat_id", "status": False})
    DB.create_notify(request.args["chat_id"], f"Открыт запрещенный сайт - <b>{request.args['name']}</b>!")
    return jsonify({"message": "Ok", "status": True})

