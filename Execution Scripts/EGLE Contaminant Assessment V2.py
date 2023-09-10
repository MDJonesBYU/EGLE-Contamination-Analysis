#!/usr/bin/env python
# coding: utf-8

# In[428]:


#####################################################################################
#------------Notice of Invention, Copyright, and Terms of Use-----------------------#
#                                                                                   #
#   This tool ranks prioritization of site remediation actions for facilities       #
#   subject to Parts 201 and/or Parts 2013 Based on the proximity to sensitive      #
#   communities and at-risk populations. It is developed using publicly availably   #
#   datasets, provided through Michigan's Environmental, Great Lakes, and Energy    #
#   (EGLE) and integrates querying using geodata sources including geopandas        #
#   Originally developed in python.                                                 #
#                                                                                   # 
#   Acceptable Use Resistrictions: Free for educational or non-profit use           #
#                                  Pay-per-use required for commerical use          #
#                                  Commerical use forbidden without written consent #
#                                                                                   #
#   For Attribution in research, publications, etc, cite the developer below:       #
#                                                                                   #
#   Developed by Matthew Jones, Data Scientist, UM MADS Program, Copyright 2022     #
#   B.Sc. Chemical Engineering BYU | MS Applied Data Science UMich                  #
#   Contact Information: MJones@Envirolytica.com,                                   #
#   LinkedIn: https://www.linkedin.com/in/jonesmatthewdavid/                        #
#                                                                                   #
#####################################################################################
#
#
#
#####################################################################################
#----------------------------------Control Log--------------------------------------#
#                                                                                   #
#   Version 1.0  Released Dec. 2022 by M. Jones, Submitted to EGLE                  #
#   Version 2.0  Released Sept. 2023 by M. Jones, Submitted to EGLE
#                                                                                   #
#                                                                                   #
#----------------------------------Control Log--------------------------------------#

#####################################################################################
#--------------------Datasources used for this Analysis-----------------------------#
#Main Datasource: 
#0) Mi Datahub: https://gis-michigan.opendata.arcgis.com/search?collection=Dataset&q=Public%20Health
#1) Mi List of Healthcare Places: 
#----https://gis-michigan.opendata.arcgis.com/datasets/Michigan::health-care-1/explore?location=42.964147%2C-85.033721%2C9.82
#2) Mi List of Wellhead Protection Areas:
#----https://gis-michigan.opendata.arcgis.com/datasets/egle::wellhead-protection-areas/explore?location=42.627007%2C-84.186577%2C8.78
#3) Mi List of WSSN County and Pop Served 
#----https://www.midrinkingwater.org/find_your_public_water_type
#4) Mi List of Schools across the state (Does not show school pop size, requires finess to get new table)
#----https://michigan.maps.arcgis.com/apps/webappviewer/index.html?id=438dc453faf749d786e0c6e8be731cfd
#5) Mi List of Contam Sites: 
#----https://www.egle.state.mi.us/RIDE/inventory-of-facilities/facilities
# Well head Locations: 
#6) UP Wells 
#----https://gis-michigan.opendata.arcgis.com/datasets/egle::water-wells-upper-peninsula/explore?location=46.108409%2C-85.243453%2C12.30&showTable=true
#7) LP Wells --SE Michigan
#----https://gis-michigan.opendata.arcgis.com/datasets/egle::water-wells-south-central-southeastern-michigan/explore?location=44.837291%2C-86.135708%2C7.17
#8  LP Wells --E Michigan
#----https://gis-michigan.opendata.arcgis.com/datasets/egle::water-wells-east-central-lower-peninsula/explore?location=44.753902%2C-86.135708%2C7.00
#9  LP Wells --WC Michigan
#----https://gis-michigan.opendata.arcgis.com/datasets/egle::water-wells-west-central-lower-peninsula/explore?location=44.753902%2C-86.135708%2C7.00
#10  LP Wells -- N Michigan
#----https://gis-michigan.opendata.arcgis.com/datasets/egle::water-wells-northern-lower-peninsula/explore
#11 LP Wells SW Michigan 
#----https://gis-michigan.opendata.arcgis.com/datasets/egle::water-wells-southwest-michigan/explore?location=44.868358%2C-86.135708%2C7.64
#                                                                                     #
#                                                                                     #
#######################################################################################
#----------------------------------------------Beginning of Code----------------------#
#--------STEP 1: Import required Packages and set Cut Offs: ---------------------------
#This one will load in the FOIA data and merge. 
import pandas as pd, numpy as np, math, time, datetime as dt, geopandas as gpd, matplotlib.pyplot as plt, collections
from datetime import datetime
from shapely.geometry import Point
from shapely.geometry import Polygon


