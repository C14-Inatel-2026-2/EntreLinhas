const { defineConfig } = require("cypress");

module.exports = defineConfig({
  reporter: "cypress-mochawesome-reporter",
  reporterOptions: {
    reportDir: "reports/cypress",
    reportFilename: "index",
    reportPageTitle: "Entre Linhas — testes da interface web",
    charts: true,
    embeddedScreenshots: true,
    inlineAssets: true,
    saveJson: true,
    overwrite: true
  },
  screenshotsFolder: "reports/cypress/screenshots",
  video: false,
  viewportWidth: 1280,
  viewportHeight: 900,
  e2e: {
    baseUrl: "http://127.0.0.1:8000",
    specPattern: "cypress/e2e/**/*.cy.js",
    supportFile: "cypress/support/e2e.js",
    setupNodeEvents(on, config) {
      require("cypress-mochawesome-reporter/plugin")(on);
      return config;
    }
  }
});
