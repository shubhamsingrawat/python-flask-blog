import os
from flask import Flask , render_template , request , flash , session ,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
import json
import datetime
import pymysql
from flask_mail import Mail
#from werkzeug import secure_filename

pymysql.install_as_MySQLdb()

with open('config.json','r') as c:
    params = json.load(c)['params']

app = Flask(__name__)
app.config['UPLOAD'] = params['upload_location']
# updating configration for sendin gmail
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com' ,
    MAIL_PORT = '587',
    MAIL_USE_TLS = True,
    MAIL_USERNAME = params['gmail-user'] ,
    MAIL_PASSWORD = params['gmail-password']
)
mail = Mail(app)

app.secret_key = "super secret key"
if params['local_server']:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Contact(db.Model):
    '''
    name,email,message,phone,date
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable = False)
    email = db.Column(db.String(80), nullable = False)
    message = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(100), nullable = False)
    date = db.Column(db.String(100), nullable = True)

    def __init__(self, name,email,message,phone, date):
       self.name = name
       self.email = email
       self.message = message
       self.phone = phone
       self.date = date

class Posts(db.Model):
    '''
    name,email,message,phone,date
    '''
    sno = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(80), nullable = False)
    content = db.Column(db.String(120), nullable = False)
    date = db.Column(db.String(100), nullable = True)
    slug =  db.Column(db.String(80), nullable = False)
    img_file = db.Column(db.String(80), nullable = False)
    tagline = db.Column(db.String(80), nullable = False)

    def __init__(self, title,content,date,slug,img_file,tagline):
        self.title = title
        self.content = content
        self.date = date
        self.slug = slug
        self.img_file = img_file
        self.tagline = tagline

@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    #[: params['no-of-posts']]
    last = len(posts)/params['no-of-posts']
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1

    page = int(page)
    posts = posts[(page-1)*params['no-of-posts']:(page-1)*params['no-of-posts']+params['no-of-posts']]
    if page==1:
        prev ='#'
        next ='/?page='+str(page+1)
    elif page == last:
        prev ='/?page='+str(page-1)
        next ='#'
    else:
        prev ='/?page='+str(page-1)
        next ='/?page='+str(page+1)

    return render_template('index.html',params = params , posts = posts,prev = prev,next =next)

# @app.route("/home")
# def home_new():
#     posts = Posts.query.filter_by().all()[:params['no-of-posts']]
#     return render_template('index.html',params = params , posts = posts)

# @app.route("/dashboard")
# def dashboard():
#     posts = Posts.query.filter_by().all()[:params['no-of-posts']]
#     return render_template('dashboard.html',params = params, posts = posts)

#/<string:post_slug>", methods = ['GET']
@app.route("/post/<string:post_slug>", methods = ['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug = post_slug).first()
    return render_template('post.html', params = params, post = post)

@app.route("/about")
def about():
    return render_template('about.html',params = params)

@app.route("/dashboard", methods =['GET','POST'])
def dash_login():
    if 'user' in session and session['user'] == params['admin_user']:
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params , posts = posts)
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        user_pass = request.form.get('user_pass')
        if ( user_name == params['admin_user'] and user_pass == params['admin_pass']) :
            session['user'] = user_name
            flash('You were successfully logged in')
            posts = Posts.query.all()
            return render_template('dashboard.html', params = params ,posts = posts)

    return render_template('login.html',params = params)

@app.route("/delete/<string:sno>", methods = ['GET','POST'])
def delete(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        posts = Posts.query.filter_by(sno=sno).first()
        db.session.delete(posts)
        db.session.commit()
        flash('post no '+sno+' is deleted successfully')
    return redirect('/dashboard')

# @app.route("/add",methods=['GET','POST'])
# def add():
#     if 'user' in session and session['user'] == params['admin_user']:
#         if request.method == 'POST':
#             title = request.form.get('title')
#             tagline = request.form.get('tagline')
#             slug = request.form.get('slug')
#             content = request.form.get('content')
#             # img_file = request.form.get('img_file')
#             date = datetime.datetime.now()
#             f = request.files['img_file']
#             f.save(os.path.join(app.config['UPLOAD'], f.filename))
#             entry = Posts(title=title, tagline=tagline, slug=slug, content=content, img_file=f.filename, date=date)
#             print(title)
#             db.session.add(entry)
#             db.session.commit()
#             return redirect('/dashboard')
#     return render_template('add.html', params=params)



@app.route("/edit/<string:sno>", methods = ['GET','POST'])
def edit(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.datetime.now()
            print("nice"+sno)

            if sno== '0':
                title = request.form.get('title')
                tagline = request.form.get('tagline')
                slug = request.form.get('slug')
                content = request.form.get('content')
                # img_file = request.form.get('img_file')
                date = datetime.datetime.now()
                f = request.files['img_file']
                f.save(os.path.join(app.config['UPLOAD'], f.filename))
                entry = Posts(title=title, tagline=tagline, slug=slug, content=content, img_file=f.filename, date=date)
                print(title)
                db.session.add(entry)
                db.session.commit()
                return redirect('/dashboard')
            else :
                posts = Posts.query.filter_by(sno=sno).first()
                posts.title = title
                posts.tagline = tagline
                posts.slug = slug
                posts.content = content
                f = request.files['img_file']
                f.save(os.path.join(app.config['UPLOAD'], f.filename))
                posts.img_file=f.filename
                db.session.commit()
                return redirect('/edit/'+sno)
                print("line 149"+sno)
        posts = Posts.query.filter_by(sno=sno).first()
        print(posts)
        print("line 150"+sno)
        return render_template('edit.html',params = params , posts=posts,sno=sno)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('user', None)
    flash('User is logout sucessfully')
    return redirect('/dashboard')

@app.route("/uploader" , methods=['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            try:
                f= request.files['img_file']
                f.save(os.path.join(app.config['UPLOAD'],f.filename))
                return "uploaded Sucessfully"
            except:
                return "Not uploaded"


@app.route("/contact" ,  methods =['GET','POST'])
def contact():
    if (request.method == 'POST'):
        # name = request.form.get('name')
        # email = request.form.get('email')
        # phone = request.form.get('phone')
        # message = request.form.get('message')
        #entry = Contact(name = name, email = email, phone = phone ,message = message)
        entry = Contact(request.form['name'], request.form['email'], request.form['message'],request.form['phone'],date = datetime.datetime.now() )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('new message good luck from '+ request.form['name'],
                          sender = request.form['email'],
                          recipients = params['guest'],
                          body =  'mobile:'+'\n'+ request.form['phone'] + '\n' + request.form['message']

                          )
        flash('Record was successfully added')
    return render_template('contact.html', params = params)

if __name__ == '__main__':

    app.run(debug = True)