start = time.time()
today = datetime.now()
cutoff_date = today.replace(year = today.year - 50) #Future could ask user to define desired age/lookup time
retain_depth = 80 #feet
well_type = ["IRRI", "TY1PU", "TY2PU", "TY3PU", 'HOSHLD']
well_status = ["ACT", "UNK", "OTH"]


#--------STEP 2: Load Master Datafiles: ---------------------------------------------------------
df_contam  = pd.read_csv('Master_contam.csv')
df_schools = pd.read_csv('Master_Schools.csv')
df_HC      = pd.read_csv('Master_Health_Care.csv')
df_WW_ELP  = pd.read_csv('Water_Wells_-_East_Central_Lower_Peninsula.csv')
df_WW_NLP  = pd.read_csv('Water_Wells_-_Northern_Lower_Peninsula.csv')
df_WW_SCLP = pd.read_csv('Water_Wells_-_South_Central_%26_Southeastern_Michigan.csv')
df_WW_SWLP = pd.read_csv('Water_Wells_-_Southwest_Michigan.csv')
df_WW_UP   = pd.read_csv('Water_Wells_-_Upper_Peninsula_Master.csv')
df_WW_WCLP = pd.read_csv('Water_Wells_-_West_Central_Lower_Peninsula.csv')
df_WW_pop  = pd.read_excel('Wellhead Pop Served.xlsx')
df_WHPA = gpd.GeoDataFrame.from_file('Wellhead_Protection_Areas.shp')
df_WHPA_LL = pd.read_csv('WHPA_point_table.csv')


read_time = time.time() - start
print('time to load input data ', read_time, "s")
start = time.time()


#--------STEP 3: Confirmation Check that all wellhead datafiles have same column structure, Exiting Script if not 
columns = list(map(lambda x: list(x.columns), [df_WW_ELP,df_WW_NLP, df_WW_SCLP, df_WW_SWLP, df_WW_UP,df_WW_WCLP]))
data = pd.DataFrame(columns).fillna("").drop_duplicates(keep="first")
if len(data) > 1:
    raise Exception ("""............................
    WARNING! Well Data have different columns. Current Script Will Require Modification(s)
    .......................
    Exiting Script""")
else:  
    well_df = pd.concat([df_WW_ELP,df_WW_NLP, df_WW_SCLP, df_WW_SWLP, df_WW_UP,df_WW_WCLP])
    
    
#--------STEP 4: Clean raw data files ---------------------------------------------------------------
cols = ['Township', 'Latitude', 'Longitude', 'Facility Name', 'Project Manager', 'EGLE District', 'Full Address', 
        'Risk Condition', 'Release Status', 'County', 'Senate District' , 'House District','U.S. Congressional District',
       'EPA ID','LUST Name', 'City']
df_contam = df_contam[df_contam['Release Status'] != "\tClosed"].assign(
    **{col: df_contam[col].str.lstrip('\t').str.rstrip(' ') for col in cols}).astype(
    {'Latitude': 'float64', 'Longitude': 'float64'})

dict_map = pd.Series(df_contam['EGLE District'].values,index=df_contam['County']).to_dict() #Dict of County: EGLE Dist. 
df_HC = df_HC.assign(
    County=df_HC['County'].astype(str).apply(lambda x: x.lstrip('\n').lstrip(' ')),
    **{        'EGLE District': df_HC['County'].map(dict_map),
        'StreetAddress_Used': df_HC['StreetAddress'] + ", " + df_HC['City'] + ", " + df_HC['State']})


df_schools = df_schools.assign(
    **{'EGLE District': df_schools['COUNTY'].map(dict_map),
       'Address_Used': df_schools['STREET'] + ", " + df_schools['CITY'] + ", " + df_schools['STATE']})


