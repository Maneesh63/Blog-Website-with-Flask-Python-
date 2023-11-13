from flask import Flask ,render_template,redirect,request,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import login_required,LoginManager,login_user,logout_user,UserMixin,current_user
from flask_migrate import Migrate
from datetime import datetime

app=Flask(__name__)

app.secret_key="yoursecretkey"
 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:632765@localhost/data'

login_manager = LoginManager()

db=SQLAlchemy(app)
migrate=Migrate(app,db)
 

login_manager.init_app(app)

bcrypt=Bcrypt(app)

class User(db.Model,UserMixin):   
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    #plain text password created by user
    password=db.Column(db.String(150),nullable=False)
    #hash will auto generate a mixtue of strong password so it will help to keep away from attackers
    password_hash = db.Column(db.String(200), nullable=False)

   #current date and time from the datetime library
    date_added=db.Column(db.DateTime,default=datetime.utcnow)

    #established a relationship to Post Model and backref represent current(User) Model
    post=db.relationship('Post', backref='user',lazy=True)
     
    Description=db.relationship('Description', backref='user',lazy=True)


 
    def get_id(self):
        return str(self.user_id)
    

class Like(db.Model):
    like_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'))

class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(600), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    #connected the User model with Post using Foreignkey
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    like = db.relationship('Like', backref='post', lazy='dynamic')

class Description(db.Model):
    des_id=db.Column(db.Integer,primary_key=True)
    des=db.Column(db.String(200), nullable=True)
                                                #backref.table column
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'))





@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

 

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

 
@app.route('/home2')
def home2():
    return render_template('home2.html')


@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']


        
        existing_user=User.query.filter_by(email=email).first()
        if existing_user:
           flash('Email already exists','ex1')
           return redirect('/signup')
        else:
          auth=bcrypt.generate_password_hash(password).decode('utf-8')
         
          new=User(username=username,email=email,password=password,password_hash=auth)
          
        
        
          db.session.add(new)
          db.session.commit()
        
          flash("You Became a Member", 'succ1')
          return redirect(url_for('login'))
         
    return render_template('signup.html')


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']

        check=User.query.filter_by(email=email).first()
        if check and bcrypt.check_password_hash(check.password_hash,password):
            login_user(check)
            flash('you are in','log')
            return redirect('/home')
        
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/home')

@app.route('/delete_user/<int:user_id>',methods=['GET','POST'])
def delete_user(user_id):
   delete=User.query.get_or_404(user_id)
   
   db.session.delete(delete)
   db.session.commit()
   return redirect('/webusers')




@app.route('/create_post',methods=['GET','POST'])
@login_required
def create_post():
    if request.method=='POST':
        title=request.form['title']
        content=request.form['content']
        date=datetime.utcnow()

        
        new=Post(title=title,content=content,date=date,user_id=current_user.user_id)

        db.session.add(new)
        db.session.commit()
        return redirect('/home')

    return render_template('create_post.html')


@app.route('/list')
def list():
    list=Post.query.order_by(Post.date)

    return render_template('list.html',list=list)

@app.route('/individual/<int:post_id>',methods=['GET','POST'])
def individual(post_id):
    individual=Post.query.get_or_404(post_id)

    return render_template('ind.html',individual=individual)

@app.route('/edit_post/<int:post_id>',methods=['GET','POST'])
@login_required
def edit_post(post_id):
    find=Post.query.get_or_404(post_id)
    if request.method=='POST':
      find.title = request.form['title']
      find.content=request.form['content']

      db.session.commit()
      return redirect('/home2')
    return render_template('edit_post.html',find=find)

@app.route('/delete_post/<int:post_id>',methods=['GET','DELETE'])
@login_required
def delete_post(post_id):
     remove=Post.query.get_or_404(post_id)

     if remove.user_id == current_user.user_id:
         db.session.delete(remove)
         db.session.commit()
         return redirect('/list')
     else:
         flash('you are not an authorized user')


@app.route('/admin',methods=['POST','GET'])
@login_required
def admin():
    user_id=current_user.user_id
    if user_id==1:
        data=User.query.get_or_404(user_id)
        db.session.commit()
        return render_template('admin.html',data=data)


@app.route('/webusers',methods=['POST','GET'])
@login_required
def webusers():
    user_id=current_user.user_id
    if user_id==1:
        data=User.query.all()
        db.session.commit()
        return render_template('webuser.html',data=data)


@app.route('/like/<int:post_id>',methods=['GET','POST'])
def like(post_id):
    co=Post.query.get_or_404(post_id)
    lik=like.query(user_id=current_user.user_id,post_id=co.post_id)
  
    db.session.add(lik)
    db.session.commit()


 
@app.route('/dashboard/<int:user_id>', methods=['GET','POST'])
def dashboard(user_id):
    dash=User.query.get_or_404(user_id)
    user_authenticated =True

    return render_template('dashboard.html',dash=dash,user_authenticated=user_authenticated)



@app.route('/description',methods=['GET','POST'])
def description( ):
   
    if request.method=='POST':
        description=request.form['description']
          
        save=Description(description=description)
        db.session.add(save)
        db.session.commit()
        
    
    return render_template('description.html')
          
@app.route('/edit_dash/<int:user_id>',methods=['GET','POST'])
def edit_dash(user_id):
    edit=User.query.get_or_404(user_id)
    if request.method== 'POST':
        
        edit.username=request.form['username']
        db.session.commit()

        return redirect('/dashboard')
    
    return render_template('description.html',edit=edit)


if __name__ == '__main__':
     app.run(debug=True)

