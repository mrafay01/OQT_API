import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import date
from flask_cors import CORS


app = Flask("QuranAPI")

CORS(app)

# Configure the SQL Server database connection
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mssql+pyodbc://sa:123@DESKTOP-51B7KMU/QURAN_TUTOR_DB?driver=ODBC+Driver+17+for+SQL+Server"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app, engine_options={"isolation_level": "AUTOCOMMIT"})


@app.route("/GetStudent", methods=["GET"])
def appuser():
    return jsonify("Hassan"), 200


@app.route("/GetAllstudents", methods=["GET"])
def get_users():
    rows = db.session.execute(text("SELECT * FROM Student"))
    rw = []
    keys = [
        "S_id",
        "S_Username",
        "S_Name",
        "S_psw",
        "S_region",
        "S_gender",
        "S_dob",
        "S_pic",
        "Parent_id",
    ]
    for row in rows:
        print(row)
        rw.append(dict(zip(keys, row)))

    return jsonify(rw), 200


@app.route("/GetAllTeachers", methods=["GET"])
def get_teachers():
    rows = db.session.execute(text("SELECT * FROM Teacher"))
    rw = []
    keys = [
        "T-id",
        "T_username",
        "Name",
        "Password",
        "CNIC",
        "Region",
        "Qualification",
        "Gender",
        "DOB",
        "pic",
        "Rating"

    ]
    for row in rows:
        print(row)
        rw.append(dict(zip(keys, row)))

    return jsonify(rw), 200



@app.route("/SignUpStudents", methods=["Post"])
def SignupStudent():
    body = request.json
    print(body)
    name = body.get("name", "def")
    dob = body.get("dob", "def")
    username = body.get("username", "def")
    region = body.get("region", "def")
    password = body.get("password", "def")
    gender = body.get("gender", "def")
    spic = body.get("spic", "def")

    check_query = text(f"SELECT COUNT(*) FROM Student WHERE username = '{username}'")
    result = db.session.execute(check_query, {"username": username}).scalar()

    if result > 0:
        return jsonify(
            {"error": "Username already taken, please try a different username"}
        ), 409

    else:
        query = text(
            f"INSERT INTO STUDENT VALUES('{username}','{name}','{password}','{region}','{gender}','{dob}','{spic}',1)"
        )

        try:
            db.session.execute(query)
        except Exception as e:
            print(e)

        return jsonify("Inserted Data")


@app.route("/SignupParent", methods=["Post"])
def SignUpParent():  
    body = request.json
    print(body)
    name = body.get("name", "def")
    region = body.get("region", "def")
    cnic = body.get("cnic", "def")
    username = body.get("username", "def")
    password = body.get("password", "def")

    check_query = text(f"SELECT COUNT(*) FROM Parent WHERE username = '{username}'")
    result = db.session.execute(check_query, {"username": username}).scalar()

    if result > 0:
        return jsonify(
            {"error": "Username already taken, please try a different username"}
        ), 409
    else:
        query = text(
        f"INSERT INTO PARENT VALUES ('{name}','{cnic}','{username}','{password}','{region}')"
        )
        try:
            db.session.execute(query)

        except Exception as err:
            print(err)

    return jsonify("Data has been Inserted")


@app.route("/SignUpTeacher", methods=["Post"])
def SignUpTeacher():
    body = request.json

    firstname = body.get("firstname", "def")
    lastname = body.get("lastname", "def")
    username = body.get("username", "def")
    region = body.get("region", "def")
    password = body.get("password", "def")
    gender = body.get("gender", "def")
    tpic = body.get("spic", "def")
    qual = body.get("qual", "def")
    cnic = body.get("cnic", "def")

    check_query = text(f"SELECT COUNT(*) FROM Teacher WHERE username = '{username}'")
    result = db.session.execute(check_query, {"username": username}).scalar()

    if result > 0:
        return jsonify(
            {"error": "Username already taken, please try a different username"}
        ), 409
    else:
        query = text(
            f"INSERT INTO TEACHER VALUES('{firstname}','{lastname}','{region}','{tpic}','{qual}','{username}','{password}','{0}','{cnic}','{gender}')"
        )
        try:
            db.session.execute(query)
        except Exception as error:
            print(error)

    return jsonify("Thank You for joining us")


