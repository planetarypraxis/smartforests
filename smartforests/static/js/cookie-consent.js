window.addEventListener("load", function () {
  CookieConsent.run({
    categories: {
      necessary: {
        enabled: true,
        readOnly: true,
      },
      analytics: {
        autoClear: {
          cookies: [
            {
              name: /^ph_/,
            },
            {
              name: /^__ph/,
            },
          ],
        },
      },
    },
    language: {
      default: window.LANGUAGE_CODE || "en",
      translations: {
        en: {
          consentModal: {
            title: "We use cookies!",
            description:
              'Hi, this website uses essential cookies to ensure its proper operation and tracking cookies to understand how you interact with it. The latter will be set only after consent. <button type="button" data-cc="c-settings" class="cc-link">Let me choose</button>',
            acceptAllBtn: "Accept all",
            acceptNecessaryBtn: "Reject all",
            showPreferencesBtn: "Manage preferences",
          },
          preferencesModal: {
            title: "Cookie preferences",
            acceptAllBtn: "Accept all",
            acceptNecessaryBtn: "Reject all",
            savePreferencesBtn: "Save preferences",
            closeIconLabel: "Close",
            sections: [
              {
                title: "Cookie usage",
                description:
                  'We use cookies to ensure the basic functionalities of the website and to enhance your online experience. You can choose for each category to opt-in/out whenever you want. For more details relative to cookies and other sensitive data, please read the full <a href="/terms-and-conditions/">terms and conditions</a>.',
              },
              {
                title: "Strictly necessary cookies",
                description:
                  "These cookies are essential for the proper functioning of my website. Without these cookies, the website would not work properly.",
                linkedCategory: "necessary",
              },
              {
                title: "Performance and Analytics cookies",
                description:
                  "These cookies allow the research team to collect usage data so they can improve the website over time.",
                linkedCategory: "analytics",
                cookieTable: {
                  headers: {
                    name: "Name",
                    domain: "Service",
                    description: "Description",
                    expiration: "Expiration",
                  },
                  body: [
                    {
                      name: /^ph_/,
                      domain: "Posthog",
                      description:
                        'Cookie set by <a href="https://posthog.com">Posthog</a>',
                      expiration: "Never",
                    },
                    {
                      name: /^__ph/,
                      domain: "Posthog",
                      description:
                        'Cookie set by <a href="https://posthog.com">Posthog</a>',
                      expiration: "Never",
                    },
                  ],
                },
              },
              {
                title: "More information",
                description:
                  "For any queries in relation to our policy on cookies and your choices, please contact us at jennifer@planetarypraxis.org.",
              },
            ],
          },
        },
      },
    },
  });
});
