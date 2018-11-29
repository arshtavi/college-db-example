import sqlite3

class db:
    def __init__ (self,dbname):
        try:
            self.db = sqlite3.connect(dbname)
            self.command = self.db.cursor()
            self.command.executescript("""
            CREATE TABLE IF NOT EXISTS
            `Student` (`CWID` INTEGER NOT NULL UNIQUE, 
                `name`	TEXT NOT NULL, `major` TEXT NOT NULL, 
                `level` INTEGER NOT NULL, PRIMARY KEY(`CWID`));
            CREATE TABLE IF NOT EXISTS
            `Enrollment` (`CID` INTEGER NOT NULL,
                `type`	TEXT NOT NULL, `student` TEXT NOT NULL,
                UNIQUE (CID,student));
            CREATE TABLE IF NOT EXISTS
            `Course` (`CID` INTEGER NOT NULL UNIQUE, 
                `title` TEXT NOT NULL, `credit` NUMERIC NOT NULL, 
                PRIMARY KEY(`CID`));""")
            self.db.commit()
        except sqlite3.Error as error:
            print(error.args[0])
        
    def add_student(self,CWID,name,major,level):
        try:
            self.command.execute("""
            INSERT OR REPLACE INTO Student(CWID,name,major,level)
                VALUES ({c},'{n}','{m}',{l});""".format(\
                c=CWID,n=name,m=major,l=level))
            self.db.commit()
        except sqlite3.Error as error:
            print(error.args[0])
    
    def add_course(self,CID,title,credit):
        try:
            self.command.execute("""
            INSERT OR REPLACE INTO Course(CID,title,credit)
                VALUES ({c},'{t}','{cr}');""".format(\
                c=CID,t=title,cr=credit))
            self.db.commit()
        except sqlite3.Error as error:
            print(error.args[0])
            
    def enroll_student(self,CID,type,student):
        try:
            self.command.execute("""
            INSERT OR REPLACE INTO Enrollment(CID,type,student)
                VALUES ((SELECT CID FROM Course WHERE CID = {c}),'{t}',
                (SELECT name FROM Student WHERE name = '{s}'));""".format(\
                c=CID,t=type,s=student))
            self.db.commit()
        except sqlite3.Error as error:
            if 'CID' in error.args[0]:
                print("Enrollment failed - Course does not exist.\n")
            elif 'student' in error.args[0]:
                print("Enrollment failed - Student does not exist.\n")
            else:
                print(error.args[0])
    
    def lookup_student(self,cwid_or_name=''):
        if cwid_or_name is '': return print('No student information provided for lookup.\n')
        if str(cwid_or_name).isdigit():
            for student in self.command.execute("SELECT * FROM Student WHERE CWID = {c};".format(c=cwid_or_name)):
                if student:
                    enrollment = 0
                    enrollment_query = "SELECT COUNT(*) FROM Enrollment WHERE student = '{n}';".format(n=student[1])
                    for enrollments in self.command.execute(enrollment_query):enrollment = enrollments[0]
                    if enrollment==1:
                        return print('CWID:{c}\n{s} is a {l} student enrolled in 1 class.\n'.format(\
                        c=cwid_or_name,s=student[1],l=self.level_verbose(student[3])))
                    else:
                        return print('CWID:{c}\n{s} is a {l} student enrolled in {e} classes.\n'.format(\
                        c=cwid_or_name,s=student[1],l=self.level_verbose(student[3]),e=enrollment))
            return print('No student found with that CWID.\n')
        else:
            for student in self.command.execute("SELECT * FROM Student WHERE name = '{c}';".format(c=cwid_or_name)):
                if student:
                    enrollment = 0
                    enrollment_query = "SELECT COUNT(*) FROM Enrollment WHERE student = '{n}';".format(n=student[1])
                    for enrollments in self.command.execute(enrollment_query):enrollment = enrollments[0]
                    if enrollment==1:
                        return print('CWID:{c}\n{s} is a {l} student enrolled in 1 class.\n'.format(\
                        cwid=student[0],s=cwid_or_name,l=self.level_verbose(student[3])))
                    else:
                        return print('CWID:{c}\n{s} is a {l} student enrolled in {e} classes.\n'.format(\
                        c=student[0],s=cwid_or_name,l=self.level_verbose(student[3]),e=enrollment))
            return print('No student found with that name.\n')
    
    def lookup_course(self, CID_or_title_or_type):
        if str(CID_or_title_or_type).isdigit(): #using course id
            for course in self.command.execute("SELECT * FROM Course WHERE CID = {c};".format(c=CID_or_title_or_type)):
                if course:
                    body = ''
                    i = 0
                    title="[{cid}] {cname} - {credit} credits".format(\
                    credit=course[2],cid=course[0],cname=course[1])
                    self.command.execute(\
                    "SELECT * FROM Enrollment WHERE CID = {c} ORDER BY type;".format(c=CID_or_title_or_type))
                    allstudents=self.command.fetchall()
                    while i < len(allstudents):
                        students = allstudents[i]
                        body+= "({t}) {n}\n".format(t=students[1],n=students[2])
                        i+=1
                    return print("{t}\nStudents attending this course:\n{b}".format(t=title,b=body))
            return print('No course found with that CID.\n')
        else: #using course title/type
            if len(CID_or_title_or_type) < 5: #using course type - (3-4) letter type
                self.command.execute(\
                "SELECT * FROM Enrollment WHERE type='{t}' ORDER BY student;".format(t=CID_or_title_or_type))
                all_students=self.command.fetchall()
                body=''
                if all_students:
                    i = 0
                    while i < len(all_students):
                        students = all_students[i]
                        body += "[{c}] {n}\n".format(c=students[0],n=students[2])
                        i+=1
                    return print("Below is a list of all enrollments for {t} courses:\n{b}".format(b=body,t=CID_or_title_or_type))
                        
                return print('No students are enrolling in any courses.\n')
            else: #using course title
                for course in self.command.execute("SELECT * FROM Course WHERE title = '{t}';".format(t=CID_or_title_or_type)):
                    if course:
                        body = ''
                        i = 0
                        title="[{cid}] {cname} - {credit} credits".format(\
                        credit=course[2],cid=course[0],cname=course[1])
                        self.command.execute(\
                        "SELECT * FROM Enrollment WHERE CID = {c} ORDER BY type;".format(c=course[0]))
                        allstudents=self.command.fetchall()
                        while i < len(allstudents):
                            students = allstudents[i]
                            body+= "({t}) {n}\n".format(t=students[1],n=students[2])
                            i+=1
                        return print("{t}\nStudents attending this course:\n{b}".format(t=title,b=body))
                return print('No course found with that title.\n')
    
    def lookup_all_students(self):
        self.command.execute("SELECT * FROM Enrollment ORDER BY student;")
        all_students=self.command.fetchall()
        body=''
        if all_students:
            i = 0
            while i < len(all_students):
                students = all_students[i]
                body += "({t}) [{c}] {n}\n".format(c=students[0],t=students[1],n=students[2])
                i+=1
            return print("Below is a list of all enrollments:\n{b}".format(b=body))
                
        return print('No students are enrolling in any courses.\n')
                
    def level_verbose(self,level):
        if level==1:return 'Freshman'
        if level==2:return 'Sophomore'
        if level==3:return 'Junior'
        if level==4:return 'Senior'
        if level==5:return 'Graduate'

