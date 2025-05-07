import flask
from flask_sqlalchemy import SQLAlchemy


app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost/test_db7'
db = SQLAlchemy(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(512), nullable=False)

    def __init__(self, text, tags):
        self.text = text
        self.tags = [
            Tag(text=tag) for tag in tags.split(',')
        ]


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(32), nullable=False)

    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    message = db.relationship('Message', backref=db.backref('tags', lazy=True))


@app.route('/', methods=['GET'])
def hello():
    return flask.render_template('index.html', messages=Message.query.all())


@app.route('/add_message', methods=['POST'])
def add_message():
    text = flask.request.form['text']
    tag = flask.request.form['tag']
    # messages.append(Message(text, tag))
    db.session.add(Message(text, tag))
    db.session.commit()

    return flask.redirect(flask.url_for('hello'))




with app.app_context():
    db.create_all()
app.run()