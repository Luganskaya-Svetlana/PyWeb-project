from flask import Flask
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our_secret_key'


def main():
    db_session.global_init("db/all.db")
    app.run('127.0.0.1', 9090, debug=True)


if __name__ == '__main__':
    main()