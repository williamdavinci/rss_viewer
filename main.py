from datetime import datetime
from flask import Flask, render_template, request
import bleach
import feedparser
import requests
import validators
from bs4 import BeautifulSoup as bs

app = Flask(__name__)
app.secret_key = 'xxxxxx'
allowed_tags = ['p', 'strong', 'blockquote', 'li', 'ul', 'ol'] 

@app.route('/')
def index():
    """RSS feed viewer main page"""
    url = request.args.get('url')
    header = ""
    code = 0
    err = None
    feed = None
    data = None
    default = "https://"
    contentType = None
    if validators.url(url): 
        try:
            response = requests.head(url, timeout=5) #, headers=customHeaders)
            contentType = response.headers['content-type']
            code = response.status_code
            header = contentType
            default = url
        except Exception as e:
            err = "That host... is a ghost"
        print(contentType)
        if contentType in ["text/xml", "application/xml", "application/rss+xml; charset=UTF-8"]:
            feed = feedparser.parse(url)
            data = [{"title":feed.feed.title, "description":feed.feed.description}]
            title = feed.feed.title
            for entry in feed.entries:
                data.append({
                    "title": entry.title,
                    "date_str": entry.published,
                    "date_int": entry.published_parsed,
                    "description": bleach.clean(entry.description, strip=True,tags=allowed_tags, attributes={'strong': ['style']})
                    })
    return render_template('index.html', request=request, header=header, code=code, default=default, err=err, data=data)


@app.errorhandler(404)
def page_not_found(e):
    """Handler for 404"""
    return render_template('404.html', errormsg=e)

if __name__ == '__main__':
    app.run(debug=True, port=8001)
