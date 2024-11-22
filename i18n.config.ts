import english from "#i18n/locales/en.json";
import spanish from "#i18n/locales/es.json";

export default defineI18nConfig(() => ({
  legacy: false,
  locale: "en",
  messages: {
    en: english,
    es: spanish,
  },
}));
