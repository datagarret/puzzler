import googlemaps
import pandas as pd

key = input('Enter gmaps Key: ')
gmaps = googlemaps.Client(key=key)
#'832 W. 63rd St. Chicago, Il 60621' whole foods address
destination = input('Enter the destination address: ')

txt_reply = pd.read_csv('responses_clean.csv')
txt_reply['Coord'].fillna('(0, 0)',inplace=True)
#converts strings to tuple
txt_reply['Coord'] = txt_reply['Coord'].apply(eval)

def lat_lng(coordinates):
    '''Add error of ~100m to lat_lng coordinates by removing dec. points
    Arg: Tuple of lat_lng outputted from nominatim geolocation
    Returns: Tuple of floats with truncated lat_lng'''
    if coordinates != (0, 0):
        lat = round(coordinates[0],5)
        lng = round(coordinates[1],5)
        return (lat,lng)
    else:
        return (0,0)

txt_reply['Coord'] = txt_reply['Coord'].apply(lat_lng)
pat_address_dict = dict(zip(txt_reply['PatientID'].values,
                            txt_reply['Coord'].values))
pat_dist_time = {}
transit_list = ["driving", "walking", "bicycling", "transit"]

for pat in pat_address_dict:
    if pat_address_dict[pat] == (0,0):
        continue
    pat_dist_time[pat] = {}
    for transit in transit_list:
        dist_mat = gmaps.distance_matrix(pat_address_dict[pat],destination,mode=transit)
        #makes retrieval of info look better in later query
        data_retriever = dist_mat['rows'][0]['elements'][0]
        #status != Ok than issue with query
        if dist_mat['status'] != 'OK' or data_retriever['status'] != 'OK':
            #conversion of units in df will be divided to -1
            distance = -1
            duration = -1
        else:
            #converts minutes to hours and meters to km
            distance = data_retriever['distance']['value']/1000
            duration = data_retriever['duration']['value']/60
        pat_dist_time[pat].update({transit+"_query_status":dist_mat['status'],
                                   transit+"_distance":distance,
                                   transit+"_duration":duration})

pt_dmatrix_df = pd.DataFrame.from_dict(pat_dist_time,orient='index')
#compare all status columns to see if all queries were successful
status_cols = [i for i in pt_dmatrix_df.columns if 'status' in i]
pt_dmatrix_df['query_pass'] = pt_dmatrix_df[status_cols].eq(pt_dmatrix_df.loc[:,status_cols[0]],axis=0).all(axis=1)


pt_dmatrix_df = pd.merge(pt_dmatrix_df,clean_respondent[['Response']],
                         left_index=True,right_on='PatientID')

pt_dmatrix_df.sort_index(axis=1,inplace=True)
pt_dmatrix_df.to_csv('transit_dist.csv')
