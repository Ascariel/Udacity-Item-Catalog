General Instructions:

To run this app, execute the python file called project.py, inside the catalog folder

Once running, go to localhost:5000, and navigate through the website

Initially, the DB for this catalog has been filled with real item names, only descriptions were generated using lorem ipsum to avoid excesive text creation when using a large DB.
You can update any oh these at any time.



App Usage:

This app allows users to see a catalog list, with items for every category. Users can log in and create categories of their own, as also create items for any category. They can edit or delete categories/items, only when they were the ones who created them.

Theres also an API for this app, to retrieve all categories listed, with their corresponding info
Make a get request to he following endpoint:

localhost:5000/request_categories

To get every item inside a specific category, use the following endpoint:

localhost:5000/category/<category_name>/items 


Environment Set Up :

Make sure you have the following installed:

<ul>
<li><a href="https://www.virtualbox.org/">VirtualBox</a></li>
<li><a href="https://www.vagrantup.com/">Vagrant</a></li>
<li><a href="https://git-scm.com/">Git</a></li>
<li><a href="http://www.sqlalchemy.org/download.html">SQL Alchemy</a></li>
<li><a href="http://flask.pocoo.org/docs/0.10/quickstart/">Flask</a></li>

</ul>

Clone this repo with the following URL:
git clone https://github.com/Ascariel/Udacity-Item-Catalog.git

Go to App folder
cd Udacity-Item-Catalog/

Start Virtual Machine: 
vagrant up

SSH into Virtual Machine:
vagrant ssh

Go to app folder inside de VM:
cd /vagrant

Run the app:
python project.py


DB Set Up:
The app autopopulates when you run the project.py file, so you can relax




Thanks for using this app :)