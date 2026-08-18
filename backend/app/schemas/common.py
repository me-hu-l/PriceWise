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


class InsufficientDataResponse(BaseModel):
    """Returned instead of a forecast/confidence when a material genuinely lacks
    enough price history to model at all (roadmap section 40) — never fabricated."""

    status: str = "insufficient_data"
    reason: str = "Insufficient data for reliable forecast."

