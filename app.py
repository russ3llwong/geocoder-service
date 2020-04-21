from flask import Flask, render_template, request, send_file
from geopy.geocoders import ArcGIS
import pandas
import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/submit", methods=['POST'])
def submit():

    try:
        gc = ArcGIS(scheme='http')
        addr = request.form['address']
        coordinates = gc.geocode(addr, exactly_one=True)[1]
        return render_template("home.html", coordinates = coordinates)

    except Exception as e:
        return render_template("home.html", coordinates = "Invalid address")
    

@app.route('/submit-csv', methods=['POST'])
def submit_csv():
    global filename # so download function can access

    if request.method == "POST":
        file = request.files['file']

        try:
            # read input and apply geocoding
            df = pandas.read_csv(file)
            gc = ArcGIS(scheme='http')
            df["coordinates"] = df["Address"].apply(gc.geocode)
            # append latitude and longitude to dataframe
            df['Latitude'] = df['coordinates'].apply(lambda x : x.latitude if x != None else None)
            df['Longitude'] = df['coordinates'].apply(lambda x : x.longitude if x != None else None)
            # drop coordinates column
            df = df.drop("coordinates",1)
            # create file with unique filename
            filename = datetime.datetime.now().strftime("files/%Y-%m-%d-%H-%M-%S-%f" + ".csv")
            df.to_csv(filename, index = None)
            return render_template("home.html", text = df.to_html(), btn = 'download.html')

        except Exception as e:
            return render_template("home.html", text = str(e))

@app.route("/download-file/")
def download():
    return send_file(filename, attachment_filename='yourfile.csv', as_attachment=True)

if __name__ == "__main__":
    app.run(debug = True)