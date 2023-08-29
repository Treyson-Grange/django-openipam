import React, { useEffect, useMemo, useState } from "react";
import { AutocompleteSelect } from "./autocomplete";
import { Place } from "@mui/icons-material";
import { Address } from "../../utils/types";
import { useInfiniteAddresses } from "../../hooks/queries/useInfiniteAddresses";

export const AddressAutocomplete = (p: {
  onAddressChange: (Address: any) => void;
  addressId?: any;
  type?: number;
  available?: boolean;
}) => {
  const [filter, setFilter] = useState("");
  const AddressList = useInfiniteAddresses({
    address: filter,
    ...(p.type ? { type: p.type } : {}),
    ...(p.available ? { available: p.available } : {}),
  });

  const Addresss = useMemo<any[]>(() => {
    if (!AddressList.data) {
      return [];
    }
    return AddressList.data.pages.flatMap((page) => page.addresses);
  }, [AddressList.data]);

  const [Address, setAddress] = useState<Address>();

  useEffect(() => {
    p.onAddressChange(Address);
  }, [Address]);

  useEffect(() => {
    if (!p.addressId) {
      setAddress(undefined);
      setFilter("");
      return;
    }
    const Address = Addresss.find((n) => n.address === p.addressId);
    if (Address) {
      setAddress(Address);
    }
  }, [p.addressId]);

  return (
    <AutocompleteSelect
      options={Addresss}
      getValueFromOption={(option) => (option ? option.address : "")}
      value={Address}
      setValue={setAddress}
      textFilter={filter}
      setTextFilter={setFilter}
      loading={AddressList.isFetching}
      icon={<Place />}
    />
  );
};
