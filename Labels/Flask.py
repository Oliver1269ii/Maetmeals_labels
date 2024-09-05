from flask import Flask, send_from_directory, request, redirect, url_for, render_template, flash
import requests
from fpdf import FPDF
import os
import shutil
import secrets

def main(email, password, date):
    
    pdf = FPDF("P", "mm", (100, 192))

    def lengthcheck(input_string, max_length=30):
        # Check if the length of the string is more than max_length
        if len(input_string) > max_length:
            # Split the string into chunks of max_length
            return [input_string[i:i + max_length] for i in range(0, len(input_string), max_length)]
        else:
            # If the string is within the length limit, return it as a single element list
            return [input_string]

    def notesplit(line):
        global note, place, content, index
        note = 1
        line = line.split("-")
        content = line[0]
        print(content)

        content = content.split(",")
        translated_items = []
        for item in content:
            if not len(item) < 2:
                item = item.split("x")
                item[0] = note_translation[item[0].strip()]
                item[1] = " - ", item[1], " stk"
                item[1] = "".join(item[1])
                item = "".join(item)
                translated_items.append(item)
        line[0] = ""
        for x in translated_items:
            line[0] = line[0], x
            line[0] = ", ".join(line[0])
        content = line[0][2:-1]
        place = line[1]
        places.append(place)
        contents.append(content)

    def nextpage(ordercount, name, ordernumber, address, postnummer, city,
                 content, place):
        pdf.add_page()
        pdf.set_font("helvetica", "", 15)
        spacing = 6
        pdf.cell(0, 1, f"Stop {ordercount}", align="R", ln=1)
        pdf.set_font("helvetica", "B", 25)
        pdf.cell(0, 10, ordernumber, ln=1)
        pdf.set_font("helvetica", "B", 15)
        pdf.cell(0, 15, "Leveringsinformation", ln=1)
        pdf.set_font("helvetica", "", 12)
        pdf.cell(0, spacing, name, ln=1)
        pdf.cell(0, spacing, address, ln=1)
        pdf.cell(0, spacing, f"{postnummer} {city}", ln=1)

 
        place = place.split(":")
        place[0] = place[0] + ":"
        for i in place:
            if i == "Må stilles:":
                pdf.set_font("helvetica", "B", 12)
                pdf.cell(22, spacing, place[0])
        pdf.set_font("helvetica", "", 12)
        place = lengthcheck(place[1])
        for i in range(len(place)):
            pdf.cell(0, spacing, place[i].lstrip(), ln=1)

        pdf.cell(0, 5, "_" * 25, ln=1)

        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 12, "Indhold:", ln=1)
        pdf.set_font("helvetica", "", 12)
        print(content)
        content = content.split(",")
        print(content)
        for i in content:
            if "stk" not in i:
                i = i + "k"
            i = i.lstrip()

            pdf.cell(0, spacing, i, ln=1)


    print("Main has been called with:")
    print(email)
    print(password)
    print(date)

    # Authentication
    url_post = "https://api.treiber.dk/v1/authenticate"
    auth = {"email": f"{email}", "password": f"{password}"}
    post_response = requests.post(url_post, json=auth)
    post_response_json = post_response.json()
    statuscode = post_response.status_code
    if statuscode == 401:
        print("Auth failed")
        return statuscode

    token = post_response_json["token"]

    note_translation = {
        "R01": "R01 - Rush Roast Chicken",
        "R02": "R02 - Peas & Love",
        "R03": "R03 - Sweet Hurry Curry",
        "R04": "R04 - Papa Rika",
        "R05": "R05 - Red Coco Curry",
        "R06": "R06 - Moroccan Chickpea Dinner",
        "R07": "R07 - Pronto Pesto",
        "R08": "R08 - Instant India",
        "R09": "R09 - Busy Bolo",
        "R10": "R10 - Cauliflower Power"
    }

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    base_url = 'https://api.treiber.dk/v1/routes'

    date = date + "T22:00:00.000Z"
    params = {'date': date}
    response = requests.get(base_url, headers=headers, params=params)
    response = response.json()
    length = len(response["routes"])

    if length == 0:
        print("Date is empty")
        return "empty_date"
    ordercount = 0

    # group 1
    addresses = []
    zipcodes = []
    cities = []
    subcities = []

    # group 2
    references = []
    recipientnames = []
    notes = []

    # group 3, used in notesplit()
    places = []
    contents = []

    if statuscode == 200:


        # fills group 1
        for i in range(len(response["routes"][0]["entries"])):
            addresses.append(
                response["routes"][0]["entries"][i]["address"]["full_address"])
            zipcodes.append(
                response["routes"][0]["entries"][i]["address"]["zipcode"])
            cities.append(
                response["routes"][0]["entries"][i]["address"]["city"])
            subcities.append(
                response["routes"][0]["entries"][i]["address"]["sub_city"])

        for i in range(len(response["routes"][0]["entries"])):
            if response["routes"][0]["entries"][i]["work_point"] != None:
                references.append(response["routes"][0]["entries"][i]
                                  ["work_point"]["reference"])
                recipientnames.append(response["routes"][0]["entries"][i]
                                      ["work_point"]["recipient_name"])
                notes.append(
                    response["routes"][0]["entries"][i]["work_point"]["note"])
    else:
        print(response.text)  # Print the error message if available

    addresses = addresses[1:-1]
    zipcodes = zipcodes[1:-1]
    cities = cities[1:-1]
    subcities = subcities[1:-1]

    for line in notes:
        notesplit(line)

    for i in references:
        index = references.index(i)
        ordercount = ordercount + 1
        name = recipientnames[index]
        ordernumber = references[index]
        address = addresses[index]
        postnumber = zipcodes[index]
        city = cities[index]
        content = contents[index]
        place = places[index].lstrip()
        #"""(ordercount, name, ordernumber, address, postnummer, city, content, place)"""
        nextpage(ordercount, name, ordernumber, address, postnumber, city,
                 content, place)

    #Generates output folder and file
    output_dir = dirused
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    outputfilename = "output.pdf"
    output_path = os.path.join(output_dir, outputfilename)
    folder_path = dirused
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        # Check if it is a file and remove it
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.remove(item_path)
        # If it is a directory, remove it along with its contents
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)
    pdf.output(output_path)


    print("Done")
    return True
global dirused
dirused = "/home/oliver/Documents/Coding/savedprojects/Python/Testfolder/uploads"
app = Flask(__name__)
UPLOAD_FOLDER = dirused
app.secret_key = secrets.token_hex(16)

@app.route('/')
def index():
    print("Rendering index")
    return render_template('index.html')


@app.route('/uploads/<filename>')
def download_file(filename):
    print("Sending file")
    return send_from_directory(UPLOAD_FOLDER, filename)




@app.route('/login', methods=["POST"])
def login():
    print("getting the form details")
    email = request.form.get('email')
    password = request.form.get('password')
    date = request.form.get('date')


    print(f"Received email: {email}, password: {password}, date: {date}")
    date = date.split("-")
    day = int(date[2])
    day = day - 1
    date[2] = str(day).zfill(2)
    date = "-".join(date)

    print("Calling main \n")
    check = main(email, password, date)
    print(f"Main returned: {check}")
    if check == 401:
        flash('Username or password is incorrect')
        return redirect(url_for('index'))
    elif check == "empty_date":
        flash("Date is empty. Try another.")
        return redirect(url_for("index"))
    elif check== True:
        return redirect(url_for('upload'))
    else:
        return redirect(url_for('index'))

@app.route('/upload')
def upload():
    return render_template('upload.html')




app.run()