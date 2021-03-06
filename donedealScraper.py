import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
from pprint import pprint
import PySimpleGUI as sg
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

price = []
mileage = []
adUrl = []

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
		  [sg.Text('Fuel Type', size=(15, 1)), sg.InputText('Petrol')],
		  [sg.Submit(), sg.Cancel()]
		 ]

	button, inputParams = form.Layout(layout).Read()

	return inputParams

# Get ad data from each page
def getAdsDataStrings(inputParams, start):

	# Search URL
	url = 'https://api.donedeal.ie/search/api/v4/find/'
	end = start + 30

	startStr = str(start)
	endStr = str(end)

	params = '{ \
			"fuelType":"' + inputParams[4] + '", \
			"year_from":"' + inputParams[2] + '", \
			"year_to":"' + inputParams[3] + '", \
			"section":"cars", \
			"adType":"forsale", \
			"sort":"relevance desc", \
			"priceStrType":"Euro", \
			"mileageType":"Kilometres", \
			"max":' + endStr + ',"start":' + startStr + ', \
			"viewType":"list", \
			"dependant":[{"parentName":"make", \
			"parentValue":"' + inputParams[0] + '", \
			"childName":"model", \
			"childValues":["' + inputParams[1] + '"]}] \
			}'

	# POST Request
	headers = {
		'Content-Type': 'application/json',
		'Accept': 'application/json',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
	}

	adsData = requests.post(url, data=params, headers=headers, verify=False, allow_redirects=False)
	jsonAdsData = adsData.json()
	numAds = 0
	if "ads" in jsonAdsData:
		ads = jsonAdsData["ads"]
		# Add priceStr and mileage data to lists
		for ad in ads:
			if ("price" in ad and len(ad["keyInfo"]) >= 3 and ad["keyInfo"][2] != ""):
				getPrice(ad["price"], ad["currency"])
				getMileage(ad["keyInfo"][2])
				adUrl.append(ad["friendlyUrl"])

		numAds = len(ads)

	return numAds

# Loop through pages and retrieve data from each page
# Better to have the above as its own function and loop through as we effectively
# do a "do while" loop in this function and invoke the above function twice
def getAdsData(inputParams):

	start = 0
	numAds = getAdsDataStrings(inputParams, start)
	# While there are more ads to get, get them
	while numAds == 30:
		start += 30
		numAds = getAdsDataStrings(inputParams, start)

# Convert price strings to ints
def getPrice(prc, currency):

	priceNum = int(prc.replace(",", ""))

	if currency != "EUR":
		priceNum = priceNum * 1.12

	price.append(priceNum)

# Convert mileage strings to ints and convert to kilometres
def getMileage(km):

	strLen = len(km)
	
	if km[strLen-2:strLen] == "mi":
		multiplier = 1.60934
	else:
		multiplier = 1

	km = km[0:strLen - 3]

	kmVal = int(km.replace(",", ""))

	# If the user has given a value of 120 miles, they mean 120,000 miles
	# If mileage is over 1 million, divide by 10
	if kmVal < 1000:
		kmVal = kmVal * 1000
	elif kmVal > 1000000:
		kmVal = kmVal // 10

	mileage.append(kmVal * multiplier)

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

	inputParams = getInputParams()
	make, model = inputParams[0], inputParams[1]
	getAdsData(inputParams)
	plotData(make, model)

if __name__ == "__main__":
	main()