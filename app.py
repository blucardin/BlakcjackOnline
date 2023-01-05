import time
from flask import Flask, render_template, request
import sqlite3
import os
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from multiprocessing import Value

conn = sqlite3.connect('database', check_same_thread=False)
c = conn.cursor()
# create a table called rooms if it doesn't exist with room_id and epoch_time
c.execute('''CREATE TABLE IF NOT EXISTS rooms (room_id text, timestamp integer)''')
conn.commit()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

counter = Value('i', 0)


@app.route('/')
def homepage():  # put application's code here
    return render_template('index.html')


@app.route('/create')
def create():
    with counter.get_lock():
        counter.value += 1
        new_room_id = counter.value
        #update database with new room id and datestamp
        c.execute('''INSERT INTO rooms VALUES (?, ?)''', (new_room_id, time.time()))
        print(new_room_id)
        return render_template('createRoom.html', room_id=new_room_id)


@app.route('/room')
def room():
    room_id = request.args.get('room_id')
    # check if the room exists in the database
    c.execute('''SELECT * FROM rooms WHERE room_id=?''', (room_id,))
    if c.fetchone() is None:
        return render_template('joinRoom.html', invalid=True)

    return render_template('enterRoom.html', room_id=room_id)


@app.route('/join')
def join():
    return render_template('joinRoom.html', invalid=False)


if __name__ == '__main__':
    socketio.run(app)
