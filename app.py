from flask import Flask, render_template, request
import psycopg2
from datetime import datetime, timedelta

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
      if num_bookings > 0:
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
            "b.booking_id = %s", (str(b_id)))
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
    cursor.execute("SELECT DISTINCT ON(b.booking_id) b.booking_id, "\
    "b.start, b.finish, r.name FROM "\
    "Booking b INNER JOIN Participant p ON p.person_id = %s INNER JOIN "\
    "Room r ON r.room_id = b.room_id WHERE "\
    "b.start >= current_timestamp",(str(id)))
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

@app.route('/book/<int:id>')
def book(id):
  int(id)
  global cursor
  try:
    cursor.execute("SELECT full_name FROM Person WHERE person_id=%s", str(id))
    full_name = cursor.fetchone()[0]
    cursor.execute("SELECT room_id, name, cost_per_hour FROM Room")
    rooms = cursor.fetchall()
    cursor.execute("SELECT person_id, full_name FROM Person")
    people = cursor.fetchall()
    cursor.execute("SELECT Team.team_id, team_name FROM Team\
    INNER JOIN Employee\
    ON Employee.person_id = %s\
    AND Employee.team_id = Team.team_id\
    AND Team.active = true", str(id))
    teams = cursor.fetchall()
    
    # get facilities for each room
    for i in range(0, len(rooms)):
      cursor.execute("SELECT name FROM Facility WHERE room_id=%s", str(rooms[i][0]))
      facilities = cursor.fetchall()
      if len(facilities) == 0:
        fstr = "None"
      else:
        fstr = ""
        for f in facilities:
          if not len(fstr) == 0:
            fstr += ", "
          fstr += f[0]
      rooms[i] = (rooms[i][0], rooms[i][1], rooms[i][2], fstr)
    
    def_date = datetime.now().strftime("%Y-%m-%d")
    
    print(id)
    print(teams)
    
    return render_template(
      'book.html',
      id=id,
      full_name=full_name,
      rooms=rooms,
      people=people,
      teams=teams,
      def_date=def_date
    )
  except ValueError:
    return "Bad request"

@app.route('/perform_booking', methods=['POST'])
def perform_booking():
  global cursor
  try:
    booked_by = int(request.form['booked_by'])
    room = int(request.form['room'])
    meetingdate = datetime.strptime(request.form['date'], "%Y-%m-%d")
    start = datetime.strptime(request.form['start_time'], "%H:%M")\
    .replace(year=meetingdate.year, month=meetingdate.month, day=meetingdate.day)
    end = datetime.strptime(request.form['end_time'], "%H:%M")\
    .replace(year=meetingdate.year, month=meetingdate.month, day=meetingdate.day)
    participants = [int(p) for p in request.form.getlist('participant')]
    team = int(request.form['team'])
    hours = (end-start).total_seconds() / 3600
    
    now = datetime.now()
    
    err = ""
    if start < now:
      err = "Cannot book meetings in the past."
    
    query = "BEGIN;\
    INSERT INTO Booking (room_id, person_id, team_id, start, finish, total_cost)\
    SELECT *\
    FROM (SELECT\
    {0}, {1}, {2}, timestamp '{3}', timestamp '{4}',\
      {5} *\
      (SELECT cost_per_hour\
      FROM Room\
      WHERE Room.room_id = {0})\
    ) AS a\
    WHERE NOT EXISTS (\
      SELECT *\
      FROM Booking as b\
      WHERE b.start < '{4}'\
      AND b.finish > '{3}'\
      AND b.room_id = {0}\
    ) RETURNING booking_id;".format(str(room), str(booked_by), str(team), str(start),
    str(end), str(hours))
    
    if err == "":
      cursor.execute(query)
      booking_id = cursor.fetchone()
      if booking_id == None:
        err = "Cannot book meeting."
      else:
        booking_id = booking_id[0]
    
    if err == "":
      query = ""
      for p in participants:
        query += "INSERT INTO Participant(person_id, booking_id) VALUES ({0}, {1});"\
        .format(str(p), str(booking_id))
      query += "COMMIT;"
      cursor.execute(query)
    
    return render_template(
      "perform_booking.html",
      booked_by=booked_by,
      err=err
    )
  except ValueError:
    raise
    #return "Bad request"

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
