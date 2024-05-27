import plotly.express as px
import geopandas as gpd
import panel as pn
import pandas as pd
import hvplot.pandas
import os
import re
import warnings
warnings.filterwarnings("ignore")

pn.extension('katex', 'mathjax', 'plotly')

print("Starting application...")

########################### LOAD DATASET ##################
# Cargo el archivo shp
gdf = gpd.read_file(os.path.join('Municipalities_with_topo.shp'))
gdf = gdf.to_crs("WGS84")

# Cargo el archivo con los datos
df = pd.read_csv(os.path.join('Municipalities_with_topo.csv'), dtype={"CVEGEO": str})
df = df.iloc[:,2:]

# Etiquetas para las columnas
def generate_description(col):
    desc = col
    # Reemplazar los sufijos específicos
    desc = re.sub(r'_mean$', ' Mean', desc)
    desc = re.sub(r'_stde$', ' Sd', desc)
    desc = re.sub(r'_max$', ' Max', desc)
    # Reemplazar los prefijos específicos
    desc = re.sub(r'^tri1k', 'TRI', desc)
    desc = re.sub(r'^vrm1k', 'VRM', desc)
    desc = re.sub(r'^tpi1k', 'TPI', desc)
    desc = re.sub(r'^slp1k', 'Slope', desc)
    desc = re.sub(r'^rou1k', 'Roughness', desc)
    desc = re.sub(r'^ele1k', 'Elevation', desc)
    return desc

# Crear el diccionario de descripciones
descriptions = {col: generate_description(col) for col in df.columns}

# Renombrar las columnas del DataFrame original
df.rename(columns=descriptions, inplace=True)
    #dfgeo.rename(columns=descriptions, inplace=True)
df_page = df.head()

# Variables para los widgets
numeric_cols = df.iloc[:,4:].columns
vars = list(descriptions.values())[6:]
vars_mean = [descriptions[col] for col in descriptions if col.endswith('_mean')]
vars_stde = [descriptions[col] for col in descriptions if col.endswith('_stde')]
vars_max = [descriptions[col] for col in descriptions if col.endswith('_max')]

################################# CREATE TABLES ############################
t_summ = df_page.describe().T

print("Dataset loaded successfully")
################################# CREATE CHARTS ############################
@pn.cache(max_items=32, policy='LRU')
def create_kde(sel_var):
    return df.hvplot.kde(y=sel_var, alpha=0.5).opts(active_tools=[],tools=['pan'])

@pn.cache(max_items=32, policy='LRU')
def create_scatter_chart(x_axis, y_axis):
    return df.hvplot.scatter(x=x_axis, y=y_axis, color="CVE_ENT",
                                size=100, alpha=0.9, height=400).opts(active_tools=['wheel_zoom'])

@pn.cache(max_items=32, policy='LRU')
def create_bar_chart(sel_cols):
    # Agrupar y calcular la media
    avg_df = df.groupby("CVE_ENT")[list(numeric_cols)].mean().reset_index()
    # Ordenar el DataFrame por las columnas seleccionadas
    avg_df = avg_df.sort_values(by=sel_cols, ascending=True)
    return avg_df.hvplot.barh(x="CVE_ENT", y=sel_cols, bar_width=0.9, height=800,
                            ylabel='').opts(active_tools=[],tools=['pan'])
    
#@pn.cache(max_items=32, policy='LRU')
#def create_corr_heatmap(v):
#    # Filtrar el DataFrame para incluir solo las columnas especificadas en vars
#    filtered_df = df[v]
#    df_corr = filtered_df.corr(numeric_only=True)
#    return df_corr.hvplot.heatmap(cmap="Blues", rot=45, height=500).opts(active_tools=[])

@pn.cache(max_items=32, policy='LRU')
def create_map(v):
    # Filtrar el DataFrame para incluir solo las columnas especificadas en vars
    map = px.choropleth_mapbox(
        data_frame = df.set_index("CVEGEO"), # Usar el ID como índice de los datos
        geojson = gdf.geometry,                 # La geometría
        locations = gdf.index,                  # El índice de los datos
        color = v,
        # Estética
        color_continuous_scale="Viridis",
        opacity=0.5,
        mapbox_style = 'open-street-map',
        center = {"lat": 23.4346697, "lon": -100.8707838},
        zoom = 3
    )
    map.update_geos(fitbounds="locations", visible=False)
    return map

##################### WIDGETS & CALLBACK ###############
# SIDE-BAR BUTTONS
# https://tabler-icons.io/
button1 = pn.widgets.Button(name="Introduction", button_type="warning", icon="file-info", styles={"width": "100%"})
button2 = pn.widgets.Button(name="Dataset", button_type="warning", icon="clipboard-data", styles={"width": "100%"})
button3 = pn.widgets.Button(name="Distributions", button_type="warning", icon="chart-histogram", styles={"width": "100%"})
button4 = pn.widgets.Button(name="Relationship", button_type="warning", icon="chart-dots-filled", styles={"width": "100%"})
button5 = pn.widgets.Button(name="Avg Features", button_type="warning", icon="chart-bar", styles={"width": "100%"})
button6 = pn.widgets.Button(name="Correlation", button_type="warning", icon="chart-treemap", styles={"width": "100%"})

# Widgets kdensity
dist_mean = pn.widgets.RadioButtonGroup(name="Variables", options=vars_mean, value="TRI Mean", button_type='primary',button_style='outline')
dist_stde = pn.widgets.RadioButtonGroup(name="Variables", options=vars_stde, value="TRI Sd", button_type='success',button_style='outline')
dist_max = pn.widgets.RadioButtonGroup(name="Variables", options=vars_max, value="TRI Max", button_type='light',button_style='outline')

