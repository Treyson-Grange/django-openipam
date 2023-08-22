import React, { useState } from "react";
import { useDomainsTable } from "./useDomainsTable";
import { Table } from "../../components/table/table";
import { AddDomainModule } from "./addDomainModule";
import { EditDomainModule } from "./editDomainModule";
import { CreateDomain } from "../../utils/types";
import { useAuth } from "../../hooks/useAuth";

export const Domains = () => {
  const auth = useAuth();
  const [showAddDomain, setShowAddDomain] = useState(false);
  const [editDomain, setEditDomain] = useState<{
    show: boolean;
    domainData: CreateDomain | undefined;
  }>({
    show: false,
    domainData: undefined,
  });
  const table = useDomainsTable({
    setShowAddDomain: setShowAddDomain,
    setEditDomain: setEditDomain,
  });
  return (
    <div className="m-auto mt-8 overflow-x-scroll flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">Domains</h1>
      <Table table={table.table} loading={table.loading} />
      {auth?.is_ipamadmin && (
        <>
          <AddDomainModule
            showModule={showAddDomain}
            setShowModule={setShowAddDomain}
          />
          <EditDomainModule
            showModule={editDomain.show}
            setShowModule={setEditDomain}
            domainData={editDomain.domainData}
          />
        </>
      )}
    </div>
  );
};
