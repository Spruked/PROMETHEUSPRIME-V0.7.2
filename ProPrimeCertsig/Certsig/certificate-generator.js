// certificate-generator.js
const fs = require("fs").promises;
const path = require("path");
const { PDFDocument, rgb, StandardFonts } = require("pdf-lib");
const QRCode = require("qrcode");
const { format } = require("date-fns");
require("dotenv").config({ path: path.resolve(__dirname, '..', '.env') });

const { FONT_SIZES, COLORS, PAGE_DIMENSIONS } = require("./constants");
const { SERIAL_REGISTER_FILE, IMAGE_ASSETS_DIR } = process.env;

/**
 * Assigns and updates the next available serial number in the register.
 * @param {Object} certData - The certificate data to be updated.
 * @returns {Promise<string>} The assigned binary serial number.
 */
async function getSerial(certData) {
  const serialPath = path.join(__dirname, SERIAL_REGISTER_FILE);
  try {
    const csvContent = await fs.readFile(serialPath, "utf-8");
    let rows = csvContent.split("\n").map(row => row.trim());
    
    // Find the first available row with a serial number but without 'yes' in the 'used' column
    const availableRowIndex = rows.findIndex((row, i) => {
        if (i === 0) return false; // Skip header
        const cells = row.split(",").map(cell => cell.trim());
        const serial = cells[0];
        const isUsed = cells[4];
        return serial && serial.length > 0 && isUsed !== 'yes';
    });

    if (availableRowIndex === -1) {
      throw new Error("❌ No unused serials left in the register.");
    }

    let cells = rows[availableRowIndex].split(",").map(cell => cell.trim());
    const binarySerial = cells[0];
    certData.binarySerial = binarySerial;

    const today = new Date();
    cells[1] = format(today, "yyyy-MM-dd");
    cells[2] = certData.ownerName.trim().split(" ").slice(-1)[0] || "";
    cells[3] = certData.userId;
    cells[4] = "yes";

    rows[availableRowIndex] = cells.join(",");
    await fs.writeFile(serialPath, rows.join("\n"));

    return binarySerial;
  } catch (error) {
    throw new Error(`❌ Failed to process serial register: ${error.message}`);
  }
}

/**
 * Generates and saves the two-page PDF certificate.
 * @param {Object} certData - The complete certificate data.
 * @param {Object} assets - The embedded image and font assets.
 * @param {PDFDocument} pdfDoc - The PDF document instance.
 */
