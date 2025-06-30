import base64
import os
import subprocess
import tempfile
from contextlib import contextmanager


class Vault():
    @classmethod
    def read(cls):
        return "ZHVtbXlrZXl0YWJkYXRhMTIzNDU2"


@contextmanager
def vault_keytab():
    """fetches a base64 keytab from vault , write it out , yields its fname
    then delete it on exits
    """
    secret = Vault.read()
    kt_bytes = base64.b64decode(secret)
    # write a real temp file and close it so kinit can open it
    tf = tempfile.NamedTemporaryFile(delete_on_close=False)
    try:
        tf.write(kt_bytes)
        tf.close()
        yield tf.name
    finally:
        os.remove(tf.name)


with vault_keytab() as kt_path:
    subprocess.run(["cat", kt_path], check=True)
