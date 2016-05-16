from flask import Flask, render_template, request, jsonify
from OpenSSL import SSL
import json, string, random, requests

# SSL setup
context = ("keys/cfa.crt","keys/cfa.key")

cla = Flask(__name__)

# list of eligible voters
eligible_voters = {
    "100":["Kartik", "Chopra", False],
    "111":["AP", "V", False],
    "200":["John", "Doe", False],
    "300":["Devina", "Bharrat", False]
}
@cla.route("/")
def main():
    return render_template("cla_register.html")

@cla.route("/validation", methods=["POST"])
def validation():
    if request.method == "POST":
        message = validate_voters(request.form["first"], request.form["last"], request.form["secret"])
        return jsonify(message=message)

@cla.route("/voter_name", methods=["POST"])
def get_votername():
    if request.method == "POST":
        valid_num = request.form["valid_num"]
        name = ""
        for voter in eligible_voters:
            if eligible_voters[voter][2] == True and eligible_voters[voter][3] == valid_num:
                name = eligible_voters[voter][0] + " " + eligible_voters[voter][1]
                send_name(name)
                break
    return "voter_name"

def send_name(name):
    info = {"name":name}
    req = requests.post("https://localhost:8090/get_votername", data=info, verify=False)

def send_valid_num(validation_num):
    info = {"valid_num":validation_num}
    req = requests.post("https://localhost:8090/add", data=info, verify=False)

def generate_valid_num(length):
    lst = [random.choice(string.ascii_letters + string.digits)
      for n in xrange(length)]
    rand = "".join(lst)
    return rand

def validate_voters(first, last, secret):
    eligible = False # whether or not voter is eligible to register
    repeat = False # whether voter has already registered
    validation_num = None
    if not first or not last or not secret:
        return "Please fill all of the fields."
    elif eligible_voters.has_key(secret):
        voter = eligible_voters[secret]
        if voter[0] == first and voter[1] == last:
            if voter[2] == False:
                validation_num = generate_valid_num(15)
                voter.append(validation_num) # add validation num to voter
                send_valid_num(validation_num) # send validation number to CTF
                voter[2] = True # update: voter has alredy registered
                eligible = True
            else:
                repeat = True

    if eligible == True and validation_num is not None:
        return first + " " + last + ", your validation number is: " + validation_num
    elif repeat == True:
        return "You have already registered."
    else:
        return "You are not eligible to register."

if __name__ == "__main__":
    cla.run(host="localhost", port=8091, debug=True, threaded=True, ssl_context=context)
