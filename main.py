# импортируем библиотеки
import logging
import json
import os

from flask import Flask, request

app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/')
@app.route('/index')
def index():
    return "Hello!"


animals_to_buy = ('слон', 'кролик')


@app.route("/post", methods=["POST"])
def main():
    logging.info(f"Request: {request.json}")
    response = {
        "session": request.json["session"],
        "version": request.json["version"],
        "response": {"end_session": False},
    }
    # Отправляем request.json и response в функцию handle_dialog.
    # Она сформирует оставшиеся поля JSON, которые отвечают
    # непосредственно за ведение диалога
    handle_dialog(request.json, response)
    logging.info(f"Response: {response}")
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req["session"]["user_id"]
    if req["session"]["new"]:
        sessionStorage[user_id] = {
            "suggests": [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ],
            "step": 0,
        }
        res["response"]["text"] = f"Привет! Купи {animals_to_buy[0]}а! "
        res["response"]["buttons"] = get_suggests(user_id)
        return


    # Сюда дойдем только, если пользователь не новый,
    # и разговор с Алисой уже был начат
    # Обрабатываем ответ пользователя.
    # В req['request']['original_utterance'] лежит весь текст,
    # что нам прислал пользователь
    # Если он написал 'ладно', 'куплю', 'покупаю', 'хорошо',
    # то мы считаем, что пользователь согласился.
    # Подумайте, всё ли в этом фрагменте написано "красиво"?
    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо'] or 'куп' in req['request']['original_utterance'].lower():
        # Пользователь согласился, прощаемся.
        step = sessionStorage[user_id]["step"]
        res["response"]["text"] = f"{animals_to_buy[step]}а можно найти на Яндекс.Маркете!"
        if step:
            res["response"]["end_session"] = True
        else:
            sessionStorage[user_id]["step"] += 1
            res["response"]["text"] += "\nА теперь купи кролика!"
        return
    step = sessionStorage[user_id]["step"]
    res["response"][
        "text"
    ] = f"Все говорят '{req['request']['original_utterance']}', а ты купи {animals_to_buy[step]}а!"
    res["response"]["buttons"] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]
    suggests = [{"title": suggest, "hide": True} for suggest in session["suggests"][:2]]
    session["suggests"] = session["suggests"][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append(
            {
                "title": "Ладно",
                "url": f"https://market.yandex.ru/search?text={animals_to_buy[session['step']]}",
                "hide": True,
            }
        )

    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
