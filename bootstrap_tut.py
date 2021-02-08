from flask import Flask, render_template


app = Flask(__name__)

print(__name__)

@app.route('/')
def hello():
    # return 'Sanjeev Kumar'
    return render_template("index.html")


@app.route("/bootstrap")
def bootstrap():
    return render_template("bootstrap.html")

@app.route('/about')
def about():
    name = "Sanjeev Kumar"
    return render_template("about.html", myName=name)


app.run(debug=True)