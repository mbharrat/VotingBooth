from flask import Flask, render_template

home = Flask(__name__)

@home.route("/")
def main():
    elec_end = reg_end = True
    return render_template("home.html", elec_end=elec_end, reg_end=reg_end)

if __name__ == "__main__":
    home.run(host="localhost", port=8080, debug=True)
