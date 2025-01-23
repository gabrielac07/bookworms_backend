from flask import Flask, jsonify, Blueprint
from flask_restful import Api
from flask_cors import CORS
from __init__ import app

app_api = Blueprint('app_api', __name__, url_prefix='/api/app')
api = Api(app_api)

@app.route('/api/avika')
def get_avika():
    avika_info = [{
        "FirstName": "Avika",
        "LastName": "Prasad",
        "DOB": "January 22",
        "Residence": "San Diego",
        "Email": "avikapd22@gmail.com",
        "Favorite_Books": ["The Inheritance Games", "Harry Potter 1-7", "Mystiwick School of Musicraft", "The Hunger Games"]
    }]
    return jsonify(avika_info)

@app.route('/api/gabi')
def get_gabi():
    gabi_info = [{
        "FirstName": "Gabriela",
        "LastName": "Connelly",
        "DOB": "December 16",
        "Residence": "San Diego",
        "Email": "gabrielac@myyahoo.com",
        "Favorite_Books": ["Made You Up", "The Cruel Prince", "Diary of a Wimpy Kid 1-19", "Legend"]
    }]
    return jsonify(gabi_info)

@app.route('/api/katherine')
def get_katherine():
    katherine_info = [{
        "FirstName": "Katherine",
        "LastName": "Chen",
        "DOB": "July 30",
        "Residence": "San Diego",
        "Email": "katherine.yx.chen@gmail.com",
        "Favorite_Books": ["A Court of Thornes and Roses", "Talon", "49 Miles Alone", "They Both Die in the End", "The Silent Patient"]
    }]
    return jsonify(katherine_info)

@app.route('/api/soumini')
def get_soumini():
    soumini_info = [{
        "FirstName": "Soumini",
        "LastName": "Kandula",
        "DOB": "December 21",
        "Residence": "Alaska",
        "Email": "souminik21@gmail.com",
        "Favorite_Books": ["Harry Potter 1-7", "The Silent Patient", "A Good Girl's Guide to Murder", "Legend", "The Fault in Our Stars"]
    }]
    return jsonify(soumini_info)

@app.route('/api/aditi')
def get_aditi():
    aditi_info = [{
        "FirstName": "Aditi",
        "LastName": "Bandaru",
        "DOB": "May 21",
        "Residence": "San Diego",
        "Email": "aditib03015@stu.powayusd.com",
        "Favorite_Books": ["A Feast for Crows", "Scythe", "A Game of Thrones", "Wings of Fires", "Frankenstein"]
    }]
    return jsonify(aditi_info)

@app.route('/api/maryam')
def get_maryam():
    maryam_info = [{
        "FirstName": "Maryam",
        "LastName": "Abdul-Aziz",
        "DOB": "November 23",
        "Residence": "The Bermuda Triangle",
        "Email": "maryama42841@stu.powayusd.com",
        "Favorite Books": ["The Outsiders", "Tex", "The Catcher in the Rye", "The Hunger Games", "Renegades"]
    }]
    return jsonify(maryam_info)

@app.route('/')
def say_hello():
    html_content = """
    <html>
    <head>
        <title>Bookworms</title>
    </head>
    <body>
        <h2>Hello, meet the team of the Bookworms!</h2>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    # starts flask server on default port, http://127.0.0.1:5001
    app.run(port=5001)
