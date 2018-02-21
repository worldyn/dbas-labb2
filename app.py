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
    
    # post request: delete meetings
    if request.method == 'POST':
      global cursor
      b_ids = request.form.getlist('booking_id')
      num_bookings = len(b_ids)
      p_id = request.form['person_id']
      b_ids = tuple([int(x) for x in b_ids])
      cursor.execute("SELECT booking_id FROM Booking b WHERE "\
      "b.person_id = %s AND b.booking_id IN %s",(int(p_id),b_ids))
      valid_bids = cursor.fetchall()
      if num_bookings != len(valid_bids):
        error_message = "You can only delete bookings made by you!"
      if len(valid_bids) > 0:  
        # transform to tuple for the sql query
        if len(valid_bids) == 1:
          b_id = valid_bids[0][0]
          cursor.execute("DELETE FROM Booking b WHERE "\
          "b.booking_id = %s", [b_id])
        else:
          valid_bids = tuple(map(lambda tup: tup[0], valid_bids))
          cursor.execute("DELETE FROM Booking b WHERE b.booking_id "\
          "IN %s",(valid_bids))

    # Get person_id and full name 
    cursor.execute("SELECT person_id,full_name FROM Person "\
    "WHERE person_id=%s", (str(id)))
    person = cursor.fetchone()
    person_id  = person[0]
    full_name = person[1]

    # get bookings
    cursor.execute("SELECT b.booking_id, b.start, b.finish, r.name FROM "\
    "Booking b INNER JOIN Participant p ON p.person_id = %s INNER JOIN "\
    "Room r ON r.room_id = b.room_id",(str(id)))
    meetings = cursor.fetchall()

    return render_template(
      'meetings.html', 
      full_name=full_name, 
      person_id=person_id,
      meetings=meetings,
      error_message=error_message
    )
  except ValueError:
    return "Bad request"

#@app.route('/book/<id>')
#def book(id=None):
#  return render_template('book.html')

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
