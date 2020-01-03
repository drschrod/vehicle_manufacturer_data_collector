import requests, html5lib, json, time
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

class VehicleSpecParser:
    def __init__(self, make, model, year, url, debugger):
        self.make = make.lower()
        self.model = model.lower()
        self.year = year
        self.url = url
        self.debugger = debugger
        self.__setupDriver()
        self.__clickSpecsButton()
        self.__getVehicleFeatureCategories()
    
    def cleanup(self):
        self.driver.quit()
         
    def __setupDriver(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(5)
        self.driver.get(self.url)
        sleep(2)
        
    def __clickSpecsButton(self):
        specsButton = self.driver.find_element_by_xpath("//*[text()='Specs']")
        specsButton.click()
        sleep(3)
        self.series = [s.text for s in self.driver.find_elements_by_css_selector("span[class='series']") if s.text != '']
        self.trims = [t.text for t in self.driver.find_elements_by_css_selector("div[class='trim']") if t.text != '']
        self.trimAndSeries = {}
        for i, s in enumerate(self.series):
            self.trimAndSeries[s] = self.trims[i]
        sleep(3)
        
    def __ignoreEmptys(self, x):
        if x.text != '':
            return True
        else:
            return False
        
    def __getVehicleFeatureCategories(self):
        collapseButton = self.driver.find_element_by_css_selector("button[data-di-id='#collapse-btn']")
        collapseButton.click()
        featuresElement = self.driver.find_element_by_css_selector("div[class='feature-accordions']")
        self.features = [f.text for f in filter(
            self.__ignoreEmptys, featuresElement.find_elements_by_css_selector("div[class='tcom-accordion']"))]
        sleep(3)

    def findAndClickMore(self, featureElement):
        moreButtons = [button for button in 
                       featureElement.find_elements_by_css_selector("a") if button.text.lower() == "more"]
        for button in moreButtons:
            button.click()
        sleep(3)

    def __getFeatureElement(self, feature):
        try:
            if 'Warranty Information' in feature:
                featureElement = self.driver.find_element_by_css_selector(
                    f"div[class='tcom-accordion'][title='Warranty Information*']")
            else:
                featureElement = self.driver.find_element_by_css_selector(
                    f"div[class='tcom-accordion'][title='{feature}']")
            return featureElement
        except Exception as e:
            self.debugger.addErrors({"error": repr(e), "make": self.make, "model": self.model,  "url": self.url, "origin": "__getFeatureElement"})
            return self.driver

    def __revealFeatureElement(self, featureElement):
        featureButton = featureElement.find_element_by_css_selector("button")
        featureButton.click()
    
    def __getValue(self, valueDriver):
        if valueDriver.text != '':
            return valueDriver.text
        return valueDriver.find_element_by_css_selector("i").get_attribute('aria-label')

    def __getRowData(self, categoryContainer):
        rowData = {}
        values = categoryContainer.find_elements_by_css_selector("td[class='category-value']")
        for i, s in enumerate(self.series):
            rowData[s] = self.__getValue(values[i])
        return rowData

    def __getSubtitleIfExists(self, category):
        try:
            subtitle = category.find_element_by_css_selector("td[class='category-title sub-header']").text
            return subtitle
        except:
            return None

    def __getCategoryData(self, featureElement):
        categoryData = {}
        for s in self.series:
            categoryData[s] = {}
        categories = featureElement.find_elements_by_css_selector("table[class='feature-group']")
        for c in categories:
            if c.text == '':
                self.debugger.logWeirdElement(c, self.url, self.model, self.make, "__getCategoryData: empty text")
                continue
            try:
                categoryContainer = c.find_element_by_css_selector("tr[class='category-container']")
            except Exception as e:
                self.debugger.logWeirdElement(c, self.url, self.model, self.make, "__getCategoryData: bad element access")
                self.debugger.addErrors(
                    {"error": repr(e), "make": self.make, "model": self.model,  "url": self.url, "origin": "__getCategoryData: bad element access"})
                continue
            title = categoryContainer.find_element_by_css_selector("td[class='category-title']").text
            subtitle = self.__getSubtitleIfExists(c)
            rowData = self.__getRowData(categoryContainer)
            for seriesColumn in rowData:
                categoryData[seriesColumn]["title"] = title
                categoryData[seriesColumn]["value"] = rowData[seriesColumn]
                if subtitle is not None:
                    categoryData[seriesColumn]["subtitle"] = subtitle
        return categoryData
    
    def parseSpecs(self):
        '''
        Given the web page for a specific vehicle,
        Parse out all vehicle specs from the web page
        Divided out by: Feature > Category (row of data in a feature) > spec
        '''
        self.specs = {
            "Trims": self.trims, 
            "Series": self.series,
            "Model": self.model,
            "Make": self.make,
            "Year": self.year,
            "URL": self.url,
            "trimAndSeries": self.trimAndSeries, 
            "featuresList": self.features,
            "Features": {}
        }
        startTime = time.time()
        print(f"{self.model}:\tParsing Vehicle Features")
        for feature in self.features:
            print(f"\t{self.model}:\tParsing Feature: {feature}")
            # Find the element containing the specific feature 
            featureElement = self.__getFeatureElement(feature)
            self.__revealFeatureElement(featureElement)
            self.findAndClickMore(featureElement) # NOTE: need to click not in bulk
            self.specs["Features"][feature] = self.__getCategoryData(featureElement)
        print(f"{self.model}:\t Parsing Completed in {(time.time() - startTime)/60} minutes")
        return self.specs