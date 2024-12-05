import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import numpy as np
import os

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


'''

from plotmaker import MapMaker

# Paths to the CSV files containing the data for each platform
file_paths = {
    'ubereats': 'data_for_plots\ubereats_data.csv', 
    'takeaway': 'data_for_plots\takeaway_data.csv', 
    'deliveroo': 'data_for_plots\deliveroo_data.csv'  
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


class KapsalonMapMaker:
    def __init__(self, file_paths):
        """
        Initialize the KapsalonMapMaker class with file paths for each platform.

        Args:
            file_paths (dict): Dictionary where keys are platform names and values are file paths.
        """
        self.file_paths = file_paths
        self.df_all = self.load_data()
        self.gdf_all = self.create_geodataframe()
        self.norm = plt.Normalize(self.gdf_all['avg_pr'].min(), self.gdf_all['avg_pr'].max())
        self.cmap = plt.cm.cividis  # Color map for visualization

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
        return pd.concat(dfs, ignore_index=True)

    def create_geodataframe(self):
        """
        Convert the combined DataFrame into a GeoDataFrame with WGS84 coordinate reference system (EPSG:4326).

        Returns:
            gpd.GeoDataFrame: GeoDataFrame with the data and geometry.
        """
        gdf = gpd.GeoDataFrame(
            self.df_all,
            geometry=gpd.points_from_xy(self.df_all['longitude'], self.df_all['latitude']),
            crs='EPSG:4326'
        )
        # Convert to EPSG:3857 for compatibility with contextily
        return gdf.to_crs(epsg=3857)

    def create_kapsalon_map_for_platform(self, platform_name, output_directory="output_maps"):
        """
        Create and save a map for a given platform with color mapping based on 'avg_pr'.

        Args:
            platform_name (str): The name of the platform to create a map for.
            output_directory (str): Directory to save the map .jpg file. Default is 'output_maps'.
        """
        gdf_platform = self.gdf_all[self.gdf_all['platform'] == platform_name]

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

'''

from plotmaker import KapsalonMapMaker 

# Paths to the CSV files containing the data for each platform
file_paths = {
    'ubereats': 'kapsalons_data/kapsalons_ubereats.csv', 
    'takeaway': 'kapsalons_data/kapsalons_takeaway.csv', 
    'deliveroo': 'kapsalons_data/kapsalons_deliveroo.csv'  
}

# Create an instance of the PlotMaker class with the provided file paths and borders file
kapsalon_map_maker = KapsalonMapMaker(file_paths)

# Save individual maps for each platform to the "output_maps/" directory
kapsalon_map_maker.create_kapsalon_map_for_platform('ubereats', output_directory="output_maps")
kapsalon_map_maker.create_kapsalon_map_for_platform('takeaway', output_directory="output_maps")
kapsalon_map_maker.create_kapsalon_map_for_platform('deliveroo', output_directory="output_maps")

'''
lol