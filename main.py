from app import create_app
from flask import render_template

app = create_app()


@app.route("/")
def home():
    return render_template("home.html")

#example to how add pages. look at base file to see how to add this page to the navbar
@app.route("/test")
def test():
    return render_template("test.html")


if __name__ == '__main__':
    app.run(debug=True)
