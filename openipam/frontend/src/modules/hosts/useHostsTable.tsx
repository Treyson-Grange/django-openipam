import {
  ColumnFiltersState,
  createColumnHelper,
  getCoreRowModel,
  getFacetedMinMaxValues,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useEffect, useMemo, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { betweenDatesFilter, fuzzyFilter } from "../../components/filters";
import React from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import {
  Add,
  Autorenew,
  Edit,
  ExpandMore,
  Visibility,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { Host } from "../../utils/types";
import { BooleanRender, booleanAccessor } from "../../components/boolean";

//TODO disabled columns only shows for admins.

export const useInfiniteHosts = (p: { [key: string]: string | number }) => {
  const api = useApi();
  const query = useInfiniteQuery({
    queryKey: ["Hosts, all", ...Object.entries(p).flat()],
    queryFn: async ({ pageParam = 1 }) => {
      const results = await api.hosts.get({
        page: pageParam,
        ...Object.fromEntries(Object.entries(p).filter(([_, val]) => val)),
      });
      return {
        results: results.results,
        page: pageParam,
        nextPage: results.next,
      };
    },
    getNextPageParam: (lastPage) => {
      return lastPage.nextPage ? lastPage.page + 1 : undefined;
    },
  });
  useEffect(() => {
    const currentPage = query.data?.pages.at(-1)?.page ?? 0;
    if (query.hasNextPage && !query.isFetchingNextPage && currentPage < 1) {
      query.fetchNextPage();
    }
  }, [
    query.hasNextPage,
    query.isFetchingNextPage,
    query.fetchNextPage,
    query.data,
  ]);
  return query;
};

export const useHostsTable = (p: {
  setShowAddHost: React.Dispatch<React.SetStateAction<boolean>>;
  setEditHost: React.Dispatch<
    React.SetStateAction<{ show: boolean; HostData: Host | undefined }>
  >;
  setRenewModule: React.Dispatch<
    React.SetStateAction<{ show: boolean; data: Host | undefined }>
  >;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState();
  const [columnVisibility, setColumnVisibility] = useState({});
  const [prevData, setPrevData] = useState<Host[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    if (columnFilters.length !== 0) {
      console.log(columnFilters);
    }
  }, [columnFilters]);

  const data = useInfiniteHosts({
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
            case "group_owners":
              return [`group`, val ?? ""];
            default:
              return [key, val ?? ""];
          }
        })
    ),
    expires__gt: (columnFilters.find((filter) => filter.id === "expires")
      ?.value as (string | undefined)[])?.[0],
    expires__lt: (columnFilters.find((filter) => filter.id === "expires")
      ?.value as (string | undefined)[])?.[1],
    changed_gt: (columnFilters.find((filter) => filter.id === "changed")
      ?.value as string[])?.[1],
    changed__lt: (columnFilters.find((filter) => filter.id === "changed")
      ?.value as string[])?.[1],
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
    {
      size: 100,
      enableHiding: false,
      enableSorting: false,
      enableColumnFilter: false,
      id: "actions",
      header: ({ table }: any) => (
        <div className="flex gap-1 items-center relative">
          {/* <PlainIndeterminateCheckbox
              checked={table.getIsAllRowsSelected()}
              indeterminate={table.getIsSomeRowsSelected()}
              onChange={table.getToggleAllRowsSelectedHandler()}
            /> */}
          <div className="tooltip tooltip-right" data-tip="Load More">
            <button
              className="btn btn-circle btn-ghost btn-xs mt-1"
              onClick={() => data.fetchNextPage?.()}
              disabled={!data.hasNextPage || data.isFetchingNextPage}
            >
              <ExpandMore />
            </button>
          </div>
          <button
            className="btn btn-circle btn-ghost btn-xs"
            onClick={() => {
              p.setShowAddHost((prev: boolean) => !prev);
            }}
          >
            <Add />
          </button>
        </div>
      ),
      cell: ({ row }: { row: any }) => (
        <div className="flex gap-1 items-center">
          {/* <PlainIndeterminateCheckbox
              checked={row.getIsSelected()}
              onChange={row.getToggleSelectedHandler()}
              disabled={!row.getCanSelect()}
              indeterminate={row.getIsSomeSelected()}
            /> */}
          <button
            className="btn btn-circle btn-ghost btn-xs"
            onClick={() => navigate(`/Hosts/${row.original.mac}`)}
            disabled={!row.original.mac}
          >
            <Visibility fontSize="small" />
          </button>
          <button
            className="btn btn-circle btn-ghost btn-xs"
            onClick={() => {
              p.setEditHost({
                show: true,
                HostData: row.original,
              });
            }}
          >
            <Edit fontSize="small" />
          </button>
          <button
            className="btn btn-circle btn-ghost btn-xs"
            onClick={() => {
              p.setRenewModule({
                show: true,
                data: row.original,
              });
            }}
          >
            <Autorenew fontSize="small" />
          </button>
        </div>
      ),
    },
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "mac",
          header: "Mac",
          accessorFn: (row) => row.mac,
          meta: {
            filterType: "string",
          },
          filterFn: undefined,
        },
        {
          id: "hostname",
          header: "Hostname",
          accessorFn: (row) => row.hostname,
          meta: {
            filterType: "string",
          },
          filterFn: undefined,
        },
      ],
    }),
    columnHelper.group({
      id: "Primary Details",
      header: "Primary Details",
      columns: [
        {
          id: "expires",
          size: 200,
          header: "Expires",
          accessorFn: (row) =>
            row.expires
              ? new Date(row.expires).toISOString().split("T")[0]
              : null,
          cell: ({ row }: { row: any }) => {
            return row?.original.expires ? (
              <div className="flex flex-col">
                <p className="flex flex-row justify-start">{`${
                  row.original.expires
                    ? new Date(row.original.expires).toISOString().split("T")[0]
                    : ""
                }`}</p>
                <p className="flex flex-row justify-end">{`(${
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
          filterFn: undefined,
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
          meta: {
            filterType: "string",
          },
        },
        {
          id: "dhcp_group",
          header: "DHCP Group",
          accessorFn: (row) => row.dhcp_group?.name,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "disabled_host",
          size: 75,
          header: "Disabled Host",
          accessorFn: booleanAccessor("disabled_host"),
          cell: BooleanRender,
          meta: {
            filterType: "boolean",
          },
        },
        {
          id: "is_dynamic",
          size: 75,
          header: "Dynamic",
          cell: BooleanRender,
          accessorFn: booleanAccessor("is_dynamic"),
          meta: {
            filterType: "boolean",
          },
        },
      ],
    }),
    columnHelper.group({
      id: "Owners",
      header: "Owners",
      columns: [
        {
          id: "user_owners",
          header: "User Owners",
          size: 200,
          accessorFn: (row) => row.user_owners?.join(",\n"),
          meta: {
            filterType: "string",
          },
        },
        {
          id: "group_owners",
          header: "Group Owners",
          size: 200,
          accessorFn: (row) => row.group_owners?.join(",\n"),
          meta: {
            filterType: "string",
          },
        },
      ],
    }),
    // columnHelper.group({
    //   id: "Changed",
    //   header: "Changed",
    //   columns: [
    //     {
    //       id: "changed",
    //       header: "Last Changed",
    //       accessorFn: (row) =>
    //         row.changed
    //           ? new Date(row.changed).toISOString().split("T")[0]
    //           : null,
    //       meta: {
    //         filterType: "date",
    //       },
    //       filterFn: betweenDatesFilter,
    //     },
    //     {
    //       id: "changedBy",
    //       header: "Changed By",
    //       accessorFn: (row) => row.changed_by.username,
    //       meta: {
    //         filterType: "string",
    //       },
    //     },
    //   ],
    // }),
  ];

  const table = useReactTable({
    getCoreRowModel: getCoreRowModel(),
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
    getFacetedMinMaxValues: getFacetedMinMaxValues(),
    // Sorting
    getSortedRowModel: getSortedRowModel(),
    // Filters
    onColumnFiltersChange: setColumnFilters,
    getFilteredRowModel: getFilteredRowModel(),
    onGlobalFilterChange: setGlobalFilter,
    globalFilterFn: fuzzyFilter,
    onColumnVisibilityChange: setColumnVisibility,
    data: Hosts,
    state: {
      columnFilters,
      get globalFilter() {
        return globalFilter;
      },
      set globalFilter(value) {
        setGlobalFilter(value);
      },
      columnVisibility,
    },
    meta: {
      trProps: (row: any) => {
        return {
          className:
            row.expires && new Date(row.expires) < new Date()
              ? "bg-red-500 bg-opacity-70"
              : "",
        };
      },
    },
    columns,
    filterFns: {
      fuzzy: fuzzyFilter,
    },
  });

  return useMemo(() => ({ table, loading: data.isFetching }), [
    table,
    data.isFetching,
  ]);
};
