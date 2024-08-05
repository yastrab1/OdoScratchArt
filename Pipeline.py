from AudioMixer import AudioMixer
def createPipelineFunc(pipelineObj, funcRaw):
    return lambda x: funcRaw(pipelineObj, x)

class Pipeline():
    def __init__(self,mixer:AudioMixer):
        self.functions = []
        self.baseFrame = None
        self.mixer = mixer

    def __next__(self):
        frame = None
        for function in self.functions:
            frame = function[0](frame)
            self.mixer.finishFrame()
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
            print(pipelineModuleName,pipelineClassName,pipelineFuncName)
            pipelineModule = __import__(pipelineModuleName)
            pipelineClass = getattr(pipelineModule, pipelineClassName)
            pipelineObj = pipelineClass(self.baseFrame,self.mixer)
            funcRaw = getattr(pipelineClass, pipelineFuncName)
            pipelineFunc = createPipelineFunc(pipelineObj,funcRaw)
            self.functions.append([pipelineFunc,pipelineFuncName])
            if(i == 0):
                self.baseFrame = pipelineFunc(None)
