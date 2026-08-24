import { useQuery } from "@tanstack/react-query";
import { loadStoreSettings, storeSettingsService } from "../services/storeSettings";

export function useStoreSettings() {
  return useQuery({
    queryKey: ["store-settings"],
    queryFn: loadStoreSettings,
    staleTime: 60_000,
    retry: false,
  });
}

export function useLoginBranding() {
  return useQuery({
    queryKey: ["store-settings", "public"],
    queryFn: async () => {
      const res = await storeSettingsService.getPublic();
      return res.data.data;
    },
    staleTime: 60_000,
    retry: false,
  });
}
