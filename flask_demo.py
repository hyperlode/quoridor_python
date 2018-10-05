# http://flask.pocoo.org/

# python pip install flask
# cd .. go to folder of this script
# set FLASK_APP=flask_demo.py  #name of this script in environmental variable.
# flask run #execute, web server started.
# go to brower. in address bar: http://127.0.0.1:5000/  or localhost:5000
# contents are displayed.
#will only run on localhost. To make accessible by other ips on the network: http://flask.pocoo.org/docs/1.0/quickstart/#quickstart ("externally visible server")

from flask import Flask, url_for, request
import quoridor as tttp
import time 

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"

@app.route("/quoridor")
def quoridor():
    time.sleep(1)
    q = tttp.Quoridor({"player_1":"Joos", "player_2":"Lode", "game":"n s n s n s n 6e 4d 4g e5 6c a6 b6 4b 5a 3a c3 1c 2b 1a 2d 1e 2f 1g 3h h1 sw"})
    board_string = q.board_as_html()
    return board_string
    
@app.route("/lode")
def lode():
    return "you went to localhost:5000/lode didn't you?"


@app.route("/testingUrl/<var>")
def url_test(var):
    return ("to check which url will trigger this function, test it without browser just in the python script. Make sure url_for is imported.")


@app.route('/login', methods=['GET', 'POST'])
def login():
    # see http://flask.pocoo.org/docs/1.0/quickstart/#quickstart  --> HTTP Methods
    # default is always only GET.
    if request.method == 'POST':
        return "do_the_login()"
    else:
        return "show_the_login_form()"


def run():
    # will run the server until exit.
    app.run()


if __name__ == "__main__":
    with app.test_request_context():
        print(url_for('url_test', var = "value"))
    run()