fall2018 = db('fall2018_semester.db')

fall2018.add_course(505,'Foundation of Cybersecurity Sciences',3)
fall2018.add_course(585,'Applied Cryptography',3)
 
fall2018.add_student(11111111,'Arsh Tavi','Cybersecurity',4)
fall2018.add_student(22222222,'Bill Gates','Computer Science',1)
fall2018.add_student(33333333,'Bob Hugin','Business',3)
fall2018.add_student(44444444,'Lazy Student','Business',1)
fall2018.add_student(55555555,'Good Student','Mathematics',2)

fall2018.enroll_student(505,'DFA','Arsh Tavi')
fall2018.enroll_student(505,'DFA','Bill Gates')
fall2018.enroll_student(505,'DFA','Bob Hugin')
fall2018.enroll_student(505,'DLA','Lazy Student')
fall2018.enroll_student(505,'DFA','Good Student')

fall2018.enroll_student(585,'DLA','Arsh Tavi')
fall2018.enroll_student(585,'DFA','Bill Gates')
fall2018.enroll_student(585,'DLA','Bob Hugin')
fall2018.enroll_student(585,'DFA','Lazy Student')
fall2018.enroll_student(585,'DFA','Good Student')

fall2018.lookup_student('11111111') #using CWID - can be int or string
fall2018.lookup_student('Bill Gtes') #using name
fall2018.lookup_course('505') #using course number - can be int or string
fall2018.lookup_course('Applied Cryptography') #using course title
fall2018.lookup_course('DLA') #using course type
fall2018.lookup_all_students()
