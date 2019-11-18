#Entry file for python backend
from flask import Flask,render_template,flash,url_for,session,logging,redirect,request
from data import GetArticles
from flask_mysqldb import MySQL
from wtforms import StringField,TextAreaField,PasswordField,validators,Form
from passlib.hash import sha256_crypt


app = Flask(__name__)
articles = GetArticles()

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Abc@123'
app.config['MYSQL_DB'] = 'myFlaskApp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' # By default return ds of my SQL

# initialize Cursor
mysql = MySQL(app)

@app.route("/")
def Index():
    return render_template("home.html")

@app.route("/about")
def About():
    return render_template("about.html")

@app.route("/articles")
def Articles():
    return render_template("articles.html",articles = articles)

@app.route("/article/<string:id>")
def Article(id):
    return render_template("article.html",id=id)


class RegisterForm(Form):
    name = StringField("Name ",[validators.Length(min=1,max=50)])
    username = StringField("Username ",[validators.Length(min=4,max=50)])
    email = StringField("Email",[validators.Length(min=6,max=100)])
    password = PasswordField("Password",[validators.DataRequired(),
    validators.EqualTo("confirm",message="Password do not match"),
    validators.Length(min=6)])
    confirm = PasswordField("Confirm Password")

@app.route("/register", methods=["GET","POST"])
def Register():
    form = RegisterForm(request.form)
    if (request.method == 'POST' and form.validate()):
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create Cursor
        with mysql.connection.cursor() as cur:
            cur.execute("INSERT INTO user(name,email,username,password) VALUES('{0}','{1}','{2}','{3}')".format(name,email,username,password))
            # commit to db
            mysql.connection.commit()
        flash("Registered Successfully",'success')
        return redirect(url_for("Index"))
    return render_template("register.html",form=form)

# User Login
@app.route("/login",methods=["GET","POST"])
def User_Login():
    if (request.method == "POST"):
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']
        # create cursor
        with mysql.connection.cursor() as cur:
            result = cur.execute("SELECT * FROM user WHERE username = '{0}'".format(username))
            if (result > 0):
                # Get Stored Hash
                queryData = cur.fetchone()
                password_db = queryData['password']
                name = queryData['name']
                # compare password 
                if (sha256_crypt.verify(password_candidate,password_db)):
                    session['logged_in'] = True
                    session['username'] = username
                    session['name'] = name
                    flash("You are now logged in",'success')
                    return redirect(url_for("Index",name=name))
                else:
                    error = "Invalid Login"
                    return render_template("login.html",error=error)
            else:
                error = "User not found"
                return render_template("login.html",error=error)
    return render_template("login.html")
        # get user by username


if (__name__ == '__main__'):
    app.secret_key = 'secret123'
    app.run(debug=True)