import type { Row, RowSelectionState, Table } from "@tanstack/react-table";
import { useRef } from "react";
import { DebouncedInput } from "./debouncedInput";
import { TableBody } from "./tableBody";
import { TableHead, TableHeaderCell } from "./tableHead";
import React from "react";
import { useAuth } from "../../hooks/useAuth";
import { IdToName } from "../idToName";
import { Delete } from "@mui/icons-material";

export const PrimaryTable = (p: {
  estimateColumnSize?: number;
  table: Table<any>;
  className?: string;
}) => {
  const auth = useAuth();
  const tableContainerRef = useRef<HTMLDivElement>(null);
  const selectedRows = p.table.getSelectedRowModel();
  const activeFilters = p.table.getState().columnFilters;
  const rows = p.table.getRowModel().rows;
  const total = p.table.options.meta?.total ?? rows.length;
  const [globalFilter, setGlobalFilter] = [
    p.table.getState().globalFilter,
    p.table.setGlobalFilter,
  ];

  return (
    <div
      ref={tableContainerRef}
      className={`overflow-scroll max-h-[calc(100vh-192px)] ${
        p.className || ""
      }`}
    >
      <div className="w-full grid grid-cols-3 gap-10">
        {auth?.is_ipamadmin ? (
          <div className="flex flex-col justify-between w-full max-w-2xl">
            <div className="flex flex-row gap-4 ">
              <p className="">{selectedRows.rows.length} Rows Selected</p>
            </div>
            {p.table.options.meta?.rowActions?.(
              selectedRows.rows.map((r) => r.original)
            )}
          </div>
        ) : (
          <div></div>
        )}
        <div className="flex flex-row gap-4 m-1">
          <div className="flex flex-col justify-between">
            <div className="flex flex-row gap-4">
              <p className="">
                Loaded {rows.length} of {total} rows
              </p>
            </div>
            <div className="flex flex-row gap-4 ">
              <p className=" mt-1">Active Column Filters:</p>
              {activeFilters.length > 0 && (
                <button
                  className="btn btn-sm btn-outline btn-ghost"
                  onClick={() => p.table.resetColumnFilters()}
                >
                  Clear All
                </button>
              )}
            </div>
            <div className="flex gap-2 ">
              {activeFilters.length ? (
                activeFilters.map((filter) => (
                  <div
                    className="flex flex-row gap-2 flex-wrap"
                    key={Math.random()}
                  >
                    <p className="">{IdToName(filter.id)}:</p>
                    <p className="">{JSON.stringify(filter.value)}</p>
                  </div>
                ))
              ) : (
                <p className="">No Active Filters</p>
              )}
            </div>
          </div>
        </div>
        <div className="flex flex-row gap-4 m-1">
          <div className="flex flex-col gap-2 w-full justify-between">
            <label className=" m-1">Advanced Filters:</label>
            {globalFilter?.map((filter: { id: string; text: string }) => (
              <div
                className="flex flex-row gap-2 flex-wrap"
                key={Math.random()}
              >
                <p className="">{filter.text}</p>
                <button
                  className="btn btn-sm btn-ghost"
                  onClick={() => {
                    setGlobalFilter?.((prev: any[]) =>
                      prev.filter((f) => f.id !== filter.id)
                    );
                  }}
                >
                  <Delete />
                </button>
              </div>
            ))}
            {p.table.options.meta?.globalFilter ?? <></>}
          </div>
        </div>
      </div>
      <table className="table table-sm table-fixed">
        <TableHead table={p.table} />
        <TableBody
          tableContainerRef={tableContainerRef}
          table={p.table}
          estimateColumnSize={p.estimateColumnSize}
        />
        <tfoot>
          {p.table.getFooterGroups().map((footerGroups) => (
            <tr key={footerGroups.id} className="sticky bottom-0">
              {footerGroups.headers.map((header) => (
                <TableHeaderCell
                  header={header}
                  headerGroup={footerGroups}
                  key={header.id}
                  hideSorting
                  hideFilter
                  table={p.table}
                />
              ))}
            </tr>
          ))}
        </tfoot>
      </table>
    </div>
  );
};
