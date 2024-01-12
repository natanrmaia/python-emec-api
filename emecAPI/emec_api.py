from .ies    import IesAPI
import aiohttp
import logging

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
        return f"EmecAPI(institutions={self.institutions})"

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

    async def to_dict(self):
        """
        Converts the EmecAPI instance to a dictionary representation.

        Returns:
            dict: A dictionary representation of the EmecAPI instance, where the keys are the institution (IES) IDs
                and the values are the corresponding institution (IES) objects converted to dictionaries.
        """
        print('Converting to dict')
        print(self.institutions)
        return {ies_id: await ies.to_dict() for ies_id, ies in self.institutions.items()}