from .utils.fields  import convert_text_to_base64, convert_b64_to_text, normalize_key, set_url, clean_boolean_fields
from .settings      import BASE_URL
from typing         import Optional
from bs4            import BeautifulSoup
import aiohttp, json, asyncio, logging

class IesAPI:
    def __init__(self) -> None:
        """
        Initializes an instance of the IesAPI class.

        Returns:
            None
        """
        self.__setup_logger()
        self.logger.debug('Initializing EMEC API object. Please wait...')


        self.results    = {}
        self.errors     = {}
        self.warnings   = {}
        self.logger     = None
        self.ies_id     = None
        self.ies_data   = {}

    def __repr__(self) -> str:
        """
        Returns a string representation of the EMEC API object.

        If the ies_id attribute is defined, the string will be formatted as 'EMEC API - IES: {ies_id}'.
        If the ies_id attribute is not defined, the string will be 'EMEC API - No IES defined'.

        Returns:
            str: A string representation of the EMEC API object.
        """
        if self.ies_id is not None:
            str_name = f'EMEC API - Data for IES: {self.ies_id}'
        else:
            str_name = 'EMEC API - No IES defined'
        return str_name

    def __str__(self) -> str:
        self.__repr__()

    def __setup_logger(self) -> None:
        """
        Sets up the logger.

        Returns:
            None
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
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

        msg = f'Error in IES: {self.ies_id}. Method >> {method} <<. {type(exception).__name__}: {exception}'

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

    async def process(self, ies_id: int = None, session: aiohttp.ClientSession = None, methods: list = [], ignore_errors: bool = False, logger: object = None) -> None:
        """
        Processes the EMEC API object.

        Args:
            ies_id (int): The ID of the educational institution.
            session (object): The aiohttp session object.
            methods (list, optional): A list of methods to be processed. If the list is empty, all methods will be processed.
            ignore_errors (bool, optional): If set to True, errors will be ignored. If set to False, errors will be raised.

        Returns:
            self: Returns the EMEC API object.
        """

        if logger is not None:
            self.logger = logger
        else:
            self.__setup_logger()

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

        self.ignore_errors = ignore_errors

        self.logger.debug('EMEC API object initialized with the following parameters:')
        self.logger.debug(f'IES ID: {self.ies_id} | Methods: {methods} | Ignore errors: {self.ignore_errors}')

        self.__check_methods(methods)

        method_tasks = [self.__handle_method(method) for method in self.methods]
        await asyncio.gather(*method_tasks)
        return self

    async def __handle_method(self, method: str) -> None:
        """
        Handles the specified method.

        Args:
            method (str): The name of the method to be processed.

        Returns:
            None
        """

        data = {}

        match method:
            case 'ies':
                data                = await self._handle_ies_data()
            case 'metrics':
                data                = await self._handle_ies_metrics()
            case 'regulatory_act':
                data                = await self._handle_ies_regulatory_act()
            case 'mec_process':
                data                = await self._handle_ies_mec_process()
            case 'campus':
                pass
                # ies_data['campus'] = await self._handle_campus()
            case 'courses':
                pass
        #         ies_data['courses'] = await self._handle_courses()
            case _:
                self.__handle_exception('__handle_method', ValueError(f'Method {method} is not supported.'))

        self.ies_data.update(data)

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

    async def to_dict(self) -> dict:
        """Converts the data to dict format.

        Returns:
            dict: Returns the data in dict format.
        """
        if self.ies_data:
            return self.ies_data
        else:
            self.__handle_warning('to_dict', 'No data to convert to dict for the specified IES.')
            return {}

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
        processed_data  = {}
        current_line    = 0
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


                data = {
                    normalize_key('year'): year,
                    normalize_key('ci'): ci,
                    normalize_key('igc'): igc,
                    normalize_key('ci_ead'): ci_ead
                }

                processed_data[current_line] = data
                current_line += 1

        parsed_data['metrics'] = processed_data

        return parsed_data

    async def _handle_ies_regulatory_act(self) -> dict | None:
        """
        Retrieves the regulatory acts for the educational institution.

        Returns:
            dict: A dictionary containing the parsed data, including the regulatory acts and the URL.
                  The 'acts' key contains a dictionary of regulatory acts, where each act is represented by a key-value pair.
                  The 'url' key contains the URL used to retrieve the regulatory acts.
            None: If the regulatory acts data is not available or cannot be parsed.
        """
        parsed_data     = {}
        acts_data    = await self.__get('regulatory_act')

        if acts_data is None:
            return None

        data = acts_data.find('table')
        if data is None:
            return None  # Add a check if the 'table' tag is not found

        trs         = data.find_all('tr')
        acts        = {}
        current_act = 0
        act         = {}  # Dicionário para armazenar os pares chave-valor do grupo atual

        for tr_index in range(len(trs)):
            tr = trs[tr_index]
            tds = tr.find_all('td')

            for i in range(0, len(tds), 2):
                if i+1 < len(tds):  # Verificar se o índice i+1 está dentro do limite
                    key = normalize_key(tds[i].get_text(strip=True))
                    if key == normalize_key('arquivo_para_download'):
                        if tds[i+1].find('img', class_='link') is None:
                            value = None
                        else:
                            # value = self.BASE_URL + tds[i+1].find('img', class_='link').get('onclick').split('emec/')[1].split("'")[0]
                            value = BASE_URL + tds[i+1].find('img', class_='link').get('onclick').split('emec/')[1].split("'")[0]
                    else:
                        value = tds[i+1].get_text(strip=True)

                    # Adicionar ou atualizar a chave no dicionário act
                    act[key] = value

            # Verificar se o tr atual tem a classe específica para adicionar o act ao acts e começar um novo act
            if 'subline' in tr.get('class', []):

                acts[current_act] = act
                current_act += 1
                act = {}

        # Certificar-se de adicionar o último act se ele não estiver vazio
        if act:
            acts[current_act] = act

        parsed_data['regulatory_act'] = acts

        return parsed_data

    async def _handle_ies_mec_process(self) -> dict | None:
        parsed_data     = {}
        processed_data  = {}
        current_line    = 0
        process_data    = await self.__get('mec_process')

        if process_data is None:
            return None

        data = process_data.find('table')
        if data is None:
            return None

        trs         = data.find_all('tr', class_='corDetalhe2') + data.find_all('tr', class_='corDetalhe1')

        for tr in trs:
            tds = tr.find_all('td')

            id         = tds[0].get_text(strip=True) if tds[0].get_text(strip=True) != '' else None
            type       = tds[1].get_text(strip=True) if tds[1].get_text(strip=True) != '' else None
            course     = tds[2].get_text(strip=True) if tds[2].get_text(strip=True) != '' else None
            status     = tds[3].get_text(strip=True) if tds[3].get_text(strip=True) != '' else None

            process = {
                "id": id,
                "type": type,
                "course": course,
                "status": status
            }

            processed_data[current_line] = process
            current_line += 1

        parsed_data['mec_process'] = processed_data

        return parsed_data