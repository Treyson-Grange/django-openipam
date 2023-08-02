import React, { useEffect, useState } from "react";
// import { useDomainTable } from "./useDomainsTable";
import { Table } from "../../components/table";
import { useParams } from "react-router-dom";
import { useDomainTable } from "./useDomainTable";
import { useApi } from "../../hooks/useApi";
import { AddDnsModule } from "./addDnsModule";
import { EditDnsModule } from "./editDnsModule";

type Domain = {
  id: number;
  name: string;
  description: string;
  changed_by: string;
  master: string;
  changed: string;
  user_perms: Record<string, string>;
  group_perms: Record<string, string>;
};

// type DnsRecord = {
//   ip_content: string | undefined;
//   text_content: string | undefined;
//   content: string | undefined;
//   name: string;
//   ttl: number;
//   dns_type: string;
// };

export const Domain = () => {
  const { domain } = useParams();
  const [domainInfo, setDomainInfo] = useState<Domain | undefined>();
  const [showModule, setShowModule] = useState<boolean>(false);
  // const [editModule, setEditModule] = useState<{
  //   show: boolean;
  //   dnsData: DnsRecord | undefined;
  // }>({
  //   show: false,
  //   dnsData: undefined,
  // })
  const data = useDomainTable({ domain: domain ?? "", setShowModule });
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

  return (
    <div className="m-8 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">{domain}</h1>
      <h4>Here is some info and some optionss</h4>
      {/* card displayig domain information */}
      <div className="flex flex-col gap-4 m-8 justify-center items-center content-center">
        <div className="card w-[80%] md:w-[50rem] bg-gray-600 shadow-xl">
          <div className="card-body">
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
                      <div>
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
                        <div>
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
      {/* table for dns info */}
      <div className="flex flex-col gap-4 m-8">
        <Table table={data.table} loading={false} />
      </div>
      <AddDnsModule
        domain={domain ?? ""}
        showModule={showModule}
        setShowModule={setShowModule}
      />
      {/* <EditDnsModule
        domain={domain ?? ""}
        showModule={editModule.show}
        setShowModule={setEditModule}
        DnsData={editModule.dnsData}
      /> */}
    </div>
  );
};
