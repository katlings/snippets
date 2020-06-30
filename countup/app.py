import datetime

from dateparser import parse
from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def countup():
    with open('timestamp.txt') as f:
        ts = f.read()
    try:
        last_date = parse(ts.strip())
        days_since = datetime.datetime.now() - last_date
        return render_template('countup.html', days=days_since.days)
    except Exception as e:
        print(e)
        return 'Unknown'


@app.route('/reset')
def reset():
    with open('timestamp.txt', 'w+') as f:
        f.write(datetime.datetime.now().isoformat())

    return countup()


if __name__ == '__main__':
    app.run()
