from flask import Flask, request
from kkaas import klauskleber

app = Flask(__name__)
klaus = klauskleber.LabelPrinter("/dev/ttyUSB0")


@app.route("/", methods=["POST"])
def print_label():
    if request.json is None:
        return "Request has to be JSON"

    # required fields
    id = request.json['id']
    name = request.json['name']
    maintainer = request.json['maintainer']
    owner = request.json['owner']
    use_pol = request.json['use_pol']
    discard_pol = request.json['discard_pol']

    label = klauskleber.Label(thing_id=id,
                              thing_name=name,
                              thing_maintainer=maintainer,
                              thing_owner=owner,
                              thing_use_pol=use_pol,
                              thing_discard_pol=discard_pol)

    klaus.print_label(label)
    return "OK", 200
