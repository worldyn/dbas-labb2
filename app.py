from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)
# global variables pointing to database
# connection and cursor for queries
conn = None
cursor = None

# Choose employee from list of employees
@app.route('/')
def employees():
  global cursor
  cursor.execute('SELECT p.person_id, p.full_name FROM Person p INNER JOIN '\
  'Employee e ON p.person_id = e.person_id')
  emps = cursor.fetchall()  
  print(emps)
  return render_template('employees.html', employees=emps) 

# See your meetings and possibly cancel some
@app.route('/meetings/<int:id>', methods=['GET','POST'])
def meetings(id):
  global cursor
  try:
    # double check for non wanted inputs
    int(id)

    # error message
    error_message = ""
    
    # post request: delete a meeting 
    #if request.method == 'POST':
    #  meeting_id = request.form['meeting_id']

    # Get meetings and full name 
    cursor.execute("SELECT full_name FROM Person WHERE person_id=%s", (str(id)))
    full_name = cursor.fetchone()[0]
    cursor.execute("SELECT b.start, b.finish, r.name FROM Booking b "\
    "INNER JOIN Participant p ON p.person_id = %s INNER JOIN Room r ON "\
    "r.room_id = b.room_id",(str(id)))
    meetings = cursor.fetchall()
    return render_template(
      'meetings.html',
      id=id,
      full_name=full_name,
      meetings=meetings,
      error_message=error_message
    )
  except ValueError:
    return "Bad request"

@app.route('/book/<int:id>')
def book(id):
  return render_template('book.html')

# PostgreSQL database connection and
# initialization of global cursor 
def db_con():  
  conn_string = "host='localhost' dbname='postgres'\
  user='worldyn' password=''" 
  print("Connecting to db...")
  global conn
  global cursor
  conn = psycopg2.connect(conn_string) 
  cursor = conn.cursor()
  print("Connection established")

# Start db and run application
if __name__ == '__main__':
  app.config['DEBUG']
  db_con()
  # app.run() will block
  app.run()
  cursor.close()
  conn.close()