# Widgets MultiSelect (usado en bar y heat)
multi_select = pn.widgets.MultiSelect(name="Variables", options=vars, value=["TRI Mean","VRM Mean"])

# Widgets Ejes de gráficos (usado en scatter matrix)
x_axis = pn.widgets.Select(name="X-Axis", options=vars_mean, value="TRI Mean")
y_axis = pn.widgets.Select(name="Y-Axis", options=vars_mean, value="VRM Mean")

############# DESPLAZAMIENTO ENTRE PÁGINAS ###################
def show_page(page_key):
    main_area.clear()
    main_area.append(mapping[page_key])

button1.on_click(lambda event: show_page("Page1"))
button2.on_click(lambda event: show_page("Page2"))
button3.on_click(lambda event: show_page("Page3"))
button4.on_click(lambda event: show_page("Page4"))
button5.on_click(lambda event: show_page("Page5"))
button6.on_click(lambda event: show_page("Page6"))

############################ CREATE PAGE LAYOUT ##################################
def CreatePage1():
    return pn.Column(pn.pane.Markdown("""
        ## Measures of topographic heterogeneity:
        Topographic heterogeneity can be described as the variability **elevation** values within an area. It can be measured using summastatistics, such as the standard deviation, or specific indicexpressing the rate of elevational change in response to changes location.
        Four indices to express topographic heterogeneity:
        - Terrain Ruggedness Index (TRI)
        - Topographic Position Index (TPI)
        - Roughness
        - Vector Ruggedness Measure (VRM)
        
        ### Terrain Ruggedness Index
        Is the mean of the absolute differences in elevation between a focal cell and its 8 surrounding cells. It quantifies the total elevation change across the 3x3 cells. Flat areas have a value of zero whereas mountain areas with steep ridges have positive values, which can be greater than 2000m in the Himalaya area.
        
        ### Topographic Position Index
        Is the difference between the elevation of a focal cell and the mean of its 8 surrounding cells. Positive and negative values correspond to ridges and valleys, respectively, while zero values correspond generally to flat areas (with the exception of a special case where a focal cell with a value 5 can have surrounding cells with values of 4x1 and 4x9, resulting in a TPI of 0.
        
        ### Roughness
        Is expressed as the largest inter-cell difference of a focal cell and its 8 surrounding cells.
        
        ### Vector Ruggedness Measure
        Quantifies terrain ruggedness by measuring the dispersion of vectors orthogonal to the terrain surface. Slope and aspect are decomposed into 3-dimensional vector components (in the x, y, and z directions) using standard trigonometric operators, and by calculating the resultant vector magnitude within a user-specified moving window size (in this study 3x3). The VRM quantifies local variation of slope in the terrain more independently than the TPI and TRI methods30. VRM values range from 0-1 in flat and rugged regions, respectively.
        """,
        styles={'font-size': '14pt'}),
        pn.pane.Image("topografia.png",width=700)
        ,
        width=700,
        align="start")

def CreatePage2(df):
    return pn.Column(
        pn.pane.Markdown("## Dataset Example"),
        pn.pane.DataFrame(df_page, width=700),
        pn.pane.Markdown("## Summaty Stats"),
        pn.pane.DataFrame(df, height=450),
        align="start",
    )

def CreatePage3():
    return pn.Column(
        pn.pane.Markdown("## Explore Distribution of Measures"),
        dist_mean,
        pn.bind(create_kde, dist_mean),
        dist_stde,
        pn.bind(create_kde, dist_stde),
        dist_max,
        pn.bind(create_kde, dist_max),
        align="start",
    )

def CreatePage4():
    return pn.Column(
        pn.pane.Markdown("## Explore Relationship Between Measures"),
        pn.Row(x_axis, y_axis),
        pn.bind(create_scatter_chart, x_axis, y_axis),
        align="start",
    )

def CreatePage5():
    return pn.Column(
        pn.pane.Markdown("## Explore Avg Values of Measures per EF"),
        dist_mean,
        pn.bind(create_bar_chart, dist_mean),
        align="start",
    )

def CreatePage6():
    return pn.Column(
        pn.pane.Markdown("## Map"),
        dist_mean,
        pn.bind(create_map, dist_mean),
        align="start",
    )

mapping = {
    "Page1": CreatePage1(),
    "Page2": CreatePage2(t_summ[5:][['mean', 'std', 'min', 'max']]),
    "Page3": CreatePage3(),
    "Page4": CreatePage4(),
    "Page5": CreatePage5(),
    "Page6": CreatePage6(),
}

#################### SIDEBAR LAYOUT ##########################
sidebar = pn.Column(pn.pane.Markdown("## Pages", align="center"), button1, button2, button3, button4, button5, button6, styles={"width": "100%", "padding": "15px"})

#################### MAIN AREA LAYOUT ##########################
main_area = pn.Column(mapping["Page1"], styles={"width":"100%"})

###################### APP LAYOUT ##############################
template = pn.template.BootstrapTemplate(
    title="Dashboard Topography",
    sidebar=[sidebar],
    main=[main_area],
    header_background="black", 
    site="Santiago Cerutti", theme=pn.template.DarkTheme,
    sidebar_width=200, ## Default is 330
    busy_indicator=None,
)

# Serve the Panel app
template.servable()