import React, { useMemo, useReducer } from "react";
import { useApi } from "../../hooks/useApi";
import { CreateHost } from "../../utils/types";
import { useAddressTypes } from "../../hooks/queries/useAddressTypes";
import { useInfiniteNetworks } from "../../hooks/queries/useInfiniteNetworks";
import { NetworkAutocomplete } from "../../components/networkAutocomplete";
const choices = {
  1: "1 Day",
  7: "1 Week",
  14: "2 Weeks",
  180: "6 Months",
  365: "1 Year",
  10950: "30 Years",
};
const hostReducer = (state: any, action: any) => {
  switch (action.type) {
    case "mac":
      return { ...state, mac: action.payload };
    case "hostname":
      return { ...state, hostname: action.payload };
    case "address_type":
      return { ...state, address_type: action.payload };
    case "description":
      return { ...state, description: action.payload };
    case "expire_days":
      return { ...state, expire_days: action.payload };
    default:
      return state;
  }
};
export const AddHostModule = (p: {
  showModule: boolean;
  setShowModule: (show: boolean) => void;
}) => {
  const api = useApi();
  const [host, dispatch] = useReducer(hostReducer, {
    mac: "",
    hostname: "",
    network: { id: 0, network: "" },
    address_type: "Dynamic",
    description: "",
    expire_days: 365,
  });
  const addressTypes = useAddressTypes().data?.addressTypes;
  const addHost = async (hostData: CreateHost) => {
    const results = await api.hosts.create({ ...hostData });
    alert(`successfully created ${hostData.hostname}`);
    p.setShowModule(false);
  };
  return (
    <>
      <input
        type="checkbox"
        hidden
        checked={p.showModule}
        onChange={(prev) => !prev}
        id="add-host-module"
        className="modal-toggle"
      />
      <dialog id="add-host-module" className="modal">
        <div className="modal-box border border-white">
          <label
            htmlFor="add-host-module"
            onClick={() => p.setShowModule(false)}
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
          <h1 className="text-2xl font-bold mb-4">Add host</h1>
          <form
            className="flex flex-col gap-4"
            onSubmit={(e: any) => {
              e.preventDefault();
              addHost(host);
            }}
          >
            <div className="flex flex-col gap-2">
              <label htmlFor="host-mac">Mac</label>
              <input
                type="text"
                id="host-mac"
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="host-name">Host Name</label>
              <input
                type="text"
                id="host-name"
                className="border border-gray-300 rounded-md p-2"
                onChange={(e) =>
                  dispatch({ type: "hostname", payload: e.target.value })
                }
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="type">Address Type</label>
              <select
                id={`type`}
                value={host.address_type}
                onChange={(v) => {
                  dispatch({ type: "address_type", payload: v.target.value });
                }}
                className="rounded-md p-2 select select-bordered"
              >
                {addressTypes?.map(({ name, id }) => (
                  <option value={name} key={id}>
                    {name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="network">Network</label>
              <NetworkAutocomplete
                onNetworkChange={(network) => {
                  dispatch({ type: "network", payload: network });
                }}
                networkId={host.network.id}
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="host-description">Description</label>
              <textarea
                id="host-description"
                className="border border-gray-300 rounded-md p-2"
                onChange={(e) =>
                  dispatch({ type: "description", payload: e.target.value })
                }
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="Dns-name">Expires</label>
              <select
                id={`expires`}
                value={host.expire_days}
                onChange={(v) => {
                  dispatch({ type: "expire_days", payload: v.target.value });
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
            <div className="flex justify-end gap-4 mt-4">
              <button
                className="bg-gray-500 hover:cursor-pointer hover:bg-gray-400 rounded-md px-4 py-2"
                onClick={() => p.setShowModule(false)}
                type="reset"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="bg-blue-500 hover:cursor-pointer hover:bg-blue-600 rounded-md px-4 py-2 text-white"
                onClick={() => p.setShowModule(false)}
              >
                Add host
              </button>
            </div>
          </form>
        </div>
      </dialog>
    </>
  );
};
