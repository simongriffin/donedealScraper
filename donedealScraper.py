import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
from pprint import pprint
import PySimpleGUI as sg
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

url = 'https://api.donedeal.ie/search/api/v4/find/'
priceStr = []
mileageStr = []
price = []
mileage = []
adUrl = []
currency = [] 

headers = {
	'Content-Type': 'application/json',
	'Accept': 'application/json',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
}

# Accept user inputted parameters
def getInputParams():
	# Very basic form.  Return values as a list
	form = sg.FlexForm('Input Parameters')  # begin with a blank form

	layout = [
		  [sg.Text('Please enter car details')],
		  [sg.Text('Make', size=(15, 1)), sg.InputText('Ford')],
		  [sg.Text('Model', size=(15, 1)), sg.InputText('Focus')],
		  [sg.Text('Year From', size=(15, 1)), sg.InputText('2010')],
		  [sg.Text('Year To', size=(15, 1)), sg.InputText('2010')],
		  [sg.Text('Fuel Type', size=(15, 1)), sg.InputText('Diesel')],
		  [sg.Submit(), sg.Cancel()]
		 ]

	button, inputParams = form.Layout(layout).Read()

	return inputParams

# Get ad data from each page
def getAdsDataStrings(inputParams, start, end):

	params = '{ \
			"fuelType":"' + inputParams[4] + '", \
			"year_from":"' + inputParams[2] + '", \
			"year_to":"' + inputParams[3] + '", \
			"section":"cars", \
			"adType":"forsale", \
			"sort":"relevance desc", \
			"priceStrType":"Euro", \
			"mileageType":"Kilometres", \
			"max":' + end + ',"start":' + start + ', \
			"viewType":"list", \
			"dependant":[{"parentName":"make", \
			"parentValue":"' + inputParams[0] + '", \
			"childName":"model", \
			"childValues":["' + inputParams[1] + '"]}] \
			}'

	adsData = requests.post(url, data=params, headers=headers, verify=False, allow_redirects=False)
	jsonAdsData = adsData.json()
	numAds = 0
	if not ("ads" not in jsonAdsData):
		ads = jsonAdsData["ads"]
		# Add priceStr and mileage data to lists
		for ad in ads:
			if not ("price" not in ad or len(ad["keyInfo"]) < 3 or ad["keyInfo"][2] == ""):
				priceStr.append(ad["price"])
				mileageStr.append(ad["keyInfo"][2])
				adUrl.append(ad["friendlyUrl"])
				currency.append(ad["currency"])

		numAds = len(ads)

	return numAds

# Loop through pages and retrieve data from each page
# Better to have the above as its own function and loop through as we effectively
# do a "do while" loop in this function and invoke the above function twice
def getAdsData(inputParams):

	start = 0
	end = 30
	numAds = getAdsDataStrings(inputParams, str(start), str(end))
	num = numAds
	# While there are more ads to get, get them
	while numAds == 30:
		start += 30
		end += 30
		numAds = getAdsDataStrings(inputParams, str(start), str(end))
		num += numAds

# Convert price strings to ints
def getPrice():

	i = 0
	for prc in priceStr:
		strLen = len(prc)
		if strLen > 4:
			priceNum = int(prc[0:strLen-4] + prc[strLen-3:strLen])
		else:
			priceNum = int(prc)

		if currency[i] != "EUR":
			priceNum = priceNum * 1.12

		price.append(priceNum)

		i += 1

# Convert mileage strings to ints and convert to kilometres
def getMileage():
	for km in mileageStr:
		strLen = len(km)
		if strLen > 11:
			kmVal = int(km[0:strLen-11] + km[strLen-10:strLen-7] + km[strLen-6:strLen-3])
		elif strLen <= 11 and strLen > 7:
		# if strLen > 7:
			kmVal = int(km[0:strLen-7] + km[strLen-6:strLen-3])
		else:
			kmVal = int(km[0:strLen-3])
		
		# If the user has given a value of 120 miles, they mean 120,000 miles
		# If mileage is over 1 million, divide by 10
		if kmVal < 1000:
			kmVal = kmVal * 1000
		elif kmVal > 1000000:
			kmVal = kmVal // 10

		if km[strLen-2:strLen] == "mi":
			mileage.append(kmVal * 1.60934)
		else:
			mileage.append(kmVal)

# Plot price vs mileage
def plotData(make, model):
	f = plt.figure(figsize=(10,10))
	s = plt.scatter(mileage, price)
	plt.title(make + " " + model)
	plt.xlabel('Mileage (km)')
	plt.ylabel('Price (€)')
	s.set_urls(adUrl)
	f.savefig('adsData.svg')

def main():
	# print(params)
	inputParams = getInputParams()
	make, model = inputParams[0], inputParams[1]
	getAdsData(inputParams)
	getPrice()
	getMileage()
	plotData(make, model)

if __name__ == "__main__":
	main()

# if "priceStr" not in jsonAdsData["ads"][0]:
# 	print("False")
# else:
# 	print("True")
# numberOfAds = len(jsonAdsData["ads"])