well_df = (well_df.merge(
    df_WW_pop.assign(WSSN=df_WW_pop['Water Supply Serial Number'].astype('float64')), on='WSSN', how='left')
    .assign(
        CONST_DATE=lambda x: pd.to_datetime(x['CONST_DATE'].fillna('1900-01-01').str.split(' ').str[0], format='mixed')
    )
)

well_df['EGLE District'] = well_df['COUNTY'].map(dict_map)  # Set the EGLE District for Wells
well_df = well_df.loc[
    lambda x: x['WELL_TYPE'].isin(well_type) &
               x['WEL_STATUS'].isin(well_status) &
               (x['WELL_DEPTH'] <= retain_depth) &
               (x['CONST_DATE'] <= cutoff_date)
]

end = time.time()
print("time to apply initial cleaning", end-start, "s")

start = time.time()
#--------STEP 5 Read FOIA contaminant Data from FOIA and characterize contaminant by business, prep for merge--------: 
df_contam_2 = pd.read_csv("FOIA_Contam_list.csv")
unique_contaminants = set(df_contam_2["Contaminant Class"])
df_contam_2["Contaminant ID"] = df_contam_2["Contaminant Class"].map(contaminants_id)
df_contam_2["Contaminant Class"] = df_contam_2["Contaminant Class"].fillna('not specified')#, inplace=True)
#Add the contam ID to the Dataframe: 
df_contam_2["loc_class"] = df_contam_2["Location ID"].astype(str) + df_contam_2["Contaminant Class"]
df_contam_2 = df_contam_2.groupby("Location ID").agg({"Location ID": "first", "Location Name":"first", "Address": "first", "City": "first", "Zip": "first", "Latitude": "first", "Longitude":"first","Business Type": "first","Contaminant Class": "first", "loc_class":"first", "Contaminant ID": lambda x: list(x)})
df_contam_2 = df_contam_2.loc[:, df_contam_2.columns != "loc_class"]

def count_elements(row):
    return len(row)
df_contam_2["Contaminant Qty"] = df_contam_2['Contaminant ID'].apply(count_elements)
df_contam_2 = df_contam_2.reset_index(drop=True)
df_contam_2

#Now Weight the Contaminants Present for each site from the FOIA: 
def weighting_work(column):
    weighting_list = []
    count_nan =0
    for i in range(len(column)):
        if len(column[i]) == 1 and (column[i] == 8 or column[i] == 16):
            count_nan +=1
            group_1 = 0
            group_2 = 0 
            group_3 = 0
        else:
            count_0 = column[i].count(0)
            count_1 = column[i].count(1)
            count_2 = column[i].count(2)
            count_3 = column[i].count(3)
            count_4 = column[i].count(4)
            count_5 = column[i].count(5)
            count_6 = column[i].count(6)
            count_7 = column[i].count(7)
            count_8 = column[i].count(8)
            count_9 = column[i].count(9)
            count_10 = column[i].count(10)
            count_11 = column[i].count(11)
            count_12 = column[i].count(12)
            count_13 = column[i].count(13)    
            count_14 = column[i].count(14)
            count_15 = column[i].count(15)
            count_16 = column[i].count(16)
            count_17 = column[i].count(17)
            group_1 = count_16 + count_6 #Chlorinated VOCs and Pesticies
            group_2 = count_17 + count_13 + count_8 #PFAS, PBB, PCB, 
            group_3 = count_11 + count_12  #Petrol, Hydrocarbons
            group_4 = count_1 + count_2 + count_3 + count_4 + count_15 #Lead, Mercury, Metals, Dioxins, PAHs
            group_5 = count_5 + count_7 + count_9 + count_10+count_14  # Methane, Water Quality, PH, Not Classified 
            group_6 = count_0 #Not listed
        weighting = group_1 + group_2 / 2 + group_3 / 3 + group_4/4 + group_5/5 +group_6/6 
        weighting_list.append(weighting)

    max_haz = max(weighting_list)
    min_haz = min(weighting_list)
    weighting_list = [int(((haz - min_haz)/(max_haz-min_haz))*100) for haz in weighting_list]
    return(weighting_list)

hazard_column = weighting_work(df_contam_2["Contaminant ID"])
df_contam_2["contaminant hazard"] = hazard_column

