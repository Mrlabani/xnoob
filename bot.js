// bot.js
const { Telegraf } = require('telegraf');
const { teraboxDownload } = require('./terabox');
const { BOT_TOKEN } = require('./config');

// Create a new Telegraf bot instance
const bot = new Telegraf(BOT_TOKEN);

// Command handler for /start
bot.start((ctx) => {
    ctx.reply("Welcome! Send me a Terabox download link.");
});

// Handler for incoming messages
bot.on('text', async (ctx) => {
    const link = ctx.message.text;
    ctx.reply(`Processing your link: ${link}`);
    
    const downloadLink = await teraboxDownload(link);
    
    if (downloadLink) {
        ctx.reply(`Download link: ${downloadLink}`);
    } else {
        ctx.reply("An error occurred while generating the download link.");
    }
});

module.exports = bot;
