import argparse
import logging
import ssl
import sys
import time
import xml.etree.ElementTree as eT
from dataclasses import dataclass, field
from pathlib import Path

import httpx

# Default constants
DEFAULT_CERT_PATH = Path(__file__).parent / 'images' / 'ca.pem'
POLL_INTERVAL = 8  # seconds
CIPHER = 'xxxx'
BASE_URL = 'https://XXXXXXX'
JOB_ID = 'XXXXXXXX'


def _create_ssl_context(cert_path: Path) -> ssl.SSLContext:
    """
    Create and configure an SSL context for secure server authentication.
    """
    context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    if hasattr(context, 'minimum_version'):
        context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_verify_locations(cafile=str(cert_path))
    context.set_ciphers(CIPHER)
    return context


def _get_attribute_value(xml_text: str, attribute: str) -> str:
    """
    Extract the value of the given attribute from the first <execution> element in the XML.
    """
    root = eT.fromstring(xml_text)
    elem = root.find('.//execution')
    if elem is None or attribute not in elem.attrib:
        raise DeploymentError(f"Missing <execution> element or '{attribute}' in response XML")
    return elem.attrib[attribute]


class DeploymentError(Exception):
    """Custom exception for deployment-related errors."""
    pass


@dataclass
class DeploymentClient:
    """
    Client for triggering and monitoring Rundeck deployment jobs. Use as a context manager.
    """
    token: str
    cert_path: Path = DEFAULT_CERT_PATH
    client: httpx.Client = field(init=False)

    def __post_init__(self):
        ssl_context = _create_ssl_context(self.cert_path)
        transport = httpx.HTTPTransport(verify=ssl_context)
        self.client = httpx.Client(
            transport=transport,
            headers={
                'X-Rundeck-Auth-Token': self.token,
                'Content-Type': 'application/json',
            },
            http2=False,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def trigger(self, tag: str) -> str:
        """
        Trigger the deployment job and return its execution ID.
        """
        url = f"{BASE_URL}/api/14/job/{JOB_ID}/run"
        payload = {'options': {'ENV': 'int', 'VERSION': tag}}

        resp = self.client.post(url, json=payload)
        resp.raise_for_status()
        xml = resp.text

        exec_id = _get_attribute_value(xml, 'id')
        status = _get_attribute_value(xml, 'status')
        if status != 'running':
            raise DeploymentError(f"Job failed to start (status={status})")

        logging.info(f"Job started, execution ID: {exec_id}")
        return exec_id

    def poll(self, execution_id: str) -> str:
        """
        Poll the execution status until it is no longer 'running'. Returns the final status.
        """
        url = f"{BASE_URL}/api/14/execution/{execution_id}"
        while True:
            time.sleep(POLL_INTERVAL)
            resp = self.client.get(url)
            resp.raise_for_status()
            status = _get_attribute_value(resp.text, 'status')
            logging.info(f"Status: {status}")
            if status != 'running':
                return status

    def deploy(self, tag: str) -> str:
        """
        Full deploy flow: trigger + poll. Returns final status.
        """
        exec_id = self.trigger(tag)
        return self.poll(exec_id)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Trigger and monitor a Rundeck deployment job."
    )
    parser.add_argument('--token', required=True, help='Rundeck API token')
    parser.add_argument('--tag', required=True, help='Version tag to deploy')
    parser.add_argument(
        '--cert-path', type=Path, default=DEFAULT_CERT_PATH,
        help='Path to CA certificate'
    )
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )
    args = parse_args()

    try:
        with DeploymentClient(token=args.token, cert_path=args.cert_path) as client:
            final_status = client.deploy(args.tag)

        if final_status != 'succeeded':
            logging.error(f"Deployment ended with status: {final_status}")
            return 1

        logging.info("Deployment succeeded.")
        return 0

    except Exception as e:
        logging.exception("Deployment failed.", e)
        return 1


if __name__ == '__main__':
    sys.exit(main())