#Now Need to Assign the Industry Expected Hazard  based on business type: 
filter_df = df_contam_2.dropna().loc[df_contam_2['Contaminant Class'] != 'not specified']
contaminant_counts = (filter_df.groupby('Business Type')['Contaminant Class']
                      .value_counts().groupby(level=0).head(1)
                      .reset_index(name='count')
                      .sort_values(by=['count'], ascending=[False]))
df_contam_2['Business Chemical'] = contaminant_counts['Contaminant Class'].map(contaminants_id)
df_contam_2['Business Chemical'] = df_contam_2['Business Chemical'].fillna(0)
df_contam_2['Business Chemical'] = df_contam_2['Business Chemical'].astype(int)
df_contam_2['Business Chemical'] = df_contam_2['Business Chemical'].apply(lambda x: [x])# 
df_contam_2['Business Risk']  = weighting_work(df_contam_2['Business Chemical'])

business_weight = 0.5
contaminant_weight = 0.5
df_contam_2['Biz_chem_Risk'] = business_weight*df_contam_2['Business Risk']+contaminant_weight*df_contam_2['contaminant hazard']
max_total_risk = df_contam_2['Biz_chem_Risk'].max()
min_total_risk = df_contam_2['Biz_chem_Risk'].min()

df_contam_2['Biz_chem_Risk'] = (df_contam_2['Biz_chem_Risk'] - min_total_risk) / (max_total_risk - min_total_risk)*100
df_contam_2['Biz_chem_Risk'] = df_contam_2['Biz_chem_Risk'].astype(int)
df_contam_2["detailed address"] = df_contam_2["Address"] + ", " + df_contam_2["City"] + ", MI " + df_contam_2["Zip"]

#--------STEP 6: Merge and clean the Contamination sets for Vectorized Analysis-------- 
contam_df_total = df_contam.merge(df_contam_2, how='outer', left_on='Facility ID', right_on='Location ID')
contam_df_total['Latitude'] = np.where(contam_df_total['Latitude_x'].notna(), 
                                       contam_df_total['Latitude_x'], contam_df_total['Latitude_y'])
contam_df_total['Longitude'] = np.where(contam_df_total['Longitude_x'].notna(), 
                                        contam_df_total['Longitude_x'], contam_df_total['Longitude_y'])
contam_df_total['City'] = np.where(contam_df_total['City_x'].notna(), 
                                   contam_df_total['City_x'], contam_df_total['City_y'])
contam_df_total = contam_df_total.dropna(
    subset=['Latitude', 'Longitude']).loc[contam_df_total['Risk Condition'] != 'Risk Controlled'].drop(
    columns=['Latitude_x', 'Latitude_y', 'City_x', 'City_y', 'Longitude_x', 'Longitude_y', "U.S. Congressional District",
            "House District", "Senate District"])

contam_df_total.fillna({'Facility Name': contam_df_total['Location Name'],
                         'Full Address': contam_df_total['detailed address'],
                         'Facility ID': contam_df_total['Location ID'],
                         'Risk Condition': 'Risks Not Determined',
                         'Project Manager': 'Unknown',
                         'Release Status': 'Unknown'}, inplace=True)
contam_df_total = contam_df_total[contam_df_total['Release Status'].str.upper() != 'CLOSED']

contam_df_total.reset_index(drop=True, inplace=True)

end = time.time()
print("time to add FOIA contaminants and merge datasets", end-start, "s")


start = time.time()
#--------STEP 7: Repeat Chemical Assessment on Remaining Columns: --------
contam_df_total.head(10)
#Now re-assign the business risk for all rows where the business risk is missing.....
#set(contam_df_total['contaminant hazard'])
hazard_column = weighting_work(contam_df_total["Contaminant ID"])
contam_df_total["contaminant hazard"] = hazard_column

#Now Need to Assign the Industry Expected Hazard  based on business type: 
filter_df = contam_df_total.dropna().loc[contam_df_total['Contaminant Class'] != 'not specified']
contaminant_counts = (filter_df.groupby('Business Type')['Contaminant Class']
                      .value_counts().groupby(level=0).head(1)
                      .reset_index(name='count')
                      .sort_values(by=['count'], ascending=[False]))