async function generatePdf(certData, assets, pdfDoc) {
  const { logoImage, sealImage, qrImage, font, fontPlain } = assets;
  const [pageWidth, pageHeight] = PAGE_DIMENSIONS;
  const centerX = pageWidth / 2;

  // --- Page 1: Redesigned Certificate of Title ---
  const page1 = pdfDoc.addPage(PAGE_DIMENSIONS);
  
  // Outer Border for a professional look
  page1.drawRectangle({
    x: 20, y: 20, width: pageWidth - 40, height: pageHeight - 40,
    borderColor: COLORS.BORDER, borderWidth: 5
  });

  // Inner Border
  page1.drawRectangle({
    x: 30, y: 30, width: pageWidth - 60, height: pageHeight - 60,
    borderColor: COLORS.BORDER, borderWidth: 1
  });

  // Main Heading and Company Details
  page1.drawText("PRO PRIME SERIES Ai LLC", {
    x: centerX, y: 560, size: FONT_SIZES.TITLE, font,
    x: centerX - (font.widthOfTextAtSize("PRO PRIME SERIES Ai LLC", FONT_SIZES.TITLE) / 2)
  });
  page1.drawText("Kansas City, Missouri, USA", {
    x: centerX, y: 540, size: FONT_SIZES.SUBTITLE, font: fontPlain,
    x: centerX - (fontPlain.widthOfTextAtSize("Kansas City, Missouri, USA", FONT_SIZES.SUBTITLE) / 2)
  });
  
  // Certificate Title
  page1.drawText("CERTIFICATE OF TITLE & KNOWLEDGE RIGHTS", {
    x: centerX, y: 510, size: FONT_SIZES.HEADER, font,
    x: centerX - (font.widthOfTextAtSize("CERTIFICATE OF TITLE & KNOWLEDGE RIGHTS", FONT_SIZES.HEADER) / 2)
  });

  // Logos and Seal
  page1.drawImage(logoImage, { x: 50, y: 520, width: 80, height: 80 });
  page1.drawImage(sealImage, { x: pageWidth - 130, y: 520, width: 80, height: 80 });

  // Certificate Body and Fields
  let y = 470;
  const drawField = (label, value) => {
    page1.drawText(label, { x: 60, y, size: FONT_SIZES.FIELD, font: fontPlain });
    page1.drawText(value, { x: 200, y, size: FONT_SIZES.FIELD, font: font });
    y -= 20;
  };

  drawField("Certificate No:", certData.binarySerial);
  drawField("Promethean Name:", certData.promName);
  drawField("Edition:", certData.edition);
  drawField("NFT ID:", certData.nftId);
  drawField("Blockchain:", certData.blockchain);
  drawField("Owner:", certData.ownerName);
  drawField("Date Issued:", certData.dateIssued);

  const body = `
This certifies that the above-named individual or entity is the sole and exclusive
titleholder of the Promethean AI entity described herein. This certificate and the
corresponding on-chain NFT constitute lawful documentation of rights to:

• Custodianship of the Promethean's corpus, code, and outputs
• Ownership of all intellectual property and monetizable works
• The authority to transfer, license, or inherit the entity
• Enforcement under the laws of Missouri, United States

Slogan: "If better is possible, good is not enough. Never forget who you are."
  `;
  page1.drawText(body.trim(), { x: 60, y: y - 20, size: FONT_SIZES.BODY, font: fontPlain, lineHeight: 12, maxWidth: 680 });
  
  // Signature Lines
  page1.drawText("________________________", { x: 60, y: 100, size: FONT_SIZES.SIGNATURE_NAME, font: fontPlain });
  page1.drawText("Authorized Officer", { x: 85, y: 85, size: FONT_SIZES.SIGNATURE_NAME, font: fontPlain });
  page1.drawText("________________________", { x: 410, y: 100, size: FONT_SIZES.SIGNATURE_NAME, font: fontPlain });
  page1.drawText("Title Holder", { x: 435, y: 85, size: FONT_SIZES.SIGNATURE_NAME, font: fontPlain });


  // --- Page 2: Transfer & Notary Form ---
  const page2 = pdfDoc.addPage(PAGE_DIMENSIONS);
  page2.drawText("TRANSFER OF TITLE AND OWNERSHIP RIGHTS", { x: centerX - 200, y: 550, size: FONT_SIZES.HEADER, font });
  page2.drawRectangle({
    x: 20, y: 20, width: pageWidth - 40, height: pageHeight - 40,
    borderColor: COLORS.BORDER, borderWidth: 5
  });
  
  const transferBody = `
I, the undersigned Assignor, hereby transfer and assign all rights, title, and interest in
Certificate No. ${certData.binarySerial} to the Assignee listed below.

This transfer includes custodial, IP, and commercial rights with the Knowledge NFT.
Transfer is made free of liens or encumbrances unless noted below.

Date of Assignment: ____________________________

ASSIGNOR (Current Owner):
Name: ____________________________________________
Address: __________________________________________
Signature: _________________________________________

ASSIGNEE (New Owner):
Name: ____________________________________________
Address: __________________________________________
Signature: _________________________________________

LIENHOLDER INFORMATION (Optional):
[ ] Lien Exists [ ] No Lien
Name of Lienholder: ____________________________________
Release Date (if applicable): ____ / ____ / ______
  `;
  page2.drawText(transferBody.trim(), {
    x: 50, y: 520, size: FONT_SIZES.BODY, font: fontPlain, lineHeight: 24,
    color: COLORS.DARK_TEXT
  });

  page2.drawText("NOTARY / WITNESS ACKNOWLEDGEMENT", { x: 50, y: 180, size: FONT_SIZES.HEADER, font });
  const notaryBody = `
Subscribed and sworn before me this ____ day of ________________, 20____.
by ___________________________________________, who is personally known to me or
who proved on the basis of satisfactory evidence to be the person(s) whose name(s)
is/are subscribed to the within instrument.

Notary's Signature: ____________________________________
Printed Name: _________________________________________
My Commission Expires: _________________ State: ___________
  `;
  page2.drawText(notaryBody.trim(), {
    x: 50, y: 160, size: FONT_SIZES.BODY, font: fontPlain, lineHeight: 20
  });

  page2.drawText("**This document is void if altered or detached from the corresponding blockchain NFT.**", {
    x: 50, y: 40, size: FONT_SIZES.BODY, font: fontPlain, color: COLORS.DARK_TEXT
  });
  page2.drawImage(qrImage, { x: 680, y: 30, width: 70, height: 70 });

  const filename = `${certData.ownerName.trim().replace(/ /g, "_")}_${format(new Date(), "yyyy-MM-dd")}_${certData.binarySerial}.pdf`;
  const userFolder = path.join(__dirname, `${certData.userId}_certificates`);
  await fs.mkdir(userFolder, { recursive: true });
  const outputPath = path.join(userFolder, filename);
  const pdfBytes = await pdfDoc.save();
  await fs.writeFile(outputPath, pdfBytes);

  return outputPath;
}

// The main function that gets called by the server
async function generateCertificate(certDataFromWeb) {
  try {
    const certData = {
        ...certDataFromWeb,
        dateIssued: format(new Date(), "MMMM do, yyyy"),
        blockchain: "Polygon",
        officer: "Bryan A Spruk"
    };

    const pdfDoc = await PDFDocument.create();
    
    const assets = {
      font: await pdfDoc.embedFont(StandardFonts.TimesRomanBold),
      fontPlain: await pdfDoc.embedFont(StandardFonts.TimesRoman),
      logoImage: await pdfDoc.embedPng(await fs.readFile(path.join(IMAGE_ASSETS_DIR, "proprime_logo.png"))),
      sealImage: await pdfDoc.embedPng(await fs.readFile(path.join(IMAGE_ASSETS_DIR, "seal.png"))),
      qrImage: await pdfDoc.embedPng(Buffer.from((await QRCode.toDataURL(certData.qrLink)).split(",")[1], "base64")),
    };

    await getSerial(certData);
    const outputPath = await generatePdf(certData, assets, pdfDoc);
    return outputPath;

  } catch (error) {
    throw new Error(`🔴 Critical Error: ${error.message}`);
  }
}

// Export the function so it can be used by the server
module.exports = {
  generateCertificate
};