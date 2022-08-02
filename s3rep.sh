source="sourceinsbutme1"
destination="destinationinsbutme1"


aws s3api create-bucket \
--bucket $destination \
--region us-west-2 \
--create-bucket-configuration LocationConstraint=us-west-2 \
--profile htduong


aws s3api create-bucket \
--bucket $destination \
--region us-west-2 \
--create-bucket-configuration LocationConstraint=us-west-2 \
--profile htduong