contam_df_total['Business Chemical'] = contaminant_counts['Contaminant Class'].map(contaminants_id)
contam_df_total['Business Chemical'] = contam_df_total['Business Chemical'].fillna(0)
contam_df_total['Business Chemical'] = contam_df_total['Business Chemical'].astype(int)
contam_df_total['Business Chemical'] = contam_df_total['Business Chemical'].apply(lambda x: [x])# 
contam_df_total['Business Risk']  = weighting_work(contam_df_total['Business Chemical'])

business_weight = 0.5
contaminant_weight = 0.5
contam_df_total['Biz_chem_Risk'] = business_weight*contam_df_total['Business Risk']+contaminant_weight*contam_df_total['contaminant hazard']
max_total_risk = contam_df_total['Biz_chem_Risk'].max()
min_total_risk = contam_df_total['Biz_chem_Risk'].min()

contam_df_total['Biz_chem_Risk'] = (contam_df_total['Biz_chem_Risk'] - min_total_risk) / (max_total_risk - min_total_risk)*200
contam_df_total['Biz_chem_Risk'] = contam_df_total['Biz_chem_Risk'].astype(int)
contam_df_total["detailed address"] = contam_df_total["Address"] + ", " + contam_df_total["City"] + ", MI " + contam_df_total["Zip"]
contam_df_total['Risk Condition'].fillna('Risks Not Determined', inplace=True)
end = time.time()
print("time to characterize chemical risk and business risk for all facilities", end-start, "s")


#--------STEP 8: Identify if the Contam Site is within a Wellhead protection area (Vectorized) ---------------------
start = time.time()
contam_df_total.reset_index(drop=True, inplace=True)
contam_coords = tuple(zip(contam_df_total['Longitude'],contam_df_total['Latitude'])) #tuple of Lat/Long for each contam site
WHPA_poly_list ,in_WHPA, point_list = ([] for i in range(3))
WHPA = df_WHPA['geometry'] #Lat/Long Coords of each WHPA polygon
WHPA_poly_array = np.array(WHPA)
contam_coords_array = np.array([Point(coord) for coord in contam_coords])
contains_matrix = np.array([poly.contains(point) for poly in WHPA_poly_array for point in contam_coords_array])
contains_matrix = contains_matrix.reshape(len(WHPA_poly_array), len(contam_coords_array))
is_in_WHPA = np.any(contains_matrix, axis=0)
in_WHPA = np.where(is_in_WHPA, "in WHPA", "Not in WHPA")
contam_df_total['IN_WHPA'] = in_WHPA.tolist()
end = time.time()
print((end-start)/60, "min to map which Contam Sites are in WHPAs")

well_df, contam_df_total, df_schools, df_HC, df_WHPA, df_WHPA_LL = [
    df.reset_index(drop=True) for df in [well_df, contam_df_total, df_schools, df_HC, df_WHPA, df_WHPA_LL]]


start = time.time()
#--------STEP 9: Determine District If Not Already Specified district--------------------------------------
contam_df_total

geojson_file_path = 'Counties_(v17a).geojson'
gdf = gpd.read_file(geojson_file_path)

#Check if 
contam_coords = tuple(zip(contam_df_total['Longitude'],contam_df_total['Latitude'])) #tuple of Lat/Long for each contam site
county_polygons = gdf['geometry'] #Lat/Long Coords of each WHPA polygon
county_polygons_list = []
county_list = []
point_list = [] 
for i in range(len(county_polygons)):
    county_polygons_list.append(county_polygons[i]) #set list of individual polygons
for i in range(len(contam_coords)):
    point_list.append(Point(contam_coords[i])) #set list of individual contam coords to check

#Now Check if the contam site is in the polygon.
for j in range(len(point_list)):
    point_covered = False
    for i in range(len(county_polygons_list)):
        if county_polygons_list[i].covers(point_list[j]):
            county_list.append(gdf["NAME"][i])
            point_covered = True
            break
    
    if not point_covered:
        county_list.append(0)
contam_df_total["County"] = county_list

filtered_df = contam_df_total[contam_df_total['EGLE District'] != 0].dropna(subset=['EGLE District', 'County'])
district_to_counties = filtered_df.groupby('EGLE District')['County'].apply(set).to_dict()
county_to_district = {county: district for district, counties in district_to_counties.items() for county in counties}
del county_to_district[0]
contam_df_total['EGLE District'] = contam_df_total['County'].map(county_to_district).fillna(
    contam_df_total['EGLE District'])
