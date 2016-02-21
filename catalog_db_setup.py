from flask import Flask#, jsonify
import sqlalchemy
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base


app = Flask(__name__)
# from Flask import flask_sqlalchemy
# from sqlalchemy import create_engine

Base = declarative_base()
engine = create_engine("sqlite:///catalog.db")
# engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(bind=engine)
session = Session()

meta = sqlalchemy.MetaData(bind = engine)


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key = True)
	name = Column(String(120), nullable = False)
	email = Column(String(40), nullable = False)
	picture = Column(String)

	@property
	def serialize(self):
		return {
			'id': self.id,
			'name': self.name,
			'email': self.email,
			'picture': self.picture
		}  

class Category(Base):
	__tablename__ = "categories"

	id = Column(Integer, primary_key = True)
	name = Column(String(120), nullable = False)
	description = Column(String(400) )
	user_id = Column(Integer, ForeignKey("users.id"))
	user = relationship(User, backref = "users")	

	@property
	def serialize(self):
		return {
			'id': self.id,
			'name': self.name,
			"description": self.description,
			"user_id": self.user_id
		}  	


class Item(Base):
	__tablename__ = "items"

	id = Column(Integer, primary_key = True)
	name = Column(String(120), nullable = False)	
	description = Column(String(400) )
	category_id = Column(Integer, ForeignKey("categories.id"))
	category = relationship(Category, backref="categories")	
	user_id = Column(Integer, ForeignKey("users.id"))
	user = relationship(User, backref="user")


	@property
	def serialize(self):
		return {	
			'id': self.id,
			'name': self.name,
			"description": self.description,
			"category_id": self.category_id,
			"user_id": self.user_id
		}  	

User.categories = (relationship("Category", backref="users"))
Category.items = (relationship("Item", backref = "categories"))
Base.metadata.create_all(engine)

def db():
	u = len(session.query(User).all())
	c = len(session.query(Category).all())
	i = len(session.query(Item).all())

	print("User length {0}".format(u))
	print("Category length {0}".format(c))
	print("Item length {0}".format(i))

	return c

def clean():
	session.query(User).delete()
	session.query(Item).delete()
	session.query(Category).delete()
	session.commit()	
	print("DB Cleaned")

def fill_db():

	# Creating Users

 	u = User(name="Pablo", email="pablocangas@gmail.com")
 	session.add(u)
 	u = User(name="Andrea", email="andrea.saravia.c@gmail.com")
 	session.add(u)
 	u = User(name="Gabriela", email="gabriela.cangas@gmail.com")
 	session.add(u)
 	u = User(name="Jose", email="jose.cangas@gmail.com")
 	session.add(u)

 	session.commit

	item_description = """ Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam aliquam 
	augue nec neque venenatis, vel ullamcorper ex elementum. Pellentesque vel faucibus augue, 
	eget facilisis orci. Duis at libero eu ligula sodales cursus sed ac nunc. Integer lobortis 
	sodales ligula in hendrerit. Etiam eget viverra mauris. Mauris scelerisque risus at dui cursus 
	varius. Quisque dictum, quam a faucibus fermentum, nunc turpis ullamcorper sem, ut viverra 
	libero tellus eu urna. Aenean sed neque enim. Nulla laoreet justo ligula, mattis mollis nibh 
	tincidunt ac. Ut felis nunc, cursus non augue ac, bibendum dictum lacus. Praesent vehicula, 
	mi ac fermentum molestie, nisl velit luctus libero, ac maximus felis nisl eget lectus. 
	Curabitur lobortis dui non turpis consequat, non aliquam sem venenatis. Duis est ligula,
	 hendrerit sed nisl sed, aliquam aliquam ex. Fusce eleifend placerat eros, eu tempor mauris 
	 ultricies sed """

	users = session.query(User).all() 

 	movies = ["Deadpool", "Kunfu Panda 3", "Batman vs Superman", "The 5th Wave", "Zoolander 2", "Zootopia", "Finding Dory"]
 	books = ["Red Rising", "Golden Son", "Morning Star", "The Final Empire", "Well of Ascension", "The Hero of Ages"]
 	music = ["Coldplay", "Guns and Roses", "Stratovarius", "iron Maiden", "Soda Stereo"]
 	phones = ["Motorola", "Iphone", "Samsung", "Lumia"]
 	cars= ["Chevrolet", "Toyota", "Suzuki", "Mazda"]
 	bicycles = ["Trek", "GT", "Kanon", "Cannondale"]
 
 	categories = [ ["Movies", movies], ["Books", books ], ["Music", music ], ["Phones", phones], ["Cars", cars ], ["Bicycles", bicycles] ]


	 # Generating Categories
	for i in categories:
		# print("Creating Category {0}".format(i[0]))
		user = random.choice(users)
		print(user.email)
		items = i[1]
		c = Category(name= i[0], description = "Category Description Placeholder", user_id = user.id )
		session.add(c)
		session.commit()

		for x in items:
			u = random.choice(users)
			item = Item(name= x, description = item_description, category_id = c.id, user_id = u.id  )
			print(u.email)
			session.add(item)
			session.commit()
			# print("Item Created {0}".format(item.name)) 			

	print("DB Setup Finished")


print("Cleaning DB")
clean()

if db() <= 0:
	fill_db()	
	print("Filling DB")


# fill_db()
# print(session.query(User).first().email)

