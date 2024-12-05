import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import numpy as np
import plotly.express as px
import os



class MapMaker:
    def __init__(self, file_paths):
        """
        Initialize the PlotMaker class with file paths for the data and borders.

        Args:
            file_paths (dict): Dictionary containing platform names as keys and CSV file paths as values.
            borders_path (str): Path to the GeoJSON or shapefile containing region boundaries.
        """
        self.file_paths = file_paths
        self.borders_path = None
        self.platform_colors = {
            'ubereats': 'blue',
            'takeaway': 'green',
            'deliveroo': 'red'
        }
        self.df_all = self.load_data()
        self.gdf_all = self.create_geodataframe()
        self.borders = None

    def set_borders(self,border_path):
        self.borders_path = border_path
        self.borders = self.load_borders()
        

    def load_data(self):
        """
        Load data from CSV files and combine it into one DataFrame.

        Returns:
            pd.DataFrame: Combined DataFrame with data from all platforms.
        """
        dfs = []
        for platform, path in self.file_paths.items():
            df = pd.read_csv(path)
            df['platform'] = platform
            df['color'] = self.platform_colors[platform]
            dfs.append(df)

        df_all = pd.concat(dfs, ignore_index=True)
        return df_all

    def create_geodataframe(self):
        """
        Convert the DataFrame to a GeoDataFrame and set CRS to WGS84.

        Returns:
            gpd.GeoDataFrame: GeoDataFrame with restaurant locations.
        """
        gdf = gpd.GeoDataFrame(
            self.df_all,
            geometry=gpd.points_from_xy(self.df_all['lon'], self.df_all['lat']),
            crs='EPSG:4326'
        )
        return gdf.to_crs(epsg=3857)

    def load_borders(self):
        """
        Load the region boundaries from a shapefile or GeoJSON file.

        Returns:
            gpd.GeoDataFrame: GeoDataFrame with region boundaries.
        """
        borders = gpd.read_file(self.borders_path)
        if borders.crs is None:
            borders.set_crs(epsg=4326, inplace=True)
        return borders.to_crs(epsg=3857)
    
    def create_kapsalon_map_for_platform(self, platform_name, output_directory="output_maps"):
        """
        Create and save a map for a given platform with color mapping based on 'avg_pr'.

        Args:
            platform_name (str): The name of the platform to create a map for.
            output_directory (str): Directory to save the map .jpg file. Default is 'output_maps'.
        """
        gdf_platform = self.gdf_all[self.gdf_all['platform'] == platform_name]
        self.norm = plt.Normalize(self.gdf_all['avg_pr'].min(), self.gdf_all['avg_pr'].max())
        self.cmap = plt.cm.cividis  # Color map for visualization

        # Create a plot for better visibility
        fig, ax = plt.subplots(figsize=(14, 10))

        # Plot the restaurant locations with color mapping based on 'avg_pr'
        scatter = gdf_platform.plot(
            ax=ax,
            markersize=gdf_platform['avg_pr'] * 10 if 'avg_pr' in gdf_platform.columns else 50,
            cmap=self.cmap,
            norm=self.norm,
            alpha=0.7,
            legend=False  # Disable the automatic legend to customize it later
        )

        # Add a basemap using contextily
        ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

        # Add a color bar (legend) on the side of the map
        sm = plt.cm.ScalarMappable(cmap=self.cmap, norm=self.norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, orientation='vertical', fraction=0.02, pad=0.04)
        cbar.set_label('Average Price', rotation=270, labelpad=20)

        # Set the plot title
        ax.set_title(f"Map of Kapsalon Locations and Their Average Prices ({platform_name.capitalize()})", fontsize=18)

        # Remove axis for a cleaner look
        ax.set_axis_off()

        # Ensure the output directory exists
        os.makedirs(output_directory, exist_ok=True)

        # Save the plot as a .jpg file
        output_file_path = os.path.join(output_directory, f"{platform_name}_kapsalons_map.jpg")
        plt.savefig(output_file_path, bbox_inches='tight', dpi=300, format='jpg')
        plt.close()  # Close the plot to free up memory

    def create_combined_map(self, border_path,output_file=None):
        """
        Create a combined map showing all platforms on the same plot.

        Args:
            output_file (str): Path to save the output file. If None, the plot will not be saved.
        """
        if self.borders is None:
            self.set_borders(border_path)
        self.df_all = self.df_all[self.df_all['rest_count'] > 0]

        fig, ax = plt.subplots(figsize=(12, 8))

        # Plot the boundaries
        self.borders.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=0.5)

        # Plot the restaurant locations for each platform
        for platform in self.df_all['platform'].unique():
            gdf_platform = self.gdf_all[self.gdf_all['platform'] == platform]
            ax.scatter(
                gdf_platform.geometry.x,
                gdf_platform.geometry.y,
                s=np.interp(gdf_platform['rest_count'], (self.gdf_all['rest_count'].min(), self.gdf_all['rest_count'].max()), (10, 100)),
                c=gdf_platform['color'].iloc[0],
                alpha=0.7,
                label=platform.capitalize()
            )

        # Add a basemap using contextily
        ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

        # Customize the plot
        ax.set_title("Distribution of Restaurants by Platform", fontsize=16)
        ax.set_axis_off()
        plt.legend(loc='upper right')

        if output_file:
            plt.savefig(output_file, bbox_inches='tight', dpi=300, format='jpg')  # Save as .jpg
            plt.close()  # Close the plot to avoid it being shown
        else:
            plt.show()

    def create_individual_maps(self, border_path,output_directory="output_maps/"):
        """
        Create individual maps for each platform with color scale and size scale.
        
        Args:
            output_directory (str): Directory to save the individual maps. Default is 'output_maps/'.
        """
        self.df_all = self.df_all[self.df_all['rest_count'] > 0]
        if  self.borders is None:
            self.set_borders(border_path)
        for platform in self.df_all['platform'].unique():
            gdf_platform = self.gdf_all[self.gdf_all['platform'] == platform]
            fig, ax = plt.subplots(figsize=(12, 8))

            # Plot the boundaries
            self.borders.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=0.5)

            # Plot the restaurant locations with a color scale
            scatter = ax.scatter(
                gdf_platform.geometry.x,
                gdf_platform.geometry.y,
                s=np.interp(gdf_platform['rest_count'], (self.gdf_all['rest_count'].min(), self.gdf_all['rest_count'].max()), (10, 100)),
                c=gdf_platform['rest_count'],
                cmap='plasma',
                alpha=0.7,
                label=platform.capitalize()
            )

            # Add a basemap using contextily
            ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

            # Add a color bar
            cbar = plt.colorbar(scatter, ax=ax, orientation='vertical')
            cbar.set_label('Number of Restaurants', fontsize=12)

            # Customize the plot
            ax.set_title(f"Distribution of Restaurants for {platform.capitalize()}", fontsize=16)
            ax.set_axis_off()
            plt.legend(loc='upper right')

            # Save the map as a .jpg file
            output_file = f"{output_directory}{platform}_distribution.jpg"
            plt.savefig(output_file, bbox_inches='tight', dpi=300, format='jpg')
            plt.close()  # Close the plot to avoid it being shown


