from dataclasses import dataclass


class Model:
    def __init__(
        self,
        id: str = None,
        name: str = None,
        displayName: str = None,
        preprompt: str = None,
        promptExamples: list = None,
        websiteUrl: str = None,
        description: str = None,
        datasetName: str = None,
        datasetUrl: str = None,
        modelUrl: str = None,
        parameters: dict = None,
        unlisted: bool = None,
        logoUrl: str = None,
        reasoning: bool = None,
        multimodal: bool = None,
        tools: bool = None,
        hasInferenceAPI: bool = None,
    ):
        """
        Returns a model object
        """

        self.id: str = id
        self.name: str = name
        self.displayName: str = displayName

        self.preprompt: str = preprompt
        self.promptExamples: list = promptExamples
        self.websiteUrl: str = websiteUrl
        self.description: str = description

        self.datasetName: str = datasetName
        self.datasetUrl: str = datasetUrl
        self.modelUrl: str = modelUrl
        self.parameters: dict = parameters

        self.unlisted: bool = unlisted
        self.logoUrl: str = logoUrl
        self.reasoning: bool = reasoning
        self.multimodal: bool = multimodal
        self.tools: bool = tools
        self.hasInferenceAPI: bool = hasInferenceAPI

    def __str__(self) -> str:
        return self.id

    def display(self):
        return f"id: {self.id}\nname:{self.name}\ndisplayName: {self.displayName}\npreprompt: {self.preprompt}\nwebsiteUrl: {self.websiteUrl}\ndescription: {self.description}\nmodelUrl: {self.modelUrl}\nparameters: {self.parameters}"
