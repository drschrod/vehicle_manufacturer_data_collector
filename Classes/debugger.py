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
    
    def encounteredErrors(self):
        found = False
        if len(self.mismatchElements) > 0:
            print("Check Logs for Mismatched Elements")
            found = True
        if len(self.errors) > 0:
            print("Check Logs for Errors")
            found = True
        return found
    
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
            self.addErrors({"error": repr(e), "origin": "__saveToFile()"})
    
    def __saveErrors(self):
        if len(self.errors) > 0:
            self.__saveToFile(self.errors, f"Logs/{self.timestamp}_errors.json")
    
    def __saveMismatchElements(self):
        if len(self.mismatchElements) > 0:
            self.__saveToFile(self.mismatchElements, f"Logs/{self.timestamp}_mismatchElements.json")
    
    def saveToLogs(self):
        self.__saveErrors()
        self.__saveMismatchElements()