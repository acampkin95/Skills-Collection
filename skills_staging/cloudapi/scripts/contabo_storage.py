#!/usr/bin/env python3
"""
Contabo Object Storage Management Script
S3-compatible storage operations using boto3.
Credentials loaded from environment variables.
"""

import os
import sys
import json
import argparse
from typing import Optional, List, Dict, Any

try:
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError
except ImportError:
    print("Error: boto3 required. Install with: pip install boto3", file=sys.stderr)
    sys.exit(1)


class ContaboStorage:
    """Contabo S3-compatible object storage client."""
    
    def __init__(self):
        self.access_key = os.environ.get("CONTABO_ACCESS_KEY")
        self.secret_key = os.environ.get("CONTABO_SECRET_KEY")
        self.endpoint = os.environ.get("CONTABO_ENDPOINT", "https://sin1.contabostorage.com")
        self.bucket = os.environ.get("CONTABO_BUCKET")
        
        if not self.access_key or not self.secret_key:
            raise ValueError("CONTABO_ACCESS_KEY and CONTABO_SECRET_KEY required")
        
        self.s3 = boto3.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4')
        )
    
    def list_buckets(self) -> List[Dict[str, Any]]:
        """List all buckets."""
        response = self.s3.list_buckets()
        return [{"name": b["Name"], "created": b["CreationDate"].isoformat()} 
                for b in response.get("Buckets", [])]
    
    def list_objects(self, bucket: Optional[str] = None, prefix: str = "",
                     max_keys: int = 1000) -> List[Dict[str, Any]]:
        """List objects in bucket."""
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name required - set CONTABO_BUCKET or pass --bucket")
        
        response = self.s3.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
            MaxKeys=max_keys
        )
        
        objects = []
        for obj in response.get("Contents", []):
            objects.append({
                "key": obj["Key"],
                "size": obj["Size"],
                "modified": obj["LastModified"].isoformat(),
                "etag": obj["ETag"].strip('"')
            })
        return objects
    
    def upload_file(self, local_path: str, remote_key: str, 
                    bucket: Optional[str] = None) -> dict:
        """Upload file to storage."""
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name required")
        
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Local file not found: {local_path}")
        
        self.s3.upload_file(local_path, bucket, remote_key)
        return {"success": True, "bucket": bucket, "key": remote_key}
    
    def download_file(self, remote_key: str, local_path: str,
                      bucket: Optional[str] = None) -> dict:
        """Download file from storage."""
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name required")
        
        self.s3.download_file(bucket, remote_key, local_path)
        return {"success": True, "downloaded": local_path}
    
    def delete_object(self, remote_key: str, bucket: Optional[str] = None) -> dict:
        """Delete object from storage."""
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name required")
        
        self.s3.delete_object(Bucket=bucket, Key=remote_key)
        return {"success": True, "deleted": remote_key}
    
    def delete_objects(self, keys: List[str], bucket: Optional[str] = None) -> dict:
        """Delete multiple objects."""
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name required")
        
        delete_dict = {"Objects": [{"Key": k} for k in keys]}
        response = self.s3.delete_objects(Bucket=bucket, Delete=delete_dict)
        return {
            "success": True,
            "deleted": [d["Key"] for d in response.get("Deleted", [])],
            "errors": response.get("Errors", [])
        }
    
    def get_presigned_url(self, remote_key: str, expiry: int = 3600,
                          bucket: Optional[str] = None) -> str:
        """Generate presigned URL for object access."""
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name required")
        
        url = self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': remote_key},
            ExpiresIn=expiry
        )
        return url
    
    def get_object_info(self, remote_key: str, bucket: Optional[str] = None) -> dict:
        """Get object metadata."""
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name required")
        
        response = self.s3.head_object(Bucket=bucket, Key=remote_key)
        return {
            "key": remote_key,
            "size": response["ContentLength"],
            "modified": response["LastModified"].isoformat(),
            "content_type": response.get("ContentType", "unknown"),
            "etag": response["ETag"].strip('"')
        }
    
    def copy_object(self, source_key: str, dest_key: str,
                    source_bucket: Optional[str] = None,
                    dest_bucket: Optional[str] = None) -> dict:
        """Copy object within or between buckets."""
        source_bucket = source_bucket or self.bucket
        dest_bucket = dest_bucket or self.bucket
        
        if not source_bucket or not dest_bucket:
            raise ValueError("Bucket names required")
        
        copy_source = {"Bucket": source_bucket, "Key": source_key}
        self.s3.copy_object(
            CopySource=copy_source,
            Bucket=dest_bucket,
            Key=dest_key
        )
        return {"success": True, "copied_to": f"{dest_bucket}/{dest_key}"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Contabo Object Storage Management")
    parser.add_argument("--bucket", help="Override bucket name")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # List buckets
    subparsers.add_parser("buckets", help="List all buckets")
    
    # List objects
    list_parser = subparsers.add_parser("list", help="List objects in bucket")
    list_parser.add_argument("--prefix", default="", help="Filter by prefix")
    list_parser.add_argument("--max", type=int, default=1000, help="Max results")
    
    # Upload
    upload_parser = subparsers.add_parser("upload", help="Upload file")
    upload_parser.add_argument("local", help="Local file path")
    upload_parser.add_argument("remote", help="Remote key/path")
    
    # Download
    download_parser = subparsers.add_parser("download", help="Download file")
    download_parser.add_argument("remote", help="Remote key/path")
    download_parser.add_argument("local", help="Local file path")
    
    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete object(s)")
    delete_parser.add_argument("keys", nargs="+", help="Remote key(s) to delete")
    
    # Presign
    presign_parser = subparsers.add_parser("presign", help="Generate presigned URL")
    presign_parser.add_argument("key", help="Remote key")
    presign_parser.add_argument("--expiry", type=int, default=3600, help="Expiry seconds")
    
    # Info
    info_parser = subparsers.add_parser("info", help="Get object info")
    info_parser.add_argument("key", help="Remote key")
    
    # Copy
    copy_parser = subparsers.add_parser("copy", help="Copy object")
    copy_parser.add_argument("source", help="Source key")
    copy_parser.add_argument("dest", help="Destination key")
    copy_parser.add_argument("--dest-bucket", help="Destination bucket")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        storage = ContaboStorage()
        bucket = args.bucket if hasattr(args, 'bucket') else None
        result = None
        
        if args.command == "buckets":
            result = storage.list_buckets()
        
        elif args.command == "list":
            result = storage.list_objects(bucket, args.prefix, args.max)
        
        elif args.command == "upload":
            result = storage.upload_file(args.local, args.remote, bucket)
        
        elif args.command == "download":
            result = storage.download_file(args.remote, args.local, bucket)
        
        elif args.command == "delete":
            if len(args.keys) == 1:
                result = storage.delete_object(args.keys[0], bucket)
            else:
                result = storage.delete_objects(args.keys, bucket)
        
        elif args.command == "presign":
            url = storage.get_presigned_url(args.key, args.expiry, bucket)
            result = {"url": url, "expires_in": args.expiry}
        
        elif args.command == "info":
            result = storage.get_object_info(args.key, bucket)
        
        elif args.command == "copy":
            result = storage.copy_object(
                args.source, args.dest, 
                bucket, args.dest_bucket or bucket
            )
        
        if result is not None:
            if args.json or isinstance(result, (list, dict)):
                print(json.dumps(result, indent=2))
            else:
                print(result)
            sys.exit(0)
        
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except ClientError as e:
        print(f"S3 error: {e.response['Error']['Message']}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
