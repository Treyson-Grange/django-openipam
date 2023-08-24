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

//TODO disabled columns only shows for admins.

export const useHostsTable = (p: {
  setShowAddHost: React.Dispatch<React.SetStateAction<boolean>>;
  setEditHost: React.Dispatch<
    React.SetStateAction<{ show: boolean; HostData: Host | undefined }>
  >;
  setRenewModule: React.Dispatch<
    React.SetStateAction<{ show: boolean; data: Host[] | undefined }>
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
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [rowSelection, setRowSelection] = useState({});
  const [columnSort, setColumnSort] = useState<any[]>([]);
  const [prevData, setPrevData] = useState<Host[]>([]);
  const [globalFilter, setGlobalFilter] = useState<string>("");
  const [pageSize, setPageSize] = useState<number>(10);
  const auth = useAuth();
  const addressTypes = useAddressTypes().data?.addressTypes;
  const [selectAll, setSelectAll] = useState<boolean>(false);

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
        })
    ),
    ...getExpiresDateFromFilter(
      columnFilters.find((filter) => filter.id === "expires")?.value as
        | string
        | undefined
    ),
    page_size: pageSize,
    selectAll,
    ordering: getOrdering(columnSort),
  });

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

  const table = CreateTable({
    data: Hosts,
    setColumnFilters,
    setRowSelection,
    setGlobalFilter,
    setColumnSort,
    state: {
      columnFilters,
      rowSelection,
      globalFilter,
      pageSize,
      sorting: columnSort,
    },
    meta: {
      total: data.data?.pages?.[0]?.count,
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
      pageSize,
    },
    columns: HostTableColumns({
      data,
      setShowAddHost: p.setShowAddHost,
      setEditHost: p.setEditHost,
      setRenewModule: p.setRenewModule,
      setActionModule: p.setActionModule,
      pageSize,
      setPageSize,
      setSelectAll,
      auth,
    }),
  });

  useEffect(() => {
    if (!selectAll || table.getIsAllRowsSelected()) return;
    table.resetRowSelection(true);
    table.toggleAllRowsSelected();
  }, [Hosts, selectAll]);

  return useMemo(() => ({ table, loading: data.isFetching }), [
    table,
    data.isFetching,
    Hosts,
    data.data,
  ]);
};

const getExpiresDateFromFilter = (
  filterValue: string | undefined
): {
  expires__lt?: string;
  expires__gt?: string;
} => {
  //values are 'Expired, 1 day left, 7 days left, 30 days left, all'
  switch (filterValue) {
    case "Expired":
      return {
        expires__lt: new Date().toISOString().split("T")[0],
      };
    case "1 Day Left":
      return {
        expires__lt: new Date(new Date().setDate(new Date().getDate() + 1))
          .toISOString()
          .split("T")[0],
        expires__gt: new Date().toISOString().split("T")[0],
      };
    case "7 Days Left":
      return {
        expires__lt: new Date(new Date().setDate(new Date().getDate() + 7))
          .toISOString()
          .split("T")[0],
        expires__gt: new Date().toISOString().split("T")[0],
      };
    case "30 Days Left":
      return {
        expires__lt: new Date(new Date().setDate(new Date().getDate() + 30))
          .toISOString()
          .split("T")[0],
        expires__gt: new Date().toISOString().split("T")[0],
      };
    case "Unexpired":
      return {
        expires__gt: new Date().toISOString().split("T")[0],
      };
    default:
      return {};
  }
};

const getOrdering = (columnSort: any[]) => {
  return columnSort
    .map((sort) => {
      if (sort.desc) {
        return `-${sort.id}`;
      } else {
        return sort.id;
      }
    }, [])
    .join(",");
};
