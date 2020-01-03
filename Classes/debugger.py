import json, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

class Debugger:
    def __init__(self):
        self.errors = []
        self.mismatchElements = []
        self.timestamp = int(time.time())
        
    def printElements(self, elements):
        try:
            [self.printElement(e) for e in elements]
        except  AttributeError:
            print("Dont worry, not a driver object. Remove this line")

    def printElement(self, element):
        try:
            print(element.text)
        except  AttributeError:
            print("Dont worry, not a driver object. Remove this line")

    def addErrors(self, error):
        self.errors.append(error)
    
    def logWeirdElement(self, element, url, model, make, origin):
        self.mismatchElements.append({
                "innerHTML": element.get_attribute('innerHTML'), 
                "outerHTML": element.get_attribute('outerHTML'),
                "element": element.text,
                "url": url,
                "make": make,
                "model": model,
                "origin": origin
            })
    
    def printMismatchElements(self):
        for element in self.mismatchElements:
            print(element)
            
    def printErrors(self):
        for error in self.errors:
            print(error)
    
    def __saveToFile(self, data, filename):
        try:
            with open(filename, 'w') as outfile:
                json.dump(data, outfile)
        except Exception as e:
            print(f"Error Saving to File: {e}")
            self.addErrors({"error": repr(e), "make": v["make"], "model": v["model"],  "url": v["link"], "origin": "__saveToFile()"})
    
    def __saveErrors(self):
        self.__saveToFile(self.errors, f"Logs/{self.timestamp}_errors.json")
    
    def __saveMismatchElements(self):
        self.__saveToFile(self.mismatchElements, f"Logs/{self.timestamp}_mismatchElements.json")
    
    def saveToLogs(self):
        self.__saveErrors()
        self.__saveMismatchElements()