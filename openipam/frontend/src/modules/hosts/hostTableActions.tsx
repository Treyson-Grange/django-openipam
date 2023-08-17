import React, { ReactNode, useMemo, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { Host } from "../../utils/types";
import { ExportToCsv } from "../../components/download";
import { useDhcpGroups } from "../../hooks/queries/useDhcpGroups";
import { useInfiniteNetworks } from "../../hooks/queries/useInfiniteNetworks";

export const HostTableActions = (p: {
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
  rows: Host[];
  table: any;
}) => {
  const [action, setAction] = useState<string>("renew");
  const api = useApi();
  const dhcpGroups = useDhcpGroups();

  const dhcp = useMemo<any[]>(() => {
    if (!dhcpGroups.data) {
      return [];
    }
    return dhcpGroups.data.pages.flatMap((page) => page.dhcpGroups);
  }, [dhcpGroups.data]);

  const networkList = useInfiniteNetworks({ getAll: true });

  const networks = useMemo<any[]>(() => {
    if (!networkList.data) {
      return [];
    }
    return networkList.data.pages.flatMap((page) => page.networks);
  }, [networkList.data]);

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
          className="rounded-md p-2 select select-bordered max-w-lg"
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
              case "renew":
                p.setRenewModule({
                  show: true,
                  data: p.rows,
                });
                break;
              case "disable":
                p.setActionModule({
                  show: true,
                  data: p.rows,
                  title: "Disable Hosts",
                  onSubmit: (data) => {
                    p.rows.forEach((host) => {
                      api.hosts.byId(host.mac).disable({
                        reason: data,
                      });
                    });
                  },
                  children: (
                    <div>
                      <label className="label">Reason</label>
                      <input type="test" className="input input-bordered" />
                    </div>
                  ),
                });
                break;
              case "enable":
                p.setActionModule({
                  show: true,
                  data: p.rows,
                  title: "Enable Hosts",
                  onSubmit: () => {
                    p.rows.forEach((host) => {
                      api.hosts.byId(host.mac).enable();
                    });
                  },
                  children: (
                    <div>
                      <input className="hidden" />
                    </div>
                  ),
                });
                break;
              case "delete":
                p.setActionModule({
                  show: true,
                  data: p.rows,
                  title: "Delete Hosts",
                  onSubmit: () => {
                    p.rows.forEach((host) => {
                      api.hosts.byId(host.mac).delete();
                    });
                  },
                  children: (
                    <div>
                      <input className="hidden" />
                    </div>
                  ),
                });
                break;
              case "rename":
                p.setActionModule({
                  show: true,
                  data: p.rows,
                  multiple: true,
                  title: "Rename Hosts",
                  onSubmit: (e: any) => {
                    const regex = e.target[0].value;
                    const replacement = e.target[1].value;
                    p.rows.forEach((host) => {
                      api.hosts.byId(host.mac).update({
                        hostname: host.hostname.replace(regex, replacement),
                      });
                    });
                  },
                  children: (
                    <div>
                      <label className="label">Regex</label>
                      <input className="input input-bordered" />
                      <label className="label">Replacement</label>
                      <input className="input input-bordered" />
                    </div>
                  ),
                });
                break;
              case "export":
                p.setActionModule({
                  show: true,
                  data: p.rows,
                  title: "Download CSV",
                  children: (
                    <div className="m-auto mt-10">
                      <ExportToCsv
                        rows={p.rows}
                        columns={p.table
                          .getAllLeafColumns()
                          .slice(1)
                          .map((col: any) => col.columnDef)}
                        fileName="Hosts"
                      />
                    </div>
                  ),
                });
                break;
              case "populate":
                p.setActionModule({
                  show: true,
                  data: p.rows,
                  title: "Populate DNS Records",
                  onSubmit: () => {
                    p.rows.forEach((host) => {
                      api.hosts.byId(host.mac).populateDns();
                    });
                  },
                  children: (
                    <div>
                      <input className="hidden" />
                    </div>
                  ),
                });
                break;
              case "changeNetwork":
                p.setActionModule({
                  show: true,
                  data: p.rows,
                  title: "Change Network",
                  onSubmit: (v) => {
                    p.rows.forEach((host) => {
                      api.hosts.byId(host.mac).setNetwork({
                        network: v,
                      });
                    });
                  },
                  children: (
                    <div>
                      <p>
                        Note: If not all networks are loaded, close and reopen
                        the module
                      </p>
                      <select
                        id={`network`}
                        className="rounded-md p-2 select select-bordered max-w-md"
                      >
                        {networks.map((group: any) => (
                          <option value={group.network} key={group.network}>
                            {group.network}
                          </option>
                        ))}
                      </select>
                    </div>
                  ),
                });
                break;
              case "addOwners":
                p.setActionModule({
                  show: true,
                  data: p.rows,
                  title: "Add Owners",
                  multiple: true,
                  onSubmit: (e: any) => {
                    const group = e.target[0].value.split(",");
                    const users = e.target[1].value.split(",");
                    p.rows.forEach((host) => {
                      api.hosts
                        .byId(host.mac)
                        .users.create(
                          Object.fromEntries(
                            users.map((user: string) => [user, user])
                          )
                        );
                      api.hosts
                        .byId(host.mac)
                        .groups.create(
                          Object.fromEntries(
                            group.map((group: string) => [group, group])
                          )
                        );
                    });
                  },
                  children: (
                    <div>
                      <p>Tip: add multiple owners by separating with a comma</p>
                      <label className="label">Group Owners</label>
                      <input className="input input-bordered" />
                      <label className="label">User Owners</label>
                      <input className="input input-bordered" />
                    </div>
                  ),
                });
                break;
              case "replaceOwners":
                p.setActionModule({
                  show: true,
                  data: p.rows,
                  title: "Replace Owners",
                  multiple: true,
                  onSubmit: (e: any) => {
                    const group = e.target[0].value.split(",");
                    const users = e.target[1].value.split(",");
                    p.rows.forEach((host) => {
                      api.hosts
                        .byId(host.mac)
                        .users.put(
                          Object.fromEntries(
                            users.map((user: string) => [user, user])
                          )
                        );
                      api.hosts
                        .byId(host.mac)
                        .groups.put(
                          Object.fromEntries(
                            group.map((group: string) => [group, group])
                          )
                        );
                    });
                  },
                  children: (
                    <div>
                      <p>
                        Tip: separate owners by comma. All previous owners will
                        be removed.
                      </p>
                      <label className="label">Group Owners</label>
                      <input className="input input-bordered" />
                      <label className="label">User Owners</label>
                      <input className="input input-bordered" />
                    </div>
                  ),
                });
                break;
              case "removeOwners":
                p.setActionModule({
                  show: true,
                  data: p.rows,
                  title: "Remove Owners",
                  multiple: true,
                  onSubmit: (e: any) => {
                    const group = e.target[0].value.split(",");
                    const users = e.target[1].value.split(",");
                    p.rows.forEach((host) => {
                      api.hosts
                        .byId(host.mac)
                        .users.put(
                          Object.fromEntries(
                            host.user_owners
                              .filter((u) => !users.includes(u))
                              .map((user: string) => [user, user])
                          )
                        );
                      api.hosts
                        .byId(host.mac)
                        .groups.put(
                          Object.fromEntries(
                            host.group_owners
                              .filter((u) => !group.includes(u))
                              .map((group: string) => [group, group])
                          )
                        );
                    });
                  },
                  children: (
                    <div>
                      <p>
                        Tip: remove multiple owners by separating with a comma
                      </p>
                      <label className="label">Group Owners</label>
                      <input className="input input-bordered" />
                      <label className="label">User Owners</label>
                      <input className="input input-bordered" />
                    </div>
                  ),
                });
                break;
              case "addAttribute":
                p.setAttributeModule({
                  show: true,
                  data: p.rows,
                  delete: false,
                });
                break;
              case "deleteAttribute":
                p.setAttributeModule({
                  show: true,
                  data: p.rows,
                  delete: true,
                });
                break;
              case "setDhcpGroup":
                p.setActionModule({
                  show: true,
                  data: p.rows,
                  title: "Set DHCP Group",
                  onSubmit: (v) => {
                    p.rows.forEach((host) => {
                      api.hosts.byId(host.mac).dhcp.set({
                        dhcp_group: v,
                      });
                    });
                  },
                  children: (
                    <div>
                      <select
                        id={`dhcp_group`}
                        className="rounded-md p-2 select select-bordered max-w-md"
                      >
                        {dhcp.map((group: any) => (
                          <option value={group.name} key={group.name}>
                            {group.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  ),
                });
                break;
              case "deleteDhcpGroup":
                p.setActionModule({
                  show: true,
                  data: p.rows,
                  title: "Confirm Delete DHCP Group",
                  onSubmit: () => {
                    p.rows.forEach((host) => {
                      api.hosts.byId(host.mac).dhcp.delete();
                    });
                  },
                  children: (
                    <div>
                      <input className="hidden" />
                    </div>
                  ),
                });
                break;
              default:
                break;
            }
          }}
        >
          Go
        </button>
      </div>
    </div>
  );
};

const actions = {
  renew: "Renew",
  disable: "Disable",
  enable: "Enable",
  delete: "Delete",
  rename: "Rename",
  export: "Export to CSV",
  populate: "Populate DNS",
  changeNetwork: "Change Network",
  addOwners: "Add Owners",
  replaceOwners: "Replace Owners",
  removeOwners: "Remove Owners",
  addAttribute: "Add Attribute",
  deleteAttribute: "Delete Attribute",
  setDhcpGroup: "Set DHCP Group",
  deleteDhcpGroup: "Delete DHCP Group",
};
