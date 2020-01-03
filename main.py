from Classes.vehicleSpecParser import VehicleSpecParser
from Classes.debugger import Debugger
from Classes.frontPageListingParser import FrontPageListingParser
from Classes.fileWriter import FileWriter

from time import sleep
import time, json


def main():
    debug = Debugger()
    frontPageParser = FrontPageListingParser(url="https://www.toyota.com", collectNewImages=False)
    vehicles = frontPageParser.getVehicleFrontPageListing()

    startTime = time.time()

    fileWriter = FileWriter(debug)
    
    for v in vehicles:
        print(f'{v["model"]} - {v["year"]} - {v["link"]}')
        specs = {}
        vehicleData = []
        try:
            vehicleSpecParser = VehicleSpecParser("Toyota", v["model"], v["year"], v["link"], debug)
            specs = vehicleSpecParser.parseSpecs()
            # image and category
            specs.update({"image": v["image"], "category": v["category"]})
            vehicleData.append(specs)
            vehicleSpecParser.cleanup()
        except Exception as e:
            print(f'Model: {v["model"]} Error Occurred {e}')
            debug.addErrors({"error": repr(e), "make": "Toyota", "model": v["model"],  "url": v["link"], "origin": "main()"})
            vehicleSpecParser.cleanup()
        fileWriter.appendToFile(vehicleData)
        sleep(5)

    print(f"\n\nProcessing Completed in {(time.time() - startTime)/60} minutes")   
    debug.saveToLogs()