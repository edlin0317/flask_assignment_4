from flask import Flask, jsonify, request
import requests
import json

app = Flask(__name__)
#json 中文回傳
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def home():
    return 'Welcome to Assignment 4!'

def _news_api(q, n=10, w=50):
    #string to list
    q = q.split(',')
    #assignment 1, refresh every 5 minute
    url = 'https://linebot4106029040.herokuapp.com/getjson/yahoo-news.json'
    r = requests.get(url)
    news = r.json()
    result = []
    for elem in news:
        #check title
        title_ok = True
        for qq in q:
            if qq in elem['title']:
                continue
            title_ok = False
            break
        #check content
        content_ok = True
        for qq in q:
            if qq in elem['content']:
                continue
            content_ok = False
            break
        #enough result
        if len(result) >= n:
            break
        #meet one of the requirements
        if title_ok or content_ok:
            title = elem['title']
            content = elem['content'][:w]
            result.append({
                'title':title,
                'content':content
            })
    return result
    
@app.route('/news_api')
def news_api():
    try:
        q = request.args.get('q')
        n = int(request.args.get('n'))
        w = int(request.args.get('w'))
        data = json.loads(json.dumps(_news_api(q, n, w)))
        return jsonify(data)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run()