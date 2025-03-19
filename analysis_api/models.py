from typing import Annotated, Self
from enum import Enum
from pydantic import BaseModel, Field, model_validator


class AnalysisRequestBase(BaseModel):
    """
    Base model for an analysis request.

    Attributes
    ----------
    track_id : str
        The unique identifier for the track.
    lyrics : str
        The lyrics of the song to be analyzed.
    """

    track_id: str
    lyrics: str
    

class EmotionalProfileRequest(AnalysisRequestBase):
    """
    Request model for retrieving the emotional profile of a track.

    Inherits from AnalysisRequestBase, using the same attributes.
    """

    pass


EmotionPercentage = Annotated[float, Field(ge=0, le=1)]
"""
Type alias for emotion proportions.

Ensures that all emotion percentages are between 0 and 1.
"""


class EmotionalProfile(BaseModel):
    """
    Represents the emotional profile of a track.

    Attributes
    ----------
    joy : float
        Proportion of lyrics associated with joy.
    sadness : float
        Proportion of lyrics associated with sadness.
    anger : float
        Proportion of lyrics associated with anger.
    fear : float
        Proportion of lyrics associated with fear.
    love : float
        Proportion of lyrics associated with love.
    hope : float
        Proportion of lyrics associated with hope.
    nostalgia : float
        Proportion of lyrics associated with nostalgia.
    loneliness : float
        Proportion of lyrics associated with loneliness.
    confidence : float
        Proportion of lyrics associated with confidence.
    despair : float
        Proportion of lyrics associated with despair.
    excitement : float
        Proportion of lyrics associated with excitement.
    mystery : float
        Proportion of lyrics associated with mystery.
    defiance : float
        Proportion of lyrics associated with defiance.
    gratitude : float
        Proportion of lyrics associated with gratitude.
    spirituality : float
        Proportion of lyrics associated with spirituality.

    Notes
    -----
    The sum of all emotion proportions is always equal to 1.
    """

    joy: EmotionPercentage
    sadness: EmotionPercentage
    anger: EmotionPercentage
    fear: EmotionPercentage
    love: EmotionPercentage
    hope: EmotionPercentage
    nostalgia: EmotionPercentage
    loneliness: EmotionPercentage
    confidence: EmotionPercentage
    despair: EmotionPercentage
    excitement: EmotionPercentage
    mystery: EmotionPercentage
    defiance: EmotionPercentage
    gratitude: EmotionPercentage
    spirituality: EmotionPercentage

    @model_validator(mode='after')
    def check_total_proportions_at_most_1(self) -> Self:
        values = self.model_dump().values()
        total_emotion_percentage = sum(values)

        if round(total_emotion_percentage, 5) != 1.0:
            print(f"{total_emotion_percentage = }")
            raise ValueError("Total emotion percentage should always equal 1.")

        return self


class EmotionalProfileResponse(EmotionalProfileRequest):
    """
    Response model for an emotional profile request.

    Attributes
    ----------
    emotional_profile : EmotionalProfile
        The emotional profile of the track, containing emotion proportions.
    """

    emotional_profile: EmotionalProfile


class Emotion(Enum):
    """
    Enum representing possible emotions in a song's lyrics.

    Attributes
    ----------
    JOY : str
        Represents joy.
    SADNESS : str
        Represents sadness.
    ANGER : str
        Represents anger.
    FEAR : str
        Represents fear.
    LOVE : str
        Represents love.
    HOPE : str
        Represents hope.
    NOSTALGIA : str
        Represents nostalgia.
    LONELINESS : str
        Represents loneliness.
    CONFIDENCE : str
        Represents confidence.
    DESPAIR : str
        Represents despair.
    EXCITEMENT : str
        Represents excitement.
    MYSTERY : str
        Represents mystery.
    DEFIANCE : str
        Represents defiance.
    GRATITUDE : str
        Represents gratitude.
    SPIRITUALITY : str
        Represents spirituality.
    """

    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    LOVE = "love"
    HOPE = "hope"
    NOSTALGIA = "nostalgia"
    LONELINESS = "loneliness"
    CONFIDENCE = "confidence"
    DESPAIR = "despair"
    EXCITEMENT = "excitement"
    MYSTERY = "mystery"
    DEFIANCE = "defiance"
    GRATITUDE = "gratitude"
    SPIRITUALITY = "spirituality"


class EmotionalTagsRequest(AnalysisRequestBase):
    """
    Request model for retrieving emotional tags in a track's lyrics.

    Attributes
    ----------
    emotion : Emotion
        The specific emotion to identify and tag within the lyrics.
    """

    emotion: Emotion


class EmotionalTagsResponse(EmotionalTagsRequest):
    """
    Response model for an emotional tags request.

    Inherits from EmotionalTagsRequest, using the same attributes.
    """

    pass
