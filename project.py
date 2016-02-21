
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, json, session
import random, string
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalog_db_setup import Base, User, Category, Item

app = Flask(__name__)
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Convenience methods

def get_category_with_name(category_name):
	category = session.query(Category).filter(Category.name == category_name).first()
	return category

def get_item_with_name(item_name):
	item = session.query(Item).filter(Item.name == item_name).first()
	return item

def get_category_with_id(category_id):
	category = session.query(Category).filter(Category.id == category_id).first()
	return category

def get_item_with_id(item_id):
	item = session.query(Item).filter(Item.id == item_id).first()
	return item	

def get_user_with_id(user_id):
	user = session.query(User).filter(User.id == user_id).first()
	return user

def get_user_with_email(email):
	user = session.query(User).filter(User.email == email).first()
	return user	

# Routing

@app.route("/")
def home():
	categories = session.query(Category).order_by(Category.id.desc()).all()
	items = session.query(Item).order_by(Item.id.desc()).limit(10)

	# Forgery Protection
	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
	for x in xrange(32))
	login_session['state'] = state	


	return render_template("home.html", items= items, categories = categories, \
	 login_session = login_session, state = state)


@app.route("/login/log_user/", methods=["POST", "GET"])
def log_user():
	# Gets response info from facebook authentication, and creates a session object
	# containing them, allowing to maintain login state through different views

	response = request.args



	user_id = response["userID"]
	email = response["email"]
	picture = response["picture"]
	name = response["name"]
	token = response["accessToken"]
	state = response["state"]
	user = get_user_with_email(email)

	if state != login_session["state"]:
		return "Invalid state parameter"	

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
	# Cleans login session to logout user

	login_session.pop("email")
	login_session.pop("picture")
	login_session.pop("name")
	login_session.pop("state")
	login_session.pop("user_id")

	return "Login session erased: {0}".format(login_session)


# One Category View
@app.route("/catalog/<category_name>")
def category(category_name):
	# Shows info for one specific category
	category = get_category_with_name(category_name)
	categories = session.query(Category).all()
	items = category.items

	return render_template("category.html", categories = categories, category = category, \
	                       items = items)

# One Item View
@app.route("/catalog/<category_name>/items/<item_name>")
def item(category_name, item_name):
	# Shows info for one specific item

	categories = session.query(Category).all()
	item = get_item_with_name(item_name)
	category = item.category

	return render_template("item.html", categories = categories, category = category, \
	                       item = item)

# Add Item
@app.route("/catalog/<category_name>/items/new", methods = ["GET", "POST"])
def new_item(category_name):
	categories = session.query(Category).all()
	category = get_category_with_name(category_name)
	
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
		item = Item(name = name, description = description, category_id = category.id, \
		            user_id = login_session["user_id"])
		session.add(item)
		session.commit()		
		return redirect("/catalog/{0}".format(category.name))
	else:
		return render_template("add_item.html", category = category)

# Add Category
@app.route("/catalog/new", methods = ["GET", "POST"])
def new_category():
	if request.method == "GET":
		return render_template("add_category.html")

	# Processing Post Request
	name = request.form.get("name")

	validation_result = validate_creation("Category", name)
	valid = validation_result[0]
	message = validation_result[1]
	flash(message)

	if valid:
		category = Category(name = name, user_id = login_session["user_id"])
		session.add(category)
		session.commit()		
		return redirect("/")
	else:
		return render_template("add_category.html")


@app.route("/catalog/<category_name>/edit", methods = ["GET", "POST"])
def edit_category(category_name):
	category = get_category_with_name(category_name)

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

@app.route("/catalog/<category_name>/items/<item_name>/edit", methods = ["GET", "POST"])
def edit_item(category_name, item_name):

	item = get_item_with_name(item_name)
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

	if valid:
		item.name = name if name else item.name
		item.description = description if description else item.description
		session.add(item)
		session.commit()		
		return redirect("/catalog/{0}".format(category.name))
	else:
		return render_template("edit_item.html", category = category, item = item)



@app.route("/catalog/<category_name>/items/<item_name>/delete", methods = ["GET", "POST"])
def delete_item(category_name, item_name):

	item = get_item_with_name(item_name)
	category = item.category

	if request.method == "GET":
		return render_template("delete_item.html", category = category, item = item)

	# Processing Post Request
	name = request.form.get("name")

	session.delete(item)
	session.commit()
	flash("Item {0} was successfully deleted".format(item.name))

	return redirect("/catalog/{0}".format(category.name))

@app.route("/catalog/<category_name>/delete", methods = ["GET", "POST"])
def delete_category(category_name):

	category =  get_category_with_name(category_name)
	items = category.items

	if request.method == "GET":
		return render_template("delete_category.html", category = category)

	# Processing Post Request
	for i in items:
		print("Deleting " + i.name)
		session.delete(i)
		session.commit()

	session.delete(category)
	session.commit()
	flash("Category {0}, and all items inside were successfully deleted".format(category.name))

	return redirect("/")

# Starting API Endpoints
@app.route("/request_categories")
def request_categories():
	# Returns all categories in JSON format
	categories = session.query(Category).all()
	formatted_category_array = [c.serialize for c in categories]

	return json.dumps(formatted_category_array)

@app.route("/category/<category_name>/request_items")
def request_category_items(category_name):
	category = get_category_with_name(category_name)

	if category == None:
		return "Category not found for :{0}".format(category_name)

	items = category.items
	formatted_items_array = [i.serialize for i in items]

	return json.dumps(formatted_items_array)


	def create_user(name, email, picture):
		if(get_user_with_email(email)):
			print("Email already in use")
			return False
		else:
			user = User(name=name, email = email, picture = picture)
			session.add(user)
			session.commit()
			return user

# VALIDATION METHODS

def validate_creation(record_type, name, optional_category_id = None):
	if record_type == "Category":
		record = session.query(Category).filter(Category.name.like(name)).first()
	else:
		if (optional_category_id == None): 
			raise NameError, "Optional category_id was not given as argument, and was needed" 
		record = session.query(Item).filter(Item.name.like(name)) \
		.filter(Item.category_id == optional_category_id).first()

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
		available_name = session.query(Category).filter(Category.name.like(name)) \
		.filter(Category.id != record.id).count() == 0 or name == record.name
	else:
		# record = session.query(Item).filter(Item.name.like(name)).filter(Item.category_id == optional_category_id).first()
		print(name)
		print("record.name:")
		print(name, record.name)

		category = record.category
		available_name = session.query(Item).filter(Item.name.like(name)) \
		.filter(Item.category_id == category.id).count() == 0 or name == record.name

	
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





