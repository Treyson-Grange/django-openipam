import React, { ReactNode, useEffect, useState } from "react";
import { Table } from "../../components/table/table";
import { useParams } from "react-router-dom";
import { useDomainTable } from "./useDomainTable";
import { useApi } from "../../hooks/useApi";
import { AddDnsModule } from "./addDnsModule";
import { EditDnsModule } from "./editDnsModule";
import { Edit } from "@mui/icons-material";
import { EditDomainModule } from "../domains/editDomainModule";
import { DnsRecord, Domain } from "../../utils/types";
import { Tab, Tabs } from "../../components/tabs";
import { useDhcpTable } from "./useDhcpTable";
import { useAuth } from "../../hooks/useAuth";
import { SingleActionModule } from "../../components/singleActionModule";

const tabs = ["DNS", "DHCP"];

export const DomainPage = () => {
  const auth = useAuth();
  const { domain } = useParams();
  const [domainInfo, setDomainInfo] = useState<Domain | undefined>();
  const [tab, setTab] = useState<typeof tabs[number]>("DNS");
  const [selectingColumns, setSelectingColumns] = useState<boolean>(false);
  const [showModule, setShowModule] = useState<boolean>(false);
  const [actionModule, setActionModule] = useState<{
    show: boolean;
    data: DnsRecord[] | undefined;
    title: string;
    onSubmit?: (data: DnsRecord[]) => void;
    children: ReactNode;
    multiple?: boolean;
  }>({
    show: false,
    data: undefined,
    title: "",
    onSubmit: () => {},
    children: <></>,
  });

  const [showEditDomainModule, setShowEditDomainModule] = useState<{
    show: boolean;
    domainData: Domain | undefined;
  }>({
    show: false,
    domainData: undefined,
  });
  const [editModule, setEditModule] = useState<{
    show: boolean;
    DnsData: DnsRecord | undefined;
  }>({
    show: false,
    DnsData: undefined,
  });
  const data = useDomainTable({
    domain: domain ?? "",
    setShowModule,
    setEditModule,
    setActionModule,
    onSelectColumns: () => {
      setSelectingColumns(true);
    },
  });
  const api = useApi();
  const getDomainInfo = async (domain: string) => {
    const results = await api.domains.byId(domain).get({});
    setDomainInfo(results);
  };
  useEffect(() => {
    if (domain) {
      getDomainInfo(domain);
    }
  }, [domain]);

  const dhcp = useDhcpTable({
    domain: domain ?? "",
  });

  return (
    <div className="m-8 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">{domain}</h1>
      {/* card displayig domain information */}
      <div className="flex flex-col gap-4 m-8 justify-center items-center content-center">
        <div className="card w-[80%] md:w-[50rem] bg-base-300 shadow-xl">
          <div className="card-body relative">
            {auth?.is_ipamadmin && (
              <div className="absolute r-2">
                <button
                  className="btn btn-circle btn-ghost btn-xs"
                  onClick={() => {
                    setShowEditDomainModule({
                      show: true,
                      domainData: domainInfo,
                    });
                  }}
                >
                  <Edit />
                </button>
              </div>
            )}
            <div className="card-title text-2xl justify-center">
              Domain Info
            </div>
            {domainInfo && (
              <div className="flex flex-col gap-4">
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Last Changed:</div>
                  <div className="text-xl col-span-2">
                    {domainInfo.changed
                      ? new Date(domainInfo.changed).toISOString().split("T")[0]
                      : ""}
                  </div>
                </div>
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Changed By:</div>
                  <div className="text-xl col-span-2">
                    {domainInfo.changed_by}
                  </div>
                </div>
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">User Permissions:</div>
                  <div className="text-xl col-span-2">
                    {Object.entries(domainInfo.user_perms).map(([key, val]) => (
                      <div key={key}>
                        {key}: {val as string}
                      </div>
                    ))}
                  </div>
                </div>
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Group Permissions:</div>

                  <div className="text-xl col-span-2">
                    {Object.entries(domainInfo.group_perms).map(
                      ([key, val]) => (
                        <div key={key}>
                          {key}: {val as string}
                        </div>
                      )
                    )}
                  </div>
                </div>
                <div className="flex flex-row gap-2 grid-cols-3 w-full justify-between">
                  <div className="col-span-1 text-xl">Description:</div>

                  <div className="text-xl col-span-2">
                    {domainInfo.description}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      <Tabs tabs={tabs} tab={tab} setTab={setTab}>
        <Tab tab={tab} name={"DNS"} props={"m-2"} data={data}>
          <Table
            table={data.table}
            loading={data.loading}
            showSelectColumns={selectingColumns}
            hideShowSelectColumns={() => setSelectingColumns(false)}
          />
        </Tab>
        <Tab tab={tab} name={"DHCP"} props={"m-2"} data={dhcp}>
          <Table table={dhcp.table} loading={dhcp.loading} />
        </Tab>
      </Tabs>
      <AddDnsModule
        domain={domain ?? ""}
        showModule={showModule}
        setShowModule={setShowModule}
      />
      <EditDnsModule
        domain={domain ?? ""}
        showModule={editModule.show}
        setShowModule={setEditModule}
        DnsData={editModule.DnsData}
      />
      <EditDomainModule
        domainData={domainInfo}
        showModule={showEditDomainModule.show}
        setShowModule={setShowEditDomainModule}
      />
      <SingleActionModule
        showModule={actionModule.show}
        setShowModule={setActionModule}
        data={actionModule.data ?? []}
        title={actionModule.title}
        onSubmit={actionModule.onSubmit}
        children={actionModule.children}
        multiple={actionModule.multiple ?? false}
      />
    </div>
  );
};