@app.route("/GetStudentByUsername", methods=["GET"])
def GetStudentByUsername():
    usrname = request.args.get("usrname")
    if not usrname:
        return jsonify({"error": "Username is required"}), 400

    rows = db.session.execute(text(f"SELECT * FROM Student WHERE username='{usrname}'"))
    rw = []
    keys = [
        "id",
        "username",
        "name",
        "password",
        "region",
        "gender",
        "dob",
        "pic",
        "parent_id"
    ]
    for row in rows:
        rw.append(dict(zip(keys, row)))

    return jsonify(rw), 200


# from sqlalchemy import text


@app.route("/UpdateStudentByUsername", methods=["POST"])
def UpdateStudentByUsername():
    usrname = request.args.get("usrname")

    if not usrname:
        return jsonify({"error": "Username is required"}), 400

    data = request.json
    firstname = data.get("firstname", "Def")
    lastname = data.get("lastname", "Def")
    spic = data.get("spic", "Def")
    region = data.get("region", "Def")
    psw = data.get("psw", "Def")

    try:
        query = text("""
            UPDATE Student
            SET fname = :firstname,
                lname = :lastname,
                pic = :spic,
                region = :region,
                psw = :psw
            WHERE username = :usrname
        """)
        db.session.execute(
            query,
            {
                "firstname": firstname,
                "lastname": lastname,
                "spic": spic,
                "region": region,
                "psw": psw,
                "usrname": usrname,
            },
        )
        db.session.commit()

        return jsonify({"message": "Student information updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/DeleteStudentByUsername", methods=["DELETE"])
def DeleteStudentByUsername():
    usrname = request.args.get("usrname")

    if not usrname:
        return jsonify({"error": "Username is required"}), 400

    try:
        # Check if the student exists
        student = db.session.execute(
            text("SELECT * FROM Student WHERE username = :usrname"),
            {"usrname": usrname},
        ).fetchone()

        if not student:
            return jsonify({"error": "Student not found"}), 404

        # Delete the student
        query = text("DELETE FROM Student WHERE username = :usrname")
        db.session.execute(query, {"usrname": usrname})
        db.session.commit()

        return jsonify(
            {"message": f"Student with username '{usrname}' deleted successfully"}
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/LoginStudent", methods=["GET"])
def LoginStudent():
    # Retrieve username and password from query parameters
    username = request.args.get("username")
    password = request.args.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        # Query the database to verify the username and password
        query = text("""
            SELECT * FROM Student 
            WHERE username = :username AND password = :password
        """)
        result = db.session.execute(
            query, {"username": username, "password": password}
        ).fetchone()

        if result:
            # If a match is found, return success
            return jsonify({"message": "Login successful", "username": username}), 200
        else:
            # If no match is found, return error
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/GetTeachersByCourse", methods=["GET"])
def GetTeachersByCourse():
    id = request.args.get("id")

    try:
        query = text(
            f"Select qari_id,name,gender,region,pic from TeacherCourse tc inner JOIN Teacher t ON t.id = tc.qari_id where tc.course_id='{id}'"
        )
        result = db.session.execute(query)
        rw = []
        keys = [
            "qari_id",
            "name",
            "gender",
            "region",
            "pic",
        ]
        for row in result:
            rw.append(dict(zip(keys, row)))

        return jsonify(rw)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/getAvailableSlots", methods=["GET"])
def avail_slots():
    qari_id = request.args.get("qari_id")
    query = text(f"""SELECT t.id AS qariId, t.name AS qariName, ts.day, s.time, s.slot_id  FROM Teacher t 
                    INNER JOIN TeacherSchedule ts ON t.id = ts.teacher_id 
                    INNER JOIN Slot s ON ts.id = s.sch_id
                    WHERE t.id = '{qari_id}' AND booked = 0""")
    print(query)
    try:
        res = db.session.execute(query)
        rw = []
        keys = [
            "qariId",
            "qariName",
            "day",
            "time",
            "slot_id",
        ]
        for row in res:
            rw.append(dict(zip(keys, row)))
        return jsonify(rw)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/bookSlots", methods=["POST"])
def book_slots():
    body = request.json
    qari_id = body.get("qari_id")
    student_id = body.get("student_id")
    course_id = body.get("course_id")
    slots = body.get("slots")  # [ 1, 2, 3, 4, 5] => 1,2,3,4,5

    try:
        bookedSlots = ",".join([str(x) for x in slots])
        res = db.session.execute(
            text(
                f"INSERT INTO Enrollment OUTPUT inserted.id VALUES('{student_id}', '{qari_id}', '{course_id}')"
            )
        )
        generated_id = res.scalar()
        bookQuery = text(f"UPDATE Slot SET booked = 1 WHERE slot_id IN({bookedSlots})")
        db.session.execute(bookQuery)

        for i in slots:
            db.session.execute(
                text(
                    f"INSERT INTO BookedEnrollmentSlots VALUES('{generated_id}', '{i}')"
                )
            )

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/GetEnrolledCourses", methods=["Get"])
def EnrolledCourses():
    stu_id = request.args.get("stu_id")
    query = text(f"""SELECT s.name as Studentname, c.name as Coursename, c.description as coursedescription, t.name AS TeacherName, sl.time as SlotTime FROM Student s 
                    INNER JOIN Enrollment e
                    ON s.id = e.student_id
                    INNER JOIN Course c
                    ON e.course_id = c.id
                    INNER JOIN Teacher t
                    ON t.id = e.qari_id
                    INNER JOIN BookedEnrollmentSlots bs 
                    ON bs.enrollment_id = e.id
                    INNER JOIN Slot sl 
                    ON sl.slot_id = bs.slot_id 
                    where s.id='{stu_id}'""")
    print(query)
    try:
        res = db.session.execute(query)
        rw = []
        keys = [
            "Studentname",
            "CourseName",
            "coursedescription",
            "Teachername",
            "SlotTime",
        ]
        for row in res:
            rw.append(dict(zip(keys, row)))
        return jsonify(rw)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/GetCourses", methods=["Get"])
def get_course():
    rows = db.session.execute(text("Select * from Course"))
    rw = []
    keys = ["c_id", "c_name", "c_desc"]
    for row in rows:
        rw.append(dict(zip(keys, row)))

    return jsonify(rw)





# Teacher Side
@app.route("/UpdateTeacherByUsername", methods=["POST"])
def UpdateTeacherByUsername():
    # Get the username from query parameters
    username = request.args.get("username")

    if not username:
        return jsonify({"error": "Username is required"}), 400

    # Get the body of the request
    body = request.json
    print(body)

    # Extract values from the body
    name = body.get("name", "def")
    password = body.get("password", "def")
    pic = body.get("pic", "def")
    dob = body.get("dob", "def")
    qualification = body.get("qualification", "def")
    region = body.get("region", "def")

    try:
        query = text(f"""
            UPDATE Teacher
            SET name = '{name}',
                password = '{password}',
                pic = '{pic}',
                dob = '{dob}',
                qualification = '{qualification}',
                region = '{region}'
            WHERE username = '{username}'
        """)

        db.session.execute(query)
        db.session.commit()

        return jsonify(
            {"message": f"Teacher with username '{username}' updated successfully"}
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/GetQariCoursesAndSchedule", methods=["GET"])
def GetQariCoursesAndSchedule():
    qari_id = request.args.get("qari_id")

    if not qari_id:
        return jsonify({"error": "Qari ID is required"}), 400

    query = text("""
            SELECT t.id AS QariId,t.name AS QariName,c.id AS CourseId,c.name AS CourseName,c.description AS CourseDescription,ts.day AS ScheduleDay,s.time AS SlotTime,s.slot_id AS SlotId, s.booked AS IsBooked
            FROM Teacher t
            INNER JOIN TeacherCourse tc 
            ON t.id = tc.qari_id
            INNER JOIN Course c 
            ON tc.course_id = c.id
            INNER JOIN TeacherSchedule ts 
            ON t.id = ts.teacher_id
            INNER JOIN Slot s 
            ON ts.id = s.sch_id
            WHERE t.id = :qari_id
            """)

    try:
        result = db.session.execute(query, {"qari_id": qari_id})
        rw = []
        keys = [
            "QariId",
            "QariName",
            "CourseId",
            "CourseName",
            "CourseDescription",
            "ScheduleDay",
            "SlotTime",
            "SlotId",
            "IsBooked",
        ]

        for row in result:
            rw.append(dict(zip(keys, row)))

        if not rw:
            return jsonify(
                {"message": "No courses or schedules found for the specified Qari"}
            ), 404

        return jsonify(rw), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


app.run(debug=True)