contam_df_total['EGLE District'].fillna('to be determined', inplace=True)

end = time.time()
print(end-start, "s to evaluate County")


#-------Step 10: Add in Assessment Risk Factor: 
risk_mapping = {
    'Risks Present and Immediate': 200,
    'Risks Present and Require Action in Short-term': 150,
    'Risks Present and Require Action in Long-term': 100,
    'Risks Not Determined': 100,
    'Risks Controlled-Interim': 50,
    'Residential Closure (under Section 20101(1)(tt))': 0,
    'Contact Lead Division': 100
}

risk_dict = {item: risk_mapping.get(item, 100) for item in set(contam_df_total["Risk Condition"])}
contam_df_total['Assessment Risk'] = contam_df_total['Risk Condition'].map(risk_dict)


#-------STEP 11: Calculate the density of schools, wells, and HC sites in vicinity of the contamination site -----------
#        to our data dictionary
haversine_start = time.time()
def get_proximity(item_number):
    lat1 = contam_df_total['Latitude'][item_number] * (np.pi / 180)
    long1 = contam_df_total['Longitude'][item_number] * (np.pi / 180)

    school_lat = df_schools['LATITUDE'] * (np.pi / 180)
    school_long = df_schools['LONGITUDE'] * (np.pi / 180)
    HC_lat  = df_HC['Latitude']    / (180/np.pi)
    HC_long = df_HC['Longitude']   / (180/np.pi)
    WHPA_lat  = df_WHPA_LL['POINT_Y']    / (180/np.pi) #latitude
    WHPA_long = df_WHPA_LL['POINT_X']   / (180/np.pi) #longitude
    Well_lat   = well_df['LATITUDE'] / (180/np.pi)
    Well_long  = well_df['LONGITUDE'] / (180/np.pi)
    def haversine(lat1, long1, lat2, long2):
        dlat = lat2 - lat1
        dlong = long2 - long1
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlong / 2) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        dist_array = np.sort(3963 * c)  # in miles
        return(dist_array)

    SC_dist_array = haversine(lat1, long1, school_lat, school_long)
    SC_density = np.sum(SC_dist_array <= 1)
    SC_worst = np.min(SC_dist_array)

    HC_dist_array = haversine(lat1, long1, HC_lat, HC_long)
    HC_density = np.sum(HC_dist_array <= 1)
    HC_worst = np.min(HC_dist_array)

    WHPA_dist_array = haversine(lat1, long1, WHPA_lat, WHPA_long)
    WHPA_density = np.sum(WHPA_dist_array <= 1)
    WHPA_worst = np.min(WHPA_dist_array)

    Well_dist_array = haversine(lat1, long1, Well_lat, Well_long)
    Well_density = np.sum(Well_dist_array <= 1)
    Well_worst = np.min(Well_dist_array)
    return (SC_density,SC_worst, HC_density, HC_worst,Well_density,Well_worst, WHPA_density, WHPA_worst)
# Timing

myDict = {}
contam_df_total.reset_index(drop=True, inplace=True) 
for i in range(len(contam_df_total)):
    #print(i)
    proximity = get_proximity(i) 
    #Building the dictionary that will be output as our master file
    myDict[contam_df_total['Facility Name'][i]] = {}
    myDict[contam_df_total['Facility Name'][i]]['site ID'] = contam_df_total['Facility ID'][i]
    myDict[contam_df_total['Facility Name'][i]]['Address'] = contam_df_total['Full Address'][i]
    myDict[contam_df_total['Facility Name'][i]]['County']  = contam_df_total['County'][i]    
    myDict[contam_df_total['Facility Name'][i]]['school Density'] = proximity[0]
    myDict[contam_df_total['Facility Name'][i]]['closest school'] = proximity[1]
    myDict[contam_df_total['Facility Name'][i]]['Medical Density'] = proximity[2]
    myDict[contam_df_total['Facility Name'][i]]['Closest HealthCare'] = proximity[3]
    myDict[contam_df_total['Facility Name'][i]]['Well Density'] = proximity[4]
    myDict[contam_df_total['Facility Name'][i]]['Closest Well'] = proximity[5]  
    myDict[contam_df_total['Facility Name'][i]]['WHPA Density'] = proximity[6]
    myDict[contam_df_total['Facility Name'][i]]['Closest WHPA'] = proximity[7] 
    myDict[contam_df_total['Facility Name'][i]]['Contam Lat'] = contam_df_total['Latitude'][i]
    myDict[contam_df_total['Facility Name'][i]]['Contam Long']=contam_df_total['Longitude'][i]
    myDict[contam_df_total['Facility Name'][i]]['in WHPA']=contam_df_total['IN_WHPA'][i]
