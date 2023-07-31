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
import {
  betweenDatesFilter,
  fuzzyFilter,
  stringFilter,
} from "../../components/filters";
import React from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import {
  Add,
  Edit,
  ExpandMore,
  MoreVert,
  Visibility,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";

//TODO permissions, add, edit

type Domain = {
  id: number;
  name: string;
  description: string;
  changed_by: string;
  master: string;
  last_check: string;
  type: string;
  notified_serial: string;
  account: string;
  changed: string;
};

export const useInfiniteDomains = () => {
  const api = useApi();
  const query = useInfiniteQuery({
    queryKey: ["domains, all"],
    queryFn: async ({ pageParam = 1 }) => {
      const results = await api.domains.get({ page: pageParam });
      return { results: results.results, page: pageParam };
    },
    getNextPageParam: (lastPage) => {
      return lastPage.results.length > 0 ? lastPage.page + 1 : undefined;
    },
  });
  useEffect(() => {
    const currentPage = query.data?.pages.at(-1)?.page ?? 0;
    if (query.hasNextPage && !query.isFetchingNextPage && currentPage < 10) {
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

export const useDomainsTable = () => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState();
  const [columnVisibility, setColumnVisibility] = useState({});
  const [prevData, setPrevData] = useState<Domain[]>([]);
  const navigate = useNavigate();

  const data = useInfiniteDomains();
  const domains = useMemo<Domain[]>(() => {
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

  const columnHelper = createColumnHelper<Domain>();
  const columns = [
    {
      size: 50,
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
              alert("TODO: create domain");
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
            onClick={() => navigate(`/domains/${row.original.name}`)}
            disabled={!row.original.name}
          >
            <Visibility fontSize="small" />
          </button>
          <button
            className="btn btn-circle btn-ghost btn-xs"
            onClick={() => {
              alert("TODO: edit ");
            }}
          >
            <Edit fontSize="small" />
          </button>
        </div>
      ),
    },
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "name",
          header: "Name",
          accessorFn: (row) => row.name,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "description",
          header: "Description",
          accessorFn: (row) => row.description,
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
          id: "master",
          header: "Master",
          accessorFn: (row) => row.master,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "changed",
          header: "Last Changed",
          accessorFn: (row) =>
            row.changed
              ? new Date(row.changed).toISOString().split("T")[0]
              : null,
          meta: {
            filterType: "date",
          },
          filterFn: betweenDatesFilter,
        },
        {
          id: "changedBy",
          header: "Changed By",
          accessorFn: (row) => row.changed_by,
          meta: {
            filterType: "string",
          },
        },
        {
          id: "last_check",
          header: "Last Check",
          accessorFn: (row) => row.last_check,
          meta: {
            filterType: "string",
          },
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
    data: domains,
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

  return useMemo(() => ({ table, loading: data.isFetching }), [
    table,
    data.isFetching,
  ]);
};
