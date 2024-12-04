
# def deliveroo_kapsalon():
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

# def takeaway_kapsalon():
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



