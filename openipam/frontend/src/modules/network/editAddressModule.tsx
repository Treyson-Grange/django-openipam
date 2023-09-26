import React from "react";
import { useApi } from "../../hooks/useApi";
import { Address } from "../../utils/types";

export const EditAddressModule = (p: {
  show: boolean;
  setShow: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      address: Address | undefined;
    }>
  >;
  address: Address | undefined;
}) => {
  const api = useApi();
  const editAddress = async () => {
    p.setShow({
      show: false,
      address: undefined,
    });
  };
  return (
    <>
      <input
        type="checkbox"
        hidden
        checked={p.show}
        onChange={(prev) => !prev}
        id="add-Dns-module"
        className="modal-toggle"
      />
      <dialog id="Dns-module" className="modal">
        <div className="modal-box border border-white">
          <label
            htmlFor="add-Dns-module"
            onClick={() =>
              p.setShow({
                show: false,
                address: undefined,
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
          <h1 className="text-2xl font-bold mb-4">Edit Address</h1>
          <form
            className="flex flex-col gap-4"
            onSubmit={(e: any) => {
              e.preventDefault();
              editAddress();
            }}
          >
            <div className="flex justify-end gap-4 mt-4">
              <button
                className="btn btn-neutral text-neutral-content"
                onClick={() =>
                  p.setShow({
                    show: false,
                    address: undefined,
                  })
                }
                type="reset"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary text-primary-content"
              >
                Save
              </button>
            </div>
          </form>
        </div>
      </dialog>
    </>
  );
};