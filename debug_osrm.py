from app.tools.distance_calculator_tool import DistanceCalculatorTool

def test_pair(patient, hospital):
    tool = DistanceCalculatorTool()
    pc = tool._geocode_city(patient)
    hc = tool._geocode_city(hospital)
    print(f"Patient: {patient} -> coords: {pc}")
    print(f"Hospital: {hospital} -> coords: {hc}")
    road = tool._get_road_distance(pc[0], pc[1], hc[0], hc[1])
    print(f"OSRM road distance (km): {road}")
    straight = tool._haversine_distance(pc[0], pc[1], hc[0], hc[1])
    print(f"Haversine distance (km): {straight}")
    print('-'*40)

if __name__ == '__main__':
    hospital = 'Ninewells Hospital, Sri Lanka'
    for p in ['Homagama', 'Kottawa']:
        try:
            test_pair(p, hospital)
        except Exception as e:
            print('Error for', p, e)
