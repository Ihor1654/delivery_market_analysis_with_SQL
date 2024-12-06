# delivery_market_analysis_with_SQL
## &#x1F4DC; Description
Hi! This is a project me and my team made in relation to querying! Hereby we were required to answer 5 questions accompanied with visualization. 
We took a modular approach using the sqlalchemy library in python.

![delivery driver](https://cdn.dribbble.com/users/1520198/screenshots/4728543/media/72ec320e7a1ebd2677406cc46bd1d7fd.gif)

## :factory:How does it work?
So essentially we divided up the construction into several python files. a file to handle the databases, a file to handle querying, a file to handle the plotting of the data and finally a file that gives out the answer along with a main file that put's it all together. 

We used sqlalchemy in python to do the querying. Afterwards we manipulated the data using pandas followed by plotting using matplotlib/plotly/geopandas. We used a combination of ORM and OOP for modularity, allowing you to swap out the queries or plots for ease of use.

### Libraries
* sqlalchemy
* Pandas
* Contextily
* Matploblib
* Plotly

### Example outputs
![Deliveroo Distribution](visualizations/deliveroo_distribution.jpg)
![Deliveroo Kapsalon Map](visualizations/deliveroo_kapsalon_map.jpg)

## Repo Structure
```plaintext 
delivery-market-analysis/
│
├── visualizations_data/             
│   └── prices_destribution_data/             
│          └── prices.csv
│   └── kapsalons_data/
│           └── kapsalons_deliveroo
│           └── kapsalons_ubereats
│           └── kapsalons_takeaway
│   └── deliveroo_data
│   └── takeaway_data
│
├── databases/                  
│       └── ubereats.db
│       └── takeaway.db
│       └── deliveroo.db
│
├── assets/
├── visualizations/
│ 
├── utils/
│     └── answers.py
│     └── dbhandler.py
│     └── plotmaker.py
│     └── querybuilder.py
│ 
├── notebooks/
├── requirements.txt                                            
├── README.md                  
└── main.py
```
## :watch: Timeframe 
This project was completed in 5 days

## :panda_face: Updates
So far no updates planned, might change in the future!

## :pushpin: Personal note
This project was done as part of the AI Boocamp at BeCode.org.
### team members
* https://github.com/IzaMacBor
* https://github.com/Ihor1654
* https://github.com/Rasmita-D

Be sure to check out their repos!
