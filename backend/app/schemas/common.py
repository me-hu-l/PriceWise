from pydantic import BaseModel


class NotImplementedResponse(BaseModel):
    """Structured placeholder for functionality deferred to a later phase.

    Never fabricate numeric forecasts/confidence/recommendations (roadmap section 40) —
    endpoints not yet implemented must say so explicitly instead of returning fake data.
    """

    status: str = "not_implemented"
    feature: str
    phase: str
    reason: str
