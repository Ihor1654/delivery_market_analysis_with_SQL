from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine,inspect,func,desc, cast,distinct
from sqlalchemy.orm import sessionmaker
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
                restaurant_to_categories = tables['restaurant_to_categories']
                query = session.query(cast(restaurants.c.id, String).label('id'),restaurants.c.title.label('name'),restaurants.c.rating__rating_value.label('rating'),restaurants.c.rating__review_count.label('review_count') ).outerjoin(restaurant_to_categories,restaurants.c.id == restaurant_to_categories.c.restaurant_id).where(restaurant_to_categories.c.category == 'Pizza',restaurants.c.rating__review_count>50).order_by(desc('rating')).limit(10)
            case 'takeaway':
                rest_categories = tables['categories_restaurants']
                query = session.query(restaurants.primarySlug.label('id'),restaurants.name,restaurants.ratings.label('rating'),restaurants.ratingsNumber.label('review_count'),).distinct().outerjoin(rest_categories,rest_categories.restaurant_id == restaurants.primarySlug).filter(rest_categories.category_id.like('%pizza%')).where(restaurants.ratingsNumber>50).order_by(desc('rating'),desc('review_count')).limit(10)
            case 'deliveroo':
               query = session.query(restaurants.id,
                      restaurants.name,
                      restaurants.rating,
                      restaurants.rating_number.label('review_count')).where(cast(restaurants.rating_number,Integer) > 9,restaurants.category == 'Pizza').order_by(desc(restaurants.rating),desc(restaurants.rating_number)).limit(10)
        
        
        res = query.all()
        for row in res:
            print(f'id: {row.id}, title: {row.name}, rating: {row.rating}, review_count: {row.review_count}  ')
        df = pd.DataFrame(res,columns=['id','name','rating','review_count'])
        session.close()
        return df

  


    def create_df_for_all_db_rpl(self):
        df_dict = {}
        df_dict['ubereats'] = self.rest_per_loc_query().head()
        df_dict['takeaway'] = self.rest_per_loc_query(db_name='takeaway').head()
        df_dict['deliveroo'] = self.rest_per_loc_query(db_name='deliveroo').head()
        return df_dict
    
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
    
    def save_prices_to_csv(self, file_name='prices.csv'):
        df = self.create_prices_df_for_all_db()
        df.to_csv(file_name, index=False)
        print(f"Prices saved to {file_name}")

    


        
    




