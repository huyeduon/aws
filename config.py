from botocore.config import Config

profileName="htduong"
regionName="us-west-2"

profileConfig = Config(
    region_name=regionName,
    signature_version='v4',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)
