// terabox.js
const axios = require('axios');

async function teraboxDownload(link) {
    const payload = { url: link };
    const headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    };

    try {
        const response = await axios.post(
            'https://ytshorts.savetube.me/api/v1/terabox-downloader',
            payload,
            { headers }
        );

        if (response.data.response && response.data.response.length > 0) {
            const fastDownloadUrl = response.data.response[0].resolutions["Fast Download"];
            const slowDownloadUrl = response.data.response[0].resolutions["HD Video"];
            
            if (fastDownloadUrl) {
                const downloadResponse = await axios.get(fastDownloadUrl, { responseType: 'arraybuffer' });
                
                if (downloadResponse.status === 200 && downloadResponse.headers['content-type'] === 'application/octet-stream') {
                    return fastDownloadUrl;
                } else {
                    console.log("Fast download link is unusable. Trying slow download.");
                    return slowDownloadUrl;
                }
            }

            return slowDownloadUrl; // Return slow download if fast download link is not valid
        } else {
            console.error("Unexpected response format.");
            return null;
        }
    } catch (error) {
        console.error(`Error generating download link: ${error.message}`);
        return null;
    }
}

module.exports = {
    teraboxDownload
};
