import base64
import datetime
import os
from flask import Flask, current_app, jsonify, request
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
        "id",
        "username",
        "name",
        "password",
        "region",
        "gender",
        "dob",
        "pic"
    ]
    for row in rows:
        rw.append(dict(zip(keys, row)))
    return jsonify(rw), 200



@app.route("/GetAllTeachers", methods=["GET"])
def get_teachers():
    query = """
        SELECT 
            t.id AS T_id,
            t.username,
            t.name,
            t.password,
            t.cnic,
            t.region,
            t.qualification,
            t.gender,
            t.dob,
            t.pic,
            t.ratings,
            t.hourly_rate,
            t.bio,
            STRING_AGG(tl.Languages, ', ') AS Languages
        FROM Teacher t
        LEFT JOIN Teacher_Languages tl ON t.id = tl.TeacherID
        GROUP BY 
            t.id, t.username, t.name, t.password, t.cnic, t.region,
            t.qualification, t.gender, t.dob, t.pic, t.ratings,
            t.hourly_rate, t.bio
    """
    rows = db.session.execute(text(query))
    keys = [
        "id", "username", "name", "password", "cnic", "region",
        "qualification", "gender", "dob", "pic", "ratings",
        "hourly_rate", "bio", "languages"
    ]
    rw = [dict(zip(keys, row)) for row in rows]
    return jsonify(rw), 200


@app.route("/SignUpStudents", methods=["POST"])
def SignupStudent():
    body = request.json
    print(body)
    name = body.get("name", "def")
    dob = body.get("dob", "def")
    username = body.get("username", "def")
    region = body.get("region", "def")
    password = body.get("password", "def")
    gender = body.get("gender", "def")
    pic = body.get("pic")
    pic_path = None

    print("RAW pic value:", pic)

    if pic and pic != "def" and len(pic) > 30:
        try:
            header, encoded = pic.split(',', 1) if ',' in pic else ('', pic)
            img_bytes = base64.b64decode(encoded)
            
            img_dir = os.path.join(current_app.root_path, 'static', 'profile_images')
            os.makedirs(img_dir, exist_ok=True)

            filename = f"{username}_profile.png"
            file_path = os.path.join(img_dir, filename)

            with open(file_path, 'wb') as f:
                f.write(img_bytes)

            pic_path = f"/static/profile_images/{filename}"
            print(f"Image saved at: {pic_path}")
        except Exception as e:
            print("Image save failed:", e)
            return jsonify({"error": "Failed to save image", "details": str(e)}), 500
    else:
        print("No valid image provided.")

    check_query = text(f"SELECT COUNT(*) FROM Student WHERE username = :username")
    result = db.session.execute(check_query, {"username": username}).scalar()

    if result > 0:
        return (
            jsonify(
                {"error": "Username already taken, please try a different username"}
            ),
            409,
        )

    else:
        query = text(
            "INSERT INTO Student (username, name, password, region, gender, dob, pic) VALUES (:username, :name, :password, :region, :gender, :dob, :pic)"
        )

        try:
            db.session.execute(
                query,
                {
                    "username": username,
                    "name": name,
                    "password": password,
                    "region": region,
                    "gender": gender,
                    "dob": dob,
                    "pic": pic_path,
                },
            )
            db.session.commit()
            return jsonify({"message": "Inserted Data"}), 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify({"error": "Database insert failed", "details": str(e)}), 500


@app.route("/SignupParent", methods=["POST"])
def SignUpParent():
    body = request.json
    print(body)

    name = body.get("name", "def")
    region = body.get("region", "def")
    cnic = body.get("cnic", "def")
    username = body.get("username", "def")
    password = body.get("password", "def")
    student_username = body.get("student_username", "def")
    pic = body.get("pic")
    pic_path = None

    print("RAW pic value:", pic)
    
    if pic and pic != "def" and len(pic) > 30:
        try:
            header, encoded = pic.split(',', 1) if ',' in pic else ('', pic)
            img_bytes = base64.b64decode(encoded)
            
            img_dir = os.path.join(current_app.root_path, 'static', 'profile_images')
            os.makedirs(img_dir, exist_ok=True)

            filename = f"{username}_profile.png"
            file_path = os.path.join(img_dir, filename)

            with open(file_path, 'wb') as f:
                f.write(img_bytes)

            pic_path = f"/static/profile_images/{filename}"
            print(f"Image saved at: {pic_path}")
        except Exception as e:
            print("Image save failed:", e)
            return jsonify({"error": "Failed to save image", "details": str(e)}), 500
    else:
        print("No valid image provided.")

    # 1. Check if username already exists
    check_query = text("SELECT COUNT(*) FROM Parent WHERE username = :username")
    result = db.session.execute(check_query, {"username": username}).scalar()

    if result > 0:
        return (
            jsonify(
                {"error": "Username already taken, please try a different username"}
            ),
            409,
        )

    # 2. Get student_id from Student table
    student_query = text("SELECT id FROM Student WHERE username = :s_username")
    student_result = db.session.execute(
        student_query, {"s_username": student_username}
    ).fetchone()

    if not student_result:
        return jsonify({"error": "Student username not found"}), 404

    student_id = student_result[0]

    # 3. Insert into Parent table with student_id
    insert_query = text(
        "INSERT INTO Parent (name, cnic, username, password, region, student_ID) "
        "VALUES (:name, :cnic, :username, :password, :region, :student_id)"
    )

    try:
        db.session.execute(
            insert_query,
            {
                "name": name,
                "cnic": cnic,
                "username": username,
                "password": password,
                "region": region,
                "student_id": student_id,
            },
        )
        db.session.commit()
        return jsonify({"message": "Data has been inserted"}), 201

    except Exception as err:
        print(err)
        db.session.rollback()
        return jsonify({"error": "Database insert failed", "details": str(err)}), 500


