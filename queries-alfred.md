**insert new user:**
```SQL
INSERT INTO Person (full_name)
VALUES ('Test');
```

**insert new team:**
```SQL
INSERT INTO Team (team_name, active)
VALUES ('Team Foo', true);
```

**delete old users:**
```SQL
DELETE FROM Person
WHERE person_id=1;
```

**delete team:**
```SQL
DELETE FROM Team
WHERE team_id=1;
```

**delete teams without affecting log of costs:**
```SQL
UPDATE Team
SET active = false
WHERE team_name='Team 2';
```

**what rooms are available for a given time slot**
```SQL
SELECT name
FROM Room
WHERE NOT EXISTS (
  SELECT *
  FROM Booking
  WHERE start < timestamp '2018-02-16 14:00:00'
  AND finish > timestamp '2018-02-16 13:00:00'
  AND Booking.room_id = Room.room_id
);
```

**insert booking if not overlapping with another booked meeting**
(removed because it was outdated)

**delete meetings that have not occured**
```SQL
```

**fetch occupied rooms for a given date**
```SQL
```

Adam gör dessa:
**show which users have booked which rooms**
```SQL
```

**show participants of a given meeting**
```SQL
```

**cost for team for given time interval**
```SQL
```
