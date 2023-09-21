import { ColumnFiltersState, createColumnHelper } from "@tanstack/react-table";
import { ReactNode, useEffect, useMemo, useState } from "react";
import React from "react";
import { Address } from "../../utils/types";
import { BooleanRender, booleanAccessor } from "../../components/table/boolean";
import { useInfiniteNetworkAddresses } from "../../hooks/queries/useInfiniteNetworkAddresses";
import { ActionsColumn } from "../../components/table/actionsColumn";
import { CreateTable } from "../../components/table/createTable";
import { useNavigate } from "react-router";
import { getOrdering } from "../../components/table/getOrdering";
import { useApi } from "../../hooks/useApi";

const AddressLookupKeys = ["address", "name", "gateway", "description"];

export const useAddressesTable = (p: {
  network: string;
  range: string;
  setShowModule: React.Dispatch<React.SetStateAction<boolean>>;
  setEditModule: React.Dispatch<
    React.SetStateAction<{ show: boolean; address: Address | undefined }>
  >;
  setActionModule: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      data: Address[] | undefined;
      title: string;
      onSubmit?: (data: Address[]) => void;
      children: ReactNode;
      multiple?: boolean;
    }>
  >;
  onSelectColumns: () => void;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [prevData, setPrevData] = useState<Address[]>([]);
  const [rowSelection, setRowSelection] = useState({});
  const [columnSort, setColumnSort] = useState<any[]>([]);
  const [pageSize, setPageSize] = useState<number>(16);
  const [page, setPage] = useState<number>(1);
  const [action, setAction] = useState<string>("delete");
  const api = useApi();
  const [columnVisibility, setColumnVisibility] = useState<any>(
    localStorage.getItem("networkAddressesTableColumns")
      ? JSON.parse(localStorage.getItem("networkAddressesTableColumns")!)
      : {
          host: false,
          changed: false,
        }
  );
  useEffect(() => {
    localStorage.setItem(
      "networkAddressesTableColumns",
      JSON.stringify(columnVisibility)
    );
  }, [columnVisibility]);
  const data = useInfiniteNetworkAddresses({
    network: p.network,
    range: p.range,
    ...Object.fromEntries(
      columnFilters
        .filter((f) => AddressLookupKeys.includes(f.id) && f.value)
        .map((filter) => [filter.id, filter.value as string])
    ),
    page_size: pageSize,
    page,
    ordering: getOrdering(columnSort),
  });
  const dns = useMemo<Address[]>(() => {
    if (!data.data) {
      return prevData.length ? prevData : [];
    }
    return data.data.pages.flatMap((page) => page.addresses);
  }, [data.data]);
  const navigate = useNavigate();
  useEffect(() => {
    if (data.data) {
      setPrevData(() => [...data.data.pages.flatMap((page) => page.addresses)]);
    }
  }, [data.data]);
  const columnHelper = createColumnHelper<Address>();
  const columns = [
    ...ActionsColumn({
      data,
      size: 80,
      pageSizes: [16, 32, 64, 128, 256],
      enableSelection: true,
      onAdd: () => {
        p.setShowModule(true);
      },
      onView: (row) => {
        navigate(`/addresses/${row.address}`);
      },
      onEdit: (row) => {
        p.setEditModule({
          show: true,
          address: row.address,
        });
      },
      onSelectColumns: p.onSelectColumns,
      pageSize,
      setPageSize,
    }),
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "address",
          header: "Address",
          accessorFn: (row) => row.address,
        },
        {
          id: "host",
          header: "Host",
          cell: ({ row }: { row: { original: Address } }) => {
            return row.original.host ? (
              <a
                className="text-blue-500 hover:underline btn btn-sm btn-ghost"
                href={`#/hosts/${row.original.host}`}
              >
                {row.original.host}
              </a>
            ) : (
              <></>
            );
          },

          accessorFn: (row) => row.host,
        },
        {
          id: "hostname",
          header: "Hostname",
          size: 200,
          cell: ({ row }: { row: { original: Address } }) => {
            return row.original.hostname ? (
              <a
                className="text-blue-500 hover:underline btn btn-sm btn-ghost"
                href={`#/hosts/${row.original.hostname}`}
              >
                {row.original.hostname}
              </a>
            ) : (
              <></>
            );
          },

          accessorFn: (row) => row.host,
        },
        {
          id: "gateway",
          header: "Gateway",
          accessorFn: (row) => row.gateway,
        },
      ],
    }),
    columnHelper.group({
      id: "Last Seen",
      header: "Last Seen",
      columns: [
        {
          id: "last_seen",
          header: "Last Seen",
          accessorFn: (row) =>
            row.last_seen ? new Date(row.last_seen).toDateString() : "",
        },
        {
          id: "last_mac_seen",
          header: "Last Mac Seen",
          accessorFn: (row) =>
            row.last_mac_seen ? new Date(row.last_mac_seen).toDateString() : "",
        },
      ],
    }),
    columnHelper.group({
      id: "Other Details",
      header: "Other Details",
      columns: [
        {
          id: "reserved",
          header: "Reserved",
          accessorFn: booleanAccessor("reserved"),
          cell: BooleanRender,
          meta: {
            filterType: "boolean",
          },
        },
        {
          id: "pool",
          header: "Pool",
          accessorFn: (row) => row.pool?.name,
        },
        {
          id: "changed",
          header: "Changed",
          accessorFn: (row) =>
            row.changed ? new Date(row.changed).toDateString() : "",
        },
      ],
    }),
  ];

  const table = CreateTable({
    setColumnFilters,
    setRowSelection,
    setColumnSort,
    setColumnVisibility,
    data: dns,
    state: {
      columnFilters,
      rowSelection,
      pageSize,
      sorting: columnSort,
      columnVisibility,
    },
    columns,
    orderingColumns: ["address", "changed"],
    meta: {
      total: data.data?.pages?.[0]?.count,
      pageSize,
      page,
      setPage,
      rowActions: (rows: Address[]) => {
        return (
          <div className="flex flex-col gap-2 m-2">
            <label>Actions</label>
            <div className="flex flex-row gap-2">
              <select
                id={`actions`}
                onChange={(v) => {
                  setAction(v.target.value);
                }}
                value={action}
                className="rounded-md p-2 select select-bordered w-full"
              >
                {Object.entries(actions).map(([key, value]) => (
                  <option value={key} key={key}>
                    {value}
                  </option>
                ))}
              </select>
              <button
                className="btn btn-primary"
                onClick={() => {
                  switch (action) {
                    case "delete":
                      p.setActionModule({
                        show: true,
                        data: rows,
                        title: "Delete Records",
                        onSubmit: () => {
                          // rows.forEach((row) => {
                          //   api.addresses.byId(row.address).delete();
                          // });
                        },
                        children: <div></div>,
                      });
                      break;
                    default:
                      break;
                  }
                }}
                disabled={rows.length === 0}
              >
                Go
              </button>
            </div>
          </div>
        );
      },
    },
  });

  return useMemo(
    () => ({
      loading: data.isFetching,
      table,
    }),
    [data.data, data.isFetching]
  );
};

const actions = {
  delete: "Delete",
};
