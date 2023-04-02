from app import create_app
from flask import render_template

app = create_app()


@app.route("/")
def home():
    return render_template("base.html")


if __name__ == '__main__':
    app.run(debug=True)
