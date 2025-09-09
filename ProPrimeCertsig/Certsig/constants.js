// constants.js
const { rgb } = require("pdf-lib");

module.exports = {
  FONT_SIZES: {
    TITLE: 24, // Larger title font
    SUBTITLE: 14,
    HEADER: 18, // Larger header font
    FIELD: 12, // Slightly larger field font
    BODY: 10,
    SIGNATURE: 11,
    SIGNATURE_NAME: 10,
  },
  COLORS: {
    BORDER: rgb(0.1, 0.1, 0.1),
    WATERMARK: rgb(0.8, 0.8, 0.8),
    DARK_TEXT: rgb(0.1, 0.1, 0.1),
  },
  PAGE_DIMENSIONS: [792, 612], // Width, Height
};