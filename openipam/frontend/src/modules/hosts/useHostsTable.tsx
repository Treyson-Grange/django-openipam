import { ColumnFiltersState } from "@tanstack/react-table";
import { ReactNode, useEffect, useMemo, useState } from "react";
import React from "react";
import { Host } from "../../utils/types";
import { useInfiniteHosts } from "../../hooks/queries/useInfiniteHosts";
import { HostTableActions } from "./hostTableActions";
import { HostTableColumns } from "./hostTableColumns";
import { CreateTable } from "../../components/table/createTable";
import { useAuth } from "../../hooks/useAuth";
import { useAddressTypes } from "../../hooks/queries/useAddressTypes";
import { HostGlobalAutocomplete } from "./hostGlobalAutocomplete";
import { getOrdering } from "../../components/table/getOrdering";
import { getExpiresDateFromFilter } from "./expiresDateFilter";

export const useHostsTable = (p: useHostsTableProps) => {
  const auth = useAuth();
  const [loading, setLoading] = useState<boolean>(false);

  //Table state
  const [pageSize, setPageSize] = useState<number>(10);
  const [page, setPage] = useState<number>(1);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [rowSelection, setRowSelection] = useState({});
  const [columnSort, setColumnSort] = useState<any[]>([]);
  const [globalFilter, setGlobalFilter] = useState<
    { id: string; text: string }[]
  >([]);

  //Select All Rows feature
  const [selectAll, setSelectAll] = useState<boolean>(false);

  //Table column visibility state
  const [columnVisibility, setColumnVisibility] = useState<any>(
    localStorage.getItem("hostsTableColumns")
      ? JSON.parse(localStorage.getItem("hostsTableColumns")!)
      : {
          dhcp_group: false,
          address_type: false,
          group_owners: false,
          user_owners: false,
          disabled_host: false,
          description: false,
          changed: false,
          changed_by: false,
        }
  );
  useEffect(() => {
    localStorage.setItem("hostsTableColumns", JSON.stringify(columnVisibility));
  }, [columnVisibility]);

  //onMount, get Table state from local storage
  useEffect(() => {
    const filterState = localStorage.getItem("hostsTableFilters");
    if (filterState) {
      const {
        columnFilters,
        columnSort,
        globalFilter,
        page,
        pageSize,
      } = JSON.parse(filterState);
      setColumnFilters(columnFilters);
      setColumnSort(columnSort);
      setGlobalFilter(globalFilter);
      setPage(page);
      setPageSize(pageSize);
      setLoading(true);
    }
  }, []);
  useEffect(() => {
    if (!loading) return;
    localStorage.setItem(
      "hostsTableFilters",
      JSON.stringify({
        columnFilters,
        columnSort,
        globalFilter,
        page,
        pageSize,
      })
    );
  }, [columnFilters, columnSort, globalFilter, page, pageSize]);

  //For the custom Quick Filters feature
  useEffect(() => {
    setSelectAll(false);
    p.setCurrentFilters({ columnFilters, columnSort, globalFilter });
  }, [columnFilters, columnSort, globalFilter]);

  useEffect(() => {
    if (!p.customFilters) return;
    setColumnFilters(p.customFilters.columnFilters ?? []);
    setColumnSort(p.customFilters.columnSort ?? []);
    setGlobalFilter(p.customFilters.globalFilter ?? []);
  }, [p.customFilters]);

  //Hosts data
  const data = useInfiniteHosts({
    ...Object.fromEntries(
      columnFilters.map((filter) => getKeyVal([filter.id, filter.value]))
    ),
    ...getExpiresDateFromFilter(
      columnFilters.find((filter) => filter.id === "expires")?.value as
        | string
        | undefined
    ),
    page_size: pageSize,
    page,
    selectAll,
    ordering: getOrdering(
      columnSort,
      new Map([
        ["ip_addresses", "addresses"],
        ["dhcp_group", "dhcp_group__name"],
        // ["address_type", "address_type__id"],
      ])
    ),
    advanced_search: globalFilter.map((filter) => filter.id).join(","),
    quickFilter: p.quickFilter,
  });

  // Flatten the data from the infinite query, use previous state if fetching
  const [prevData, setPrevData] = useState<Host[]>([]);
  const Hosts = useMemo<Host[]>(() => {
    if (data.isFetching) {
      return [];
    }
    if (!data.data) {
      return prevData.length ? prevData : [];
    }
    return data.data.pages.flatMap((page) => page.results);
  }, [data.data]);

  useEffect(() => {
    if (data.data) {
      setPrevData(() => [
        ...data.data.pages.flatMap((page) => page.results ?? []),
      ]);
    }
  }, [data.data]);

  //Table
  const table = CreateTable({
    data: Hosts,
    setColumnFilters,
    setRowSelection,
    setColumnSort,
    setColumnVisibility,
    setGlobalFilter,
    state: {
      columnFilters,
      rowSelection,
      globalFilter,
      pageSize,
      sorting: columnSort,
      columnVisibility,
    },
    orderingColumns,
    meta: {
      setSorting: setColumnSort,
      total: data.data?.pages?.[0]?.count,
      pageSize,
      page,
      setPage,
      globalFilter: (
        <HostGlobalAutocomplete
          onAddFilter={(v) => {
            setGlobalFilter((prev) => [...prev, v]);
          }}
        />
      ),
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
            refetch={data.refetch}
          />
        );
      },
    },
    columns: HostTableColumns({
      ...p,
      data,
      pageSize,
      setPageSize,
      setSelectAll,
      auth,
    }),
  });

  //Select All Rows feature
  useEffect(() => {
    if (!selectAll || table.getIsAllRowsSelected()) return;
    table.resetRowSelection(true);
    table.toggleAllRowsSelected();
  }, [Hosts, selectAll]);

  return useMemo(() => ({ table, loading: data.isFetching }), [
    table,
    data.isFetching,
  ]);
};

const orderingColumns = [
  "mac",
  "hostname",
  "expires",
  "dhcp_group",
  "ip_addresses",
  "changed",
];

const getKeyVal = ([key, val]: any[]): any[] => {
  //to map address type name to id
  const addressTypes = useAddressTypes().data?.addressTypes;
  switch (key) {
    case "expires":
      return [];
    case "group_owners":
      return [`group`, val ?? ""];
    case "user_owners":
      return [`user`, val ?? ""];
    case "disabled_host":
      return [`disabled`, val];
    case "ip_addresses":
      return [`ip_address`, val ?? ""];
    case "address_type":
      return [
        `address_type`,
        addressTypes?.find((t) => t.name === val)?.id ?? "",
      ];
    default:
      return [key, val ?? ""];
  }
};

type useHostsTableProps = {
  setShowAddHost: React.Dispatch<React.SetStateAction<boolean>>;
  setEditHost: React.Dispatch<
    React.SetStateAction<{ show: boolean; HostData: Host | undefined }>
  >;
  setRenewModule: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      data: Host[] | undefined;
      refetch: VoidFunction;
    }>
  >;
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
  onSelectColumns: VoidFunction;
  onAddByCsv: VoidFunction;
  quickFilter?: string[][];
  setCurrentFilters: (filters: {
    columnFilters: ColumnFiltersState;
    columnSort: any[];
    globalFilter: { id: string; text: string }[];
  }) => void;
  customFilters?: {
    columnFilters: ColumnFiltersState;
    columnSort: any[];
    globalFilter: { id: string; text: string }[];
  };
};
