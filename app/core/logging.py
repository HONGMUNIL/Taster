import logging



def setup_logging(debug: bool = True):
    level = logging.DEBUG if debug else logging.INFO


    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s"
    )


    

