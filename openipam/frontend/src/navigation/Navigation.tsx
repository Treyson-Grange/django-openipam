import React, { useContext } from "react";
import { Link, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { ThemeContext, useThemes } from "../hooks/useTheme";
import { Palette } from "@mui/icons-material";
import { IdToName } from "../components/idToName";

export const Navigation = () => {
  const auth = useAuth();
  const { theme, setTheme } = useContext(ThemeContext);
  const themes = useThemes();
  return (
    <div
      className={`${theme === "dark" ? "bg-gray-800" : "bg-base-100"
        } min-h-screen min-w-screen w-full h-full`}
      data-theme={theme}
    >
      <div className="w-full navbar menu menu-horizontal items-center flex flex-row justify-between bg-base-300">
        <div className="flex-flex-row justify-start">

          <Link className="link-hover font-semibold" to="/">
            <button className="btn btn-ghost btn-primary text-lg">
              Home
            </button>
          </Link>
          <Link className="link-hover font-semibold" to="/hosts">
            <button className="btn btn-ghost btn-primary text-lg">
              Hosts
            </button>
          </Link>
          <Link className="link-hover font-semibold" to="/domains">
            <button className="btn btn-ghost btn-primary text-lg">
              Domains
            </button>
          </Link>
          {auth?.is_ipamadmin && (
            <>
              <Link
                className="link-hover font-semibold"
                to="/networks"
              >
                <button className="btn btn-ghost btn-primary text-lg">
                  Networks
                </button>
              </Link>
              <Link
                className="link-hover font-semibold"
                to="/admin/logs"
              >
                <button className="btn btn-ghost btn-primary text-lg">
                  Logs
                </button>
              </Link>
              <Link
                className="link-hover font-semibold"
                to="/admin/users"
              >
                <button className="btn btn-ghost btn-primary text-lg">
                  Users
                </button>
              </Link>
            </>
          )}
        </div>
        <div className="flex flex-row gap-2 mr-4">
          <Palette />
          <select
            className="btn btn-ghost btn-primary"
            onChange={(e) => {
              setTheme(e.target.value);
            }}
            value={theme}
          >
            {themes.map((theme) => (
              <option key={theme} value={theme}>
                {IdToName(theme)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <Outlet />
    </div>
  );
};
