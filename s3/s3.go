package s3

import (
	"context"
	"log"
	"os"

	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
)

const S3EndpointEnv = "S3_ENDPOINT"
const S3AccessKeyIdEnv = "S3_ACCESS_KEY_ID"
const S3SecretAccessKeyEnv = "S3_SECRET_ACCESS_KEY"

const BucketName = "bucket"
const DefaultRegion = "us-east-1"

const ObjectNotExistErrorCode = "NoSuchKey"

var client *minio.Client
var ctx context.Context

func Setup() {
	c, err := createClient()
	if err != nil {
		panic("")
	}
	client = c

	ctx = context.Background()
}

func UploadFile(filePath string, objectName string) error {
	contentType := "application/octet-stream"
	ctx := context.Background()
	client, err := createClient()
	if err != nil {
		return err
	}
	createBucketIfNotExists(ctx, BucketName)
	_, err = client.FPutObject(ctx, BucketName, objectName, filePath, minio.PutObjectOptions{ContentType: contentType})
	if err != nil {
		log.Fatalln(err)
	}
	return nil
}

func IsObjectExists(objName string, checksum string) (bool, error) {
	client, err := createClient()
	if err != nil {
		return false, err
	}
	o := minio.ObjectAttributesOptions{}
	attr, err := client.GetObjectAttributes(ctx, BucketName, objName, o)
	if err != nil {
		if minio.ToErrorResponse(err).Code == ObjectNotExistErrorCode {
			return false, nil
		}
		return false, err
	}
	match := attr.Checksum.ChecksumSHA1 == checksum
	return match, nil
}

func createBucketIfNotExists(ctx context.Context, bucketName string) {
	exists, err := client.BucketExists(ctx, bucketName)
	if err != nil {
		log.Fatalln(err)
	}
	if !exists {
		err = client.MakeBucket(ctx, bucketName, minio.MakeBucketOptions{Region: DefaultRegion})
		if err != nil {
			log.Fatalln(err)
		} else {
			log.Printf("Bucket '%s' is created\n", bucketName)
		}
	}
}

func createClient() (*minio.Client, error) {
	endpoint := os.Getenv(S3EndpointEnv)
	accessKeyID := os.Getenv(S3AccessKeyIdEnv)
	secretAccessKey := os.Getenv(S3SecretAccessKeyEnv)
	useSSL := true

	client, err := minio.New(endpoint, &minio.Options{
		Creds:  credentials.NewStaticV4(accessKeyID, secretAccessKey, ""),
		Secure: useSSL,
	})
	return client, err
}
