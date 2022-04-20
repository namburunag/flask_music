import time
import os
import eyed3
import sqlite3
from flask import *
from werkzeug.utils import secure_filename

app = Flask(__name__) 

@app.route('/')  
def options():
    return render_template("options.html")

@app.route('/upload')  
def upload():  
    return render_template("upload.html")  
 
@app.route('/upload_success', methods = ['POST'])  
def upload_success():
    status=""
    if request.method == 'POST':  
        f = request.files['file']  
        fn=str(time.time())+"_"+secure_filename(f.filename)
        f.save("./audio_files/"+fn)
        audio=eyed3.load("./audio_files/"+fn)
        aat= audio.tag.artist+" # "+audio.tag.album+" # "+audio.tag.title+" # "+secure_filename(f.filename)
        try:
            conn = sqlite3.connect("./database/test.db")
            cur = conn.cursor()
            cur.execute("INSERT INTO MPT (NAME, META) VALUES (?,?)",(fn, aat))            
            conn.commit()
            print("Record successfully added")
        except:
            conn.rollback()
            print("error in insert operation")
            status="Not"
        finally:
            conn.close() 
            return render_template("success.html", name=secure_filename(f.filename), status=status)

@app.route('/search')  
def search():  
    return render_template("search.html")

@app.route('/show')  
def show():  
    mptsearch=request.args.get('mptsearch')
    w=""
    if mptsearch!=None:
        w="WHERE "
        m=mptsearch.split()
        m=['META LIKE "%'+i+'%"' for i in m]
        w=w+" AND ".join(m)
    try:
        conn = sqlite3.connect('./database/test.db')
        cur = conn.cursor()
        l=cur.execute('SELECT * FROM MPT '+w).fetchall()
    except sqlite3.Error as error:
        print("Failed to delete:", error)
    finally:
        if conn:
            conn.close()
            print("Connection is closed")
    urls={}
    for i in l:
        urls[i[0]]=i[1]
    return render_template("show.html", urls=urls)

@app.route('/<name>')
def play(name):
    return send_from_directory('./audio_files', name)

@app.route('/delete/<name>')
def delete(name):
    status=""
    try:
        conn = sqlite3.connect('./database/test.db')
        cursor = conn.cursor()
        print("Connected to database")
        cursor.execute("DELETE from MPT where NAME="+"'"+name+"'")
        conn.commit()
        print("Deleted successfully ")
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to delete:", error)
        status="Not"
    finally:
        if conn:
            conn.close()
            print("Connection is closed")
    if not os.path.exists("./audio_files/"+name):
        status="Already"
    if status=="":
        os.remove("./audio_files/"+name)
    return render_template("success.html",name=name, status=status)

if __name__ == '__main__':
    if not os.path.exists("database"):
        os.makedirs("database")
    if not os.path.exists("audio_files"):
        os.makedirs("audio_files")
    try:
        conn = sqlite3.connect('./database/test.db')
        print ("Opened database successfully");
        c = conn.cursor()
        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='MPT' ''')
        if c.fetchone()[0]!=1:
            print('Table does not exists.')
            conn.execute('''CREATE TABLE MPT (NAME TEXT NOT NULL,META TEXT NOT NULL);''')
            print ("Table created successfully")
    except sqlite3.Error as error:
        print("Failed:", error)
    finally:
        if conn:
            conn.close()
            print("Connection is closed")
    app.run(debug = True)
