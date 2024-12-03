from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine,inspect,func
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, MetaData

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
            engine = create_engine(db_url, echo=True)
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
                        self.db_data[db_name]['tables'][tabel] =   Table(f'{tabel}', metadata, autoload_with=engine).c
                case _:
                    base_tabel_list = Base.classes.keys()
                    for tabel in base_tabel_list:
                        self.db_data[db_name]['tables'][tabel] = Base.classes[f'{tabel}']
                    metadata = MetaData()
                    many_to_many_list = [x for x in tabel_list if x not in base_tabel_list]
                    for tabel in many_to_many_list:
                        self.db_data[db_name]['tables'][tabel] = Table(f'{tabel}',metadata,autoload_with=engine).c

    def get_session(self,db_name):
        return self.db_data[db_name]['session']
    
    def get_tables(self,db_name):
        return self.db_data[db_name]['tables']
    

    def query_execution_example(self,db_name):
        session = self.get_session(db_name)
        tables = self.get_tables(db_name)
        restaurants = tables['restaurants']
        query = session.query(restaurants.title)
        res = query.all()
        session.close()
        return res

        
    




manager = DataBaseManager(db_urls=db_urls)
# print(manager.db_data)

for row in manager.query_execution_example('ubereats'):
    print(row[0])

