class Pipeline():
    def __init__(self):
        self.functions = []
        self.baseFrame = None

    def __next__(self):
        frame = None
        for function in self.functions:
            frame = function(frame)
        return frame

    def __iter__(self):
        return self

    def loadFromConfig(self):
        config = ""
        with open("pipeline.config", "r", encoding="utf-8") as configFile:
            config = configFile.read()
        splitConfig = config.split("\n")
        for i in range(len(splitConfig)):
            configItem = splitConfig[i]
            split = configItem.split(".")
            pipelineModuleName = split[0]
            pipelineClassName = pipelineModuleName[0].upper() + pipelineModuleName[1:]
            pipelineFuncName = split[1]

            pipelineModule = __import__(pipelineModuleName)
            pipelineClass = getattr(pipelineModule, pipelineClassName)
            pipelineObj = pipelineClass(self.baseFrame)
            pipelineFunc = lambda x: getattr(pipelineClass, pipelineFuncName)(pipelineObj, x)
            self.functions.append(pipelineFunc)
            if(i == 0):
                self.baseFrame = pipelineFunc(None)
