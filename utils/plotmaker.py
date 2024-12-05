import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import numpy as np
import plotly.express as px


class MapMaker:
    def __init__(self, file_paths, borders_path):
        """
        Initialize the PlotMaker class with file paths for the data and borders.

        Args:
            file_paths (dict): Dictionary containing platform names as keys and CSV file paths as values.
            borders_path (str): Path to the GeoJSON or shapefile containing region boundaries.
        """
        self.file_paths = file_paths
        self.borders_path = borders_path
        self.platform_colors = {
            'ubereats': 'blue',
            'takeaway': 'green',
            'deliveroo': 'red'
        }
        self.df_all = self.load_data()
        self.gdf_all = self.create_geodataframe()
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
        return df_all[df_all['rest_count'] > 0]

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

    def create_combined_map(self, output_file=None):
        """
        Create a combined map showing all platforms on the same plot.

        Args:
            output_file (str): Path to save the output file. If None, the plot will not be saved.
        """
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

    def create_individual_maps(self, output_directory="output_maps/"):
        """
        Create individual maps for each platform with color scale and size scale.
        
        Args:
            output_directory (str): Directory to save the individual maps. Default is 'output_maps/'.
        """
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









'''
from plotmaker import PlotMaker

# Paths to the CSV files containing the data for each platform
file_paths = {
    'ubereats': 'ubereats_data.csv', 
    'takeaway': 'takeaway_data.csv', 
    'deliveroo': 'deliveroo_data.csv'  
    }

# Path to the boundaries GeoJSON or shapefile for plotting the region's borders
borders_path = 'gadm41_BEL_3.shx'  

# Create an instance of the PlotMaker class with the provided file paths and borders file
plot_maker = PlotMaker(file_paths, borders_path)

# Save the combined map (with all platforms) to the output folder as a JPG file
plot_maker.create_combined_map(output_file="output_maps/combined_map.jpg")

# Save individual maps for each platform to the "output_maps/" directory
plot_maker.create_individual_maps(output_directory="output_maps/")

'''