import logging
import multiprocessing

# Disabilita il logger di Uvicorn
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.handlers = []  # Rimuovi tutti i gestori
uvicorn_logger.propagate = False  # Non propagare i log a genitori

if __name__ == "__main__":
    # enable support for multiprocessing
    multiprocessing.freeze_support()

    import uvicorn

    uvicorn.run("src.api.api:app", host="0.0.0.0", port=51012, reload=True)  # TODO check workers
