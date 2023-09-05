import { ColumnFiltersState, createColumnHelper } from "@tanstack/react-table";
import { ReactNode, useEffect, useMemo, useState } from "react";
import React from "react";
import { People, PeopleOutline } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { Host } from "../../utils/types";
import { useInfiniteMyHosts } from "../../hooks/queries/useInfiniteMyHosts";
import { ActionsColumn } from "../../components/table/actionsColumn";
import { CreateTable } from "../../components/table/createTable";
import { getExpiresDateFromFilter } from "../hosts/expiresDateFilter";
import { getOrdering } from "../../components/table/getOrdering";
import { HostTableActions } from "../hosts/hostTableActions";

export const useUserHostsTable = (p: {
  //   setShowAddHost: React.Dispatch<React.SetStateAction<boolean>>;
  //   setEditHost: React.Dispatch<
  //     React.SetStateAction<{ show: boolean; HostData: Host | undefined }>
  //   >;
  setActionModule: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      data: Host[] | undefined;
      title: string;
      onSubmit?: (data: Host[]) => void;
      children: ReactNode;
      multiple?: boolean;
    }>
  >;
  setAttributeModule: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      data: Host[] | undefined;
      delete?: boolean;
    }>
  >;
  onSelectColumns: () => void;
  setRenewModule: React.Dispatch<
    React.SetStateAction<{ show: boolean; data: Host[] | undefined }>
  >;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [pageSize, setPageSize] = useState<number>(10);
  const [page, setPage] = useState<number>(1);
  const [columnVisibility, setColumnVisibility] = useState<any>(
    localStorage.getItem("myHostsTableColumns")
      ? JSON.parse(localStorage.getItem("myHostsTableColumns")!)
      : {}
  );
  useEffect(() => {
    localStorage.setItem(
      "myHostsTableColumns",
      JSON.stringify(columnVisibility)
    );
  }, [columnVisibility]);
  const [rowSelection, setRowSelection] = useState({});
  const [columnSort, setColumnSort] = useState<any[]>([]);
  const [prevData, setPrevData] = useState<Host[]>([]);
  const [showGroups, setShowGroups] = useState(false);
  const navigate = useNavigate();

  const data = useInfiniteMyHosts({
    ...Object.fromEntries(
      columnFilters
        .map((filter) => [
          filter.id,
          filter.value as string | number | string[],
        ])
        .map(([key, val]) => {
          switch (key) {
            case "expires":
              return [];
            case "mac":
              return [`mac`, val ?? ""];
            case "hostname":
              return [`hostname`, val ?? ""];
            case "ip_addresses":
              return [`ip_address`, val ?? ""];
            case "group_owners":
              return [`group`, val ?? ""];
            default:
              return [key, val ?? ""];
          }
        })
    ),
    ...getExpiresDateFromFilter(
      columnFilters.find((filter) => filter.id === "expires")?.value as
        | string
        | undefined
    ),
    page_size: pageSize,
    page,
    ordering: getOrdering(columnSort),
    show_groups: showGroups,
  });
  const Hosts = useMemo<Host[]>(() => {
    if (!data.data) {
      return prevData.length ? prevData : [];
    }
    return data.data.pages.flatMap((page) => page.results);
  }, [data.data]);

  useEffect(() => {
    if (data.data) {
      setPrevData(() => [...data.data.pages.flatMap((page) => page.results)]);
    }
  }, [data.data]);

  const columnHelper = createColumnHelper<Host>();
  const columns = [
    ...ActionsColumn({
      data,
      size: 100,
      pageSize,
      setPageSize,
      enableSelection: true,
      onSelectColumns: p.onSelectColumns,
      onView: (row) => {
        navigate(`/Hosts/${row.mac}`);
      },
      onRenew: (row) => {
        p.setRenewModule({
          show: true,
          data: [row],
        });
      },
      customHead: (
        <div
          className="tooltip tooltip-right"
          data-tip={`${showGroups ? "Hide" : "Show"} Groups`}
        >
          <button
            className="btn btn-circle btn-ghost btn-xs"
            onClick={() => {
              setShowGroups((prev) => !prev);
            }}
          >
            {showGroups ? (
              <People
                fontSize="small"
                color="inherit"
                style={{ fill: "inherit" }}
              />
            ) : (
              <PeopleOutline
                fontSize="small"
                color="inherit"
                style={{ fill: "inherit" }}
              />
            )}
          </button>
        </div>
      ),
    }),
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "mac",
          header: "Mac",
          accessorFn: (row) => row.mac,
        },
        {
          id: "hostname",
          header: "Hostname",
          accessorFn: (row) => row.hostname,
        },
      ],
    }),
    columnHelper.group({
      id: "Primary Details",
      header: "Primary Details",
      columns: [
        {
          id: "expires",
          header: "Expires",
          accessorFn: (row) =>
            row.expires
              ? new Date(row.expires).toISOString().split("T")[0]
              : null,
          cell: ({ row }: { row: any }) => {
            return row.original.expires ? (
              <div className="flex flex-row justify-between mx-2">
                <p className="flex align-middle">{`${
                  row.original.expires
                    ? new Date(row.original.expires).toISOString().split("T")[0]
                    : ""
                }`}</p>
                <p className="flex align-middle">{`(${
                  new Date(row.original.expires) < new Date()
                    ? "Expired"
                    : `${Math.ceil(
                        (new Date(row.original.expires).getTime() -
                          new Date().getTime()) /
                          (1000 * 3600 * 24)
                      )} Days Left`
                })`}</p>
              </div>
            ) : (
              ""
            );
          },
          meta: {
            filterType: "date",
          },
        },
        {
          id: "ip_addresses",
          header: "IP Addresses",
          cell: ({ row }: { row: any }) => {
            return row.original.master_ip_address ||
              row.addresses?.leased?.[0] ? (
              <div className="flex flex-row">
                <a
                  className="text-blue-500 hover:underline btn btn-sm btn-ghost"
                  href={`#/addresses/${
                    row.original.master_ip_address ?? row.addresses?.leased?.[0]
                  }`}
                >{`${
                  row.original.master_ip_address ??
                  row.original.addresses?.leased?.[0]
                }`}</a>
                <p className="flex align-middle m-auto">{`(${
                  row.original.addresses?.leased?.length +
                  row.original.addresses?.static?.length
                })`}</p>
              </div>
            ) : (
              <p className="flex align-middle m-auto">No IP Address</p>
            );
          },
          accessorFn: (row) =>
            `${row.master_ip_address ?? row.addresses?.leased?.[0]}
             (${
               row.addresses?.leased?.length + row.addresses?.static?.length
             })`,
        },
      ],
    }),
  ];

  const table = CreateTable({
    data: Hosts,
    setColumnFilters,
    setRowSelection,
    setColumnSort,
    setColumnVisibility,
    state: {
      columnFilters,
      rowSelection,
      pageSize,
      sorting: columnSort,
      columnVisibility,
    },
    meta: {
      total: data.data?.pages?.[0]?.count,
      pageSize,
      page,
      setPage,
      trProps: (row: any) => {
        return {
          className:
            row.expires && new Date(row.expires) < new Date()
              ? "bg-red-500 bg-opacity-70"
              : "",
        };
      },
      rowActions: (rows: Host[]) => {
        return (
          <HostTableActions
            rows={rows}
            table={table}
            setActionModule={p.setActionModule}
            setRenewModule={p.setRenewModule}
            setAttributeModule={p.setAttributeModule}
          />
        );
      },
    },
    columns,
  });

  return useMemo(() => ({ table, loading: data.isFetching }), [
    table,
    data.isFetching,
  ]);
};