class PlotMaker():
    def __init__(self,df,name) -> None:
        self.df = df
        self.df_name = name
    

    def change_df(self,df,name):
        self.df = df
        self.df_name = name

    
    def create_top_ten_pizza_plot(self,):
        self.df['review_count'] = pd.to_numeric(self.df['review_count'], errors='coerce')
        
        fig = px.scatter(self.df, 
        x='weight_score', 
        y='name', 
        size='review_count',  
        color='rating',  
        hover_name='name',  
        size_max=60,
        title=f'Top 10 Restaurants by Rating and Review Count ({self.df_name})',
        labels={'rating': 'Rating', 'name': 'Restaurant', 'review_count': 'Review Count','weight_score':'Adjusted Rating'}
        )
        fig.update_layout(
            xaxis_title='Adjusted ratio',
            yaxis_title='Restaurant',
            showlegend=False
        )
        fig.update_yaxes(categoryorder='array', categoryarray=self.df['name'][::-1])
        fig.show()

    def plot_top_categories(self):
        df = self.df.head()
        df['category'] = df['category'].replace('2600','Miscellaneous')
        fig = px.bar(df, x='category', y='avg_rating',
                hover_data=['avg_rating','avg_number_of_ratings'], color='category',
                title=f'Top 5 categories in {self.df_name}',
                labels={'avg_rating':'Rating','category':'Category'}
                )
        fig.update_traces(showlegend=False)
        fig.update_layout( xaxis={'categoryorder':'total descending'},title_x=0.5)
        fig.show()

    def price_distribution(self):
        
        df_clean = self.df.apply(pd.to_numeric, errors='coerce')
        df_clean = df_clean.dropna(how='any')
        df_clean['ubereats'] = df_clean['ubereats'].apply(lambda x: x / 100 if pd.notnull(x) else x)

        df_long = df_clean.melt(var_name='Platform', value_name='Price (in Euros)')
        
        price_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        price_labels = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90-100']
        
        df_long['Price Range'] = pd.cut(df_long['Price (in Euros)'], bins=price_bins, labels=price_labels, right=False)
        
        fig = px.histogram(
            df_long, 
            x='Price Range', 
            color='Platform', 
            title=f"Price Distribution per Platform (in Euros) -",
            labels={"Price Range": "Price Range (in Euros)", "count": "Frequency"},
            category_orders={"Price Range": price_labels},
            barmode='group', 
            color_discrete_map={
                'ubereats': 'blue',
                'takeaway': 'green',
                'deliveroo': 'red'
            }
        )
        
        print(df_long['Price Range'].value_counts())
        fig.show()

