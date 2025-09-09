// server.js
const express = require('express');
const path = require('path');
const fs = require('fs').promises;

const { generateCertificate } = require('./certificate-generator');

const app = express();

app.use(express.urlencoded({ extended: true }));

app.use(express.static('public'));

app.post('/generate', async (req, res) => {
    try {
        const formData = req.body;
        
        // Pass the form data directly to your certificate generation function
        const pdfPath = await generateCertificate(formData);

        res.download(pdfPath, (err) => {
            if (err) {
                console.error("Error sending PDF:", err);
            }
            fs.unlink(pdfPath).catch(console.error);
        });
        
    } catch (error) {
        console.error("Error in /generate route:", error);
        res.status(500).send("An error occurred during certificate generation.");
    }
});

const port = 3000;
app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});
