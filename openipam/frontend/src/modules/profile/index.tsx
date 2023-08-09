import React, { useEffect, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { User } from "../../utils/types";
import { useUserHostsTable } from "./useUserHostsTable";
import { Table } from "../../components/table";

export const Profile = () => {
  const api = useApi();
  const [user, setUser] = useState<User | undefined>();
  useEffect(() => {
    api.user
      .get()
      .then((res) => {
        setUser(res);
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  const hosts = useUserHostsTable({});

  return (
    <div className="m-4 flex flex-col gap-2 items-center justify-center text-white">
      <h1 className="text-4xl">
        Welcome, {user?.first_name.charAt(0).toUpperCase()}
        {user?.first_name.slice(1)}
      </h1>
      <p className="mt-8">Your Hosts:</p>
      <div className="flex flex-col gap-4 m-8">
        <Table table={hosts.table} loading={hosts.loading} />
      </div>
      <h2>For admins</h2>
      <p>Display total number of IP addresses, Domains, Networks, Hosts</p>
      <p>Quick add toolbar</p>
      <p>Most recent relevant Logs</p>
      <p>Other Stats/Reports</p>
    </div>
  );
};
