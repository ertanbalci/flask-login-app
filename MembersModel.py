from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager
from datetime import date

db = SQLAlchemy()
login = LoginManager()

class Members(UserMixin, db.Model):
     __tablename__ = "members"
     id        =  db.Column(db.Integer, primary_key=True)
     adı       =  db.Column(db.String(25))
     s_adı     =  db.Column(db.String(25))
     tel       =  db.Column(db.String(12))
     eposta    =  db.Column(db.String(40), unique=True)
     hashed_pw =  db.Column(db.String())
     mem_ilan  =  db.relationship("İlanlar", backref="milan", lazy="dynamic")
     
     def hash_password(self, pw):
          self.hashed_pw = generate_password_hash(pw)

     def control_password(self, pw):
          return check_password_hash(self.hashed_pw, pw)

class İlanlar(db.Model):
     __tablename__ = "ilanlar"
     id        =  db.Column(db.Integer, primary_key=True)
     işlem     =  db.Column(db.String(15))
     ilantarihi=  db.Column(db.Date, default= date.today)
     başlık    =  db.Column(db.String(50))
     il        =  db.Column(db.String(15))
     ilçe_marka=  db.Column(db.String(25))
     mah_model =  db.Column(db.String(35))
     kat_yıl   =  db.Column(db.Integer)
     oda_km    =  db.Column(db.String(7))
     açıklama  =  db.Column(db.String(400))
     fiyat     =  db.Column(db.Integer)
     foto1     =  db.Column(db.String(40))
     foto2     =  db.Column(db.String(40))
     foto3     =  db.Column(db.String(40))
     mem_id    =  db.Column(db.Integer, db.ForeignKey("members.id")) 
     
@login.user_loader
def load_user(id):
     return Members.query.get(int(id))
