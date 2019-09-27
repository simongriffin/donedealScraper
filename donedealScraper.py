import requests
import json
import matplotlib.pyplot as plt
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

url = 'https://api.donedeal.ie/search/api/v4/find/'

params = '{ \
	"fuelType":"Petrol", \
	"year_from":"2010", \
	"year_to":"2010", \
	"section":"cars", \
	"adType":"forsale", \
	"sort":"relevance desc", \
	"priceStrType":"Euro", \
	"mileageType":"Kilometres", \
	"max":30,"start":0, \
	"viewType":"list", \
	"dependant":[{"parentName":"make", \
	"parentValue":"Ford", \
	"childName":"model", \
	"childValues":["Focus"]}] \
	}'

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
}

priceStr = []
mileageStr = []
price = []
mileage = []

def getAdData():
	adsData = requests.post(url, data=params, headers=headers, verify=False, allow_redirects=False)
	jsonAdsData = adsData.json()
	jsonAdsDataFormatted = json.dumps(jsonAdsData, indent=4, sort_keys=True)
	# pprint (jsonAdsData["ads"][0])

	#jsonAdsDataFile = open('/home/simon/src/python projects/donedealScraper/carData.json', 'w')
	#jsonAdsDataFile.write(jsonAdsDataFormatted)
	i = 0

	# Add priceStr and mileage data to lists
	for ad in jsonAdsData["ads"]:
		if not ("price" not in ad or len(ad["keyInfo"]) < 3):
			priceStr.append(ad["price"])
			mileageStr.append(ad["keyInfo"][2])
			# print ("Ad-" + str(i) + "\n\tpriceStr: " + priceStr[i] + "\n\tMileage: " + mileage[i] + "\n")
		i += 1

# Convert price strings to ints
def getPrice():
	for prc in priceStr:
		strLen = len(prc)
		if strLen > 4:
			price.append(int(prc[0:strLen-4] + prc[strLen-3:strLen]))
		else:
			price.append(int(prc))

# Convert mileage strings to ints and convert to kilometres
def getMileage():
	for km in mileageStr:
		strLen = len(km)
		if strLen > 7:
			kmVal = int(km[0:strLen-7] + km[strLen-6:strLen-3])
		else:
			kmVal = int(km[0:strLen-3])
		
		if km[strLen-2:strLen] == "mi":
			mileage.append(kmVal * 1.60934)
		else:
			mileage.append(kmVal)

# Plot price vs mileage
def plotData():
	plt.plot(mileage, price, 'ro')
	plt.xlabel('Mileage (km)')
	plt.ylabel('Price (€)')
	plt.show()

def main():
    getAdData()
    getPrice()
    getMileage()
    plotData()
    # for prc in price:
    # 	print(prc)

if __name__ == "__main__":
    main()

# if "priceStr" not in jsonAdsData["ads"][0]:
# 	print("False")
# else:
# 	print("True")
# numberOfAds = len(jsonAdsData["ads"])