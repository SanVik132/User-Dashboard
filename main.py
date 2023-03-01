'''
You need to create a Dashboard where you need to show all the user list who's registered and you have to create a super admin who can manage all the users from the Dashboard.

Sing up Panel: Name, email, Mobile, Description & submit.
* once the user will submit the details. Details should be saved on the database server.

Login Panel: Email, Password & submit
* once the user will submit the details. then the user can see the dashboard

Dashboard:
On Dashboard, the user can see their details like, Picture upload or change, Password reset, Mobile and other details can be changed by him.

Note: the Candidate needs to complete the task within 2 Days.

'''

from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def is_valid(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT userId, email, password, user_type FROM users')
    data = cur.fetchall()
    for row in data:
        if row[1] == email and row[2] == hashlib.md5(password.encode()).hexdigest():
            session['userId'] = row[0]
            session['user_type'] = row[3]
            return True
    return False

@app.route("/home")
def root():
    loggedIn, firstName, user_type ,userId = getLoginDetails()
    if loggedIn:
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            if user_type == 'admin':    
                cur = conn.cursor()
                cur.execute('SELECT userId, email, firstName, lastName, image FROM users')
                itemData = cur.fetchall()
            else:
                cur.execute('SELECT userId, email, firstName, lastName, image FROM users WHERE userId = ?', (userId, ))
                itemData = cur.fetchone()
        return render_template('home.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName,user_type = user_type)
    else:
        return render_template('login.html', error='')



def getLoginDetails():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            user_type = None
        else:
            loggedIn = True
            cur.execute("SELECT userId, firstName,user_type FROM users WHERE email = ?", (session['email'], ))
            userId, firstName,user_type = cur.fetchone()
    conn.close()
    return (loggedIn, firstName, user_type,userId)


@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        print(request.form)
        #Parse form data    
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO users (password, email, firstName, lastName) VALUES (?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName))

                con.commit()

                msg = "Registered Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return render_template("login.html", error=msg)


@app.route("/register_admin", methods = ['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        print(request.form)
        #Parse form data    
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO users (password, email, firstName, lastName,user_type) VALUES (?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName,'admin'))

                con.commit()

                msg = "Registered Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return render_template("login.html", error=msg)




@app.route("/registerationForm")
def registrationForm():
    return render_template("register.html")

@app.route("/registerationadminForm")
def registrationadminForm():
    return render_template("register-admin.html")

@app.route("/")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)


@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('loginForm'))

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS



@app.route("/updateProfileadmin", methods=["GET", "POST"])
def updateProfileadmin():
    if request.method == 'POST':
        UserId = int(request.args.get('UserId'))
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        
        image = request.files['image']

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        print(imagename)
        with sqlite3.connect('database.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute('UPDATE users SET firstName = ?, lastName = ?, email = ?, image = ? WHERE UserId = ?', (firstName, lastName, email, imagename,UserId))

                    con.commit()
                    msg = "Saved Successfully"
                except:
                    con.rollback()
                    msg = "Error occured"
                print(msg)
        con.close()
        return redirect(url_for('editProfile'))




@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        
        image = request.files['image']

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        print(imagename)
        with sqlite3.connect('database.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute('UPDATE users SET firstName = ?, lastName = ?, email = ?, image = ? WHERE email = ?', (firstName, lastName, email, imagename,email))

                    con.commit()
                    msg = "Saved Successfully"
                except:
                    con.rollback()
                    msg = "Error occured"
                print(msg)
        con.close()
        return redirect(url_for('editProfile'))
    
@app.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('/'))
    print(getLoginDetails())
    loggedIn, firstName, user_type,userId = getLoginDetails()
    return render_template("profileHome.html", loggedIn=loggedIn, firstName=firstName)

@app.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('/'))
    loggedIn, firstName, user_type,userId = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, firstName, lastName, image FROM users WHERE userId = ?", (session['userId'], ))
        profileData = cur.fetchone()
    conn.close()
    return render_template("editProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName)


@app.route("/account/profileedit")
def editProfileroot():

    UserId = int(request.args.get('UserId'))
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, firstName, lastName, image FROM users WHERE userId = ?", (UserId, ))
        profileData = cur.fetchone()
    conn.close()
    return render_template("editProfileroot.html", profileData=profileData)




@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    if 'email' not in session:
        return redirect(url_for('/'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId, password FROM users WHERE email = ?", (session['email'], ))
            userId, password = cur.fetchone()
            if (password == oldPassword):
                try:
                    cur.execute("UPDATE users SET password = ? WHERE userId = ?", (newPassword, userId))
                    conn.commit()
                    msg="Changed successfully"
                except:
                    conn.rollback()
                    msg = "Failed"
                return redirect(url_for('logout'))
                #return render_template("changePassword.html", msg=msg)
            else:
                msg = "Wrong password"
        conn.close()
        #return redirect(url_for('logout'))
        return render_template("changePassword.html", msg=msg)
    else:
        return render_template("changePassword.html")


if __name__ == '__main__':
    app.run(debug=True)