
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, json, session
import random, string
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalog_db_setup import Base, User, Category, Item

app = Flask(__name__)
engine = create_engine('sqlite:///catalog.db')
# engine = create_engine("sqlite:///catalog.db")
# engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()



@app.route("/")
def home():
	categories = session.query(Category).order_by(Category.id.desc()).all()
	items = session.query(Item).order_by(Item.id.desc()).limit(10)

	# Forgery Protection
	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
	for x in xrange(32))
	login_session['state'] = state	

	# print(login_session)

	# if("email" in  login_session):


	return render_template("home.html", items= items, categories = categories, login_session = login_session, state = state)
# Login, Token extension
@app.route("/login/log_user/", methods=["POST", "GET"])
def log_user():

	response = request.args
	print(response)
	user_id = response["userID"]
	email = response["email"]
	picture = response["picture"]
	name = response["name"]
	token = response["accessToken"]
	state = response["state"]
	user = session.query(User).filter(User.email == email).first()


	if user:
		user.picture = picture
		session.add(user)
		session.commit()
		
	else:
		user = User(name=name, email=email, picture = picture)
		session.add(user)
		session.commit()
		flash("New user created {0}".format(email))

		

	login_session["email"] = email
	login_session["picture"] = picture
	login_session["name"] = name
	login_session["user_id"] = user.id
	login_session["state"] = state

	print(login_session)

	return "login_session worked for {0}: {1}".format(name, email)

@app.route("/user/logout", methods=["POST", "GET"])
def logout_user():

	login_session.pop("email")
	login_session.pop("picture")
	login_session.pop("name")
	login_session.pop("state")
	login_session.pop("user_id")


	print(login_session)

	return "Login session erased: {0}".format(login_session)


# One Category
@app.route("/catalog/<category_id>")
def category(category_id):
	categories = session.query(Category).all()
	category = session.query(Category).filter(Category.id == category_id).first()
	items = category.items
	# items = session.query(Item).filter(Item.category_id == category_id).order_by(Item.id.desc()).limit(10)
	print(category.user.email)

	return render_template("category.html", categories = categories, category = category, items = items)

# One Item
@app.route("/catalog/<category_id>/items/<item_id>")
def item(category_id, item_id):
	categories = session.query(Category).all()

	item = session.query(Item).filter(Item.id == item_id).first()
	category = item.category

	print("############################# Item " + item.name + " Owner " + item.category.user.email)
	return render_template("item.html", categories = categories, category = category, item = item)

# Add Item
@app.route("/catalog/<category_id>/items/new", methods = ["GET", "POST"])
def new_item(category_id):
	categories = session.query(Category).all()
	category = session.query(Category).filter(Category.id == category_id).first()
	
	if request.method == "GET":
		return render_template("add_item.html", category = category)

	# Processing Post Request
	name = request.form.get("name")
	description = request.form.get("description")

	validation_result = validate_creation("Item", name, category.id)
	valid = validation_result[0]
	message = validation_result[1]
	flash(message)	

	if valid:
		item = Item(name = name, description = description, category_id = category.id, user_id = login_session["user_id"])
		session.add(item)
		session.commit()		
		return redirect("/catalog/{0}".format(category.id))
	else:
		return render_template("add_item.html", category = category)

	
	


@app.route("/user/<user_id>")
def user_info(user_id):
	print("inside user_info")

	user = session.query(User).filter_by(id = user_id).first()

	if user == None:
		flash("User not registered, please create an account")
		return redirect(url_for("home"))

	return render_template("/test.html", user = user)


@app.route("/catalog/new", methods = ["GET", "POST"])
def new_category():
	if request.method == "GET":
		print(login_session["user_id"])
		return render_template("add_category.html")

	# Processing Post Request
	name = request.form.get("name")

	validation_result = validate_creation("Category", name)
	valid = validation_result[0]
	message = validation_result[1]
	flash(message)

	print(login_session["user_id"])

	if valid:
		category = Category(name = name, user_id = login_session["user_id"])
		session.add(category)
		session.commit()		
		return redirect("/")
	else:
		return render_template("add_category.html")


@app.route("/catalog/<category_id>/edit", methods = ["GET", "POST"])
def edit_category(category_id):

	category = session.query(Category).filter(Category.id == category_id ).first()

	if request.method == "GET":
		return render_template("edit_category.html", category = category)

	# Processing Post Request
	name = request.form.get("name")

	validation_result = validate_edit("Category", category, name)
	valid = validation_result[0]
	message = validation_result[1]
	flash(message)

	if valid:
		category.name = name
		session.add(category)
		session.commit()		
		return redirect("/")
	else:
		return render_template("edit_category.html", category = category)

