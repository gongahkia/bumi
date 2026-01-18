# ----- FASTAPI SERVER -----

from .validation import validate_username
from .exceptions import BumiException
from .scrapers import (
    scrape_letterboxd,
    scrape_letterboxd_user_watchlist,
    scrape_user_diary,
    scrape_user_reviews,
    scrape_film_details,
)
from .snapshot import batch_scrape_users
from .validation import check_profile_exists


def create_api_server():
    """
    creates a FastAPI server exposing scraping functionality

    Returns:
        FastAPI app instance

    Requires:
        pip install fastapi uvicorn
    """
    try:
        from fastapi import FastAPI, HTTPException, BackgroundTasks
        from fastapi.responses import JSONResponse
        from pydantic import BaseModel
        from typing import Optional, List
    except ImportError:
        raise ImportError("FastAPI required: pip install fastapi uvicorn")

    app = FastAPI(
        title="Bumi API",
        description="Letterboxd profile scraper API",
        version="1.0.0",
    )

    class ScrapeRequest(BaseModel):
        username: str
        paginate: Optional[bool] = True

    class BatchScrapeRequest(BaseModel):
        usernames: List[str]
        paginate: Optional[bool] = True

    class FilmRequest(BaseModel):
        film_slug: str

    # store for async job results
    _job_results = {}

    @app.get("/")
    async def root():
        return {"message": "Bumi API - Letterboxd Scraper", "version": "1.0.0"}

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    @app.post("/scrape/user")
    async def scrape_user_endpoint(request: ScrapeRequest):
        """scrapes a single user profile"""
        try:
            validation = validate_username(request.username)
            if not validation["valid"]:
                raise HTTPException(status_code=400, detail=validation["error"])

            target_url = f"https://letterboxd.com/{request.username}/"
            result = scrape_letterboxd(target_url, paginate=request.paginate)
            return JSONResponse(content=result)
        except BumiException as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Scraping failed: {e}")

    @app.post("/scrape/batch")
    async def scrape_batch_endpoint(
        request: BatchScrapeRequest, background_tasks: BackgroundTasks
    ):
        """scrapes multiple user profiles"""
        try:
            for username in request.usernames:
                validation = validate_username(username)
                if not validation["valid"]:
                    raise HTTPException(
                        status_code=400, detail=f"Invalid username: {username}"
                    )

            result = batch_scrape_users(request.usernames)
            return JSONResponse(content=result)
        except BumiException as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/scrape/user/{username}")
    async def scrape_user_get(username: str, paginate: bool = True):
        """scrapes a user profile via GET"""
        try:
            validation = validate_username(username)
            if not validation["valid"]:
                raise HTTPException(status_code=400, detail=validation["error"])

            target_url = f"https://letterboxd.com/{username}/"
            result = scrape_letterboxd(target_url, paginate=paginate)
            return JSONResponse(content=result)
        except BumiException as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/scrape/watchlist/{username}")
    async def scrape_watchlist_endpoint(
        username: str, paginate: bool = True, max_pages: int = 50
    ):
        """scrapes a user's watchlist"""
        try:
            validation = validate_username(username)
            if not validation["valid"]:
                raise HTTPException(status_code=400, detail=validation["error"])

            target_url = f"https://letterboxd.com/{username}/"
            result = scrape_letterboxd_user_watchlist(
                target_url, paginate=paginate, max_pages=max_pages
            )
            return JSONResponse(content={"username": username, "watchlist": result})
        except BumiException as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/scrape/diary/{username}")
    async def scrape_diary_endpoint(
        username: str, paginate: bool = True, max_pages: int = 50
    ):
        """scrapes a user's diary"""
        try:
            validation = validate_username(username)
            if not validation["valid"]:
                raise HTTPException(status_code=400, detail=validation["error"])

            target_url = f"https://letterboxd.com/{username}/"
            result = scrape_user_diary(
                target_url, paginate=paginate, max_pages=max_pages
            )
            return JSONResponse(content={"username": username, "diary": result})
        except BumiException as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/scrape/reviews/{username}")
    async def scrape_reviews_endpoint(
        username: str, paginate: bool = True, max_pages: int = 50
    ):
        """scrapes a user's reviews"""
        try:
            validation = validate_username(username)
            if not validation["valid"]:
                raise HTTPException(status_code=400, detail=validation["error"])

            target_url = f"https://letterboxd.com/{username}/"
            result = scrape_user_reviews(
                target_url, paginate=paginate, max_pages=max_pages
            )
            return JSONResponse(content={"username": username, "reviews": result})
        except BumiException as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/scrape/film")
    async def scrape_film_endpoint(request: FilmRequest):
        """scrapes film details"""
        try:
            result = scrape_film_details(request.film_slug)
            return JSONResponse(content=result)
        except BumiException as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/scrape/film/{film_slug}")
    async def scrape_film_get(film_slug: str):
        """scrapes film details via GET"""
        try:
            result = scrape_film_details(film_slug)
            return JSONResponse(content=result)
        except BumiException as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/validate/{username}")
    async def validate_endpoint(username: str):
        """validates a username"""
        result = validate_username(username)
        return JSONResponse(content=result)

    @app.get("/check/{username}")
    async def check_profile_endpoint(username: str):
        """checks if a profile exists"""
        target_url = f"https://letterboxd.com/{username}/"
        result = check_profile_exists(target_url)
        return JSONResponse(content=result)

    return app


def run_api_server(host="0.0.0.0", port=8000):
    """
    runs the FastAPI server

    Args:
        host: host to bind to
        port: port to listen on
    """
    try:
        import uvicorn
    except ImportError:
        raise ImportError("uvicorn required: pip install uvicorn")

    app = create_api_server()
    uvicorn.run(app, host=host, port=port)
