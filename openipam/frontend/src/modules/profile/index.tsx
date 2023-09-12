import React, { ReactNode, useEffect, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { Host, User } from "../../utils/types";
import { useUserHostsTable } from "./useUserHostsTable";
import { Table } from "../../components/table/table";
import { RenewHostModule } from "./renewHostModule";
import { useAuth } from "../../hooks/useAuth";
import { SingleActionModule } from "../../components/singleActionModule";
import { AttributeModule } from "../hosts/attributeModule";
import { Stats } from "./stats";
import { QuickAddToolbar } from "./quickAddToolbar";
import { RecentLogs } from "./recentLogs";

export const Profile = () => {
  const api = useApi();
  const auth = useAuth();
  const [renewModule, setRenewModule] = useState<{
    show: boolean;
    data: Host[] | undefined;
  }>({
    show: false,
    data: undefined,
  });
  const [actionModule, setActionModule] = useState<{
    show: boolean;
    data: Host[] | undefined;
    title: string;
    onSubmit?: (data: Host[]) => void;
    children: ReactNode;
    multiple?: boolean;
  }>({
    show: false,
    data: undefined,
    title: "",
    onSubmit: () => {},
    children: <></>,
  });
  const [attributeModule, setAttributeModule] = useState<{
    show: boolean;
    data: Host[] | undefined;
    delete?: boolean;
  }>({
    show: false,
    data: undefined,
    delete: false,
  });
  const [selectingColumns, setSelectingColumns] = useState<boolean>(false);

  const hosts = useUserHostsTable({
    setRenewModule,

    setActionModule,
    setAttributeModule,
    onSelectColumns: () => {
      setSelectingColumns(true);
    },
  });

  return (
    <div className="m-4 flex flex-col gap-2 content-center items-center justify-center align-middle text-center">
      <h1 className="text-4xl text-center">
        Welcome, {auth?.first_name?.charAt(0).toUpperCase()}
        {auth?.first_name?.slice(1)}
      </h1>
      <Stats />
      <div className="grid grid-cols-5 gap-2 mb-20">
        <div className="grid col-span-3">
          <div className="text-center">
            <p className="mt-4">Your Hosts:</p>
            <Table
              table={hosts.table}
              loading={hosts.loading}
              showSelectColumns={selectingColumns}
              hideShowSelectColumns={() => setSelectingColumns(false)}
            />
          </div>
        </div>
        <div className="grid col-span-2">
          <div className="w-full flex flex-col gap-16 justify-center mt-2">
            <QuickAddToolbar />
            <RecentLogs />
          </div>
        </div>
      </div>
      <RenewHostModule
        HostData={renewModule.data}
        showModule={renewModule.show}
        setShowModule={setRenewModule}
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
      <AttributeModule
        showModule={attributeModule.show}
        setShowModule={setAttributeModule}
        data={attributeModule.data ?? []}
        delete={attributeModule.delete}
      />
    </div>
  );
};
