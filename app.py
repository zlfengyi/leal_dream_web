# app.py
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import threading
import json
import time
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tweets.db'
db = SQLAlchemy(app)

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    task_id = db.Column(db.String(200), nullable=True)
    task_file_name = db.Column(db.String(200), nullable=True)

with app.app_context():
    # db.drop_all()
    db.create_all()

def call_midjourney(tweet):
    with app.app_context():
        url = "https://api.midjourneyapi.io/v2/imagine"
        headers = {"Authorization": "cc778a04-390b-4188-826b-638304dd6411", "Content-Type": "application/json", "Accept-Charset": "utf-8" }
        data = {"prompt": tweet.content}
        json_data = json.dumps(data, ensure_ascii=False)  # 将data转换为JSON格式字符串，并保留中文字符
        print(json_data)

        print(json_data.encode('utf-8'))
        response = requests.post(url, data=json_data.encode('utf-8'), headers=headers)
        print(response.content)

        tweet.task_id = response.content
        db.session.add(tweet)
        db.session.commit()

        # 循环100次去查询midjourney是否完成
        for i in range(100):
            time.sleep(3)
            url_result = 'https://api.midjourneyapi.io/v2/result'
            response = requests.post(url_result, data=tweet.task_id, headers=headers)
            print(response.content)
            if 'imageURL' in response.json():
                img_result = requests.get(response.json()['imageURL'])
                path = f'static/{tweet.task_id}.png'
                with open(path, 'wb') as f:
                    f.write(img_result.content)
                tweet.task_file_name = path
                db.session.commit()
                break


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form['username']
        content = request.form['content']
        tweet = Tweet(username=username, content=content)
        db.session.add(tweet)
        db.session.commit()
        thread = threading.Thread(target=call_midjourney, args=(tweet,))
        thread.start()
        return redirect('/')
    tweets = Tweet.query.order_by(Tweet.timestamp.desc()).all()
    for t in tweets:
        if (datetime.utcnow() - t.timestamp < timedelta(hours=1)):
            t.recent = 1
        else:
            t.recent = 0
        t.display_timestamp = t.timestamp + timedelta(hours=8)
    
    return render_template('home.html', tweets=tweets)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='80', debug=True)