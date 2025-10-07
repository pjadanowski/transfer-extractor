# Get Transfer - Log Processor

A Python application to download and process transfer logs from SSH server, extract XML responses, and format them nicely.

## Features

- 🔐 SSH connection using SSH keys (automatic detection or specify key file)
- 🔍 Search for log files by alias prefix (e.g., zurich.log.*, axa.log.*)
- 📥 Download files with automatic decompression (gzip and zstd support)
- 🎯 Extract XML from the second line containing "Response:" in log files
- ✨ Format and save XML with proper indentation
- 💻 Easy-to-use command-line interface

## Installation

```bash
# Install dependencies
uv sync

# Or using pip
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python main.py --alias zurich --identity "1235435zvcxvsdf"
```

### Advanced Usage
```bash
python main.py \
  --hostname transfer01.live.bipro.demv.systems \
  --username developer \
  --log-dir /var/www/bipro-transfer/current/logs \
  --alias zurich \
  --identity "1235435zvcxvsdf" \
  --output-dir ./downloads \
  --xml-output extracted_response.xml
```

### Using SSH Key Authentication
```bash
# With specific SSH key
python main.py \
  --key-file ~/.ssh/id_rsa \
  --alias axa \
  --identity "your-identity-string"

# Using default SSH keys (automatic detection)
python main.py --alias zurich --identity "abc123"
```

## Options

- `--hostname`: SSH server hostname (default: transfer01.live.bipro.demv.systems)
- `--username`: SSH username (default: developer)
- `--key-file`: Path to SSH private key file (optional - will try default keys if not provided)
- `--log-dir`: Remote log directory path (default: /var/www/bipro-transfer/current/logs)
- `--alias`: File name prefix to search for (e.g., "zurich" for zurich.log.* files) (required)
- `--identity`: Identity string to search for in log files (required)
- `--output-dir`: Local directory for downloads (default: ./downloads)
- `--xml-output`: Output filename for extracted XML (default: extracted_response.xml)

## How It Works

1. **SSH Connection**: Connects to the specified server using SSH keys (tries default keys or specified key file)
2. **File Search**: Searches for files matching the alias pattern (e.g., `zurich.log.*`) in the log directory
3. **Content Search**: Checks each matching file for the specified identity string
4. **Download**: Downloads matching files to local machine
5. **Decompression**: Automatically decompresses gzipped (.gz) and zstandard (.zst) files
6. **XML Extraction**: Finds the second line containing "Response:" and extracts clean XML SOAP envelope
7. **Formatting**: Formats the XML with proper indentation and saves to file

## Output

- Downloaded log files are saved to `./downloads/` (or specified directory)
- Extracted and formatted XML files are saved to `./downloads/extracted/` subdirectory
- XML files are named with the original log file prefix (e.g., `jan.log.1_extracted_response.xml`)
- If XML formatting fails, raw content is saved with `raw_` prefix

## Example

```bash
$ python main.py --alias jan --identity "11570475" --username=pjadanowski

🚀 Starting Transfer Log Processor
Target server: pjadanowski@transfer01.live.bipro.demv.systems
Log directory: /var/www/bipro-transfer/current/logs
File alias: jan
File pattern: jan\.log.*
Identity string: 11570475
--------------------------------------------------
Connecting to transfer01.live.bipro.demv.systems using default SSH keys...
✅ SSH connection established successfully!
Searching in directory: /var/www/bipro-transfer/current/logs
File pattern: jan\.log.*
Search string: 11570475
Found 33 files matching pattern: ['jan.log.13.zst', 'jan.log.8.zst', 'jan.log.7.zst', ...]
✅ Found string in: jan.log.1.zst
❌ String not found in: jan.log
❌ String not found in: jan.log.2.zst
...
✅ Found 1 matching file(s)

📁 Processing: /var/www/bipro-transfer/current/logs/jan.log.1.zst
Downloading /var/www/bipro-transfer/current/logs/jan.log.1.zst to downloads/jan.log.1.zst
✅ File downloaded and decompressed (zstd): downloads/jan.log.1
Found 312 lines with 'Response:'
Processing line 4
✅ Found XML content (10684 characters)
✅ Formatted XML saved to: jan.log.1_extracted_response.xml
✅ Successfully processed /var/www/bipro-transfer/current/logs/jan.log.1.zst

🎉 Processing completed!
SSH connection closed.
```

## Sample Output

The extracted XML file (`jan.log.1_extracted_response.xml`) will contain a cleanly formatted SOAP envelope:

```xml
<?xml version='1.0' encoding='utf-8'?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <xf:getShipmentResponse xmlns:xf="http://www.bipro.net/namespace/transfer">
      <xf:Response xmlns:allg="http://www.bipro.net/namespace/allgemein" 
                   xmlns:basis="http://www.bipro.net/namespace/basis" 
                   xmlns:nac="http://www.bipro.net/namespace/nachrichten">
        <nac:BiPROVersion>2.5.0.1.0</nac:BiPROVersion>
        <nac:Status>
          <nac:ProzessID>getShipment_2.5.0.1.0</nac:ProzessID>
          <nac:Zeitstempel>2025-09-18T08:10:04</nac:Zeitstempel>
          <nac:StatusID>OK</nac:StatusID>
          <nac:Gueltigkeitsende>2028-09-13</nac:Gueltigkeitsende>
          <nac:Schwebe>false</nac:Schwebe>
          <nac:Meldung>
            <nac:ArtID>Hinweis</nac:ArtID>
            <nac:MeldungID>04000</nac:MeldungID>
            <nac:Text>Transferprozess erfolgreich</nac:Text>
          </nac:Meldung>
        </nac:Status>
        <xf:Lieferung>
          <xf:ID>11570438</xf:ID>
          <xf:ArtDerLieferung>1002</xf:ArtDerLieferung>
          <xf:EnthaeltNurDaten>false</xf:EnthaeltNurDaten>
          <xf:AnzahlTransfers>4</xf:AnzahlTransfers>
        </xf:Lieferung>
      </xf:Response>
    </xf:getShipmentResponse>
  </soap:Body>
</soap:Envelope>
```