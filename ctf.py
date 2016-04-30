from base64 import b64encode, b64decode
from flask import Flask, render_template, request, jsonify
from OpenSSL import SSL
from Crypto.Signature import PKCS1_PSS as PKCS
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
import string, random, requests

# SSL setup
context = ("keys/ctf.crt","keys/ctf.key")

ctf = Flask(__name__)

voters = {}
valid_nums = {}
votes = {"bernie": 0, "hillary": 0}
names = []

@ctf.route("/confirmation", methods=["POST"])
def confirmation():
    if request.method == "POST":
        message = validate_voter(request.form["rand_id"], request.form["valid_num"], request.form["party"])
        if "candidate" in message:
            request_voter_name(request.form["valid_num"])
        return jsonify(message = message)

@ctf.route("/get_votername", methods=["POST"])
def get_votername():
    if request.method == "POST":
        signature = request.form["digsig"]
        name = request.form["name"]
        if verify_dig_sig(signature, name):
            names.append(name)
    return "get_votername"

@ctf.route("/")
def main():
    return render_template("ctf_vote.html")

@ctf.route("/add", methods=["POST"])
def add():
    if request.method == "POST":
        signature = request.form["digsig"]
        valid_num = request.form["valid_num"]
        verified = False
        if verify_dig_sig(signature, valid_num):
            valid_nums[valid_num] = False
    return "add"

@ctf.route("/results")
def display_results():
    return render_template("ctf_results.html", voters=voters, votes=votes, names=names)

def request_voter_name(valid_num):
    signature = create_dig_sig(valid_num)
    info = {"digsig":signature , "valid_num":valid_num}
    req = requests.post("https://localhost:8091/voter_name", data=info, verify=False)

def create_dig_sig(message):
    f = open("./keys/ctf_rsa", "r") # get ctf's private key
    key = RSA.importKey(f.read())
    h = SHA.new()
    h.update(message)
    signer = PKCS.new(key)
    signature = signer.sign(h)
    return b64encode(signature)

def verify_dig_sig(signature, message):
    f = open("./keys/rsa.pub", "r") # get cla's public key
    key = RSA.importKey(f.read())
    h = SHA.new()
    h.update(message)
    verifier = PKCS.new(key)
    if verifier.verify(h, b64decode(signature)):
        return True
    else:
        return False

def validate_voter(rand_id, valid_num, vote):
    allowed = False
    repeated = False
    if not rand_id or not valid_num or vote is None:
        return "Please fill all of the fields."
    elif voters.has_key(rand_id):
        return "Your random identification number is already taken, please try again."
    elif valid_nums.has_key(valid_num):
        if valid_nums[valid_num] == False:
            info = {"valid_num":valid_num, "vote":vote}
            voters[rand_id] = info # store voting info
            votes[vote] = votes[vote] + 1 # increase tally
            valid_nums[valid_num] = True # update: voter already voted
            allowed = True
        else:
            repeated = True

    if allowed == True:
        lookup = {"bernie":"Bernie Sanders","hillary":"Hillary Clinton"}
        return "Voter ["+rand_id+"] voted for "+lookup.get(vote)+" as their candidate!"
    elif repeated == True:
        return "You have already voted."
    else:
        return "You are not registered to vote."

if __name__ == "__main__":
    ctf.run(host="localhost", port=8090, debug=True, threaded=True, ssl_context=context)
