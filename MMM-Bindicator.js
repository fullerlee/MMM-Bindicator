Module.register("MMM-Bindicator", {

  defaults: {
    weeksToShow: 2
  },

  /**
   * Apply the default styles.
   */
  getStyles() {
    return ["template.css"]
  },

  /**
   * Pseudo-constructor for our module. Initialize stuff here.
   */
  start() {
    console.log("MMM-Bindicator started!");
    
    // set timeout for next random text
    
    this.sendSocketNotification("BINDICATOR_COLLECT_BINS", { amountCharacters: 15 })
  },

  /**
   * Handle notifications received by the node helper.
   * So we can communicate between the node helper and the module.
   *
   * @param {string} notification - The notification identifier.
   * @param {any} payload - The payload data`returned by the node helper.
   */
  socketNotificationReceived: function (notification, payload) {
    if (notification === "BINDICATOR_BINS_READY") {
      const binDates = JSON.parse(payload.binDates)

      this.templateContent = '';
      for (let i = 0; i < Math.min(binDates.length, this.config.weeksToShow); i++) {
        this.templateContent += `${i > 0 ? '<br />' : ''}${binDates[i].date} - ${binDates[i].collectionType}`
      }
      this.updateDom()
    }
  },

  /**
   * Render the page we're on.
   */
  getDom() {
    const wrapper = document.createElement("div")
    wrapper.className = `bindicator-container`;
    wrapper.innerHTML = `<b>Bins</b><br />${this.templateContent}`

    return wrapper
  },

  addRandomText() {
    this.sendSocketNotification("GET_RANDOM_TEXT", { amountCharacters: 15 })
  },

  /**
   * This is the place to receive notifications from other modules or the system.
   *
   * @param {string} notification The notification ID, it is preferred that it prefixes your module name
   * @param {number} payload the payload type.
   */
  notificationReceived(notification, payload) {
    if (notification === "TEMPLATE_RANDOM_TEXT") {
      this.templateContent = `${this.config.exampleContent} ${payload}`
      this.updateDom()
    }
  }
})
