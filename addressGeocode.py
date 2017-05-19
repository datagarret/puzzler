import pandas as pd
import re
import string
import geocoder

#Patient_address.csv from consensus
patient_address = pd.read_csv('tot_pat_address.csv')
#Zip codes can only be length 5, all zips > 5 contain hyphen
patient_address['Zipcode'] = patient_address['Zipcode'].str.split('-').str[0]
patient_address['City'] = patient_address['City'].str.upper()
patient_address['Street1'] = patient_address['Street1'].str.upper()
patient_address['StateGBLCode'] = patient_address['StateGBLCode'].str.upper()
#String cleaner key value pairs will interate through to replace undesired apt info
#that do not work in the geocoder
rpl_str_dict = {'.':'',
                " AVE[\s].*| AVENUE\s.*":" AVE",
                " DR[\s].*| DRIVE[\s].*":" DR",
                " ST[\s].*| STREET[\s].*":" ST",
                " PL[\s].*| PLACE[\s].*":" PL",
                " BLVD[\s].*":" BLVD",
                " C[R]*T[\s].*":" CRT",
                " RD[\s].*| ROAD[\s]":" RD",
                " APT[\s].*":"",
                " #[\d|\s].*":"",
                " BASEMENT":"",
                " BSMT":""
               }

for sub in rpl_str_dict:
    patient_address['Street1'] = patient_address['Street1'].str.replace(sub,rpl_str_dict[sub])
#concatenate the address portions to make a full address
patient_address['Address'] = (patient_address['Street1'].str.strip() + " " + patient_address['City'].str.strip() +
                              " " + patient_address['Zipcode'].str.strip() + " "+ patient_address['StateGBLCode'])
for i in string.punctuation:
    patient_address['Address'] = patient_address['Address'].str.replace(i,'')

def geocode_select(address):
    geodata = geocoder.osm(address,url='http://localhost:8080')
    geodata = geodata.json
    if geodata['status'] == 'OK':
        return (geodata['lat'],geodata['lng'])
    return '(0,0)'

patient_address['Coord'] = patient_address['Address'].apply(geocode_select)
patient_address.to_csv('patient_address_coord.csv')
