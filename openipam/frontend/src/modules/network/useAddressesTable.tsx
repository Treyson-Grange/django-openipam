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
import { betweenDatesFilter, fuzzyFilter } from "../../components/filters";
import React from "react";
import { Address } from "../../utils/types";
import { BooleanRender, booleanAccessor } from "../../components/boolean";
import { useInfiniteNetworkAddresses } from "../../hooks/queries/useInfiniteNetworkAddresses";
import { ActionsColumn } from "../../components/actionsColumn";

const AddressLookupKeys = ["address", "name", "gateway", "description"];

export const useAddressesTable = (p: {
  network: string;
  subnet: string;
  setShowModule: any;
  setEditModule: any;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState();
  const [columnVisibility, setColumnVisibility] = useState({});
  const [prevData, setPrevData] = useState<Address[]>([]);

  const data = useInfiniteNetworkAddresses({
    network: p.network,
    subnet: p.subnet,
    ...Object.fromEntries(
      columnFilters
        .filter((f) => AddressLookupKeys.includes(f.id) && f.value)
        .map((filter) => [filter.id, filter.value as string])
    ),
  });
  const dns = useMemo<Address[]>(() => {
    if (!data.data) {
      return prevData.length ? prevData : [];
    }
    return data.data.pages.flatMap((page) => page.addresses);
  }, [data.data]);

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
      onAdd: () => {
        p.setShowModule(true);
      },
      onEdit: (row) => {
        p.setEditModule({
          show: true,
          Address: row.address,
        });
      },
    }),
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "address",
          header: "Address",
          accessorFn: (row) => row.address,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "host",
          header: "host",
          accessorFn: (row) => row.host,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "gateway",
          header: "Gateway",
          accessorFn: (row) => row.gateway,
          meta: {
            filterType: "string",
          },
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
          meta: {
            filterType: "string",
          },
        },
        {
          id: "changed",
          header: "Changed",
          accessorFn: (row) =>
            row.changed ? new Date(row.changed).toLocaleString() : "",
          meta: {
            filterType: "date",
          },
          filterFn: betweenDatesFilter,
        },
      ],
    }),
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
    data: dns,
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
    columns,
    filterFns: {
      fuzzy: fuzzyFilter,
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
