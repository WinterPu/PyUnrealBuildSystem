#!/usr/bin/env python3
import plistlib
import hashlib
import binascii
import re
import subprocess
import argparse
from pathlib import Path


## TBD(WinterPu):
## 1. Impl update ios cert json config 

## Get mobileprovision cert data sha-1 as "provisioning_profile" value
## 1. Step 01: security cms -D -i /path_mobileprovision
## 2. Step 02: get <data> in <DeveloperCertificates> (data without <data> tag), and save it as a [cert.b64] file
## 2. Step 03: base64 -D -i cert.b64 | openssl x509 -inform der -fingerprint -sha1

def extract_and_hash_certificates(mobileprovision_path):
    """
    Extract DeveloperCertificates from a .mobileprovision file and calculate SHA-1 hash
    for each certificate.
    """
    # Convert to Path object if it's not already
    mobileprovision_path = Path(mobileprovision_path)
    
    print(mobileprovision_path)
    # Check if the file exists
    if not mobileprovision_path.exists():
        print(f"Error: File {mobileprovision_path} does not exist")
        return

    try:
        # Method 1: Use security cms to extract the plist
        try:
            cmd = ['security', 'cms', '-D', '-i', str(mobileprovision_path)]
            plist_xml = subprocess.check_output(cmd)
            plist_data = plistlib.loads(plist_xml)
        except (subprocess.SubprocessError, plistlib.InvalidFileException):
            # Method 2: Try direct parsing if security cms fails
            with mobileprovision_path.open('rb') as f:
                content = f.read()
                # Find the start of the XML content
                start = content.find(b'<?xml')
                if start == -1:
                    raise ValueError("Could not find XML content in mobileprovision file")
                # Find the end of the plist
                end = content.find(b'</plist>') + 8  # 8 is length of '</plist>'
                plist_xml = content[start:end]
                plist_data = plistlib.loads(plist_xml)

        # Extract UUID
        uuid = plist_data.get('UUID', '')
        print(f"UUID: {uuid}")
        
        # Extract developer certificates
        developer_certs = plist_data.get('DeveloperCertificates', [])
        
        if not developer_certs:
            print("No DeveloperCertificates found in the provisioning profile")
            return

        print(f"Found {len(developer_certs)} developer certificate(s)")
        
        for i, cert_data in enumerate(developer_certs):
            # Calculate SHA-1 hash
            sha1_hash = hashlib.sha1(cert_data).hexdigest()
            print(f"Certificate {i+1} SHA-1 hash: {sha1_hash.upper()}")
            
    except Exception as e:
        print(f"Error processing mobileprovision file: {e}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Extract DeveloperCertificates from a mobileprovision file and calculate SHA-1 hashes'
    )
    
    # Add arguments
    parser.add_argument(
        'profile_path', 
        type=Path,  # Now accepts Path objects directly
        help='Path to the .mobileprovision file'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Process the mobileprovision file
    extract_and_hash_certificates(args.profile_path)

if __name__ == "__main__":
    main()