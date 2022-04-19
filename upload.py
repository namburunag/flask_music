import time
import os
import re
import eyed3
import sqlite3
from flask import *  
app = Flask(__name__) 

@app.route('/')  
def options(): 
    conn = sqlite3.connect('test.db')
    print ("Opened database successfully");
    c = conn.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='MPT' ''')
    if c.fetchone()[0]!=1:
        print('Table does not exists.')
        conn.execute('''CREATE TABLE MPT (NAME TEXT NOT NULL,META TEXT NOT NULL);''')
        print ("Table created successfully")
    conn.close() 
    return render_template("options.html")

@app.route('/upload')  
def upload():  
    return render_template("upload.html")  
 
@app.route('/upload_success', methods = ['POST'])  
def upload_success():  
    if request.method == 'POST':  
        f = request.files['file']  
        fn=str(time.time())+"_"+f.filename
        f.save(fn)
        try:
            audio=eyed3.load(fn)
            aat= audio.tag.artist+" # "+audio.tag.album+" # "+audio.tag.title         
            with sqlite3.connect("test.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO MPT (NAME, META) VALUES (?,?)",(fn, aat))            
                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"
        finally:
            con.close() 
            return render_template("success.html", name = f.filename)

@app.route('/search')  
def search():  
    return render_template("search.html")

@app.route('/show')  
def show():  
    mptsearch=request.args.get('mptsearch')
    conn = sqlite3.connect('test.db')
    conn.row_factory = sqlite3.Row
    w=""
    if mptsearch!=None:
        w="WHERE "
        m=mptsearch.split()
        m=['META LIKE "%'+i+'%"' for i in m]
        w=w+" AND ".join(m)
    cur = conn.cursor()
    l=cur.execute('SELECT * FROM MPT '+w).fetchall()
    conn.close()
    urls={}
    for i in l:
        urls[i[0]]=i[1]
    return render_template("show.html", urls=urls)

@app.route('/<name>')
def play(name):
    return send_from_directory('./', name)

@app.route('/delete/<name>')
def delete(name):
    try:
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        print("Connected to database")
        cursor.execute("DELETE from MPT where NAME="+"'"+name+"'")
        conn.commit()
        print("Deleted successfully ")
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to delete:", error)
    finally:
        if conn:
            conn.close()
            print("Connection is closed")
    os.remove("./"+name)
    return render_template("success.html",name=name)

if __name__ == '__main__':  
    app.run(debug = True)
