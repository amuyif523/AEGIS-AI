import React, { createContext, useContext, useState, useEffect } from 'react';

const translations = {
  en: {
    offline: 'OFFLINE MODE',
    filters: 'Filters',
    severity: 'Severity',
    type: 'Type',
    timeline: 'Timeline',
    proximity: 'Proximity Radius',
    hours: 'hours',
    disabled: 'Disabled'
  },
  am: {
    offline: 'ከመስመር ውጭ',
    filters: 'ማጣሪያዎች',
    severity: 'ክብደት',
    type: 'አይነት',
    timeline: 'የጊዜ መስመር',
    proximity: 'የቀረበ ክበብ',
    hours: 'ሰዓታት',
    disabled: 'ተሰናክሏል'
  }
};

const LocaleContext = createContext({ locale: 'en', t: (k) => k, setLocale: () => {} });

export const LocaleProvider = ({ children }) => {
  const [locale, setLocale] = useState(localStorage.getItem('aegis_locale') || 'en');

  useEffect(() => {
    localStorage.setItem('aegis_locale', locale);
  }, [locale]);

  const t = (key) => translations[locale]?.[key] || translations.en[key] || key;

  return (
    <LocaleContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </LocaleContext.Provider>
  );
};

export const useLocale = () => useContext(LocaleContext);
