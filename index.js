// index.js
const bot = require('./bot');

// Start the bot
bot.launch()
    .then(() => {
        console.log("Bot started successfully.");
    })
    .catch((error) => {
        console.error(`Error starting the bot: ${error.message}`);
    });
