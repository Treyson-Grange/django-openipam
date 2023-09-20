import { ColumnFiltersState, createColumnHelper } from "@tanstack/react-table";
import { ReactNode, useEffect, useMemo, useState } from "react";
import React from "react";
import { User } from "../../utils/types";
import { ActionsColumn } from "../../components/table/actionsColumn";
import { CreateTable } from "../../components/table/createTable";
import { useInfiniteUsers } from "../../hooks/queries/useInfiniteUsers";
import { BooleanRender, booleanAccessor } from "../../components/table/boolean";
import { getOrdering } from "../../components/table/getOrdering";
import { UserTableActions } from "./userTableActions";

export const useUsersTable = (p: {
  setActionModule: React.Dispatch<
    React.SetStateAction<{
      show: boolean;
      data: User[] | undefined;
      title: string;
      onSubmit?: (data: User[]) => void;
      children: ReactNode;
      multiple?: boolean;
    }>
  >;
  onSelectColumns: VoidFunction;
}) => {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [prevData, setPrevData] = useState<User[]>([]);
  const [rowSelection, setRowSelection] = useState({});
  const [columnSort, setColumnSort] = useState<any[]>([]);
  const [columnVisibility, setColumnVisibility] = useState<any>(
    localStorage.getItem("usersTableColumns")
      ? JSON.parse(localStorage.getItem("usersTableColumns")!)
      : {
          first_name: false,
          last_name: false,
          date_joined: false,
          is_active: false,
        }
  );
  useEffect(() => {
    localStorage.setItem("usersTableColumns", JSON.stringify(columnVisibility));
  }, [columnVisibility]);
  const [pageSize, setPageSize] = useState<number>(25);
  const [page, setPage] = useState<number>(1);
  const data = useInfiniteUsers({
    ...Object.fromEntries(
      columnFilters
        .filter((f) => f.value !== undefined && f.value !== null)
        .map((filter) => [filter.id, filter.value as string])
        .map(([id, value]) => {
          if (id === "is_staff") return [id, value === "Y" ? true : false];
          if (id === "is_ipamadmin") return [id, value === "Y" ? true : false];
          if (id === "is_superuser") return [id, value === "Y" ? true : false];
          if (id === "is_active") return [id, value === "Y" ? true : false];

          return [id, value];
        })
    ),
    ordering: getOrdering(columnSort),
    page,
    page_size: pageSize,
  });
  const dns = useMemo<User[]>(() => {
    if (!data.data) {
      return prevData.length ? prevData : [];
    }
    return data.data.pages.flatMap((page) => page.users);
  }, [data.data]);

  useEffect(() => {
    if (data.data) {
      setPrevData(() => [...data.data.pages.flatMap((page) => page.users)]);
    }
  }, [data.data]);

  const columnHelper = createColumnHelper<User>();
  const columns = [
    ...ActionsColumn({
      size: 100,
      data,
      pageSize,
      setPageSize,
      enableSelection: true,
      onSelectColumns: p.onSelectColumns,
    }),
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "username",
          header: "Username",
          accessorFn: (row) => row.username,
        },
        {
          id: "fullname",
          header: "Full Name",
          accessorFn: (row) => row.first_name + " " + row.last_name,
        },
        {
          id: "first_name",
          header: "First Name",
          accessorFn: (row) => row.first_name,
        },
        {
          id: "last_name",
          header: "Last Name",
          accessorFn: (row) => row.last_name,
        },
        {
          id: "email",
          header: "Email",
          accessorFn: (row) => row.email,
        },
      ],
    }),
    columnHelper.group({
      id: "Permissions",
      header: "Permissions",
      columns: [
        {
          id: "is_staff",
          header: "Staff",
          accessorFn: booleanAccessor("is_staff"),
          cell: BooleanRender,
          meta: {
            filterType: "boolean",
          },
        },
        {
          id: "is_ipamadmin",
          header: "Admin",
          accessorFn: booleanAccessor("is_ipamadmin"),
          cell: BooleanRender,
          meta: {
            filterType: "boolean",
          },
        },
        {
          id: "is_superuser",
          header: "Superuser",
          accessorFn: booleanAccessor("is_superuser"),
          cell: BooleanRender,
          meta: {
            filterType: "boolean",
          },
        },
        {
          id: "is_active",
          header: "Active",
          accessorFn: booleanAccessor("is_active"),
          cell: BooleanRender,
          meta: {
            filterType: "boolean",
          },
        },
      ],
    }),
    columnHelper.group({
      id: "Other Details",
      header: "Other Details",
      columns: [
        {
          id: "groups",
          header: "Groups",
          accessorFn: (row) => row.groups.join(", "),
        },
        {
          id: "source",
          header: "Source",
          accessorFn: (row) => row.source,
          meta: {
            filterOptions: ["LDAP", "INTERNAL"],
            filterType: "exact",
          },
        },
        {
          id: "last_login",
          header: "Last Login",
          accessorFn: (row) =>
            row.last_login
              ? new Date(row.last_login).toLocaleDateString()
              : null,
          meta: {
            filterType: "date",
          },
        },
        {
          id: "date_joined",
          header: "Date Joined",
          accessorFn: (row) =>
            row.date_joined
              ? new Date(row.date_joined).toLocaleDateString()
              : null,
          meta: {
            filterType: "date",
          },
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
    orderingColumns: [
      "username",
      "first_name",
      "last_name",
      "email",
      "is_active",
      "source",
      "last_login",
    ],
    columns,
    meta: {
      total: data.data?.pages?.[0]?.count,
      page,
      pageSize,
      setSorting: setColumnSort,
      setPage,
      rowActions: (rows: User[]) => {
        return (
          <UserTableActions
            rows={rows}
            table={table}
            setActionModule={p.setActionModule}
            refetch={data.refetch}
          />
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
