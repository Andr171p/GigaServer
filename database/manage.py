import json


def add_comment(data):
    with open(r"/app/database/comments.json",
              "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def see_comments():
    feedback_text = []
    with open(r"/app/database/comments.json",
              "r", encoding="utf-8") as file:
        comments = json.load(file)

    for comment in comments:
        username = comment['username']
        text = comment['comment']
        feedback_text.append([username, text])

    return feedback_text
