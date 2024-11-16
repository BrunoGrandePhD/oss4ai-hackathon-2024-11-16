import { useState, useEffect } from "react";
import { useAxios } from "./useAxios";
const host = "http://localhost:8080";

export function useMaxWave(
  position: { lat: number; lng: number } | null
): [number, any] {
  const [maxWaveHeight, setMaxWaveHeight]: [number, any] = useState(0);

  const [{ data: waveHeight }, fetchWaveHeight] = useAxios(
    {
      url: `${host}/api/v1/wave-height`,
      method: "GET",
      params: {
        latitude: position?.lat,
        longitude: position?.lng,
      },
    },
    { useCache: false, manual: true } // manual: so we don't fetch data right away.
  );

  useEffect(() => {
    if (position) {
      fetchWaveHeight();
    }
  }, [fetchWaveHeight, position]);

  useEffect(() => {
    if (waveHeight) {
      setMaxWaveHeight(waveHeight.wave_height);
    }
  }, [waveHeight]);

  return [maxWaveHeight, fetchWaveHeight];
}
