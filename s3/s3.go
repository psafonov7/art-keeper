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

const BucketName = "artifacts"
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
	_, err := client.FPutObject(ctx, BucketName, objectName, filePath, minio.PutObjectOptions{ContentType: contentType})
	if err != nil {
		log.Fatalln(err)
	}
	return nil
}

func IsObjectExists(objName string, checksum string) (bool, error) {
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

func CreateBucketIfNotExists() error {
	exists, err := client.BucketExists(ctx, BucketName)
	if err != nil {
		return err
	}
	if exists {
		log.Printf("Bucket '%s' is alredy exists", BucketName)
		return nil
	}
	err = client.MakeBucket(ctx, BucketName, minio.MakeBucketOptions{Region: DefaultRegion})
	if err == nil {
		log.Printf("Bucket '%s' is created\n", BucketName)
	}
	return err
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
