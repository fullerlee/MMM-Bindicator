const NodeHelper = require("node_helper")
const { exec } = require('child_process');

module.exports = NodeHelper.create({

  start () {
    console.log("MMM-Bindicator NodeHelper started!");
    self = this;
  },

  async socketNotificationReceived(notification, payload) {
    console.log("MMM-Bindicator NodeHelper received notification:", notification, payload)
    if (notification === "BINDICATOR_COLLECT_BINS") {
      const amountCharacters = payload.amountCharacters || 10
      //const randomText = Array.from({ length: amountCharacters }, () => String.fromCharCode(Math.floor(Math.random() * 26) + 97)).join("")
      //this.sendSocketNotification("BINDICATOR_BINS_READY", { text: randomText })
      this.collectBins(amountCharacters);
    }
  },

  collectBins(amountCharacters) {
    
    exec('./modules/MMM-Bindicator/bindicator.sh', (err, stdout, stderr) => {
      
      if (err) {
        // node couldn't execute the command
        return;
      }

      // the *entire* stdout and stderr (buffered)
      console.log(`MMM-Bindicator stdout: ${stdout}`);
      console.log(`MMM-Bindicator stderr: ${stderr}`);

      //Now parse out what we need!


      this.sendSocketNotification("BINDICATOR_BINS_READY", { text: stdout.trim() })
    });
  }
})
