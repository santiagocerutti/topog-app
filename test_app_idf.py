import panel as pn
import pandas as pd
import hvplot.pandas
import os
import re
import warnings
warnings.filterwarnings("ignore")

print("Starting application...")

########################### LOAD DATASET ##################
df = pd.read_csv(os.path.join('Municipalities_with_topo.csv'))
df = df.iloc[:,3:]


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
df_page = df.head()

# Variables para los widgets
numeric_cols = df.iloc[:,3:].columns
vars = list(descriptions.values())[6:]
vars_mean = [descriptions[col] for col in descriptions if col.endswith('_mean')]
vars_stde = [descriptions[col] for col in descriptions if col.endswith('_stde')]
vars_max = [descriptions[col] for col in descriptions if col.endswith('_max')]

idf = df.interactive()

################################# CREATE TABLES ############################
t_summ = df_page.describe().T

print("Dataset loaded successfully")
################################# CREATE CHARTS ############################
def create_kde(sel_var):
    return idf.hvplot(kind="kde", y=sel_var, alpha=0.5).opts(active_tools=[])

def create_scatter_chart(x_axis, y_axis):
    return df.hvplot.scatter(x=x_axis, y=y_axis, color="CVE_ENT",
                                size=100, alpha=0.9, height=400).opts(active_tools=[])

def create_bar_chart(sel_cols):
    avg_df = df.groupby("CVE_ENT")[list(numeric_cols)].mean().reset_index()
    return avg_df.hvplot.bar(x="CVE_ENT", y=sel_cols, bar_width=0.8,
                            rot=45, height=400,
                            ylabel='').opts(active_tools=[])

def create_corr_heatmap(v):
    # Filtrar el DataFrame para incluir solo las columnas especificadas en vars
    filtered_df = df[v]
    df_corr = filtered_df.corr(numeric_only=True)
    return df_corr.hvplot.heatmap(cmap="Blues", rot=45, height=500).opts(active_tools=[])

############################# WIDGETS & CALLBACK ###################################
# SIDE-BAR BUTTONS
# https://tabler-icons.io/
button1 = pn.widgets.Button(name="Introduction", button_type="warning", icon="file-info", styles={"width": "100%"})
button2 = pn.widgets.Button(name="Dataset", button_type="warning", icon="clipboard-data", styles={"width": "100%"})
button3 = pn.widgets.Button(name="Distributions", button_type="warning", icon="chart-histogram", styles={"width": "100%"})
button4 = pn.widgets.Button(name="Relationship", button_type="warning", icon="chart-dots-filled", styles={"width": "100%"})
button5 = pn.widgets.Button(name="Avg Features", button_type="warning", icon="chart-bar", styles={"width": "100%"})
button6 = pn.widgets.Button(name="Correlation", button_type="warning", icon="chart-treemap", styles={"width": "100%"})


# Widgets kdensity
dist_mean = pn.widgets.Select(name="Variables", options=vars_mean, value="TRI Mean")
dist_stde = pn.widgets.Select(name="Variables", options=vars_stde, value="TRI Sd")
dist_max = pn.widgets.Select(name="Variables", options=vars_max, value="TRI Max")

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
    return pn.Column(pn.pane.Markdown("# HOLA", width=550),
                    align="center")

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
        pn.pane.Markdown("## Explore Distribution of Variables"),
        idf.widgets(),
        pn.bind(create_kde, dist_mean),
        dist_stde,
        pn.bind(create_kde, dist_stde),
        dist_max,
        pn.bind(create_kde, dist_stde),
        align="center",
    )

def CreatePage4():
    return pn.Column(
        pn.pane.Markdown("## Explore Relationship Between Variables"),
        pn.Row(x_axis, y_axis),
        pn.bind(create_scatter_chart, x_axis, y_axis),
        align="center",
    )

def CreatePage5():
    return pn.Column(
        pn.pane.Markdown("## Explore Avg Values of Features per EF"),
        multi_select,
        pn.bind(create_bar_chart, multi_select),
        align="center",
    )

def CreatePage6():
    return pn.Column(
        pn.pane.Markdown("## Variable Correlation Heatmap"),
        multi_select,
        pn.bind(create_corr_heatmap, multi_select),
        align="center",
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
sidebar = pn.Column(pn.pane.Markdown("## Pages"), button1, button2, button3, button4, button5, button6, styles={"width": "100%", "padding": "15px"})

#################### MAIN AREA LAYOUT ##########################
main_area = pn.Column(mapping["Page1"], styles={"width":"100%"})

###################### APP LAYOUT ##############################
template = pn.template.BootstrapTemplate(
    title="Dashboard Topography",
    sidebar=[sidebar],
    main=[main_area],
    header_background="black", 
    site="Santiago Cerutti", logo=os.path.join("python.png"), theme=pn.template.DarkTheme,
    sidebar_width=250, ## Default is 330
    busy_indicator=None,
)

# Serve the Panel app
template.servable()