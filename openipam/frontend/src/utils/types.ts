import React from "react";

export const LogTypes = [
  "host",
  "dnsrecord",
  "address",
  "user",
  "group",
  "domain",
  "email",
] as const;

export const LogActions = ["Addition", "Change", "Deletion"] as const;

export type Log = {
  id: number;
  content_type: typeof LogTypes[number];
  action_flag: typeof LogActions[number];
  action_time: string;
  object_id: number;
  object_repr: string;
  change_message: string;
  user: number;
} & {
  when: string;
  to: string;
  subject: string;
  body: string;
};

export type CreateHost = {
  mac: string;
  hostname: string;
  expires: string;
  description: string;
};

export type Host = {
  mac: string;
  hostname: string;
  expires: string;
  description: string;
  changed_by: {
    first_name: string;
    last_name: string;
    username: string;
    email: string;
  };
  changed: string;
  user_owners: string[];
  group_owners: string[];
  addresses: {
    leased: string[];
    static: string[];
  };
  attributes: {
    [key: string]: string;
  };
  is_dynamic: boolean;
  disabled_host: boolean;
  master_ip_address: string;
  dhcp_group: {
    id: number;
    name: string;
    description: string;
  };
};

export type Domain = {
  id: number;
  name: string;
  description: string;
  changed_by: string;
  master: string;
  changed: string;
  user_perms: Record<string, string>;
  group_perms: Record<string, string>;
  type: string | undefined;
  notified_serial: string | undefined;
  account: string | undefined;
  last_check: string | undefined;
};

export type CreateDomain = Omit<
  Domain,
  "id" | "changed_by" | "changed" | "user_perms" | "group_perms"
>;

export type DhcpRecord = {
  id: number;
  host: string;
  ttl: number;
  changed: string;
  ip_content: string;
};

export type DnsRecord = {
  ip_content: string | undefined;
  text_content: string | undefined;
  content: string | undefined;
  name: string;
  ttl: number;
  dns_type: string;
  id: number;
  host: string;
  url: string;
};

export type CreateDnsRecord = Omit<
  DnsRecord,
  "id" | "url" | "host" | "content"
>;

export const DNS_TYPES = [
  "A",
  "A6",
  "AAAA",
  "AFSDB",
  "APL",
  "ATMA",
  "AXFR",
  "CERT",
  "CNAME",
  "DHCID",
  "DLV",
  "DNAME",
  "DNSKEY",
  "DS",
  "EID",
  "GID",
  "GPOS",
  "HINFO",
  "HIP",
  "IPSECKEY",
  "ISDN",
  "IXFR",
  "KEY",
  "KX",
  "LOC",
  "MAILA",
  "MAILB",
  "MB",
  "MD",
  "MF",
  "MG",
  "MINFO",
  "MR",
  "MX",
  "NAPTR",
  "NIMLOC",
  "NS",
  "NSAP",
  "NSAP-PTR",
  "NSEC",
  "NSEC3",
  "NSEC3PARAM",
  "NULL",
  "NXT",
  "OPT",
  "PTR",
  "PX",
  "RP",
  "RRSIG",
  "RT",
  "SIG",
  "SINK",
  "SOA",
  "SPF",
  "SRV",
  "SSHFP",
  "TA",
  "TKEY",
  "TSIG",
  "TXT",
  "UID",
  "UINFO",
  "UNSPEC",
  "WKS",
  "X25",
];
