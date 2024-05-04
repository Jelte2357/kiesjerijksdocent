import os
import json
from datetime import datetime
from itertools import groupby
from flask import Flask, flash, redirect, render_template, request, session, render_template_string
from flask_session import Session
from string import digits, punctuation
from datetime import timedelta
import pickle


# Configure application
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_DURATION"] = timedelta(days=7)
Session(app)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index(): 
    if session.get("has_voted"):
        return redirect("/gestemd")
    return render_template("index.html")

@app.route("/stem", methods=["GET", "POST"]) #the argument "p" will be given, and should be handled by the server
def stem():
    if request.method == "GET":
        if session.get("has_voted"):
            return redirect("/gestemd")
        
        if not request.args.get("p"):
            return redirect("/")
        if request.args.get("p") not in [''.join(file.split(".")[:-1]) for file in os.listdir("static")]:
            return redirect("/")
        if request.args.get("p") in ["de_rond", "lapien", "de_nijs", "veerman", "pel", "matthijssen", "luijks", "heijnsdijk", "turk", "glowacz"]:
            gender = "meneer"
        else:
            gender = "mevrouw"
        return render_template("stem.html", picture=request.args.get("p"), gender=gender)
    
    elif request.method == "POST":
        if session.get("has_voted"):
            return redirect("/gestemd")
        
        with open("static/data.json", "r+") as f:
            data = json.loads(f.read())
            
            if request.form.get("stem") not in [''.join(file.split(".")[:-1]) for file in os.listdir("static")]:
                return render_template_string("{{ message }}", message="Deze persoon bestaat niet.")
            if (not request.form.get("stem") in data) or (data[request.form.get("stem")] == 0):
                data[request.form.get("stem")] = 1
            else:
                data[request.form.get("stem")] += 1

            f.seek(0)
            json.dump(data, f)
            f.truncate()
        
        session["has_voted"] = request.form.get("stem")
        return redirect("/gestemd")

@app.route("/gestemd", methods=["GET", "POST"])
def gestemd():
    if not session.get("has_voted"):
        return redirect("/")
    
    if request.method == "GET":
        if not session.get("has_voted"):
            return redirect("/")
        
        return render_template("gestemd.html", picture=session.get("has_voted"))
    elif request.method == "POST":
        
        with open("static/data.json", "r+") as f:
            data = json.loads(f.read())

            if not request.form.get("revoke"):
                return redirect("/gestemd")
            if data.get(session.get("has_voted")):
                data[session.get("has_voted")] -= 1  
            
            f.seek(0)
            json.dump(data, f)
            f.truncate()
        
        session.clear()
        return redirect("/")
    
@app.route("/resultaten")
def resultaten():
    with open("static/data.json", "r+") as f:
        data = json.loads(f.read())
        
    sorted_data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
    results = [[position, key, value] for position, (key, value) in enumerate(sorted_data.items(), 1)]
    return render_template("resultaten.html", results=results)

@app.route("/hoeveelheid")
def hoeveelheid():
    with open("static/data.json", "r+") as f:
        data = json.loads(f.read())
    
    sorted_data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
    results = [[position, key, value] for position, (key, value) in enumerate(sorted_data.items(), 1)]
    return render_template_string(str(sum([value[2] for value in results])))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
