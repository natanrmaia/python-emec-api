from .utils.fields import convert_text_to_base64, convert_b64_to_text, normalize_key, set_url, clean_boolean_fields
import aiohttp, json
from typing import Optional
import logging
from bs4 import BeautifulSoup

class EmecAPI:
    def __init__(self, ignore_errors: bool = False) -> None:
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
        self.ignore_errors = ignore_errors

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

    def __handle_warning(self, method: str, warning: str) -> None:
        """
        Handles warnings that occur in the specified method.

        Args:
            method (str): The name of the method where the warning occurred.
            warning (str): The warning message.

        Returns:
            None
        """
        msg = f'Warning in method >> {method} <<. {warning}'
        self.logger.warning(msg)
        self.warnings[method] = msg

    def __check_methods(self, methods: list) -> None:
        """
        Verifies and updates the list of allowed methods based on the provided methods.

        If no methods are provided or an empty list is provided, the allowed methods are used.
        Otherwise, only the methods that are present in the allowed methods list are kept.

        Returns:
            None
        """
        allowed_methods     = ['ies', 'metrics', 'regulatory_act', 'mec_process', 'campus', 'courses']
        dissallowed_methods = []
        self.methods        = methods

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

        self.__check_methods(methods)
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
        match method:
            case 'ies':
                self.ies_data['ies'] = await self._handle_ies_data()
            case 'metrics':
                self.ies_data['metrics'] = await self._handle_ies_metrics()
        #     case 'regulatory_act':
        #         self.ies_data['regulatory_act'] = await self._handle_regulatory_act()
        #     case 'mec_process':
        #         self.ies_data['mec_process'] = await self._handle_mec_process()
        #     case 'campus':
        #         self.ies_data['campus'] = await self._handle_campus()
        #     case 'courses':
        #         self.ies_data['courses'] = await self._handle_courses()
            case _:
                self.__handle_exception('__handle_method', ValueError(f'Method {method} is not allowed.'))

    async def __get(self, method: str, course_id_b64: str = None) -> BeautifulSoup:
        """
        Sends a GET request to the specified URL and returns the parsed HTML content as a BeautifulSoup object.

        Parameters:
            url (str): The URL to send the GET request to.

        Returns:
            BeautifulSoup: The parsed HTML content as a BeautifulSoup object.

        Raises:
            Exception: If the HTTP response status is not 200, an exception is raised with the corresponding status code and reason.
        """

        if method == 'courses_details' and course_id_b64 is None:
            self.__handle_exception('__get', Exception('Course id not provided for method courses_details!'))

        url = set_url(method, self.ies_id_b64, course_id_b64)

        async with self.session.get(url) as response:
            if response.status == 200:
                return BeautifulSoup(await response.text(), 'html.parser')
            else:
                self.__handle_exception('__get', Exception(f'HTTP {response.status} - {response.reason}'))

    def to_dict(self) -> dict:
        """Converts the data to dict format.

        Returns:
            dict: Returns the data in dict format.
        """
        if self.ies_data:
            return self.ies_data
        else:
            self.__handle_warning('to_dict', 'No data to convert to dict.')
            return {}

    def to_json(self) -> str:
        """Converts the data to JSON format.

        Returns:
            str: Returns the data in JSON format.
        """
        if self.ies_data:
            return json.dumps(self.ies_data)
        else:
            self.__handle_warning('to_json', 'No data to convert to JSON.')
            return '{}'

    async def _handle_ies_data(self) -> dict | None:

        def __parse_data(table: str) -> dict:
            """
            Extracts data from a table and returns it as a dictionary.

            Args:
                table: The table element to extract data from.

            Returns:
                A dictionary containing the extracted data.
            """
            table_data      = table.find_all('tr', class_='avalLinhaCampos')
            processed_data  = {}

            for row in table_data:

                tds = row.find_all('td')

                for i in range(0, len(tds), 2):
                    processed_data = __parse_data_table_td(tds[i:i+2]) | processed_data

            return processed_data

        def __parse_data_table_td(td: list) -> dict:
            """
            Process the table data in a <td> element and return a dictionary with the processed data.

            Args:
                td (list): A list containing two <td> elements.

            Returns:
                dict: A dictionary containing the processed data.

            """
            processed_td = {}
            key     = normalize_key(td[0].get_text(strip=True))  # Remove blank spaces and normalize key
            value   = td[1].get_text(strip=True)                 # Remove blank spaces

            value   = value if value != '' else None              # convert empty strings to None
            value   = clean_boolean_fields(value)                 # Convert boolean fields to boolean

            # Process the data
            if key == normalize_key('mantenedora'):
                id              = int(value.split(') ')[0].replace('(', ''))
                name            = value.split(') ')[1].split(' - ')[0]

                processed_td[normalize_key('id')]   = id
                processed_td[key]                   = name

            elif key == normalize_key('Nome da IES - Sigla'):
                id              = int(value.split(') ')[0].replace('(', ''))
                name            = value.split(') ')[1].split(' - ')[0]
                acronym         = value.split(' - ')[1] if key == normalize_key('Nome da IES - Sigla') else None

                processed_td[normalize_key('id')]           = id
                processed_td[normalize_key('nome_da_ies')]  = name
                processed_td[normalize_key('sigla_da_ies')] = acronym

            elif key == normalize_key('cnpj'):
                value           = value.replace('.', '').replace('/', '').replace('-', '')
                processed_td[key] = value
            elif key == normalize_key('representante_legal'):
                value           = value.split(' (')[0]
                processed_td[key] = value
            elif key == normalize_key('tipo_de_credenciamento'):
                processed_td[key] = None
                values           = value.split('/')
                values          = [value.strip() for value in values]

                all_values = []

                for i, value in enumerate(values):
                    key_name = normalize_key(key + ' ' + str(i+1))
                    all_values.append(value)

                processed_td[key] = all_values

            elif key == normalize_key('telefone') or key == normalize_key('fax'):
                phones = value.split(' ')
                phones = [phone.replace('(', '+55').replace(')','') for phone in phones]

                all_phones = []

                for i, phone in enumerate(phones):
                    all_phones.append(phone)

                processed_td[key] = all_phones
            else:
                processed_td[key] = value

            return processed_td

        parsed_data  = {}
        ies_data    = await self.__get('ies')

        if ies_data is None:
            return None

        ies_tables = ies_data.find_all('table', class_='avalTabCampos')

        ies_maintainer_table        = ies_tables[0]
        parsed_data['maintainer']   = __parse_data(ies_maintainer_table)

        ies_data_table              = ies_tables[1]
        parsed_data['ies']          = __parse_data(ies_data_table)

        return parsed_data

    async def _handle_ies_metrics(self) -> dict | None:
        parsed_data     = {}
        metrics_data    = await self.__get('metrics')

        if metrics_data is None:
            return None

        metrics_table = metrics_data.find('table')

        for row in metrics_table.find_all('tr'):
            tds = row.find_all('td')
            tds = [td.get_text(strip=True) for td in tds if td.get_text(strip=True) != '']

            if len(tds) == 0:
                continue
            else:
                year   = tds[0] if tds[0] != '-' else None
                ci     = int(tds[1]) if tds[1] != '-' else None
                igc    = int(tds[2]) if tds[2] != '-' else None
                ci_ead = int(tds[3]) if tds[3] != '-' else None

                year = normalize_key(year)


                parsed_data[year] = {
                    normalize_key('ci'): ci,
                    normalize_key('igc'): igc,
                    normalize_key('ci_ead'): ci_ead
                }

        return parsed_data