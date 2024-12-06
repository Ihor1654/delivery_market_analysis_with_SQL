from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine,inspect,func,desc, cast,distinct, not_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from sqlalchemy import Table, MetaData, String, Integer
import pandas as pd
db_urls = {
        'ubereats': 'sqlite:///databases/ubereats.db',
        'deliveroo': 'sqlite:///databases/deliveroo.db',
        'takeaway': 'sqlite:///databases/takeaway.db'
    }






class DataBaseManager():
    def __init__(self,db_urls) -> None:
        self.db_data = {}
        self.db_urls = db_urls
        for db_name, db_url in db_urls.items():
            self.db_data[db_name] = {'engine': None, 'session': None, 'tables': {}}
            engine = create_engine(db_url, echo=False)
            inspector = inspect(engine)
            self.db_data[db_name]['engine'] = engine
            Session = sessionmaker(bind=engine)
            self.db_data[db_name]['session'] = Session()
            Base = automap_base()
            Base.prepare(autoload_with=engine)
            tabel_list = inspector.get_table_names()
            match db_name:
                case 'ubereats':
                    metadata = MetaData()
                    for tabel in tabel_list:
                        self.db_data[db_name]['tables'][tabel] =   Table(f'{tabel}', metadata, autoload_with=engine)
                case _:
                    base_tabel_list = Base.classes.keys()
                    for tabel in base_tabel_list:
                        self.db_data[db_name]['tables'][tabel] = Base.classes[f'{tabel}']
                    metadata = MetaData()
                    many_to_many_list = [x for x in tabel_list if x not in base_tabel_list]
                    for tabel in many_to_many_list:
                        self.db_data[db_name]['tables'][tabel] = Table(f'{tabel}',metadata,autoload_with=engine)

    def get_session(self,db_name):
        return self.db_data[db_name]['session']
    
    def get_tables(self,db_name):
        return self.db_data[db_name]['tables']
    

    def rest_per_loc_query(self,db_name = 'ubereats'):
        session = self.get_session(db_name)
        tables = self.get_tables(db_name)
        locations = tables['locations']
        locations_to_restaurants = tables['locations_to_restaurants']
        match db_name:
            case 'ubereats':
                query = session.query(
                    locations.c.id.label('id'),
                    locations.c.name.label('location_name'),
                    locations.c.latitude.label('lat'),
                    locations.c.longitude.label('lon'),
                    func.count(locations_to_restaurants.c.restaurant_id).label('restaurant_count')).outerjoin(locations_to_restaurants,locations.c.id == locations_to_restaurants.c.location_id).group_by(locations.c.id).order_by(desc('restaurant_count'))
            case 'takeaway':
                query = session.query(
                    locations.ID.label('id'),
                    locations.name.label('location_name'),
                    locations.latitude.label('lat'),
                    locations.longitude.label('lon'),
                    func.count(locations_to_restaurants.c.restaurant_id).label('restaurant_count')).outerjoin(locations_to_restaurants,locations.ID == locations_to_restaurants.c.location_id).group_by(locations.ID).order_by(desc('restaurant_count'))
            case 'deliveroo':
                query = session.query(
                    locations.id.label('id'),
                    locations.name.label('location_name'),
                    locations.latitude.label('lat'),
                    locations.longitude.label('lon'),
                    func.count(locations_to_restaurants.c.restaurant_id).label('restaurant_count')).outerjoin(locations_to_restaurants,locations.id == locations_to_restaurants.c.location_id).group_by(locations.id).order_by(desc('restaurant_count'))
        res = query.all()
        df = pd.DataFrame(res,columns=['id','name','lat','lon','rest_count'])
        session.close()
        return df

    

    def get_top10_Pizza_restaurants(self,db_name):
        session = self.get_session(db_name)
        tables = self.get_tables(db_name)
        restaurants = tables['restaurants']
        print(type(restaurants))
        match db_name:
            case 'ubereats':
                adjust_rating = (
                        (restaurants.c.rating__rating_value * 0.3) + 
                        (restaurants.c.rating__review_count * 0.7)
                        ).label('weighted_score')
                restaurant_to_categories = tables['restaurant_to_categories']
                query = session.query(cast(restaurants.c.id, String).label('id'),
                                      restaurants.c.title.label('name'),
                                      restaurants.c.rating__rating_value.label('rating'),
                                      func.cast(func.replace(restaurants.c.rating__review_count, '+', ''),Integer).label('review_count'),
                                      adjust_rating 
                                      ).outerjoin(restaurant_to_categories,restaurants.c.id == restaurant_to_categories.c.restaurant_id).where(restaurant_to_categories.c.category == 'Pizza').order_by(desc(adjust_rating)).limit(10)
            case 'takeaway':
                adjust_rating = ((restaurants.ratings*0.3)
                                 + (restaurants.ratingsNumber * 0.7)).label('weighted_score')
                rest_categories = tables['categories_restaurants']
                query = session.query(restaurants.primarySlug.label('id'),
                                      restaurants.name,
                                      restaurants.ratings.label('rating'),
                                      restaurants.ratingsNumber.label('review_count'),
                                      adjust_rating
                                      ).distinct().outerjoin(rest_categories,rest_categories.restaurant_id == restaurants.primarySlug).filter(rest_categories.category_id.like('%pizza%')).where().order_by(desc('weighted_score')).limit(10)
            case 'deliveroo':
               
               adjust_rating = (
                   (restaurants.rating*0.3)+
                   (func.cast(func.replace(restaurants.rating_number, '+', ''),Integer)*0.7)
               ).label('weighted_score')
               query = session.query(
                   restaurants.id,
                   restaurants.name,
                   restaurants.rating,
                  func.cast(
                    func.replace(restaurants.rating_number, '+', ''),
                    Integer
                ),
                adjust_rating
                   ).where(  
                       restaurants.category == 'Pizza' 
                       ).order_by(
                           desc(adjust_rating),
                           ).limit(10)
        
        res = query.all()
        df = pd.DataFrame(res,columns=['id','name','rating','review_count','weight_score'])
        print(df)
        session.close()
        return df

  


    def save_to_csv_dfs_for_rpl(self):
        df_uber = self.rest_per_loc_query().head()
        df_uber.to_csv('vizualizations_data/ubereats_data.csv')
        df_takeaway = self.rest_per_loc_query(db_name='takeaway').head()
        df_takeaway.to_csv('vizualizations_data/takeaway_data.csv')
        df_deliveroo = self.rest_per_loc_query(db_name='deliveroo').head()
        df_deliveroo.to_csv('vizualizations_data/deliveroo_data.csv')

    
    def query_prices_per_db(self, db_name='ubereats'):
        session = self.get_session(db_name)
        tables = self.get_tables(db_name)
        match db_name:
            case 'ubereats':
                menu_items = tables['menu_items']
                query = session.query(menu_items.c.price)
            case 'takeaway':
                menu_items = tables['menuItems']
                query = session.query(menu_items.price)
            case 'deliveroo':
                menu_items = tables['menu_items']
                query = session.query(menu_items.price)
            case _:
                raise ValueError(f"Unsupported database: {db_name}")
        
        prices = [row.price for row in query.all()]
        session.close()
        return prices

    def create_prices_df_for_all_db(self):
        prices_dict = {}
        prices_dict['ubereats'] = self.query_prices_per_db(db_name='ubereats')
        prices_dict['takeaway'] = self.query_prices_per_db(db_name='takeaway')
        prices_dict['deliveroo'] = self.query_prices_per_db(db_name='deliveroo')
        
        prices_df = pd.DataFrame({key: pd.Series(value) for key, value in prices_dict.items()})
        return prices_df
    
    def save_prices_to_csv(self, file_name='price_destribution_data/prices.csv'):
        df = self.create_prices_df_for_all_db()
        df.to_csv(file_name, index=False)
        print(f"Prices saved to {file_name}")

    def get_top_categories(self,db_name):
        session = self.get_session(db_name)
        tables = self.get_tables(db_name)
        restaurants = tables['restaurants']
        match db_name:
            case 'ubereats':
                restaurant_to_categories = tables['restaurant_to_categories']
                query = session.query(
                    restaurant_to_categories.c.category,
                    func.avg(restaurants.c.rating__rating_value).label('avg_rating'),
                    func.avg(restaurants.c.rating__review_count).label('avg_number_of_ratings')
                    ).join(restaurants, restaurants.c.id == restaurant_to_categories.c.restaurant_id).group_by(restaurant_to_categories.c.category).having(func.avg(restaurants.c.rating__review_count)>100).order_by(func.avg(restaurants.c.rating__rating_value).desc())
            case 'takeaway':
                rest_categories = tables['categories_restaurants']
                query = session.query(
                     rest_categories.category_id.label('category'),
                     func.avg(restaurants.ratings).label('avg_rating'),
                     func.avg(restaurants.ratingsNumber).label('avg_number_of_ratings')).join(restaurants, restaurants.primarySlug == rest_categories.restaurant_id).group_by(rest_categories.category_id).having(func.avg(restaurants.ratingsNumber)>100).order_by(func.avg(restaurants.ratings).desc())

            case 'deliveroo':
                query = session.query(restaurants.category,
                                     func.avg(restaurants.rating).label('avg_rating'),
                                     func.avg(restaurants.rating_number).label('avg_number_of_ratings')).group_by(restaurants.category).having(func.avg(restaurants.rating_number)>100).order_by(func.avg(restaurants.rating).desc())
        
        df=pd.read_sql(query.statement,query.session.bind)
        df['adjustedRating'] = df['avg_rating']*0.3 + df['avg_number_of_ratings']*0.7
        sorted_df = df.sort_values(by='adjustedRating',ascending=False)
        session.close()
        return sorted_df
        


    


    def get_kapsalons(self,db_name):
        session = self.get_session(db_name)
        tables = self.get_tables(db_name)
        restaurants = tables['restaurants']
        locations = tables['locations']
        locations_to_restaurants = tables['locations_to_restaurants']
        match db_name:
            case 'ubereats':
                menu_item = tables['menu_items']
                query = session.query(
                    restaurants.c.title.label('restaurant_name'),
                    (func.avg(menu_item.c.price) / 100).label('avg_price'),  
                    func.min(locations.c.latitude).label('latitude'),
                    func.min(locations.c.longitude).label('longitude')
                    ).select_from(menu_item). \
                    join(restaurants, restaurants.c.id == menu_item.c.restaurant_id). \
                    join(locations_to_restaurants, locations_to_restaurants.c.restaurant_id == restaurants.c.id). \
                    join(locations, locations.c.id == locations_to_restaurants.c.location_id). \
                    filter(menu_item.c.name.like('%kapsalon%')). \
                    group_by(restaurants.c.title)
            case 'takeaway':
                menu_item = tables['menuItems']
                query = session.query(
                    restaurants.name.label('restaurant_name'),
                    func.avg(menu_item.price).label('avg_price'),  
                    func.min(locations.latitude).label('latitude'),
                    func.min(locations.longitude).label('longitude')
                    ).select_from(menu_item). \
                    join(restaurants, restaurants.primarySlug == menu_item.primarySlug). \
                    join(locations_to_restaurants, locations_to_restaurants.c.restaurant_id == restaurants.primarySlug). \
                    join(locations, locations.ID == locations_to_restaurants.c.location_id). \
                    filter(menu_item.name.like('%kapsalon%')). \
                    group_by(restaurants.name)
            case 'deliveroo':
                menu_item = tables['menu_items']
                query = session.query(restaurants.name.label('restaurant_name'),
                    func.avg(menu_item.price).label('avg_price'),  
                    func.min(locations.latitude).label('latitude'),
                    func.min(locations.longitude).label('longitude')
                    ).select_from(menu_item). \
                    join(restaurants, restaurants.id == menu_item.restaurant_id). \
                    join(locations_to_restaurants, locations_to_restaurants.c.restaurant_id == restaurants.id). \
                    join(locations, locations.id == locations_to_restaurants.c.location_id). \
                    filter(menu_item.name.like('%kapsalon%')). \
                    group_by(restaurants.name)
        res = query.all()
        df = pd.DataFrame(res,columns=['name','avg_pr','lat','lon'])
        session.close()
        return df
    
    def get_full_kapsalons_df(self):
            kapsalons_list = []
            for db_name in self.db_data.keys():
             kapsalons_list.append( self.get_kapsalons(db_name=db_name))
             kapsalons_df = pd.concat(kapsalons_list, ignore_index=True)
            return kapsalons_df
            
    def save_to_csv_kapsalon_dfs(self):
            for db_name in self.db_data.keys():
              df = self.get_kapsalons(db_name=db_name)
              df.to_csv(f'vizualizations_data/kapsalons_data/kapsalons_{db_name}.csv')
            
    
    def save_kapsalons_to_csv(self, file_name='vizualizations_data/kapsalons_data/kapsalons.csv'):
        df = self.get_full_kapsalons_df()
        df.to_csv(file_name, index=False)
        print(f"Kapsalons saved to {file_name}")


    def get_veg_restaurants(self,db_name):
        session = self.get_session(db_name)
        tables = self.get_tables(db_name)
        Restaurant = tables['restaurants']
        match db_name:
            case 'takeaway':
                MenuItem=tables['menuItems']
                query = session.query(
                distinct(Restaurant.name).label('Restaurant_Name'),
                Restaurant.latitude,
                Restaurant.longitude,
                ).join(MenuItem, Restaurant.primarySlug == MenuItem.primarySlug
                ).filter(MenuItem.name.like('%veg%'))

                takeaway_veg=pd.read_sql(query.statement,query.session.bind)
                takeaway_veg['longitude']= takeaway_veg['longitude'].astype('float64')
                takeaway_veg['latitude']= takeaway_veg['latitude'].astype('float64')
                takeaway_veg['source']='takeaway'

                return takeaway_veg

            case 'ubereats':
                MenuItem=tables['menu_items']
                query = session.query(
                distinct(Restaurant.c.title).label('Restaurant_Name'),
                Restaurant.c.location__latitude.label('latitude'),
                Restaurant.c.location__longitude.label('longitude')
                ).join(MenuItem, Restaurant.c.id == MenuItem.c.restaurant_id
                ).filter(MenuItem.c.name.like('%veg%'))

                ubereats_veg=pd.read_sql(query.statement,query.session.bind)
                ubereats_veg['latitude'] = ubereats_veg['latitude'].astype('float64')
                ubereats_veg['longitude'] = ubereats_veg['longitude'].astype('float64')
                ubereats_veg['source']='ubereats'

                return ubereats_veg

            case 'deliveroo':
                MenuItem=tables['menu_items']
                query = session.query(
                distinct(Restaurant.name).label('Restaurant_Name'),
                Restaurant.latitude,
                Restaurant.longitude,
                ).join(MenuItem, Restaurant.id == MenuItem.restaurant_id
                ).filter(MenuItem.name.like('%veg%'))

                deliveroo_veg=pd.read_sql(query.statement,query.session.bind)
                deliveroo_veg['latitude']= deliveroo_veg['latitude'].astype('float64')
                deliveroo_veg['longitude']= deliveroo_veg['longitude'].astype('float64')
                deliveroo_veg['source']='deliveroo'

                return deliveroo_veg




