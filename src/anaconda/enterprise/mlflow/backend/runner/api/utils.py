from typing import Optional

from ae5_tools.api import AEUserSession

from anaconda.enterprise.server.common.sdk import demand_env_var

from ..sdk.contracts.dto.client_options import ClientOptions


def get_ae_user_session(options: Optional[ClientOptions] = None) -> AEUserSession:
    """
    Get an AE User Session

    Parameters
    ----------
    options: Optional[ClientOptions]
        Optional configuration for the client instantiation.

    Returns
    -------
    client: AEClient
        An instance of an AEClient.
    """

    if options is None:
        options_dict: dict = {
            "hostname": demand_env_var(name="AE_HOSTNAME"),
            "username": demand_env_var(name="AE_USERNAME"),
            "password": demand_env_var(name="AE_AUTH"),
        }
        options: ClientOptions = ClientOptions.parse_obj(options_dict)

    return AEUserSession(**options.dict())
