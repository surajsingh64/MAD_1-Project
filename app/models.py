from datetime import datetime
from flask_login import UserMixin
from app import db

# user
class User(UserMixin, db.Model):
     __tablename__ = "users"

     id = db.Column(db.Integer, primary_key=True)
     email = db.Column(db.String(120) , unique=True, nullable=False)
     password = db.Column(db.String(120) , nullable=False)
     role = db.Column(db.String(20), nullable=False)
     is_active = db.Column(db.Boolean, default=True)
     created_at = db.Column(db.DateTime, default=datetime.utcnow)

     def __repr__(self):
          return f"<User {self.email} | {self.role}>"

# Student
class Student(db.Model):
     __tablename__ = "students"
     id = db.Column(db.Integer, primary_key=True )
     user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

     name = db.Column(db.String(100), nullable=False)
     roll_no = db.Column(db.String(50), unique=True, nullable=False)
     branch= db.Column(db.String(50))
     cgpa=db.Column(db.Float)
     phone = db.Column(db.String(15))
     resume = db.Column(db.String(200))

     is_blacklisted = db.Column(db.Boolean, default=False)

     user = db.relationship('User',backref='student', uselist=False)

     def __repr__(self):
          return f"<Student {self.name}>"

# company
class Company(db.Model):
     __tablename__ = "companies"

     id = db.Column(db.Integer, primary_key=True)
     user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
     company_name = db.Column(db.String(150), nullable=False)
     hr_name = db.Column(db.String(100))
     website = db.Column(db.String(150))

     approval_status = db.Column(db.String(20), default="pending")

     is_blacklisted = db.Column(db.Boolean, default=False)
     user = db.relationship('User', backref="company", uselist=False)

     def __repr__(self): 
          return f"<Company {self.company_name}>"




# Placement drive
class PlacementDrive(db.Model):
     __tablename__ = "placement_drives"

     id = db.Column(db.Integer, primary_key=True)
     company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
     job_title = db.Column(db.String(150), nullable=False )
     description = db.Column(db.Text)
     eligibility= db.Column(db.String(200))
     deadline = db.Column(db.Date)
     status = db.Column(db.String(20) , default = 'pending')

     created_at  = db.Column(db.DateTime, default=datetime.utcnow)
     company= db.relationship('Company', backref='drives')

     def __repr__(self):
          return f"<Drive {self.job_title}>"



# Application
class Application(db.Model):
     __tablename__ = "applications"

     id = db.Column(db.Integer, primary_key=True)
     student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
     drive_id =db.Column(db.Integer, db.ForeignKey("placement_drives.id"), nullable=False)
     applied_on =db.Column(db.DateTime, default=datetime.utcnow)
     status = db.Column(db.String(20), default="applied")
     student = db.relationship("Student", backref="applications")
     drive= db.relationship("PlacementDrive", backref="applications")

     __table_args__ = (
          db.UniqueConstraint("student_id","drive_id", name="unique_application"),
     )

     def __repr__(self):
          return f"<Application S : {self.student_id} D : {self.drive_id}>"