import Axios from "axios";
import { makeUseAxios } from "axios-hooks";

export const useAxios = makeUseAxios({
  axios: Axios.create({
    headers: {
      "Content-Type": "application/json",
    },
  }),
});
