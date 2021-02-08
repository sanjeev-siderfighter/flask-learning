from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello():
    # return 'Sanjeev Kumar'
    return render_template("index_page.html")


@app.route('/about')
def about():
    name = "Sanjeev Kumar"
    return render_template("about_page.html", myName=name)


app.run(debug=True)
