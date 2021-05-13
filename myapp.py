from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user
from MembersModel import Members, İlanlar, db, login
from datetime import date
from my_form import yForm, gForm, diForm, viForm 
import os

app = Flask(__name__)
app.secret_key = "xyz12346"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".jpeg", ".png"] 
app.config["UPLOAD_FOLDER"] = "static/uploaded_images"

db.init_app(app)         #db objesini ana uygulamaya bağlıyoruz ve ilklendiriyoruz
login.init_app(app)      #login objesini ana uygulamaya bağlıyoruz ve ilklendiriyoruz
login.login_view = "login" #kimliği doğrulanmamış kullanıcılar login sayfasına yönlndirilecek

@app.before_first_request # ilk kullanıcı request'inden önce 
def create_all():         # sadece bir kez veritabanını oluşturuyoruz.
     db.create_all()

@app.route('/')         # Ana sayfa
def index():            # Uygulama varsayılan olarak satılık daire ilanlarını
     return redirect(url_for("ilanlar", search="SATILIK DAİRE")) # göstermek üzere ilanlar view fonksiyonuna yönlendirilir.                               

# Fonksiyon search parametresi alır. SATILIK DAİRE - KİRALIK DAİRE - SATILIK ARAÇ
# Kullanıcı authentication işlemi yapmış mı? kullanıcı adı / Misafir
# Tüm ilanlar VT'ından çekilir. Search değerine göre ilan listesi hazırlanır.
# index.html sayfası search, liste ve kullanıcı adı parametreleri ile açılır.
# index sayfasında
# - ilanlar listelenir.
# - Satılık/kiralık araç/ev bağlantıları arasında geçiş yapılabilir.
# - ilan tıklandığında ilan hakkında detay sayfası açılır.
# - Ziyaretçi siteye üye olmak istiyorsa yeni üyelik sayfasına yönlendirilir.
# - Ziyaretçi üye ise login sayfasına geçebilir.     
@app.route('/ilanlar/<search>', methods = ['POST', 'GET'])
def ilanlar(search):
     if current_user.is_authenticated:
          user = current_user.adı
     else:
          user = "Misafir"
     li = []
     for i in İlanlar.query.all():
          if search == i.işlem:
               li.append([date.strftime(i.ilantarihi, "%d.%m.%Y"), i.başlık,
                         i.il, i.ilçe_marka, i.mah_model, i.kat_yıl, i.fiyat, i.id, i.mem_id])
     return render_template("index.html", mems=li, user=user, search=search)

# Search. ilan id ve üye id parametrelerini alır.
# İlanlar tablosundan ilan id ile ilan objesi çekilir.
# Members tablosundan ilan üye id ile üye objesi çekilir.
# detay.html sayfası bu parametreler ile açılır. Sayfada
# - ilan bilgileri / fotoğraflar ve satıcının iletişim bilgileri gösterilir.
@app.route('/detay/<search>/<ilan_id>/<mem_id>', methods = ['POST', 'GET'])
def detay(search, ilan_id, mem_id):
     i = İlanlar.query.get(ilan_id)
     m = Members.query.filter(Members.id==mem_id).first() #Members.query.get(mem_id)
     if not i.foto1: i.foto1="no_image.png"
     if not i.foto2: i.foto2="no_image.png"
     if not i.foto3: i.foto3="no_image.png"
     print(i.foto1)
     print(i.foto2)
     print(i.foto3)
     
     return render_template("detay.html", ilan=i, mem=m, search=search)

# new_acc.html sayfası açılır.
# Sayfada adı, soyadı, tel no, eposta adresi ve parola hücreleri ile
# submit butonunu içeren bir form vardır.
# form doldurulup (post ile) submit edildiğinde
# eposta adresi Members tablosunda aranır.Bulunamazsa 
# bilgiler ve hash edilmiş parola tabloya kaydedilir. İndex fonksiyona dönülür.
@app.route('/new_account', methods = ['POST', 'GET'])
def new_account():
     form = yForm()
     if form.validate_on_submit():
          adı  = form.adı.data
          sadı = form.s_adı.data
          tel  = form.tel.data
          pos  = form.eposta.data
          psw  = form.parola.data
          if Members.query.filter_by(eposta=pos).first():
               return pos+ " eposta adresi mevcut."
          member = Members(adı=adı, s_adı=sadı, tel=tel, eposta=pos)
          member.hash_password(psw)
          db.session.add(member)
          db.session.commit()
          return redirect("/")
     else:
          return render_template("new_acc.html", form=form)

# Kullanıcı authentication işlemi yapmışsa memberpage fonksiyonuna yönlendirilir.
# login.html sayfası açılır.
# Sayfada e-posta ve parola hücreleri ve submit butonu içeren bir form vardır.
# form doldurulup submit edildiğinde
# - Members tablosunda eposta adresi aranır. Bulunursa parola teydi yapılır.
# - Parola doğrulanırsa kullanıcı oturumu başlatılır.
# - uygulama memberpage fonksiyonuna yönlendirilir.
# - eposta kayıtlı değilse/parola yanlışsa login.html hata mesajı ile açılır.     
@app.route('/login', methods = ['POST', 'GET']) 
def login():
     mesaj=""
     form=gForm()
     if current_user.is_authenticated:
          return redirect("member_page")
     if form.validate_on_submit():
          m_pos  = form.eposta.data
          m_psw  = form.parola.data
          member = Members.query.filter_by(eposta=m_pos).first()
          if member:
               m_id =member.id
               if member.control_password(m_psw):
                    login_user(member)
                    return redirect("member_page")
          mesaj="Hatalı eposta adresi veya parola"
          return render_template("login.html", form=form, mesaj=mesaj)
     return render_template("login.html", form=form, mesaj=mesaj)