haversine_end = time.time()
proximity_time = haversine_end - haversine_start
print("Time to run Proximity Calculations: ",proximity_time/60, " minutes" )


#---------STEP 11: Load Env Justice Data--------------: 
start = time.time()
geojson_file_path = 'MiEJScreen_Draft_Data.geojson'
gdf = gpd.read_file(geojson_file_path)

#Check if 
contam_coords = tuple(zip(contam_df_total['Longitude'],contam_df_total['Latitude'])) #tuple of Lat/Long for each contam site
EJS_polygons = gdf['geometry'] #Lat/Long Coords of each WHPA polygon
EJS_polygons_list = []
MiEJScore_list = []
point_list = [] 
for i in range(len(EJS_polygons)):
    EJS_polygons_list.append(EJS_polygons[i]) #set list of individual polygons
for i in range(len(contam_coords)):
    point_list.append(Point(contam_coords[i])) #set list of individual contam coords to check

#Now Check if the contam site is in the polygon.
for j in range(len(point_list)):
    point_covered = False
    for i in range(len(EJS_polygons_list)):
        if EJS_polygons_list[i].covers(point_list[j]):
            MiEJScore_list.append(gdf["MiEJScreenOverallScore"][i])
            point_covered = True
            break
    
    if not point_covered:
        MiEJScore_list.append(0)
contam_df_total["EJS Sore"] = MiEJScore_list
end = time.time()
print(end-start, "s to evaluate Environmental Justics Score")


#--------STEP 12: Calculate the Total Risk based on proximity to wells, schools, and healthcare ------------------
start = time.time()
max_sc, max_hc, max_well, max_WH, far_sc, far_hc, far_well, far_WH   = [0,0,0,0,0,0,0,0]
close_sc, close_hc, close_well, close_WH = [1000,1000,1000,1000]
#First iteration: capture max density of schools, hospital, and wells. 
for i in (myDict): 
    if myDict[i]['school Density'] > max_sc: 
        max_sc = myDict[i]['school Density']
    if myDict[i]['Medical Density'] > max_hc:
        max_hc = myDict[i]['Medical Density']    
    if myDict[i]['Well Density'] > max_well:
        max_well = myDict[i]['Well Density']
    if myDict[i]['WHPA Density'] > max_WH:
        max_WH = myDict[i]['WHPA Density']

    if myDict[i]['closest school'] > far_sc: 
        far_sc = myDict[i]['closest school']
    if myDict[i]['Closest HealthCare'] > far_hc:
        far_hc = myDict[i]['Closest HealthCare']    
    if myDict[i]['Closest Well'] > far_well:
        far_well = myDict[i]['Closest Well'] 
    if myDict[i]['Closest WHPA'] > far_WH:
        far_WH = myDict[i]['Closest WHPA']

    if myDict[i]['closest school'] < close_sc: 
        close_sc = myDict[i]['closest school']
    if myDict[i]['Closest HealthCare'] < close_hc:
        close_sc = myDict[i]['Closest HealthCare']    
    if myDict[i]['Closest Well'] < close_well:
        close_well = myDict[i]['Closest Well'] 
    if myDict[i]['Closest WHPA'] < close_WH:
        close_WH = myDict[i]['Closest WHPA']
        
        
