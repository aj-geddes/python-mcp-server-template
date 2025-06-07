from mcp_server import main as main_async

if __name__ == "__main__":
    import asyncio
    import logging
    import sys

    logger = logging.getLogger(__name__)

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            loop.create_task(main_async())
            loop.run_forever()
        else:
            loop.run_until_complete(main_async())

    except KeyboardInterrupt:
        logger.info("Server interrupted, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
