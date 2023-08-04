import React from "react";
import { useApi } from "../../hooks/useApi";
import { CreateDomain } from "../../utils/types";

export const EditDomainModule = (p: {
  domainData: CreateDomain | undefined;
  showModule: boolean;
  setShowModule: (show: any) => void;
}) => {
  const api = useApi();
  const updateDomain = async (domainData: CreateDomain) => {
    const results = await api.domains
      .byId(domainData.name)
      .update({ ...domainData });
    console.log(results);
    alert(`successfully created ${domainData.name}`);
  };
  return (
    <>
      <input
        type="checkbox"
        hidden
        checked={p.showModule}
        onChange={(prev) => !prev}
        id="add-domain-module"
        className="modal-toggle"
      />
      <dialog id="add-domain-module" className="modal">
        <div className="modal-box border border-white">
          <label
            htmlFor="add-domain-module"
            onClick={() =>
              p.setShowModule({
                show: false,
                domainData: undefined,
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
          <h1 className="text-2xl font-bold mb-4">Edit Domain</h1>
          <form
            className="flex flex-col gap-4"
            onSubmit={(e: any) => {
              e.preventDefault();
              const domainData = {
                name: e.target[0].value,
                description: e.target[1].value,
                master: e.target[2].value,
                type: e.target[3].value,
                notified_serial: e.target[4].value,
                account: e.target[5].value,
                last_check: e.target[6].value,
                changed: new Date().toISOString(),
              };
              updateDomain(domainData);
            }}
          >
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-name">Domain Name</label>
              <input
                type="text"
                id="domain-name"
                onChange={() => {}}
                value={p.domainData?.name ?? ""}
                disabled
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-description">Description</label>
              <textarea
                id="domain-description"
                onChange={() => {}}
                value={p.domainData?.description ?? "" ?? ""}
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-master">Master</label>
              <input
                type="text"
                id="domain-master"
                onChange={() => {}}
                value={p.domainData?.master ?? ""}
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-type">Type</label>
              <input
                type="text"
                id="domain-type"
                onChange={() => {}}
                value={p.domainData?.type ?? ""}
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-type">Notified Serial</label>
              <input
                type="text"
                id="domain-serial"
                onChange={() => {}}
                value={p.domainData?.notified_serial ?? ""}
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-account">Account</label>
              <input
                type="text"
                id="domain-account"
                onChange={() => {}}
                value={p.domainData?.account ?? ""}
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="domain-last-check">Last Check</label>
              <input
                type="date"
                min={new Date(0).getTime()}
                max={new Date().getTime()}
                id="domain-check"
                onChange={() => {}}
                value={p.domainData?.last_check ?? ""}
                className="border border-gray-300 rounded-md p-2"
              />
            </div>
            <div className="flex justify-end gap-4 mt-4">
              <button
                className="bg-gray-500 hover:cursor-pointer hover:bg-gray-400 rounded-md px-4 py-2"
                onClick={() =>
                  p.setShowModule({
                    show: false,
                    domainData: undefined,
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
                    domainData: undefined,
                  })
                }
              >
                Update Domain
              </button>
            </div>
          </form>
        </div>
      </dialog>
    </>
  );
};
