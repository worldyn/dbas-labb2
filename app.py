from flask import Flask
import psycopg2
#from models import db

app = Flask(__name__)

@app.route('/')
def meetings():
  return "hej"

def db_con():  
  conn_string = "host='localhost' dbname='postgres'\
  user='worldyn' password=''" 
  print("Connecting to db...")
  conn = psycopg2.connect(conn_string) 
  cursor = conn.cursor()
  print("Connection established")

if __name__ == '__main__':
  app.config['DEBUG']
  db_con()
  app.run()
  #db.init_app(app)