@app.route("/SignUpTeacher", methods=["POST"])
def SignUpTeacher():
    body = request.json
    name = body.get("name", "def")
    username = body.get("username", "def")
    region = body.get("region", "def")
    password = body.get("password", "def")
    gender = body.get("gender", "def")
    qualification = body.get("qual", "def")
    cnic = body.get("cnic", "def")
    dob = body.get("dob", "def")
    ratings = 0
    hourly_rate = body.get("hourly_rate", 0)
    bio = body.get("bio", "None")
    sample_clip = body.get("sample_clip", None)
    languages = body.get("languages", [])  # list of strings
    pic = body.get("pic")
    pic_path = None

    # Handle image upload
    if pic and len(pic) > 30:
        try:
            header, encoded = pic.split(',', 1) if ',' in pic else ('', pic)
            img_bytes = base64.b64decode(encoded)
            img_dir = os.path.join(current_app.root_path, 'static', 'profile_images')
            os.makedirs(img_dir, exist_ok=True)
            filename = f"{username}_profile.png"
            file_path = os.path.join(img_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(img_bytes)
            pic_path = f"/static/profile_images/{filename}"
        except Exception as e:
            return jsonify({"error": "Failed to save image", "details": str(e)}), 500

    # Check duplicate username
    check_query = text("SELECT COUNT(*) FROM Teacher WHERE username = :username")
    result = db.session.execute(check_query, {"username": username}).scalar()
    if result > 0:
        return jsonify({"error": "Username already taken"}), 409

    # Insert Teacher
    insert_query = text("""
        INSERT INTO Teacher (username, name, password, cnic, region, qualification, gender, dob, pic, ratings, hourly_rate, bio, SampleClip)
        VALUES (:username, :name, :password, :cnic, :region, :qualification, :gender, :dob, :pic, :ratings, :hourly_rate, :bio, :sample_clip)
    """)
    try:
        db.session.execute(insert_query, {
            "username": username,
            "name": name,
            "password": password,
            "cnic": cnic,
            "region": region,
            "qualification": qualification,
            "gender": gender,
            "dob": dob,
            "pic": pic_path,
            "ratings": ratings,
            "hourly_rate": hourly_rate,
            "bio": bio,
            "sample_clip": sample_clip,
        })
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Teacher insertion failed", "details": str(e)}), 500

    # Insert languages
    teacher_id = db.session.execute(text("SELECT id FROM Teacher WHERE username = :username"), {"username": username}).scalar()
    for lang in languages:
        db.session.execute(
            text("INSERT INTO Teacher_Languages (TeacherID, Languages) VALUES (:teacher_id, :language)"),
            {"teacher_id": teacher_id, "language": lang}
        )
    db.session.commit()

    return jsonify({"message": "Teacher registered successfully"}), 201


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
        "parent_id",
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
        query = text(
            """
            UPDATE Student
            SET fname = :firstname,
                lname = :lastname,
                pic = :spic,
                region = :region,
                psw = :psw
            WHERE username = :usrname
        """
        )
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

        return (
            jsonify(
                {"message": f"Student with username '{usrname}' deleted successfully"}
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# LOGINS 

@app.route("/LoginStudent", methods=["GET"])
def LoginStudent():
    # Retrieve username and password from query parameters
    username = request.args.get("username")
    password = request.args.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        # Query the database to verify the username and password
        query = text(
            """
            SELECT * FROM Student 
            WHERE username = :username AND password = :password
        """
        )
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


@app.route("/LoginTeacher", methods=["GET"])
def LoginTeacher():
    # Retrieve username and password from query parameters
    username = request.args.get("username")
    password = request.args.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        # Query the database to verify the username and password
        query = text(
            """
            SELECT * FROM Teacher 
            WHERE username = :username AND password = :password
        """
        )
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


@app.route("/LoginParent", methods=["GET"])
def LoginParent():
    # Retrieve username and password from query parameters
    username = request.args.get("username")
    password = request.args.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        # Query the database to verify the username and password
        query = text(
            """
            SELECT * FROM Parent 
            WHERE username = :username AND password = :password
        """
        )
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
    query = text(
        f"""SELECT t.id AS qariId, t.name AS qariName, ts.day, s.time, s.slot_id  FROM Teacher t 
                    INNER JOIN TeacherSchedule ts ON t.id = ts.teacher_id 
                    INNER JOIN Slot s ON ts.id = s.sch_id
                    WHERE t.id = '{qari_id}' AND booked = 0"""
    )
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
    query = text(
        f"""SELECT s.name as Studentname, c.name as Coursename, c.description as coursedescription, t.name AS TeacherName, sl.time as SlotTime FROM Student s 
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
                    where s.id='{stu_id}'"""
    )
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
        query = text(
            f"""
            UPDATE Teacher
            SET name = '{name}',
                password = '{password}',
                pic = '{pic}',
                dob = '{dob}',
                qualification = '{qualification}',
                region = '{region}'
            WHERE username = '{username}'
        """
        )

        db.session.execute(query)
        db.session.commit()

        return (
            jsonify(
                {"message": f"Teacher with username '{username}' updated successfully"}
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/GetQariCoursesAndSchedule", methods=["GET"])
def GetQariCoursesAndSchedule():
    qari_id = request.args.get("qari_id")

    if not qari_id:
        return jsonify({"error": "Qari ID is required"}), 400

    query = text(
        """
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
            """
    )

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
            return (
                jsonify(
                    {"message": "No courses or schedules found for the specified Qari"}
                ),
                404,
            )

        return jsonify(rw), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


app.run(debug=True)
