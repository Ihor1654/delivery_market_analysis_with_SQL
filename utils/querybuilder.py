''' 
Question 4 query functions

'''


# import pandas as pd
# from sqlalchemy import create_engine, func, Table, MetaData, inspect
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.automap import automap_base

# def deliveroo_kapsalon():
#     DATABASE_URL = 'sqlite:///databases/deliveroo.db'
#     engine = create_engine(DATABASE_URL)

#     metadata = MetaData()
#     locations_to_restaurants = Table('locations_to_restaurants', metadata, autoload_with=engine)

#     Base = automap_base()
#     Base.prepare(autoload_with=engine)
#     restaurants = Base.classes.restaurants
#     menu_item = Base.classes.menu_items
#     locations = Base.classes.locations

#     Session = sessionmaker(bind=engine)
#     session = Session()

 
#     query = session.query(
#         restaurants.name.label('restaurant_name'),
#         func.avg(menu_item.price).label('avg_price'),
#         func.min(locations.latitude).label('latitude'),  
#         func.min(locations.longitude).label('longitude')  
#     ).select_from(menu_item). \
#         join(restaurants, restaurants.id == menu_item.restaurant_id). \
#         join(locations_to_restaurants, locations_to_restaurants.c.restaurant_id == restaurants.id). \
#         join(locations, locations.id == locations_to_restaurants.c.location_id). \
#         filter(menu_item.name.like('%kapsalon%')). \
#         group_by(
#             restaurants.name
#         )

#     result = query.all()
#     results = []
#     if result:
#         for row in result:
#             results.append({
#                 'restaurant_name': row.restaurant_name,
#                 'avg_price': row.avg_price, 
#                 'latitude': row.latitude,
#                 'longitude': row.longitude
#             })
#     else:
#         print("No results found.")
    
#     return results 


# def ubereats_kapsalon():
#     DATABASE_URL = 'sqlite:///databases/ubereats.db'
#     engine = create_engine(DATABASE_URL)
    
#     metadata = MetaData()

#     try:
#         restaurants = Table('restaurants', metadata, autoload_with=engine)
#         menu_item = Table('menu_items', metadata, autoload_with=engine)
#         locations = Table('locations', metadata, autoload_with=engine)
#         locations_to_restaurants = Table('locations_to_restaurants', metadata, autoload_with=engine)
#     except Exception as e:
#         print(f"Error loading tables: {e}")
#         return []  

#     Session = sessionmaker(bind=engine)
#     session = Session()

#     print(f"Restaurants Columns: {[column.name for column in restaurants.columns]}")
#     print(f"Menu Items Columns: {[column.name for column in menu_item.columns]}")
#     print(f"Locations Columns: {[column.name for column in locations.columns]}")

#     try:
#         query = session.query(
#             restaurants.c.title.label('restaurant_name'),
#             (func.avg(menu_item.c.price) / 100).label('avg_price'),  
#             func.min(locations.c.latitude).label('latitude'),
#             func.min(locations.c.longitude).label('longitude')
#         ).select_from(menu_item). \
#             join(restaurants, restaurants.c.id == menu_item.c.restaurant_id). \
#             join(locations_to_restaurants, locations_to_restaurants.c.restaurant_id == restaurants.c.id). \
#             join(locations, locations.c.id == locations_to_restaurants.c.location_id). \
#             filter(menu_item.c.name.like('%kapsalon%')). \
#             group_by(restaurants.c.title)

#         result = query.all()
#         results = []
#         if result:
#             for row in result:
#                results.append({
#                     'restaurant_name': row.restaurant_name,
#                     'avg_price': row.avg_price,
#                     'latitude': row.latitude,
#                     'longitude': row.longitude
#                 })
#         else:
#             print("No results found.")

#     except Exception as e:
#         print(f"Error executing query: {e}")
#         return []

#     return results

# def takeaway_kapsalon():
#     DATABASE_URL = 'sqlite:///databases/takeaway.db'
#     engine = create_engine(DATABASE_URL)

   
#     metadata = MetaData()

   
#     try:
#         restaurants = Table('restaurants', metadata, autoload_with=engine)
#         menu_item = Table('menuItems', metadata, autoload_with=engine)
#         locations = Table('locations', metadata, autoload_with=engine)
#         locations_to_restaurants = Table('locations_to_restaurants', metadata, autoload_with=engine)
#     except Exception as e:
#         print(f"Error loading tables: {e}")
#         return

#     Session = sessionmaker(bind=engine)
#     session = Session()


#     print(f"Restaurants Columns: {[column.name for column in restaurants.columns]}")
#     print(f"Menu Items Columns: {[column.name for column in menu_item.columns]}")
#     print(f"Locations Columns: {[column.name for column in locations.columns]}")
    
#     try:
#         query = session.query(
#             restaurants.c.name.label('restaurant_name'),
#             func.avg(menu_item.c.price).label('avg_price'),
#             func.min(locations.c.latitude).label('latitude'),
#             func.min(locations.c.longitude).label('longitude')
#         ).select_from(menu_item). \
#             join(restaurants, restaurants.c.primarySlug == menu_item.c.primarySlug). \
#             join(locations_to_restaurants, locations_to_restaurants.c.restaurant_id == restaurants.c.primarySlug). \
#             join(locations, locations.c.ID == locations_to_restaurants.c.location_id). \
#             filter(menu_item.c.name.like('%kapsalon%')). \
#             group_by(restaurants.c.name)

#         result = query.all()
#         results = []
#         if result:
#             for row in result:
#                results.append({
#                     'restaurant_name': row.restaurant_name,
#                     'avg_price': row.avg_price,
#                     'latitude': row.latitude,
#                     'longitude': row.longitude
#                 })
#         else:
#             print("No results found.")

#     except Exception as e:
#         print(f"Error executing query: {e}")
#         return []

#     return results

# deliveroo_results = deliveroo_kapsalon()
# ubereats_results = ubereats_kapsalon()
# takeaway_results = takeaway_kapsalon()
# merged_results = deliveroo_results + ubereats_results + takeaway_results

# df = pd.DataFrame(merged_results)
# df = df.drop_duplicates()
# print(df)

lol