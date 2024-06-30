import inspect
from typing import Set

import yarl

from confhub.core.error import ConfhubError


class URLBuilder:
    """
    A class for generating a URL based on parameters passed to an object.

    The `get_url` method builds URLs using parameters matching the `yarl.URL.build` method signature.
    """

    def get_url(self) -> str:
        """
        Generates and returns a URL based on object parameters.

        Returns:
            str: Generated URL in human-readable format.

        Exceptions:
            ConfhubError: Occurs if there is an error creating the URL.
        """
        # We get the signature of the yarl.URL.build method
        build_signature: inspect.Signature = inspect.signature(yarl.URL.build)
        valid_keys: Set[str] = set(build_signature.parameters.keys())

        # Collecting parameters to create a URL
        params = {
            key:
                (f"/{value}" if "/" not in value and key == "path" else value)
                if isinstance(value, str)
                else value
            for key, value in self.__dict__.items()
            if not key.startswith('_') and key in valid_keys
        }

        try:
            url: yarl.URL = yarl.URL.build(**params)
            # Returning the URL in human-readable format; Example: `http://localhost:8000`
            return url.human_repr()
        except Exception as err:
            raise ConfhubError("Error creating service url", err=err, params=params)
