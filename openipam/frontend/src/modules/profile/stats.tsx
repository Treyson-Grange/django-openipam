import React, { useEffect, useState } from "react";
import { useApi } from "../../hooks/useApi";
import { useAuth } from "../../hooks/useAuth";

export const Stats = () => {
  const api = useApi();
  const auth = useAuth();
  const [stats, setStats] = useState<any>({});


  type StatValue = {
    count: number;
    wireless_count?: number;
  };

  useEffect(() => {
    if (auth?.is_ipamadmin) {
      api.admin.stats().then((res) => {
        setStats(res);
      });
    }
  }, [auth]);

  {
    /* This should reflect the 'snapshot' in reports */
  }
  return (
    <div className="flex w-full md:max-w-[100%] lg:max-w-[100%] flex-row gap-4 flex-wrap justify-center it content-center mt-4">
      <div className="card card-bordered p-4 flex flex-col flex-wrap justify-center">
        <div className="card-title mb-4 text-center">Hosts</div>
        <div className="stats">
          {(Object.entries(stats) as [string, StatValue][])
            .splice(0, 4)
            .map(([key, value]: [string, StatValue]) => (
              <div className="stat" key={Math.random()}>
                <div className="stat-title">{key}</div>
                <div className="stat-value">
                  {value.count}
                  {value.wireless_count !== undefined && ` / ${value.wireless_count}`}
                </div>
              </div>
            ))}
        </div>
      </div>
      <div className="card card-bordered p-4 flex flex-col flex-wrap justify-center">
        <div className="card-title mb-4 mb-4 text-center">Leases</div>
        <div className="stats">
          {(Object.entries(stats) as [string, StatValue][])
            .splice(4, 2)
            .map(([key, value]: [string, StatValue]) => (
              <div className="stat" key={Math.random()}>
                <div className="stat-title">{key}</div>
                <div className="stat-value">
                  {value.count}
                  {value.wireless_count !== undefined && ` / ${value.wireless_count}`}
                </div>
              </div>
            ))}
        </div>
      </div>
      <div className="card card-bordered p-4 flex flex-col flex-wrap justify-center">
        <div className="card-title mb-4 text-center">Networks</div>
        <div className="stats">
          {(Object.entries(stats) as [string, StatValue][])
            .splice(6, 2)
            .map(([key, value]: [string, StatValue]) => (
              <div className="stat" key={Math.random()}>
                <div className="stat-title">{key}</div>
                <div className="stat-value">
                  {value.count}
                  {value.wireless_count !== undefined && ` / ${value.wireless_count}`}
                </div>
              </div>
            ))}
        </div>
      </div>
      <div className="card card-bordered p-4 flex flex-col flex-wrap justify-center">
        <div className="card-title mb-4 text-center">DNS Records</div>
        <div className="stats">
          {(Object.entries(stats) as [string, StatValue][])
            .splice(8, 3)
            .map(([key, value]: [string, StatValue]) => (
              <div className="stat" key={Math.random()}>
                <div className="stat-title">{key}</div>
                <div className="stat-value">
                  {value.count}
                  {value.wireless_count !== undefined && ` / ${value.wireless_count}`}
                </div>
              </div>
            ))}
        </div>
      </div>
      <div className="card card-bordered p-4 flex flex-col flex-wrap justify-center">
        <div className="card-title mb-4 text-center">Users</div>
        <div className="stats">
          {(Object.entries(stats) as [string, StatValue][])
            .splice(11)
            .map(([key, value]: [string, StatValue]) => (
              <div className="stat" key={Math.random()}>
                <div className="stat-title">{key}</div>
                <div className="stat-value">
                  {value.count}
                  {value.wireless_count !== undefined && ` / ${value.wireless_count}`}
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};
