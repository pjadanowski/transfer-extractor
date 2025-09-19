#!/usr/bin/env python3
"""
Application to download and process transfer logs from SSH server.

This application connects to a remote SSH server, searches for log files
containing specific strings, downloads them, and extracts formatted XML content.
"""

import os
import re
import gzip
import tempfile
from pathlib import Path
from typing import Optional, List, Tuple

import click
import paramiko
from lxml import etree


class TransferLogProcessor:
    """Main class for processing transfer logs from SSH server."""
    
    def __init__(self, hostname: str, username: str, key_filename: Optional[str] = None):
        """Initialize SSH connection parameters."""
        self.hostname = hostname
        self.username = username
        self.key_filename = key_filename
        self.ssh = None
        self.sftp = None
        
    def connect(self) -> bool:
        """Establish SSH connection to the server using SSH keys."""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.key_filename and Path(self.key_filename).exists():
                click.echo(f"Connecting to {self.hostname} using key file: {self.key_filename}")
                self.ssh.connect(
                    hostname=self.hostname,
                    username=self.username,
                    key_filename=self.key_filename
                )
            else:
                click.echo(f"Connecting to {self.hostname} using default SSH keys...")
                self.ssh.connect(
                    hostname=self.hostname,
                    username=self.username,
                    look_for_keys=True
                )
            
            self.sftp = self.ssh.open_sftp()
            click.echo("✅ SSH connection established successfully!")
            return True
            
        except Exception as e:
            click.echo(f"❌ SSH connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close SSH and SFTP connections."""
        if self.sftp:
            self.sftp.close()
        if self.ssh:
            self.ssh.close()
        click.echo("SSH connection closed.")
    
    def search_log_files(self, log_dir: str, file_pattern: str, search_string: str) -> List[str]:
        """Search for log files matching pattern and containing search string."""
        try:
            click.echo(f"Searching in directory: {log_dir}")
            click.echo(f"File pattern: {file_pattern}")
            click.echo(f"Search string: {search_string}")
            
            # List files in the log directory
            files = self.sftp.listdir(log_dir)
            matching_files = []
            
            # Filter files by pattern (e.g., jan.log*)
            pattern_files = [f for f in files if re.match(file_pattern, f)]
            click.echo(f"Found {len(pattern_files)} files matching pattern: {pattern_files}")
            
            # Search for the string in matching files
            for filename in pattern_files:
                file_path = f"{log_dir}/{filename}"
                if self._file_contains_string(file_path, search_string):
                    matching_files.append(file_path)
                    click.echo(f"✅ Found string in: {filename}")
                else:
                    click.echo(f"❌ String not found in: {filename}\n")
            
            return matching_files
            
        except Exception as e:
            click.echo(f"❌ Error searching log files: {e}")
            return []
    
    def _file_contains_string(self, file_path: str, search_string: str) -> bool:
        """Check if a file contains the search string."""
        try:
            filename = Path(file_path).name
            
            # Handle different file types
            if filename.endswith('.zst'):
                return self._search_in_zst_file(file_path, search_string)
            elif filename.endswith('.gz'):
                return self._search_in_gz_file(file_path, search_string)
            else:
                return self._search_in_text_file(file_path, search_string)
                
        except Exception as e:
            click.echo(f"Warning: Could not read {file_path}: {e}")
            return False
    
    def _search_in_text_file(self, file_path: str, search_string: str) -> bool:
        """Search for string in a regular text file."""
        try:
            # Download and try binary approach to avoid paramiko encoding issues
            import tempfile
            with tempfile.NamedTemporaryFile() as temp_file:
                self.sftp.get(file_path, temp_file.name)
                
                with open(temp_file.name, 'rb') as f:
                    data = f.read()
                
                content = self._decode_with_fallback(data, file_path)
                if content is None:
                    return False
                    
                return search_string in content
                
        except Exception as e:
            click.echo(f"Warning: Error reading text file {file_path}: {e}")
            return False
    
    def _search_in_gz_file(self, file_path: str, search_string: str) -> bool:
        """Search for string in a gzipped file."""
        try:
            import tempfile
            import gzip
            
            # Download file to temporary location and decompress
            with tempfile.NamedTemporaryFile() as temp_file:
                self.sftp.get(file_path, temp_file.name)
                
                with gzip.open(temp_file.name, 'rb') as gz_file:
                    decompressed_data = gz_file.read()
                
                # Try different encodings to decode the content
                content = self._decode_with_fallback(decompressed_data, file_path)
                if content is None:
                    return False
                
                # Search for the string  
                return search_string in content
                    
        except Exception as e:
            click.echo(f"Warning: Error reading gzip file {file_path}: {e}")
            return False
    
    def _search_in_zst_file(self, file_path: str, search_string: str) -> bool:
        """Search for string in a zstandard compressed file."""
        try:
            import tempfile
            import pyzstd
            
            # Download file to temporary location and decompress
            with tempfile.NamedTemporaryFile() as temp_file:
                self.sftp.get(file_path, temp_file.name)
                
                with open(temp_file.name, 'rb') as compressed_file:
                    compressed_data = compressed_file.read()
                
                # Decompress the data
                decompressed_data = pyzstd.decompress(compressed_data)
                
                # Try different encodings to decode the content
                content = self._decode_with_fallback(decompressed_data, file_path)
                if content is None:
                    return False
                
                # Search for the string
                return search_string in content
                
        except Exception as e:
            click.echo(f"Warning: Error reading zst file {file_path}: {e}")
            return False
    
    def _decode_with_fallback(self, data: bytes, file_path: str) -> str:
        """Try to decode bytes with multiple encodings."""
        encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'ascii']
        
        for encoding in encodings_to_try:
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
        
        # If all encodings fail, try with error handling
        try:
            return data.decode('utf-8', errors='ignore')
        except Exception as e:
            click.echo(f"Warning: Could not decode {file_path} with any encoding: {e}")
            return None
    
    def download_file(self, remote_path: str, local_dir: str = "./downloads") -> Optional[str]:
        """Download a file from the remote server."""
        try:
            # Create local directory if it doesn't exist
            Path(local_dir).mkdir(parents=True, exist_ok=True)
            
            # Extract filename from remote path
            filename = Path(remote_path).name
            local_path = Path(local_dir) / filename
            
            click.echo(f"Downloading {remote_path} to {local_path}")
            self.sftp.get(remote_path, str(local_path))
            
            # Check if file is compressed and decompress if needed
            if filename.endswith('.gz'):
                decompressed_path = self._decompress_gzip_file(str(local_path))
                if decompressed_path:
                    click.echo(f"✅ File downloaded and decompressed (gzip): {decompressed_path}")
                    return decompressed_path
            elif filename.endswith('.zst'):
                decompressed_path = self._decompress_zst_file(str(local_path))
                if decompressed_path:
                    click.echo(f"✅ File downloaded and decompressed (zstd): {decompressed_path}")
                    return decompressed_path
            
            click.echo(f"✅ File downloaded: {local_path}")
            return str(local_path)
            
        except Exception as e:
            click.echo(f"❌ Error downloading file: {e}")
            return None
    
    def _decompress_gzip_file(self, compressed_path: str) -> Optional[str]:
        """Decompress a gzipped file."""
        try:
            decompressed_path = compressed_path[:-3]  # Remove .gz extension
            
            with gzip.open(compressed_path, 'rt', encoding='utf-8') as gz_file:
                with open(decompressed_path, 'w', encoding='utf-8') as out_file:
                    out_file.write(gz_file.read())
            
            # Remove the compressed file
            os.remove(compressed_path)
            return decompressed_path
            
        except Exception as e:
            click.echo(f"❌ Error decompressing gzip file: {e}")
            return None
    
    def _decompress_zst_file(self, compressed_path: str) -> Optional[str]:
        """Decompress a zstandard (.zst) file."""
        try:
            import subprocess
            
            # Remove .zst extension for output file
            decompressed_path = compressed_path[:-4]
            
            # Use zstd command-line tool to decompress
            result = subprocess.run(
                ['zstd', '-d', compressed_path, '-o', decompressed_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # If zstd command is not available, try using pyzstd if available
                try:
                    import pyzstd
                    with open(compressed_path, 'rb') as f_in:
                        compressed_data = f_in.read()
                    
                    decompressed_data = pyzstd.decompress(compressed_data)
                    
                    with open(decompressed_path, 'wb') as f_out:
                        f_out.write(decompressed_data)
                    
                except ImportError:
                    click.echo("❌ zstd tool not found and pyzstd not installed. Please install zstd or pyzstd.")
                    return None
            
            # Remove the compressed file
            os.remove(compressed_path)
            return decompressed_path
            
        except Exception as e:
            click.echo(f"❌ Error decompressing zstd file: {e}")
            return None
    
    def extract_second_response_xml(self, file_path: str) -> Optional[str]:
        """Extract XML from the second line containing 'Response:' in the file."""
        try:
            # Try to read the file with different encodings
            content = None
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, try binary mode with fallback decoding
            if content is None:
                with open(file_path, 'rb') as file:
                    data = file.read()
                content = self._decode_with_fallback(data, file_path)
                if content is None:
                    click.echo("❌ Could not decode file with any encoding")
                    return None
            
            # Split into lines and find lines containing 'Response:'
            lines = content.split('\n')
            response_lines = []
            
            for i, line in enumerate(lines):
                if 'Response:' in line:
                    response_lines.append((i+1, line))
            
            if len(response_lines) < 2:
                click.echo(f"❌ Found only {len(response_lines)} line(s) with 'Response:', need at least 2")
                return None
            
            click.echo(f"Found {len(response_lines)} lines with 'Response:'")
            
            # Get the second line with 'Response:'
            second_response_line_num, second_response_line = response_lines[1]
            click.echo(f"Processing line {second_response_line_num}")
            
            # Look for XML content in this line - after the log timestamp
            # XML usually starts with <?xml or directly with <soap: or similar
            xml_patterns = [
                r'<\?xml.*?</soap:Envelope>',  # Full XML with SOAP envelope
                r'<\?xml.*?</soapenv:Envelope>',  # Full XML with soapenv envelope
                r'<soap:Envelope.*?</soap:Envelope>',  # SOAP envelope without XML declaration
                r'<soapenv:Envelope.*?</soapenv:Envelope>',  # SOAP envelope with soapenv prefix
            ]
            
            for pattern in xml_patterns:
                matches = re.findall(pattern, second_response_line, re.DOTALL)
                if matches:
                    # Take the first match
                    match = matches[0]
                    if len(match.strip()) > 100:  # Minimum XML content length
                        click.echo(f"✅ Found XML content ({len(match)} characters)")
                        return match.strip()
            
            # Fallback: try to extract everything between first < and last > in the line
            start_xml = second_response_line.find('<')
            if start_xml != -1:
                xml_part = second_response_line[start_xml:]
                
                # Look for the end of the SOAP envelope to avoid extra content
                soap_end_patterns = [
                    '</soap:Envelope>',
                    '</soapenv:Envelope>',
                    '</Envelope>'
                ]
                
                end_pos = -1
                for pattern in soap_end_patterns:
                    pos = xml_part.find(pattern)
                    if pos != -1:
                        end_pos = pos + len(pattern)
                        break
                
                if end_pos != -1:
                    xml_content = xml_part[:end_pos]
                else:
                    # Fallback to finding last > if no envelope end found
                    end_xml = xml_part.rfind('>')
                    if end_xml != -1:
                        xml_content = xml_part[:end_xml+1]
                    else:
                        xml_content = xml_part
                
                if len(xml_content) > 100:
                    click.echo(f"✅ Found XML-like content ({len(xml_content)} characters)")
                    return xml_content
            
            click.echo("❌ No XML content found in second Response line")
            return None
            
        except Exception as e:
            click.echo(f"❌ Error extracting XML: {e}")
            return None
    
    def format_and_save_xml(self, xml_content: str, output_file: str = "extracted_response.xml") -> bool:
        """Format XML content nicely and save to file."""
        try:
            # Parse and format the XML
            try:
                # Try parsing as XML
                root = etree.fromstring(xml_content.encode('utf-8'))
                formatted_xml = etree.tostring(
                    root, 
                    pretty_print=True, 
                    xml_declaration=True, 
                    encoding='utf-8'
                ).decode('utf-8')
            except etree.XMLSyntaxError:
                # If parsing fails, try to clean up the XML and retry
                cleaned_xml = self._clean_xml_content(xml_content)
                root = etree.fromstring(cleaned_xml.encode('utf-8'))
                formatted_xml = etree.tostring(
                    root, 
                    pretty_print=True, 
                    xml_declaration=True, 
                    encoding='utf-8'
                ).decode('utf-8')
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(formatted_xml)
            
            click.echo(f"✅ Formatted XML saved to: {output_file}")
            return True
            
        except Exception as e:
            click.echo(f"❌ Error formatting XML: {e}")
            # Save raw content as fallback
            try:
                with open(f"raw_{output_file}", 'w', encoding='utf-8') as file:
                    file.write(xml_content)
                click.echo(f"⚠️  Saved raw content to: raw_{output_file}")
                return True
            except Exception as e2:
                click.echo(f"❌ Error saving raw content: {e2}")
                return False
    
    def _clean_xml_content(self, xml_content: str) -> str:
        """Clean XML content to make it parseable."""
        # Remove common issues that might prevent parsing
        cleaned = xml_content.strip()
        
        # Ensure it starts with XML declaration or root element
        if not cleaned.startswith('<?xml') and not cleaned.startswith('<'):
            # Find the first < character
            start_pos = cleaned.find('<')
            if start_pos > 0:
                cleaned = cleaned[start_pos:]
        
        return cleaned


@click.command()
@click.option('--hostname', default='transfer01.live.bipro.demv.systems', 
              help='SSH server hostname')
@click.option('--username', default='developer', 
              help='SSH username')
@click.option('--key-file', type=click.Path(exists=True), 
              help='Path to SSH private key file (if not provided, will try default SSH keys)')
@click.option('--log-dir', default='/var/www/bipro-transfer/current/logs', 
              help='Remote log directory path')
@click.option('--alias', required=True, 
              help='File name prefix to search for (e.g., "zurich" for zurich.log.*)')
@click.option('--identity', required=True, 
              help='Identity string to search for in log files')
@click.option('--output-dir', default='./downloads', 
              help='Local directory to save downloaded files')
@click.option('--xml-output', default='extracted_response.xml', 
              help='Output filename for extracted XML')
def main(hostname, username, key_file, log_dir, alias, 
         identity, output_dir, xml_output):
    """
    Download and process transfer logs from SSH server.
    
    This application connects to a remote SSH server using SSH keys, searches for log files
    containing specific identity strings, downloads them, and extracts formatted XML content.
    
    Example usage:
    python main.py --alias zurich --identity "1235435zvcxvsdf"
    python main.py --key-file ~/.ssh/my_key --alias axa --identity "abc123"
    """
    # Generate file pattern from alias
    file_pattern = rf'{re.escape(alias)}\.log.*'
    
    click.echo("🚀 Starting Transfer Log Processor")
    click.echo(f"Target server: {username}@{hostname}")
    click.echo(f"Log directory: {log_dir}")
    click.echo(f"File alias: {alias}")
    click.echo(f"File pattern: {file_pattern}")
    click.echo(f"Identity string: {identity}")
    click.echo("-" * 50)
    
    # Initialize processor
    processor = TransferLogProcessor(
        hostname=hostname,
        username=username,
        key_filename=key_file
    )
    
    try:
        # Step 1: Connect to SSH server
        if not processor.connect():
            return 1
        
        # Step 2: Search for log files
        matching_files = processor.search_log_files(log_dir, file_pattern, identity)
        
        if not matching_files:
            click.echo("❌ No matching files found!")
            return 1
        
        click.echo(f"✅ Found {len(matching_files)} matching file(s)")
        
        # Step 3: Process each matching file
        for file_path in matching_files:
            click.echo(f"\n📁 Processing: {file_path}")
            
            # Download file
            local_file = processor.download_file(file_path, output_dir)
            if not local_file:
                click.echo(f"❌ Failed to download {file_path}")
                continue
            
            # Extract XML from second Response
            xml_content = processor.extract_second_response_xml(local_file)
            if not xml_content:
                click.echo(f"❌ Failed to extract XML from {local_file}")
                continue
            
            # Format and save XML
            output_filename = f"{Path(file_path).stem}_{xml_output}"
            if processor.format_and_save_xml(xml_content, output_filename):
                click.echo(f"✅ Successfully processed {file_path}")
            else:
                click.echo(f"❌ Failed to save XML from {file_path}")
        
        click.echo("\n🎉 Processing completed!")
        return 0
        
    except KeyboardInterrupt:
        click.echo("\n⚠️  Process interrupted by user")
        return 1
    except Exception as e:
        click.echo(f"\n❌ Unexpected error: {e}")
        return 1
    finally:
        processor.disconnect()


if __name__ == "__main__":
    exit(main())
