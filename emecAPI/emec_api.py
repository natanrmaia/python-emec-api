
class EmecAPI:
    def __init__(self, ies_id: int) -> None:
        self.ies_id = ies_id


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


    