#Second iteration: assign Risk Weighting based on quantity of sensitive area basis.         
for i in (myDict):
    SCD = myDict[i]['school Density']
    SCC = myDict[i]['closest school']
    sc_risk = SCD / max_sc + (1-SCC/far_sc)
    myDict[i]['School Risk'] = sc_risk * 100

    HCD = myDict[i]['Medical Density']
    HCC = myDict[i]['Closest HealthCare']
    hc_risk = HCD / max_hc + (1-HCC/far_hc)
    myDict[i]['Healthcare Risk'] = hc_risk * 100

    if myDict[i]['in WHPA'] == "in WHPA":
        well_risk = 2
        myDict[i]['Well Risk'] = well_risk * 100
    else: 
        WCD = myDict[i]['Well Density']
        WCC = myDict[i]['Closest Well']
        well_risk = WCD / max_well + (1-WCC/far_well)
        myDict[i]['Well Risk'] = well_risk * 100
        
    #ADD BUSINESS CHEMICAL RISK
    myDict[i]['Business Chemical Risk'] = contam_df_total.loc[contam_df_total['Facility ID'] == myDict[i]['site ID'],
                                                              'Biz_chem_Risk'].iloc[0]
    
    myDict[i]['EJS Risk'] = contam_df_total.loc[contam_df_total['Facility ID'] == myDict[i]['site ID'],
                                                              'EJS Sore'].iloc[0]
    
    myDict[i]['Assessment Risk'] = contam_df_total.loc[contam_df_total['Facility ID'] == myDict[i]['site ID'],
                                                              'Assessment Risk'].iloc[0]
    bc_risk = myDict[i]['Business Chemical Risk']
    EJS_risk = myDict[i]['EJS Risk']
    a_risk = myDict[i]['Assessment Risk']
    total_risk = (sc_risk + hc_risk + well_risk + bc_risk + EJS_risk*2 + a_risk)
    myDict[i]['Total Risk'] = total_risk
    myDict[i]['Contaminated Site Name'] = i
end = time.time()

print(end-start, "s time to Evaluate Total Risk")


#--------STEP 13 load in additional query items for Visualization----------------------------------------
for i in range(len(contam_df_total)):
    #myDict[Contam_FNM[i]]['Contam Long']=Contam_Long[i]
    myDict[contam_df_total['Facility Name'][i]]['EGLE Manager'] = contam_df_total['Project Manager'][i]
    myDict[contam_df_total['Facility Name'][i]][' District'] = contam_df_total['EGLE District'][i]
    myDict[contam_df_total['Facility Name'][i]]['Risk'] = contam_df_total['Risk Condition'][i]
    myDict[contam_df_total['Facility Name'][i]]['Release Status'] = contam_df_total['Release Status'][i]
    myDict[contam_df_total['Facility Name'][i]]['Regulatory Program'] = contam_df_total['Regulatory Program'][i]

    
start = time.time()
#--------STEP 14: Assign Ranking based on importance by district--------------------------------------
#Rank by priority for each district --> ~10s Execution time
df_ranking = pd.DataFrame(data=myDict).T
df_ranking['Rank_set'] = df_ranking['Total Risk'].rank(ascending=False) #Rank low value = last

#Calculate Rank for each district 
#Need to Fix Rank on District....
ranking = []
ranking_index = []
for district in set(df_ranking[' District']):
    data = df_ranking[(df_ranking[' District'] == district)]
    rank_list = np.array(data['Total Risk'].rank(ascending=False))
    j = 0 
    for i in range(len(data)): 
        if data[' District'][i] == district:
            #print(j)
            #print(rank_list)
            #print(rank_list[j])
            j+=1
            ranking.append(j)
            ranking_index.append(data.index[i])
    print(district, " has been evaluated and ranked")
print(len(ranking),len(df_ranking))
#df_ranking['Rank_set2'] = df_ranking['Total Risk'].rank(ascending=False) #Rank low value = last
df_district_ranks = pd.DataFrame({"District Ranking": ranking, "Site":ranking_index})
df_ranking = df_ranking.reset_index(drop=True)

#Map to the Ranking df
output_df = df_ranking.merge(df_district_ranks, left_on="Contaminated Site Name",right_on="Site",  how='left')
output_df = output_df.sort_values(by='Total Risk', ascending=False)
end = time.time()
print(end-start, "s time to Rank by District")


#--------STEP 15: Assign Ranking based on importance by district--------------------------------------
start = time.time()
df_well = well_df[['EGLE District', 'WELLID']]
df_well.to_excel("PBI_well_FileV3.xlsx")
df_schools.to_excel("PBI_School_FileV3.xlsx")
df_HC.to_excel("PBI_HC_FileV3.xlsx")
output_df.to_excel('EGLE_Contam_Prioritization_V3.xlsx')
end = time.time()
print(end-start, "s time to Export Files")

