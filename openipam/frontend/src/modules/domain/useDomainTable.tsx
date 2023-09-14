import { ColumnFiltersState, createColumnHelper } from "@tanstack/react-table";
import { ReactNode, useContext, useEffect, useMemo, useState } from "react";
import React from "react";
import { DNS_TYPES, DnsRecord } from "../../utils/types";
import { useInfiniteDnsRecords } from "../../hooks/queries/useInfiniteDnsRecords";
import { ActionsColumn } from "../../components/table/actionsColumn";
import { CreateTable } from "../../components/table/createTable";
import { useApi } from "../../hooks/useApi";
import { ThemeContext } from "../../hooks/useTheme";
import { getOrdering } from "../../components/table/getOrdering";

//TODO search permissions

const DNSLookupKeys = ["name", "content", "dns_type", "host"];

export const useDomainTable = (p: {
  domain: string;
  setShowModule: any;
  setEditModule: any;
  setActionModule: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      data: DnsRecord[] | undefined;
      title: string;
      onSubmit?: (data: DnsRecord[]) => void;
      children: ReactNode;
      multiple?: boolean;
    }>
  >;
  onSelectColumns: () => void;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [prevData, setPrevData] = useState<DnsRecord[]>([]);
  const [rowSelection, setRowSelection] = useState({});
  const [columnSort, setColumnSort] = useState<any[]>([]);
  const [pageSize, setPageSize] = useState<number>(10);
  const [page, setPage] = useState<number>(1);
  const [columnVisibility, setColumnVisibility] = useState<any>(
    localStorage.getItem("domainTableColumns")
      ? JSON.parse(localStorage.getItem("domainTableColumns")!)
      : {}
  );
  useEffect(() => {
    localStorage.setItem(
      "domainDNSTableColumns",
      JSON.stringify(columnVisibility)
    );
  }, [columnVisibility]);
  const [action, setAction] = useState<string>("delete");
  const api = useApi();
  const data = useInfiniteDnsRecords({
    domain: p.domain,
    ...Object.fromEntries(
      columnFilters
        .filter((f) => DNSLookupKeys.includes(f.id))
        .map((filter) => [filter.id, filter.value as string])
    ),
    ordering: getOrdering(columnSort),
    page,
    page_size: pageSize,
  });
  const dns = useMemo<DnsRecord[]>(() => {
    if (!data.data) {
      return prevData.length ? prevData : [];
    }
    return data.data.pages.flatMap((page) => page.dns);
  }, [data.data]);

  useEffect(() => {
    if (data.data) {
      setPrevData(() => [...data.data.pages.flatMap((page) => page.dns)]);
    }
  }, [data.data]);
  const { theme } = useContext(ThemeContext);
  const columnHelper = createColumnHelper<DnsRecord>();
  const columns = [
    ...ActionsColumn({
      size: 80,
      enableSelection: true,
      onAdd: () => {
        p.setShowModule(true);
      },
      data,
      onEdit: (row) => {
        p.setEditModule({
          show: true,
          DnsData: row,
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
          id: "name",
          header: "Name",
          accessorFn: (row) => row.name,
        },
        {
          id: "content",
          header: "Content",
          cell: ({ row }: { row: { original: DnsRecord } }) => {
            return row.original.dns_type === "A" ? (
              <a
                className={`${
                  theme === "dark" || theme === "black"
                    ? "text-secondary"
                    : "text-primary"
                } hover:underline btn btn-sm btn-ghost`}
                href={`#/addresses/${row.original.content}`}
              >
                {row.original.content}
              </a>
            ) : (
              row.original.content
            );
          },
          accessorFn: (row) => row.content,
        },
      ],
    }),
    columnHelper.group({
      id: "Other Details",
      header: "Other Details",
      columns: [
        {
          id: "dns_type",
          header: "Type",
          accessorFn: (row) => row.dns_type,
          meta: {
            filterType: "exact",
            filterOptions: DNS_TYPES,
          },
        },
        {
          id: "ttl",
          header: "Ttl",
          accessorFn: (row) => row.ttl,
        },
        {
          id: "host",
          header: "Host",
          cell: ({ row }: { row: { original: DnsRecord } }) => {
            return (
              <a
                className={`${
                  theme === "dark" || theme === "black"
                    ? "text-secondary"
                    : "text-primary"
                } hover:underline btn btn-sm btn-ghost`}
                href={`#/hosts/${row.original.host}`}
              >
                {row.original.host}
              </a>
            );
          },
          accessorFn: (row) => row.host,
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
    meta: {
      total: data.data?.pages?.[0]?.count,
      page,
      pageSize,
      setPage,
      rowActions: (rows: DnsRecord[]) => {
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
                          rows.forEach((row) => {
                            api.dns.byId(row.id).delete();
                          });
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
