import { ArrowDownward, ArrowUpward } from "@mui/icons-material";
import {
  Column,
  Header,
  HeaderGroup,
  Table,
  flexRender,
} from "@tanstack/react-table";
import { Fragment, useMemo } from "react";
import { DebouncedInput } from "./debouncedInput";
import React from "react";

export const useTHBorderClasses = (
  header: Header<any, unknown>,
  headerGroup: HeaderGroup<any>,
  visibleCols: Column<any, unknown>[]
) => {
  return useMemo(() => {
    if (
      header.isPlaceholder ||
      header.index === headerGroup.headers.length - 1 ||
      header.index === 0
    )
      return "";
    const startPositionMatches = visibleCols.at(0)?.id === header.column.id;
    const endPositionMatches = visibleCols.at(-1)?.id === header.column.id;
    if (
      header.subHeaders.length > 0 ||
      (startPositionMatches && endPositionMatches)
    )
      return "border-x-base-100 border-x-8 border-y-0 border";
    if (startPositionMatches)
      return "border-x-base-100 border-l-8 border-r-0 border-y-0 border";
    if (endPositionMatches)
      return "border-x-base-100 border-l-0 border-r-8 border-y-0 border";
    return "";
  }, [header, headerGroup, visibleCols]);
};

const TableHeaderLabel = (p: {
  header: Header<any, unknown>;
  hideSorting: boolean;
}) => {
  const header = p.header;
  return (
    <div
      className={`whitespace-nowrap ${
        header.column.getCanSort() && !p.hideSorting
          ? "cursor-pointer select-none"
          : ""
      }`}
      onClick={header.column.getToggleSortingHandler() as any}
    >
      {flexRender(header.column.columnDef.header, header.getContext())}
      {{
        asc: (
          <>
            &nbsp;
            <ArrowUpward />
          </>
        ),
        desc: (
          <>
            &nbsp;
            <ArrowDownward />
          </>
        ),
      }[p.hideSorting ? "" : (header.column.getIsSorted() as string)] ?? null}
    </div>
  );
};

function Filter({
  column,
  table,
  header,
}: {
  column: Column<any, unknown>;
  table: Table<any>;
  header: Header<any, unknown>;
}) {
  const firstValue = table
    .getPreFilteredRowModel()
    .flatRows[0]?.getValue(column.id);

  const columnFilterValue = column.getFilterValue();

  const sortedUniqueValues = useMemo(
    () =>
      typeof firstValue === "number"
        ? []
        : Array.from(column.getFacetedUniqueValues().keys()).sort(),
    [column.getFacetedUniqueValues()]
  );

  const filterType = header.column.columnDef.meta?.filterType;
  switch (filterType) {
    case "string":
      return (
        <>
          <datalist id={column.id + "list"}>
            {sortedUniqueValues.slice(0, 5000).map((value: any, i: number) => (
              <option value={value} key={i} />
            ))}
          </datalist>
          <DebouncedInput
            type="text"
            value={(columnFilterValue ?? "") as string}
            onChange={(value) => column.setFilterValue(value)}
            placeholder={`Search (${column.getFacetedUniqueValues().size})`}
            className="w-full border shadow rounded input input-xs input-bordered"
            list={column.id + "list"}
          />
          <div className="h-1" />
        </>
      );
    case "exact":
      const uniqueValues = header.column.columnDef.meta?.filterOptions ?? [];
      return (
        <>
          <datalist id={column.id + "list"}>
            {uniqueValues.map((value: any, i: number) => (
              <option value={value} key={i} />
            ))}
          </datalist>
          <DebouncedInput
            type="text"
            value={(columnFilterValue ?? "") as string}
            onChange={(value) => column.setFilterValue(value)}
            placeholder={`Search (${uniqueValues.length})`}
            className="w-full border shadow rounded input input-xs input-bordered"
            list={column.id + "list"}
          />
          <div className="h-1" />
        </>
      );
    case "date":
      const maxDate = new Date().getTime();
      const minDate = new Date("1970-01-01").getTime();
      return (
        <div>
          <div className="flex flex-col w-full space-x-2">
            <input
              type="date"
              min={minDate}
              max={maxDate}
              value={(columnFilterValue as [string, string])?.[0] ?? ""}
              onChange={(e) => {
                column.setFilterValue((old: [string, string]) => [
                  e.target.value,
                  old?.[1],
                ]);
              }}
              placeholder="Search"
              className="border shadow rounded w-full input input-xs input-bordered"
            />
            <input
              type="date"
              min={minDate}
              max={maxDate}
              value={(columnFilterValue as [string, string])?.[1] ?? ""}
              onChange={(e) => {
                column.setFilterValue((old: [string, string]) => [
                  old?.[0],
                  e.target.value,
                ]);
              }}
              placeholder="Search"
              className="border shadow rounded w-full input input-xs input-bordered"
            />
          </div>
        </div>
      );
    default:
      return null;
  }
}

export const TableHeaderCell = (p: {
  header: Header<any, unknown>;
  headerGroup: HeaderGroup<any>;
  hideSorting?: boolean;
  hideFilter?: boolean;
  table: Table<any>;
}) => {
  const { header, headerGroup } = p;
  const visibleCols = useMemo(() => {
    return header.column.parent?.columns.filter((c) => c.getIsVisible()) ?? [];
  }, [header]);
  const headerBorderClasses = useTHBorderClasses(
    header,
    headerGroup,
    visibleCols
  );
  const thProps = header.column.columnDef.meta?.thProps?.() || {};
  return (
    <th
      {...thProps}
      className={`sticky top-0 text-center bg-gray-500 text-white ${headerBorderClasses} ${
        thProps.className ?? ""
      }`}
      colSpan={header.colSpan}
    >
      {header.isPlaceholder ? null : (
        <>
          <TableHeaderLabel
            header={header}
            hideSorting={Boolean(p.hideSorting)}
          />
          {header.column.getCanFilter() && !p.hideFilter && (
            <Filter column={header.column} table={p.table} header={header} />
          )}
        </>
      )}
    </th>
  );
};

export const TableHead = (p: { table: Table<any>; selectedColumns?: any }) => {
  return (
    <thead>
      <tr>
        {p.table.getAllLeafColumns().map((column) => {
          if (!column.getIsVisible()) return <Fragment key={column.id} />;
          return (
            <th
              key={column.id}
              style={{ width: column.getSize() }}
              className="h-0 p-0 m-0 bg-white"
            />
          );
        })}
      </tr>
      {p.table.getHeaderGroups().map((headerGroup) => (
        <tr key={headerGroup.id}>
          {headerGroup.headers.map((header) => (
            <TableHeaderCell
              header={header}
              headerGroup={headerGroup}
              key={header.id}
              table={p.table}
            />
          ))}
        </tr>
      ))}
    </thead>
  );
};
