""" Anaconda Enterprise Service Wrapper Definition """

import sys
from argparse import ArgumentParser, Namespace

from anaconda.enterprise.server.common.sdk import load_ae5_user_secrets

from .controller import AEMLFlowBackendRunnerController
from .sdk.contracts.dto.launch_parameters import LaunchParameters

if __name__ == "__main__":
    # This function is meant to provide a handler mechanism between the AE5 deployment arguments
    # and those required by the called process (or service).

    # arg parser for the standard anaconda-project options
    parser = ArgumentParser(
        prog="anaconda-enterprise-mlflow-plugin-backend-runner",
        description="anaconda enterprise mlflow plugin backend runner",
    )
    parser.add_argument("--anaconda-project-host", action="append", default=[], help="Hostname to allow in requests")
    parser.add_argument("--anaconda-project-port", action="store", default=8086, type=int, help="Port to listen on")
    parser.add_argument(
        "--anaconda-project-iframe-hosts",
        action="append",
        help="Space-separated hosts which can embed us in an iframe per our Content-Security-Policy",
    )
    parser.add_argument(
        "--anaconda-project-no-browser", action="store_true", default=False, help="Disable opening in a browser"
    )
    parser.add_argument(
        "--anaconda-project-use-xheaders", action="store_true", default=False, help="Trust X-headers from reverse proxy"
    )
    parser.add_argument("--anaconda-project-url-prefix", action="store", default="", help="Prefix in front of urls")
    parser.add_argument(
        "--anaconda-project-address",
        action="store",
        default="0.0.0.0",
        help="IP address the application should listen on",
    )
    parser.add_argument(
        "--activity",
        action="store",
        type=str,
        choices=["server", "worker"],
        help="The function (server, worker) to perform",
    )

    # Load command line arguments
    args: Namespace = parser.parse_args(sys.argv[1:])
    print(args)

    # load defined environmental variables
    load_ae5_user_secrets(silent=False)

    # Create our controller
    controller: AEMLFlowBackendRunnerController = AEMLFlowBackendRunnerController()

    # Build launch parameters
    params: LaunchParameters = LaunchParameters(
        port=args.anaconda_project_port, address=args.anaconda_project_address, activity=args.activity
    )

    # Execute the request
    controller.execute(params=params)
