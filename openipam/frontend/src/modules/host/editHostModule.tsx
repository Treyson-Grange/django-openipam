import React from "react";
import { useApi } from "../../hooks/useApi";
import { CreateHost, Host } from "../../utils/types";

const choices = {
  1: "1 Day",
  7: "1 Week",
  14: "2 Weeks",
  180: "6 Months",
  365: "1 Year",
  10950: "30 Years",
};

export const EditHostModule = (p: {
  HostData: Host | undefined;
  showModule: boolean;
  setShowModule: (show: any) => void;
}) => {
  const api = useApi();
  const [disabled, setDisabled] = React.useState<boolean>(
    p.HostData?.disabled_host ?? false
  );
  const updateHost = async (HostData: CreateHost) => {
    const results = await api.hosts.byId(HostData.mac).update({ ...HostData });
    alert(`successfully edited ${HostData.mac}`);
  };
  return (
    <>
      <input
        type="checkbox"
        hidden
        checked={p.showModule}
        onChange={(prev) => !prev}
        id="add-Host-module"
        className="modal-toggle"
      />
      <dialog id="add-Host-module" className="modal">
        <div className="modal-box border border-white">
          <label
            htmlFor="add-Host-module"
            onClick={() =>
              p.setShowModule({
                show: false,
                HostData: undefined,
              })
            }
            className="absolute top-0 right-0 p-4 cursor-pointer"
          >
            <svg
              className="w-6 h-6 text-gray-500 hover:text-gray-300"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </label>
          <h1 className="text-2xl font-bold mb-4">Edit Host</h1>
          <form
            className="flex flex-col gap-4"
            onSubmit={(e: any) => {
              e.preventDefault();
              const HostData = {
                mac: e.target[0].value,
                hostname: e.target[1].value,
                description: e.target[2].value,
                expire_days: e.target[3].value,
              };
              updateHost(HostData);
            }}
          >
            <div className="flex flex-col gap-2">
              <label htmlFor="host-mac">Mac</label>
              <input
                type="text"
                id="host-mac"
                value={p.HostData?.mac ?? ""}
                disabled
                onChange={() => {}}
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="host-name">Host Name</label>
              <input
                type="text"
                id="host-name"
                value={p.HostData?.hostname ?? ""}
                onChange={() => {}}
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="host-description">Description</label>
              <textarea
                id="host-description"
                value={p.HostData?.description ?? ""}
                onChange={() => {}}
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="Dns-name">Expires</label>
              <select
                id={`expires`}
                value={365}
                onChange={(v) => {
                  console.log(v);
                }}
                className="rounded-md p-2 select select-bordered"
              >
                {Object.entries(choices).map(([key, value]) => (
                  <option value={key} key={key}>
                    {value}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="host-last-check">Disable Host</label>
              <input
                type="checkbox"
                checked={disabled}
                onChange={() => {
                  setDisabled(!disabled);
                }}
                id="host-disabled"
                className="border border-gray-300 rounded-md p-2 checkbox checkbox-error checkbox-sm"
              />
            </div>
            {/* If disabled is checked, add reason */}
            {disabled && (
              <div className="flex flex-col gap-2">
                <label htmlFor="host-last-check">Reason to Disable</label>
                <textarea
                  id="host-description"
                  value={p.HostData?.description ?? ""}
                  onChange={() => {}}
                  className="border border-gray-300 rounded-md p-2"
                />
              </div>
            )}

            <div className="flex justify-end gap-4 mt-4">
              <button
                className="bg-gray-500 hover:cursor-pointer hover:bg-gray-400 rounded-md px-4 py-2"
                onClick={() =>
                  p.setShowModule({
                    show: false,
                    HostData: undefined,
                  })
                }
                type="reset"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="bg-blue-500 hover:cursor-pointer hover:bg-blue-600 rounded-md px-4 py-2 text-white"
                onClick={() =>
                  p.setShowModule({
                    show: false,
                    HostData: undefined,
                  })
                }
              >
                Update Host
              </button>
            </div>
          </form>
        </div>
      </dialog>
    </>
  );
};