# Bu kullanıcının tüm ilanları İlanlar tablosundan liste halinde çekilir.
# memberpage.html sayfası ilanlar listesi ile açılır. Bu sayfada:
# - Kullanıcının tüm ilanları listelenir.
# - Kullanıcı yen bir ilan girmek isterse seçimine göre 
#   daire_ilan veya araç_ilan fonksiyonuna yönlendirilir.
# - Kull.ilanına fotoğraf eklemek isterse foto_ekle fonksiyonuna yönlendirilir.
# - Kull.bir ilanı silmek isterse ilan no ile ilan_sil fonksiyonuna yönlendirilir.
@app.route('/member_page')
@login_required     # Sadece login olmuş kullanıcılar erişebilir. 
def member_page():
     ilanlarım = İlanlar.query.filter_by(mem_id=current_user.id).all()
     return render_template("memberpage.html", ilanlarım=ilanlarım, sil="")

# daire_ilan.html sayfası açılır. 
# Sayfada daireye ait bilgi hücreleri ile submit butonunu içeren bir form vardır.
# form doldurulup submit edildiğinde bilgiler İlanlar tablosuna kaydedilir. 
@app.route('/daire_ilan/<islem>', methods = ['POST', 'GET'])
@login_required                    # Sadece login olmuş kullanıcılar erişebilir. 
def daire_ilan(islem):             # islem = "SATILIK DAİRE"  veya "KİRALIK DAİRE"
     form=diForm()
     if form.validate_on_submit():
          bas = form.başlık.data
          il  = form.il.data
          ilc = form.ilçe.data
          mah = form.mahalle.data
          kat = form.kat.data
          oda = form.oda.data
          fyt = form.fiyat.data
          iln = form.ilan.data
          yeni_ilan = İlanlar(işlem=islem, başlık=bas, il=il, ilçe_marka=ilc, mah_model=mah, kat_yıl=kat,
                              oda_km=oda, fiyat=fyt, açıklama=iln, mem_id=current_user.id)
          db.session.add(yeni_ilan)
          db.session.commit()
          return redirect("/member_page")
     else:
          return render_template("daire_ilan.html", form=form, islem=islem)
     
 
 # araç_ilan.html sayfası açılır. islem içeriği SATILIK ARAÇ
 # Sayfada araca ait bilgi hücreleri ile submit butonunu içeren bir form vardır.
 # form doldurulup submit edildiğinde bilgiler İlanlar tablosuna kaydedilir.     
@app.route('/arac_ilan/<islem>', methods = ['POST', 'GET'])
@login_required   # Sadece login olmuş kullanıcılar erişebilir.
def arac_ilan(islem): # islem = "SATILIK ARAÇ"
     form=viForm()
     if form.validate_on_submit():
          bas = form.başlık.data
          il  = form.il.data
          mrk = form.marka.data
          mod = form.model.data
          yıl = form.yıl.data
          km  = form.km.data
          fyt = form.fiyat.data
          iln = form.ilan.data
          yeni_ilan = İlanlar(işlem=islem, başlık=bas, il=il, ilçe_marka=mrk, mah_model=mod, kat_yıl=yıl,
                              oda_km=km, fiyat=fyt, açıklama=iln, mem_id=current_user.id)
          db.session.add(yeni_ilan)
          db.session.commit()
          return redirect("/member_page")
     else:
          return render_template("araç_ilan.html", form=form, islem=islem)

# İlanlar tablosunda ilan no bulunur ve kayıt silinir.
# member-page fonksiyonuna geri dönülür. 
@app.route('/ilan_sil/<ilanno>', methods = ['POST', 'GET'])
@login_required   # Sadece login olmuş kullanıcılar erişebilir.
def ilan_sil(ilanno):
     silinecekilan = İlanlar.query.get(ilanno)
     db.session.delete(silinecekilan)
     db.session.commit()
     return redirect("/member_page")
     
# foto_loader.html sayfası açılır.
# Kullanıcı bilgisayarından bir imaj dosyası yükler.Post eder.(max 3 imaj)
# Dosyanın uzantı uygunluk kontolü yapılır.
# Uygunsa imaj ilan ve sıra numarası ile birlikte VT'na kaydedilir. 
# member-page fonksiyonuna geri dönülür.
@app.route('/foto_ekle/<ilanno>/<no>', methods = ['POST', 'GET'])
@login_required   # Sadece login olmuş kullanıcılar erişebilir.
def foto_ekle(ilanno,no):
     if request.method=="POST":
          dosya = request.files["imaj"]
          if dosya:
               uzanti = os.path.splitext(dosya.filename)[1].lower()
               dosya_adi = "im-"+str(ilanno)+"-"+str(no)+uzanti
               if uzanti in app.config["UPLOAD_EXTENSIONS"]:
                    dosya.save(os.path.join(app.config["UPLOAD_FOLDER"], dosya_adi))
                    ilan = İlanlar.query.get(ilanno)
                    if no=="1":
                         ilan.foto1=dosya_adi
                    elif no=="2":
                         ilan.foto2=dosya_adi
                    else:
                         ilan.foto3=dosya_adi
                    db.session.add(ilan) # ilanı güncelliyoruz
                    db.session.commit()
          return redirect("/member_page")
     else:
          return render_template("foto_loader.html", ilanno=ilanno, no=no)
     
# Bu fonksiyon çağrıldığında kullanıcı oturumu sonlandırılır.
# Uygulama akışı index fonksiyonuna yönlendirilir.
@app.route('/logout')
def logout():
     logout_user()
     return redirect(url_for("index"))

if __name__ == "__main__":
     app.run(debug=True)

 
