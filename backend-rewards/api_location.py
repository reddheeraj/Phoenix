"""
API endpoints for location-based offer finding.
Add these to your existing api.py or use as a separate module.
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from location_based_finder import LocationBasedOfferFinder
import asyncio

router = APIRouter(prefix="/location", tags=["Location-Based Offers"])


class LocationOffersRequest(BaseModel):
    """Request model for location-based offers."""
    zipcode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class LocationOffer(BaseModel):
    """Response model for location-based offer."""
    title: str
    restaurant: str
    brand: str
    discount_percent: Optional[float]
    estimated_value: float
    url: str
    distance_km: float
    cuisine: str
    verified_live: bool
    scraped_at: str


@router.post("/offers", response_model=List[LocationOffer])
async def get_location_offers(
    zipcode: str = Query(..., description="US Zip code (e.g., 10001)"),
):
    """
    Find live restaurant offers near your location.
    
    Returns ONLY offers that currently exist on restaurant websites.
    Searches restaurants within ~3 miles of your zipcode.
    
    Example: `/location/offers?zipcode=10001`
    """
    if not zipcode or len(zipcode) != 5:
        raise HTTPException(status_code=400, detail="Invalid zipcode. Must be 5 digits.")
    
    finder = LocationBasedOfferFinder(zipcode=zipcode)
    await finder.initialize()
    
    try:
        offers = await finder.find_all_local_offers()
        return offers
    finally:
        await finder.close()


@router.get("/restaurants")
async def get_nearby_restaurants(
    zipcode: str = Query(..., description="US Zip code"),
):
    """
    Get list of nearby restaurants (without offers).
    Useful to see what's around you.
    """
    if not zipcode or len(zipcode) != 5:
        raise HTTPException(status_code=400, detail="Invalid zipcode")
    
    finder = LocationBasedOfferFinder(zipcode=zipcode)
    await finder.initialize()
    
    try:
        restaurants = await finder.find_nearby_restaurants()
        return {
            "zipcode": zipcode,
            "restaurants_found": len(restaurants),
            "restaurants": restaurants[:50]  # Limit to 50
        }
    finally:
        await finder.close()


# To integrate into main api.py, add:
# from api_location import router as location_router
# app.include_router(location_router)

