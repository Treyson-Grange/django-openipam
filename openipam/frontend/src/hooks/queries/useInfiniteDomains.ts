import React, { useEffect } from "react";
import { useApi } from "../useApi";
import { useInfiniteQuery } from "@tanstack/react-query";

export const useInfiniteDomains = (p: { [key: string]: string | number }) => {
  const api = useApi();
  const query = useInfiniteQuery({
    queryKey: ["domains, all", ...Object.entries(p).flat()],
    queryFn: async ({ pageParam = 1 }) => {
      const results = await api.domains.get({ page: pageParam, ...p });
      return {
        results: results.results,
        page: pageParam,
        nextPage: results.next,
      };
    },
    getNextPageParam: (lastPage) => {
      return lastPage.nextPage ? lastPage.page + 1 : undefined;
    },
  });
  useEffect(() => {
    const currentPage = query.data?.pages.at(-1)?.page ?? 0;
    if (query.hasNextPage && !query.isFetchingNextPage && currentPage < 1) {
      query.fetchNextPage();
    }
  }, [
    query.hasNextPage,
    query.isFetchingNextPage,
    query.fetchNextPage,
    query.data,
  ]);
  return query;
};
