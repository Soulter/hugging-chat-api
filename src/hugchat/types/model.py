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

    def __str__(self) -> str:
        return self.id
