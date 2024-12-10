from flask import Flask, jsonify
from flask_cors import CORS

# initialize a flask application (app)
app = Flask(__name__)
CORS(app, supports_credentials=True, origins='*')  # Allow all origins (*)

# ... your existing Flask

# add an api endpoint to flask app
@app.route('/api/avika')
def get_avika():
    # start a list, to be used like a information database
    InfoDb = []

    InfoDb.append({
        "FirstName": "Avika",
        "LastName": "Prasad",
        "DOB": "January 22",
        "Residence": "San Diego",
        "Email": "avikapd22@gmail.com",
        "Favorite_Books": ["The Inheritance Games", "Harry Potter 1-7", "Mystiwick School of Musicraft", "The Hunger Games"]
    })
    return jsonify(InfoDb)

    
@app.route('/api/gabi')
def get_gabi():
    # start a list, to be used like a information database
    InfoDb = []

    # add a row to list, an Info record
    InfoDb.append({
        "FirstName": "Gabriela",
        "LastName": "Connelly",
        "DOB": "October 21",
        "Residence": "San Diego",
        "Email": "gabrielac@myyahoo.com",
        "Favorite_Books": ["Made You Up", "The Cruel Prince", "Diary of a Wimpy Kid 1-19", "Legend"]
    })
    return jsonify(InfoDb)


@app.route('/api/katherine')
def get_katherine():
    # start a list, to be used like a information database
    InfoDb = []

    # add a row to list, an Info record
    InfoDb.append({
        "FirstName": "Katherine",
        "LastName": "Chen",
        "DOB": "July 30",
        "Residence": "San Diego",
        "Email": "katherine.yx.chen@gmail.com",
        "Favorite_Books": ["A Court of Thornes and Roses", "Talon", "49 Miles Alone", "They Both Die in the End", "The Silent Patient"]
    })
    
    return jsonify(InfoDb)


@app.route('/api/soumini')
def get_soumini():
    # start a list, to be used like a information database
    InfoDb = []

    # add a row to list, an Info record
    InfoDb.append({
        "FirstName": "Soumini",
        "LastName": "Kandula",
        "DOB": "December 21",
        "Residence": "Alaska",
        "Email": "souminik21@gmail.com",
        "Favorite Books": ["Harry Potter 1-7", "The Silent Patient", "A Good Girl's Guide to Murder", "Legend", "The Fault in Our Stars"]
    })
    
    return jsonify(InfoDb)

@app.route('/api/aditi')
def get_aditi():
    # start a list, to be used like a information database
    InfoDb = []

    # add a row to list, an Info record
    InfoDb.append({
        "FirstName": "Aditi",
        "LastName": "Bandaru",
        "DOB": "May 21",
        "Residence": "San Diego",
        "Email": "aditib03015@stu.powayusd.com",
        "Favorite_Books": ["A Feast for Crows", "Scythe", "A Game of Thrones", "Wings of Fires", "Frankenstein"]
    })

    return jsonify(InfoDb)

@app.route('/api/maryam')
def get_maryam():
    # start a list, to be used like a information database
    InfoDb = []

    # add a row to list, an Info record
    InfoDb.append({
        "FirstName": "Maryam",
        "LastName": "Abdul-Aziz",
        "DOB": "November 23",
        "Residence": "The Bermuda Triangle",
        "Email": "maryama42841@stu.powayusd.com",
        "Favorite Books": ["The Outsiders", "Tex", "The Catcher in the Rye", "The Hunger Games", "Renegades"]
    })
    
    return jsonify(InfoDb)

@app.route('/')
def justin_did_this():
    html_content = """
    <html>
    <head>
        <title>Hellox</title>
    </head>
    <body>
        <h2>Hello, World!</h2>
        <p>Justin says hi. If your pages aren't uploading try killing your backend proceses.</p>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    # starts flask server on default port, http://127.0.0.1:5001
    app.run(port=5001)