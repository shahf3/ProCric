import json
json_string = '''
{
    "matches": [
        {
            "date_time": "2024-02-23T05:36:00",
            "match_number": 1,
            "team1": "DCU Cricket Club",
            "team2": "UCC Cricket Club"
        },
        {
            "date_time": "2024-02-23T05:36:00",
            "match_number": 2,
            "team1": "DCU Cricket Club",
            "team2": "SETU Cricket Club"
        }
    ]
}
'''
test_data = json.loads(json_string)
print(type(test_data))