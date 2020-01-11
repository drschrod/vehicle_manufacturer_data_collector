class FileWriter:
    def __init__(self, debugger):
        self.filename = f'Results/{int(time.time())}_vehicleSpecs.json'
        self.debugger = debugger
        self.initialized = False
        
    def __initializeResultsFile(self):
        with open(self.filename, mode='w') as resultsFile:
            json.dump([], resultsFile)

    def appendToFile(self, vehicleSpecs):
        if not self.initialized:
            self.__initializeResultsFile()
            self.initialized = True
        try:
            currentData = []
            with open(self.filename, 'r') as resultsFile:
                currentData = json.load(resultsFile)
                currentData.append(vehicleSpecs)
            with open(self.filename, 'w') as resultsFile:
                json.dump(currentData, resultsFile, indent=4, sort_keys=True)
        except Exception as e:
            print(f"Couldnt save vehicle data to file: {e}")
            self.debugger.addErrors({"error": repr(e), "origin": "appendToFile"})
    
    def writeToDemoFile(self, specs):
        try:
            with open('Results/demo_vehicleSpecs.json', 'w') as outfile:
                json.dump(specs, outfile, indent=4, sort_keys=True)
        except Exception as e:
            self.debugger.addErrors(repr(e))