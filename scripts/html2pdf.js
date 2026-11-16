// Print a standalone HTML file (MathML math) to PDF with headless Chromium (Playwright).
// usage: node scripts/html2pdf.js in.html out.pdf
const { chromium } = require('playwright');
(async () => {
  const [inp, out] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + require('path').resolve(inp), { waitUntil: 'load' });
  await page.pdf({ path: out, format: 'A4', printBackground: true,
    margin: { top: '22mm', bottom: '22mm', left: '22mm', right: '22mm' },
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;"><span class="pageNumber"></span></div>' });
  await browser.close();
})();
