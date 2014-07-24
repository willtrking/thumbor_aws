Thumbor AWS
===========

 * thumbor_aws.loaders.s3_loader
 * thumbor_aws.result_storages.s3_storage
 * thumbor_aws.storages.s3_storage

Additional Configuration values used:

	# the Amazon Web Services access key to use
    AWS_ACCESS_KEY = ""
    # the Amazon Web Services secret of the used access key
    AWS_SECRET_KEY = ""


    
    # configuration settings specific for the s3_loader

    # list of allowed buckets for the s3_loader
    S3_ALLOWED_BUCKETS = []



    # configuration settings specific for the storages

    # put data into S3 using the Server Side Encryption functionality to 
    # encrypt data at rest in S3
    # https://aws.amazon.com/about-aws/whats-new/2011/10/04/amazon-s3-announces-server-side-encryption-support/
    S3_STORAGE_SSE = True or False (Default: False)

    # put data into S3 with Reduced Redundancy
    # https://aws.amazon.com/about-aws/whats-new/2010/05/19/announcing-amazon-s3-reduced-redundancy-storage/
    S3_STORAGE_RRS = True or False (Default: False)
