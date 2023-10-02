import ky from "ky";

export const api = ky.extend({
  hooks: {
    beforeRequest: [
      async (request) => {},
    ],
    afterResponse: [
      (_request, _options, response) => {
        return response;
      },
    ],
  },
});
export const API_URL = import.meta.env.VITE_API_URL;
