import json

f = open("C:\DEV\Django\MovieRecommendation\sample.json",)

context = json.load(f)
print(context)