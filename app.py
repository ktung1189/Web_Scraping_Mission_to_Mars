from flask import Flask, render_template
# Import scrape_mars
import scrape_mars

# Import our pymongo library, which lets us connect our Flask app to our Mongo database.
import pymongo

# Create an instance of our Flask app.
app = Flask(__name__)

# Create connection variable
conn = 'mongodb://localhost:27017/mission_to_mars'

# Pass connection to the pymongo instance.
client = pymongo.MongoClient(conn)
db = client.marsdb
collection = db.marsdb.marscollection

# Set route
@app.route("/")
def index():
    data = list(collection.find({}).sort('date', pymongo.DESCENDING).limit(1))
    latest_data = data[0]
    return render_template("index.html", mars=latest_data)

# Scrape 
@app.route("/scrape")
def scrape():
    scrape_data = scrape_mars.scrape()
    collection.insert_one(scrape_data)
    data = collection.find_one({})
    return render_template("index.html", mars = scrape_data)

if __name__ == "__main__":
    app.run(debug=True)