@app.route("/catalog/<category_id>/items/<item_id>/edit", methods = ["GET", "POST"])
def edit_item(category_id, item_id):

	item = session.query(Item).filter(Item.id == item_id).first()
	category = item.category

	if request.method == "GET":
		return render_template("edit_item.html", category = category, item = item)

	# Processing Post Request
	name = request.form.get("name") 
	description = request.form.get("description")

	validation_result = validate_edit("Item", item, name)
	valid = validation_result[0]
	message = validation_result[1]
	flash(message)
	print("Item desc")
	print(description)

	if valid:
		item.name = name if name else item.name
		item.description = description if description else item.description
		session.add(item)
		session.commit()		
		return redirect("/catalog/{0}".format(category.id))
	else:
		return render_template("edit_item.html", category = category, item = item)



@app.route("/catalog/<category_id>/items/<item_id>/delete", methods = ["GET", "POST"])
def delete_item(category_id, item_id):

	item = session.query(Item).filter(Item.id == item_id).first()
	category = item.category

	if request.method == "GET":
		return render_template("delete_item.html", category = category, item = item)

	# Processing Post Request
	name = request.form.get("name")

	session.delete(item)
	session.commit()
	flash("Item {0} was successfully deleted".format(item.name))

	return redirect("/catalog/{0}".format(category.id))

@app.route("/catalog/<category_id>/delete", methods = ["GET", "POST"])
def delete_category(category_id):

	category = session.query(Category).filter(Category.id == category_id ).first()
	items = category.items

	if request.method == "GET":
		return render_template("delete_category.html", category = category)

	# Processing Post Request
	for i in items:
		print("Deleting " + i.name)
		session.delete(i)
		session.commit()

	print("Deleting Category " + category.name)
	session.delete(category)
	session.commit()
	flash("Category {0}, and all items inside were successfully deleted".format(category.name))

	return redirect("/")


	def create_user(name, email, picture):
		if(get_user_id(email)):
			print("Email already in use")
			return False
		else:
			user = User(name=name, email = email, picture = picture)
			session.add(user)
			session.commit()
			return user


	def get_user_info(user_id):
		user = session.query(User).filter(User.id == user_id).first()
		return user

	def get_user_id(email):
		user = session.query(User).filter(User.email == email).first()
		return user


# VALIDATION METHODS

def validate_creation(record_type, name, optional_category_id = None):
	if record_type == "Category":
		record = session.query(Category).filter(Category.name.like(name)).first()
	else:
		if (optional_category_id == None): 
			raise NameError, "Optional category_id was not given as argument, and was needed" 
		record = session.query(Item).filter(Item.name.like(name)).filter(Item.category_id == optional_category_id).first()

	new_record = record == None
	empty_name = len(name) == 0

	# Form Validation
	if new_record and not empty_name:
		message = "{0} {1} Successfully Created".format(record_type, name)
		return [True, message]
	# Prevents Empty Name
	elif empty_name:
		print("Failed: Empty Name")
		message = "{0} Name can't be empty. Try another name".format(record_type)
		return [False, message]
	# Prevents Repeated name
	elif not new_record:
		print("Failed: Repeated {0}")
		message =  "{0} Name {1} already exists. Try another name".format(record_type, name)
		return [False, message]
	
def validate_edit(record_type, record, name):
	if record_type == "Category":
		# record = session.query(Category).filter(Category.id == record.id).first()
		# name = record.name
		print(name)
		print("record.name:")
		print(name, record.name)
		available_name = session.query(Category).filter(Category.name.like(name)).filter(Category.id != record.id).count() == 0 or name == record.name
	else:
		# record = session.query(Item).filter(Item.name.like(name)).filter(Item.category_id == optional_category_id).first()
		print(name)
		print("record.name:")
		print(name, record.name)

		category = record.category
		available_name = session.query(Item).filter(Item.name.like(name)).filter(Item.category_id == category.id).count() == 0 or name == record.name

	
	empty_name = len(name) == 0

	# Form Validation
	if available_name and not empty_name:
		message = "{0} {1} Successfully Updated".format(record_type, name)
		return [True, message]
	# Prevents Empty Name
	elif empty_name:
		print("Failed: Empty Name")
		message = "{0} Name can't be empty. Try another name".format(record_type)
		return [False, message]
	# Prevents Repeated name
	elif not available_name:
		print("Failed: Repeated {0}")
		message =  "{0} Name {1} is already being used. Try another name".format(record_type, name)
		return [False, message]















if __name__ == '__main__':
		app.secret_key = "super_secret_key"
		app.debug = True
		app.run(host='0.0.0.0', port=5000)





