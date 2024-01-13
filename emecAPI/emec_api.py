from .ies    import IesAPI
import logging, json
import asyncio, aiohttp, pathlib

class EmecAPI:
    def __init__(self, session=None, auto_add_ies=True):
        """
        Initializes an instance of EmecAPI. This class is used to retrieve data from the Ministry of Education (MEC)
        website, specifically from the e-MEC API (https://emec.mec.gov.br/).
        This class is a manager for IesAPI instances, which are used to retrieve data from the MEC website.

        Args:
            session (aiohttp.ClientSession, optional): The aiohttp ClientSession to be used for making HTTP requests.
                If not provided, a new ClientSession will be created.
            auto_add_ies (bool, optional): Flag indicating whether to automatically add institutions (IES) when
                retrieving them. Defaults to True.
        """
        self.session        = session
        self.auto_add_ies   = True if auto_add_ies else False
        self.institutions   = {}

        self.__setup_logger()

    def __str__(self) -> str:
        """
        Returns a string representation of the EmecAPI instance.

        Returns:
            str: A string representation of the EmecAPI instance.
        """
        ies = ', '.join([str(ies_id) for ies_id in self.institutions])
        return f"EmecAPI(institutions = {ies})"

    def __setup_logger(self) -> None:
        """
        Sets up the logger.

        Returns:
            None
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler())

    async def add_ies(self, ies_id:int, methods:list = []):
        """
        Adds an institution (IES) to the EmecAPI instance.

        Args:
            ies_id (str): The ID of the institution (IES) to be added.
        """
        if ies_id not in self.institutions:
            print(f'Adding IES {ies_id}')
            api = IesAPI()
            await api.process(ies_id=ies_id, methods=methods, session=self.session, ignore_errors=True, logger=self.logger)

            self.institutions[ies_id] = api

    async def get_ies(self, ies_id, methods:list = []):
        """
        Retrieves an institution (IES) from the EmecAPI instance.

        Args:
            ies_id (str): The ID of the institution (IES) to be retrieved.

        Returns:
            IesAPI: The retrieved institution (IES) object, or None if it doesn't exist and auto_add_ies is False.
        """
        if ies_id in self.institutions:
            print(f'IES {ies_id} already exists')
            return self.institutions[ies_id]
        elif self.auto_add_ies:
            await self.add_ies(ies_id, methods=methods)
            return self.institutions[ies_id]
        else:
            return None

    def remove_ies(self, ies_id):
        """
        Removes an institution (IES) from the EmecAPI instance.

        Args:
            ies_id (str): The ID of the institution (IES) to be removed.
        """
        if ies_id in self.institutions:
            del self.institutions[ies_id]

    def to_dict(self):
        """
        Converts the EmecAPI instance to a dictionary representation.

        Returns:
            dict: A dictionary representation of the EmecAPI instance, where the keys are the institution (IES) IDs
                and the values are the corresponding institution (IES) objects converted to dictionaries.
        """
        data = asyncio.run(self.to_dict_async())
        return data

    async def to_dict_async(self):
        """
        Converts the EmecAPI instance to a dictionary representation asynchronously.

        Returns:
            dict: A dictionary representation of the EmecAPI instance, where the keys are the institution (IES) IDs
                and the values are the corresponding institution (IES) objects converted to dictionaries.
        """
        return {ies_id: await ies.to_dict() for ies_id, ies in self.institutions.items()}

    def to_json(self, file='EMEC_API.json', indent=4, ensure_ascii=False, encoding='utf-8', **kwargs):
        """
        Converts the EmecAPI instance to JSON format and writes it to a file.

        Args:
            file (str): The path to the output JSON file.
            indent (int): The number of spaces used for indentation in the JSON file. Defaults to 4.
            ensure_ascii (bool): If True, non-ASCII characters will be escaped in the JSON file. Defaults to False.
            **kwargs: Additional keyword arguments to be passed to the json.dumps() function.

        Returns:
            None
        """
        asyncio.run(self.to_json_async(file=file, indent=indent, ensure_ascii=ensure_ascii, **kwargs))

    async def to_json_async(self, file='EMEC_API.json', indent=4, ensure_ascii=False, encoding='utf-8', **kwargs):
        """
        Converts the object to JSON format and writes it to a file asynchronously.

        Args:
            file (str): The path to the output JSON file. Defaults to 'EMEC_API.json'.
            indent (int): The number of spaces used for indentation in the JSON file. Defaults to 4.
            ensure_ascii (bool): If True, non-ASCII characters will be escaped in the JSON file. Defaults to False.
            **kwargs: Additional keyword arguments to be passed to the json.dumps() function.

        Returns:
            None
        """
        pathlib.Path(file).parent.mkdir(parents=True, exist_ok=True)
        file = pathlib.Path(file).absolute()

        with open(file, 'w', encoding=encoding) as f:
            f.write(json.dumps(await self.to_dict_async(), indent=indent, ensure_ascii=ensure_ascii, **kwargs))

    @classmethod
    def main(cls, ies_ids, method:list = []):
        """
        Executes the main logic of the EMEC API. This method is for example purposes only.
        For a better usage, it is recommended to use the EmecAPI class directly in your code.

        Args:
            ies_ids (list): A list of IES IDs.
            method (str): The method to be used.

        Returns:
            EMECAPI: An instance of the EMECAPI class.
        """
        async def async_main():
            async with aiohttp.ClientSession() as session:
                api = cls(session=session, auto_add_ies=True)
                tasks = [asyncio.create_task(api.get_ies(ies_id, methods=method)) for ies_id in ies_ids]
                await asyncio.gather(*tasks)
                return api

        return asyncio.run(async_main())