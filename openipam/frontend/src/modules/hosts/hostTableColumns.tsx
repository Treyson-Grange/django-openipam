import { createColumnHelper } from "@tanstack/react-table";
import React, { ReactNode, useContext } from "react";
import { Host, User } from "../../utils/types";
import { ActionsColumn } from "../../components/table/actionsColumn";
import { useNavigate } from "react-router-dom";
import { UseInfiniteQueryResult } from "@tanstack/react-query";
import { ToolTip } from "../../components/tooltip";
import { useAddressTypes } from "../../hooks/queries/useAddressTypes";
import { MoreVert } from "@mui/icons-material";
import { BooleanRender, booleanAccessor } from "../../components/table/boolean";
import { ThemeContext } from "../../hooks/useTheme";

export const HostTableColumns = (p: {
  data: UseInfiniteQueryResult<
    {
      results: any;
      page: any;
      nextPage: any;
      count: number;
    },
    unknown
  >;
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
  onSelectColumns: VoidFunction;
  onAddByCsv: VoidFunction;
  pageSize: number;
  setPageSize: React.Dispatch<React.SetStateAction<number>>;
  setSelectAll: React.Dispatch<React.SetStateAction<boolean>>;
  auth: User | undefined;
}) => {
  const columnHelper = createColumnHelper<Host>();
  const addressTypes = useAddressTypes().data?.addressTypes;
  const navigate = useNavigate();
  const { theme } = useContext(ThemeContext);
  return [
    ...(p.auth?.is_ipamadmin
      ? ActionsColumn({
          data: p.data,
          pageSize: p.pageSize,
          setPageSize: p.setPageSize,
          setSelectAll: p.setSelectAll,
          enableSelection: true,
          onAdd: () => {
            p.setShowAddHost((prev: boolean) => !prev);
          },
          onEdit: (data) => {
            p.setEditHost({
              show: true,
              HostData: data,
            });
          },
          onView: (data) => {
            navigate(`/Hosts/${data.mac}`);
          },
          onRenew: (data) => {
            p.setRenewModule({
              show: true,
              data: [data],
              refetch: p.data.refetch,
            });
          },
          customHead: (
            <>
              <div className="dropdown mt-1">
                <label
                  tabIndex={0}
                  className="btn btn-circle btn-ghost btn-xs text-neutral"
                >
                  <MoreVert style={{ fill: "inherit" }} />
                </label>
                <ul
                  tabIndex={0}
                  className="dropdown-content menu p-2 shadow bg-neutral-focus rounded-box w-48 mt-2"
                >
                  <li onClick={p.onSelectColumns}>
                    <a className="text-neutral-content">Show/Hide Columns</a>
                  </li>
                  <li
                    onClick={() => {
                      p.setSelectAll(true);
                    }}
                  >
                    <ToolTip
                      text="Caution! Includes Unseen Rows!"
                      props="rounded-tr-none top-10 right-2"
                    >
                      <a className="text-neutral-content">Select ALL rows</a>
                    </ToolTip>
                  </li>
                  <li onClick={p.onAddByCsv}>
                    <a className="text-neutral-content">Add By CSV</a>
                  </li>
                </ul>
              </div>
            </>
          ),
        })
      : ActionsColumn({
          size: 100,
          data: p.data,
          pageSize: p.pageSize,
          setPageSize: p.setPageSize,
          onView: (data) => {
            navigate(`/Hosts/${data.mac}`);
          },
          customHead: (
            <>
              <div className="dropdown mt-1">
                <label
                  tabIndex={0}
                  className="btn btn-circle btn-ghost btn-xs text-neutral"
                >
                  <MoreVert style={{ fill: "inherit" }} />
                </label>
                <ul
                  tabIndex={0}
                  className="dropdown-content menu p-2 shadow bg-neutral-focus rounded-box w-48 mt-2"
                >
                  <li onClick={p.onSelectColumns}>
                    <a className="text-neutral-content">Show/Hide Columns</a>
                  </li>
                </ul>
              </div>
            </>
          ),
        })),
    columnHelper.group({
      id: "Identification",
      header: "Identification",
      columns: [
        {
          id: "mac",
          header: ({ table }: any) => (
            <div className="flex w-full gap-1 flex-row items-center justify-center m-auto">
              <p className="flex text-center text-neutral">Mac</p>
              <ToolTip
                text={
                  <div className="flex flex-col justify-center gap-1">
                    <div className="text-sm text-white">
                      Use . , : - or a space or no separator.
                    </div>
                    <div className="text-sm text-white">
                      Ex: XX.XX-XX,xx:XXXX
                    </div>
                    <div className="text-sm text-white">
                      Start with ~ for regex.
                    </div>
                    <div className="text-sm text-white">Ex: ~^24</div>
                    <div className="text-sm text-white">
                      Start with - to exclude.
                    </div>
                    <div className="text-sm text-white">Ex: -00</div>
                  </div>
                }
                props="-right-28 top-20 p-1"
              />
            </div>
          ),
          accessorFn: (row) => row.mac,
        },
        {
          size: 175,
          id: "hostname",
          header: ({ table }: any) => (
            <div className="flex w-full gap-1 flex-row items-center justify-center m-auto">
              <p className="flex text-center text-neutral">Hostname</p>
              <ToolTip
                text={
                  <div className="flex flex-col justify-center gap-1">
                    <div className="text-sm text-white">
                      Start with ~ for regex.
                    </div>
                    <div className="text-sm text-white">Ex: ~^A0</div>
                    <div className="text-sm text-white">
                      Start with - to exclude.
                    </div>
                    <div className="text-sm text-white">Ex: -bluezone</div>
                  </div>
                }
                props="-right-20 top-20 p-1"
              />
            </div>
          ),
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
          size: 120,
          header: "Expires",
          accessorFn: (row) =>
            row.expires
              ? new Date(row.expires).toISOString().split("T")[0]
              : null,
          cell: ({ row }: { row: any }) => {
            return row?.original.expires ? (
              <div className="flex flex-row flex-wrap">
                <p>{`${
                  new Date(row.original.expires) < new Date()
                    ? "Expired"
                    : `${Math.ceil(
                        (new Date(row.original.expires).getTime() -
                          new Date().getTime()) /
                          (1000 * 3600 * 24)
                      )} Days Left`
                }`}</p>
              </div>
            ) : (
              ""
            );
          },
          meta: {
            filterType: "exact",
            filterOptions: expiredFilterOptions.map((t) => t),
          },
        },
        {
          id: "ip_addresses",
          header: ({ table }: any) => (
            <div className="flex w-full gap-1 flex-row items-center justify-center m-auto">
              <p className="flex text-center text-neutral">IP Addresses</p>
              <ToolTip
                text="XX.XX.XX.XX"
                props="rounded-br-none right-4 bottom-4"
              />
            </div>
          ),
          cell: ({ row }: { row: any }) => {
            return row.original.master_ip_address ||
              row.addresses?.leased?.[0] ? (
              <div className="flex flex-row">
                <a
                  className={`${
                    theme === "dark" || theme === "black"
                      ? "text-secondary"
                      : "text-primary"
                  } hover:underline btn btn-sm btn-ghost`}
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
            row.master_ip_address ?? row.addresses?.leased?.[0],
        },
        {
          id: "vendor",
          size: 200,
          header: () => (
            <div className="flex w-full gap-1 flex-row items-center justify-center m-auto">
              <p className="flex text-center text-neutral">Vendor</p>
              <ToolTip
                text="This can be SLOW"
                props="rounded-br-none right-4 bottom-4"
              />
            </div>
          ),
          accessorFn: (row) => row.vendor?.split(",")[0],
        },
      ],
    }),
    columnHelper.group({
      id: "Last Seen",
      header: "Last Seen",
      columns: [
        {
          id: "last_seen",
          header: "Mac Last Seen",
          enableSorting: false,
          accessorFn: (row) =>
            row.last_seen
              ? `${Math.ceil(
                  (new Date(row.last_seen).getTime() - new Date().getTime()) /
                    (1000 * 3600 * 24)
                )} Days Ago`
              : "No Data",
          meta: {
            hideFilter: true,
          },
        },
        {
          id: "last_seen_ip",
          header: "IP Last Seen",
          enableSorting: false,
          accessorFn: (row) =>
            row.last_seen
              ? `${Math.ceil(
                  (new Date(row.last_seen).getTime() - new Date().getTime()) /
                    (1000 * 3600 * 24)
                )} Days Ago`
              : "No Data",
          meta: {
            hideFilter: true,
          },
        },
      ],
    }),
    columnHelper.group({
      id: "Secondary Details",
      header: "Secondary Details",
      columns: [
        {
          id: "address_type",
          header: "Address Type",
          accessorFn: (row) => row.address_type,
          meta: {
            filterType: "exact",
            filterOptions: addressTypes?.map((t) => t.name) ?? [],
          },
        },
        {
          id: "dhcp_group",
          header: "DHCP Group",
          accessorFn: (row) => row.dhcp_group?.name,
        },
        {
          id: "disabled_host",
          header: "Disabled",
          accessorFn: booleanAccessor("disabled_host"),
          cell: BooleanRender,
          meta: {
            filterType: "boolean",
          },
        },
        {
          id: "description",
          header: "Description",
          accessorFn: (row) => row.description,
        },
      ],
    }),
    columnHelper.group({
      id: "Changed",
      header: "Changed",
      columns: [
        {
          id: "changed",
          header: "Changed",
          accessorFn: (row) =>
            row.changed
              ? new Date(row.changed).toISOString().split("T")[0]
              : "",
          meta: {
            hideFilter: true,
          },
        },
        {
          id: "changed_by",
          header: "Changed By",
          accessorFn: (row) => row.changed_by?.username,
        },
      ],
    }),
    columnHelper.group({
      id: "Owners",
      header: "Owners",
      columns: [
        {
          id: "user_owners",
          // header: "User Owners",
          header: ({ table }: any) => (
            <div className="flex w-full gap-1 flex-row items-center justify-center m-auto">
              <p className="flex text-center text-neutral">User Owners</p>
              <ToolTip
                text="By Username"
                props="rounded-br-none right-4 bottom-4"
              />
            </div>
          ),
          size: 200,
          accessorFn: (row) => row.user_owners?.join(", "),
        },
        {
          id: "group_owners",
          header: ({ table }: any) => (
            <div className="flex w-full gap-1 flex-row items-center justify-center m-auto">
              <p className="flex text-center text-neutral">Group Owners</p>
              <ToolTip
                text="Use Full Name"
                props="rounded-br-none right-4 bottom-4"
              />
            </div>
          ),
          size: 200,
          accessorFn: (row) => row.group_owners?.join(", "),
        },
      ],
    }),
  ];
};

export const expiredFilterOptions = [
  "Expired",
  "1 Day Left",
  "7 Days Left",
  "30 Days Left",
  "Unexpired",
] as const;
