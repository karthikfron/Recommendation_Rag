import puppeteer from "puppeteer";
import path from "path";
import { promises as fs } from "fs";

import { baseUrl, solutionsStartUrl, solutionTypes, startIndex, limit } from "./helper/const.js";

async function saveProduct(product) {
    console.log("Saving product:", product);

    try {
        // Ensure the directory exists
        const directory = path.join("pre-packaged-solutions");
        await fs.mkdir(directory, { recursive: true });

        // Use path.join to construct the file path and encode the title safely
        const safeTitle = encodeURIComponent(product.title || `product-${Date.now()}`);
        const filePath = path.join(directory, `${safeTitle}.json`);

        await fs.writeFile(filePath, JSON.stringify(product, null, 2), "utf-8");
        console.log(`Product saved as JSON: ${filePath}`);
    } catch (error) {
        console.error("Error saving product:", error);
    }
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', // 👈 your Chrome path
    headless: 'new', // optional, can be true/false
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
    const page = await browser.newPage();

    let currentIndex = startIndex;
    const maxIndex = 144; 

    while (currentIndex <= maxIndex) {
        const paginatedUrl = `${baseUrl}?start=${currentIndex}&type=${solutionTypes.PRE_PACKAGED}`;
        console.log(`Navigating to: ${paginatedUrl}`);

        await page.goto(paginatedUrl, { waitUntil: "networkidle2" });
        await page.setViewport({ width: 1080, height: 1024 });

        // Extract links for prepackaged solutions only
        const links = await page.evaluate((solutionsStartUrl) => {
            const elements = document.querySelectorAll("a");
            return Array.from(elements)
                .map(el => el.href)
                .filter(href => href.startsWith(solutionsStartUrl)); // Filter for prepackaged solutions
        }, solutionsStartUrl);

        console.info(`Found ${links.length} prepackaged product links on page starting at ${currentIndex}.`);

        await Promise.all(
            links.map(async (link) => {
                const productPage = await browser.newPage(); // Open a new page for each product
                await productPage.goto(link, { waitUntil: "networkidle2" });

                /* const printLinks = await productPage.evaluate(() => {
                    const elements = document.querySelectorAll("a");
                    return Array.from(elements)
                        .map(el => el.href)
                        .filter(href => href.includes("service.shl.com/docs"));
                })
                console.log(printLinks); */
                

                const product = await productPage.evaluate(() => {
                    const getText = (selector) => document.querySelector(selector)?.innerText.trim() || null;
                    const getLink = (selector) => document.querySelector(selector)?.href || null;

                    const rows = document.querySelectorAll(".product-catalogue-training-calendar__row.typ");

                    const productData = {
                        title: null,
                        description: null,
                        jobLevels: null,
                        languages: null,
                        assessmentLength: null,
                        productFactSheet: null,
                    };

                    rows.forEach(row => {
                        const heading = row.querySelector("h4")?.innerText.trim().toLowerCase();
                        const content = row.querySelector("p")?.innerText.trim();
                        
                        productData.title = getText("h1"); 

                        if (heading === "description") {
                            productData.description = content;
                        } else if (heading === "job levels") {
                            productData.jobLevels = content;
                        } else if (heading === "languages") {
                            productData.languages = content;
                        } else if (heading === "assessment length") {
                            productData.assessmentLength = content;
                        } 
                        /* else if (heading === "downloads") {
                            console.log(printLinks);
                            productData.productFactSheet = printLinks;
                        } */
                    });

                    /* // ✅ Moved inside: extract PDF links here itself */
    const pdfLinks = Array.from(document.querySelectorAll("a"))
        .map(el => el.href)
        .filter(href => href.includes("service.shl.com/docs"));

    productData.productFactSheet = pdfLinks;

    return productData;
                });

                console.log("Extracted product:", product);
                await saveProduct(product);
                await productPage.close();
            })
        );

        currentIndex += limit;
    }

    await browser.close();
})();