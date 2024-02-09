const fs = require("fs");
const puppeteer = require('puppeteer-extra');
 
// Add stealth plugin and use defaults 
const pluginStealth = require('puppeteer-extra-plugin-stealth');

// Use stealth 
puppeteer.use(pluginStealth())

const args = [
	'--no-sandbox',
	'--disable-setuid-sandbox',
	'disable-gpu', 
	'--disable-infobars', 
	'--disable-extensions', 
	'--ignore-certificate-errors',
	'--window-position=0,0',
	'--ignore-certifcate-errors',
	'--ignore-certifcate-errors-spki-list',
	'--proxy-server=http://113.208.119.142',
]

// Launch pupputeer-stealth 
puppeteer.launch({
	args : args,
	headless:false,
	ignoreDefaultArgs: ['--enable-automation'],
	executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
	defaultViewport: null,
	slowMo: 100,
	setTimeout: 10000,
	args: ['--start-maximized']
}).then(async browser => {

	const getText = async(xpath) => {
		let element = await page.$x(xpath)
		let text = await page.evaluate(el => el.textContent, element[0])
		return text.trim()
	};

	// use automatically opened tab
	const page = (await browser.pages())[0];

	const userAgents = [
		'Mozilla/5.0 (Linux; Android 10; CPH1931 Build/QKQ1.200209.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.138 Mobile Safari/537.36 Instagram 294.0.0.33.87 Android (29/10; 320dpi; 720x1456; OPPO; CPH1931; OP4B79L1; qcom; it_IT; 500160587)',
		'Mozilla/5.0 (iPhone; CPU iPhone OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/20H19 Instagram 305.0.0.16.118 (iPhone14,3; iOS 16_7; it_IT; it; scale=3.00; 1284x2778; 526608156)',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2829.12 Safari/537.36',
		'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36',
		'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
		'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
		'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36',
		'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
	]

	// set headers
	await page.setExtraHTTPHeaders({ 
		'user-agent': userAgents[(Math.floor(Math.random() * userAgents.length))],
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8', 
		'accept-encoding': 'gzip, deflate, br', 
		'accept-language': 'en-US,en;q=0.9,en;q=0.8' 
	});

	// just to have some cookies saved on the browser
	await page.goto('https://stackoverflow.com');
	await page.waitForTimeout(200);
	let acceptCookiesButton = await page.$x('/html/body/div[4]/div[1]/button[1]');
	await acceptCookiesButton[0].click();
	await page.waitForTimeout(100);

	await page.goto('https://www.bing.com');
	await page.waitForTimeout(100);
 
	// Go to the website 
	await page.goto('https://abrahamjuliot.github.io/creepjs/'); 

	// Wait for site to load properly
	await page.waitForTimeout(10000);

	const pdfConfig = {
		path: 'url.pdf', // Saves pdf to disk. 
		format: 'A4',
		printBackground: true,
		margin: { // Word's default A4 margins
			top: '2.54cm',
			bottom: '2.54cm',
			left: '2.54cm',
			right: '2.54cm'
		}
	};
	await page.emulateMediaType('screen');
	await page.pdf(pdfConfig); 		// Return the pdf buffer.

	let data = {};

	// scrape needed data
	data["trustScore"] = await getText('//*[@id="fingerprint-data"]/div[2]/div/div[1]/div[1]/span');
	let lies = await getText('//*[@id="fingerprint-data"]/div[2]/div/div[2]/div[2]');
	data["lies"] = lies.split(": ")[1];
	let bot = await getText('//*[@id="fingerprint-data"]/div[2]/div/div[2]/div[5]/div[2]/div[1]');
	data["bot"] = bot.split(": ")[1].split(":")[0];
	data["fpId"] = await getText('//*[@id="fingerprint-data"]/div[2]/div/div[2]/div[5]/div[1]/span[1]');
	console.log(data);

	data = JSON.stringify(data);
	fs.writeFile("data.json", data, (error) => {
		// throwing the error in case of a writing problem
		if (error) {
		  // logging the error
		  console.error(error);
		  throw error;
		}
		console.log("data.json written correctly");
	  });

});
