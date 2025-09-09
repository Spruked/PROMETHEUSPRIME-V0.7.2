# Certsig Certificate Generator

This project generates blockchain-backed certificate PDFs for Promethean AI entities. It uses Node.js and pdf-lib to create professional certificates with embedded QR codes and serial tracking.

## Features
- Loads certificate data from a JSON config file
- Assigns unique serial numbers from a CSV register
- Embeds images and QR codes into a two-page PDF
- Saves certificates to a user-specific folder
- Command-line operation (no UI)

## Folder Structure
```
Certsig/
  certificate-generator.js      # Main script
  constants.js                 # Font sizes, colors, page dimensions
  certificate-config.json      # Certificate data (edit for each certificate)
  serial-register.csv          # Serial number register
  proprime_logo.png            # Logo image
  seal.png                     # Seal image
```

## Setup
1. Install Node.js (v18+ recommended)
2. Run `npm install pdf-lib qrcode date-fns dotenv`
3. Ensure `.env` file exists in parent folder with:
   ```
   CERT_CONFIG_FILE=certificate-config.json
   SERIAL_REGISTER_FILE=serial-register.csv
   IMAGE_ASSETS_DIR=.
   ```
4. Add required images and config files to the Certsig folder.

## Usage
From the `Certsig` folder, run:
```
node certificate-generator.js
```
The generated PDF will be saved in a folder named `<userId>_certificates`.

## Customization
- Edit `certificate-config.json` for each certificate
- Add more serials to `serial-register.csv` as needed
- Update images for branding

## Troubleshooting
- Ensure all required files exist in the folder
- Check `.env` variable paths
- Review error messages for missing files or data

## License
MIT
