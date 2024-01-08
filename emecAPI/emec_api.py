from .utils.fields import convert_text_to_base64, convert_b64_to_text, normalize_key
import aiohttp
from typing import Optional
import logging
from bs4 import BeautifulSoup

class EmecAPI:
    def __init__(self) -> None:
        """
        Initializes an instance of the EmecAPI class.

        Returns:
            None
        """
        self.__setup_logger()
        self.logger.debug('Initializing EMEC API object. Please wait...')
        self.logger.debug('EMEC API object initialized.')

        self.results    = {}
        self.errors     = {}
        self.warnings   = {}

    def __str__(self) -> str:
        """
        Returns a string representation of the EMEC API object.

        If the ies_id attribute is defined, the string will be formatted as 'EMEC API - IES: {ies_id}'.
        If the ies_id attribute is not defined, the string will be 'EMEC API - No IES defined'.

        Returns:
            str: A string representation of the EMEC API object.
        """
        if self.ies_id:
            str_name = f'EMEC API - IES: {self.ies_id}'
        else:
            str_name = 'EMEC API - No IES defined'
        return str_name

    def __setup_logger(self) -> None:
        """
        Sets up the logger.

        Returns:
            None
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler())

    def __handle_exception(self, method: str, exception: Exception) -> None:
        """
        Handles exceptions that occur in the specified method.

        Args:
            method (str): The name of the method where the exception occurred.
            exception (Exception): The exception that was raised.

        Returns:
            None
        """

        msg = f'Error in method >> {method} <<. {type(exception).__name__}: {exception}'

        if self.ignore_errors:
            msg = f'Ignoring error. {msg}'
            self.logger.warning(msg)
            self.warnings[method] = msg
        else:
            self.logger.error(msg)
            self.errors[method] = msg
            raise exception

    def __check_methods(self) -> None:
        """
        Verifies and updates the list of allowed methods based on the provided methods.

        If no methods are provided or an empty list is provided, the allowed methods are used.
        Otherwise, only the methods that are present in the allowed methods list are kept.

        Returns:
            None
        """
        allowed_methods = ['ies', 'metrics', 'regulatory_act', 'mec_process', 'campus', 'courses']

        if self.methods is None or len(self.methods) == 0:
            self.methods = allowed_methods
        else:
            dissallowed_methods = [method for method in self.methods if method not in allowed_methods]
            self.methods = [method for method in self.methods if method in allowed_methods]

        if len(dissallowed_methods) > 0:
            self.logger.warning(f'The following methods are not allowed: {dissallowed_methods}. They will be ignored.')

    async def process(self, ies_id: int = None, session: object = None, methods: list = [], ignore_errors: bool = False) -> None:
        """
        Processes the EMEC API object.

        Args:
            ies_id (int): The ID of the educational institution.
            session (object): The aiohttp session object.
            methods (list, optional): A list of methods to be processed. If the list is empty, all methods will be processed.
            ignore_errors (bool, optional): If set to True, errors will be ignored. If set to False, errors will be raised.

        Returns:
            None
        """
        if ies_id is None:
            self.__handle_exception('process', ValueError('ies_id is required.'))
        else:
            self.ies_id     = ies_id
            self.ies_id_b64 = convert_text_to_base64(self.ies_id)

        if session is None:
            self.__handle_exception('process', ValueError('AIOHTTP Session is required.'))
        if not isinstance(session, aiohttp.ClientSession):
            self.__handle_exception('process', ValueError('AIOHTTP Session must be an instance of aiohttp.ClientSession.'))
        else:
            self.session    = session

        self.ies_data = {}

        self.__check_methods()
        for method in self.methods:
            await self.__handle_method(method)

    async def __handle_method(self, method: str) -> None:
        """
        Handles the specified method.

        Args:
            method (str): The name of the method to be processed.

        Returns:
            None
        """
        pass
        # match method:
        #     case 'ies':
        #         self.ies_data['ies'] = await self._handle_ies()
        #     case 'metrics':
        #         self.ies_data['metrics'] = await self._handle_metrics()
        #     case 'regulatory_act':
        #         self.ies_data['regulatory_act'] = await self._handle_regulatory_act()
        #     case 'mec_process':
        #         self.ies_data['mec_process'] = await self._handle_mec_process()
        #     case 'campus':
        #         self.ies_data['campus'] = await self._handle_campus()
        #     case 'courses':
        #         self.ies_data['courses'] = await self._handle_courses()
        #     case _:
        #         self.__handle_exception('__handle_method', ValueError(f'Method {method} is not allowed.'))

    async def __get(self, url: str) -> BeautifulSoup:
        pass