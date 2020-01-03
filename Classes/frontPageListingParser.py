class FrontPageListingParser():
    def __init__(self, url, debugger=None, collectNewImages=False):
        self.vehicles = []
        self.url = url
        self.parsedModels = {}
        if debugger is not None:
            self.debugger = debugger
        self.__setupDriver()
        self.__clickVehicleDropDown()
        self.__setVehicleCategoryButtons()
        self.collectNewImages = collectNewImages
        
    def __setupDriver(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(5)
        self.driver.get(self.url)
        sleep(2)
        
    def __clickVehicleDropDown(self):
        python_button = self.driver.find_element_by_css_selector("button[data-view='select-vehicle']")
        if python_button.text == "Select Vehicle":
            python_button.click()
        else:
            raise ValueError(f"ERROR: Bad Button access: {python_button.text}")
        sleep(2)
        
    def __setVehicleCategoryButtons(self):
        vehicleCategories = self.driver.find_element_by_css_selector("ul[class='models']")
        self.vehicleCategoryButtons = vehicleCategories.find_elements_by_tag_name("li")
        sleep(3)
    
    def __validateVehicle(self, vehicleData):
        #Note: we can have it update the category here
        if vehicleData['model'] not in self.parsedModels.keys():
            self.parsedModels.update({vehicleData['model']: vehicleData})
            self.vehicles.append(vehicleData)
    
    def __borrowImage(self, li, model):
        filename = f"./Images/{model}.png"
        if self.collectNewImages:
            imageDiv = li.find_element_by_css_selector("div[class='vehicle-image-wrapper']")
            imageURL = imageDiv.find_element_by_css_selector("img").get_attribute("data-srcset")
            urllib.request.urlretrieve(self.url + imageURL, filename)
        return filename
    
    def getVehicleFrontPageListing(self):
        print("Getting Vehicle Listing...")
        for button in self.vehicleCategoryButtons:
            category = button.text
            button.click()
            parentList = self.driver.find_elements_by_css_selector("ul[class='vehicles']")
            for vehicleGroup in parentList:
                listItems = vehicleGroup.find_elements_by_css_selector("li")
                for li in listItems:
                    link = li.find_element_by_css_selector("a").get_attribute("href")
                    details = li.find_element_by_css_selector("p[class='model']").text
                    if link is not None and details != '':
                        vehicleData = {}
                        vehicleData["link"] = link
                        vehicleData["category"] = category
                        vehicleData["year"], vehicleData["model"] =  details.split(' ', 1)
                        vehicleData["image"] = self.__borrowImage(li, vehicleData["model"])
                        self.__validateVehicle(vehicleData)
        sleep(3)
        self.driver.quit()
        print(f"Retrieved {len(self.vehicles)} vehicles from the homepage {self.url}")
        return self.vehicles