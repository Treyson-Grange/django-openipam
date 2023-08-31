import React, { useEffect, useLayoutEffect } from "react";

export const ThemeContext = React.createContext({
  theme: localStorage.getItem("theme") ?? "light",
  setTheme: (theme: string) => {},
});

function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = React.useState(
    localStorage.getItem("theme") ?? "light"
  ); // Default theme is light

  useLayoutEffect(() => {
    localStorage.getItem("theme") &&
      setTheme(localStorage.getItem("theme") as string);
  }, []);

  useEffect(() => {
    localStorage.getItem("theme") &&
      setTheme(localStorage.getItem("theme") as string);
  }, [theme]);

  const setThemeWrapper = (theme: string) => {
    localStorage.setItem("theme", theme);
    setTheme(theme);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme: setThemeWrapper }}>
      {children}
    </ThemeContext.Provider>
  );
}

export { ThemeProvider };

export const useThemes = () => {
  return themes;
};

const themes = [
  "light",
  "dark",
  "dracula",
  "winter",
  "night",
  "cupcake",
  "black",
  "corporate",
  "synthwave",
  "retro",
  "bumblebee",
  "emerald",
  "halloween",
  "garden",
  "forest",
  "lofi",
  "fantasy",
  "cmyk",
  "autumn",
  "lemonade",
  "valentine",
];
