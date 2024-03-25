from flask import Flask, request, render_template
from flask import Markup

import google.generativeai as palm
import replicate
import os
import sqlite3
import datetime

palm.configure(api_key="AIzaSyDgmTVwLcUX8D6yi3GeBEIS7y5m9j2CEaw")
model = {
    "model": "models/chat-bison-001",
}

os.environ["REPLICATE_API_TOKEN"] = "r8_WR6BJXiTA7ce5FwsJBT8Glc4Cwz5j8013rgxP"

change_name_flag = 1
name = ""

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():
    return(render_template("index.html"))

@app.route("/main", methods=["GET","POST"])
def main():
    global name, change_name_flag
    if change_name_flag == 1:
        name = request.form.get("name")
        change_name_flag = 0
        dt = datetime.datetime.now()
        conn = sqlite3.connect('log.db')
        c = conn.execute("insert into customer (name,timestamp) values (?,?)",(name,dt))
        conn.commit()
        c.close()
        conn.close()
    return(render_template("main.html",r=name))

@app.route("/palm", methods=["GET","POST"])
def palm_flask():
    return(render_template("palm.html"))

@app.route("/mj", methods=["GET","POST"])
def mj():
    return(render_template("mj.html"))

@app.route("/palm_query", methods=["GET","POST"])
def palm_query():
    q = request.form.get("q")
    print(q)
    r = palm.chat(
        **model,
        messages=q
    )
    print(r.last)
    return(render_template("palm_reply.html",r=r.last))

@app.route("/mj_query", methods=["GET","POST"])
def mj_query():
    q = request.form.get("q")
    r = replicate.run(
        "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf", 
        input={"prompt": q}
    )
    return(render_template("mj_reply.html",r=r[0]))

@app.route("/db_query", methods=["GET","POST"])
def db_query():
    conn = sqlite3.connect('log.db')
    c = conn.execute("select * from customer")
    r = ""
    for row in c:
        print(row)
        r = r+str(row)+"<br>"
    c.close()
    conn.close()
    r = Markup(r)
    return(render_template("db_query.html",r=r))

@app.route("/db_delete", methods=["GET","POST"])
def db_delete():
    return(render_template("db_delete.html"))

@app.route("/db_delete_success", methods=["GET","POST"])
def db_delete_sucess():
    password = request.form.get("password")
    if password == "1234":
        conn = sqlite3.connect('log.db')
        c = conn.execute("delete from customer")
        conn.commit()
        c.close()
        conn.close()
        return(render_template("db_delete_sucess.html"))
    else:
        print("password wrong")
        return(render_template("db_delete_fail.html"))

@app.route("/end", methods=["GET","POST"])
def end():
    global change_name_flag
    change_name_flag = 0
    return(render_template("index.html",r=name))

if __name__ == "__main__":
    app.run()
