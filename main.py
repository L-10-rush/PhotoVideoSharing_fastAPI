import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.app:app", 
        host="0.0.0.0", 
        reload=True, 
        port=8000,
        reload_dirs=["app"],          # only watch your actual source folder
        reload_excludes=["*.db", "*.db-journal", "*.sqlite3"],
    )
