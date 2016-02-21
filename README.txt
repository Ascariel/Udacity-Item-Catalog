Instructions:

To run this app, execute the python file called project.py, inside the catalog folder

Once running, go to localhost:5000, and navigate through the website

Initially, the DB for this catalog has been filled with real item names, only descriptions were generated using lorem ipsum to avoid excesive text creation when using a large DB.
ou can update any oh these at any time.

Objectives:

This app allows users to see a catalog list, with items for every category. Users can log in and create categories of their own, as also create items for any category. They can edit or delete categories/items, only when they were the ones who created them.

Theres also an API for this app, to retrieve all categories listed, with their corresponding info
Make a get request to he following endpoint:

localhost:5000/request_categories

To get every item inside a specific category, use the following endpoint:

localhost:5000/category/<category_name>/items

Thanks for using this app :)