import requests, html5lib, json, time, copy
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# for each spec group parse the important info
## Vehicle Spec Parser Class here
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
        self.__createRowTemplate()
        self.__createSeriesLists()
    
    def cleanup(self):
        self.driver.quit()
         
    def __setupDriver(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(5)
        self.driver.get(self.url)
        sleep(2)
    
    def __createRowTemplate(self):
        self.__rowTemplate = {}
        for s in self.series:
            self.__rowTemplate[s] = {}
    
    def __createSeriesLists(self):
        self.__seriesLists = {}
        for s in self.series:
            self.__seriesLists[s] = []
            
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

    def __findAndClickMore(self, row):
        # class="view-more"
        try:
            moreButton = row.find_element_by_css_selector("button[class='view-more']")
            if moreButton:
                morebutton.click()
        except Exception as e:
            self.debugger.addErrors(e)

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


    
    def __expandDescription(self, container):
        desc = container.find_element_by_css_selector("td[class='category-title']")
        self.__findAndClickMore(desc)
        return desc.text
    
    def __getGroupingDescription(self, featureGroup):
        try:
            groupingDescription = featureGroup.find_element_by_css_selector("td[class='category-title sub-header']").text
            if groupingDescription == "":
                return None
            return groupingDescription
        except:
            return None
    
    def __getDescription(self, categoryRow):
        return self.__expandDescription(categoryRow)
        

    def __getRowData(self, featureRow):
        rowData = {}
        values = featureRow.find_elements_by_css_selector("td[class='category-value']")
        for i, s in enumerate(self.series):
            rowData[s] = self.__getValue(values[i])
        return rowData
        
    def __getRows(self, featureRows, featureGroup):
        groupingDescription = self.__getGroupingDescription(featureGroup)
        seriesLists = copy.deepcopy(self.__seriesLists)
        
        for featureRow in featureRows:
            description = self.__getDescription(featureRow)
            data = self.__getRowData(featureRow)
            
            for series in data:
                seriesData = { "description": description, "subgroup": groupingDescription,"value": data[series] }
                seriesLists[series].append(seriesData)
        return seriesLists
        

    def __getFeatureData(self, featureElement):
        featureData = copy.deepcopy(self.__seriesLists)
        
        # a featureGroup is a table of related data within a feature
        # there can be multiple featureGroups, generally marked with a groupingDescription
        featureGroups = featureElement.find_elements_by_css_selector("table[class='feature-group']")
        for featureGroup in featureGroups:
            if featureGroup.text == '':
                self.debugger.logWeirdElement(featureGroup, self.url, self.model, self.make, "__getFeatureData: empty text")
                continue
            try:
                # featureRows is a row that has a title, and a column of data for each series
                featureRows = featureGroup.find_elements_by_css_selector("tr[class='category-container']")
                data = self.__getRows(featureRows, featureGroup)
                for series in data:
                    featureData[series].extend(data[series])
                 
                
            except Exception as e:
                self.debugger.logWeirdElement(featureGroup, self.url, self.model, self.make, "__getFeatureData: bad element access")
                self.debugger.addErrors(
                    {"error": repr(e), "make": self.make, "model": self.model,  "url": self.url, "origin": "__getFeatureData: bad element access"})
                continue
        return featureData
    
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
            "TrimAndSeries": self.trimAndSeries, 
            "FeaturesList": self.features,
            "Features": {}
        }
        startTime = time.time()
        print(f"{self.model}:\tParsing Vehicle Features")
        for feature in self.features:
            print(f"\t{self.model}:\tParsing Feature: {feature}")
            # Find the element containing the specific feature 
            featureElement = self.__getFeatureElement(feature)
            self.__revealFeatureElement(featureElement)
            self.specs["Features"][feature] = self.__getFeatureData(featureElement)
            # print(self.specs["Features"][feature])
        print(f"{self.model}:\t Parsing Completed in {(time.time() - startTime)/60} minutes")
        return self.specs