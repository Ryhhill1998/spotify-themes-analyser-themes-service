from analysis_api.models import AnalysisRequest, EmotionalProfile
from analysis_api.services.model_service import ModelService
from analysis_api.services.storage_service import StorageService


class DataService:
    def __init__(self, model_service: ModelService, storage_service: StorageService):
        self.model_service = model_service
        self.storage_service = storage_service

    def get_emotional_profile(self, analysis_requests: list[AnalysisRequest]) -> EmotionalProfile:
        emotional_profiles = []

        for req in analysis_requests:
            data = self.model_service.generate_response(req.lyrics)
            emotional_profile = EmotionalProfile(**data)
            emotional_profiles.append(emotional_profile)

        num_emotional_profiles = len(emotional_profiles)
        average_data = {
            "joy": sum(p.joy for p in emotional_profiles) / num_emotional_profiles,
            "sadness": sum(p.sadness for p in emotional_profiles) / num_emotional_profiles,
            "anger": sum(p.anger for p in emotional_profiles) / num_emotional_profiles,
            "fear": sum(p.fear for p in emotional_profiles) / num_emotional_profiles,
            "love": sum(p.love for p in emotional_profiles) / num_emotional_profiles,
            "hope": sum(p.hope for p in emotional_profiles) / num_emotional_profiles,
            "nostalgia": sum(p.nostalgia for p in emotional_profiles) / num_emotional_profiles,
            "loneliness": sum(p.loneliness for p in emotional_profiles) / num_emotional_profiles,
            "confidence": sum(p.confidence for p in emotional_profiles) / num_emotional_profiles,
            "despair": sum(p.despair for p in emotional_profiles) / num_emotional_profiles,
            "excitement": sum(p.excitement for p in emotional_profiles) / num_emotional_profiles,
            "mystery": sum(p.mystery for p in emotional_profiles) / num_emotional_profiles,
            "defiance": sum(p.defiance for p in emotional_profiles) / num_emotional_profiles,
            "gratitude": sum(p.gratitude for p in emotional_profiles) / num_emotional_profiles,
            "spirituality": sum(p.spirituality for p in emotional_profiles) / num_emotional_profiles,
        }

        return EmotionalProfile(**average_data)
