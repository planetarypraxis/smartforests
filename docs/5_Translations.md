# Translations

# Add a new language (`locale`), with a fallback to English (or another language)

Just to go over the basics, this is how to add any new locale to the site.

1. Go to settings > locale
2. Click "add a locale"
3. Click "enable" under "synchronise" and select English — this is the fallback that @conatus was talking about.
  - You could select  a different language to synchronise from, if you prefer not to fall back to English for a certain locale.
  - This ensures that all the normal pages (e.g. Map, Logbook Index, etc.) show up
  - It also allows users to switch between different translations of existing pages that haven't been translated under the new locale yet

![create-locale](https://user-images.githubusercontent.com/237556/151366959-d75d823d-f127-4625-b666-6864542e3e32.gif)

# Delete a language (`locale`) and all its pages

### 1. Delete the French locale root page
<img width="300" alt="Screenshot 2022-04-07 at 11 42 41" src="https://user-images.githubusercontent.com/237556/162181802-3d375275-6564-403b-93e8-9aa8416df28f.png">
<img width="300" alt="Screenshot 2022-04-07 at 11 42 48" src="https://user-images.githubusercontent.com/237556/162181812-6d38a3c7-c4eb-4451-a3ec-2dc6dc0606a0.png">
<img width="300" alt="Screenshot 2022-04-07 at 11 42 51" src="https://user-images.githubusercontent.com/237556/162181827-06a33348-2548-43de-8635-9fbd76f004d7.png">

### 2. Delete the locale now that there are no French pages depending on it
<img width="300" alt="Screenshot 2022-04-07 at 11 43 01" src="https://user-images.githubusercontent.com/237556/162181770-b8d46cac-5933-4548-9945-eab75d3eab0b.png">

# Create a page in the contributor's own language

You can create a new page in any locale, as long as you've added it at the global level (see above). The system does not particularly bias English as a language, except that it is what the standard index pages were created in.

1. In the sidebar, select Pages > Atlas [your desired locale]
2. Add child pages as normal. The pages will be created in this new language.

![create-locale-page](https://user-images.githubusercontent.com/237556/151366670-c79d8208-45ba-4820-bab0-28a107167c2c.gif)

# Add a translation for this non-English page

### First, set up translations to other languages for this page
  
1. In the page list, click the "translate this page" option for the page
2. Select select all, or pick a subset of languages
3. Press submit. Translations for this page are now possible.

![enable-translations](https://user-images.githubusercontent.com/237556/151366153-280ac83b-9036-4883-8182-ee3c421f6e5c.gif)

## Switch to that language in the Page Editor and add the translation copy.

1. Go to the page editor for this page
2. In the header, select the current language dropdown and select the new target translation language
3. Add translations for the various fields
4. Click "save" for those fields, in line
5. Publish the translation

![add-locale-page-translation](https://user-images.githubusercontent.com/237556/151366182-704aca6c-b80e-4164-a2c9-c95ef87a2bc2.gif)