from shop import create_app, db  # Make sure to import your database setup
from shop.models import Product  # Ensure your Product model is imported

# Sample products to add to the database
sweets = [
    Product(name="Toxic Waste", description="Extremely sour candy made from radioactive substances.", price=2.99, image_file="toxic_waste.jpg", carbon_footprint=10.5),
    Product(name="Candy Canes", description="Traditional Christmas treat, great for christmas stockings.", price=1.50, image_file="candy_canes.jpg", carbon_footprint=1.2),
    Product(name="Chocolate Bar", description="Rich milk chocolate bar.", price=3.25, image_file="chocolate_bar.jpg", carbon_footprint=5.0),
    Product(name="Gummy Bears", description="Soft and fruity gummy bears that come in a variety of flavors.", price=2.00, image_file="gummy_bears.jpg", carbon_footprint=3.5),
    Product(name="Jelly Beans", description="Colorful jelly beans with over 20 different flavors.", price=1.99, image_file="jelly_beans.jpg", carbon_footprint=2.5),
    Product(name="Marshmallow Twists", description="Fluffy and sweet marshmallows in fun twist shapes. Great for BBQs.", price=2.25, image_file="marshmallow_twists.jpg", carbon_footprint=1.8)
]

with create_app().app_context():
    db.session.bulk_save_objects(sweets)
    db.session.commit()