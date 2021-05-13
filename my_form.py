from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, TextAreaField
from wtforms.validators import InputRequired, Email, EqualTo, Length, Optional

class yForm(FlaskForm): # yeni üye formu
     adı = StringField("Adınız", [InputRequired(),
                                  Length(min=3, message="İsim en az 3 karakter olmalı")])
     s_adı = StringField("Soyadınız", validators=[InputRequired()])
     tel   = StringField("Telefon No", validators=[InputRequired()])
     eposta = StringField("e-posta adresiniz", validators=[InputRequired(),
                                                           Email(message="Geçersiz E-Posta Adresi")])
     parola = PasswordField("Parolanız", [InputRequired(),
                                          Length(min=8, max=16,
                                                 message="Parola uzunluğu 8-16 karakter olmalı")])
     cparola = PasswordField("Parolanız Tekrar", [EqualTo("parola", message="Girdiğiniz parolalar farklı")])
     submit = SubmitField("Gönder")

class gForm(FlaskForm): # yeni giriş formu (login formu)
     eposta = StringField("e-posta adresiniz", validators=[InputRequired(),
                                                           Email(message="Geçersiz E-Posta Adresi")])
     parola = PasswordField("Parolanız", [InputRequired(),
                                          Length(min=8, max=16,
                                                 message="Parola uzunluğu 8-16 karakter olmalı")])
     submit = SubmitField("Gönder")
          
class diForm(FlaskForm): # Daire ilan formu
     başlık = StringField("İlan Başlığı", [InputRequired()])
     il     = StringField("İl", [InputRequired()])
     ilçe   = StringField("İlçe", [InputRequired()])
     mahalle= StringField("Mahalle", [InputRequired()])
     kat    = StringField("Bulunduğu Kat", [InputRequired()])
     oda    = StringField("Oda/Salon Sayısı", [InputRequired()])
     ilan   = TextAreaField("İlan Açıklama", render_kw={'rows':'4', 'cols':'80'}, validators=[InputRequired()])
     fiyat  = IntegerField("Fiyat (TL)", [InputRequired()])
     submit = SubmitField("Kaydet")

class viForm(FlaskForm): # Araç ilan formu
     başlık = StringField("İlan Başlığı", [InputRequired()])
     il     = StringField("İl", [InputRequired()])
     marka  = StringField("Marka", [InputRequired()])
     model  = StringField("Model", [InputRequired()])
     yıl    = StringField("Yıl", [InputRequired()])
     km     = StringField("Km", [InputRequired()])
     ilan   = TextAreaField("İlan Açıklama", render_kw={'rows':'4', 'cols':'80'}, validators=[InputRequired()])
     fiyat  = IntegerField("Fiyat (TL)", [InputRequired()])
     submit = SubmitField("Kaydet")


     
